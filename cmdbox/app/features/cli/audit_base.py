from cmdbox.app import feature
from cmdbox.app.options import Options
from pathlib import Path
import logging
import sqlite3


class AuditBase(feature.ResultEdgeFeature):
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False,
            discription_ja="",
            discription_en="",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのサービスホストを指定します。",
                     discription_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのサービスポートを指定します。",
                     discription_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                     discription_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default="server", required=True, multi=False, hide=True, choice=None, web="readonly",
                     discription_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     discription_en="Specify the service name of the inference server. If omitted, `server` is used."),

                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     discription_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     discription_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     discription_ja="Redisサーバーに再接続までの秒数を指定します。",
                     discription_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="15", required=False, multi=False, hide=True, choice=None,
                     discription_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     discription_en="Specify the maximum waiting time until the server responds."),
            ]
        )
    
    def initdb(self, data_dir:Path, logger:logging.Logger) -> sqlite3.Connection:
        """
        データベースを初期化します

        Args:
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー

        Returns:
            sqlite3.Connection: データベース接続
        """
        db_path = data_dir / '.audit' / 'audit.db'
        db_path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT COUNT(*) FROM sqlite_master WHERE TYPE="table" AND NAME="audit"')
            if cursor.fetchone()[0] == 0:
                # テーブルが存在しない場合は作成
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS audit (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        audit_type TEXT,
                        clmsg_id TEXT,
                        clmsg_date TEXT,
                        clmsg_src TEXT,
                        clmsg_user TEXT,
                        clmsg_body JSON,
                        clmsg_tag JSON,
                        svmsg_id TEXT,
                        svmsg_date TEXT DEFAULT CURRENT_TIMESTAMP
                    )
                ''')
        finally:
            cursor.close()
        conn.commit()
        return conn

