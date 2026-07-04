from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.options import Options
from cmdbox.app.features.cli import cmdbox_limiter_evidences, cmdbox_limiter_load, cmdbox_limiter_plan_load
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
from datetime import datetime
import argparse
import logging
import json
import pydantic


class LimiterBillingCalc(feature.OneshotResultEdgeFeature, validator.Validator):

    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'billing_calc'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="プラン設定一覧を取得し、各プランのエビデンスを基に請求データを計算・保存します。既に保存済みの請求データは上書きしません。",
            description_en="Retrieves the list of plan configurations, calculates billing data based on evidences for each plan, and saves the results. Existing billing data files will not be overwritten.",
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
                dict(opt="plan_name", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="処理対象のプラン識別名を指定します。省略時はすべてのプランを対象とします。",
                     description_en="Specify the plan identifier name to process. If omitted, all plans are targeted."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        plan_name = getattr(args, 'plan_name', None)
        payload = dict(plan_name=plan_name)
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class BillingResult(resdata.Base):
            billing_file: Union[str, None] = pydantic.Field(default=None, description="保存した請求データファイルのパス")
            plan_name: Union[str, None] = pydantic.Field(default=None, description="プラン識別名")
            billing_limiter: Union[str, None] = pydantic.Field(default=None, description="請求対象のリミッター名")
            last_reset: Union[str, None] = pydantic.Field(default=None, description="リセット日時")
            billing_amount: Union[float, None] = pydantic.Field(default=None, description="計算された請求金額")
            billing_currency: Union[str, None] = pydantic.Field(default="JPY", description="請求通貨")
            skipped: Union[bool, None] = pydantic.Field(default=False, description="既にファイルが存在したためスキップされた場合はTrue")

        class Data(resdata.Data):
            data: Union[List[BillingResult], None] = pydantic.Field(default=None, description="請求データ処理結果一覧")

        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")

        return Result

    def is_cluster_redirect(self):
        return False

    @classmethod
    def _calc_billing_amount(cls, configure: Dict[str, Any], last_counter: Dict[str, Any], limiter_config: Dict[str, Any]) -> Union[float, None]:
        """
        エビデンスの last_counter を基に請求金額を計算します。

        Args:
            configure: プラン設定辞書
            last_counter: エビデンスの last_counter
            limiter_config: 請求対象リミッターの設定辞書
        Returns:
            計算された請求金額と請求対象量。計算不可の場合は (None, None)。
            
        """
        billing_type = configure.get('billing_type')
        billing_unit_price = configure.get('billing_unit_price')

        if billing_type == 'period':
            return float(billing_unit_price) if billing_unit_price is not None else None, None

        if billing_type == 'metered':
            if billing_unit_price is None:
                return None, None
            billing_limiter_item = configure.get('billing_limiter_item', 'credits')
            counter = last_counter or {}
            if billing_limiter_item == 'registrations':
                billing_value = counter.get('total_registrations', 0)
            elif billing_limiter_item == 'count':
                billing_value = counter.get('total_count', 0)
            elif billing_limiter_item == 'time':
                billing_value = counter.get('total_time', 0.0)
            elif billing_limiter_item == 'input':
                billing_value = counter.get('total_input', 0)
            elif billing_limiter_item == 'process':
                billing_value = counter.get('total_process', 0)
            elif billing_limiter_item == 'output':
                billing_value = counter.get('total_output', 0)
            else:  # 'credits' がデフォルト
                billing_value = counter.get('total_credits', 0)
                max_total_credits = limiter_config.get('max_total_credits', 0) if limiter_config else 0
                if max_total_credits:
                    billing_value = max_total_credits if max_total_credits < billing_value else billing_value
            billing_value = billing_value if billing_value else 0
            amount = float(billing_value) * float(billing_unit_price)
            billing_min = configure.get('billing_min_amount')
            billing_max = configure.get('billing_max_amount')
            if billing_min is not None:
                amount = max(amount, float(billing_min))
            if billing_max is not None:
                amount = min(amount, float(billing_max))
            return amount, billing_value

        return None, None

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            filter_plan_name = payload.get('plan_name')
            plan_dir = data_dir / limiter.Limiter.LIMITER_DIR
            results: List[Dict[str, Any]] = []
            if not plan_dir.exists() or not plan_dir.is_dir():
                out = dict(success=dict(data=results))
                redis_cli.rpush(reskey, out)
                return self.RESP_SUCCESS

            # プラン設定ファイルを収集
            kwd = f"plan-{filter_plan_name}" if filter_plan_name else "plan-*"
            plan_files = sorted(plan_dir.glob(f"{kwd}.json"))
            for plan_path in plan_files:
                plan_stem = plan_path.stem  # e.g. "plan-myplan"
                if not plan_stem.startswith('plan-'):
                    continue
                plan_name = plan_stem[len('plan-'):]
                try:
                    configure = cmdbox_limiter_plan_load.LimiterPlanLoad._load_plan_config(data_dir, plan_name)
                except FileNotFoundError as e:
                    logger.warning(f"Plan config not found for '{plan_name}': {e}")
                    continue
                billing_limiter = configure.get('billing_limiter')
                if not billing_limiter:
                    logger.debug(f"Plan '{plan_name}' has no billing_limiter, skipping.")
                    continue

                # billing_limiter のリミッター設定を取得（credits上限計算用）
                limiter_config: Dict[str, Any] = {}
                try:
                    limiter_config = cmdbox_limiter_load.LimiterLoad._load_limiter_config(data_dir, billing_limiter)
                except Exception as e:
                    logger.warning(f"Failed to load limiter config for '{billing_limiter}': {e}")
                # billing_limiter のエビデンス一覧を取得
                evidences = cmdbox_limiter_evidences.LimiterEvidences._load_evidences(data_dir, billing_limiter, include_history=False)
                for evidence in evidences:
                    last_reset_str = evidence.get('last_reset', '')
                    last_counter = evidence.get('last_counter') or {}
                    # ファイル名用に last_reset を YYYYMMDD_HHMMSS 形式へ変換
                    last_reset_formatted = common.datetimestr2filename(last_reset_str)
                    billing_filename = f"billing-{billing_limiter}-{last_reset_formatted}.json"
                    billing_path = plan_dir / billing_filename
                    # 既にファイルが存在する場合はスキップ
                    if billing_path.exists():
                        results.append(dict(
                            billing_file=str(billing_path),
                            plan_name=plan_name,
                            billing_limiter=billing_limiter,
                            last_reset=last_reset_str,
                            billing_amount=None,
                            billing_currency=configure.get('billing_currency', 'JPY'),
                            skipped=True,
                        ))
                        logger.debug(f"Billing file already exists, skipping: {billing_path}")
                        continue
                    # 請求金額を計算
                    billing_amount, billing_qty = LimiterBillingCalc._calc_billing_amount(configure, last_counter, limiter_config)
                    # 請求データを構築
                    billing_data = dict(
                        plan_name=plan_name,
                        plan_title=configure.get('plan_title'),
                        billing_limiter=billing_limiter,
                        billing_limiter_item=configure.get('billing_limiter_item', 'credits'),
                        billing_type=configure.get('billing_type'),
                        billing_currency=configure.get('billing_currency', 'JPY'),
                        billing_unit_price=configure.get('billing_unit_price'),
                        billing_qty=billing_qty,
                        billing_min_amount=configure.get('billing_min_amount'),
                        billing_max_amount=configure.get('billing_max_amount'),
                        billing_amount=billing_amount,
                        last_reset=last_reset_str,
                        calc_datetime=datetime.now().isoformat(),
                        evidence_filename=evidence.get('filename'),
                        last_counter=last_counter,
                    )
                    # ファイルに保存（既存ファイルは上書きしない）
                    try:
                        with billing_path.open('x', encoding='utf-8') as f:
                            json.dump(billing_data, f, indent=4, ensure_ascii=False)
                        logger.info(f"Billing file saved: {billing_path}")
                        results.append(dict(
                            billing_file=str(billing_path),
                            plan_name=plan_name,
                            billing_limiter=billing_limiter,
                            last_reset=last_reset_str,
                            billing_amount=billing_amount,
                            billing_currency=configure.get('billing_currency', 'JPY'),
                            skipped=False,
                        ))
                    except FileExistsError:
                        # open('x') で競合が起きた場合もスキップ
                        results.append(dict(
                            billing_file=str(billing_path),
                            plan_name=plan_name,
                            billing_limiter=billing_limiter,
                            last_reset=last_reset_str,
                            billing_amount=None,
                            billing_currency=configure.get('billing_currency', 'JPY'),
                            skipped=True,
                        ))
                        logger.debug(f"Billing file already exists (concurrent write), skipping: {billing_path}")

            out = dict(success=dict(data=results))
            redis_cli.rpush(reskey, out)
            return self.RESP_SUCCESS

        except Exception as e:
            out = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, out)
            return self.RESP_WARN
