from cmdbox import version
from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
import logging


class BbforceCmd(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/bbforce_cmd')
        async def del_cmd(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return str(dict(warn=f'Please log in to retrieve session.'))
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f"web.bbforce_cmd")
            try:
                web.container['cmdbox_app'].sv.is_running = False
            except Exception as e:
                pass
            try:
                web.container['cmdbox_app'].cl.is_running = False
            except Exception as e:
                pass
            try:
                web.container['cmdbox_app'].web.is_running = False
            except Exception as e:
                pass
            try:
            #    web.container['pipe_proc'].send_signal(signal.CTRL_C_EVENT)
                web.container['pipe_proc'].terminate()
            except Exception as e:
                pass
            return dict(success='bbforce_cmd')

