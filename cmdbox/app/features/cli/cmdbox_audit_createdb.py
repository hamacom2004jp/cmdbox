from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.features.cli import audit_base
from cmdbox.app.options import Options
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import psycopg


class AuditCreatedb(feature.UnsupportEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'audit'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'createdb'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=True,
            discription_ja="監査を記録するデータベースを作成します。",
            discription_en="Create a database to record audits.",
            choice=[
                dict(opt="pg_host", type=Options.T_STR, default='localhost', required=True, multi=False, hide=False, choice=None,
                     discription_ja="postgresqlホストを指定する。",
                     discription_en="Specify the postgresql host."),
                dict(opt="pg_port", type=Options.T_INT, default=5432, required=True, multi=False, hide=False, choice=None,
                     discription_ja="postgresqlのポートを指定する。",
                     discription_en="Specify the postgresql port."),
                dict(opt="pg_user", type=Options.T_STR, default='postgres', required=True, multi=False, hide=False, choice=None,
                     discription_ja="postgresqlのユーザー名を指定する。",
                     discription_en="Specify the postgresql user name."),
                dict(opt="pg_password", type=Options.T_STR, default='postgres', required=True, multi=False, hide=False, choice=None,
                     discription_ja="postgresqlのパスワードを指定する。",
                     discription_en="Specify the postgresql password."),
                dict(opt="pg_dbname", type=Options.T_STR, default='audit', required=True, multi=False, hide=False, choice=None,
                     discription_ja="postgresqlデータベース名を指定します。",
                     discription_en="Specify the postgresql database name."),
                dict(opt="new_pg_dbname", type=Options.T_STR, default='audit', required=True, multi=False, hide=False, choice=None,
                     discription_ja="新しいpostgresqlデータベース名を指定します。",
                     discription_en="Specify a new postgresql database name."),

                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのサービスホストを指定します。",
                     discription_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのサービスポートを指定します。",
                     discription_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                     discription_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
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


    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'audit_create'

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if args.svname is None:
            msg = dict(warn=f"Please specify the --svname option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.pg_host is None:
            msg = dict(warn=f"Please specify the --pg_host option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.pg_port is None:
            msg = dict(warn=f"Please specify the --pg_port option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.pg_user is None:
            msg = dict(warn=f"Please specify the --pg_user option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.pg_password is None:
            msg = dict(warn=f"Please specify the --pg_password option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.pg_dbname is None:
            msg = dict(warn=f"Please specify the --pg_dbname option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.new_pg_dbname is None:
            msg = dict(warn=f"Please specify the --new_pg_dbname option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None

        pg_host_b64 = convert.str2b64str(args.pg_host)
        pg_port = args.pg_port if isinstance(args.pg_port, int) else None
        pg_user_b64 = convert.str2b64str(args.pg_user)
        pg_password_b64 = convert.str2b64str(args.pg_password)
        pg_dbname_b64 = convert.str2b64str(args.pg_dbname)
        new_pg_dbname_b64 = convert.str2b64str(args.new_pg_dbname)

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                    [pg_host_b64, pg_port, pg_user_b64, pg_password_b64, pg_dbname_b64, new_pg_dbname_b64],
                                     retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, False, tm, None, False, pf=pf)
        if 'success' not in ret:
            return 1, ret, cl
        return 0, ret, cl

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        この機能のサーバー側の実行を行います

        Args:
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            msg (List[str]): 受信メッセージ
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        
        Returns:
            int: 終了コード
        """
        pg_host = convert.b64str2str(msg[2])
        pg_port = int(msg[3]) if msg[3]!='None' else None
        pg_user = convert.b64str2str(msg[4])
        pg_password = convert.b64str2str(msg[5])
        pg_dbname = convert.b64str2str(msg[6])
        new_pg_dbname = convert.b64str2str(msg[7])
        st = self.createdb(msg[1], pg_host, pg_port, pg_user, pg_password, pg_dbname, new_pg_dbname,
                        data_dir, logger, redis_cli)
        return st

    def createdb(self, reskey:str, pg_host:str, pg_port:int, pg_user:str, pg_password:str, pg_dbname:str, new_pg_dbname:str,
              data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient) -> int:
        """
        監査ログデータベースを作成する

        Args:
            reskey (str): レスポンスキー
            pg_host (str): PostgreSQLホスト
            pg_port (int): PostgreSQLポート
            pg_user (str): PostgreSQLユーザー
            pg_password (str): PostgreSQLパスワード
            pg_dbname (str): PostgreSQLデータベース名
            new_pg_dbname (str): 新しいPostgreSQLデータベース名
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント

        Returns:
            int: レスポンスコード
        """
        try:
            constr = f"host={pg_host} port={pg_port} user={pg_user} password={pg_password} dbname={pg_dbname} connect_timeout=5"
            with psycopg.connect(constr, autocommit=True) as conn:
                cursor = conn.cursor()
                try:
                    cursor.execute(f'create database {new_pg_dbname}')
                    rescode, msg = (self.RESP_SCCESS, dict(success=True))
                    redis_cli.rpush(reskey, msg)
                    return rescode
                finally:
                    cursor.close()
        except Exception as e:
            logger.warning(f"Failed to createdb: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to createdb: {e}"))
            return self.RESP_WARN
