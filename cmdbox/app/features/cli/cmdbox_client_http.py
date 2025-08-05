from cmdbox.app import common, client, feature, filer
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import requests
import urllib.parse


class ClientHttp(feature.ResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'client'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'http'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False,
            description_ja="HTTPサーバーに対してリクエストを送信し、レスポンスを取得します。",
            description_en="Sends a request to the HTTP server and gets a response.",
            choice=[
                dict(opt="url", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="リクエスト先URLを指定します。",
                     description_en="Specify the URL to request."),
                dict(opt="proxy", type=Options.T_STR, default="no", required=False, multi=False, hide=False, choice=['no', 'yes'],
                     choice_show=dict(no=["send_method", "send_content_type", "send_apikey", "send_header",],
                                      yes=[]),
                     description_ja="webモードで呼び出された場合、受信したリクエストパラメータをリクエスト先URLに送信するかどうかを指定します。",
                     description_en="Specifies whether or not to send the received request parameters to the destination URL when invoked in web mode."),
                dict(opt="send_method", type=Options.T_STR, default="GET", required=True, multi=False, hide=False,
                     choice=['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'],
                     description_ja="リクエストメソッドを指定します。",
                     description_en="Specifies the request method."),
                dict(opt="send_content_type", type=Options.T_STR, default=None, required=False, multi=False, hide=False,
                     choice=['', 'application/octet-stream', 'application/json', 'multipart/form-data'],
                     choice_show={'application/octet-stream':["send_param", "send_data",],
                                  'application/json':["send_data",],
                                  'multipart/form-data':["send_param",],},
                     choice_edit=True,
                     description_ja="送信するデータのContent-Typeを指定します。",
                     description_en="Specifies the Content-Type of the data to be sent."),
                dict(opt="send_apikey", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="リクエスト先の認証で使用するAPIキーを指定します。",
                     description_en="Specify the API key to be used for authentication of the request destination."),
                dict(opt="send_header", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="リクエストヘッダーを指定します。",
                     description_en="Specifies the request header."),
                dict(opt="send_param", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="送信するパラメータを指定します。",
                     description_en="Specifies parameters to be sent."),
                dict(opt="send_data", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="送信するデータを指定します。",
                     description_en="Specifies the data to be sent."),
                dict(opt="send_verify", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[False, True],
                     description_ja="レスポンスを受け取るまでのタイムアウトを指定します。",
                     description_en="Specifies the timeout before a response is received."),
                dict(opt="send_timeout", type=Options.T_INT, default=30, required=False, multi=False, hide=True, choice=None,
                     description_ja="レスポンスを受け取るまでのタイムアウトを指定します。",
                     description_en="Specifies the timeout before a response is received."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

    async def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if args.url is None:
            msg = dict(warn=f"Please specify the --url option.")
            common.print_format(msg, args.format, tm, None, False, pf=pf)
            return self.RESP_WARN, msg, None
        query_param = {}
        if args.proxy == 'yes':
            from cmdbox.app.auth import signin
            from fastapi import Request
            scope = signin.get_request_scope()
            if scope is None:
                msg = dict(warn=f"Request scope is not set. Please set the request scope.")
                common.print_format(msg, args.format, tm, None, False, pf=pf)
                return self.RESP_WARN, msg, None
            req:Request = scope['req']
            args.send_method = req.method
            args.send_content_type = req.headers.get('Content-Type', None)
            args.send_apikey = req.headers.get('Authorization', '').replace('Bearer ', '')
            args.send_header = {k:v for k, v in req.headers.items() \
                                if k.lower() not in ['connection', 'proxy-authorization', 'proxy-connection', 'keep-alive',
                                                     'transfer-encoding', 'te', 'trailer', 'upgrade', 'content-length']}
            query_param = {k:v for k, v in req.query_params.items()}
            args.send_data = await req.body()

        url = urllib.parse.urlparse(args.url)
        query = urllib.parse.parse_qs(url.query)
        query = {**query, **query_param} if query else query_param
        args.url = urllib.parse.urlunparse((url.scheme, url.netloc, url.path, url.params, urllib.parse.urlencode(query), url.fragment))
        args.send_header = {**args.send_header, 'Authorization':f'Bearer {args.send_apikey}'} if args.send_apikey else args.send_header
        res = requests.request(method=args.send_method, url=args.url, headers=args.send_header,
                                   verify=args.send_verify, timeout=args.send_timeout, allow_redirects=True,
                                   data=args.send_data, params=args.send_param)
        if res.status_code != 200:
            msg = dict(error=f"Request failed with status code {res.status_code}.")
            common.print_format(msg, False, tm, None, False, pf=pf)
            return self.RESP_WARN, msg, None
        content_type = res.headers.get('Content-Type', '')
        if content_type.startswith('application/json'):
            try:
                msg = res.json()
            except ValueError as e:
                msg = res.text
            common.print_format(msg, False, tm, None, False, pf=pf)
            return self.RESP_SUCCESS, msg, None
        elif content_type.startswith('text/'):
            msg = res.text
            common.print_format(msg, False, tm, None, False, pf=pf)
            return self.RESP_SUCCESS, msg, None
        common.print_format(res.content, False, tm, None, False, pf=pf)

        return self.RESP_SUCCESS, res.content, None
