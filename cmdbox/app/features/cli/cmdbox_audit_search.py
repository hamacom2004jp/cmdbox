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
                 choice=['', 'audit_type', 'clmsg_id', 'clmsg_date', 'clmsg_src', 'clmsg_title', 'clmsg_user', 'clmsg_body', 'clmsg_tag', 'svmsg_id', 'svmsg_date'],
                 discription_ja="取得項目を指定します。指定しない場合は全ての項目を取得します。",
                 discription_en="Specify the items to be retrieved. If not specified, all items are acquired."),
            dict(opt="filter_audit_type", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=['']+Options.AUDITS,
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
            dict(opt="filter_clmsg_title", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                 discription_ja="フィルタ条件のクライアントのメッセージタイトルを指定します。LIKE検索を行います。",
                 discription_en="Specifies the message title of the client for the filter condition; a LIKE search is performed."),
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
            dict(opt="sort", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=['', 'ASC', 'DESC'],
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

        select_str = json.dumps(args.select, default=common.default_json_enc, ensure_ascii=False) if getattr(args, 'select', None) else '[]'
        select_b64 = convert.str2b64str(select_str)
        args.sort = args.sort if getattr(args, 'sort', {}) else {}
        args.sort = args.sort if isinstance(args.sort, dict) else {str(args.sort): 'DESC'}
        sort_str = json.dumps(args.sort, default=common.default_json_enc, ensure_ascii=False)
        sort_b64 = convert.str2b64str(sort_str)
        offset = getattr(args, 'offset', None)
        limit = getattr(args, 'limit', None)
        filter_audit_type_b64 = convert.str2b64str(getattr(args, 'filter_audit_type', None))
        filter_clmsg_id_b64 = convert.str2b64str(getattr(args, 'filter_clmsg_id', None))
        filter_clmsg_sdate = args.filter_clmsg_sdate+common.get_tzoffset_str() if getattr(args, 'filter_clmsg_sdate', None) else None
        filter_clmsg_sdate_b64 = convert.str2b64str(filter_clmsg_sdate)
        filter_clmsg_edate = args.filter_clmsg_edate+common.get_tzoffset_str() if getattr(args, 'filter_clmsg_edate', None) else None
        filter_clmsg_edate_b64 = convert.str2b64str(filter_clmsg_edate)
        filter_clmsg_src_b64 = convert.str2b64str(getattr(args, 'filter_clmsg_src', None))
        filter_clmsg_title_b64 = convert.str2b64str(getattr(args, 'filter_clmsg_title', None))
        filter_clmsg_user_b64 = convert.str2b64str(getattr(args, 'filter_clmsg_user', None))
        filter_clmsg_body_str = json.dumps(args.filter_clmsg_body, default=common.default_json_enc, ensure_ascii=False) if getattr(args, 'filter_clmsg_body', None) else '{}'
        filter_clmsg_body_b64 = convert.str2b64str(filter_clmsg_body_str)
        filter_clmsg_tag_str = json.dumps(args.filter_clmsg_tag, default=common.default_json_enc, ensure_ascii=False) if getattr(args, 'filter_clmsg_tag', None) else '[]'
        filter_clmsg_tag_b64 = convert.str2b64str(filter_clmsg_tag_str)
        filter_svmsg_id_b64 = convert.str2b64str(getattr(args, 'filter_svmsg_id', None))
        filter_svmsg_sdate_b64 = convert.str2b64str(getattr(args, 'filter_svmsg_sdate', None))
        filter_svmsg_edate_b64 = convert.str2b64str(getattr(args, 'filter_svmsg_edate', None))
        pg_enabled = args.pg_enabled if getattr(args, 'pg_enabled', False) and isinstance(args.pg_enabled, bool) else False
        pg_host_b64 = convert.str2b64str(getattr(args, 'pg_host', None))
        pg_port = args.pg_port if getattr(args, 'pg_port', 5432) and isinstance(args.pg_port, int) else None
        pg_user_b64 = convert.str2b64str(getattr(args, 'pg_user', None))
        pg_password_b64 = convert.str2b64str(getattr(args, 'pg_password', None))
        pg_dbname_b64 = convert.str2b64str(getattr(args, 'pg_dbname', None))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                    [select_b64, sort_b64, str(offset), str(limit),
                                     filter_audit_type_b64, filter_clmsg_id_b64, filter_clmsg_sdate_b64, filter_clmsg_edate_b64,
                                     filter_clmsg_src_b64, filter_clmsg_title_b64, filter_clmsg_user_b64, filter_clmsg_body_b64,
                                     filter_clmsg_tag_b64, filter_svmsg_id_b64, filter_svmsg_sdate_b64, filter_svmsg_edate_b64,
                                     pg_enabled, pg_host_b64, pg_port, pg_user_b64, pg_password_b64, pg_dbname_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
        common.print_format(ret, getattr(args, 'format', False), tm, None, False, pf=pf)

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
        filter_clmsg_title = convert.b64str2str(msg[11])
        filter_clmsg_user = convert.b64str2str(msg[12])
        body = json.loads(convert.b64str2str(msg[13]))
        tags = json.loads(convert.b64str2str(msg[14]))
        filter_svmsg_id = convert.b64str2str(msg[15])
        filter_svmsg_sdate = convert.b64str2str(msg[16])
        filter_svmsg_edate = convert.b64str2str(msg[17])
        pg_enabled = True if msg[18]=='True' else False
        pg_host = convert.b64str2str(msg[19])
        pg_port = int(msg[20]) if msg[20]!='None' else None
        pg_user = convert.b64str2str(msg[21])
        pg_password = convert.b64str2str(msg[22])
        pg_dbname = convert.b64str2str(msg[23])
        st = self.search(msg[1], select, sort, offset, limit,
                         filter_audit_type, filter_clmsg_id, filter_clmsg_sdate, filter_clmsg_edate,
                         filter_clmsg_src, filter_clmsg_title, filter_clmsg_user, body, tags,
                         filter_svmsg_id, filter_svmsg_sdate, filter_svmsg_edate,
                         pg_enabled, pg_host, pg_port, pg_user, pg_password, pg_dbname,
                         data_dir, logger, redis_cli)
        return st

    def search(self, reskey:str, select:List[str], sort:Dict[str, str], offset:int, limit:int,
               filter_audit_type:str, filter_clmsg_id:str, filter_clmsg_sdate:str, filter_clmsg_edate:str,
               filter_clmsg_src:str, filter_clmsg_title:str, filter_clmsg_user:str, filter_clmsg_body:Dict[str, Any],
               filter_clmsg_tags:List[str], filter_svmsg_id:str, filter_svmsg_sdate:str, filter_svmsg_edate:str,
               pg_enabled:bool, pg_host:str, pg_port:int, pg_user:str, pg_password:str, pg_dbname:str,
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
            filter_clmsg_title (str): クライアントメッセージのタイトル
            filter_clmsg_user (str): クライアントメッセージの発生させたユーザー
            filter_clmsg_body (Dict[str, Any]): クライアントメッセージの本文
            filter_clmsg_tags (List[str]): クライアントメッセージのタグ
            filter_svmsg_id (str): サーバーメッセージID
            filter_svmsg_sdate (str): サーバーメッセージ発生日時(開始)
            filter_svmsg_edate (str): サーバーメッセージ発生日時(終了)
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
                def dict_factory(cursor, row):
                    return {col[0]: row[idx] for idx, col in enumerate(cursor.description)}
                conn.row_factory = dict_row if pg_enabled else dict_factory
                cursor = conn.cursor()
                try:
                    select = [a for a in select if a != ''] if select else None
                    select = select if select and len(select)>0 else ['audit_type', 'clmsg_id', 'clmsg_date', 'clmsg_src', 'clmsg_title',
                                                                      'clmsg_user', 'clmsg_body', 'clmsg_tag', 'svmsg_id', 'svmsg_date']
                    if pg_enabled:
                        toz = common.get_tzoffset_str()
                        sel = []
                        for s in select:
                            if s in ['clmsg_date', 'svmsg_date']:
                                sel.append(f"{s} AT TIME ZONE INTERVAL '{toz}' as {s}")
                            else:
                                sel.append(s)
                        select = sel
                    sql = f'SELECT {",".join(select)} FROM audit'
                    params = []
                    where = []
                    if filter_audit_type and filter_audit_type != 'None':
                        where.append(f'audit_type={"%s" if pg_enabled else "?"}')
                        params.append(filter_audit_type)
                    if filter_clmsg_id and filter_clmsg_id != 'None':
                        where.append(f'clmsg_id={"%s" if pg_enabled else "?"}')
                        params.append(filter_clmsg_id)
                    if filter_clmsg_sdate and filter_clmsg_sdate != 'None':
                        where.append(f'clmsg_date>={"%s" if pg_enabled else "?"}')
                        params.append(filter_clmsg_sdate)
                    if filter_clmsg_edate and filter_clmsg_edate != 'None':
                        where.append(f'clmsg_date<={"%s" if pg_enabled else "?"}')
                        params.append(filter_clmsg_edate)
                    if filter_clmsg_src and filter_clmsg_src != 'None':
                        where.append(f'clmsg_src LIKE {"%s" if pg_enabled else "?"}')
                        params.append(filter_clmsg_src)
                    if filter_clmsg_title and filter_clmsg_title != 'None':
                        where.append(f'clmsg_title LIKE {"%s" if pg_enabled else "?"}')
                        params.append(filter_clmsg_title)
                    if filter_clmsg_user and filter_clmsg_user != 'None':
                        where.append(f'clmsg_user LIKE {"%s" if pg_enabled else "?"}')
                        params.append(filter_clmsg_user)
                    if filter_clmsg_body:
                        if sys.version_info[0] < 3 or sys.version_info[0] >= 3 and sys.version_info[1] < 10:
                            raise RuntimeError("Python 3.10 or later is required for JSON support.")
                        for key, value in filter_clmsg_body.items():
                            where.append(f"clmsg_body->>'{key}' LIKE {'%s' if pg_enabled else '?'}")
                            params.append(value)
                    if filter_clmsg_tags:
                        for tag in filter_clmsg_tags:
                            where.append(f"clmsg_tag like {'%s' if pg_enabled else '?'}")
                            params.append(f'%{tag}%')
                    if filter_svmsg_id and filter_svmsg_id != 'None':
                        where.append(f'svmsg_id={"%s" if pg_enabled else "?"}')
                        params.append(filter_svmsg_id)
                    if filter_svmsg_sdate and filter_svmsg_sdate != 'None':
                        where.append(f'svmsg_date>={"%s" if pg_enabled else "?"}')
                        params.append(filter_svmsg_sdate)
                    if filter_svmsg_edate and filter_svmsg_edate != 'None':
                        where.append(f'svmsg_date<={"%s" if pg_enabled else "?"}')
                        params.append(filter_svmsg_edate)
                    sql += ' WHERE ' + ' AND '.join(where) if len(where)>0 else ''
                    if sort and len(sort) > 0:
                        sql += ' ORDER BY ' + ', '.join([f"{k} {v}" for k, v in sort.items()])
                    else:
                        sql += ' ORDER BY svmsg_date DESC'
                    if offset > 0:
                        sql += f' OFFSET {"%s" if pg_enabled else "?"}'
                        params.append(offset)
                    if limit > 0:
                        sql += f' LIMIT {"%s" if pg_enabled else "?"}'
                        params.append(limit)
                    cursor.execute(sql, tuple(params))
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
