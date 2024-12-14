from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import Dict, Any
import json


class SavePipe(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/save_pipe')
        async def save_pipe(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            title = form.get('title')
            opt = form.get('opt')
            ret = self.save_pipe(web, title, json.loads(opt))
            return ret

    def save_pipe(self, web:Web, title:str, opt:Dict[str, Any]) -> Dict[str, str]:
        """
        パイプラインを保存する

        Args:
            title (str): タイトル
            opt (dict): オプション

        Returns:
            dict: 結果
        """
        if common.check_fname(title):
            return dict(warn=f'The title contains invalid characters."{title}"')
        opt_path = web.pipes_path / f"pipe-{title}.json"
        web.logger.info(f"save_pipe: opt_path={opt_path}, opt={opt}")
        common.saveopt(opt, opt_path)
        return dict(success=f'Pipeline "{title}" saved in "{opt_path}".')
