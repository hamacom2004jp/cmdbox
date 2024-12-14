from cmdbox.app import common
from cmdbox.app.features.web import cmdbox_web_gui
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import Dict, Any, List
import logging
import json


class RawCmd(cmdbox_web_gui.Gui):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/raw_cmd')
        async def raw_cmd(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            title = form.get('title')
            opt = form.get('opt')
            ret = self.raw_cmd(web, title, json.loads(opt))
            return ret

    def raw_cmd(self, web:Web, title:str, opt:dict) -> List[Dict[str, Any]]:
        """
        コマンドライン文字列、オプション文字列、curlコマンド文字列を作成する

        Args:
            title (str): タイトル
            opt (dict): オプション
        
        Returns:
            list[Dict[str, Any]]: コマンドライン文字列、オプション文字列、curlコマンド文字列
        """
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.raw_cmd: title={title}, opt={opt}")
        opt_list, _ = web.options.mk_opt_list(opt)
        if 'stdout_log' in opt: del opt['stdout_log']
        if 'capture_stdout' in opt: del opt['capture_stdout']
        curl_cmd_file = self.mk_curl_fileup(web, opt)
        return [dict(type='cmdline',raw=' '.join(['python','-m',self.ver.__appid__]+opt_list)),
                dict(type='optjson',raw=json.dumps(opt, default=common.default_json_enc)),
                dict(type='curlcmd',raw=f'curl {curl_cmd_file} http://localhost:{web.listen_port}/exec_cmd/{title}')]
