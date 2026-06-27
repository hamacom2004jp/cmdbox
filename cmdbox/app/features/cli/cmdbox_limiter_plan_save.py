from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class LimiterPlanSave(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'plan_save'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="複数の制限設定をまとめたプラン設定を追加/保存します。",
            description_en="Adds or saves plan settings that bundle multiple limiter configurations.",
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
                # プラン基本情報
                dict(opt="plan_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="プランの識別名を指定します。",
                     description_en="Specify the identifier name of the plan."),
                dict(opt="plan_title", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="プランのタイトルを指定します。",
                     description_en="Specify the title of the plan."),
                dict(opt="plan_desc", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="プランの説明を指定します。",
                     description_en="Specify the description of the plan."),
                dict(opt="limiters", type=Options.T_STR, default=None, required=True, multi=True, hide=False, choice=[],
                     callcmd="async () => {await cmdbox.callcmd('limiter','list',{},(res)=>{"
                             + "const val = $(\"[name='limiters']\").val();"
                             + "$(\"[name='limiters']\").empty().append('<option></option>');"
                             + "res['data'].map(elm=>{$(\"[name='limiters']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                             + "$(\"[name='limiters']\").val(val);"
                             + "},$(\"[name='title']\").val(),'limiters');"
                             + "}",
                     description_ja="このプランに含まれるリミッター設定名を指定します。",
                     description_en="Specify the limiter configuration names included in this plan."),
                # プラン期間設定
                dict(opt="plan_start", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="プランの適用開始日時を指定します（例: 2024-01-01T00:00:00）。省略時は制限しません。",
                     description_en="Specify the start datetime of the plan application (e.g. 2024-01-01T00:00:00). If omitted, no limit is applied."),
                dict(opt="plan_end", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="プランの適用終了日時を指定します（例: 2024-12-31T23:59:59）。省略時は制限しません。",
                     description_en="Specify the end datetime of the plan application (e.g. 2024-12-31T23:59:59). If omitted, no limit is applied."),
                dict(opt="open_date", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="ユーザーの利用開始日時を指定します（例: 2024-01-01T00:00:00）。省略時は制限しません。",
                     description_en="Specify the start datetime for user access (e.g. 2024-01-01T00:00:00). If omitted, no limit is applied."),
                dict(opt="suspend_date", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="ユーザーの利用停止日時を指定します（例: 2024-12-31T23:59:59）。省略時は制限しません。",
                     description_en="Specify the end datetime for user access (e.g. 2024-12-31T23:59:59). If omitted, no limit is applied."),
                dict(opt="notice_date", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="利用停止日の手前で、利用停止日を通知する日時を指定します（例: 2024-12-20T00:00:00）。省略時は通知しません。",
                     description_en="Specify the datetime to notify about the suspension date before the suspend_date (e.g. 2024-12-20T00:00:00). If omitted, no notification is sent."),
                # 請求タイプ
                dict(opt="billing_type", type=Options.T_STR, default="period", required=True, multi=False, hide=False, choice=["period", "metered"],
                     choice_show=dict(period=["billing_period_unit", "billing_period_qty", "billing_unit_price"],
                                      metered=["billing_limiter", "billing_min_amount", "billing_max_amount", "billing_unit_price"]),
                     description_ja="請求タイプを指定します。`period` は期間課金、`metered` は従量課金です。",
                     description_en="Specify the billing type. `period` for period-based billing, `metered` for metered billing."),
                # 期間課金用オプション
                dict(opt="billing_period_unit", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=["hour", "day", "month", "year"],
                     description_ja="請求期間単位を指定します（期間課金の場合）。hour, day, month, year から選択します。",
                     description_en="Specify the billing period unit (for period-based billing). Choose from hour, day, month, year."),
                dict(opt="billing_period_qty", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="請求期間数量を指定します（期間課金の場合）。",
                     description_en="Specify the billing period quantity (for period-based billing)."),
                dict(opt="billing_unit_price", type=Options.T_FLOAT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="請求単価を指定します。期間課金の場合は期間単位の単価、従量課金の場合はクレジット当たりの単価です。",
                     description_en="Specify the billing unit price. For period-based billing, the price per period. For metered billing, the price per credit."),
                # 従量課金用オプション
                dict(opt="billing_limiter", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=[],
                     callcmd="async () => {await cmdbox.callcmd('limiter','list',{},(res)=>{"
                             + "const val = $(\"[name='billing_limiter']\").val();"
                             + "$(\"[name='billing_limiter']\").empty().append('<option></option>');"
                             + "res['data'].map(elm=>{$(\"[name='billing_limiter']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                             + "$(\"[name='billing_limiter']\").val(val);"
                             + "},$(\"[name='title']\").val(),'billing_limiter');"
                             + "}",
                     description_ja="請求対象のリミッター名を指定します（従量課金の場合）。このリミッターのクレジットカウンターを基に請求されます。",
                     description_en="Specify the limiter name to be billed (for metered billing). Billing is based on the credit counter of this limiter."),
                dict(opt="billing_min_amount", type=Options.T_FLOAT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="請求の最小金額を指定します（従量課金の場合）。",
                     description_en="Specify the minimum billing amount (for metered billing)."),
                dict(opt="billing_max_amount", type=Options.T_FLOAT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="請求の最大金額を指定します（従量課金の場合）。",
                     description_en="Specify the maximum billing amount (for metered billing)."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        # 請求タイプ別の検証
        if args.billing_type == 'period':
            if not args.billing_period_unit or not args.billing_period_qty or args.billing_unit_price is None:
                result = dict(warn="For period-based billing, billing_period_unit, billing_period_qty, and billing_unit_price are required.")
                logger.warning("For period-based billing, billing_period_unit, billing_period_qty, and billing_unit_price are required.")
                common.print_format(result, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, result, None
        elif args.billing_type == 'metered':
            if not args.billing_limiter or args.billing_unit_price is None:
                result = dict(warn="For metered billing, billing_limiter and billing_unit_price are required.")
                logger.warning("For metered billing, billing_limiter and billing_unit_price are required.")
                common.print_format(result, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, result, None

        # リミッターリストの処理
        limiters = []
        if hasattr(args, 'limiters') and args.limiters:
            if isinstance(args.limiters, list):
                limiters = args.limiters
            else:
                limiters = [args.limiters]

        configure = dict(
            plan_name=args.plan_name,
            plan_title=args.plan_title if hasattr(args, 'plan_title') else None,
            plan_desc=args.plan_desc if hasattr(args, 'plan_desc') else None,
            limiters=limiters,
            plan_start=str(args.plan_start) if hasattr(args, 'plan_start') and args.plan_start is not None else None,
            plan_end=str(args.plan_end) if hasattr(args, 'plan_end') and args.plan_end is not None else None,
            open_date=str(args.open_date) if hasattr(args, 'open_date') and args.open_date is not None else None,
            suspend_date=str(args.suspend_date) if hasattr(args, 'suspend_date') and args.suspend_date is not None else None,
            notice_date=str(args.notice_date) if hasattr(args, 'notice_date') and args.notice_date is not None else None,
            billing_type=args.billing_type,
            billing_period_unit=args.billing_period_unit if hasattr(args, 'billing_period_unit') else None,
            billing_period_qty=args.billing_period_qty if hasattr(args, 'billing_period_qty') else None,
            billing_limiter=args.billing_limiter if hasattr(args, 'billing_limiter') else None,
            billing_min_amount=args.billing_min_amount if hasattr(args, 'billing_min_amount') else None,
            billing_max_amount=args.billing_max_amount if hasattr(args, 'billing_max_amount') else None,
            billing_unit_price=args.billing_unit_price if hasattr(args, 'billing_unit_price') else None,
        )

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

            plan_name = configure.get('plan_name')
            if not plan_name:
                out = dict(warn="plan_name is required.")
                redis_cli.rpush(reskey, out)
                return self.RESP_WARN

            configure_path = data_dir / ".limiter" / f"plan-{plan_name}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            common.save_file(configure_path, lambda f: json.dump(configure, f, indent=4), encoding='utf-8', nolock=False)
            out = dict(success=f"Plan configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, out)
            return self.RESP_SUCCESS

        except Exception as e:
            out = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, out)
            return self.RESP_WARN
