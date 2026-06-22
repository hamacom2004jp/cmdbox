from cmdbox.app import common, client, feature, filer
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class ClientFileIs(feature.OneshotResultEdgeFeature, validator.Validator):
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
        return 'file_is'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=True,
            description_ja="指定した操作が実行可能かどうかを判断します。",
            description_en="Determine whether the specified file operation is executable.",
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
                dict(opt="file_func", type=Options.T_STR, default=None, required=True, multi=False, hide=False,
                     choice=["copy", "download", "list", "mkdir", "move", "remove", "rmdir", "upload"],
                     description_ja="実行可能かどうかを判断する操作を指定します。",
                     description_en="Specify the operation to determine whether it is executable.",),
                dict(opt="svpath", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="操作対象のパスを指定します。copy・move 以外の操作で使用します。",
                     description_en="Specify the target path. Used for operations other than copy and move.",
                     test_true={"server": "/", "client": "/", "current": "/"}),
                dict(opt="from_path", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="コピー・移動元のパスを指定します。copy・move 操作で使用します。",
                     description_en="Specify the source path. Used for copy and move operations."),
                dict(opt="to_path", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="コピー・移動先のパスを指定します。copy・move 操作で使用します。",
                     description_en="Specify the destination path. Used for copy and move operations."),
                dict(opt="fwpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="単一パス操作において、指定したパスが範囲内かどうかを判定するパスを指定します。",
                     description_en="Specify a path to determine whether the target path is within bounds for single-path operations."),
                dict(opt="rjpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="単一パス操作において、指定したパスが要求されたパスにマッチする場合、アクセスが拒否されます。正規表現として解釈します。",
                     description_en="For single-path operations, access will be denied if the path matches. Interpreted as a regular expression."),
                dict(opt="from_fwpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="copy・move 操作において、コピー・移動元が範囲内かどうかを判定するパスを指定します。",
                     description_en="Specify a path to determine whether the source path is within bounds for copy/move operations."),
                dict(opt="to_fwpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="copy・move 操作において、コピー・移動先が範囲内かどうかを判定するパスを指定します。",
                     description_en="Specify a path to determine whether the destination path is within bounds for copy/move operations."),
                dict(opt="from_rjpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="copy・move 操作において、コピー・移動元パスがマッチする場合、アクセスが拒否されます。正規表現として解釈します。",
                     description_en="For copy/move operations, access will be denied if the source path matches. Interpreted as a regular expression."),
                dict(opt="to_rjpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="copy・move 操作において、コピー・移動先パスがマッチする場合、アクセスが拒否されます。正規表現として解釈します。",
                     description_en="For copy/move operations, access will be denied if the destination path matches. Interpreted as a regular expression."),
                dict(opt="scope", type=Options.T_STR, default="client", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="スコープを指定します。`client` はクライアント側、`server` はサーバー側です。`current` は実行時ディレクトリです。",
                     description_en="Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="15", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
            ]
        )

    @validator.apprun_check
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
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)

        client_data = Path(str(args.client_data).replace('"', '')) if args.client_data is not None else None
        svpath = str(args.svpath).replace('"', '') if args.svpath is not None else None
        from_path = str(args.from_path).replace('"', '') if args.from_path is not None else None
        to_path = str(args.to_path).replace('"', '') if args.to_path is not None else None

        args.fwpath = args.fwpath if isinstance(args.fwpath, list) else [args.fwpath] if args.fwpath is not None and args.fwpath != "********" else []
        args.rjpath = args.rjpath if isinstance(args.rjpath, list) else [args.rjpath] if args.rjpath is not None and args.rjpath != "********" else []
        args.from_fwpath = args.from_fwpath if isinstance(args.from_fwpath, list) else [args.from_fwpath] if args.from_fwpath is not None and args.from_fwpath != "********" else []
        args.to_fwpath = args.to_fwpath if isinstance(args.to_fwpath, list) else [args.to_fwpath] if args.to_fwpath is not None and args.to_fwpath != "********" else []
        args.from_rjpath = args.from_rjpath if isinstance(args.from_rjpath, list) else [args.from_rjpath] if args.from_rjpath is not None and args.from_rjpath != "********" else []
        args.to_rjpath = args.to_rjpath if isinstance(args.to_rjpath, list) else [args.to_rjpath] if args.to_rjpath is not None and args.to_rjpath != "********" else []

        fwpaths = [str(p).replace('"', '') for p in args.fwpath]
        rjpaths = [str(p).replace('"', '') for p in args.rjpath]
        from_fwpaths = [str(p).replace('"', '') for p in args.from_fwpath]
        to_fwpaths = [str(p).replace('"', '') for p in args.to_fwpath]
        from_rjpaths = [str(p).replace('"', '') for p in args.from_rjpath]
        to_rjpaths = [str(p).replace('"', '') for p in args.to_rjpath]

        ret = cl.file_is(args.file_func, svpath=svpath, from_path=from_path, to_path=to_path,
                         fwpaths=fwpaths if fwpaths else None, rjpaths=rjpaths if rjpaths else None,
                         from_fwpaths=from_fwpaths if from_fwpaths else None, to_fwpaths=to_fwpaths if to_fwpaths else None,
                         from_rjpaths=from_rjpaths if from_rjpaths else None, to_rjpaths=to_rjpaths if to_rjpaths else None,
                         scope=args.scope, client_data=client_data,
                         retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, cl

        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            file_func: Union[str, None] = pydantic.Field(default=None, description="操作種別")
            path: Union[str, None] = pydantic.Field(default=None, description="操作対象パス")
            from_path: Union[str, None] = pydantic.Field(default=None, description="コピー・移動元パス")
            to_path: Union[str, None] = pydantic.Field(default=None, description="コピー・移動先パス")
            executable: Union[bool, None] = pydantic.Field(default=None, description="実行可能かどうか")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        この機能のサーバー側の実行を行います

        Args:
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            msg (List[str]): 受信メッセージ
            sessions (Dict[str, Dict[str, Any]]): セッション情報

        Returns:
            int: 終了コード
        """
        payload = json.loads(convert.b64str2str(msg[2]))
        file_func = payload.get('file_func', None)
        svpath = payload.get('svpath', None)
        from_path = payload.get('from_path', None)
        to_path = payload.get('to_path', None)
        fwpaths = payload.get('fwpaths', None)
        rjpaths = payload.get('rjpaths', None)
        from_fwpaths = payload.get('from_fwpaths', None)
        to_fwpaths = payload.get('to_fwpaths', None)
        from_rjpaths = payload.get('from_rjpaths', None)
        to_rjpaths = payload.get('to_rjpaths', None)
        st = self.file_is(msg[1], file_func, svpath, from_path, to_path,
                          fwpaths, rjpaths, from_fwpaths, to_fwpaths, from_rjpaths, to_rjpaths,
                          data_dir, logger, redis_cli, sessions)
        return st

    def file_is(self, reskey:str, file_func:str, svpath:str, from_path:str, to_path:str,
                fwpaths:List[str], rjpaths:List[str],
                from_fwpaths:List[str], to_fwpaths:List[str],
                from_rjpaths:List[str], to_rjpaths:List[str],
                data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient,
                sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        指定した操作が実行可能かどうかを確認する

        Args:
            reskey (str): レスポンスキー
            file_func (str): 操作種別
            svpath (str): 操作対象パス
            from_path (str): コピー・移動元パス
            to_path (str): コピー・移動先パス
            fwpaths (List[str]): 範囲内かどうかを示すパスのリスト
            rjpaths (List[str]): 範囲外かどうかを示すパスのリスト
            from_fwpaths (List[str]): コピー・移動元の範囲内パスのリスト
            to_fwpaths (List[str]): コピー・移動先の範囲内パスのリスト
            from_rjpaths (List[str]): コピー・移動元の範囲外パスのリスト
            to_rjpaths (List[str]): コピー・移動先の範囲外パスのリスト
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報

        Returns:
            int: レスポンスコード
        """
        try:
            f = filer.Filer(data_dir, logger)
            rescode, msg = f.file_is(file_func, svpath=svpath, from_path=from_path, to_path=to_path,
                                     fwpaths=fwpaths, rjpaths=rjpaths,
                                     from_fwpaths=from_fwpaths, to_fwpaths=to_fwpaths,
                                     from_rjpaths=from_rjpaths, to_rjpaths=to_rjpaths)
            redis_cli.rpush(reskey, msg)
            return rescode
        except Exception as e:
            logger.warning(f"Failed to check file operation: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to check file operation: {e}"))
            return self.RESP_WARN
