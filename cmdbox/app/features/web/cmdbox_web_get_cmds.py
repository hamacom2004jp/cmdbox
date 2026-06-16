from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException


class GetCmds(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/get_cmds', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def get_cmds(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            mode = form.get('mode')
            if not mode:
                return ['Please select mode.']
            #ret = web.options.get_cmds(mode)
            ret = web.signin.get_enable_cmds(mode, req, res)
            return ret
