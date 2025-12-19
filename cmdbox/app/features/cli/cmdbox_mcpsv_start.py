from cmdbox.app import common, feature, web
from cmdbox.app.options import Options
from cmdbox.app import mcp as mcp_mod
from cmdbox.app.auth import signin
from cmdbox.app.web import ThreadedASGI
from uvicorn.config import Config
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import multiprocessing
import os


class McpsvStart(feature.UnsupportEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'mcpsv'

    def get_cmd(self) -> str:
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
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="MCP サーバーを起動します。",
            description_en="Start MCP server.",
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
                dict(opt="gunicorn_workers", type=Options.T_INT, default=multiprocessing.cpu_count(), required=False, multi=False, hide=True, choice=None,
                     description_ja="gunicornワーカー数を指定します。Linux環境でのみ有効です。-1又は未指定の場合はCPU数を使用します。",
                     description_en="Specifies the number of gunicorn workers, valid only in Linux environment. If -1 or unspecified, the number of CPUs is used."),
                dict(opt="gunicorn_timeout", type=Options.T_INT, default=30, required=False, multi=False, hide=True, choice=None,
                     description_ja="gunicornワーカーのタイムアウトの時間を秒で指定します。",
                     description_en="Specify the timeout duration of the gunicorn worker in seconds."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="処理結果jsonファイルを追記保存します。",
                     description_en="Save the processing result json file by appending."),
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
        """
        if args.data is None:
            msg = dict(warn=f"Please specify the --data option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        try:
            # Signin 準備
            signin_file = None if not hasattr(args, 'signin_file') or args.signin_file is None else Path(args.signin_file)
            signin_data = signin.Signin.load_signin_file(signin_file) if signin_file is not None else None
            # ツール側で参照できるようにするためにインスタンス化
            _web = web.Web.getInstance(logger, Path(args.data), appcls=self.appcls, ver=self.ver,
                                       redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                                       signin_file=args.signin_file)

            from fastmcp import FastMCP
            sign = signin.Signin(logger, signin_file, signin_data, _web.redis_cli, self.appcls, self.ver)
            self.mcp = mcp_mod.Mcp(logger, Path(args.data), sign, self.appcls, self.ver)
            fastmcp:FastMCP = self.mcp.create_mcpserver(logger, args, self.mcp.create_tools(logger, args, False))

            # SSL/paths を Path に揃える
            args.ssl_cert = None if args.ssl_cert is None else Path(args.ssl_cert)
            args.ssl_key = None if args.ssl_key is None else Path(args.ssl_key)
            args.ssl_ca_certs = None if args.ssl_ca_certs is None else Path(args.ssl_ca_certs)

            # FastMCP の ASGI アプリを取得して起動
            mcp_app = fastmcp.http_app() if fastmcp is not None else None
            if mcp_app is None:
                msg = dict(warn="MCP app is not created.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

            # mcpsvはセッションを使用しないが、signinミドルウェアでセッションが必要なため追加する
            from starlette.middleware.sessions import SessionMiddleware
            mwparam = dict(path='/mcp', max_age=900, secret_key=common.random_string())
            mcp_app.add_middleware(SessionMiddleware, **mwparam)

            # スタート
            if args.ssl_cert is not None and args.ssl_key is not None:
                https_config = Config(app=mcp_app, host=args.allow_host, port=args.ssl_listen_port,
                                      ssl_certfile=args.ssl_cert, ssl_keyfile=args.ssl_key,
                                      ssl_keyfile_password=args.ssl_keypass, ssl_ca_certs=args.ssl_ca_certs)
                th = ThreadedASGI(mcp_app, logger, config=https_config,
                                  gunicorn_config=dict(workers=args.gunicorn_workers, timeout=args.gunicorn_timeout))
                th.start()
            else:
                http_config = Config(app=mcp_app, host=args.allow_host, port=args.listen_port)
                th = ThreadedASGI(mcp_app, logger, config=http_config,
                                  gunicorn_config=dict(workers=args.gunicorn_workers, timeout=args.gunicorn_timeout))
                th.start()

            try:
                def _w(f):
                    f.write(str(os.getpid()))
                common.save_file("mcpsv.pid", _w)
                # ブロッキングで稼働
                import gevent
                while True:
                    gevent.sleep(1)
            except KeyboardInterrupt:
                if th is not None:
                    th.stop()

            msg = dict(success="mcpsv complate.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, msg, fastmcp
        except Exception as e:
            logger.error(f"MCP server start error. {e}", exc_info=True)
            msg = dict(warn=f"MCP server start error. {e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
