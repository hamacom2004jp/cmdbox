from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class LimiterCounter(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'counter'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="制限設定のカウンターを取得します。",
            description_en="Gets the counter for a limiter configuration.",
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
                     description_ja="カウンターを取得する制限設定の識別名を指定します。",
                     description_en="Specify the identifier name of the limiter configuration to get the counter for."),
                dict(opt="scope", type=Options.T_STR, default="server", required=True, multi=False, hide=False, choice=["client", "server"],
                     description_ja="参照先スコープを指定します。`client` はクライアントローカル、`server` はサーバー側から取得します。",
                     description_en="Specify the reference scope. `client` loads from the client local, `server` loads from the server side.",),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        scope = args.scope if hasattr(args, 'scope') else 'server'

        if scope not in ['client', 'server']:
            result = dict(warn="Limiters are supported only in the 'client' and 'server' scopes.")
            logger.warning("Limiters are supported only in the 'client' and 'server' scopes.")
            common.print_format(result, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, result, None

        if scope == 'client':
            client_data = args.client_data if hasattr(args, 'client_data') else None
            if not client_data:
                result = dict(warn="client_data is required when scope is 'client'.")
                logger.warning("client_data is required when scope is 'client'.")
                common.print_format(result, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, result, None
            redis_cli = redis_client.RedisClient(logger, host=args.host, port=args.port, password=args.password, svname=args.svname)
            lmt = limiter.Limiter(redis_client=redis_cli)
            counter = lmt.load_counter(Path(client_data), args.limiter_name)
            out = dict(success=dict(data=counter))
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
        class Counter(resdata.Base):
            limiter_name: Union[str, None] = pydantic.Field(default=None, description="制限設定の識別名")
            total_count: Union[int, None] = pydantic.Field(default=None, description="実行回数")
            total_time: Union[float, None] = pydantic.Field(default=None, description="実行総時間（秒）")
            total_input: Union[int, None] = pydantic.Field(default=None, description="入力総バイト数")
            total_process: Union[int, None] = pydantic.Field(default=None, description="処理総バイト数")
            total_output: Union[int, None] = pydantic.Field(default=None, description="出力総バイト数")
            total_registrations: Union[int, None] = pydantic.Field(default=None, description="登録総数")
            last_refresh: Union[str, None] = pydantic.Field(default=None, description="最終リセット日時")
        class Data(resdata.Data):
            data: Union[Counter, None] = pydantic.Field(default=None, description="処理結果のデータ")
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

            # Redis からカウンターを取得
            counter = None
            try:
                raw = redis_cli.redis_cli.hget(
                    f"{redis_cli.lmtname}_{limiter.Limiter.REDIS_COUNTER_HASH}", limiter_name)
                if raw is not None:
                    text = raw.decode('utf-8') if isinstance(raw, bytes) else raw
                    counter = json.loads(text)
            except Exception:
                pass

            # Redis になければファイルから取得
            if counter is None:
                lmt = limiter.Limiter(redis_client=redis_cli)
                counter = lmt._load_counter_from_file(data_dir, limiter_name)

            result = dict(success=dict(data=counter))
            redis_cli.rpush(reskey, result)
            return self.RESP_SUCCESS

        except Exception as e:
            result = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, result)
            return self.RESP_WARN
