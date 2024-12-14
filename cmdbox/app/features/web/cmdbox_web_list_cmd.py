from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import List, Dict, Any
import glob
import logging


class ListCmd(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/list_cmd')
        async def list_cmd(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            kwd = form.get('kwd')
            ret = self.list_cmd(web, kwd)
            ret = [r for r in ret if web.check_cmd(req, res, r['mode'], r['cmd'])]
            return ret

    def list_cmd(self, web:Web, kwd:str) -> List[Dict[str, Any]]:
        """
        コマンドファイルのタイトル一覧を取得する

        Args:
            web (Web): Webオブジェクト
            kwd (str): キーワード

        Returns:
            list: コマンドファイルのタイトル一覧
        """
        if kwd is None or kwd == '':
            kwd = '*'
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.list_cmd: kwd={kwd}")
        paths = glob.glob(str(web.cmds_path / f"cmd-{kwd}.json"))
        ret = [common.loadopt(path) for path in paths]
        ret = sorted(ret, key=lambda cmd: cmd["title"])
        return ret
