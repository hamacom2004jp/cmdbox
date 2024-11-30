from cmdbox import version
from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
import logging


class GetServerOpt(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/get_server_opt')
        async def get_server_opt(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return dict(warn=f'Please log in to retrieve session.')
            opt = dict(host=web.redis_host, port=web.redis_port, password=web.redis_password, svname=web.svname,
                       data=str(web.data), client_only=web.client_only)
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.get_server_opt: opt={opt}")
            return opt
