from cmdbox import version
from cmdbox.app import common, web
from cmdbox.app.feature import Feature
from pathlib import Path
from typing import Dict, Any, Tuple
import argparse
import logging
import traceback

class WebStart(Feature):
    def __init__(self):
        pass

    def get_mode(self):
        """
        この機能のモードを返します

        Returns:
            str: モード
        """
        return 'web'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'start'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_MEIGHT,
            discription_ja="Webモードを起動します。",
            discription_en="Start Web mode.",
            choise=[
                dict(opt="host", type="str", default=self.default_host, required=False, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーのサービスホストを指定します。",
                        discription_en="Specify the service host of the Redis server."),
                dict(opt="port", type="int", default=self.default_port, required=False, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーのサービスポートを指定します。",
                        discription_en="Specify the service port of the Redis server."),
                dict(opt="password", type="str", default=self.default_pass, required=False, multi=False, hide=True, choise=None,
                        discription_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                        discription_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type="str", default="server", required=False, multi=False, hide=True, choise=None,
                        discription_ja="推論サーバーのサービス名を指定します。省略時は `server` を使用します。",
                        discription_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="data", type="file", default=common.HOME_DIR / f".{version.__appid__}", required=False, multi=False, hide=False, choise=None,
                        discription_ja="省略した時は `$HONE/.cmdbox` を使用します。",
                        discription_en="When omitted, `$HONE/.cmdbox` is used."),
                dict(opt="allow_host", type="str", default="0.0.0.0", required=False, multi=False, hide=False, choise=None,
                        discription_ja="省略した時は `0.0.0.0` を使用します。",
                        discription_en="If omitted, `0.0.0.0` is used."),
                dict(opt="listen_port", type="int", default="8081", required=False, multi=False, hide=False, choise=None,
                        discription_ja="省略した時は `8081` を使用します。",
                        discription_en="If omitted, `8081` is used."),
                dict(opt="signin_file", type="file", default=None, required=False, multi=False, hide=True, choise=None,
                        discription_ja="サインイン可能なユーザーとパスワードを記載したファイルを指定します。省略した時は認証を要求しません。"
                                    +"サインインファイルは、各行が1ユーザーを示し、ユーザーID、パスワード、ハッシュアルゴリズム名の順で、「 : 」で区切って記載します。"
                                    +"ハッシュアルゴリズム名は「plain」「md5」「sha1」「sha256」が指定できます。",
                        discription_en="Specify a file containing users and passwords with which they can signin. If omitted, no authentication is required."
                                    +"In the signin file, each line represents one user, in the order of user ID, password, and hash algorithm name, separated by ' :'."
                                    +"The hash algorithm name can be “plain”, “md5”, “sha1”, or “sha256”."),
                dict(opt="session_timeout", type="int", default="600", required=False, multi=False, hide=True, choise=None,
                        discription_ja="サインインしたユーザーのセッションタイムアウトの時間を秒で指定します。",
                        discription_en="Specify the session timeout in seconds for signed-in users."),
                dict(opt="client_only", type="bool", default=False, required=False, multi=False, hide=True, choise=[True, False],
                        discription_ja="サーバーへの接続を行わないようにします。",
                        discription_en="Do not make connections to the server."),
                dict(opt="outputs_key", type="str", default=None, required=False, multi=True, hide=False, choise=None,
                        discription_ja="showimg及びwebcap画面で表示する項目を指定します。省略した場合は全ての項目を表示します。",
                        discription_en="Specify items to be displayed on the showimg and webcap screens. If omitted, all items are displayed."),
                dict(opt="gui_html", type="file", default=None, required=False, multi=False, hide=False, choise=None,
                        discription_ja="`gui.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。",
                        discription_en="Specify `gui.html`. If omitted, the cmdbox built-in HTML file is used."),
                dict(opt="filer_html", type="file", default=None, required=False, multi=False, hide=False, choise=None,
                        discription_ja="`filer.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。",
                        discription_en="Specify `filer.html`. If omitted, the cmdbox built-in HTML file is used."),
                dict(opt="assets", type="file", default=None, required=False, multi=True, hide=False, choise=None,
                        discription_ja="htmlファイルを使用する場合に必要なアセットファイルを指定します。",
                        discription_en="Specify the asset file required when using html files."),
                dict(opt="signin_html", type="file", default=None, required=False, multi=False, hide=False, choise=None,
                        discription_ja="`signin.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。",
                        discription_en="Specify `signin.html`. If omitted, the cmdbox built-in HTML file is used."),
                dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choise=[True, False],
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                        discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type="int", default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choise=None,
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                        discription_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
        
        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if args.data is None:
            msg = {"warn":f"Please specify the --data option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg
        w = None
        try:
            w = web.Web(logger, Path(args.data), redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                        client_only=args.client_only, gui_html=args.gui_html, filer_html=args.filer_html,
                        assets=args.assets, signin_html=args.signin_html, signin_file=args.signin_file)
            w.start(args.allow_host, args.listen_port, session_timeout=args.session_timeout, outputs_key=args.outputs_key)
            msg = {"success":"web complate."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 0, msg, w
        except Exception as e:
            msg = {"warn":f"Web server start error. {traceback.format_exc()}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, w