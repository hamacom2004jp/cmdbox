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
        @app.get('/usesignout', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        @app.get('/signin/usesignout', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def usesignout(req:Request, res:Response):
            if web.signin_file is not None:
                return dict(success={'usesignout': True})
            return dict(success={'usesignout': False})
