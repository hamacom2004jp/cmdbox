from cmdbox.app import common, feature
from cmdbox.app.auth import signin
from cmdbox.app.commons import convert
from cmdbox.app.web import Web
from fastapi import FastAPI, Depends, HTTPException, Request, Response, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
from starlette.websockets import WebSocketDisconnect
from pathlib import Path
from starlette.applications import Starlette
from starlette.datastructures import UploadFile
from starlette.routing import Mount
from typing import Dict, Any, Tuple, List, Union
import locale
import logging
import json
import re
import time
import traceback

class Agent(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
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
            web.options.audit_exec(req, res, web)
            return web.agent_html_data

        @app.post('/agent/session/list')
        async def agent_session_list(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            if web.agent_runner is None:
                web.logger.error(f"agent_runner is null. Start web mode with `--agent use`.")
                raise HTTPException(status_code=500, detail='agent_runner is null. Start web mode with `--agent use`.')
            res.headers['Access-Control-Allow-Origin'] = '*'
            web.options.audit_exec(req, res, web)
            # ユーザー名を取得する
            user_id = common.random_string(16)
            if 'signin' in req.session:
                user_id = req.session['signin']['name']
            form = await req.form()
            session_id = form.get('session_id', None)
            sessions = await web.list_agent_sessions(web.agent_runner.session_service, user_id, session_id=session_id)
            data = [dict(id=s.id, app_name=s.app_name, user_id=s.user_id, last_update_time=s.last_update_time,
                         events=[dict(author=ev.author,text=ev.content.parts[0].text) for ev in s.events if ev.content and ev.content.parts]) for s in sessions]
            data.reverse()  # 最新のセッションを先頭にする
            return dict(success=data)

        @app.post('/agent/session/delete')
        async def agent_session_delete(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            if web.agent_runner is None:
                web.logger.error(f"agent_runner is null. Start web mode with `--agent use`.")
                raise HTTPException(status_code=500, detail='agent_runner is null. Start web mode with `--agent use`.')
            res.headers['Access-Control-Allow-Origin'] = '*'
            web.options.audit_exec(req, res, web)
            # ユーザー名を取得する
            user_id = common.random_string(16)
            if 'signin' in req.session:
                user_id = req.session['signin']['name']
            form = await req.form()
            session_id = form.get('session_id', None)
            await web.delete_agent_session(web.agent_runner.session_service, user_id, session_id=session_id)
            return dict(success=True)

        @app.websocket('/agent/chat/ws')
        @app.websocket('/agent/chat/ws/{session_id}')
        async def ws_chat(session_id:str=None, websocket:WebSocket=None, res:Response=None, scope=Depends(signin.create_request_scope)):
            if not websocket:
                raise HTTPException(status_code=400, detail='Expected WebSocket request.')
            signin = web.signin.check_signin(websocket, res)
            if signin is not None:
                return signin
            if web.agent_runner is None:
                web.logger.error(f"agent_runner is null. Start web mode with `--agent use`.")
                raise HTTPException(status_code=500, detail='agent_runner is null. Start web mode with `--agent use`.')

            # これを行わねば非同期処理にならない。。
            await websocket.accept()
            # チャット処理
            async for res in _chat(websocket.session, session_id, websocket, websocket.receive_text):
                await websocket.send_text(res)
            return dict(success="connected")

        @app.api_route('/agent/chat/stream', methods=['GET', 'POST'])
        @app.api_route('/agent/chat/stream/{session_id}', methods=['GET', 'POST'])
        async def sse_chat(session_id:str=None, req:Request=None, res:Response=None):
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
            if web.agent_runner is None:
                web.logger.error(f"agent_runner is null. Start web mode with `--agent use`.")
                raise HTTPException(status_code=500, detail='agent_runner is null. Start web mode with `--agent use`.')
            async def receive_text():
                # 受信したデータを返す
                if 'query' in opt:
                    query = opt['query']
                    del opt['query']
                    return query
                raise self.SSEDisconnect('SSE disconnect')
            # チャット処理
            return StreamingResponse(
                _chat(req.session, session_id, req, receive_text=receive_text)
            )

        async def _chat(session:Dict[str, Any], session_id:str, sock, receive_text=None):
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"agent_chat: connected")
            # ユーザー名を取得する
            user_id = common.random_string(16)
            groups = []
            if 'signin' in session:
                user_id = session['signin']['name']
                groups = session['signin']['groups']
            # 言語認識
            language, _ = locale.getlocale()
            is_japan = language.find('Japan') >= 0 or language.find('ja_JP') >= 0
            # セッションを作成する
            agent_session = await web.create_agent_session(web.agent_runner.session_service, user_id, session_id=session_id)
            startmsg = "こんにちは！何かお手伝いできることはありますか？" if is_japan else "Hello! Is there anything I can help you with?"
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
                    """
                    if is_japan:
                        query += f"<important>なお現在のユーザーは'{user_id}'でgroupsは'{groups}'ですので引数に必要な時は指定してください。" + \
                            f"またsignin_fileの引数が必要な時は'{web.signin.signin_file}'を指定してください。</important>"
                            #f"またコマンド実行に必要なパラメータを確認し、以下の引数が必要な場合はこの値を使用してください。\n" + \
                            #f"  host = {web.redis_host if web.redis_host else self.default_host}\n" + \
                            #f", port = {web.redis_port if web.redis_port else self.default_port}\n" + \
                            #f", password = {web.redis_password if web.redis_password else self.default_pass}\n" + \
                            #f", svname = {web.svname if web.svname else self.default_svname}\n"
                    else:
                        query += f"<important>The current user is '{user_id}' and the groups is '{groups}', so please specify it when necessary." + \
                            f"Also, if the signin_file argument is required for command execution, please specify '{web.signin.signin_file}'.</important>"
                            #f"Also check the parameters required to execute the command and use these values if the following arguments are required.\n" + \
                            #f"  host = {web.redis_host if web.redis_host else self.default_host}\n" + \
                            #f", port = {web.redis_port if web.redis_port else self.default_port}\n" + \
                            #f", password = {web.redis_password if web.redis_password else self.default_pass}\n" + \
                            #f", svname = {web.svname if web.svname else self.default_svname}\n"
                    """
                    web.options.audit_exec(sock, web, body=dict(agent_session=agent_session.id, user_id=user_id, groups=groups, query=query))
                    content = types.Content(role='user', parts=[types.Part(text=query)])

                    async for event in web.agent_runner.run_async(user_id=user_id, session_id=agent_session.id, new_message=content):
                        #web.agent_runner.session_service.append_event(agent_session, event)
                        outputs = dict()
                        if event.turn_complete:
                            outputs['turn_complete'] = True
                            yield json.dumps(outputs, default=common.default_json_enc)
                        if event.interrupted:
                            outputs['interrupted'] = True
                            yield json.dumps(outputs, default=common.default_json_enc)
                        #if event.is_final_response():
                        msg = None
                        if event.content and event.content.parts:
                            msg = "\n".join([p.text for p in event.content.parts if p and p.text])
                        elif event.actions and event.actions.escalate:
                            msg = f"Agent escalated: {event.error_message or 'No specific message.'}"
                        if msg:
                            msg = json_pattern.sub(_replace_match, msg)

                            outputs['message'] = msg
                            web.options.audit_exec(sock, web, body=dict(agent_session=agent_session.id, result=msg))
                            yield json.dumps(outputs, default=common.default_json_enc)
                            if event.is_final_response():
                                break
                except WebSocketDisconnect:
                    web.logger.warning('chat: websocket disconnected.')
                    break
                except self.SSEDisconnect as e:
                    break
                except Exception as e:
                    web.logger.warning(f'chat error.', exc_info=True)
                    yield json.dumps(dict(message=f'<pre>{traceback.format_exc()}</pre>'), default=common.default_json_enc)
                    break
            
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

    class SSEDisconnect(Exception):
        """
        SSEの切断を示す例外クラス
        """
        pass