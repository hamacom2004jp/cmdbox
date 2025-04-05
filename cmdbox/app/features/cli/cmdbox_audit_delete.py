from cmdbox.app import common, client
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.features.cli import audit_base
from cmdbox.app.options import Options
from pathlib import Path
from psycopg.rows import dict_row
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import sys


class AuditDelete(audit_base.AuditBase):
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
        return 'delete'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['discription_ja'] = "監査ログを削除します。"
        opt['discription_en'] = "Delete the audit log."
        opt['choice'] += [
            dict(opt="delete_audit_type", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=Options.AUDITS,
                 discription_ja="削除条件の監査の種類を指定します。",
                 discription_en="Specifies the type of audit for the delete condition."),
            dict(opt="delete_clmsg_id", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="削除条件のクライアントのメッセージIDを指定します。",
                 discription_en="Specify the message ID of the client for the delete condition."),
            dict(opt="delete_clmsg_sdate", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="削除条件のクライアントのメッセージ発生日時(開始)を指定します。",
                 discription_en="Specify the date and time (start) when the message occurred for the client in the delete condition."),
            dict(opt="delete_clmsg_edate", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="削除条件のクライアントのメッセージ発生日時(終了)を指定します。",
                 discription_en="Specify the date and time (end) when the message occurred for the client in the delete condition."),
            dict(opt="delete_clmsg_src", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="削除条件のクライアントのメッセージの発生源を指定します。LIKE検索を行います。",
                 discription_en="Specifies the source of the message for the client in the delete condition; performs a LIKE search."),
            dict(opt="delete_clmsg_user", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="削除条件のクライアントのメッセージの発生させたユーザーを指定します。LIKE検索を行います。",
                 discription_en="Specifies the user who generated the message for the client in the delete condition; performs a LIKE search."),
            dict(opt="delete_clmsg_body", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                 discription_ja="削除条件のクライアントのメッセージの本文を辞書形式で指定します。LIKE検索を行います。",
                 discription_en="Specifies the body of the client's message in the delete condition in dictionary format; performs a LIKE search."),
            dict(opt="delete_clmsg_tag", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                 discription_ja="削除条件のクライアントのメッセージのタグを指定します。",
                 discription_en="Specifies the tag of the client's message in the delete condition."),
            dict(opt="delete_svmsg_id", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="削除条件のサーバーのメッセージIDを指定します。",
                 discription_en="Specify the message ID of the server for the delete condition."),
            dict(opt="delete_svmsg_sdate", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="削除条件のサーバーのメッセージ発生日時(開始)を指定します。",
                 discription_en="Specify the date and time (start) when the message occurred for the server in the delete condition."),
            dict(opt="delete_svmsg_edate", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="削除条件のサーバーのメッセージ発生日時(終了)を指定します。",
                 discription_en="Specify the date and time (end) when the message occurred for the server in the delete condition."),
        ]
        return opt

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'audit_delete'

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
            common.print_format(msg, args.format, tm, None, False, pf=pf)
            return 1, msg, None

        delete_audit_type_b64 = convert.str2b64str(args.delete_audit_type)
        delete_clmsg_id_b64 = convert.str2b64str(args.delete_clmsg_id)
        delete_clmsg_sdate = args.delete_clmsg_sdate+common.get_tzoffset_str() if args.delete_clmsg_sdate else None
        delete_clmsg_sdate_b64 = convert.str2b64str(delete_clmsg_sdate)
        delete_clmsg_edate = args.delete_clmsg_edate+common.get_tzoffset_str() if args.delete_clmsg_edate else None
        delete_clmsg_edate_b64 = convert.str2b64str(delete_clmsg_edate)
        delete_clmsg_src_b64 = convert.str2b64str(args.delete_clmsg_src)
        delete_clmsg_user_b64 = convert.str2b64str(args.delete_clmsg_user)
        delete_clmsg_body_str = json.dumps(args.delete_clmsg_body, default=common.default_json_enc, ensure_ascii=False) if args.delete_clmsg_body else '{}'
        delete_clmsg_body_b64 = convert.str2b64str(delete_clmsg_body_str)
        delete_clmsg_tag_str = json.dumps(args.delete_clmsg_tag, default=common.default_json_enc, ensure_ascii=False) if args.delete_clmsg_tag else '[]'
        delete_clmsg_tag_b64 = convert.str2b64str(delete_clmsg_tag_str)
        delete_svmsg_id_b64 = convert.str2b64str(args.delete_svmsg_id)
        delete_svmsg_sdate_b64 = convert.str2b64str(args.delete_svmsg_sdate)
        delete_svmsg_edate_b64 = convert.str2b64str(args.delete_svmsg_edate)
        pg_enabled = args.pg_enabled
        pg_host_b64 = convert.str2b64str(args.pg_host)
        pg_port = args.pg_port if isinstance(args.pg_port, int) else None
        pg_user_b64 = convert.str2b64str(args.pg_user)
        pg_password_b64 = convert.str2b64str(args.pg_password)
        pg_dbname_b64 = convert.str2b64str(args.pg_dbname)

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                    [delete_audit_type_b64, delete_clmsg_id_b64, delete_clmsg_sdate_b64, delete_clmsg_edate_b64,
                                     delete_clmsg_src_b64, delete_clmsg_user_b64, delete_clmsg_body_b64, delete_clmsg_tag_b64, 
                                     delete_svmsg_id_b64, delete_svmsg_sdate_b64, delete_svmsg_edate_b64,
                                     pg_enabled, pg_host_b64, pg_port, pg_user_b64, pg_password_b64, pg_dbname_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, args.format, tm, None, False, pf=pf)

        if 'success' not in ret:
            return 1, ret, cl

        if 'data' in ret['success']:
            for row in ret['success']['data']:
                try:
                    row['clmsg_tag'] = json.loads(row['clmsg_tag'])
                except:
                    pass
                try:
                    row['clmsg_body'] = json.loads(row['clmsg_body'])
                except:
                    pass

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
        delete_audit_type = convert.b64str2str(msg[2])
        delete_clmsg_id = convert.b64str2str(msg[3])
        delete_clmsg_sdate = convert.b64str2str(msg[4])
        delete_clmsg_edate = convert.b64str2str(msg[5])
        delete_clmsg_src = convert.b64str2str(msg[6])
        delete_clmsg_user = convert.b64str2str(msg[7])
        body = json.loads(convert.b64str2str(msg[8]))
        tags = json.loads(convert.b64str2str(msg[9]))
        delete_svmsg_id = convert.b64str2str(msg[10])
        delete_svmsg_sdate = convert.b64str2str(msg[11])
        delete_svmsg_edate = convert.b64str2str(msg[12])
        pg_enabled = True if msg[13]=='True' else False
        pg_host = convert.b64str2str(msg[14])
        pg_port = int(msg[15]) if msg[15]!='None' else None
        pg_user = convert.b64str2str(msg[16])
        pg_password = convert.b64str2str(msg[17])
        pg_dbname = convert.b64str2str(msg[18])
        st = self.delete(msg[1],
                         delete_audit_type, delete_clmsg_id, delete_clmsg_sdate, delete_clmsg_edate,
                         delete_clmsg_src, delete_clmsg_user, body, tags,
                         delete_svmsg_id, delete_svmsg_sdate, delete_svmsg_edate,
                         pg_enabled, pg_host, pg_port, pg_user, pg_password, pg_dbname,
                         data_dir, logger, redis_cli)
        return st

    def delete(self, reskey:str,
               delete_audit_type:str, delete_clmsg_id:str, delete_clmsg_sdate:str, delete_clmsg_edate:str,
               delete_clmsg_src:str, delete_clmsg_user:str, delete_clmsg_body:Dict[str, Any], delete_clmsg_tags:List[str],
               delete_svmsg_id:str, delete_svmsg_sdate:str, delete_svmsg_edate:str,
               pg_enabled:bool, pg_host:str, pg_port:int, pg_user:str, pg_password:str, pg_dbname:str,
               data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient) -> int:
        """
        監査ログを検索する

        Args:
            reskey (str): レスポンスキー
            delete_audit_type (str): 監査の種類
            delete_clmsg_id (str): クライアントメッセージID
            delete_clmsg_sdate (str): クライアントメッセージ発生日時(開始)
            delete_clmsg_edate (str): クライアントメッセージ発生日時(終了)
            delete_clmsg_src (str): クライアントメッセージの発生源
            delete_clmsg_user (str): クライアントメッセージの発生させたユーザー
            delete_clmsg_body (Dict[str, Any]): クライアントメッセージの本文
            delete_clmsg_tags (List[str]): クライアントメッセージのタグ
            delete_svmsg_id (str): サーバーメッセージID
            delete_svmsg_sdate (str): サーバーメッセージ発生日時(開始)
            delete_svmsg_edate (str): サーバーメッセージ発生日時(終了)
            pg_enabled (bool): PostgreSQLを使用する場合はTrue
            pg_host (str): PostgreSQLホスト
            pg_port (int): PostgreSQLポート
            pg_user (str): PostgreSQLユーザー
            pg_password (str): PostgreSQLパスワード
            pg_dbname (str): PostgreSQLデータベース名
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
                    sql = f'DELETE FROM audit'
                    params = []
                    where = []
                    if delete_audit_type and delete_audit_type != 'None':
                        where.append(f'audit_type={"%s" if pg_enabled else "?"}')
                        params.append(delete_audit_type)
                    if delete_clmsg_id and delete_clmsg_id != 'None':
                        where.append(f'clmsg_id={"%s" if pg_enabled else "?"}')
                        params.append(delete_clmsg_id)
                    if delete_clmsg_sdate and delete_clmsg_sdate != 'None':
                        where.append(f'clmsg_date>={"%s" if pg_enabled else "?"}')
                        params.append(delete_clmsg_sdate)
                    if delete_clmsg_edate and delete_clmsg_edate != 'None':
                        where.append(f'clmsg_date<={"%s" if pg_enabled else "?"}')
                        params.append(delete_clmsg_edate)
                    if delete_clmsg_src and delete_clmsg_src != 'None':
                        where.append(f'clmsg_src LIKE {"%s" if pg_enabled else "?"}')
                        params.append(delete_clmsg_src)
                    if delete_clmsg_user and delete_clmsg_user != 'None':
                        where.append(f'clmsg_user LIKE {"%s" if pg_enabled else "?"}')
                        params.append(delete_clmsg_user)
                    if delete_clmsg_body:
                        if sys.version_info[0] < 3 or sys.version_info[0] >= 3 and sys.version_info[1] < 10:
                            raise RuntimeError("Python 3.10 or later is required for JSON support.")
                        for key, value in delete_clmsg_body.items():
                            where.append(f"clmsg_body->>'{key}' LIKE {'%s' if pg_enabled else '?'}")
                            params.append(value)
                    if delete_clmsg_tags:
                        for tag in delete_clmsg_tags:
                            where.append(f"clmsg_tag like {'%s' if pg_enabled else '?'}")
                            params.append(f'%{tag}%')
                    if delete_svmsg_id and delete_svmsg_id != 'None':
                        where.append(f'svmsg_id={"%s" if pg_enabled else "?"}')
                        params.append(delete_svmsg_id)
                    if delete_svmsg_sdate and delete_svmsg_sdate != 'None':
                        where.append(f'svmsg_date>={"%s" if pg_enabled else "?"}')
                        params.append(delete_svmsg_sdate)
                    if delete_svmsg_edate and delete_svmsg_edate != 'None':
                        where.append(f'svmsg_date<={"%s" if pg_enabled else "?"}')
                        params.append(delete_svmsg_edate)
                    sql += ' WHERE ' + ' AND '.join(where) if len(where)>0 else ''
                    cursor.execute(sql, tuple(params))
                    delete_count = cursor.rowcount
                    conn.commit()
                    if delete_count <= 0:
                        rescode, msg = (self.RESP_WARN, dict(warn="No data deleted."))
                        redis_cli.rpush(reskey, msg)
                        return rescode
                    else:
                        rescode, msg = (self.RESP_SCCESS, dict(success=dict(msg=f"{delete_count} records deleted.", count=delete_count)))
                        redis_cli.rpush(reskey, msg)
                        return rescode
                finally:
                    cursor.close()
        except Exception as e:
            logger.warning(f"Failed to delete: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to delete: {e}"))
            return self.RESP_WARN
