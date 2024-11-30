from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from typing import List, Dict, Any
import glob
import logging


class ListPipe(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/list_pipe')
        async def list_pipe(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return dict(warn=f'Please log in to retrieve session.')
            form = await req.form()
            kwd = form.get('kwd')
            ret = self.list_pipe(web, kwd)
            return ret

    def list_pipe(self, web:Web, kwd:str) -> List[Dict[str, Any]]:
        """
        パイプラインファイルのリストを取得する

        Args:
            web (Web): Webオブジェクト
            kwd (str): キーワード
        
        Returns:
            list: パイプラインファイルのリスト
        """
        if kwd is None or kwd == '':
            kwd = '*'
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.list_pipe: kwd={kwd}")
        paths = glob.glob(str(web.pipes_path / f"pipe-{kwd}.json"))
        ret = [common.loadopt(path) for path in paths]
        ret = sorted(ret, key=lambda cmd: cmd["title"])
        return ret
    