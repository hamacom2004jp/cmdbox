from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from typing import Dict, Any
import logging


class Gui(feature.WebFeature):
    def __init__(self, appcls, ver):
        super().__init__(appcls=appcls, ver=ver)
        self.version_info = [dict(tabid='versions_cmdbox', title=version.__appid__,
                                  icon=f'assets/cmdbox/icon.png', url='versions_cmdbox')]

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        if web.gui_html is not None:
            if not web.gui_html.is_file():
                raise FileNotFoundError(f'gui_html is not found. ({web.gui_html})')
            with open(web.gui_html, 'r', encoding='utf-8') as f:
                web.gui_html_data = f.read()

        @app.get('/', response_class=HTMLResponse)
        async def index(req:Request, res:Response):
            return RedirectResponse(url='/gui')

        @app.get('/gui', response_class=HTMLResponse)
        @app.post('/gui', response_class=HTMLResponse)
        async def gui(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            res.headers['Access-Control-Allow-Origin'] = '*'
            return web.gui_html_data

        @app.get('/signin/gui/appid', response_class=PlainTextResponse)
        @app.get('/gui/appid', response_class=PlainTextResponse)
        async def appid(req:Request, res:Response):
            return self.ver.__appid__

        @app.get('/gui/version_info')
        async def version_info(req:Request, res:Response):
            return self.version_info

        @app.get('/gui/user_info')
        async def user_info(req:Request, res:Response):
            if 'signin' not in req.session:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            if 'userid' not in req.session['signin']:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            userid = req.session['signin']['userid']
            try:
                users = web.user_list(userid)
                if users is None or len(users) == 0:
                    return dict(warn='User information is not found.')
                return users[0]
            except Exception as e:
                return dict(error=f'{e}')

        @app.get('/gui/filemenu')
        async def filemenu(req:Request, res:Response):
            return web.filemenu

        @app.get('/gui/toolmenu')
        async def toolmenu(req:Request, res:Response):
            return web.toolmenu

        @app.get('/gui/viewmenu')
        async def viewmenu(req:Request, res:Response):
            return web.viewmenu

        @app.get('/gui/aboutmenu')
        async def aboutmenu(req:Request, res:Response):
            return web.aboutmenu

    def callback_console_modal_log_func(self, web:Web, output:Dict[str, Any]):
        """
        コンソールモーダルにログを出力する

        Args:
            web (Web): Webオブジェクト
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_console_modal_log_func: output={output_str}")
        web.cb_queue.put(('js_console_modal_log_func', None, output))

    def callback_return_cmd_exec_func(self, web:Web, title:str, output:Dict[str, Any]):
        """
        コマンド実行結果を返す

        Args:
            web (Web): Webオブジェクト
            title (str): タイトル
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_return_cmd_exec_func: output={output_str}")
        web.cb_queue.put(('js_return_cmd_exec_func', title, output))

    def callback_return_pipe_exec_func(self, web:Web, title:str, output:Dict[str, Any]):
        """
        パイプライン実行結果を返す

        Args:
            web (Web): Webオブジェクト
            title (str): タイトル
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_return_pipe_exec_func: title={title}, output={output_str}")
        web.cb_queue.put(('js_return_pipe_exec_func', title, output))

    def callback_return_stream_log_func(self, web:Web, output:Dict[str, Any]):
        """
        ストリームログを返す

        Args:
            web (Web): Webオブジェクト
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_return_stream_log_func: output={output_str}")
        web.cb_queue.put(('js_return_stream_log_func', None, output))

    def mk_curl_fileup(self, web:Web, cmd_opt:Dict[str, Any]) -> str:
        """
        curlコマンド文字列を作成する

        Args:
            web (Web): Webオブジェクト
            cmd_opt (dict): コマンドのオプション
        
        Returns:
            str: curlコマンド文字列
        """
        if 'mode' not in cmd_opt or 'cmd' not in cmd_opt:
            return ""
        curl_fileup = set()
        for ref in web.options.get_cmd_choices(cmd_opt['mode'], cmd_opt['cmd']):
            if 'fileio' not in ref or ref['fileio'] != 'in':
                continue
            if ref['opt'] in cmd_opt and cmd_opt[ref['opt']] != '':
                curl_fileup.add(f'-F "{ref["opt"]}=@&lt;{ref["opt"]}&gt;"')
        if 'stdin' in cmd_opt and cmd_opt['stdin']:
            curl_fileup.add(f'-F "input_file=@&lt;input_file&gt;"')
        return " ".join(curl_fileup)
