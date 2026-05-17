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


class DatasourceTblDrop(datasource_base.DatasourceBase, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'datasource'

    def get_cmd(self) -> str:
        return 'tbl_drop'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="指定したデータソースのテーブルを削除します。",
            description_en="Drops a table from the specified datasource.",
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
                     description_ja="削除するテーブル名を指定します。",
                     description_en="Specify the table name to drop."),
                dict(opt="if_exists", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="テーブルが存在しない場合にエラーを出さないようにするかどうかを指定します。",
                     description_en="Specify whether to suppress an error if the table does not exist."),
            ]
        )

    def _do_run(self, data_dir: Path, payload: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
        conn = None
        try:
            schema = payload.get('schema') or None
            tblname = self.validate_identifier(payload['tblname'])
            if_exists = payload.get('if_exists', False)
            ie_clause = 'IF EXISTS ' if if_exists else ''
            conn, dbtype = self.get_connection(payload)
            qualified_tbl = self.qualified_name(schema, tblname, dbtype)
            sql = f"DROP TABLE {ie_clause}{qualified_tbl}"
            with conn.cursor() as cur:
                cur.execute(sql)
            conn.commit()
            return dict(success=dict(data=f"Table '{qualified_tbl}' dropped."))
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
            if_exists=args.if_exists if hasattr(args, 'if_exists') else False,
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
