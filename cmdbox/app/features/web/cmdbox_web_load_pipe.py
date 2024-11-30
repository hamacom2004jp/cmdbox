from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from typing import Dict, Any
import logging



class LoadPipe(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/load_pipe')
        async def load_pipe(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return dict(warn=f'Please log in to retrieve session.')
            form = await req.form()
            title = form.get('title')

            ret = self.load_pipe(web, title)
            return ret

    def load_pipe(self, web:Web, title:str) -> Dict[str, Any]:
        """
        パイプラインを読み込む

        Args:
            web (Web): Webオブジェク
            title (str): タイトル

        Returns:
            dict: パイプラインの内容
        """
        opt_path = web.pipes_path / f"pipe-{title}.json"
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.load_pipe: title={title}")
        return common.loadopt(opt_path)
