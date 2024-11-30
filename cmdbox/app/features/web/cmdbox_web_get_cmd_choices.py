from cmdbox import version
from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response


class GetCmdChoices(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

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
                return dict(warn=f'Please log in to retrieve session.')
            form = await req.form()
            mode = form.get('mode')
            cmd = form.get('cmd')
            ret = web.options.get_cmd_choices(mode, cmd)
            return ret
