from cmdbox.app import common, feature, web
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
from urllib.request import pathname2url
import argparse
import logging
import multiprocessing


class WebStart(feature.UnsupportEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
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
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=True, use_agent=False,
            description_ja="Webモードを起動します。",
            description_en="Start Web mode.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None,
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="allow_host", type=Options.T_STR, default="0.0.0.0", required=False, multi=False, hide=False, choice=None,
                     description_ja="省略した時は `0.0.0.0` を使用します。",
                     description_en="If omitted, `0.0.0.0` is used."),
                dict(opt="listen_port", type=Options.T_INT, default="8081", required=False, multi=False, hide=False, choice=None,
                     description_ja="省略した時は `8081` を使用します。",
                     description_en="If omitted, `8081` is used."),
                dict(opt="ssl_listen_port", type=Options.T_INT, default="8443", required=False, multi=False, hide=False, choice=None,
                     description_ja="省略した時は `8443` を使用します。",
                     description_en="If omitted, `8443` is used."),
                dict(opt="ssl_cert", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                     description_ja="SSLサーバー証明書ファイルを指定します。",
                     description_en="Specify the SSL server certificate file."),
                dict(opt="ssl_key", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                     description_ja="SSLサーバー秘密鍵ファイルを指定します。",
                     description_en="Specify the SSL server private key file."),
                dict(opt="ssl_keypass", type=Options.T_STR, default=None, required=False, multi=False, hide=True, choice=None,
                     description_ja="SSLサーバー秘密鍵ファイルの複合化パスワードを指定します。",
                     description_en="Specify the composite password for the SSL server private key file."),
                dict(opt="ssl_ca_certs", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                     description_ja="SSLサーバーCA証明書ファイルを指定します。",
                     description_en="Specify the SSL server CA certificate file."),
                dict(opt="signin_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja=f"サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.{self.ver.__appid__}/user_list.yml' を指定します。",
                     description_en=f"Specify a file containing users and passwords with which they can signin.Typically, specify '.{self.ver.__appid__}/user_list.yml'."),
                dict(opt="session_domain", type=Options.T_STR, default=None, required=False, multi=False, hide=True, choice=None,
                     description_ja="サインインしたユーザーのセッションが有効なドメインを指定します。",
                     description_en="Specify the domain for which the signed-in user's session is valid."),
                dict(opt="session_path", type=Options.T_STR, default="/", required=False, multi=False, hide=True, choice=None,
                     description_ja="サインインしたユーザーのセッションが有効なパスを指定します。",
                     description_en="Specify the session timeout in seconds for signed-in users."),
                dict(opt="session_secure", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="サインインしたユーザーのセッションにSecureフラグを設定します。",
                     description_en="Set the Secure flag for the signed-in user's session."),
                dict(opt="session_timeout", type=Options.T_INT, default="900", required=False, multi=False, hide=True, choice=None,
                     description_ja="サインインしたユーザーのセッションタイムアウトの時間を秒で指定します。",
                     description_en="Specify the session timeout in seconds for signed-in users."),
                dict(opt="gunicorn_workers", type=Options.T_INT, default=multiprocessing.cpu_count(), required=False, multi=False, hide=True, choice=None,
                     description_ja="gunicornワーカー数を指定します。Linux環境でのみ有効です。-1又は未指定の場合はCPU数を使用します。",
                     description_en="Specifies the number of gunicorn workers, valid only in Linux environment. If -1 or unspecified, the number of CPUs is used."),
                dict(opt="gunicorn_timeout", type=Options.T_INT, default=30, required=False, multi=False, hide=True, choice=None,
                     description_ja="gunicornワーカーのタイムアウトの時間を秒で指定します。",
                     description_en="Specify the timeout duration of the gunicorn worker in seconds."),
                dict(opt="client_only", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="サーバーへの接続を行わないようにします.",
                     description_en="Do not make connections to the server."),
                dict(opt="outputs_key", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="showimg及びwebcap画面で表示する項目を指定します。省略した場合は全ての項目を表示します。",
                     description_en="Specify items to be displayed on the showimg and webcap screens. If omitted, all items are displayed."),
                dict(opt="doc_root", type=Options.T_DIR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="カスタムファイルのドキュメントルート. フォルダ指定のカスタムファイルのパスから、doc_rootのパスを除去したパスでURLマッピングします。",
                     description_en="Document root for custom files. URL mapping from the path of a folder-specified custom file with the path of doc_root removed."),
                dict(opt="gui_html", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="`gui.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。",
                     description_en="Specify `gui.html`. If omitted, the cmdbox built-in HTML file is used."),
                dict(opt="filer_html", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="`filer.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。",
                     description_en="Specify `filer.html`. If omitted, the cmdbox built-in HTML file is used."),
                dict(opt="result_html", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="`result.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。",
                     description_en="Specify `result.html`. If omitted, the cmdbox built-in HTML file is used."),
                dict(opt="users_html", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="`users.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。",
                     description_en="Specify `users.html`. If omitted, the cmdbox built-in HTML file is used."),
                dict(opt="assets", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, fileio="in",
                     description_ja="htmlファイルを使用する場合に必要なアセットファイルを指定します。",
                     description_en="Specify the asset file required when using html files."),
                dict(opt="signin_html", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="`signin.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。",
                     description_en="Specify `signin.html`. If omitted, the cmdbox built-in HTML file is used."),
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

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
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
        if args.data is None:
            msg = dict(warn=f"Please specify the --data option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        w = None
        try:
            args.gui_mode = False if not hasattr(args, 'gui_mode') or not args.gui_mode else args.gui_mode
            w = self.createWeb(logger, args)
            args.ssl_cert = None if args.ssl_cert is None else Path(args.ssl_cert)
            args.ssl_key = None if args.ssl_key is None else Path(args.ssl_key)
            args.ssl_ca_certs = None if args.ssl_ca_certs is None else Path(args.ssl_ca_certs)
            self.start(w, logger, args)
            msg = dict(success="web complate.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, msg, w
        except Exception as e:
            logger.error(f"Web server start error. {e}", exc_info=True)
            msg = dict(warn=f"Web server start error. {e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, w

    def createWeb(self, logger:logging.Logger, args:argparse.Namespace) -> web.Web:
        """
        Webオブジェクトを作成します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            web.Web: Webオブジェクト
        """
        w = web.Web.getInstance(logger, Path(args.data), appcls=self.appcls, ver=self.ver,
                    redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                    client_only=args.client_only, doc_root=args.doc_root, gui_html=args.gui_html, filer_html=args.filer_html,
                    result_html=args.result_html, users_html=args.users_html,
                    assets=args.assets, signin_html=args.signin_html, signin_file=args.signin_file, gui_mode=args.gui_mode)
        return w

    def start(self, w:web.Web, logger:logging.Logger, args:argparse.Namespace) -> None:
        """
        Webモードを起動します

        Args:
            w (web.Web): Webオブジェクト
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
        """
        w.start(allow_host=args.allow_host, listen_port=args.listen_port, ssl_listen_port=args.ssl_listen_port,
                ssl_cert=args.ssl_cert, ssl_key=args.ssl_key, ssl_keypass=args.ssl_keypass, ssl_ca_certs=args.ssl_ca_certs,
                session_domain=args.session_domain, session_path=args.session_path,
                session_secure=args.session_secure, session_timeout=args.session_timeout,
                outputs_key=args.outputs_key, gunicorn_workers=args.gunicorn_workers, gunicorn_timeout=args.gunicorn_timeout)
