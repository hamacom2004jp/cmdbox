from cmdbox.app import common, feature, web
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from cmdbox.app import a2a as a2a_mod
from cmdbox.app.auth import signin
from cmdbox.app.web import ThreadedASGI
from fastapi import FastAPI
from uvicorn.config import Config
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import multiprocessing
import os
import pydantic


class A2aSvStart(feature.UnsupportEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'a2asv'

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
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=True, use_agent=False,
            description_ja="A2A サーバーを起動します。",
            description_en="Start A2A server.",
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
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                    description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                    description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                    description_ja="Redisサーバーに再接続までの秒数を指定します。",
                    description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                    description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                    description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="allow_host", type=Options.T_STR, default="0.0.0.0", required=False, multi=False, hide=False, choice=None,
                     description_ja="省略した時は `0.0.0.0` を使用します。",
                     description_en="If omitted, `0.0.0.0` is used."),
                dict(opt="a2asv_listen_port", type=Options.T_INT, default="8071", required=False, multi=False, hide=False, choice=None,
                     description_ja="省略した時は `8071` を使用します。",
                     description_en="If omitted, `8071` is used."),
                dict(opt="ssl_a2asv_listen_port", type=Options.T_INT, default="8433", required=False, multi=False, hide=False, choice=None,
                     description_ja="省略した時は `8433` を使用します。",
                     description_en="If omitted, `8433` is used."),
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
                dict(opt="signin_file", type=Options.T_FILE, default=f'.{self.ver.__appid__}/user_list.yml', required=True, multi=False, hide=False, choice=None, fileio="in", web="mask",
                     description_ja=f"サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.{self.ver.__appid__}/user_list.yml' を指定します。",
                     description_en=f"Specify a file containing users and passwords with which they can signin.Typically, specify '.{self.ver.__appid__}/user_list.yml'."),
                dict(opt="gunicorn_workers", type=Options.T_INT, default=multiprocessing.cpu_count(), required=False, multi=False, hide=True, choice=None,
                     description_ja="gunicornワーカー数を指定します。Linux環境でのみ有効です。-1又は未指定の場合はCPU数を使用します。",
                     description_en="Specifies the number of gunicorn workers, valid only in Linux environment. If -1 or unspecified, the number of CPUs is used."),
                dict(opt="gunicorn_timeout", type=Options.T_INT, default=900, required=False, multi=False, hide=True, choice=None,
                     description_ja="gunicornワーカーのタイムアウトの時間を秒で指定します。",
                     description_en="Specify the timeout duration of the gunicorn worker in seconds."),
                dict(opt="boot_user", type=Options.T_STR, default="admin", required=False, multi=False, hide=False, choice=None,
                     description_ja="起動時に使用するユーザー名を指定します。このユーザーのAPIキーがMCPサーバーの認証に使用されます。デフォルトは 'admin' です。",
                     description_en="Specify the username to use at startup. This user's API key will be used for authentication with the MCP server. The default is 'admin'."),
                dict(opt="reasoning_effort", type=Options.T_STR, default="auto", required=False, multi=False, hide=False,
                     choice=["auto", "off", "on", "low", "medium", "high", "xhigh"], choice_edit=True,
                    description_ja="エージェントで思考の連鎖の深さを指定します。'auto', 'off', 'on', 'low', 'medium', 'high', 'xhigh' などが指定できますが、使用するモデルによってはサポートされていない場合があります。",
                    description_en="Use the agent to specify the depth of the thought chain. You can specify values such as 'auto', 'off', 'on', 'low', 'medium', 'high', or 'xhigh', but depending on the model you're using, some of these may not be supported."),
            ]
        )

    @validator.async_apprun_check
    async def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います
        """
        try:
            # Signin 準備
            signin_file = None if not hasattr(args, 'signin_file') or args.signin_file is None else Path(args.signin_file)
            if signin_file is not None and not signin_file.is_file():
                msg = dict(warn=f"Signin file '{signin_file}' is not found.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            signin_data = signin.Signin.load_signin_file(signin_file, None, self=self, logger=logger) if signin_file is not None else None
            # ツール側で参照できるようにするためにインスタンス化
            _web = web.Web.getInstance(logger, Path(args.data), appcls=self.appcls, ver=self.ver, language=args.language,
                                       redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                                       retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout,
                                       signin_file=args.signin_file)

            sign = signin.getDefaultInstance(logger, signin_file, signin_data, _web.redis_cli, self.appcls, self.ver, self.language)
            self.a2a = a2a_mod.A2a(logger, Path(args.data), sign, self.appcls, self.ver)
            
            # boot_user のAPIキーを取得
            boot_user_apikey = None
            if hasattr(args, 'boot_user') and args.boot_user is not None:
                if signin_data is not None and 'users' in signin_data:
                    boot_user_info = next((u for u in signin_data['users'] if u.get('name') == args.boot_user), None)
                    if boot_user_info is not None:
                        uid = boot_user_info.get('uid')
                        username = boot_user_info.get('name')
                        try:
                            # _web.user_data を使用してAPIキーを取得
                            apikeys = _web.user_data(None, str(uid), username, 'apikey')
                            if apikeys and isinstance(apikeys, dict) and len(apikeys) > 0:
                                # 最初のAPIキーを取得
                                first_key = next(iter(apikeys.keys()))
                                first_value = apikeys[first_key]
                                # valueが辞書の場合と文字列の場合に対応
                                if isinstance(first_value, dict):
                                    # 辞書の場合は、その辞書内の最初のキーを取得
                                    if len(first_value) > 0:
                                        boot_user_apikey = next(iter(first_value.keys()))
                                else:
                                    # 文字列の場合はそのまま使用
                                    boot_user_apikey = first_value
                                if boot_user_apikey:
                                    logger.info(f"Boot user '{args.boot_user}' API key loaded.")
                                else:
                                    logger.warning(f"No valid API key found for boot user '{args.boot_user}'.")
                            else:
                                logger.warning(f"No API keys configured for boot user '{args.boot_user}'.")
                        except Exception as e:
                            logger.warning(f"Failed to load boot_user API key: {e}")
                    else:
                        logger.warning(f"Boot user '{args.boot_user}' not found in signin_data.")
                else:
                    logger.warning("signin_data is None or does not contain 'users'.")
            
            if boot_user_apikey is not None:
                args.boot_user_apikey = boot_user_apikey
            
            a2a_app:FastAPI = await self.a2a.create_a2aserver(logger, args, _web)

            # SSL/paths を Path に揃える
            args.ssl_cert = None if args.ssl_cert is None else Path(args.ssl_cert)
            args.ssl_key = None if args.ssl_key is None else Path(args.ssl_key)
            args.ssl_ca_certs = None if args.ssl_ca_certs is None else Path(args.ssl_ca_certs)

            # スタート
            if args.ssl_cert is not None and args.ssl_key is not None:
                https_config = Config(app=a2a_app, host=args.allow_host, port=args.ssl_a2asv_listen_port,
                                      ssl_certfile=args.ssl_cert, ssl_keyfile=args.ssl_key,
                                      ssl_keyfile_password=args.ssl_keypass, ssl_ca_certs=args.ssl_ca_certs)
                th = ThreadedASGI(a2a_app, logger, config=https_config,
                                  gunicorn_config=dict(workers=args.gunicorn_workers, timeout=args.gunicorn_timeout))
                th.start()
            else:
                http_config = Config(app=a2a_app, host=args.allow_host, port=args.a2asv_listen_port)
                th = ThreadedASGI(a2a_app, logger, config=http_config,
                                  gunicorn_config=dict(workers=args.gunicorn_workers, timeout=args.gunicorn_timeout))
                th.start()

            try:
                def _w(f):
                    f.write(str(os.getpid()))
                common.save_file("a2a.pid", _w, nolock=False)
                # ブロッキングで稼働
                import gevent
                while True:
                    gevent.sleep(1)
            except KeyboardInterrupt:
                if th is not None:
                    th.stop()

            msg = dict(success="a2a complate.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, msg, a2a_app
        except Exception as e:
            logger.error(f"A2A server start error. {e}", exc_info=True)
            msg = dict(warn=f"A2A server start error. {e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: Union[str, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
