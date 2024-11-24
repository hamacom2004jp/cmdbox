from cmdbox import version
from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response


class VersionsC(feature.WebFeature):
    def __init__(self):
        super().__init__()

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/versions_cmdbox')
        async def versions_cmdbox(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return str(dict(warn=f'Please log in to retrieve session.'))
            logo = [version.__logo__]
            return logo + version.__description__.split('\n')