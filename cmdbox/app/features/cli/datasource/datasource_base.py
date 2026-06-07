from cmdbox.app import client as _cli_client, common, feature
from cmdbox.app.commons import convert as _convert
from pathlib import Path
from typing import Any, Dict, List, Tuple
import argparse
import json
import logging
import re


class _Sqlite3CursorCM:
    """sqlite3.Cursor をコンテキストマネージャーとして使えるようにするラッパー。"""
    def __init__(self, cursor):
        self._cursor = cursor

    def __enter__(self):
        return self._cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cursor.close()
        return False

    def __getattr__(self, name):
        return getattr(self._cursor, name)


class _Sqlite3ConnectionWrapper:
    """sqlite3.Connection の cursor() が CM をサポートするようにするラッパー。"""
    def __init__(self, conn):
        self._conn = conn

    def cursor(self):
        return _Sqlite3CursorCM(self._conn.cursor())

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._conn.close()
        return False

    def __getattr__(self, name):
        return getattr(self._conn, name)


class DatasourceBase(feature.ResultEdgeFeature):
    DBTYPE_PG = 'postgresql'
    DBTYPE_SQLITE = 'sqlite'
    DBTYPES = [DBTYPE_PG, DBTYPE_SQLITE]

    _IDENTIFIER_RE = re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*$')
    _COL_TYPE_RE = re.compile(r'^[A-Za-z][A-Za-z0-9_ ]*(?:\([0-9, ]+\))?$')

    def load_datasource(self, data_dir: Path, dsname: str) -> Dict[str, Any]:
        """
        データソース設定をファイルから読み込みます。
        Args:
            data_dir: データディレクトリのパス
            dsname: データソース名
        Returns:
            データソース設定の辞書
        Raises:
            FileNotFoundError: 指定されたデータソース設定ファイルが存在しない場合
            json.JSONDecodeError: データソース設定ファイルの内容が有効なJSONでない場合
        """
        ds_path = data_dir / ".datasource" / f"datasource-{dsname}.json"
        if not ds_path.exists():
            raise FileNotFoundError(
                f"Datasource configuration '{dsname}' not found at '{ds_path}'."
            )
        ret = common.load_file(ds_path, lambda f: json.load(f), encoding='utf-8', nolock=False)
        return ret

    def save_datasource(self, data_dir:Path, *, dsname:str, dbtype:str, scope:str='client', client_data:str=None,
                        db_host:str, db_port:int, db_user:str, db_password:str, db_name:str, db_timeout:int=None, db_path:str) -> None:
        """
        データソース設定をファイルに保存します。
        Args:
            data_dir: データディレクトリのパス
            dsname: データソース名
            dbtype: データベース種別（'postgresql' または 'sqlite'）
            scope: 参照スコープ（'client' または 'server'）
            client_data: ローカルを参照させる場合のデータフォルダのパス（scope='client' の場合に必要）
            db_host: データベースホスト（PostgreSQLの場合）
            db_port: データベースポート（PostgreSQLの場合）
            db_user: データベースユーザー（PostgreSQLの場合）
            db_password: データベースパスワード（PostgreSQLの場合）
            db_name: データベース名（PostgreSQLの場合）
            db_timeout: データベース接続のタイムアウト（秒）（PostgreSQLの場合）
            db_path: SQLiteのデータベースファイルパス（SQLiteの場合）
        Raises:
            ValueError: dbtype がサポートされていない場合
            IOError: データソース設定ファイルの書き込みに失敗した場合
        """
        if dbtype not in self.DBTYPES:
            raise ValueError(
                f"Unsupported dbtype: '{dbtype}'. Supported types: {self.DBTYPES}."
            )
        ds_path = data_dir / ".datasource" / f"datasource-{dsname}.json"
        ds_path.parent.mkdir(parents=True, exist_ok=True)

        current_path = db_path.replace("\\","/").replace("//","/") if db_path else None
        current_path = current_path[1:] if current_path and current_path.startswith('/') else current_path
        db_fullpath = str((data_dir / current_path).resolve()) if current_path else None
        dsconfig = dict(
            dsname=dsname,
            dbtype=dbtype,
            scope=scope,
            client_data=client_data,
            db_host=db_host,
            db_port=db_port,
            db_user=db_user,
            db_password=db_password,
            db_name=db_name,
            db_timeout=db_timeout,
            db_path=db_path,
            db_fullpath=db_fullpath,
        )
        common.save_file(ds_path, lambda f: json.dump(dsconfig, f, indent=4), encoding='utf-8', nolock=False)

    def get_connection(self, dsconfig: Dict[str, Any]):
        """
        データソース設定からデータベース接続を確立します。
        Args:
            dsconfig: データソース設定の辞書
        Returns:
            データベース接続オブジェクトとデータベース種別のタプル (connection, dbtype)
        Raises:
            ValueError: dsconfig の dbtype がサポートされていない場合
            psycopg.Error: PostgreSQL への接続に失敗した場合
            sqlite3.Error: SQLite への接続に失敗した場合
        """
        dbtype = dsconfig.get('dbtype', self.DBTYPE_SQLITE)
        if dbtype == self.DBTYPE_PG:
            import psycopg
            conn = psycopg.connect(
                host=dsconfig.get('db_host', 'localhost'),
                port=int(dsconfig.get('db_port', 5432)),
                user=dsconfig.get('db_user', 'postgres'),
                password=dsconfig.get('db_password', ''),
                dbname=dsconfig.get('db_name', ''),
                connect_timeout=dsconfig.get('db_timeout', None)
            )
            return conn, self.DBTYPE_PG
        elif dbtype == self.DBTYPE_SQLITE:
            import sqlite3
            import sqlite_vec
            db_path = dsconfig.get('db_fullpath')
            if not db_path:
                raise ValueError("db_path is required for SQLite dbtype.")
            conn = sqlite3.connect(db_path)
            conn.enable_load_extension(True)
            sqlite_vec.load(conn)
            conn.enable_load_extension(False)
            return _Sqlite3ConnectionWrapper(conn), self.DBTYPE_SQLITE
        else:
            raise ValueError(
                f"Unsupported dbtype: '{dbtype}'. Supported types: {self.DBTYPES}."
            )

    def is_dbtype_postgresql(self, dsconfig: Dict[str, Any]) -> bool:
        """
        dsconfig の dbtype が PostgreSQL かどうかを判定します。
         - dsconfig に dbtype がない場合は SQLite とみなします。

        Args:
            dsconfig: データソース設定の辞書
            dbtype: 判定したいデータベース種別（'postgresql' または 'sqlite'）
        Returns:
            bool: dsconfig の dbtype が PostgreSQL の場合 True
        Raises:
            ValueError: dbtype がサポートされていない場合
        """
        return dsconfig.get('dbtype', self.DBTYPE_SQLITE) == self.DBTYPE_PG
    
    def is_dbtype_sqlite(self, dsconfig: Dict[str, Any]) -> bool:
        """
        dsconfig の dbtype が SQLite かどうかを判定します。
         - dsconfig に dbtype がない場合は SQLite とみなします。
        Args:
            dsconfig: データソース設定の辞書
            dbtype: 判定したいデータベース種別（'postgresql' または 'sqlite'）
        Returns:
            bool: dsconfig の dbtype が SQLite の場合 True
        """
        return dsconfig.get('dbtype', self.DBTYPE_SQLITE) == self.DBTYPE_SQLITE

    def validate_identifier(self, name: str) -> str:
        """
        SQLの識別子（テーブル名、カラム名、スキーマ名など）として有効かどうかを検査します。
        有効な識別子は、英字またはアンダースコアで始まり、その後に英数字またはアンダースコアが続く文字列です。
        Args:
            name: 検査する識別子の文字列
        Returns:
            name: 入力された識別子が有効な場合はそのまま返します。
        Raises:
            ValueError: name が有効なSQL識別子でない場合に発生します。
        """
        if not self._IDENTIFIER_RE.match(name):
            raise ValueError(
                f"Invalid SQL identifier: '{name}'. "
                "Only letters, digits, and underscores are allowed, starting with a letter or underscore."
            )
        return name

    def validate_col_type(self, col_type: str) -> str:
        """
        カラムのデータ型として有効かどうかを検査します。
        Args:
            col_type: 検査するカラムのデータ型の文字列
        Returns:
            col_type: 入力されたカラムのデータ型が有効な場合はそのまま返します。
        Raises:
            ValueError: col_type が有効なカラムのデータ型でない場合に発生します。
        """
        t = col_type.strip()
        if not self._COL_TYPE_RE.match(t):
            raise ValueError(f"Invalid column type: '{col_type}'.")
        return t

    def validate_columns(self, columns_str: str) -> str:
        """
        カラムリストの文字列を検査し、SQLクエリで使用できる形式に変換します。
        Args:
            columns_str: カラムリストの文字列。カラム名をカンマ区切りで指定します。空文字列や '*' の場合は全カラムを意味します。
        Returns:
            str: SQLクエリで使用できるカラムリストの文字列。
        Raises:
            ValueError: columns_str に無効なカラム名が含まれている場合
        """
        if not columns_str or columns_str.strip() in ('', '*'):
            return '*'
        cols = [c.strip() for c in columns_str.split(',')]
        return ', '.join(self.validate_identifier(c) for c in cols if c)

    def validate_order_by(self, order_by_str: str) -> str:
        """
        ORDER BY句の文字列を検査し、SQLクエリで使用できる形式に変換します。
        Args:
            order_by_str: ORDER BY句の文字列。カラム名とオプションのASC/DESCをカンマ区切りで指定します。例: "name ASC, age DESC"
        Returns:
            str: SQLクエリで使用できるORDER BY句の文字列。空文字列の場合は空文字列を返します。
        Raises:
            ValueError: order_by_str に無効な形式が含まれている場合
        """
        if not order_by_str or not order_by_str.strip():
            return ''
        items = []
        for item in order_by_str.split(','):
            parts = item.strip().split()
            if len(parts) == 1:
                items.append(self.validate_identifier(parts[0]))
            elif len(parts) == 2 and parts[1].upper() in ('ASC', 'DESC'):
                items.append(f"{self.validate_identifier(parts[0])} {parts[1].upper()}")
            else:
                raise ValueError(
                    f"Invalid ORDER BY item: '{item}'. "
                    "Expected '<column>' or '<column> ASC|DESC'."
                )
        return ', '.join(items)

    def build_where(
        self, where_data: Dict[str, Any], dbtype: str
    ) -> Tuple[str, list]:
        """
        WHERE句の文字列を構築します。
        Args:
            where_data: WHERE句に使用する条件の辞書。キーがカラム名、値が条件値です。
            dbtype: データベースの種類（'postgresql' または 'sqlite'）
        Returns:
            Tuple[str, list]: WHERE句の文字列と対応する値のリスト
        """
        if not where_data:
            return '', []
        placeholder = '%s' if dbtype == self.DBTYPE_PG else '?'
        parts = [
            f"{self.validate_identifier(k)} = {placeholder}"
            for k in where_data
        ]
        return 'WHERE ' + ' AND '.join(parts), list(where_data.values())

    def fetch_as_dicts(self, cursor) -> List[Dict[str, Any]]:
        """
        カーソルから取得した結果を辞書のリストとして返します。
        Args:
            cursor: データベースカーソル
        Returns:
            List[Dict[str, Any]]: カーソルから取得した結果のリスト。各行は辞書として表されます。
        """
        if cursor.description is None:
            return []
        cols = [d[0] for d in cursor.description]
        return [dict(zip(cols, row)) for row in cursor.fetchall()]

    def qualified_name(self, schema: str, name: str, dbtype: str = None) -> str:
        """
        スキーマ名とオブジェクト名を結合して完全修飾名を作成します。
        SQLiteの場合はスキーマをサポートしないため、nameをそのまま返します。
        Args:
            schema: スキーマ名
            name: オブジェクト名
            dbtype: データベース種別。DBTYPE_SQLITE の場合はスキーマを無視します。
        Returns:
            str: 完全修飾名
        """
        if schema and dbtype != self.DBTYPE_SQLITE:
            return f"{self.validate_identifier(schema)}.{name}"
        return name

    def route_apprun(self, args: argparse.Namespace, payload: Dict[str, Any],
                     logger: logging.Logger, tm: float, pf: List[Dict[str, float]]) -> Tuple[int, Dict[str, Any], Any]:
        """
        データソース設定の scope に基づいて apprun 処理をルーティングします。
        client_data から dsconfig を読み込み、scope=='server' なら Redis 経由で svrun を呼び出し、
        それ以外ならローカルで _do_run を実行します。
        """
        from cmdbox.app.features.cli import cmdbox_datasource_load
        ds_load = cmdbox_datasource_load.DatasourceLoad(self.appcls, self.ver, self.language)
        st, _ds_conf, _ = ds_load.apprun(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, _ds_conf, None
        dsconfig = _ds_conf.get('success', {}).get('data', {})
        payload = {**dsconfig, **payload}
        scope = dsconfig.get('scope', 'client')
        if scope == 'server':
            payload_b64 = _convert.str2b64str(common.to_str(payload))
            cl = _cli_client.Client(logger, redis_host=args.host, redis_port=args.port,
                                    redis_password=args.password, svname=args.svname)
            ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                        retry_count=args.retry_count, retry_interval=args.retry_interval,
                                        timeout=args.timeout, nowait=False)
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            if 'success' not in ret:
                return self.RESP_WARN, ret, cl
            return self.RESP_SUCCESS, ret, cl
        elif scope == 'client':
            if payload.get('client_data') is None:
                result = dict(warn="client_data is required for client scope.")
                logger.warning("client_data is required for client scope.")
                return self.RESP_WARN, result, None
            ret = self._do_run(Path(payload['client_data']), payload, logger)
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            if 'success' not in ret:
                return self.RESP_WARN, ret, None
            return self.RESP_SUCCESS, ret, None
        else:
            result = dict(warn=f"Unsupported scope: '{scope}'.")
            logger.warning(f"Unsupported scope: '{scope}'.")
            return self.RESP_WARN, result, None

    def _do_run(self, data_dir: Path, payload: Dict[str, Any], logger: logging.Logger) -> Dict[str, Any]:
        raise NotImplementedError("Subclasses must implement _do_run method.")
