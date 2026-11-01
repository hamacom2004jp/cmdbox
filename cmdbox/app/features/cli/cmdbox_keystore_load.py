from cmdbox.app import common, client, feature
from cmdbox.app.commons import cache, convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class KeystoreLoad(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'keystore'

    def get_cmd(self) -> str:
        return 'load'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="キーストアのキー情報を読み込みます。",
            description_en="Load API key information from keystore.",
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
                dict(opt="key_id", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="読み込むキーIDを指定します。",
                     description_en="Specify the key ID to load."),
            ]
        )

    @cache.async_apprun_cache(args_key='key_id')
    @validator.async_apprun_check
    async def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        payload = dict(
            key_id=args.key_id,
        )
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = await cl.redis_cli.asend_cmd(self.get_svcmd(), [payload_b64],
                                           retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            key_id: Union[str, None] = pydantic.Field(default=None, description="キーID")
            key_name: Union[str, None] = pydantic.Field(default=None, description="キー名")
            key_provider: Union[str, None] = pydantic.Field(default=None, description="キー発行者")
            key_type: Union[str, None] = pydantic.Field(default=None, description="キー種別")
            key_usage: Union[List[str], None] = pydantic.Field(default=None, description="利用対象コマンド")
            key_value: Union[str, None] = pydantic.Field(default=None, description="キー実体")
            sign_key: Union[str, None] = pydantic.Field(default=None, description="秘密鍵ファイル")
            sign_cert: Union[str, None] = pydantic.Field(default=None, description="証明書ファイル")
            key_pass: Union[str, None] = pydantic.Field(default=None, description="秘密鍵パスワード")
            enc_key: Union[str, None] = pydantic.Field(default=None, description="暗号鍵")
            ca_cert: Union[str, None] = pydantic.Field(default=None, description="CA証明書ファイル")
            key_period_start: Union[str, None] = pydantic.Field(default=None, description="使用開始日時")
            key_period_end: Union[str, None] = pydantic.Field(default=None, description="使用終了日時")
            groups: Union[List[str], None] = pydantic.Field(default=None, description="利用可能グループ")
            owner: Union[List[str], None] = pydantic.Field(default=None, description="所有者")
            claims: Union[Dict[str, Any], None] = pydantic.Field(default=None, description="要求クレーム")
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
            keystore_dir = data_dir / '.keystore'
            if not keystore_dir.exists():
                result = dict(warn=f"Keystore directory not found at '{str(keystore_dir)}'.")
                redis_cli.rpush(reskey, result)
                return self.RESP_WARN

            key_id = payload.get('key_id')
            matches = []
            pattern = f"key_{key_id}_*.json"
            for p in sorted(keystore_dir.glob(pattern)):
                try:
                    cfg = common.load_file(p, lambda f: json.load(f), encoding='utf-8', nolock=True)
                    if cfg.get('key_id') != key_id:
                        continue
                    matches.append(cfg)
                except Exception:
                    continue

            if len(matches) <= 0:
                result = dict(warn=f"Keystore key not found. key_id='{key_id}'.")
                redis_cli.rpush(reskey, result)
                return self.RESP_WARN
            if len(matches) > 1:
                result = dict(warn=f"Multiple keystore keys found for key_id='{key_id}'. Please specify --key_name.")
                redis_cli.rpush(reskey, result)
                return self.RESP_WARN

            result = dict(success=matches[0])
            redis_cli.rpush(reskey, result)
            return self.RESP_SUCCESS
        except Exception as e:
            result = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, result)
            return self.RESP_WARN
