from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class ExtractSave(feature.OneshotResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'extract'

    def get_cmd(self) -> str:
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'save'

    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="指定されたファイルからテキストを抽出する設定を保存します。",
            description_en="Saves settings for extracting text from the specified file.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                     description_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。",
                     description_en="Specify the service name of the inference server."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。",
                     description_en="Specifies the number of reconnections to the Redis server."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default=120, required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="extract_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="抽出設定の名前を指定します。",
                     description_en="Specify the name of the extraction configuration."),
                dict(opt="extract_type", type=Options.T_STR, default='pdf_file', required=True, multi=False, hide=False,
                     choice=['', 'pdf_file'],
                     choice_show=dict(
                        pdf_file=["extract_scope", "client_data", "loadpath", "loadgrep", ],
                     ),
                     description_ja="抽出の種類を指定します。",
                     description_en="Specify the type of extraction."),
                dict(opt="extract_scope", type=Options.T_STR, default="client", required=False, multi=False, hide=False, choice=["", "client", "server"],
                     description_ja="参照先スコープを指定します。指定可能な画像タイプは `client` , `server` です。",
                     description_en="Specify the reference scope. The available image types are `client` and `server`.",),
                dict(opt="client_data", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="ローカルを参照させる場合のデータフォルダのパスを指定します。",
                     description_en="Specify the path of the data folder when local is referenced."),
                dict(opt="loadpath", type=Options.T_DIR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="読み込み元パスを指定します。",
                     description_en="Specify the source path."),
                dict(opt="loadgrep", type=Options.T_STR, default="*", required=True, multi=False, hide=False, choice=None,
                     description_ja="読込みgrepパターンを指定します。",
                     description_en="Specifies a load grep pattern."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                    description_ja="処理結果jsonの保存先ファイルを指定。",
                    description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="処理結果jsonファイルを追記保存します。",
                    description_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                    description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
            ]
        )

    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if not hasattr(args, 'extract_name') or args.extract_name is None:
            msg = dict(warn="Please specify --extract_name")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not re.match(r'^[\w\-]+$', args.extract_name):
            msg = dict(warn="Extract name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not hasattr(args, 'extract_type') or args.extract_type is None:
            msg = dict(warn="Please specify --extract_type")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        # Build payload
        payload = dict(
            extract_name=args.extract_name,
            extract_type=args.extract_type,
            extract_scope=args.extract_scope if hasattr(args, 'extract_scope') else None,
            client_data=args.client_data if hasattr(args, 'client_data') else None,
            loadpath=args.loadpath if hasattr(args, 'loadpath') else None,
            loadgrep=args.loadgrep if hasattr(args, 'loadgrep') else None,
        )

        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            configure = json.loads(convert.b64str2str(msg[2]))
            configure_path = data_dir / ".agent" / f"extract-{configure['extract_name']}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            with configure_path.open('w', encoding='utf-8') as f:
                json.dump(configure, f, indent=4)
            msg = dict(success=f"Extract configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN
