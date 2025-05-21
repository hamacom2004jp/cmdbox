from cmdbox.app import common, client
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.features.cli import audit_base
from cmdbox.app.options import Options
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import uuid


class AuditWrite(audit_base.AuditBase):
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
        return 'write'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['discription_ja'] = "監査を記録します。"
        opt['discription_en'] = "Record the audit."
        opt['choice'] += [
            dict(opt="audit_type", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=Options.AUDITS,
                 discription_ja="監査の種類を指定します。",
                 discription_en="Specifies the audit type."),
            dict(opt="clmsg_id", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="クライアントのメッセージIDを指定します。省略した場合はuuid4で生成されます。",
                 discription_en="Specifies the message ID of the client. If omitted, uuid4 will be generated."),
            dict(opt="clmsg_date", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="クライアントのメッセージ発生日時を指定します。省略した場合はサーバーの現在日時が使用されます。",
                 discription_en="Specifies the date and time the client message occurred. If omitted, the server's current date/time is used."),
            dict(opt="clmsg_src", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="クライアントのメッセージの発生源を指定します。通常 `cmdbox.app.feature.Feature` を継承したクラス名を指定します。",
                 discription_en="Specifies the source of client messages. Usually specifies the name of a class that extends `cmdbox.app.feature.Feature` ."),
            dict(opt="clmsg_title", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="クライアントのメッセージタイトルを指定します。通常コマンドタイトルを指定します。",
                 discription_en="Specifies the client message title. Usually specifies the command title."),
            dict(opt="clmsg_user", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="クライアントのメッセージを発生させたユーザーを指定します。",
                 discription_en="SpecSpecifies the user who generated the client message."),
            dict(opt="clmsg_body", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                 discription_ja="クライアントのメッセージの本文を辞書形式で指定します。",
                 discription_en="Specifies the body of the client's message in dictionary format."),
            dict(opt="clmsg_tag", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                 discription_ja="クライアントのメッセージのタグを指定します。後で検索しやすくするために指定します。",
                 discription_en="Specifies the tag for the client's message. Specify to make it easier to search later."),
            dict(opt="retention_period_days", type=Options.T_INT, default=365, required=False, multi=False, hide=True, choice=None, web="mask",
                 discription_ja="監査を保存する日数を指定します。この日数より古い監査は削除します。0以下を指定すると無期限で保存されます。",
                 discription_en="Specify the number of days to keep the audit. If the number is less than or equal to 0, the audit will be kept indefinitely."),
        ]
        return opt
    
    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'audit_write'

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
            common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.audit_type is None:
            msg = dict(warn=f"Please specify the --audit_type option.")
            common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if args.clmsg_id is None:
            args.clmsg_id = str(uuid.uuid4())
        if args.clmsg_date is None:
            args.clmsg_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + common.get_tzoffset_str()

        audit_type_b64 = convert.str2b64str(args.audit_type)
        clmsg_id_b64 = convert.str2b64str(args.clmsg_id)
        clmsg_date_b64 = convert.str2b64str(args.clmsg_date)
        clmsg_src_b64 = convert.str2b64str(args.clmsg_src) if args.clmsg_src is not None else ''
        clmsg_title_b64 = convert.str2b64str(args.clmsg_title) if args.clmsg_title is not None else ''
        clmsg_user_b64 = convert.str2b64str(args.clmsg_user) if args.clmsg_user is not None else ''
        clmsg_body_str = json.dumps(args.clmsg_body, default=common.default_json_enc, ensure_ascii=False) if args.clmsg_body is not None else '{}'
        clmsg_body_b64 = convert.str2b64str(clmsg_body_str)
        clmsg_tag_str = json.dumps(args.clmsg_tag, default=common.default_json_enc, ensure_ascii=False) if args.clmsg_tag is not None else '[]'
        clmsg_tag_b64 = convert.str2b64str(clmsg_tag_str)
        pg_enabled = args.pg_enabled
        pg_host_b64 = convert.str2b64str(args.pg_host)
        pg_port = args.pg_port if isinstance(args.pg_port, int) else None
        pg_user_b64 = convert.str2b64str(args.pg_user)
        pg_password_b64 = convert.str2b64str(args.pg_password)
        pg_dbname_b64 = convert.str2b64str(args.pg_dbname)

        if logger.level == logging.DEBUG:
            logger.debug(f"audit write args: {args}")
        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        cl.redis_cli.send_cmd(self.get_svcmd(),
                              [audit_type_b64, clmsg_id_b64, clmsg_date_b64, clmsg_src_b64, clmsg_title_b64, clmsg_user_b64, clmsg_body_b64, clmsg_tag_b64,
                               pg_enabled, pg_host_b64, pg_port, pg_user_b64, pg_password_b64, pg_dbname_b64,
                               args.retention_period_days],
                              retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=True)
        ret = dict(success=True)
        #common.print_format(ret, False, tm, None, False, pf=pf)
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
        if logger.level == logging.DEBUG:
            logger.debug(f"audit write svrun msg: {msg}")
        audit_type = convert.b64str2str(msg[2])
        clmsg_id = convert.b64str2str(msg[3])
        clmsg_date = convert.b64str2str(msg[4])
        clmsg_src = convert.b64str2str(msg[5])
        clmsg_title = convert.b64str2str(msg[6])
        clmsg_user = convert.b64str2str(msg[7])
        clmsg_body = convert.b64str2str(msg[8])
        clmsg_tags = convert.b64str2str(msg[9])
        pg_enabled = True if msg[10]=='True' else False
        pg_host = convert.b64str2str(msg[11])
        pg_port = int(msg[12]) if msg[12]!='None' else None
        pg_user = convert.b64str2str(msg[13])
        pg_password = convert.b64str2str(msg[14])
        pg_dbname = convert.b64str2str(msg[15])
        retention_period_days = int(msg[16]) if msg[16] != 'None' else None
        svmsg_id = str(uuid.uuid4())
        st = self.write(msg[1], audit_type, clmsg_id, clmsg_date, clmsg_src, clmsg_title, clmsg_user, clmsg_body, clmsg_tags, svmsg_id,
                        pg_enabled, pg_host, pg_port, pg_user, pg_password, pg_dbname,
                        retention_period_days,
                        data_dir, logger, redis_cli)
        return st

    def write(self, reskey:str, audit_type:str, clmsg_id:str, clmsg_date:str, clmsg_src:str, clmsg_title:str,
              clmsg_user:str, clmsg_body:str, clmsg_tags:str, svmsg_id:str,
              pg_enabled:bool, pg_host:str, pg_port:int, pg_user:str, pg_password:str, pg_dbname:str,
              retention_period_days:int,
              data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient) -> int:
        """
        監査ログを書き込む

        Args:
            reskey (str): レスポンスキー
            audit_type (str): 監査の種類
            clmsg_id (str): クライアントメッセージID
            clmsg_date (str): クライアントメッセージ発生日時
            clmsg_src (str): クライアントメッセージの発生源
            clmsg_title (str): クライアントメッセージのタイトル
            clmsg_user (str): クライアントメッセージの発生させたユーザー
            clmsg_body (str): クライアントメッセージの本文
            clmsg_tags (str): クライアントメッセージのタグ
            svmsg_id (str): サーバーメッセージID
            pg_enabled (bool): PostgreSQLを使用する場合はTrue
            pg_host (str): PostgreSQLホスト
            pg_port (int): PostgreSQLポート
            pg_user (str): PostgreSQLユーザー
            pg_password (str): PostgreSQLパスワード
            pg_dbname (str): PostgreSQLデータベース名
            retention_period_days (int): 監査を保存する日数
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント

        Returns:
            int: レスポンスコード
        """
        try:
            with self.initdb(data_dir, logger, pg_enabled, pg_host, pg_port, pg_user, pg_password, pg_dbname) as conn:
                cursor = conn.cursor()
                try:
                    svmsg_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S') + common.get_tzoffset_str()
                    if not pg_enabled:
                        cursor.execute('''
                            INSERT INTO audit (audit_type, clmsg_id, clmsg_date, clmsg_src, clmsg_title, clmsg_user, clmsg_body, clmsg_tag, 
                                            svmsg_id, svmsg_date)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ''', (audit_type, clmsg_id, clmsg_date, clmsg_src, clmsg_title, clmsg_user, clmsg_body, clmsg_tags, svmsg_id, svmsg_date))
                        if retention_period_days is not None and retention_period_days > 0:
                            cursor.execute('DELETE FROM audit WHERE svmsg_date < datetime(CURRENT_TIMESTAMP, ?)',
                                           (f'-{retention_period_days} days',))
                    else:
                        cursor.execute('''
                            INSERT INTO audit (audit_type, clmsg_id, clmsg_date, clmsg_src, clmsg_title, clmsg_user, clmsg_body, clmsg_tag, 
                                            svmsg_id, svmsg_date)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        ''', (audit_type, clmsg_id, clmsg_date, clmsg_src, clmsg_title, clmsg_user, clmsg_body, clmsg_tags, svmsg_id, svmsg_date))
                        if retention_period_days is not None and retention_period_days > 0:
                            cursor.execute("DELETE FROM audit WHERE svmsg_date < CURRENT_TIMESTAMP + %s ",
                                           (f'-{retention_period_days} day',))
                    conn.commit()
                    rescode, msg = (self.RESP_SCCESS, dict(success=True))
                    redis_cli.rpush(reskey, msg)
                    return rescode
                finally:
                    cursor.close()
        except Exception as e:
            logger.warning(f"Failed to write: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to write: {e}"))
            return self.RESP_WARN
