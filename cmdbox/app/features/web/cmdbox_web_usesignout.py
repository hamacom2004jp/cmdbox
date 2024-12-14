from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response


class Usesignout(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/usesignout')
        @app.get('/signin/usesignout')
        async def usesignout(req:Request, res:Response):
            if web.signin_file is not None:
                return dict(success={'usesignout': True})
            return dict(success={'usesignout': False})
