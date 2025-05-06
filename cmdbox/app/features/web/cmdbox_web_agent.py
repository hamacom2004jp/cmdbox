from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, HTTPException, Request, Response, WebSocket
from fastapi.responses import HTMLResponse, StreamingResponse
from starlette.websockets import WebSocketDisconnect
from pathlib import Path
from starlette.applications import Starlette
from starlette.routing import Mount
from typing import Dict, Any, Tuple, List, Union
import locale
import json
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

        @app.get('/agent/session/list')
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
            sessions = web.list_agent_sessions(web.agent_runner.session_service, user_id)
            sessions = [dict(id=s.id, app_name=s.app_name, user_id=s.user_id, last_update_time=s.last_update_time,
                             events=[dict(author=ev.author,text=ev.content.parts[0].text) for ev in s.events if ev.content and ev.content.parts]) for s in sessions]
            return dict(success=sessions)

        @app.websocket('/agent/chat')
        @app.websocket('/agent/chat/{session_id}')
        async def chat(session_id:str=None, websocket:WebSocket=None, res:Response=None):
            if not websocket:
                raise HTTPException(status_code=400, detail='Expected WebSocket request.')
            if web.agent_runner is None:
                web.logger.error(f"agent_runner is null. Start web mode with `--agent use`.")
                raise HTTPException(status_code=500, detail='agent_runner is null. Start web mode with `--agent use`.')
            web.logger.info(f"agent_chat: connected")
            # ユーザー名を取得する
            user_id = common.random_string(16)
            if 'signin' in websocket.session:
                user_id = websocket.session['signin']['name']
            # これを行わねば非同期処理にならない。。
            await websocket.accept()
            # 言語認識
            language, _ = locale.getlocale()
            is_japan = language.find('Japan') >= 0 or language.find('ja_JP') >= 0
            # セッションを作成する
            agent_session = web.create_agent_session(web.agent_runner.session_service, user_id, session_id=session_id)
            startmsg = "こんにちは！何かお手伝いできることはありますか？" if is_japan else "Hello! Is there anything I can help you with?"
            await websocket.send_text(json.dumps(dict(message=startmsg), default=common.default_json_enc))
            from google.genai import types
            while True:
                outputs = None
                try:
                    query = await websocket.receive_text()
                    if query is None or query == '' or query == 'ping':
                        time.sleep(0.5)
                        continue
                    content = types.Content(role='user', parts=[types.Part(text=query)])

                    async for event in web.agent_runner.run_async(user_id=user_id, session_id=agent_session.id, new_message=content):
                        outputs = dict()
                        if event.turn_complete:
                            outputs['turn_complete'] = True
                            await websocket.send_text(json.dumps(outputs, default=common.default_json_enc))
                        if event.interrupted:
                            outputs['interrupted'] = True
                            await websocket.send_text(json.dumps(outputs, default=common.default_json_enc))
                        if event.is_final_response():
                            if event.content and event.content.parts:
                                outputs['message'] = event.content.parts[0].text
                            elif event.actions and event.actions.escalate:
                                outputs['message'] = f"Agent escalated: {event.error_message or 'No specific message.'}"
                            await websocket.send_text(json.dumps(outputs, default=common.default_json_enc))
                            break
                except WebSocketDisconnect:
                    web.logger.warning('chat: websocket disconnected.')
                    break
                except Exception as e:
                    web.logger.warning(f'chat error.', exc_info=True)
                    await websocket.send_text(json.dumps(dict(message=f'<pre>{traceback.format_exc()}</pre>'), default=common.default_json_enc))

            
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

