from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class AgentLLMSave(feature.OneshotResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'llm_save'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="LLM 設定を保存します。",
            description_en="Saves LLM configuration.",
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
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="llmname", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="保存するLLM設定の名前を指定します。",
                     description_en="Specify the name of the LLM configuration to save."),
                dict(opt="llmprov", type=Options.T_STR, default=None, required=True, multi=False, hide=False,
                     choice=["", "azureopenai", "openai", "vertexai", "ollama"],
                     description_ja="llmのプロバイダを指定します。",
                     description_en="Specify llm provider.",
                     choice_show=dict(azureopenai=["llmapikey", "llmendpoint", "llmmodel", "llmapiversion"],
                                      openai=["llmapikey", "llmendpoint", "llmmodel"],
                                      vertexai=["llmprojectid", "llmsvaccountfile", "llmlocation", "llmmodel", "llmseed", "llmtemperature"],
                                      ollama=["llmendpoint", "llmmodel", "llmtemperature"],),
                     ),
                dict(opt="llmprojectid", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのプロバイダ接続のためのプロジェクトIDを指定します。",
                     description_en="Specify the project ID for llm's provider connection."),
                dict(opt="llmsvaccountfile", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="llmのプロバイダ接続のためのサービスアカウントファイルを指定します。",
                     description_en="Specifies the service account file for llm's provider connection."),
                dict(opt="llmlocation", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのプロバイダ接続のためのロケーションを指定します。",
                     description_en="Specifies the location for llm provider connections."),
                dict(opt="llmapikey", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのプロバイダ接続のためのAPIキーを指定します。",
                     description_en="Specify API key for llm provider connection."),
                dict(opt="llmapiversion", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのプロバイダ接続のためのAPIバージョンを指定します。",
                     description_en="Specifies the API version for llm provider connections."),
                dict(opt="llmendpoint", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのプロバイダ接続のためのエンドポイントを指定します。",
                     description_en="Specifies the endpoint for llm provider connections."),
                dict(opt="llmmodel", type=Options.T_STR, default="text-multilingual-embedding-002", required=False, multi=False, hide=False, choice=None,
                     description_ja="llmモデルを指定します。",
                     description_en="Specifies the llm model."),
                dict(opt="llmseed", type=Options.T_INT, default=13, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmモデルを使用するときのシード値を指定します。",
                     description_en="Specifies the seed value when using llm model."),
                dict(opt="llmtemperature", type=Options.T_FLOAT, default=0.1, required=False, multi=False, hide=False, choice=None,
                     description_ja="llmのモデルを使用するときのtemperatureを指定します。",
                     description_en="Specifies the temperature when using llm model."),
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

    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if not hasattr(args, 'llmname') or args.llmname is None:
            msg = dict(warn="Please specify --llmname")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not hasattr(args, 'llmprov') or args.llmprov is None:
            msg = dict(warn="Please specify --llmprov")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not re.match(r'^[\w\-]+$', args.llmname):
            msg = dict(warn="LLM name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        configure = dict(
            llmname=args.llmname,
            llmprov=args.llmprov,
            llmprojectid=args.llmprojectid if hasattr(args, 'llmprojectid') else None,
            llmsvaccountfile=args.llmsvaccountfile if hasattr(args, 'llmsvaccountfile') else None,
            llmlocation=args.llmlocation if hasattr(args, 'llmlocation') else None,
            llmapikey=args.llmapikey if hasattr(args, 'llmapikey') else None,
            llmapiversion=args.llmapiversion if hasattr(args, 'llmapiversion') else None,
            llmendpoint=args.llmendpoint if hasattr(args, 'llmendpoint') else None,
            llmmodel=args.llmmodel if hasattr(args, 'llmmodel') else None,
            llmseed=args.llmseed if hasattr(args, 'llmseed') else None,
            llmtemperature=args.llmtemperature if hasattr(args, 'llmtemperature') else None,
        )

        if hasattr(args, 'llmsvaccountfile') and args.llmsvaccountfile is not None:
            svaccount_path = Path(args.llmsvaccountfile)
            if not svaccount_path.exists():
                msg = dict(warn=f"The specified llmsvaccountfile '{args.llmsvaccountfile}' does not exist.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            try:
                with svaccount_path.open('r', encoding='utf-8') as f:
                    configure['llmsvaccountfile_data'] = json.load(f)
            except Exception as e:
                msg = dict(warn=f"Failed to load the specified llmsvaccountfile '{args.llmsvaccountfile}': {str(e)}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        configure_b64 = convert.str2b64str(common.to_str(configure))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [configure_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
                return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

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
        reskey = msg[1]
        try:
            configure = json.loads(convert.b64str2str(msg[2]))

            configure_path = data_dir / ".agent" / f"llm-{configure['llmname']}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            with configure_path.open('w', encoding='utf-8') as f:
                json.dump(configure, f, indent=4)
            msg = dict(success=f"LLM configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN
