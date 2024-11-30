from cmdbox import version
from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse


class Signin(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        self.load_signin_file(web)
        if web.signin_html is not None:
            if not web.signin_html.is_file():
                raise FileNotFoundError(f'signin_html is not found. ({web.signin_html})')
            with open(web.signin_html, 'r', encoding='utf-8') as f:
                web.signin_html_data = f.read()

        @app.get('/signin/{next}', response_class=HTMLResponse)
        @app.post('/signin/{next}', response_class=HTMLResponse)
        async def signin(next:str, req:Request, res:Response):
            web.enable_cors(req, res)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return web.signin_html_data

    def load_signin_file(self, web:Web):
        if web.signin_file is not None:
            if not web.signin_file.is_file():
                raise FileNotFoundError(f'signin_file is not found. ({web.signin_file})')
            with open(web.signin_file, 'r', encoding='utf-8') as f:
                web.signin_file_data = dict()
                for line in f:
                    if line.strip() == '': continue
                    parts = line.strip().split(':')
                    if len(parts) <= 2:
                        raise ValueError(f'signin_file format error. Format must be "userid:passwd:algname\\n". ({web.signin_file}). {line} split={parts} len={len(parts)}')
                    web.signin_file_data[parts[0]] = dict(password=parts[1], algname=parts[2])
                    if parts[2] not in ['plain', 'md5', 'sha1', 'sha256']:
                        raise ValueError(f'signin_file format error. Algorithms not supported. ({web.signin_file}). algname={parts[2]} "plain", "md5", "sha1", "sha256" only.')
