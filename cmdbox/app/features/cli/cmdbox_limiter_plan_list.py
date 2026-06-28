from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class LimiterPlanList(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'plan_list'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="登録済みのプラン設定を一覧表示します。",
            description_en="Lists registered plan configurations.",
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
                dict(opt="kwd", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="検索したいプラン識別名を指定します。中間マッチで検索します。",
                     description_en="Specify the plan identifier name to search for. Searches for partial matches."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        kwd = args.kwd if hasattr(args, 'kwd') else None
        payload = dict(kwd=kwd)
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class PlanInfo(resdata.Base):
            name: Union[str, None] = pydantic.Field(default=None, description="プラン識別名")
            plan_title: Union[str, None] = pydantic.Field(default=None, description="プランのタイトル")
            plan_desc: Union[str, None] = pydantic.Field(default=None, description="プランの説明")
            billing_type: Union[str, None] = pydantic.Field(default=None, description="請求タイプ")
            billing_currency: Union[str, None] = pydantic.Field(default="JPY", description="請求に使用する通貨")
            limiters: Union[List[str], None] = pydantic.Field(default=None, description="このプランに含まれるリミッター設定名一覧")
            plan_start: Union[str, None] = pydantic.Field(default=None, description="プラン適用開始日時")
            plan_end: Union[str, None] = pydantic.Field(default=None, description="プラン適用終了日時")

        class Data(resdata.Data):
            data: Union[List[PlanInfo], None] = pydantic.Field(default=None, description="プラン設定一覧")

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
            kwd = payload.get('kwd')
            if not kwd:
                kwd = '*'

            plan_dir = data_dir / ".limiter"
            results: List[Dict[str, Any]] = []
            if plan_dir.exists() and plan_dir.is_dir():
                for p in sorted(plan_dir.glob(f"plan-{kwd}.json")):
                    name = p.stem
                    if not name.startswith('plan-'):
                        continue
                    with p.open('r', encoding='utf-8') as f:
                        cfg = json.load(f)
                    results.append(dict(
                        name=name[len('plan-'):],
                        plan_title=cfg.get('plan_title', None),
                        plan_desc=cfg.get('plan_desc', None),
                        billing_type=cfg.get('billing_type', None),
                        limiters=cfg.get('limiters', []),
                        plan_start=cfg.get('plan_start', None),
                        plan_end=cfg.get('plan_end', None),
                    ))

            out = dict(success=dict(data=results))
            redis_cli.rpush(reskey, out)
            return self.RESP_SUCCESS

        except Exception as e:
            out = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, out)
            return self.RESP_WARN
