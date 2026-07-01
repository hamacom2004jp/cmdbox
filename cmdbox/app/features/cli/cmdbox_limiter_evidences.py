from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
from datetime import datetime
import argparse
import logging
import json
import pydantic
import re


class LimiterEvidences(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'limiter'

    def get_cmd(self) -> str:
        return 'evidences'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="制限設定のエビデンスファイルの一覧を取得します。エビデンスファイルはリセットタイミングが来たときに、カウンターの履歴などの情報を保存したファイルです。",
            description_en="Gets the list of evidence files for a limiter configuration. Evidence files are saved when the reset timing comes and contain information such as counter history.",
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
                     description_ja="エビデンスファイルを取得する制限設定の識別名を指定します。",
                     description_en="Specify the identifier name of the limiter configuration to get the evidence files for."),
                dict(opt="scope", type=Options.T_STR, default="server", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="スコープを指定します。`client` はクライアント側、`server` はサーバー側です。`current` は実行時ディレクトリです。",
                     description_en="Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory.",),
                dict(opt="include_history", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="エビデンスファイルの履歴情報を含めるかどうかを指定します。`True` の場合、履歴情報は出力されます。",
                     description_en="Specifies whether to include history information in the evidence file. If set to `True`, the history information is included in the output."),
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
            evidences = self._get_evidences(Path(client_data), args.limiter_name, include_history=args.include_history)
            out = dict(success=dict(data=evidences))
            common.print_format(out, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, out, None

        # scope == 'server'
        payload = dict(limiter_name=args.limiter_name, include_history=args.include_history)
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Evidence(resdata.Base):
            filename: Union[str, None] = pydantic.Field(default=None, description="エビデンスファイル名")
            filepath: Union[str, None] = pydantic.Field(default=None, description="エビデンスファイルパス")
            limiter_name: Union[str, None] = pydantic.Field(default=None, description="制限設定の識別名")
            last_counter: Union[Any, None] = pydantic.Field(default=None, description="エビデンス最終のカウンター")
            last_reset: Union[str, None] = pydantic.Field(default=None, description="リセット日時")
            config: Union[Dict[str, Any], None] = pydantic.Field(default=None, description="リミッター設定")
            history: Union[List[Dict[str, Any]], None] = pydantic.Field(default=None, description="カウンター履歴")

        class Data(resdata.Data):
            data: Union[List[Evidence], None] = pydantic.Field(default=None, description="処理結果のデータ")

        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")

        return Result

    def is_cluster_redirect(self):
        return False

    @staticmethod
    def _get_evidences(data_dir: Path, limiter_name: str, include_history: bool = False) -> List[Dict[str, Any]]:
        """Get list of evidence files for a limiter"""
        evidences: List[Dict[str, Any]] = []
        limiter_dir = Path(data_dir) / limiter.Limiter.LIMITER_DIR
        
        if not limiter_dir.exists() or not limiter_dir.is_dir():
            return evidences
        
        # Find all evidence files matching the limiter name pattern
        pattern = f"evidence-{limiter_name}-*.json"
        for p in sorted(limiter_dir.glob(pattern), reverse=True):
            if not p.is_file():
                continue
            with p.open('r', encoding='utf-8') as f:
                evidence_content = json.load(f)
            if not include_history:
                evidence_content.pop('history', None)
            evidences.append(dict(
                filename=p.name,
                filepath=str(p),
                **evidence_content,
            ))
        
        return evidences

    def _load_limiter_evidences(self, data_dir:Path, limiter_name:str, include_history:bool, logger:logging.Logger) -> List[Dict[str, Any]]:
        """Load limiter evidences (internal helper method)"""
        try:
            return self._get_evidences(data_dir, limiter_name, include_history=include_history)
        except Exception as e:
            logger.warning(f"Failed to load evidences for limiter '{limiter_name}': {e}")
            return []

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

            include_history = payload.get('include_history', False)
            evidences = self._load_limiter_evidences(data_dir, limiter_name, include_history, logger)
            result = dict(success=dict(data=evidences))
            redis_cli.rpush(reskey, result)
            return self.RESP_SUCCESS

        except Exception as e:
            result = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, result)
            return self.RESP_WARN
