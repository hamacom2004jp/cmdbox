from cmdbox.app import common, options
from cmdbox.app.auth import signin
from cmdbox.app.features.cli import cmdbox_agent_chat
from cmdbox.app.features.web import cmdbox_web_exec_cmd
from cmdbox.app.web import Web
from fastapi import FastAPI, Depends, HTTPException, Request, Response, WebSocket
from fastapi.responses import HTMLResponse
from starlette.websockets import WebSocketDisconnect
from typing import Dict, Any, Tuple, List, Union
import datetime
import logging
import json
import jwt
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
            im = req.headers.get('If-None-Match')
            ht = str(web.agent_html.stat().st_mtime_ns)
            headers = {'Cache-Control':'private, no-cache', 'ETag': ht, 'Access-Control-Allow-Origin': '*'}
            if im == ht:
                return Response(status_code=304, headers=headers)
            if ondemand_load:
                if not web.agent_html.is_file():
                    raise HTTPException(status_code=404, detail=f'agent_html is not found. ({web.agent_html})')
                with open(web.agent_html, 'r', encoding='utf-8') as f:
                    web.options.audit_exec(req, res, web)
                    return HTMLResponse(f.read(), headers=headers)
            else:
                web.options.audit_exec(req, res, web)
                return HTMLResponse(web.agent_html_data, headers=headers)

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

            # ユーザー情報を取得する
            user_name, groups, mcpserver_apikey, a2asv_apikey = self.get_user_info(web, session)
            yield json.dumps(dict(success=dict(message=self.get_startmsg(web, user_name, groups, mcpserver_apikey, a2asv_apikey))), default=common.default_json_enc)

            agent_chat = cmdbox_agent_chat.AgentChat(self.appcls, self.ver)
            _options = options.Options.getInstance(self.appcls, self.ver)
            retry_interval = _options.get_cmd_opt('agent', 'chat', 'retry_interval').get('default', 3)
            retry_count = _options.get_cmd_opt('agent', 'chat', 'retry_count').get('default', 5)
            timeout = _options.get_cmd_opt('agent', 'chat', 'timeout').get('default', 120)

            from google.genai import types
            call_reasoning = 'off'
            call_tts = True
            while True:
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
                    if query.startswith('call_reasoning_'):
                        call_reasoning = query[len('call_reasoning_'):]
                        continue

                    web.options.audit_exec(sock, web, body=dict(agent_session=session_id, user=user_name, groups=groups, query=query))
                    for st, result in agent_chat.apprun_generate(web.logger, host=web.redis_host, port=web.redis_port, password=web.redis_password, svname=web.svname,
                                                              retry_interval=retry_interval, retry_count=retry_count, timeout=timeout,
                                                              runner_name=runner_name, user_name=user_name, session_id=session_id,
                                                              mcpserver_apikey=mcpserver_apikey, a2asv_apikey=a2asv_apikey,
                                                              message=query, call_tts=call_tts, reasoning_effort=call_reasoning):

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

    def get_startmsg(self, web:Web, user_name:str, groups:List[str], mcpserver_apikey:Union[str, None], a2asv_apikey:Union[str, None]) -> str:
        """
        チャットの開始メッセージを返します

        Args:
            web (Web): Webオブジェクト
            user_name (str): ユーザー名
            groups (List[str]): ユーザーが所属するグループ
            mcpserver_apikey (Union[str, None]): MCPサーバーのAPIキー
            a2asv_apikey (Union[str, None]): A2ASVのAPIキー
        Returns:
            str: 開始メッセージ
        """
        if mcpserver_apikey is None or a2asv_apikey is None:
            if common.is_japan(language=web.language):
                return "有効なAPIキーが設定されていません。ユーザーメニューから設定し、リロードしてからご利用ください。"
            else:
                return "A valid API key has not been configured. Please configure it from the user menu, reload the page, and then use the service."

        if common.is_japan(language=web.language):
            return "こんにちは！何かお手伝いできることはありますか？"
        else:
            return "Hello! Is there anything I can help you with?"

    def get_user_info(self, web:Web, session:Dict[str, Any]) -> Tuple[str, List[str], Union[str, None], Union[str, None]]:
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
                #apikeys = session['signin'].get('apikeys', None)
                apikeys = session.get('apikeys', None)
                if apikeys is not None and isinstance(apikeys, dict) and len(apikeys) > 0:
                    # 有効なAPIキーを選択する（JWTデコード成功かつ有効期限内）
                    valid_apikey = self._select_valid_apikey(web, apikeys)
                    if valid_apikey is not None:
                        mcpserver_apikey = valid_apikey
                        a2asv_apikey = valid_apikey
        return user_name, groups, mcpserver_apikey, a2asv_apikey

    def _select_valid_apikey(self, web:Web, apikeys:Dict[str, str]) -> Union[str, None]:
        """
        複数のAPIキーから有効なものを選択する
        有効性の判定：JWTデコードが成功かつ有効期限内

        Args:
            web (Web): Webオブジェクト
            apikeys (Dict[str, str]): APIキー名とAPIキーのマップ

        Returns:
            Union[str, None]: 有効なAPIキー、存在しない場合はNone
        """
        cls = web.signin.__class__
        for apikey_name, apikey_value in apikeys.items():
            try:
                # JWT公開鍵の取得
                publickey = None
                if cls.verify_jwt_certificate is not None:
                    publickey = cls.verify_jwt_certificate.public_key()
                if publickey is None and cls.verify_jwt_publickey is not None:
                    publickey = cls.verify_jwt_publickey
                
                # JWTをデコード（有効期限確認を含む）
                t = jwt.decode(apikey_value, publickey, algorithms=[cls.verify_jwt_algorithm],
                               issuer=cls.verify_jwt_issuer, audience=cls.verify_jwt_audience,
                               options={'verify_iss': cls.verify_jwt_issuer is not None,
                                        'verify_aud': cls.verify_jwt_audience is not None})
                # デコード成功 = 有効期限内のAPIキー
                return apikey_value
            except jwt.exceptions.InvalidTokenError:
                # JWTデコード失敗（無効またはデコード失敗）
                continue
            except Exception:
                # その他のエラー
                continue
        
        # 有効なAPIキーが見つからない場合
        return None

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
