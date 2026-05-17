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


class DatasourceDataSelect(datasource_base.DatasourceBase, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'datasource'

    def get_cmd(self) -> str:
        return 'data_select'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="指定したデータソースのテーブルからレコードを検索します。",
            description_en="Selects records from a table of the specified datasource.",
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
                     description_ja="検索対象テーブル名を指定します。",
                     description_en="Specify the target table name."),
                dict(opt="column", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="取得するカラム名を指定します。省略時は全カラムを取得します。複数指定する場合は繰り返し指定します。例: `id` `name` `age`",
                     description_en="Specify column names to retrieve. If omitted, all columns are retrieved. Repeat for multiple columns. e.g. `id` `name` `age`"),
                dict(opt="where_data", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="WHERE条件のカラム名と値を key=value 形式で指定します（AND結合）。複数条件は繰り返し指定します。",
                     description_en="Specify WHERE condition column names and values in key=value format (AND join). Repeat for multiple conditions."),
                dict(opt="order_by", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="ORDER BY句をカンマ区切りで指定します。例: `id DESC,name ASC`",
                     description_en="Specify ORDER BY clause as comma-separated values. e.g. `id DESC,name ASC`"),
                dict(opt="limit", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="取得する最大行数を指定します。",
                     description_en="Specify the maximum number of rows to retrieve."),
                dict(opt="offset", type=Options.T_INT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="取得開始位置のオフセットを指定します。",
                     description_en="Specify the offset for the starting position of retrieval."),
            ]
        )

    def _do_run(self, data_dir: Path, payload: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
        conn = None
        try:
            schema = payload.get('schema') or None
            tblname = self.validate_identifier(payload['tblname'])
            col_val = payload.get('column')
            cols_clause = self.validate_columns(','.join(col_val) if isinstance(col_val, list) else col_val)
            where_data: Dict[str, Any] = payload['where_data'] if payload.get('where_data') else {}
            order_by_raw = payload.get('order_by')
            limit = payload.get('limit')
            offset = payload.get('offset')
            conn, dbtype = self.get_connection(payload)
            qualified_tbl = self.qualified_name(schema, tblname, dbtype)
            where_clause, where_vals = self.build_where(where_data, dbtype)
            sql = f"SELECT {cols_clause} FROM {qualified_tbl}"
            if where_clause:
                sql += f" {where_clause}"
            if order_by_raw:
                order_by_clause = self.validate_order_by(order_by_raw)
                sql += f" ORDER BY {order_by_clause}"
            if limit is not None:
                sql += f" LIMIT {int(limit)}"
            if offset is not None:
                sql += f" OFFSET {int(offset)}"
            with conn.cursor() as cur:
                cur.execute(sql, where_vals)
                rows = self.fetch_as_dicts(cur)
            return dict(success=dict(data=rows))
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
            column=args.column if hasattr(args, 'column') else None,
            where_data=args.where_data if hasattr(args, 'where_data') else None,
            order_by=args.order_by if hasattr(args, 'order_by') else None,
            limit=args.limit if hasattr(args, 'limit') else None,
            offset=args.offset if hasattr(args, 'offset') else None,
        )
        try:
            return self.route_apprun(args, payload, logger, tm, pf)
        except Exception as e:
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            ret = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            return self.RESP_WARN, ret, None

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: List[Dict[str, Any]] = pydantic.Field(default_factory=list, description="取得したレコードのリスト")
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
