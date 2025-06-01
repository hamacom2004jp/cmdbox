from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse


class DoSignout(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.api_route('/dosignout/{next}', methods=['GET', 'POST'], response_class=HTMLResponse)
        @app.api_route('/{full_path:path}/dosignout/{next}/', methods=['GET', 'POST'], response_class=HTMLResponse)
        async def do_signout(next, req:Request, res:Response, full_path:str=None):
            if 'signin' in req.session:
                web.options.audit_exec(req, res, web, body=dict(msg='Signout.'), audit_type='auth')
                for key in list(req.session.keys()).copy():
                    del req.session[key]
            return RedirectResponse(url=f'../signin/{next}') # nginxのリバプロ対応のための相対パス
