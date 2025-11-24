from cmdbox.app import common, feature
from cmdbox.app.auth import signin
from cmdbox.app.features.web import cmdbox_web_exec_cmd
from cmdbox.app.web import Web
from fastapi import FastAPI, Depends, HTTPException, Request, Response, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
from starlette.websockets import WebSocketDisconnect
from starlette.datastructures import UploadFile
from typing import Dict, Any, Tuple, List, Union
import locale
import logging
import json
import re
import time
import traceback

class Agent(cmdbox_web_exec_cmd.ExecCmd):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/agent/session/list')
        async def agent_session_list(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            res.headers['Access-Control-Allow-Origin'] = '*'
            # ユーザー名を取得する
            user_id = common.random_string(16)
            if 'signin' in req.session:
                user_id = req.session['signin']['name']
            form = await req.form()
            runner_name = form.get('runner_name', None)
            session_id = form.get('session_id', None)
            opt = dict(mode='agent', cmd='session_list', runner_name=runner_name, userid=user_id, session_id=session_id)
            sessions = await self.exec_cmd(req, res, web, '', opt, True, self.appcls)
            if 'success' not in sessions:
                return sessions
            sessions = sessions['success']['data']
            if sessions is None:
                return dict(success=[])
            data = [dict(id=s.id, app_name=s.app_name, user_id=s.user_id, last_update_time=s.last_update_time,
                         events=[dict(author=ev.author,text=ev.content.parts[0].text) for ev in s.events if ev.content and ev.content.parts]) for s in sessions if s]
            data.reverse()  # 最新のセッションを先頭にする
            return dict(success=data)

        @app.post('/agent/session/delete')
        async def agent_session_delete(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            res.headers['Access-Control-Allow-Origin'] = '*'
            # ユーザー名を取得する
            user_id = common.random_string(16)
            if 'signin' in req.session:
                user_id = req.session['signin']['name']
            form = await req.form()
            runner_name = form.get('runner_name', None)
            session_id = form.get('session_id', None)
            opt = dict(mode='agent', cmd='session_del', runner_name=runner_name, userid=user_id, session_id=session_id)
            ret = await self.exec_cmd(req, res, web, '', opt, True, self.appcls)
            return ret

        @app.websocket('/{webapp}/chat/ws/{runner_name}')
        @app.websocket('/{webapp}/chat/ws/{runner_name}/{session_id}')
        async def ws_chat(runner_name:str=None, session_id:str=None, webapp:str=None, websocket:WebSocket=None, res:Response=None, scope=Depends(signin.create_request_scope)):
            if not websocket:
                raise HTTPException(status_code=400, detail='Expected WebSocket request.')
            signin = web.signin.check_signin(websocket, res)
            if signin is not None:
                return signin
            # これを行わねば非同期処理にならない。。
            await websocket.accept()
            # チャット処理
            async for res in _chat(websocket.session, runner_name, session_id, websocket, res, websocket.receive_text):
                await websocket.send_text(res)
            return dict(success="connected")
        """
        @app.api_route('/{webapp}/chat/stream/{runner_name}', methods=['GET', 'POST'])
        @app.api_route('/{webapp}/chat/stream/{runner_name}/{session_id}', methods=['GET', 'POST'])
        async def sse_chat(runner_name:str=None, session_id:str=None, webapp:str=None, req:Request=None, res:Response=None):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            def _marge_opt(opt, param):
                for k in opt.keys():
                    if k in param: opt[k] = param[k]
                return opt
            content_type = req.headers.get('content-type')
            opt = None
            if content_type is None:
                opt = req.query_params._dict
            elif content_type.startswith('multipart/form-data'):
                form = await req.form()
                opt = dict()
                for key, fv in form.multi_items():
                    if not isinstance(fv, UploadFile): continue
                    opt[key] = fv.file
            elif content_type.startswith('application/json'):
                opt = await req.json()
            elif content_type.startswith('application/octet-stream'):
                opt = json.loads(await req.body())
            if opt is None:
                raise HTTPException(status_code=400, detail='Expected JSON or form data.')
            if opt['query'] is None or opt['query'] == '':
                raise HTTPException(status_code=400, detail='Expected query.')
            async def receive_text():
                # 受信したデータを返す
                if 'query' in opt:
                    query = opt['query']
                    del opt['query']
                    return query
                raise self.SSEDisconnect('SSE disconnect')
            # チャット処理
            return StreamingResponse(
                _chat(req.session, runner_name, session_id, req, receive_text=receive_text)
            )
        """
        async def _chat(session:Dict[str, Any], runner_name:str, session_id:str, sock, res:Response, receive_text=None):
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"agent_chat: connected")
            # ユーザー名を取得する
            user_id = common.random_string(16)
            groups = []
            if 'signin' in session:
                user_id = session['signin']['name']
                groups = session['signin']['groups']

            startmsg = "こんにちは！何かお手伝いできることはありますか？" if common.is_japan() else "Hello! Is there anything I can help you with?"
            yield json.dumps(dict(message=startmsg), default=common.default_json_enc)
            def _replace_match(match_obj):
                json_str = match_obj.group(0)
                try:
                    data = json.loads(json_str) # ユニコード文字列をエンコード
                    return json.dumps(data, ensure_ascii=False, default=common.default_json_enc)
                except json.JSONDecodeError:
                    return json_str
            json_pattern = re.compile(r'\{.*?\}')

            from google.genai import types
            while True:
                outputs = None
                try:
                    query = await receive_text()
                    if query is None or query == '' or query == 'ping':
                        time.sleep(0.5)
                        continue

                    web.options.audit_exec(sock, web, body=dict(agent_session=session_id, user_id=user_id, groups=groups, query=query))
                    opt = dict(mode='agent', cmd='chat', runner_name=runner_name, userid=user_id,
                            session_id=session_id, message=query)
                    ret = await self.exec_cmd(sock, res, web, '', opt, True, self.appcls)
                    if 'success' not in ret:
                        yield common.to_str(ret)
                        continue
                    for result in ret['success']:
                        agent_session_id = result.get('agent_session_id', None)
                        msg = result.get('message', '')
                        outputs = dict(message=msg)
                        web.options.audit_exec(sock, web, body=dict(agent_session=agent_session_id, result=msg))
                        yield common.to_str(outputs)
                except WebSocketDisconnect:
                    web.logger.warning('chat: websocket disconnected.')
                    break
                except self.SSEDisconnect as e:
                    break
                except NotImplementedError as e:
                    web.logger.warning(f'The session table needs to be reloaded.{e}', exc_info=True)
                    yield json.dumps(dict(message=f'The session table needs to be reloaded. Please reload your browser.'), default=common.default_json_enc)
                    break
                except Exception as e:
                    web.logger.warning(f'chat error.', exc_info=True)
                    yield json.dumps(dict(message=f'<pre>{traceback.format_exc()}</pre>'), default=common.default_json_enc)
                    break
            
    class SSEDisconnect(Exception):
        """
        SSEの切断を示す例外クラス
        """
        pass