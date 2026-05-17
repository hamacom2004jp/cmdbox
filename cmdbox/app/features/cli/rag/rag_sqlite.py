from cmdbox.app import common
from cmdbox.app.features.cli.rag import rag_store
from typing import Dict, Any, Generator, List
import json
import logging
import sqlite3
import math


def _l2_distance(v1: list, v2: list) -> float:
    """L2距離を計算します"""
    return math.sqrt(sum((a - b) ** 2 for a, b in zip(v1, v2)))


class RagSqlite(rag_store.RagStore):
    def __init__(self, dbpath:str, dbtimeout:int, logger:logging.Logger):
        """
        コンストラクタ

        Args:
            dbpath (str): データベースファイルパス
            dbtimeout (int): データベース接続のタイムアウト
            logger (logging.Logger): ロガー
        """
        if logger is None:
            raise ValueError("logger is required.")
        if dbpath is None:
            raise ValueError("dbpath is required.")
        if dbtimeout is None:
            raise ValueError("dbtimeout is required.")
        self.logger = logger
        self.dbpath = dbpath
        self.dbtimeout = dbtimeout

    def install(self) -> None:
        """
        SQLiteは特別なインストールは不要です
        """
        self.logger.info("SQLite does not require special installation.")

    def create_tables(self, servicename:str, embed_vector_dim:int=256) -> None:
        """
        テーブルを作成します

        Args:
            servicename (str): サービス名
            embed_vector_dim (int): 埋め込みベクトルの次元数（SQLiteでは参照のみ）
        """
        if servicename is None: raise ValueError("servicename is required.")

        with self.connect() as conn:
            table_name = f"{servicename}_embedding"
            conn.execute(
                f"CREATE TABLE IF NOT EXISTS {table_name} ("
                "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                "vec_id TEXT NOT NULL, "
                "content_text TEXT, "
                "content_type TEXT, "
                "content_blob BLOB, "
                "content_size INTEGER, "
                "origin_name TEXT, "
                "origin_type TEXT, "
                "origin_url TEXT, "
                "metadata TEXT, "
                "vec_model TEXT NOT NULL, "
                "vec_data TEXT NOT NULL, "
                "update_dt DATETIME DEFAULT CURRENT_TIMESTAMP, "
                "created_dt DATETIME DEFAULT CURRENT_TIMESTAMP"
                ")"
            )
            conn.execute(
                f"CREATE UNIQUE INDEX IF NOT EXISTS {table_name}_vec_id_idx ON {table_name} (vec_id)"
            )
            conn.commit()

    def insert_doc(self, *, connection:Any=None, servicename:str=None,
                   vec_id:str=None, content_text:str=None, content_type:str=None, content_blob:bytes=None,
                   origin_name:str=None, origin_type:str=None, origin_url:str=None,
                   metadata:Dict[str, Any]=None, vec_model:str=None, vec_data:Any=None
                   ) -> None:
        """
        ドキュメントを挿入します

        Args:
            connection: データベース接続オブジェクト
            servicename (str): サービス名
            vec_id (str): ベクトルID
            content_text (str): ドキュメントの内容
            content_type (str): ドキュメントのタイプ
            content_blob (bytes): ドキュメントのバイナリデータ
            origin_name (str): ドキュメントの元の名前
            origin_type (str): ドキュメントの元のタイプ
            origin_url (str): ドキュメントの元のURL
            metadata (dict): ドキュメントのメタデータ
            vec_model (str): ベクトルモデルの名前
            vec_data (Any): ベクトルデータ
        """
        if connection is None: raise ValueError("connection is required.")
        if servicename is None: raise ValueError("servicename is required.")
        vec_id = vec_id if vec_id is not None else common.gen_uuid()
        if content_text is None: raise ValueError("content_text is required.")
        content_type = content_type if content_type is not None else (metadata.get('content_type', 'text') if metadata else 'text')
        content_blob = content_blob if content_blob is not None else b''
        content_size = len(content_blob) if content_blob else 0
        origin_name = origin_name if origin_name is not None else (metadata.get('origin_name', 'unknown') if metadata else 'unknown')
        origin_type = origin_type if origin_type is not None else (metadata.get('origin_type', 'unknown') if metadata else 'unknown')
        origin_url = origin_url if origin_url is not None else (metadata.get('origin_url', 'unknown') if metadata else 'unknown')
        if metadata is None: raise ValueError("metadata is required.")
        vec_model = vec_model if vec_model is not None else metadata.get('vec_model', 'unknown')
        if vec_data is None: raise ValueError("vec_data is required.")

        table_name = f"{servicename}_embedding"
        connection.execute(
            f"INSERT INTO {table_name} ("
            "vec_id, content_text, content_type, content_blob, content_size, "
            "origin_name, origin_type, origin_url, metadata, vec_model, vec_data"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                vec_id,
                content_text,
                content_type,
                content_blob,
                content_size,
                origin_name,
                origin_type,
                origin_url,
                common.to_str(metadata),
                vec_model,
                common.to_str(vec_data),
            )
        )

    def delete_doc(self, *, connection:Any=None, servicename:str=None,
                   vec_id:str=None, content_text:str=None, content_type:str=None,
                   origin_name:str=None, origin_type:str=None, origin_url:str=None,
                   metadata:Dict[str, Any]=None, vec_model:str=None) -> None:
        """
        ドキュメントを削除します

        Args:
            connection: データベース接続オブジェクト
            servicename (str): サービス名
            vec_id (str): ベクトルID
            content_text (str): ドキュメントの内容
            content_type (str): ドキュメントのタイプ
            origin_name (str): ドキュメントの元の名前
            origin_type (str): ドキュメントの元のタイプ
            origin_url (str): ドキュメントの元のURL
            metadata (dict): ドキュメントのメタデータ
            vec_model (str): ベクトルモデルの名前
        """
        if connection is None: raise ValueError("connection is required.")
        if servicename is None: raise ValueError("servicename is required.")

        table_name = f"{servicename}_embedding"
        where_clauses = []
        params = []

        if vec_id is not None:
            where_clauses.append("vec_id = ?")
            params.append(vec_id)
        if content_text is not None:
            where_clauses.append("content_text LIKE ?")
            params.append(f'%{content_text}%')
        if content_type is not None:
            where_clauses.append("content_type = ?")
            params.append(content_type)
        if origin_name is not None:
            where_clauses.append("origin_name = ?")
            params.append(origin_name)
        if origin_type is not None:
            where_clauses.append("origin_type = ?")
            params.append(origin_type)
        if origin_url is not None:
            where_clauses.append("origin_url = ?")
            params.append(origin_url)
        if metadata is not None and len(metadata) > 0:
            for k, v in metadata.items():
                where_clauses.append(f"json_extract(metadata, '$.{k}') = ?")
                params.append(common.to_str(v))
        if vec_model is not None:
            where_clauses.append("vec_model = ?")
            params.append(vec_model)

        query = f"DELETE FROM {table_name}"
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        connection.execute(query, params)

    def select_doc(self, *, connection:Any=None, select:List[str]=None, servicename:str=None,
                   vec_id:str=None, content_text:str=None, content_type:str=None,
                   origin_name:str=None, origin_type:str=None, origin_url:str=None,
                   metadata:Dict[str, Any]=None, vec_model:str=None,
                   vec_data:str=None, sort_dict:Dict[str, Any]=None, kcount:int=None,) -> Generator[Any, Any, Any]:
        """
        ドキュメントを選択します

        Args:
            connection: データベース接続オブジェクト
            select (str): 取得する項目をカンマ区切りで指定します。未指定の場合はすべての項目を返します。
            servicename (str): サービス名
            vec_id (str): ベクトルID
            content_text (str): ドキュメントの内容
            content_type (str): ドキュメントのタイプ
            origin_name (str): ドキュメントの元の名前
            origin_type (str): ドキュメントの元のタイプ
            origin_url (str): ドキュメントの元のURL
            metadata (dict): ドキュメントのメタデータ
            vec_model (str): ベクトルモデルの名前
            vec_data (str): ドキュメントのベクトル表現
            sort_dict (dict): ソート条件を指定します。キーに項目名、値にソート順（ `ASC` (昇順) 又は `DESC` (降順)）を指定します。
            kcount (int): 検索結果件数

        Yields:
            record: ドキュメントレコード
        """
        if connection is None: raise ValueError("connection is required.")
        if servicename is None: raise ValueError("servicename is required.")

        table_name = f"{servicename}_embedding"
        where_clauses = []
        params = []

        if vec_id:
            where_clauses.append("vec_id = ?")
            params.append(vec_id)
        if content_text:
            where_clauses.append("content_text LIKE ?")
            params.append(f'%{content_text}%')
        if content_type:
            where_clauses.append("content_type = ?")
            params.append(content_type)
        if origin_name:
            where_clauses.append("origin_name = ?")
            params.append(origin_name)
        if origin_type:
            where_clauses.append("origin_type = ?")
            params.append(origin_type)
        if origin_url:
            where_clauses.append("origin_url = ?")
            params.append(origin_url)
        if metadata is not None and len(metadata) > 0:
            for k, v in metadata.items():
                where_clauses.append(f"json_extract(metadata, '$.{k}') = ?")
                params.append(common.to_str(v))
        if vec_model:
            where_clauses.append("vec_model = ?")
            params.append(vec_model)

        select_cols = [s for s in select if s] if select is not None and len(select) > 0 else None
        select_sql = ", ".join(select_cols) if select_cols else "*"

        order_sql = ""
        if vec_data is None and sort_dict is not None and len(sort_dict) > 0:
            order_clauses = []
            for k, v in sort_dict.items():
                if v.upper() not in ['ASC', 'DESC']:
                    raise ValueError("sort_dict values must be 'ASC' or 'DESC'.")
                order_clauses.append(f"{k} {v.upper()}")
            order_sql = " ORDER BY " + ", ".join(order_clauses)

        # vec_data がある場合は全件取得してPythonでソートする
        fetch_limit = ""
        if vec_data is None and kcount is not None:
            fetch_limit = f" LIMIT {kcount}"

        query = f"SELECT {select_sql} FROM {table_name}"
        if where_clauses:
            query += " WHERE " + " AND ".join(where_clauses)
        query += order_sql + fetch_limit

        cur = connection.execute(query, params)
        colnames = [desc[0] for desc in cur.description]

        if vec_data is not None:
            # Pythonサイド L2距離でソートして上位kcount件を返す
            try:
                query_vec = json.loads(vec_data) if isinstance(vec_data, str) else list(vec_data)
            except Exception:
                query_vec = list(vec_data)
            rows = []
            for row in cur:
                record = dict(zip(colnames, row))
                try:
                    stored_vec = json.loads(record.get('vec_data', '[]'))
                    dist = _l2_distance(query_vec, stored_vec)
                except Exception:
                    dist = float('inf')
                rows.append((dist, record))
            rows.sort(key=lambda x: x[0])
            if kcount is not None:
                rows = rows[:kcount]
            for _, record in rows:
                yield record
        else:
            for row in cur:
                yield dict(zip(colnames, row))
