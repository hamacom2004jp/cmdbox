from cmdbox.app import common, mcp, web as _web
from cmdbox.app.options import Options
from cmdbox.app.auth import signin
from fastapi import FastAPI, Depends, HTTPException, Request, Response
from pathlib import Path
from typing import List, Dict, Any
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
import asyncio
import argparse
import logging
import time


class A2a(mcp.Mcp):

    def __init__(self, logger:logging.Logger, data_dir:Path, sign:signin.Signin, appcls:Any, ver:Any) -> None:
        super().__init__(logger, data_dir, sign, appcls, ver)
        options = Options.getInstance(appcls, ver)
        self.agent_list = options.get_cmd_feature('agent', 'agent_list')
        self.agent_load = options.get_cmd_feature('agent', 'agent_load')
        self.agent_chat = options.get_cmd_feature('agent', 'chat')
        self.agent_chat.call_a2asv_start = True
        self.llm_list = options.get_cmd_feature('llm', 'list')
        self.llm_load = options.get_cmd_feature('llm', 'load')
        self.mcpsv_list = options.get_cmd_feature('agent', 'mcpsv_list')
        self.mcpsv_load = options.get_cmd_feature('agent', 'mcpsv_load')
        self.agent_apps:Dict[str, Starlette] = {}
        self.agent_confs:Dict[str, Dict[str, Any]] = {}
        self.agent_lifespans:Dict[str, Dict[str, Any]] = {}

    async def _startup_agent_app(self, agent_name:str, app:Starlette) -> None:
        """Start lifespan for a delegated ASGI app once and keep it alive."""
        recv_q:asyncio.Queue = asyncio.Queue()
        send_q:asyncio.Queue = asyncio.Queue()
        async def _receive() -> Dict[str, Any]:
            return await recv_q.get()
        async def _send(message:Dict[str, Any]) -> None:
            await send_q.put(message)
        scope = dict(type='lifespan', asgi=dict(version='3.0', spec_version='2.0'))
        task = asyncio.create_task(app(scope, _receive, _send))
        try:
            await recv_q.put(dict(type='lifespan.startup'))
            msg = await asyncio.wait_for(send_q.get(), timeout=60)
            if msg.get('type') != 'lifespan.startup.complete':
                err = msg.get('message', f"Unexpected startup response: {msg}")
                raise RuntimeError(f"Agent '{agent_name}' lifespan startup failed. {err}")
            self.agent_lifespans[agent_name] = dict(task=task, recv_q=recv_q, send_q=send_q)
        except Exception:
            if not task.done():
                task.cancel()
            raise

    async def _shutdown_agent_apps(self, logger:logging.Logger) -> None:
        """Shutdown delegated ASGI apps and clear lifespan state."""
        for agent_name, state in list(self.agent_lifespans.items()):
            task:asyncio.Task = state['task']
            recv_q:asyncio.Queue = state['recv_q']
            send_q:asyncio.Queue = state['send_q']
            try:
                await recv_q.put(dict(type='lifespan.shutdown'))
                msg = await asyncio.wait_for(send_q.get(), timeout=15)
                if msg.get('type') != 'lifespan.shutdown.complete':
                    logger.warning(f"Agent '{agent_name}' lifespan shutdown returned: {msg}")
            except Exception as e:
                logger.warning(f"Agent '{agent_name}' lifespan shutdown failed: {e}")
            finally:
                if not task.done():
                    task.cancel()
                try:
                    await task
                except Exception:
                    pass
        self.agent_lifespans = {}

    async def create_a2aserver(self, logger:logging.Logger, args:argparse.Namespace, web:_web.Web) -> Any:
        """
        a2aserverを作成します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            Any: A2aServer
        """
        app = FastAPI()
        @app.middleware("http")
        async def set_allow_origin(req:Request, call_next):
            res:Response = await call_next(req)
            res.headers["Access-Control-Allow-Origin"] = "*"
            return res
        # a2aはセッションを使用しないが、signinミドルウェアでセッションが必要なため追加する
        mwparam = dict(path='/a2a', max_age=900, secret_key=common.random_string())
        app.add_middleware(SessionMiddleware, **mwparam)
        # エージェントを読込み
        await self.reload_a2aserver(logger, args)

        @app.on_event("shutdown")
        async def _shutdown_a2a_apps():
            await self._shutdown_agent_apps(logger)

        @app.api_route("/a2a/{agent_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
        async def a2a_proxy(agent_name:str, path:str, req:Request, res:Response, scope=Depends(signin.create_request_scope)):
            target_app = self.agent_apps.get(agent_name, None)
            if target_app is None:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' not found.")
            agent_conf = self.agent_confs.get(agent_name, None)
            if agent_conf is None:
                raise HTTPException(status_code=404, detail=f"Agent '{agent_name}' config not found.")
            scope = req.scope.copy()
            # pathとroot_pathを正しく設定
            scope['path'] = scope['path'].replace(f"/a2a/{agent_name}", "") if scope['path'] else "/"
            scope['raw_path'] = scope['path'].encode('utf-8') if scope['path'] else b"/"
            #scope['root_path'] = scope['root_path'].replace(f"/a2a/{agent_name}", "") if scope['root_path'] else ""

            # Delegated Auth設定がある場合、現在のログインユーザーのAPI Keyを使用する
            if 'a2asv_delegated_auth' in agent_conf:
                if agent_conf['a2asv_delegated_auth']:
                    signin = web.signin.check_signin(req, res)
                    session:Dict[str, Any] = req.session
                    if signin is None and 'signin' in session:
                        # ユーザー情報を取得
                        apikey = session['signin'].get('apikey', None)
                        if apikey is None:
                            #apikeys = session['signin'].get('apikeys', None)
                            apikeys = session.get('apikeys', None)
                            if apikeys is not None and isinstance(apikeys, dict) and len(apikeys) > 0:
                                apikey = apikeys.values().__iter__().__next__()
                                scope['headers'] = list(scope['headers']) + [(b'Authorization', f"Bearer {apikey}".encode('utf-8'))]
                # API Keyが設定されている場合、それを使用する
                elif 'a2asv_apikey' in agent_conf and agent_conf['a2asv_apikey'] is not None:
                    scope['headers'] = list(scope['headers']) + [(b'Authorization', f"Bearer {agent_conf['a2asv_apikey']}".encode('utf-8'))]
            # プロキシ先アプリケーションへ転送
            await target_app(scope, req.receive, req._send)

        @app.api_route("/a2a_reload", methods=["GET", "POST"])
        async def a2a_reload(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            session:Dict[str, Any] = req.session
            if 'signin' not in session:
                raise HTTPException(status_code=401, detail="Unauthorized")
            return await self.reload_a2aserver(logger, args)
        return app

    async def reload_a2aserver(self, logger:logging.Logger, args:argparse.Namespace) -> None:
        if logger.level == logging.DEBUG:
            logger.debug(f"google-adk a2a loading..")
        from google.adk.a2a.utils import agent_to_a2a, agent_card_builder

        await self._shutdown_agent_apps(logger)
        self.agent_apps = {}
        self.agent_confs = {}
        # エージェント一覧を取得
        if logger.level == logging.DEBUG:
            logger.debug(f"agent instance loading..")
        _args = argparse.Namespace(**args.__dict__)
        status, ret, _ = common.exec_sync(self.agent_list.apprun, logger, _args, time.time(), [])
        if status != self.agent_list.RESP_SUCCESS:
            return dict(jsonrpc="2.0", error={"code":-32000, "message":f"Failed to get agent list. {ret}"}, id=None)
        agents:List[Dict[str, Any]] = ret.get('success', {}).get('data', [])

        for agent in agents:
            # エージェント情報を取得
            _args = argparse.Namespace(**(args.__dict__ | dict(agent_name=agent['name'])))
            status, agent_conf, _ = common.exec_sync(self.agent_load.apprun, logger, _args, time.time(), [])
            if status != self.agent_load.RESP_SUCCESS:
                logger.warning(f"Failed to load agent config '{agent['name']}': {ret}")
                continue
            agent_conf = agent_conf.get('success', None)
            if agent_conf is None:
                logger.warning(f"Agent config '{agent['name']}' is empty.")
                continue
            if agent_conf.get('agent_type', None) == 'remote':
                logger.info(f"Skip: Agent config, because it is a remote agent: '{agent['name']}'")
                continue # RemoteAgentはA2Aサーバーでの起動しない
            # LLM情報を取得
            _args = argparse.Namespace(**(args.__dict__ | dict(llmname=agent_conf['llm'])))
            status, llm_conf, _ = common.exec_sync(self.llm_load.apprun, logger, _args, time.time(), [])
            if status != self.llm_load.RESP_SUCCESS:
                logger.warning(f"Failed to load llm config '{agent_conf['llm']}': {ret}")
                continue
            llm_conf = llm_conf.get('success', None)
            if llm_conf is None:
                logger.warning(f"LLM config '{agent_conf['llm']}' is empty.")
                continue
            # MCPサーバー情報を取得
            mcpsv_confs:List[Dict[str, Any]] = []
            for mcpserver_name in agent_conf.get('mcpservers', []):
                _args = argparse.Namespace(**(args.__dict__ | dict(mcpserver_name=mcpserver_name)))
                status, mcpsv_conf, _ = common.exec_sync(self.mcpsv_load.apprun, logger, _args, time.time(), [])
                if status != self.mcpsv_load.RESP_SUCCESS:
                    logger.warning(f"Failed to load mcpserver config '{mcpserver_name}': {ret}")
                    continue
                mcpsv_conf = mcpsv_conf.get('success', None)
                if mcpsv_conf is None:
                    logger.warning(f"MCPServer config '{mcpserver_name}' is empty.")
                    continue
                if mcpsv_conf.get('mcpserver_apikey', None) is None and not mcpsv_conf.get('mcpserver_delegated_auth', False):
                    logger.warning(f"MCPServer config '{mcpserver_name}' does not have apikey.")
                    continue
                mcpsv_confs.append(mcpsv_conf)
            if len(mcpsv_confs) <= 0:
                logger.warning(f"Agent '{agent['name']}' has no valid MCPServer config.")
                continue
            # エージェントのインスタンスを生成
            agent_obj = self.agent_chat.create_agent(logger=logger, data_dir=self.data, disable_remote_agent=True,
                                                     agent_conf=agent_conf, llm_conf=llm_conf,
                                                     mcpsv_confs=mcpsv_confs, payload=args.__dict__)
            if agent_obj is None:
                logger.warning(f"Agent '{agent['name']}' creation skipped.")
                continue
            # A2A ServerのURLを取得
            a2asv_baseurl:str = agent_conf.get('a2asv_baseurl', None)
            if a2asv_baseurl is None:
                logger.warning(f"Agent '{agent['name']}' has no a2asv_baseurl.")
                continue
            if a2asv_baseurl.find('/a2a/') < 0:
                logger.warning(f"Agent '{agent['name']}' has invalid a2asv_baseurl: {a2asv_baseurl}")
                continue
            a2asv_baseurl = a2asv_baseurl[0:a2asv_baseurl.find('/a2a/')]
            # エージェントカードを生成
            builder = agent_card_builder.AgentCardBuilder(agent=agent_obj,
                                                          rpc_url=f"{a2asv_baseurl}/a2a/{agent['name']}")
            agent_card = await builder.build()
            agent_card.version = self.ver.__version__
            a2a_app = agent_to_a2a.to_a2a(agent_obj, agent_card=agent_card)
            try:
                await self._startup_agent_app(agent['name'], a2a_app)
            except Exception as e:
                logger.warning(f"Agent '{agent['name']}' lifespan startup failed: {e}")
                continue
            # エージェントアプリケーションと設定を保存
            self.agent_apps[agent['name']] = a2a_app
            self.agent_confs[agent['name']] = agent_conf

        return dict(success="reloaded", agent_count=len(self.agent_apps))
