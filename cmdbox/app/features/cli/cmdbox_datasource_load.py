from cmdbox.app import common, client, feature
from cmdbox.app.commons import cache, convert, redis_client, resdata, validator
from cmdbox.app.features.cli.datasource import datasource_base
from cmdbox.app.options import Options
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
import argparse
import json
import logging
import pydantic


class DatasourceLoad(datasource_base.DatasourceBase, validator.Validator):
    def __init__(self, appcls, ver, language = None):
        super().__init__(appcls, ver, language)
        self.datasource_cache = cache.MemoryCache()

    def get_mode(self) -> Union[str, List[str]]:
        return 'datasource'

    def get_cmd(self) -> str:
        return 'load'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="データソース接続設定を読み込みます。",
            description_en="Loads a datasource connection configuration.",
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
                dict(opt="dsname", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="読み込むデータソース接続設定の識別名を指定します。",
                     description_en="Specify the identifier name of the datasource configuration to load."),
                dict(opt="cache_timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=False, choice=None,
                     description_ja="設定をキャッシュする時間を秒数で指定します。",
                     description_en="Specify the duration, in seconds, for which settings should be cached."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        # データソース接続設定のキャッシュが有効で、かつキャッシュが存在し、キャッシュの有効期限が切れていない場合はキャッシュを返す
        cached = self.datasource_cache.get(args.dsname)
        if cached is not None:
            ret = dict(success=dict(data=cached))
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, ret, None

        payload = dict(dsname=args.dsname)
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl

        # 読み込んだデータソース接続設定をキャッシュする
        self.datasource_cache.set(args.dsname, ret.get('success', {}).get('data', None), args.cache_timeout)
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Configure(resdata.Base):
            dsname: Union[str, None] = pydantic.Field(default=None, description="データソース名")
            dbtype: Union[str, None] = pydantic.Field(default=None, description="データベース種別")
            scope: Union[str, None] = pydantic.Field(default=None, description="参照スコープ")
            client_data: Union[str, None] = pydantic.Field(default=None, description="クライアントスコープの場合のローカルデータパス")
            db_host: Union[str, None] = pydantic.Field(default=None, description="データベースホスト")
            db_port: Union[int, None] = pydantic.Field(default=None, description="データベースポート")
            db_user: Union[str, None] = pydantic.Field(default=None, description="データベースユーザー名")
            db_password: Union[str, None] = pydantic.Field(default=None, description="データベースパスワード")
            db_name: Union[str, None] = pydantic.Field(default=None, description="データベース名")
            db_timeout: Union[int, None] = pydantic.Field(default=None, description="データベース接続のタイムアウト（秒）")
            db_path: Union[str, None] = pydantic.Field(default=None, description="SQLiteデータベースファイルパス")
        class Data(resdata.Data):
            data: Union[Configure, None] = pydantic.Field(default=None, description="処理結果のデータ")
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
            configure = self.load_datasource(data_dir, payload['dsname'])
            result = dict(success=dict(data=configure))
            redis_cli.rpush(reskey, result)
            return self.RESP_SUCCESS
        except Exception as e:
            result = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, result)
            return self.RESP_WARN
