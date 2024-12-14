from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import List, Dict, Any
import glob
import logging


class ListPipe(feature.WebFeature):
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
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            kwd = form.get('kwd')
            ret = self.list_pipe(web, kwd, req, res)
            return ret

    def list_pipe(self, web:Web, kwd:str, req:Request, res:Response) -> List[Dict[str, Any]]:
        """
        パイプラインファイルのリストを取得する

        Args:
            web (Web): Webオブジェクト
            kwd (str): キーワード
            req (Request): リクエスト
            res (Response): レスポンス
        
        Returns:
            list: パイプラインファイルのリスト
        """
        if kwd is None or kwd == '':
            kwd = '*'
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.list_pipe: kwd={kwd}")
        paths = glob.glob(str(web.pipes_path / f"pipe-{kwd}.json"))
        pipes = [common.loadopt(path) for path in paths]
        pipes = sorted(pipes, key=lambda cmd: cmd["title"])
        pipes = [pipe for pipe in pipes if self.chk_pipe(web, pipe['pipe_cmd'], req, res)]
        return pipes

    def chk_pipe(self, web:Web, pipe_cmd:list, req:Request, res:Response) -> Dict[str, Any]:
        cmd = [title for title in pipe_cmd if self.chk_opt(web, title, req, res)]
        return len(pipe_cmd) == len(cmd)

    def chk_opt(self, web:Web, title:str, req:Request, res:Response) -> Dict[str, Any]:
        opt = common.loadopt(web.cmds_path / f'cmd-{title}.json')
        return web.check_cmd(req, res, opt['mode'], opt['cmd'])
