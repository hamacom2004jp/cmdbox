from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from starlette.responses import PlainTextResponse
import json


class GetCmds(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/get_cmds', response_class=PlainTextResponse)
        async def get_cmds(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            mode = form.get('mode')
            #ret = web.options.get_cmds(mode)
            ret = web.get_enable_cmds(mode, req, res)
            return json.dumps(ret, default=common.default_json_enc)
