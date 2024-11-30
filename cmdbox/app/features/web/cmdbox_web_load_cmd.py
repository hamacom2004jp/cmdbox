from cmdbox import version
from cmdbox.app import common
from cmdbox.app.features.web import cmdbox_web_gui
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from typing import Dict, Any
import logging


class LoadCmd(cmdbox_web_gui.Gui):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/load_cmd')
        async def load_cmd(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return dict(warn=f'Please log in to retrieve session.')
            form = await req.form()
            title = form.get('title')
            ret = self.load_cmd(web, title)
            return ret

    def load_cmd(self, web:Web, title:str) -> Dict[str, Any]:
        """
        コマンドファイルを読み込む
        
        Args:
            web (Web): Webオブジェクト
            title (str): タイトル
            
        Returns:
            dict: コマンドファイルの内容
        """
        opt_path = web.cmds_path / f"cmd-{title}.json"
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.load_cmd: title={title}, opt_path={opt_path}")
        return common.loadopt(opt_path)
