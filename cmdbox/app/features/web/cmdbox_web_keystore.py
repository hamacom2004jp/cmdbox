from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse
from pathlib import Path
from typing import Dict, Any
import logging


class Keystore(feature.WebFeature):
    def route(self, web: Web, app: FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        keystore_html = Path(__file__).resolve().parents[3] / 'web' / 'keystore.html'
        ondemand_load = web.logger.level == logging.DEBUG
        cached_html = None
        if not ondemand_load:
            if not keystore_html.is_file():
                raise FileNotFoundError(f'keystore_html is not found. ({keystore_html})')
            with open(keystore_html, 'r', encoding='utf-8') as f:
                cached_html = f.read()

        @app.get('/keystore', response_class=HTMLResponse, responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        @app.post('/keystore', response_class=HTMLResponse, responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def keystore(req: Request, res: Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            if not keystore_html.is_file():
                raise HTTPException(status_code=404, detail=f'keystore_html is not found. ({keystore_html})')
            em, headers = self.etag(web, req, str(keystore_html.stat().st_mtime_ns))
            if em:
                return Response(status_code=304, headers=headers)
            web.options.audit_exec(req, res, web)
            if ondemand_load:
                with open(keystore_html, 'r', encoding='utf-8') as f:
                    return HTMLResponse(f.read(), headers=headers)
            return HTMLResponse(cached_html, headers=headers)

    def toolmenu(self, web: Web) -> Dict[str, Any]:
        """
        ツールメニューの情報を返します

        Args:
            web (Web): Webオブジェクト

        Returns:
            Dict[str, Any]: ツールメニュー情報
        """
        return dict(keystore=dict(html='KeyStore', href='keystore', target='_blank', css_class='dropdown-item'))
