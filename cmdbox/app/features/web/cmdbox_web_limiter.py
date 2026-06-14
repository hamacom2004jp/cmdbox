from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import logging


class Limiter(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        ondemand_load = web.logger.level == logging.DEBUG
        if not ondemand_load:
            if web.limiter_html is not None:
                if not web.limiter_html.is_file():
                    raise FileNotFoundError(f'limiter_html is not found. ({web.limiter_html})')
                with open(web.limiter_html, 'r', encoding='utf-8') as f:
                    web.limiter_html_data = f.read()

        @app.get('/limiter', response_class=HTMLResponse, responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        @app.post('/limiter', response_class=HTMLResponse, responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def limiter(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            im = req.headers.get('If-None-Match')
            hs = str(web.limiter_html.stat().st_mtime_ns)
            headers = {'Cache-Control':'private, no-cache', 'ETag': hs, 'Access-Control-Allow-Origin': '*'}
            if im == hs:
                return Response(status_code=304, headers=headers)
            if ondemand_load:
                if not web.limiter_html.is_file():
                    raise HTTPException(status_code=404, detail=f'limiter_html is not found. ({web.limiter_html})')
                with open(web.limiter_html, 'r', encoding='utf-8') as f:
                    web.options.audit_exec(req, res, web)
                    return HTMLResponse(f.read(), headers=headers)
            else:
                web.options.audit_exec(req, res, web)
                return HTMLResponse(web.limiter_html_data, headers=headers)

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
        return dict(limiter=dict(html='Limiter', href='limiter', target='_blank', css_class='dropdown-item'))
