from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class LimiterSave(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'save'

    def get_option(self) -> Dict[str, Any]:
        op = Options.getInstance(self.appcls, self.ver)
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="コマンド実行に対する量的な制限設定を追加/保存します。",
            description_en="Adds or saves quantitative restriction settings for command execution.",
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
                     description_en="Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定します。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="limiter_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="制限設定の識別名を指定します。",
                     description_en="Specify the identifier name of the limiter configuration."),
                dict(opt="scope", type=Options.T_STR, default="server", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="スコープを指定します。`client` はクライアント側、`server` はサーバー側です。`current` は実行時ディレクトリです。",
                     description_en="Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory.",),
                dict(opt="target_mode", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     choice_fn=lambda o, webmode, opt: ['']+op.get_mode_keys(),
                     description_ja="制限を適用する対象コマンドのモード名を指定します。",
                     description_en="Specify the mode name of the target command to apply the restriction. If omitted, all modes are targeted."),
                dict(opt="target_cmd", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                     callcmd="async () => {"
                             + "const res = await get_cmds($(\"[name='target_mode']\").val());"
                             + "const py_load_cmd = await cmdbox.load_cmd($(\"[name='title']\").val());"
                             + "const val = py_load_cmd['target_cmd'];"
                             + "$(\"[name='target_cmd']\").empty();"
                             + "res.map(elm=>{$(\"[name='target_cmd']\").append('<option value=\"'+elm+'\">'+elm+'</option>');});"
                             + "$(\"[name='target_cmd']\").val(val);"
                             + "}",
                     description_ja="制限を適用する対象コマンドのコマンド名を指定します。",
                     description_en="Specify the command name of the target command to apply the restriction. If omitted, all commands are targeted."),
                dict(opt="target_option", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="制限を適用する対象コマンドの条件をdict形式で指定します。keyにコマンドオプション名、valにオプションの値を指定します。",
                     description_en="Specify the conditions for the commands to which the restrictions apply in dictionary format. Specify the command option name as the key and the option value as the value."),
                dict(opt="max_registrations", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="登録最大数（又は登録最大サイズ）を指定します。省略時は制限しません。",
                     description_en="Specify the maximum number of registrations (or maximum registration size). If omitted, no limit is applied."),
                dict(opt="max_total_count", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="コマンドの実行最大回数を指定します。省略時は制限しません。",
                     description_en="Specify the maximum number of command executions. If omitted, no limit is applied."),
                dict(opt="max_total_time", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="コマンドの実行可能総時間（秒）を指定します。省略時は制限しません。",
                     description_en="Specify the total executable time in seconds for the command. If omitted, no limit is applied."),
                dict(opt="max_total_input", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="入力の総バイト数の上限を指定します。省略時は制限しません。",
                     description_en="Specify the maximum total number of input bytes. If omitted, no limit is applied."),
                dict(opt="max_total_process", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="処理の総バイト数の上限を指定します。省略時は制限しません。",
                     description_en="Specify the maximum total number of process bytes. If omitted, no limit is applied."),
                dict(opt="max_total_output", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="出力の総バイト数の上限を指定します。省略時は制限しません。",
                     description_en="Specify the maximum total number of output bytes. If omitted, no limit is applied."),
                dict(opt="max_total_credits", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="コマンドの最大クレジット数を指定します。省略時は制限しません。",
                     description_en="Specify the maximum number of credits. If omitted, no limit is applied."),
                dict(opt="service_credits", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="サービスクレジット数を指定します。",
                     description_en="Specify the number of service credits."),
                dict(opt="exec_period_start", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="コマンドの実行可能期間の開始日時を指定します（例: 2024-01-01T00:00:00）。省略時は制限しません。",
                     description_en="Specify the start datetime of the executable period for the command (e.g. 2024-01-01T00:00:00). If omitted, no limit is applied."),
                dict(opt="exec_period_end", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="コマンドの実行可能期間の終了日時を指定します（例: 2024-12-31T23:59:59）。省略時は制限しません。",
                     description_en="Specify the end datetime of the executable period for the command (e.g. 2024-12-31T23:59:59). If omitted, no limit is applied."),
                dict(opt="refresh_datetime", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="この制限をリセットする日時を指定します（例: 2024-06-01T00:00:00）。指定した日時になると制限カウンタをリセットします。省略時はリセットしません。",
                     description_en="Specify the datetime to reset this restriction (e.g. 2024-06-01T00:00:00). The restriction counters are reset at the specified datetime. If omitted, no reset is performed."),
                dict(opt="refresh_interval", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="この制限をリセットするまでの時間（秒）を指定します。指定した秒数が経過すると制限カウンタをリセットします。省略時はリセットしません。",
                     description_en="Specify the interval in seconds after which this restriction is reset. The restriction counters are reset when the specified number of seconds has elapsed. If omitted, no reset is performed."),
                dict(opt="max_history_interval", type=Options.T_INT, default=3600*24*31, required=True, multi=False, hide=False, choice=None,
                     description_ja="カウンター履歴を保持する最大期間（秒）を指定します。指定した秒数を超えた履歴は削除されます。",
                     description_en="Specify the maximum duration (in seconds) for which counter history will be retained. History older than the specified number of seconds will be deleted."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if args.scope not in ['client', 'server']:
            result = dict(warn="Limiters are supported only in the “client” and “server” scopes.")
            logger.warning("Limiters are supported only in the “client” and “server” scopes.")
            common.print_format(result, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, result, None
        if args.max_history_interval and args.max_history_interval <= 120:
            result = dict(warn="max_history_interval should be greater than 120 seconds.")
            logger.warning("max_history_interval should be greater than 120 seconds.")
            common.print_format(result, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, result, None

        configure = dict(
            scope=args.scope,
            limiter_name=args.limiter_name,
            target_mode=args.target_mode if hasattr(args, 'target_mode') else None,
            target_cmd=args.target_cmd if hasattr(args, 'target_cmd') else None,
            target_option=args.target_option if hasattr(args, 'target_option') else None,
            max_total_count=args.max_total_count if hasattr(args, 'max_total_count') else None,
            max_registrations=args.max_registrations if hasattr(args, 'max_registrations') else None,
            max_total_time=args.max_total_time if hasattr(args, 'max_total_time') else None,
            max_total_input=args.max_total_input if hasattr(args, 'max_total_input') else None,
            max_total_process=args.max_total_process if hasattr(args, 'max_total_process') else None,
            max_total_output=args.max_total_output if hasattr(args, 'max_total_output') else None,
            max_total_credits=args.max_total_credits if hasattr(args, 'max_total_credits') else None,
            service_credits=args.service_credits if hasattr(args, 'service_credits') else None,
            exec_period_start=str(args.exec_period_start) if hasattr(args, 'exec_period_start') and args.exec_period_start is not None else None,
            exec_period_end=str(args.exec_period_end) if hasattr(args, 'exec_period_end') and args.exec_period_end is not None else None,
            refresh_datetime=str(args.refresh_datetime) if hasattr(args, 'refresh_datetime') and args.refresh_datetime is not None else None,
            refresh_interval=args.refresh_interval if hasattr(args, 'refresh_interval') else None,
            max_history_interval=args.max_history_interval if hasattr(args, 'max_history_interval') else None,
        )

        if args.scope == 'client':
            client_data = args.client_data if hasattr(args, 'client_data') else None
            if not client_data:
                result = dict(warn="client_data is required when scope is 'client'.")
                logger.warning("client_data is required when scope is 'client'.")
                common.print_format(result, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, result, None
            data_dir = Path(client_data)
            configure_path = data_dir / ".limiter" / f"limiter-{args.limiter_name}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            common.save_file(configure_path, lambda f: json.dump(configure, f, indent=4), encoding='utf-8', nolock=False)
            out = dict(success=f"Limiter configuration saved to '{str(configure_path)}'.")
            common.print_format(out, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, out, None

        # scope == 'server'
        configure_b64 = convert.str2b64str(common.to_str(configure))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [configure_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: Union[str, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            configure = json.loads(convert.b64str2str(msg[2]))

            limiter_name = configure.get('limiter_name')
            if not limiter_name:
                out = dict(warn="limiter_name is required.")
                redis_cli.rpush(reskey, out)
                return self.RESP_WARN

            configure_path = data_dir / ".limiter" / f"limiter-{limiter_name}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            common.save_file(configure_path, lambda f: json.dump(configure, f, indent=4), encoding='utf-8', nolock=False)
            out = dict(success=f"Limiter configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, out)
            return self.RESP_SUCCESS

        except Exception as e:
            out = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, out)
            return self.RESP_WARN
