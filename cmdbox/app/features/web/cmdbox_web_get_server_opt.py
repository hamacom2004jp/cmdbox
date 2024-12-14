from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
import logging


class GetServerOpt(feature.WebFeature):
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
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            opt = dict(host=web.redis_host, port=web.redis_port, password=web.redis_password, svname=web.svname,
                       data=str(web.data), client_only=web.client_only)
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.get_server_opt: opt={opt}")
            return opt
