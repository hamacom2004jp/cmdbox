from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException


class GetCmdChoices(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/get_cmd_choices')
        async def get_cmd_choices(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            mode = form.get('mode')
            cmd = form.get('cmd')
            ret = web.options.get_cmd_choices(mode, cmd)
            return ret
