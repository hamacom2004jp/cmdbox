from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from starlette.responses import PlainTextResponse
import json


class GetModes(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/gui/get_modes', response_class=PlainTextResponse)
        async def get_modes(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return dict(warn=f'Please log in to retrieve session.')
            ret = web.options.get_modes()
            return json.dumps(ret, default=common.default_json_enc)

