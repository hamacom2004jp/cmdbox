from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.features.cli import cmdbox_llm_load
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic
import requests
import re
from urllib.parse import urljoin


class LLMMetrics(feature.OneshotResultEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language=None):
        super().__init__(appcls, ver, language)
        self.http_timeout = 30
        self.llm_load = cmdbox_llm_load.LLMLoad(appcls, ver, language)

    def get_mode(self) -> Union[str, List[str]]:
        return 'llm'

    def get_cmd(self) -> str:
        return 'metrics'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="指定したLLMのメトリクス情報を取得します。",
            description_en="Retrieves metrics information for the specified LLM.",
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
                    description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                    description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="llmname", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('llm','list',{},(res)=>{"
                            + "const val = $(\"[name='llmname']\").val();"
                            + "$(\"[name='llmname']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='llmname']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='llmname']\").val(val);"
                            + "},$(\"[name='title']\").val(),'llmname');"
                            + "}",
                    description_ja="メトリクスを取得するLLM設定の名前を指定します。",
                    description_en="Specify the name of the LLM configuration to get metrics for."),
                dict(opt="groups", type=Options.T_STR, default=None, required=False, multi=True, hide=True, choice=None, web="mask",
                    description_ja="このユーザーグループでLLM設定を利用するように指定します。",
                    description_en="Specify user groups used to authorize access to the LLM configuration."),
                dict(opt="format_raw", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=None,
                    description_ja="Prometheusフォーマットのメトリクスを生のテキスト形式で返します。",
                    description_en="Return the metrics in raw Prometheus text format."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:

        # LLM設定を読み込み
        st, ret, _ = self.llm_load.apprun(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return self.RESP_WARN, ret, None
        configure = ret['success']

        payload = dict(llmname=args.llmname,
                       groups=args.groups if hasattr(args, 'groups') else None,
                       format_raw=args.format_raw if hasattr(args, 'format_raw') else False,
                       configure=configure)
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl

        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class MetricValue(pydantic.BaseModel):
            name: str = pydantic.Field(..., description="メトリクス名")
            value: Union[float, str] = pydantic.Field(..., description="メトリクス値")
            help_text: Union[str, None] = pydantic.Field(default=None, description="メトリクスの説明")

        class Data(resdata.Data):
            llmname: Union[str, None] = pydantic.Field(default=None, description="LLM名")
            endpoint: Union[str, None] = pydantic.Field(default=None, description="メトリクスエンドポイント")
            metrics_raw: Union[str, None] = pydantic.Field(default=None, description="生のPrometheusフォーマットメトリクス")
            metrics: Union[List[MetricValue], None] = pydantic.Field(default=None, description="パースされたメトリクス")
            gpu_load: Union[float, None] = pydantic.Field(default=None, description="GPU負荷率（%）")
            requests_running: Union[int, None] = pydantic.Field(default=None, description="実行中のリクエスト数")
            requests_waiting: Union[int, None] = pydantic.Field(default=None, description="待機中のリクエスト数")
            tokens_generated_total: Union[int, None] = pydantic.Field(default=None, description="生成されたトークンの合計数")
            cache_usage_perc: Union[float, None] = pydantic.Field(default=None, description="キャッシュ使用率（%）")

        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")

        return Result

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        """
        サーバー側で受け取ったmetricsコマンドを処理します。
        """
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))

            llmname = payload.get('llmname')
            groups = payload.get('groups')
            format_raw = payload.get('format_raw', False)
            configure = payload.get('configure', {})

            # リクエスト元のグループが許可されていない場合は警告を返す
            if groups and not self.is_allowed_by_groups(groups, configure.get('user_groups'), redis_cli):
                msg = dict(warn=f"You do not have permission to use LLM configuration '{llmname}'.")
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN

            # メトリクスを取得
            result = self.fetch_metrics(configure, format_raw, logger)

            msg = dict(success=result)
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN

    def fetch_metrics(self, llm_config: Dict[str, Any], format_raw: bool = False, logger: logging.Logger = None) -> Dict[str, Any]:
        """
        LLMエンドポイントからメトリクス情報を取得します。
        vllm、またはOpenAI互換APIのメトリクスエンドポイントにアクセスします。

        Args:
            llm_config (Dict[str, Any]): LLM設定
            format_raw (bool): 生のPrometheusフォーマットを返すかどうか
            logger (logging.Logger): ロガーインスタンス

        Returns:
            Dict[str, Any]: メトリクス情報
        """
        llmname = llm_config.get('llmname', 'unknown')
        endpoint = llm_config.get('llmendpoint')
        apikey = llm_config.get('llmapikey')

        if not endpoint:
            raise ValueError(f"LLM configuration '{llmname}' does not have 'llmendpoint' specified.")

        # メトリクスエンドポイントを構成
        metrics_url = urljoin(endpoint.rstrip('/') + '/', 'metrics')

        result = {
            'llmname': llmname,
            'endpoint': metrics_url,
        }

        if logger:
            logger.info(f"Fetching metrics from {metrics_url}")

        try:
            # HTTPヘッダーを準備
            headers = {'User-Agent': 'cmdbox-llm-metrics/1.0'}
            if apikey:
                headers['Authorization'] = f'Bearer {apikey}'

            # メトリクスエンドポイントに接続
            response = requests.get(metrics_url, headers=headers, timeout=self.http_timeout)
            response.raise_for_status()

            metrics_text = response.text

            if format_raw:
                # 生のPrometheusフォーマットを返す
                result['metrics_raw'] = metrics_text
            else:
                # Prometheusフォーマットをパースして整理
                result['metrics_raw'] = metrics_text
                metrics_dict = self.parse_prometheus_metrics(metrics_text)
                result['metrics'] = metrics_dict.get('metrics', [])

                # 主要なメトリクスを抽出
                result['gpu_load'] = metrics_dict.get('gpu_load')
                result['requests_running'] = metrics_dict.get('requests_running')
                result['requests_waiting'] = metrics_dict.get('requests_waiting')
                result['tokens_generated_total'] = metrics_dict.get('tokens_generated_total')
                result['cache_usage_perc'] = metrics_dict.get('cache_usage_perc')

            return result

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to metrics endpoint '{metrics_url}': {e}")
        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Timeout while fetching metrics from '{metrics_url}': {e}")
        except requests.exceptions.RequestException as e:
            raise RuntimeError(f"Error fetching metrics from '{metrics_url}': {e}")

    def parse_prometheus_metrics(self, metrics_text: str) -> Dict[str, Any]:
        """
        Prometheusフォーマットのメトリクスをパースします。

        Args:
            metrics_text (str): Prometheusフォーマットのメトリクステキスト

        Returns:
            Dict[str, Any]: パースされたメトリクス情報
        """
        result = {
            'metrics': [],
            'gpu_load': None,
            'requests_running': None,
            'requests_waiting': None,
            'tokens_generated_total': None,
            'cache_usage_perc': None,
        }

        current_help = {}
        lines = metrics_text.split('\n')

        for line in lines:
            line = line.strip()

            # コメント行をスキップ
            if not line or line.startswith('#'):
                # HELPコメントから説明文を抽出
                if line.startswith('# HELP'):
                    parts = line.split(None, 3)
                    if len(parts) >= 4:
                        metric_name = parts[2]
                        help_text = parts[3]
                        current_help[metric_name] = help_text
                continue

            # メトリクス行をパース
            if '{' in line:
                # ラベル付きメトリクス (metric_name{label1="value1", ...} value)
                match = re.match(r'([a-zA-Z_:][a-zA-Z0-9_:]*)\{([^}]*)\}\s+([\d.eE+-]+)', line)
                if match:
                    metric_name = match.group(1)
                    labels = match.group(2)
                    value = float(match.group(3))
                    help_text = current_help.get(metric_name)
                    result['metrics'].append({
                        'name': metric_name,
                        'value': value,
                        'help_text': help_text,
                    })
                    self._extract_key_metrics(metric_name, value, labels, result)
            else:
                # ラベルなしメトリクス (metric_name value)
                match = re.match(r'([a-zA-Z_:][a-zA-Z0-9_:]*)\s+([\d.eE+-]+)', line)
                if match:
                    metric_name = match.group(1)
                    value = float(match.group(2))
                    help_text = current_help.get(metric_name)
                    result['metrics'].append({
                        'name': metric_name,
                        'value': value,
                        'help_text': help_text,
                    })
                    self._extract_key_metrics(metric_name, value, None, result)

        return result

    def _extract_key_metrics(self, metric_name: str, value: float, labels: Union[str, None], result: Dict[str, Any]) -> None:
        """
        主要なメトリクスを抽出して結果に追加します。

        Args:
            metric_name (str): メトリクス名
            value (float): メトリクス値
            labels (str): ラベル文字列
            result (Dict[str, Any]): 結果辞書
        """
        # vllmのメトリクス名パターン
        if 'num_requests_running' in metric_name:
            result['requests_running'] = int(value)
        elif 'num_requests_waiting' in metric_name:
            result['requests_waiting'] = int(value)
        elif 'gpu_cache_usage_perc' in metric_name or 'cache_usage_perc' in metric_name:
            result['cache_usage_perc'] = round(value, 2)
        elif 'tokens_generated_total' in metric_name or 'generated_tokens_total' in metric_name:
            result['tokens_generated_total'] = int(value)
        elif 'gpu_utilization_perc' in metric_name or 'gpu_load' in metric_name:
            result['gpu_load'] = round(value, 2)
