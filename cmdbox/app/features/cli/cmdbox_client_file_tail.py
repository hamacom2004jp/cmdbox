from cmdbox.app import common, client, feature, filer
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class ClientFileTail(feature.OneshotResultEdgeFeature, validator.Validator):
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
        return 'file_tail'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=True,
            description_ja="データフォルダ配下のログファイル末尾を取得します。",
            description_en="Get tail contents of a log file under the data folder.",
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
                dict(opt="svpath", type=Options.T_FILE, default="/.logs/cmdbox_server.log", required=True, multi=False, hide=False, choice=None,
                     description_ja="読み取るファイルパスを指定します。",
                     description_en="Specify the file path to read."),
                dict(opt="fwpath", type=Options.T_FILE, default=None, required=True, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが範囲外であるかどうかを判定するパスを指定します。このパスの配下でない場合エラーにします。",
                     description_en="Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."),
                dict(opt="rjpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが要求されたパスにマッチする場合、アクセスが拒否されます。正規表現として解釈します。",
                     description_en="If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."),
                dict(opt="scope", type=Options.T_STR, default="server", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="スコープを指定します。`client` はクライアント側、`server` はサーバー側です。`current` は実行時ディレクトリです。",
                     description_en="Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory."),
                dict(opt="offset", type=Options.T_INT, default=-1, required=False, multi=False, hide=False, choice=None,
                     description_ja="読み取り開始位置のオフセット(byte)を指定します。-1 は末尾から取得します。",
                     description_en="Specify the read start byte offset. -1 reads from the end of the file."),
                dict(opt="lines", type=Options.T_INT, default=200, required=False, multi=False, hide=False, choice=None,
                     description_ja="返却する最大行数を指定します。",
                     description_en="Specify the maximum number of lines to return."),
                dict(opt="max_bytes", type=Options.T_INT, default=65536, required=False, multi=False, hide=False, choice=None,
                     description_ja="1回で読み取る最大バイト数を指定します。",
                     description_en="Specify the maximum bytes to read in one request."),
                dict(opt="encoding", type=Options.T_STR, default="utf-8", required=False, multi=False, hide=False, choice=None,
                     description_ja="ログファイルのデコード時に使用する文字コードを指定します。",
                     description_en="Specify the character encoding used to decode the log file."),
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
    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[] ) -> Tuple[int, Dict[str, Any], Any]:
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

        client_data = Path(str(args.client_data).replace('"','')) if args.client_data is not None else None
        args.fwpath = args.fwpath if isinstance(args.fwpath, list) else [args.fwpath] if args.fwpath is not None and args.fwpath != "********" else []
        args.rjpath = args.rjpath if isinstance(args.rjpath, list) else [args.rjpath] if args.rjpath is not None and args.rjpath != "********" else []
        fwpaths = [str(p).replace('"','') for p in args.fwpath]
        rjpaths = [str(p).replace('"','') for p in args.rjpath]

        ret = cl.file_tail(
            svpath=str(args.svpath).replace('"',''),
            scope=args.scope,
            client_data=client_data,
            fwpaths=fwpaths,
            rjpaths=rjpaths,
            offset=args.offset,
            lines=args.lines,
            max_bytes=args.max_bytes,
            encoding=args.encoding,
            retry_count=args.retry_count,
            retry_interval=args.retry_interval,
            timeout=args.timeout,
        )
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, cl

        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            name: Union[str, None] = pydantic.Field(default=None, description="名前")
            svpath: Union[str, Path, None] = pydantic.Field(default=None, description="サーバーパス")
            data: Union[str, None] = pydantic.Field(default=None, description="処理結果のデータ")
            lines: Union[List[str], None] = pydantic.Field(default=None, description="ログ行")
            offset: Union[int, None] = pydantic.Field(default=None, description="次回読み取りオフセット")
            file_size: Union[int, None] = pydantic.Field(default=None, description="ファイルサイズ")
            etag: Union[str, None] = pydantic.Field(default=None, description="ETag")
            not_modified: Union[bool, None] = pydantic.Field(default=None, description="更新なしフラグ")
            rotated: Union[bool, None] = pydantic.Field(default=None, description="ローテーション検知フラグ")
            encoding: Union[str, None] = pydantic.Field(default=None, description="文字コード")
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
        svpath = payload.get('svpath', '/')
        fwpaths = payload.get('fwpaths', None)
        rjpaths = payload.get('rjpaths', None)
        offset = payload.get('offset', -1)
        lines = payload.get('lines', 200)
        max_bytes = payload.get('max_bytes', 65536)
        encoding = payload.get('encoding', 'utf-8')
        st = self.file_tail(msg[1], svpath, fwpaths, rjpaths, offset, lines, max_bytes, encoding,
                            data_dir, logger, redis_cli, sessions)
        return st

    def file_tail(self, reskey:str, current_path:str, fwpaths:List[str], rjpaths:List[str],
                  offset:int, lines:int, max_bytes:int, encoding:str,
                  data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient,
                  sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        ファイル末尾を取得する

        Args:
            reskey (str): レスポンスキー
            current_path (str): ファイルパス
            fwpaths (List[str]): 範囲内かどうかを示すパスのリスト
            rjpaths (List[str]): 範囲外かどうかを示すパスのリスト
            offset (int): 読み取り開始オフセット
            lines (int): 返却行数
            max_bytes (int): 最大読み取りバイト数
            encoding (str): 文字コード
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報

        Returns:
            int: レスポンスコード
        """
        try:
            f = filer.Filer(data_dir, logger)
            rescode, msg = f.file_tail(current_path, offset=offset, lines=lines, max_bytes=max_bytes,
                                       encoding=encoding, fwpaths=fwpaths, rjpaths=rjpaths)
            redis_cli.rpush(reskey, msg)
            return rescode
        except Exception as e:
            logger.warning(f"Failed to tail file: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to tail file: {e}"))
            return self.RESP_WARN
