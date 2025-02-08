from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import Dict, Any
import json


class SaveCmd(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/save_cmd')
        async def save_cmd(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            title = form.get('title')
            opt = form.get('opt')
            ret = self.save_cmd(web, title, json.loads(opt))
            return ret

    def save_cmd(self, web:Web, title:str, opt:Dict[str, Any]) -> Dict[str, str]:
        """
        コマンドファイルを保存する

        Args:
            web (Web): Webオブジェクト
            title (str): タイトル
            opt (dict): オプション
        
        Returns:
            dict: 結果
        """
        if common.check_fname(title):
            return dict(warn=f'The title contains invalid characters."{title}"')
        opt_path = web.cmds_path / f"cmd-{title}.json"
        web.logger.info(f"save_cmd: opt_path={opt_path}, opt={opt}")
        modal_mode = opt.get('modal_mode', False)
        if modal_mode == 'add' and opt_path.exists():
            return dict(warn=f'Command "{title}" already exists')
        if 'title_disabled' in opt: del opt['title_disabled']
        if 'mode_disabled' in opt: del opt['mode_disabled']
        if 'cmd_disabled' in opt: del opt['cmd_disabled']
        if 'name_disabled' in opt: del opt['name_disabled']
        if 'modal_mode' in opt: del opt['modal_mode']
        common.saveopt(opt, opt_path, True)
        return dict(success=f'Command "{title}" saved in "{opt_path}".')
