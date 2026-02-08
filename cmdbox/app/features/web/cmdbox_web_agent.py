from cmdbox.app import common, options
from cmdbox.app.auth import signin
from cmdbox.app.features.cli import cmdbox_agent_chat
from cmdbox.app.features.web import cmdbox_web_exec_cmd
from cmdbox.app.web import Web
from fastapi import FastAPI, Depends, HTTPException, Request, Response, WebSocket
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from typing import Dict, Any, Tuple, List, Union
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
        ondemand_load = web.logger.level == logging.DEBUG
        if not ondemand_load:
            if web.agent_html is not None:
                if not web.agent_html.is_file():
                    raise FileNotFoundError(f'agent_html is not found. ({web.agent_html})')
                with open(web.agent_html, 'r', encoding='utf-8') as f:
                    web.agent_html_data = f.read()

        @app.get('/agent', response_class=HTMLResponse)
        @app.post('/agent', response_class=HTMLResponse)
        async def agent(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            res.headers['Access-Control-Allow-Origin'] = '*'
            if ondemand_load:
                if not web.agent_html.is_file():
                    raise HTTPException(status_code=404, detail=f'agent_html is not found. ({web.agent_html})')
                with open(web.agent_html, 'r', encoding='utf-8') as f:
                    web.options.audit_exec(req, res, web)
                    return HTMLResponse(f.read())
            else:
                web.options.audit_exec(req, res, web)
                return HTMLResponse(web.agent_html_data)

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

            startmsg = "こんにちは！何かお手伝いできることはありますか？" if common.is_japan(language=web.language) else "Hello! Is there anything I can help you with?"
            yield json.dumps(dict(message=startmsg), default=common.default_json_enc)
            def _replace_match(match_obj):
                json_str = match_obj.group(0)
                try:
                    data = json.loads(json_str) # ユニコード文字列をエンコード
                    return json.dumps(data, ensure_ascii=False, default=common.default_json_enc)
                except json.JSONDecodeError:
                    return json_str

            agent_chat = cmdbox_agent_chat.AgentChat(self.appcls, self.ver)
            _options = options.Options.getInstance(self.appcls, self.ver)
            retry_interval = _options.get_cmd_opt('agent', 'chat', 'retry_interval').get('default', 3)
            retry_count = _options.get_cmd_opt('agent', 'chat', 'retry_count').get('default', 5)
            timeout = _options.get_cmd_opt('agent', 'chat', 'timeout').get('default', 120)

            from google.genai import types
            while True:
                outputs = None
                call_tts = True
                try:
                    query = await receive_text()
                    if query is None or query == '' or query == 'ping':
                        time.sleep(0.5)
                        continue
                    if query=='call_tts_on':
                        call_tts = True
                        continue
                    elif query=='call_tts_off':
                        call_tts = False
                        continue

                    web.options.audit_exec(sock, web, body=dict(agent_session=session_id, user=user_name, groups=groups, query=query))
                    for st, result in agent_chat.apprun_generate(web.logger, host=web.redis_host, port=web.redis_port, password=web.redis_password, svname=web.svname,
                                                              retry_interval=retry_interval, retry_count=retry_count, timeout=timeout,
                                                              runner_name=runner_name, user_name=user_name, session_id=session_id,
                                                              mcpserver_apikey=mcpserver_apikey, a2asv_apikey=a2asv_apikey,
                                                              message=query, call_tts=call_tts):

                        if st != cmdbox_agent_chat.AgentChat.RESP_SUCCESS:
                            yield common.to_str(result)
                        else:
                            agent_session_id = result.get('ids', {}).get('agent_session_id', None)
                            msg = result.get('message', '')
                            #outputs = dict(message=msg, wav_b64=result.get('wav_b64', None))
                            web.options.audit_exec(sock, web, body=dict(agent_session=agent_session_id, result=msg))
                            yield common.to_str(result)
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

    def toolmenu(self, web:Web) -> Dict[str, Any]:
        """
        ツールメニューの情報を返します

        Args:
            web (Web): Webオブジェクト
        
        Returns:
            Dict[str, Any]: ツールメニュー情報
        
        Sample:
            {
                'filer': {
                    'html': 'Filer',
                    'href': 'filer',
                    'target': '_blank',
                    'css_class': 'dropdown-item'
                    'onclick': 'alert("filer")'
                }
            }
        """
        return dict(agent=dict(html='Agent', href='agent', target='_blank', css_class='dropdown-item'))
