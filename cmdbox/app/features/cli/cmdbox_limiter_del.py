from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class LimiterDel(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'del'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="制限設定を削除します。",
            description_en="Deletes a limiter configuration.",
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
                     description_ja="削除する制限設定の識別名を指定します。",
                     description_en="Specify the identifier name of the limiter configuration to delete."),
                dict(opt="scope", type=Options.T_STR, default="server", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="削除先スコープを指定します。`client` はクライアントローカル、`server` はサーバー側から削除します。`current` は未サポートです。",
                     description_en="Specify the delete scope. `client` deletes from the client local, `server` deletes from the server side. `current` is not supported.",),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:

        if args.scope not in ['client', 'server']:
            result = dict(warn="Limiters are supported only in the “client” and “server” scopes.")
            logger.warning("Limiters are supported only in the “client” and “server” scopes.")
            common.print_format(result, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, result, None

        if args.scope == 'client':
            client_data = args.client_data if hasattr(args, 'client_data') else None
            if not client_data:
                result = dict(warn="client_data is required when scope is 'client'.")
                logger.warning("client_data is required when scope is 'client'.")
                common.print_format(result, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, result, None
            configure_path = Path(client_data) / ".limiter" / f"limiter-{args.limiter_name}.json"
            if not configure_path.exists():
                result = dict(warn=f"Limiter configuration '{args.limiter_name}' not found at '{configure_path}'.")
                logger.warning(f"Limiter configuration '{args.limiter_name}' not found at '{configure_path}'.")
                common.print_format(result, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, result, None
            configure_path.unlink()
            out = dict(success=f"Limiter configuration '{args.limiter_name}' deleted from '{configure_path}'.")
            common.print_format(out, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, out, None

        # scope == 'server'
        payload = dict(limiter_name=args.limiter_name)
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
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
            payload = json.loads(convert.b64str2str(msg[2]))
            limiter_name = payload.get('limiter_name')
            if not limiter_name:
                result = dict(warn="limiter_name is required.")
                redis_cli.rpush(reskey, result)
                return self.RESP_WARN

            configure_path = data_dir / ".limiter" / f"limiter-{limiter_name}.json"
            if not configure_path.exists():
                result = dict(warn=f"Limiter configuration '{limiter_name}' not found at '{configure_path}'.")
                redis_cli.rpush(reskey, result)
                return self.RESP_WARN

            configure_path.unlink()
            result = dict(success=f"Limiter configuration '{limiter_name}' deleted from '{configure_path}'.")
            redis_cli.rpush(reskey, result)
            return self.RESP_SUCCESS

        except Exception as e:
            result = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, result)
            return self.RESP_WARN
