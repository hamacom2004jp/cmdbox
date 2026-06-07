from cmdbox.app import common, client, filer, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class ClientFileCopy(feature.UnsupportEdgeFeature, validator.Validator, limiter.LimitedFeature):
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
        return 'file_copy'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=True,
            description_ja="サーバー側のデータフォルダ配下のファイルをコピーします。",
            description_en="Copy the files under the data folder on the server side.",
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
                dict(opt="from_path", type=Options.T_FILE, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="サーバーのデータフォルダ以下のコピー元パスを指定します。",
                     description_en="Specify the copy source path under the data folder of the inference server.",
                     test_true={"server":"/file_server/upload/dog.jpg",
                                "client":"/file_client/upload/dog.jpg",
                                "current":"/file_current/upload/dog.jpg"}),
                dict(opt="to_path", type=Options.T_FILE, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="サーバーのデータフォルダ以下のコピー先パスを指定します。",
                     description_en="Specify the path to copy under the data folder of the inference server.",
                     test_true={"server":"/file_server/upload/dog2.jpg",
                                "client":"/file_client/upload/dog2.jpg",
                                "current":"/file_current/upload/dog2.jpg"}),
                dict(opt="from_fwpath", type=Options.T_FILE, default=None, required=True, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが範囲外であるかどうかを判定するパスを指定します。このパスの配下でない場合エラーにします。",
                     description_en="Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error.",),
                dict(opt="to_fwpath", type=Options.T_FILE, default=None, required=True, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが範囲外であるかどうかを判定するパスを指定します。このパスの配下でない場合エラーにします。",
                     description_en="Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error.",),
                dict(opt="from_rjpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが要求されたパスにマッチする場合、アクセスが拒否されます。正規表現として解釈します。",
                     description_en="If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."),
                dict(opt="to_rjpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが要求されたパスにマッチする場合、アクセスが拒否されます。正規表現として解釈します。",
                     description_en="If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."),
                dict(opt="overwrite", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="コピー先に存在していても上書きします。",
                     description_en="Overwrites the copy even if it exists at the destination.",
                     test_true={"server":True,
                                "client":False,
                                "current":False}),
                dict(opt="scope", type=Options.T_STR, default="client", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="スコープを指定します。`client` はクライアント側、`server` はサーバー側です。`current` は実行時ディレクトリです。",
                     description_en="Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory.",),
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

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'file_copy'

    @limiter.apprun_check_limit
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

        client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
        from_fwpaths = [p.replace('"','') for p in args.from_fwpath] if args.from_fwpath is not None else ["/"]
        to_fwpaths = [p.replace('"','') for p in args.to_fwpath] if args.to_fwpath is not None else ["/"]
        from_rjpaths = [p.replace('"','') for p in args.from_rjpath] if args.from_rjpath is not None else []
        to_rjpaths = [p.replace('"','') for p in args.to_rjpath] if args.to_rjpath is not None else []
        ret = cl.file_copy(args.from_path.replace('"',''), args.to_path.replace('"',''), overwrite=args.overwrite,
                           from_fwpaths=from_fwpaths, to_fwpaths=to_fwpaths,
                           from_rjpaths=from_rjpaths, to_rjpaths=to_rjpaths,
                           scope=args.scope, client_data=client_data,
                           retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, cl

        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            path: Union[str, Path, None] = pydantic.Field(default=None, description="パス")
            to_path: Union[str, Path, None] = pydantic.Field(default=None, description="コピー先・移動先のパス")
            from_path: Union[str, Path, None] = pydantic.Field(default=None, description="コピー元・移動元のパス")
            ret_path: Union[str, Path, None] = pydantic.Field(default=None, description="戻りのパス")
            msg: Union[str, None] = pydantic.Field(default=None, description="処理結果のメッセージ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return True

    @limiter.svrun_check_limit
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
        from_path = payload.get("from_path")
        to_path = payload.get("to_path")
        overwrite = payload.get("overwrite", False)=='True' or payload.get("overwrite", False) is True
        from_fwpaths = payload.get("from_fwpaths", None)
        to_fwpaths = payload.get("to_fwpaths", None)
        from_rjpaths = payload.get("from_rjpaths", None)
        to_rjpaths = payload.get("to_rjpaths", None)
        st = self.file_copy(msg[1], from_path, to_path, overwrite,
                            from_fwpaths, to_fwpaths, from_rjpaths, to_rjpaths,
                            data_dir, logger, redis_cli, sessions)
        return st

    def apprun_registrations(self, data_dir, logger, args, msg):
        total_size = sum(f.stat().st_size for f in data_dir.rglob('*') if f.is_file())
        return total_size

    def svrun_registrations(self, data_dir, logger, opt, msg):
        total_size = sum(f.stat().st_size for f in data_dir.rglob('*') if f.is_file())
        return total_size

    def file_copy(self, reskey:str, from_path:str, to_path:str, overwrite:bool,
                  from_fwpaths:List[str], to_fwpaths:List[str], 
                  from_rjpaths:List[str], to_rjpaths:List[str],
                  data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        ファイルをコピーする

        Args:
            reskey (str): レスポンスキー
            from_path (str): コピー元ファイルパス
            to_path (str): コピー先ファイルパス
            overwrite (bool): 上書きするかどうか
            from_fwpaths (List[str], optional): 範囲内かどうかを示すパスのリスト. Defaults to None.
            to_fwpaths (List[str], optional): 範囲内かどうかを示すパスのリスト. Defaults to None.
            from_rjpaths (List[str], optional): 範囲外かどうかを示すパスのリスト. Defaults to None.
            to_rjpaths (List[str], optional): 範囲外かどうかを示すパスのリスト. Defaults to None.
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報

        Returns:
            int: レスポンスコード
        """
        try:
            f = filer.Filer(data_dir, logger)
            rescode, msg = f.file_copy(from_path, to_path, overwrite, from_fwpaths, to_fwpaths, from_rjpaths, to_rjpaths)
            redis_cli.rpush(reskey, msg)
            return rescode
        except Exception as e:
            logger.warning(f"Failed to copy file: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to copy file: {e}"))
            return self.RESP_WARN

