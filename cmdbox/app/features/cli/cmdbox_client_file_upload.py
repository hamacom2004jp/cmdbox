from cmdbox.app import common, client, filer
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.feature import Feature
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class ClientFileUpload(Feature):
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
        return 'file_upload'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_MEIGHT,
            discription_ja="データフォルダ配下にファイルをアップロードします。",
            discription_en="Upload a file under the data folder.",
            choice=[
                dict(opt="host", type="str", default=self.default_host, required=True, multi=False, hide=True, choice=None,
                        discription_ja="Redisサーバーのサービスホストを指定します。",
                        discription_en="Specify the service host of the Redis server."),
                dict(opt="port", type="int", default=self.default_port, required=True, multi=False, hide=True, choice=None,
                        discription_ja="Redisサーバーのサービスポートを指定します。",
                        discription_en="Specify the service port of the Redis server."),
                dict(opt="password", type="str", default=self.default_pass, required=True, multi=False, hide=True, choice=None,
                        discription_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                        discription_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type="str", default="server", required=True, multi=False, hide=True, choice=None,
                        discription_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                        discription_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="svpath", type="str", default="/", required=True, multi=False, hide=False, choice=None,
                        discription_ja="サーバーのデータフォルダ以下のパスを指定します。",
                        discription_en="Specify the directory path to get the list of files.",
                        test_true={"server":"/file_server/upload",
                                "client":"/file_client/upload",
                                "current":"/file_current/upload"}),
                dict(opt="scope", type="str", default="client", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                        discription_ja="参照先スコープを指定します。指定可能な画像タイプは `client` , `current` , `server` です。",
                        discription_en="Specifies the scope to be referenced. When omitted, 'client' is used.",
                        test_true={"server":"server",
                                "client":"client",
                                "current":"current"}),
                dict(opt="upload_file", type="file", default="", required=False, multi=False, hide=False, choice=None, fileio="out",
                        discription_ja="クライアントのアップロード元パスを指定します。",
                        discription_en="Specify the source path of the client.",
                        test_true={"server":"tests/dog.jpg"}),
                dict(opt="client_data", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                        discription_ja="ローカルを参照させる場合のデータフォルダのパスを指定します。",
                        discription_en="Specify the path of the data folder when local is referenced.",
                        choice_show=dict(client=["client_data"]),
                        test_true={"server":None,
                                "client":common.HOME_DIR / f".{self.ver.__appid__}",
                                "current":None}),
                dict(opt="mkdir", type="bool", default=False, required=False, multi=False, hide=True, choice=[True, False],
                        discription_ja="中間フォルダがない場合作成します。",
                        discription_en="If there is no in between folder, create one.",
                        test_true={"server":True}),
                dict(opt="orverwrite", type="bool", default=False, required=False, multi=False, hide=True, choice=[True, False],
                        discription_ja="アップロード先に存在していても上書きします。",
                        discription_en="Overwrites the file even if it exists at the upload destination."),
                dict(opt="retry_count", type="int", default=3, required=False, multi=False, hide=True, choice=None,
                        discription_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                        discription_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type="int", default=5, required=False, multi=False, hide=True, choice=None,
                        discription_ja="Redisサーバーに再接続までの秒数を指定します。",
                        discription_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type="int", default="15", required=False, multi=False, hide=True, choice=None,
                        discription_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                        discription_en="Specify the maximum waiting time until the server responds."),
                dict(opt="output_json", short="o", type="file", default="", required=False, multi=False, hide=True, choice=None, fileio="out",
                        discription_ja="処理結果jsonの保存先ファイルを指定。",
                        discription_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type="bool", default=False, required=False, multi=False, hide=True, choice=[True, False],
                        discription_ja="処理結果jsonファイルを追記保存します。",
                        discription_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choice=[True, False],
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                        discription_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choice=[True, False],
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                        discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type="int", default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                        discription_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )
    
    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'file_upload'

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
        if args.svname is None:
            msg = {"warn":f"Please specify the --svname option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)

        client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
        upload_file = Path(args.upload_file.replace('"','')) if args.upload_file is not None else None
        ret = cl.file_upload(args.svpath.replace('"',''), upload_file, scope=args.scope, client_data=client_data,
                             mkdir=args.mkdir, orverwrite=args.orverwrite,
                             retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return 1, ret, cl

        return 0, ret, cl

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return True

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
        svpath = convert.b64str2str(msg[2])
        file_name = convert.b64str2str(msg[3])
        file_data = convert.b64str2bytes(msg[4])
        mkdir = msg[5]=='True'
        orverwrite = msg[6]=='True'
        st = self.file_upload(msg[1], svpath, file_name, file_data, mkdir, orverwrite, data_dir, logger, redis_cli, sessions)
        return st

    def file_upload(self, reskey:str, current_path:str, file_name:str, file_data:bytes, mkdir:bool, orverwrite:bool,
                    data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        ファイルをアップロードする

        Args:
            reskey (str): レスポンスキー
            current_path (str): ファイルパス
            file_name (str): ファイル名
            file_data (bytes): ファイルデータ
            mkdir (bool): ディレクトリを作成するかどうか
            orverwrite (bool): 上書きするかどうか
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報

        Returns:
            int: レスポンスコード
        """
        try:
            f = filer.Filer(data_dir, logger)
            rescode, msg = f.file_upload(current_path, file_name, file_data, mkdir, orverwrite)
            redis_cli.rpush(reskey, msg)
            return rescode
        except Exception as e:
            logger.warning(f"Failed to upload file: {e}", exc_info=True)
            redis_cli.rpush(reskey, {"warn": f"Failed to upload file: {e}"})
            return self.RESP_WARN


