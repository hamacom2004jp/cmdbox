from cmdbox.app import common, client
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.features.cli.datasource import datasource_base
from cmdbox.app.options import Options
from pathlib import Path
from typing import Any, Dict, List, Tuple, Union
import argparse
import json
import logging
import pydantic


class DatasourceIdxCreate(datasource_base.DatasourceBase, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'datasource'

    def get_cmd(self) -> str:
        return 'idx_create'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="指定したデータソースのテーブルにインデックスを作成します。",
            description_en="Creates an index on a table in the specified datasource.",
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
                     description_ja="接続先データソースの識別名を指定します。",
                     description_en="Specify the identifier name of the target datasource."),
                dict(opt="schema", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="スキーマ名を指定します。省略時はスキーマなしで操作します。",
                     description_en="Specify the schema name. If omitted, the operation is performed without a schema."),
                dict(opt="tblname", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="インデックスを作成するテーブル名を指定します。",
                     description_en="Specify the table name on which to create the index."),
                dict(opt="idxname", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="作成するインデックス名を指定します。",
                     description_en="Specify the index name to create."),
                dict(opt="idxcolumns", type=Options.T_STR, default=None, required=True, multi=True, hide=False, choice=None,
                     description_ja="インデックスを作成するカラム名を指定します。複数指定可能です。例: `col1` `col2`",
                     description_en="Specify the column names for the index. Multiple values can be specified. e.g. `col1` `col2`"),
                dict(opt="unique", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="一意インデックスを作成するかどうかを指定します。",
                     description_en="Specify whether to create a unique index."),
                dict(opt="if_not_exists", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="インデックスが既に存在する場合にエラーを出さないようにするかどうかを指定します。",
                     description_en="Specify whether to suppress an error if the index already exists."),
            ]
        )

    def _do_run(self, data_dir: Path, payload: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
        conn = None
        try:
            schema = payload.get('schema') or None
            tblname = self.validate_identifier(payload['tblname'])
            idxname = self.validate_identifier(payload['idxname'])
            cols_clause = self.validate_columns(','.join(payload['idxcolumns']) if isinstance(payload['idxcolumns'], list) else payload['idxcolumns'])
            if cols_clause == '*':
                raise ValueError("Column names must be specified for index creation (wildcard '*' is not allowed).")
            unique = bool(payload.get('unique', False))
            if_not_exists = bool(payload.get('if_not_exists', True))
            unique_clause = 'UNIQUE ' if unique else ''
            ine_clause = 'IF NOT EXISTS ' if if_not_exists else ''
            conn, dbtype = self.get_connection(payload)
            qualified_tbl = self.qualified_name(schema, tblname, dbtype)
            sql = f"CREATE {unique_clause}INDEX {ine_clause}{idxname} ON {qualified_tbl} ({cols_clause})"
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
            return dict(success=dict(data=f"Index '{idxname}' created on '{qualified_tbl}'."))
        except Exception as e:
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            return dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
        finally:
            if conn is not None:
                try:
                    conn.close()
                except Exception:
                    pass

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        payload = dict(
            dsname=args.dsname,
            schema=args.schema if hasattr(args, 'schema') else None,
            tblname=args.tblname,
            idxname=args.idxname,
            idxcolumns=args.idxcolumns,
            unique=args.unique if hasattr(args, 'unique') else False,
            if_not_exists=args.if_not_exists if hasattr(args, 'if_not_exists') else True,
        )
        try:
            return self.route_apprun(args, payload, logger, tm, pf)
        except Exception as e:
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            ret = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            return self.RESP_WARN, ret, None

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: Union[str, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient,
              msg: List[str], sessions: Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        payload = json.loads(convert.b64str2str(msg[2]))
        ret = self._do_run(data_dir, payload, logger)
        redis_cli.rpush(reskey, ret)
        return self.RESP_SUCCESS if 'success' in ret else self.RESP_WARN
