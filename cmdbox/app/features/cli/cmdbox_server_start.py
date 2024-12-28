from cmdbox.app import common, server
from cmdbox.app.feature import Feature
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class ServerStart(Feature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'server'

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
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_TRUE,
            discription_ja="サーバーを起動します。installモードで `cmdbox -m install -c server` を実行している場合は、 `docker-compose up -d` を使用してください。",
            discription_en="Start the inference server. If you are running `cmdbox -m install -c server` in install mode, use `docker-compose up -d`.",
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
                dict(opt="data", type="file", default=common.HOME_DIR / f".{self.ver.__appid__}", required=False, multi=False, hide=False, choice=None,
                        discription_ja="省略した時は `$HONE/.cmdbox` を使用します。",
                        discription_en="When omitted, `$HONE/.cmdbox` is used."),
                dict(opt="retry_count", type="int", default=20, required=False, multi=False, hide=True, choice=None,
                        discription_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                        discription_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type="int", default=5, required=False, multi=False, hide=True, choice=None,
                        discription_ja="Redisサーバーに再接続までの秒数を指定します。",
                        discription_en="Specifies the number of seconds before reconnecting to the Redis server."),
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
            msg = {"warn":f"Please specify the --data option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg
        if args.svname is None:
            msg = {"warn":f"Please specify the --svname option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg
        sv = server.Server(Path(args.data), logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        sv.start_server(args.retry_count, args.retry_interval)

        return 0, {"warn":f"server stoped. svname={sv.svname}"}, sv
