from cmdbox import version
from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse


class Copyright(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/copyright', response_class=PlainTextResponse)
        async def copyright(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return str(dict(warn=f'Please log in to retrieve session.'))
            return self.ver.__copyright__

