from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.options import Options
from cmdbox.app.features.cli import cmdbox_limiter_counter, cmdbox_limiter_load, cmdbox_limiter_billing_load
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
from datetime import datetime as _dt
import argparse
import logging
import json
import pydantic


class LimiterPlanLoad(feature.OneshotResultEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language=None):
        super().__init__(appcls, ver, language)
        self.limiter_load = cmdbox_limiter_load.LimiterLoad(appcls, ver, language)
        self.limiter_counter = cmdbox_limiter_counter.LimiterCounter(appcls, ver, language)
        self.billing_load = cmdbox_limiter_billing_load.LimiterBillingLoad(appcls, ver, language)

    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'plan_load'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="プラン設定を読み込みます。",
            description_en="Loads a plan configuration.",
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
                     description_ja="読み込むプランの識別名を指定します。",
                     description_en="Specify the identifier name of the plan to load."),
                dict(opt="include_history", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="エビデンスファイルの履歴情報を含めるかどうかを指定します。`True` の場合、履歴情報は出力されます。",
                     description_en="Specifies whether to include history information in the evidence file. If set to `True`, the history information is included in the output."),
                dict(opt="reflesh_counter", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="カウンタを最新化するかどうかを指定します。Trueを指定すると、カウンタが最新化されます。",
                     description_en="Specifies whether to update the counter. If set to True, the counter is updated."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        payload = dict(plan_name=args.plan_name, include_history=getattr(args, 'include_history', False),
                       reflesh_counter=getattr(args, 'reflesh_counter', False))
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class LimiterDetail(resdata.Base):
            limiter_name: Union[str, None] = pydantic.Field(default=None, description="制限設定の識別名")
            limiter_title: Union[str, None] = pydantic.Field(default=None, description="制限設定の表示名")
            target_mode: Union[str, None] = pydantic.Field(default=None, description="対象コマンドのモード名")
            target_cmd: Union[str, None] = pydantic.Field(default=None, description="対象コマンドのコマンド名")
            target_option: Union[List[Dict[str, Any]], Dict[str, Any], None] = pydantic.Field(default=None, description="対象コマンドの条件")
            max_registrations: Union[int, None] = pydantic.Field(default=None, description="登録最大数（又は登録最大サイズ）")
            max_total_count: Union[int, None] = pydantic.Field(default=None, description="実行最大回数")
            max_total_time: Union[float, None] = pydantic.Field(default=None, description="実行可能総時間（秒）")
            max_total_input: Union[int, None] = pydantic.Field(default=None, description="入力総バイト数の上限")
            max_total_process: Union[int, None] = pydantic.Field(default=None, description="処理総バイト数の上限")
            max_total_output: Union[int, None] = pydantic.Field(default=None, description="出力総バイト数の上限")
            max_total_credits: Union[int, None] = pydantic.Field(default=None, description="コマンドの最大クレジット数")
            service_credits: Union[int, None] = pydantic.Field(default=None, description="サービスクレジット数")
            exec_period_start: Union[str, None] = pydantic.Field(default=None, description="実行可能期間の開始日時")
            exec_period_end: Union[str, None] = pydantic.Field(default=None, description="実行可能期間の終了日時")
            reset_datetime: Union[str, None] = pydantic.Field(default=None, description="カウンタリセット日時")
            reset_period_unit: Union[str, None] = pydantic.Field(default=None, description="リセット単位（hour/day/month/year）")
            reset_period_qty: Union[int, None] = pydantic.Field(default=None, description="リセット間隔の数量")
            max_history_interval: Union[float, None] = pydantic.Field(default=None, description="履歴保存期間の最大間隔（秒）")
            counter: Union[Dict[str, Any], None] = pydantic.Field(default=None, description="現在のカウンター状態")

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
            last_counter: Union[Dict[str, Any], None] = pydantic.Field(default=None, description="リセット時点のカウンター")
            calc_datetime: Union[str, None] = pydantic.Field(default=None, description="請求金額計算日時")
            evidence_filename: Union[str, None] = pydantic.Field(default=None, description="エビデンスファイル名")

        class Configure(resdata.Base):
            plan_name: Union[str, None] = pydantic.Field(default=None, description="プランの識別名")
            plan_title: Union[str, None] = pydantic.Field(default=None, description="プランのタイトル")
            plan_desc: Union[str, None] = pydantic.Field(default=None, description="プランの説明")
            limiters: Union[List[LimiterDetail], None] = pydantic.Field(default=None, description="このプランに含まれるリミッター設定の詳細情報")

            plan_start: Union[str, None] = pydantic.Field(default=None, description="プラン適用開始日時")
            plan_end: Union[str, None] = pydantic.Field(default=None, description="プラン適用終了日時")
            open_date: Union[str, None] = pydantic.Field(default=None, description="ユーザー利用開始日時")
            suspend_date: Union[str, None] = pydantic.Field(default=None, description="ユーザー利用停止日時")
            notice_date: Union[str, None] = pydantic.Field(default=None, description="利用停止日の通知日時")
            billing_type: Union[str, None] = pydantic.Field(default=None, description="請求タイプ（period or metered）")
            billing_period_unit: Union[str, None] = pydantic.Field(default=None, description="請求期間単位")
            billing_period_qty: Union[int, None] = pydantic.Field(default=None, description="請求期間数量")
            billing_limiter: Union[str, None] = pydantic.Field(default=None, description="請求対象のリミッター名")
            billing_limiter_item: Union[str, None] = pydantic.Field(default="credits", description="請求計算に使用するリミッター項目（registrations/count/time/input/process/output/credits）")
            billing_min_amount: Union[float, None] = pydantic.Field(default=None, description="請求の最小金額")
            billing_max_amount: Union[float, None] = pydantic.Field(default=None, description="請求の最大金額")
            billing_unit_price: Union[float, None] = pydantic.Field(default=None, description="請求単価")
            billing_currency: Union[str, None] = pydantic.Field(default="JPY", description="請求に使用する通貨（JPY, USD, EUR等）")
            current_billing_qty: Union[float, None] = pydantic.Field(default=None, description="現在の請求対象量")
            current_billing_amount: Union[float, None] = pydantic.Field(default=None, description="現在の請求金額")
            billing_data: Union[List[BillingData], None] = pydantic.Field(default=None, description="請求データリスト")

        class Data(resdata.Data):
            data: Union[Configure, None] = pydantic.Field(default=None, description="プラン設定データ")

        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")

        return Result

    def is_cluster_redirect(self):
        return False

    @classmethod
    def _load_plan_config(cls, data_dir: Path, plan_name: str) -> Dict[str, Any]:
        """
        プラン設定ファイルを読み込んで辞書として返す
        
        Args:
            data_dir: データディレクトリのパス
            plan_name: プラン識別名
        Returns:
            プラン設定の辞書
        Raises:
            FileNotFoundError: プラン設定ファイルが存在しない場合
        """
        configure_path = data_dir / ".limiter" / f"plan-{plan_name}.json"
        if not configure_path.exists():
            raise FileNotFoundError(f"Plan configuration '{plan_name}' not found at '{configure_path}'.")
        
        with configure_path.open('r', encoding='utf-8') as f:
            configure = json.load(f)
        
        return configure

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            plan_name = payload.get('plan_name')
            include_history = payload.get('include_history', False)
            reflesh_counter = payload.get('reflesh_counter', False)
            if not plan_name:
                out = dict(warn="plan_name is required.")
                redis_cli.rpush(reskey, out)
                return self.RESP_WARN

            try:
                configure = self._load_plan_config(data_dir, plan_name)
            except FileNotFoundError as e:
                out = dict(warn=str(e))
                redis_cli.rpush(reskey, out)
                return self.RESP_WARN
            
            # limiters フィールドが存在する場合、各limiterの詳細情報を取得
            if 'limiters' in configure and isinstance(configure['limiters'], list):
                limiter_details = []
                for limiter_name in configure['limiters']:
                    try:
                        # self.limiter_load を使用して limiter 設定を取得
                        limiter_cfg = self.limiter_load._load_limiter_config(data_dir, limiter_name)
                        # self.limiter_counter を使用してカウンター情報を取得
                        if reflesh_counter:
                            lmt = limiter.Limiter.getInstance(redis_client=redis_cli, flush_interval=60, reload_interval=60)
                            self.limiter_counter._reflesh_counter(lmt, data_dir, limiter_name, scope='server', logger=logger, args=argparse.Namespace())
                        counter_data = self.limiter_counter._load_limiter_counter(data_dir, limiter_name, redis_cli, logger,
                                                                                  scope='server', load_history=include_history)
                        limiter_cfg['counter'] = counter_data
                        limiter_details.append(limiter_cfg)
                    except FileNotFoundError as e:
                        logger.warning(f"Failed to load limiter '{limiter_name}': {e}")
                        limiter_details.append({'limiter_name': limiter_name, 'error': str(e)})
                    except Exception as e:
                        logger.warning(f"Failed to load limiter '{limiter_name}': {e}")
                        limiter_details.append({'limiter_name': limiter_name, 'error': str(e)})
                
                configure['limiters'] = limiter_details
            
            # billing_limiter に対応する請求データを取得（cmdbox_limiter_billing_load を使用）
            billing_limiter = configure.get('billing_limiter')
            if billing_limiter:
                try:
                    # billing_load から請求ファイルを検索
                    billing_files = self.billing_load._find_billing_files(data_dir, billing_limiter)
                    # 各請求データファイルを読み込んで返す
                    billing_data_list = []
                    for billing_file in billing_files:
                        try:
                            with billing_file.open('r', encoding='utf-8') as f:
                                billing_data = json.load(f)
                                billing_data_list.append(billing_data)
                        except Exception as e:
                            logger.warning(f"Failed to load billing data file '{billing_file}': {e}")
                            continue
                    configure['billing_data'] = billing_data_list
                except Exception as e:
                    logger.warning(f"Failed to load billing data for billing_limiter '{billing_limiter}': {e}")
            
            # 現在の請求金額を計算
            billing_type = configure.get('billing_type')
            billing_unit_price = configure.get('billing_unit_price')
            billing_value = None
            current_billing_amount = None
            if billing_type == 'period':
                current_billing_amount = float(billing_unit_price) if billing_unit_price is not None else None
            elif billing_type == 'metered':
                billing_limiter_item = configure.get('billing_limiter_item', 'credits')
                if billing_unit_price is not None and billing_limiter:
                    # billing_limiter のカウンターから指定された項目の値を取得
                    billing_value = None
                    limiter_details_list = configure.get('limiters', [])
                    for lm in limiter_details_list:
                        if isinstance(lm, dict) and lm.get('limiter_name') == billing_limiter:
                            counter = lm.get('counter') or {}
                            # billing_limiter_item に対応するカウンター値を取得
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
                            else:
                                billing_value = counter.get('total_credits', 0)
                                max_total_credits = lm.get('max_total_credits', 0)
                                if max_total_credits:
                                    billing_value = max_total_credits if max_total_credits < billing_value else billing_value
                            billing_value = billing_value if billing_value else 0
                            break
                    if billing_value is not None:
                        amount = float(billing_value) * float(billing_unit_price)
                        billing_min = configure.get('billing_min_amount')
                        billing_max = configure.get('billing_max_amount')
                        if billing_min is not None:
                            amount = max(amount, float(billing_min))
                        if billing_max is not None:
                            amount = min(amount, float(billing_max))
                        current_billing_amount = amount
            configure['current_billing_qty'] = billing_value
            configure['current_billing_amount'] = current_billing_amount
            if configure.get('billing_type') == 'period':
                configure['billing_limiter'] = None
                configure['billing_limiter_item'] = None
                configure['billing_min_amount'] = None
                configure['billing_max_amount'] = None

            out = dict(success=dict(data=configure))
            redis_cli.rpush(reskey, out)
            return self.RESP_SUCCESS

        except Exception as e:
            out = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, out)
            return self.RESP_WARN
