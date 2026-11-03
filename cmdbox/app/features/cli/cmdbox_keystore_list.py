from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class KeystoreList(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'keystore'

    def get_cmd(self) -> str:
        return 'list'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="キーストアのキー一覧を表示します。",
            description_en="List API keys in keystore.",
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
                     description_ja="検索したいキー名を指定します。中間マッチで検索します。",
                     description_en="Specify key name to search. Partial match is used."),
            ]
        )

    @validator.async_apprun_check
    async def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        payload = dict(
            kwd=args.kwd if hasattr(args, 'kwd') else None,
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
        class KeyRecord(resdata.Base):
            key_id: str = pydantic.Field(..., description="キーID")
            key_name: str = pydantic.Field(..., description="キー名")
            key_provider: Union[str, None] = pydantic.Field(default=None, description="キー発行者")
            key_type: Union[str, None] = pydantic.Field(default=None, description="キー種別")
            key_usage: List[str] = pydantic.Field(default_factory=list, description="利用対象コマンド")
            key_period_start: Union[str, None] = pydantic.Field(default=None, description="使用開始日時")
            key_period_end: Union[str, None] = pydantic.Field(default=None, description="使用終了日時")
            groups: List[str] = pydantic.Field(default_factory=list, description="所属グループ")
            owner: List[str] = pydantic.Field(default_factory=list, description="所有者")
            description: Union[str, None] = pydantic.Field(default=None, description="説明")
            created_at: Union[str, None] = pydantic.Field(default=None, description="作成日時")
        class Data(resdata.Data):
            data: List[KeyRecord] = pydantic.Field(default_factory=list, description="処理結果のデータ")
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
            kwd = f"*{payload.get('kwd')}*" if payload.get('kwd') else '*'

            results: List[Dict[str, Any]] = []
            if keystore_dir.exists() and keystore_dir.is_dir():
                for p in sorted(keystore_dir.glob(f"key_{kwd}.json")):
                    try:
                        cfg = common.load_file(p, lambda f: json.load(f), encoding='utf-8', nolock=True)
                        results.append(dict(
                            key_id=cfg.get('key_id'),
                            key_name=cfg.get('key_name'),
                            key_provider=cfg.get('key_provider'),
                            key_type=cfg.get('key_type') if cfg.get('key_type') else 'apikey',
                            key_usage=cfg.get('key_usage') if isinstance(cfg.get('key_usage'), list) else [],
                            key_period_start=cfg.get('key_period_start'),
                            key_period_end=cfg.get('key_period_end'),
                            groups=cfg.get('groups') if isinstance(cfg.get('groups'), list) else [],
                            owner=cfg.get('owner') if isinstance(cfg.get('owner'), list) else [],
                            description=cfg.get('description'),
                            created_at=cfg.get('created_at')
                        ))
                    except Exception:
                        continue

            result = dict(success=dict(data=results))
            redis_cli.rpush(reskey, result)
            return self.RESP_SUCCESS
        except Exception as e:
            result = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, result)
            return self.RESP_WARN
