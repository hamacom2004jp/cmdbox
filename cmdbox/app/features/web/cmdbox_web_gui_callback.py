from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, HTTPException, WebSocket
from starlette.websockets import WebSocketDisconnect
import logging
import json
import queue


class GuiCallback(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.websocket('/gui/callback')
        async def gui_callback(websocket: WebSocket=None):
            if websocket is None:
                raise HTTPException(status_code=200, detail='ok.')
            await websocket.accept()
            # コマンドの実行結果をキューから取り出してブラウザに送信する
            web.logger.info(f"web.gui_callback: connected")
            if not websocket:
                raise HTTPException(status_code=400, detail='Expected WebSocket request.')
            while True:
                outputs = None
                try:
                    await websocket.receive_text() # これを行わねば非同期処理にならない。。
                    cmd, title, output = web.cb_queue.get(block=True, timeout=0.001)
                    if web.logger.level == logging.DEBUG:
                        output_str = common.to_str(output, slise=100)
                        web.logger.debug(f"web.gui_callback: cmd={cmd}, title={title}, output={output_str}")
                    outputs = dict(cmd=cmd, title=title, output=output)
                    await websocket.send_text(json.dumps(outputs, default=common.default_json_enc))
                except queue.Empty:
                    pass
                except WebSocketDisconnect:
                    web.logger.warning('web.gui_callback: websocket disconnected.')
                    break
                except Exception as e:
                    web.logger.warning(f'web.gui_callback: websocket error. {e}')
                    raise HTTPException(status_code=400, detail='Expected WebSocket request.')
