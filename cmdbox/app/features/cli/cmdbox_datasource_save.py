from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.features.cli.datasource import datasource_base
from cmdbox.app.options import Options
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
import argparse
import json
import logging
import pydantic


class DatasourceSave(datasource_base.DatasourceBase, validator.Validator, limiter.LimitedFeature):
    def get_mode(self) -> Union[str, List[str]]:
        return 'datasource'

    def get_cmd(self) -> str:
        return 'save'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="データソース接続設定を追加/保存します。",
            description_en="Adds or saves a datasource connection configuration.",
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
                     description_ja="データソース接続設定の識別名を指定します。",
                     description_en="Specify the identifier name of the datasource connection configuration."),
                dict(opt="dbtype", type=Options.T_STR, default="sqlite", required=True, multi=False, hide=False,
                     choice=["postgresql", "sqlite"],
                     choice_show=dict(
                         postgresql=["db_host", "db_port", "db_user", "db_password", "db_name", "db_timeout"],
                         sqlite=["db_path"],
                     ),
                     description_ja="データベースの種類を指定します。",
                     description_en="Specify the database type."),
                dict(opt="scope", type=Options.T_STR, default="server", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="スコープを指定します。`client` はクライアント側、`server` はサーバー側です。`current` は実行時ディレクトリです。",
                     description_en="Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory.",),
                dict(opt="db_host", type=Options.T_STR, default="localhost", required=False, multi=False, hide=False, choice=None,
                     description_ja="データベースサーバーのホストを指定します（PostgreSQL用）。",
                     description_en="Specify the database server host (for PostgreSQL)."),
                dict(opt="db_port", type=Options.T_INT, default=5432, required=False, multi=False, hide=False, choice=None,
                     description_ja="データベースサーバーのポートを指定します（PostgreSQL用）。",
                     description_en="Specify the database server port (for PostgreSQL)."),
                dict(opt="db_user", type=Options.T_STR, default="postgres", required=False, multi=False, hide=False, choice=None,
                     description_ja="データベースに接続するユーザー名を指定します（PostgreSQL用）。",
                     description_en="Specify the username for database connection (for PostgreSQL)."),
                dict(opt="db_password", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="データベースに接続するパスワードを指定します（PostgreSQL用）。",
                     description_en="Specify the password for database connection (for PostgreSQL)."),
                dict(opt="db_name", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="接続するデータベース名を指定します（PostgreSQL用）。",
                     description_en="Specify the database name to connect to (for PostgreSQL)."),
                dict(opt="db_timeout", type=Options.T_INT, default=120, required=False, multi=False, hide=False, choice=None,
                     description_ja="データベース接続のタイムアウトを指定します（PostgreSQL用）。",
                     description_en="Specify the database connection timeout (for PostgreSQL)."),
                dict(opt="db_path", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="out",
                     description_ja="SQLiteのデータベースファイルのパスを指定します（SQLite用）。",
                     description_en="Specify the path to the SQLite database file (for SQLite)."),
            ]
        )

    @limiter.apprun_check_limit
    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if args.scope == 'client' and not args.client_data:
            result = dict(warn="client_data is required when scope is 'client'.")
            logger.warning("client_data is required when scope is 'client'.")
            return self.RESP_WARN, result, None
        payload = dict(
            dsname=args.dsname,
            dbtype=args.dbtype,
            scope=args.scope,
            client_data=args.client_data if hasattr(args, 'client_data') else None,
            db_host=args.db_host if hasattr(args, 'db_host') else None,
            db_port=args.db_port if hasattr(args, 'db_port') else None,
            db_user=args.db_user if hasattr(args, 'db_user') else None,
            db_password=args.db_password if hasattr(args, 'db_password') else None,
            db_name=args.db_name if hasattr(args, 'db_name') else None,
            db_timeout=args.db_timeout if hasattr(args, 'db_timeout') else None,
            db_path=args.db_path if hasattr(args, 'db_path') else None,
        )
        payload_b64 = convert.str2b64str(common.to_str(payload))
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
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

    @limiter.svrun_check_limit
    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            self.save_datasource(
                data_dir,
                dsname=payload['dsname'],
                dbtype=payload['dbtype'],
                scope=payload.get('scope', 'server'),
                client_data=payload.get('client_data'),
                db_host=payload.get('db_host'),
                db_port=payload.get('db_port'),
                db_user=payload.get('db_user'),
                db_password=payload.get('db_password'),
                db_name=payload.get('db_name'),
                db_timeout=payload.get('db_timeout'),
                db_path=payload.get('db_path'),
            )
            result = dict(success=dict(data=f"Datasource configuration '{payload['dsname']}' saved successfully."))
            redis_cli.rpush(reskey, result)
            return self.RESP_SUCCESS
        except Exception as e:
            result = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, result)
            return self.RESP_WARN

    def apprun_registrations(self, data_dir, logger, args, msg):
        raise NotImplementedError("In the Limiter settings, please use `scope=server`.")

    def svrun_registrations(self, data_dir, logger, opt, msg):
        datasource_dir = data_dir / '.datasource'
        count = 0
        if datasource_dir.exists() and datasource_dir.is_dir():
            paths = datasource_dir.glob(f"datasource-*.json")
            for p in sorted(paths):
                name = p.name
                if not name.startswith('datasource-') or not name.endswith('.json'):
                    continue
                count += 1
        return count
