from cmdbox.app import common, web, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import logging


class Gui(feature.WebFeature):
    def __init__(self):
        super().__init__()

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
        @app.get('/gui', response_class=HTMLResponse)
        @app.post('/gui', response_class=HTMLResponse)
        async def gui(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            res.headers['Access-Control-Allow-Origin'] = '*'
            return web.gui_html_data

        @app.get('/gui/toolmenu')
        async def toolmenu(req:Request, res:Response):
            return web.toolmenu

    def callback_console_modal_log_func(self, web:web.Web, output:Dict[str, Any]):
        """
        コンソールモーダルにログを出力する

        Args:
            web (web.Web): Webオブジェクト
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_console_modal_log_func: output={output_str}")
        web.cb_queue.put(('js_console_modal_log_func', None, output))

    def callback_return_cmd_exec_func(self, web:web.Web, title:str, output:Dict[str, Any]):
        """
        コマンド実行結果を返す

        Args:
            web (web.Web): Webオブジェクト
            title (str): タイトル
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_return_cmd_exec_func: output={output_str}")
        web.cb_queue.put(('js_return_cmd_exec_func', title, output))

    def callback_return_pipe_exec_func(self, web:web.Web, title:str, output:Dict[str, Any]):
        """
        パイプライン実行結果を返す

        Args:
            web (web.Web): Webオブジェクト
            title (str): タイトル
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_return_pipe_exec_func: title={title}, output={output_str}")
        web.cb_queue.put(('js_return_pipe_exec_func', title, output))

    def callback_return_stream_log_func(self, web:web.Web, output:Dict[str, Any]):
        """
        ストリームログを返す

        Args:
            web (web.Web): Webオブジェクト
            output (Dict[str, Any]): 出力
        """
        if web.logger.level == logging.DEBUG:
            output_str = common.to_str(output, slise=100)
            web.logger.debug(f"web.callback_return_stream_log_func: output={output_str}")
        web.cb_queue.put(('js_return_stream_log_func', None, output))

    def mk_curl_fileup(self, web:web.Web, cmd_opt:Dict[str, Any]) -> str:
        """
        curlコマンド文字列を作成する

        Args:
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
