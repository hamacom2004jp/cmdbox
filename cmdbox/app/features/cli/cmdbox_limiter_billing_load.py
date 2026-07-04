from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.options import Options
from cmdbox.app.features.cli import cmdbox_limiter_plan_load
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class LimiterBillingLoad(feature.OneshotResultEdgeFeature, validator.Validator):

    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'billing_load'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="プラン名を指定して請求データを読み込みます。last_resetを指定した場合はそのタイミングの請求データを、指定しない場合は最新の請求データを返します。",
            description_en="Loads billing data by specifying a plan name. If last_reset is specified, returns billing data for that timing. If not specified, returns the latest billing data.",
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
                dict(opt="plan_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="読み込むプラン名を指定します。",
                     description_en="Specify the plan name to load."),
                dict(opt="last_reset", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="リセット日時を指定します（例: 2024-01-01T00:00:00 または 20240101_000000）。省略した場合は最新の請求データを返します。",
                     description_en="Specify the reset datetime (e.g. 2024-01-01T00:00:00 or 20240101_000000). If omitted, returns the latest billing data."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        plan_name = args.plan_name
        last_reset = getattr(args, 'last_reset', None)
        payload = dict(plan_name=plan_name, last_reset=last_reset)
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class BillingData(resdata.Base):
            plan_name: Union[str, None] = pydantic.Field(default=None, description="プランの識別名")
            plan_title: Union[str, None] = pydantic.Field(default=None, description="プランのタイトル")
            billing_limiter: Union[str, None] = pydantic.Field(default=None, description="請求対象のリミッター名")
            billing_limiter_item: Union[str, None] = pydantic.Field(default="credits", description="請求計算に使用するリミッター項目")
            billing_type: Union[str, None] = pydantic.Field(default=None, description="請求タイプ（period or metered）")
            billing_currency: Union[str, None] = pydantic.Field(default="JPY", description="請求通貨")
            billing_unit_price: Union[float, None] = pydantic.Field(default=None, description="請求単価")
            billing_min_amount: Union[float, None] = pydantic.Field(default=None, description="請求の最小金額")
            billing_max_amount: Union[float, None] = pydantic.Field(default=None, description="請求の最大金額")
            billing_amount: Union[float, None] = pydantic.Field(default=None, description="計算された請求金額")
            last_reset: Union[str, None] = pydantic.Field(default=None, description="リセット日時")
            calc_datetime: Union[str, None] = pydantic.Field(default=None, description="請求計算日時")
            evidence_filename: Union[str, None] = pydantic.Field(default=None, description="エビデンスファイル名")
            last_counter: Union[Dict[str, Any], None] = pydantic.Field(default=None, description="リセット時点のカウンター")

        class Data(resdata.Data):
            data: Union[BillingData, List[BillingData], None] = pydantic.Field(default=None, description="請求データ（last_reset指定時は単一、未指定時は配列）")

        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")

        return Result

    def is_cluster_redirect(self):
        return False

    def _find_billing_file(self, data_dir: Path, billing_limiter: str, last_reset: Union[str, None] = None) -> Union[Path, None]:
        """
        請求データファイルを検索（単一）
        
        Args:
            data_dir: データディレクトリのパス
            billing_limiter: 請求対象のリミッター名
            last_reset: リセット日時（指定した場合はそれのみ）
        Returns:
            見つかったファイルパス、見つからない場合は None
        """
        if not last_reset:
            return None
            
        limiter_dir = Path(data_dir) / limiter.Limiter.LIMITER_DIR
        if not limiter_dir.exists() or not limiter_dir.is_dir():
            return None

        # last_reset が指定されている場合、それに対応するファイルを探す
        last_reset_formatted = common.datetimestr2filename(last_reset)
        billing_file = limiter_dir / f"billing-{billing_limiter}-{last_reset_formatted}.json"
        if billing_file.exists() and billing_file.is_file():
            return billing_file
        return None

    def _find_billing_files(self, data_dir: Path, billing_limiter: str) -> List[Path]:
        """
        請求データファイルをすべて検索（新しい順）
        
        Args:
            data_dir: データディレクトリのパス
            billing_limiter: 請求対象のリミッター名
        Returns:
            見つかったファイルパスのリスト（新しい順）
        """
        limiter_dir = Path(data_dir) / limiter.Limiter.LIMITER_DIR
        if not limiter_dir.exists() or not limiter_dir.is_dir():
            return []

        pattern = f"billing-{billing_limiter}-*.json"
        files = sorted(limiter_dir.glob(pattern), reverse=True)
        return files

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            plan_name = payload.get('plan_name')
            last_reset = payload.get('last_reset')

            if not plan_name:
                out = dict(warn="plan_name is required.")
                redis_cli.rpush(reskey, out)
                return self.RESP_WARN

            # プラン設定を読み込む
            try:
                configure = cmdbox_limiter_plan_load.LimiterPlanLoad._load_plan_config(data_dir, plan_name)
            except FileNotFoundError as e:
                out = dict(warn=str(e))
                redis_cli.rpush(reskey, out)
                return self.RESP_WARN

            billing_limiter = configure.get('billing_limiter')
            if not billing_limiter:
                out = dict(warn=f"Plan '{plan_name}' has no billing_limiter configured.")
                redis_cli.rpush(reskey, out)
                return self.RESP_WARN

            # last_resetが指定されている場合は単一、指定されていない場合は全件
            if last_reset:
                # 単一の請求データファイルを検索
                billing_file = self._find_billing_file(data_dir, billing_limiter, last_reset)
                if not billing_file:
                    out = dict(warn=f"Billing data file not found for plan '{plan_name}' with limiter '{billing_limiter}' and last_reset '{last_reset}'.")
                    redis_cli.rpush(reskey, out)
                    return self.RESP_WARN

                # ファイルを読み込む
                try:
                    with billing_file.open('r', encoding='utf-8') as f:
                        billing_data = json.load(f)
                except Exception as e:
                    out = dict(warn=f"Failed to load billing data file '{billing_file}': {e}")
                    logger.warning(f"Failed to load billing data file: {e}", exc_info=True)
                    redis_cli.rpush(reskey, out)
                    return self.RESP_WARN

                out = dict(success=dict(data=billing_data))
            else:
                # すべての請求データファイルを検索
                billing_files = self._find_billing_files(data_dir, billing_limiter)
                if not billing_files:
                    out = dict(warn=f"No billing data files found for plan '{plan_name}' with limiter '{billing_limiter}'.")
                    redis_cli.rpush(reskey, out)
                    return self.RESP_WARN

                # すべてのファイルを読み込む
                billing_data_list = []
                for billing_file in billing_files:
                    try:
                        with billing_file.open('r', encoding='utf-8') as f:
                            billing_data = json.load(f)
                            billing_data_list.append(billing_data)
                    except Exception as e:
                        logger.warning(f"Failed to load billing data file '{billing_file}': {e}", exc_info=True)
                        continue

                out = dict(success=dict(data=billing_data_list))

            redis_cli.rpush(reskey, out)
            return self.RESP_SUCCESS

        except Exception as e:
            out = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, out)
            return self.RESP_WARN
