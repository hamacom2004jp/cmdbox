from cmdbox.app import common, client
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.features.cli import audit_base
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import sys


class AuditSearch(audit_base.AuditBase):
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
        return 'search'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['discription_ja'] = "監査ログを検索します。"
        opt['discription_en'] = "Search the audit log."
        opt['choice'] += [
            dict(opt="select", type=Options.T_STR, default=None, required=False, multi=True, hide=False,
                 choice=['', 'audit_type', 'clmsg_id', 'clmsg_date', 'clmsg_tag', 'clmsg_src', 'clmsg_body', 'svmsg_id', 'svmsg_date'],
                 discription_ja="取得項目を指定します。指定しない場合は全ての項目を取得します。",
                 discription_en="Specify the items to be retrieved. If not specified, all items are acquired."),
            dict(opt="filter_audit_type", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=Options.AUDITS,
                 discription_ja="フィルタ条件の監査の種類を指定します。",
                 discription_en="Specifies the type of audit for the filter condition."),
            dict(opt="filter_clmsg_id", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="フィルタ条件のクライアントのメッセージIDを指定します。",
                 discription_en="Specify the message ID of the client for the filter condition."),
            dict(opt="filter_clmsg_sdate", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="フィルタ条件のクライアントのメッセージ発生日時(開始)を指定します。",
                 discription_en="Specify the date and time (start) when the message occurred for the client in the filter condition."),
            dict(opt="filter_clmsg_edate", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="フィルタ条件のクライアントのメッセージ発生日時(終了)を指定します。",
                 discription_en="Specify the date and time (end) when the message occurred for the client in the filter condition."),
            dict(opt="filter_clmsg_src", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="フィルタ条件のクライアントのメッセージの発生源を指定します。LIKE検索を行います。",
                 discription_en="Specifies the source of the message for the client in the filter condition; performs a LIKE search."),
            dict(opt="filter_clmsg_user", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="フィルタ条件のクライアントのメッセージの発生させたユーザーを指定します。LIKE検索を行います。",
                 discription_en="Specifies the user who generated the message for the client in the filter condition; performs a LIKE search."),
            dict(opt="filter_clmsg_body", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                 discription_ja="フィルタ条件のクライアントのメッセージの本文を辞書形式で指定します。LIKE検索を行います。",
                 discription_en="Specifies the body of the client's message in the filter condition in dictionary format; performs a LIKE search."),
            dict(opt="filter_clmsg_tag", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                 discription_ja="フィルタ条件のクライアントのメッセージのタグを指定します。",
                 discription_en="Specifies the tag of the client's message in the filter condition."),
            dict(opt="filter_svmsg_id", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="フィルタ条件のサーバーのメッセージIDを指定します。",
                 discription_en="Specify the message ID of the server for the filter condition."),
            dict(opt="filter_svmsg_sdate", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="フィルタ条件のサーバーのメッセージ発生日時(開始)を指定します。",
                 discription_en="Specify the date and time (start) when the message occurred for the server in the filter condition."),
            dict(opt="filter_svmsg_edate", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="フィルタ条件のサーバーのメッセージ発生日時(終了)を指定します。",
                 discription_en="Specify the date and time (end) when the message occurred for the server in the filter condition."),
            dict(opt="sort", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=['', 'ASC', 'DICT'],
                 discription_ja="ソート項目を指定します。",
                 discription_en="Specify the sort item."),
            dict(opt="offset", type=Options.T_INT, default=0, required=False, multi=False, hide=False, choice=None,
                 discription_ja="取得する行の開始位置を指定します。",
                 discription_en="Specifies the starting position of the row to be retrieved."),
            dict(opt="limit", type=Options.T_INT, default=100, required=False, multi=False, hide=False, choice=None,
                 discription_ja="取得する行数を指定します。",
                 discription_en="Specifies the number of rows to retrieve."),
        ]
        return opt

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'audit_search'

    @Options.audit(audit_type=Options.AT_EVENT)
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

        select_str = json.dumps(args.select, default=common.default_json_enc, ensure_ascii=False) if args.select else '[]'
        select_b64 = convert.str2b64str(select_str)
        sort_str = json.dumps(args.sort, default=common.default_json_enc, ensure_ascii=False) if args.sort else '{}'
        sort_b64 = convert.str2b64str(sort_str)
        offset = args.offset
        limit = args.limit
        filter_audit_type_b64 = convert.str2b64str(args.filter_audit_type)
        filter_clmsg_id_b64 = convert.str2b64str(args.filter_clmsg_id)
        filter_clmsg_sdate_b64 = convert.str2b64str(args.filter_clmsg_sdate)
        filter_clmsg_edate_b64 = convert.str2b64str(args.filter_clmsg_edate)
        filter_clmsg_src_b64 = convert.str2b64str(args.filter_clmsg_src)
        filter_clmsg_user_b64 = convert.str2b64str(args.filter_clmsg_user)
        filter_clmsg_body_str = json.dumps(args.filter_clmsg_body, default=common.default_json_enc, ensure_ascii=False) if args.filter_clmsg_body else '{}'
        filter_clmsg_body_b64 = convert.str2b64str(filter_clmsg_body_str)
        filter_clmsg_tag_str = json.dumps(args.filter_clmsg_tag, default=common.default_json_enc, ensure_ascii=False) if args.filter_clmsg_tag else '[]'
        filter_clmsg_tag_b64 = convert.str2b64str(filter_clmsg_tag_str)
        filter_svmsg_id_b64 = convert.str2b64str(args.filter_svmsg_id)
        filter_svmsg_sdate_b64 = convert.str2b64str(args.filter_svmsg_sdate)
        filter_svmsg_edate_b64 = convert.str2b64str(args.filter_svmsg_edate)

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd('audit_search', [select_b64, sort_b64, str(offset), str(limit),
                                                     filter_audit_type_b64, filter_clmsg_id_b64, filter_clmsg_sdate_b64, filter_clmsg_edate_b64,
                                                     filter_clmsg_src_b64, filter_clmsg_user_b64, filter_clmsg_body_b64, filter_clmsg_tag_b64, 
                                                     filter_svmsg_id_b64, filter_svmsg_sdate_b64, filter_svmsg_edate_b64],
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
        select = json.loads(convert.b64str2str(msg[2]))
        sort = json.loads(convert.b64str2str(msg[3]))
        offset = int(msg[4]) if msg[4] else 0
        limit = int(msg[5]) if msg[5] else 100
        
        filter_audit_type = convert.b64str2str(msg[6])
        filter_clmsg_id = convert.b64str2str(msg[7])
        filter_clmsg_sdate = convert.b64str2str(msg[8])
        filter_clmsg_edate = convert.b64str2str(msg[9])
        filter_clmsg_src = convert.b64str2str(msg[10])
        filter_clmsg_user = convert.b64str2str(msg[11])
        body = json.loads(convert.b64str2str(msg[12]))
        tags = json.loads(convert.b64str2str(msg[13]))
        filter_svmsg_id = convert.b64str2str(msg[14])
        filter_svmsg_sdate = convert.b64str2str(msg[15])
        filter_svmsg_edate = convert.b64str2str(msg[16])
        st = self.search(msg[1], select, sort, offset, limit,
                         filter_audit_type, filter_clmsg_id, filter_clmsg_sdate, filter_clmsg_edate,
                         filter_clmsg_src, filter_clmsg_user, body, tags,
                         filter_svmsg_id, filter_svmsg_sdate, filter_svmsg_edate,
                         data_dir, logger, redis_cli)
        return st

    def search(self, reskey:str, select:List[str], sort:Dict[str, str], offset:int, limit:int,
               filter_audit_type:str, filter_clmsg_id:str, filter_clmsg_sdate:str, filter_clmsg_edate:str,
               filter_clmsg_src:str, filter_clmsg_user:str, filter_clmsg_body:Dict[str, Any], filter_clmsg_tags:List[str],
               filter_svmsg_id:str, filter_svmsg_sdate:str, filter_svmsg_edate:str,
               data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient) -> int:
        """
        監査ログを検索する

        Args:
            reskey (str): レスポンスキー
            select (List[str]): 取得項目
            sort (Dict[str, str]): ソート条件
            offset (int): 取得する行の開始位置
            limit (int): 取得する行数
            filter_audit_type (str): 監査の種類
            filter_clmsg_id (str): クライアントメッセージID
            filter_clmsg_sdate (str): クライアントメッセージ発生日時(開始)
            filter_clmsg_edate (str): クライアントメッセージ発生日時(終了)
            filter_clmsg_src (str): クライアントメッセージの発生源
            filter_clmsg_user (str): クライアントメッセージの発生させたユーザー
            filter_clmsg_body (Dict[str, Any]): クライアントメッセージの本文
            filter_clmsg_tags (List[str]): クライアントメッセージのタグ
            filter_svmsg_id (str): サーバーメッセージID
            filter_svmsg_sdate (str): サーバーメッセージ発生日時(開始)
            filter_svmsg_edate (str): サーバーメッセージ発生日時(終了)
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント

        Returns:
            int: レスポンスコード
        """
        try:
            with self.initdb(data_dir, logger) as conn:
                def dict_factory(cursor, row):
                    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
                conn.row_factory = dict_factory
                cursor = conn.cursor()
                try:
                    sql = f'SELECT {",".join(select) if select is not None and len(select)>0 else "*"} FROM audit WHERE 1=1'
                    params = []
                    if filter_audit_type and filter_audit_type != 'None':
                        sql += ' AND audit_type=?'
                        params.append(filter_audit_type)
                    if filter_clmsg_id and filter_clmsg_id != 'None':
                        sql += ' AND clmsg_id=?'
                        params.append(filter_clmsg_id)
                    if filter_clmsg_sdate and filter_clmsg_sdate != 'None':
                        sql += ' AND clmsg_date>=?'
                        params.append(filter_clmsg_sdate)
                    if filter_clmsg_edate and filter_clmsg_edate != 'None':
                        sql += ' AND clmsg_date<=?'
                        params.append(filter_clmsg_edate)
                    if filter_clmsg_src and filter_clmsg_src != 'None':
                        sql += ' AND clmsg_src LIKE ?'
                        params.append(filter_clmsg_src)
                    if filter_clmsg_user and filter_clmsg_user != 'None':
                        sql += ' AND clmsg_user LIKE ?'
                        params.append(filter_clmsg_user)
                    if filter_clmsg_body:
                        if sys.version_info[0] < 3 or sys.version_info[0] >= 3 and sys.version_info[1] < 10:
                            raise RuntimeError("Python 3.10 or later is required for JSON support.")
                        for key, value in filter_clmsg_body.items():
                            sql += f" AND clmsg_body->>'{key}' LIKE ?"
                            params.append(value)
                    if filter_clmsg_tags:
                        for tag in filter_clmsg_tags:
                            sql += f" AND clmsg_tag like ?"
                            params.append(f'%{tag}%')
                    if filter_svmsg_id and filter_svmsg_id != 'None':
                        sql += ' AND svmsg_id=?'
                        params.append(filter_svmsg_id)
                    if filter_svmsg_sdate and filter_svmsg_sdate != 'None':
                        sql += ' AND svmsg_date>=?'
                        params.append(filter_svmsg_sdate)
                    if filter_svmsg_edate and filter_svmsg_edate != 'None':
                        sql += ' AND svmsg_date<=?'
                        params.append(filter_svmsg_edate)
                    if sort and len(sort) > 0:
                        sql += ' ORDER BY ' + ', '.join([f"{k} {v}" for k, v in sort.items()])
                    else:
                        sql += ' ORDER BY svmsg_date DESC'
                    if offset > 0:
                        sql += ' OFFSET ?'
                        params.append(offset)
                    if limit > 0:
                        sql += ' LIMIT ?'
                        params.append(limit)
                    cursor.execute(sql, params)
                    rows = cursor.fetchall()
                    if not rows:
                        rescode, msg = (self.RESP_WARN, dict(warn="No data found"))
                        redis_cli.rpush(reskey, msg)
                        return rescode
                    else:
                        rescode, msg = (self.RESP_SCCESS, dict(success=rows))
                        redis_cli.rpush(reskey, msg)
                        return rescode
                finally:
                    cursor.close()
        except Exception as e:
            logger.warning(f"Failed to write: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to write: {e}"))
            return self.RESP_WARN
