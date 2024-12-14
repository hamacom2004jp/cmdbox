from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse


class Signin(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        web.load_signin_file()
        if web.signin_html is not None:
            if not web.signin_html.is_file():
                raise HTTPException(status_code=500, detail=f'signin_html is not found. ({web.signin_html})')
            with open(web.signin_html, 'r', encoding='utf-8') as f:
                web.signin_html_data = f.read()

        @app.get('/signin/{next}', response_class=HTMLResponse)
        @app.post('/signin/{next}', response_class=HTMLResponse)
        async def signin(next:str, req:Request, res:Response):
            web.enable_cors(req, res)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return web.signin_html_data

