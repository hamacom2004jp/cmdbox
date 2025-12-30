from cmdbox.app import common
from cmdbox.app.auth import signin
from cmdbox.app.features.web import cmdbox_web_exec_cmd
from cmdbox.app.web import Web
from fastapi import FastAPI, Depends, HTTPException, Request, Response, WebSocket
from starlette.websockets import WebSocketDisconnect
from typing import Dict, Any, Tuple, List, Union
import logging
import json
import re
import time
import traceback

class Agent(cmdbox_web_exec_cmd.ExecCmd):
    def route(self, web:Web, app:FastAPI) -> None:

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

        async def _chat(session:Dict[str, Any], runner_name:str, session_id:str, sock, res:Response, receive_text=None):
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"agent_chat: connected")
            # ユーザー名を取得する
            user_name = common.random_string(16)
            groups = []
            mcpserver_apikey = None
            a2asv_apikey = None
            if 'signin' in session:
                user_name = session['signin']['name']
                groups = session['signin']['groups']
                mcpserver_apikey = session['signin'].get('apikey', None)
                a2asv_apikey = session['signin'].get('apikey', None)
                if mcpserver_apikey is None:
                    apikeys = session['signin'].get('apikeys', None)
                    if apikeys is not None and isinstance(apikeys, dict) and len(apikeys) > 0:
                        mcpserver_apikey = apikeys.values().__iter__().__next__()
                        a2asv_apikey = mcpserver_apikey

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

                    web.options.audit_exec(sock, web, body=dict(agent_session=session_id, user=user_name, groups=groups, query=query))
                    opt = dict(mode='agent', cmd='chat', runner_name=runner_name, user_name=user_name,
                            session_id=session_id, mcpserver_apikey=mcpserver_apikey, a2asv_apikey=a2asv_apikey, message=query)
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