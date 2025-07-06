from cmdbox.app import feature
from cmdbox.app.options import Options
from pathlib import Path
from typing import Any
import logging
import psycopg
import sqlite3


class AuditBase(feature.ResultEdgeFeature):
    TBL_COLS = ['audit_type', 'clmsg_id', 'clmsg_date', 'clmsg_src', 'clmsg_title', 'clmsg_user', 'clmsg_body', 'clmsg_tag', 'svmsg_id', 'svmsg_date']
    DT_FMT = ['%Y/%m/%d %H:%M', '%Y/%m/%d %H', '%Y/%m/%d', '%Y/%m', '%Y', '%m', '%u']
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=True,
            description_ja="",
            description_en="",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                     description_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),

                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="15", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),

                dict(opt="pg_enabled", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False], web="mask",
                     description_ja="postgresqlデータベース・サーバを使用する場合はTrueを指定します。",
                     description_en="Specify True if using the postgresql database server."),
                dict(opt="pg_host", type=Options.T_STR, default='localhost', required=False, multi=False, hide=True, choice=None, web="mask",
                     description_ja="postgresqlホストを指定する。",
                     description_en="Specify the postgresql host."),
                dict(opt="pg_port", type=Options.T_INT, default=5432, required=False, multi=False, hide=True, choice=None, web="mask",
                     description_ja="postgresqlのポートを指定する。",
                     description_en="Specify the postgresql port."),
                dict(opt="pg_user", type=Options.T_STR, default='postgres', required=False, multi=False, hide=True, choice=None, web="mask",
                     description_ja="postgresqlのユーザー名を指定する。",
                     description_en="Specify the postgresql user name."),
                dict(opt="pg_password", type=Options.T_STR, default='postgres', required=False, multi=False, hide=True, choice=None, web="mask",
                     description_ja="postgresqlのパスワードを指定する。",
                     description_en="Specify the postgresql password."),
                dict(opt="pg_dbname", type=Options.T_STR, default='audit', required=False, multi=False, hide=True, choice=None,
                     description_ja="postgresqlデータベース名を指定します。",
                     description_en="Specify the postgresql database name."),
            ]
        )
    
    def initdb(self, data_dir:Path, logger:logging.Logger, pg_enabled:bool, pg_host:str, pg_port:int, pg_user:str, pg_password:str, pg_dbname:str) -> Any:
        """
        データベースを初期化します

        Args:
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            pg_enabled (bool): PostgreSQLを使用するかどうか
            pg_host (str): PostgreSQLホスト
            pg_port (int): PostgreSQLポート
            pg_user (str): PostgreSQLユーザー名
            pg_password (str): PostgreSQLパスワード
            pg_dbname (str): PostgreSQLデータベース名

        Returns:
            Any: データベース接続オブジェクト
        """
        if pg_enabled:
            if logger.level == logging.DEBUG:
                logger.debug(f"Initializing database with pg_enabled={pg_enabled}, pg_host={pg_host}, pg_port={pg_port}, pg_user={pg_user}, pg_dbname={pg_dbname}")
            constr = f"host={pg_host} port={pg_port} user={pg_user} password={pg_password} dbname={pg_dbname} connect_timeout=60"
            conn = psycopg.connect(constr, autocommit=False)
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT count(*) FROM information_schema.tables WHERE table_name='audit'")
                row = cursor.fetchone()
                if logger.level == logging.DEBUG:
                    logger.debug(f"SQL query: SELECT count(*) FROM information_schema.tables WHERE table_name='audit'")
                    logger.debug(f"SQL row  : {row}")
                if row[0] == 0:
                    # テーブルが存在しない場合は作成
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS audit (
                            id SERIAL PRIMARY KEY,
                            audit_type TEXT,
                            clmsg_id TEXT,
                            clmsg_date TIMESTAMP WITH TIME ZONE,
                            clmsg_src TEXT,
                            clmsg_title TEXT,
                            clmsg_user TEXT,
                            clmsg_body JSON,
                            clmsg_tag JSON,
                            svmsg_id TEXT,
                            svmsg_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
            finally:
                conn.commit()
                cursor.close()
        else:
            db_path = data_dir / '.audit' / 'audit.db'
            if logger.level == logging.DEBUG:
                logger.debug(f"Initializing database with db_path={db_path}")
            db_path.parent.mkdir(parents=True, exist_ok=True)
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            try:
                cursor.execute("SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='audit'")
                row = cursor.fetchone()
                if logger.level == logging.DEBUG:
                    logger.debug(f"SQL query: SELECT COUNT(*) FROM sqlite_master WHERE TYPE='table' AND NAME='audit'")
                    logger.debug(f"SQL row  : {row}")
                if row[0] == 0:
                    # テーブルが存在しない場合は作成
                    cursor.execute('''
                        CREATE TABLE IF NOT EXISTS audit (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            audit_type TEXT,
                            clmsg_id TEXT,
                            clmsg_date TEXT,
                            clmsg_src TEXT,
                            clmsg_title TEXT,
                            clmsg_user TEXT,
                            clmsg_body JSON,
                            clmsg_tag JSON,
                            svmsg_id TEXT,
                            svmsg_date TEXT DEFAULT CURRENT_TIMESTAMP
                        )
                    ''')
            finally:
                cursor.close()
        return conn
