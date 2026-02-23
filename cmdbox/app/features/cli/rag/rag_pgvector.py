from cmdbox.app import common
from cmdbox.app.features.cli.rag import rag_store
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import logging
import psycopg
from psycopg import sql


class RagPgvector(rag_store.RagStore):
    def __init__(self, dbhost:str, dbport:int, dbname:str, dbuser:str, dbpass:str, dbtimeout:int, logger:logging.Logger):
        """
        コンストラクタ

        Args:
            dbhost (str): データベースホスト名
            dbport (int): データベースポート
            dbname (str): データベース名
            dbuser (str): データベースユーザー名
            dbpass (str): データベースパスワード
            dbtimeout (int): データベース接続のタイムアウト
            logger (logging.Logger): ロガー
        """
        if logger is None:
            raise ValueError("logger is required.")
        if dbhost is None:
            raise ValueError("dbhost is required.")
        if dbport is None:
            raise ValueError("dbport is required.")
        if dbname is None:
            raise ValueError("dbname is required.")
        if dbuser is None:
            raise ValueError("dbuser is required.")
        if dbpass is None:
            raise ValueError("dbpass is required.")
        if dbtimeout is None:
            raise ValueError("dbtimeout is required.")
        self.logger = logger
        self.dbhost = dbhost
        self.dbport = dbport
        self.dbname = dbname
        self.dbuser = dbuser
        self.dbpass = dbpass
        self.dbtimeout = dbtimeout

    def install(self) -> None:
        """
        pgvector拡張機能をインストールします
        """
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                I = sql.Identifier
                cur.execute(sql.SQL("CREATE SCHEMA IF NOT EXISTS {}").format(I(self.dbuser)))
                cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(I(self.dbname), I(self.dbuser)))
                cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA {} TO {}").format(I(self.dbuser), I(self.dbuser)))
                cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA {} TO {}").format(I(self.dbuser), I(self.dbuser)))
                cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA {} TO {}").format(I(self.dbuser), I(self.dbuser)))
                cur.execute(sql.SQL("GRANT ALL PRIVILEGES ON SCHEMA {} TO {}").format(I(self.dbuser), I(self.dbuser)))
                cur.execute(sql.SQL("CREATE EXTENSION IF NOT EXISTS vector"))
                cur.execute(sql.SQL("SELECT extversion FROM pg_extension WHERE extname = 'vector'"))
                for record in cur:
                    self.logger.info(f"extversion={record}")

    def create_tables(self, servicename:str, embed_vector_dim:int=256) -> None:
        """
        テーブルを作成します

        Args:
            servicename (str): サービス名
            embed_vector_dim (int): 埋め込みベクトルの次元数
        """
        if servicename is None: raise ValueError("servicename is required.")

        with self.connect() as conn:
            conn.autocommit = False
            # 特徴量テーブルを作成
            with conn.cursor() as cur:
                table_name = f"{self.dbuser}.{servicename}_embedding"
                I = sql.Identifier
                cur.execute(sql.SQL(
                    "CREATE TABLE IF NOT EXISTS {} (" + \
                    "id SERIAL PRIMARY KEY, " + \
                    "vec_id UUID NOT NULL, " + \
                    "content_text TEXT, " + \
                    "content_type VARCHAR, " + \
                    "content_blob BYTEA, " + \
                    "content_size BIGINT, " + \
                    "origin_name VARCHAR, " + \
                    "origin_type VARCHAR, " + \
                    "origin_url VARCHAR, " + \
                    "metadata JSONB, " + \
                    "vec_model VARCHAR NOT NULL, " + \
                    f"vec_data vector({embed_vector_dim}) NOT NULL, " + \
                    "update_dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP, " + \
                    "created_dt TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP" + \
                    ")").format(I(table_name)))
                cur.execute(sql.SQL(
                    "CREATE UNIQUE INDEX IF NOT EXISTS {} ON {} (vec_id)"
                    ).format(I(f"{table_name}_vec_id_idx"), I(table_name)))
                cur.execute(sql.SQL(
                    "CREATE INDEX IF NOT EXISTS {} ON {} " + \
                    "USING ivfflat (vec_data vector_l2_ops) WITH (lists = 100)"
                    ).format(I(f"{table_name}_vec_data_idx"), I(table_name)))
                conn.commit()

    def connect(self) -> Any:
        """
        データベースに接続します
        """
        return psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout)

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
        content_type = content_type if content_type is not None else metadata.get('content_type', 'text')
        content_blob = content_blob if content_blob is not None else b''
        content_size = len(content_blob) if content_blob else 0
        origin_name = origin_name if origin_name is not None else metadata.get('origin_name', 'unknown')
        origin_type = origin_type if origin_type is not None else metadata.get('origin_type', 'unknown')
        origin_url = origin_url if origin_url is not None else metadata.get('origin_url', 'unknown')
        if metadata is None: raise ValueError("metadata is required.")
        vec_model = vec_model if vec_model is not None else metadata.get('vec_model', 'unknown')
        if vec_data is None: raise ValueError("vec_data is required.")

        with connection.cursor() as cur:
            table_name = f"{self.dbuser}.{servicename}_embedding"
            I = sql.Identifier
            cur.execute(sql.SQL(
                "INSERT INTO {} ("
                "vec_id, "
                "content_text, "
                "content_type, "
                "content_blob, "
                "content_size, "
                "origin_name, "
                "origin_type, "
                "origin_url, "
                "metadata, "
                "vec_model, "
                "vec_data) VALUES ("
                "%(vec_id)s,"
                "%(content_text)s,"
                "%(content_type)s,"
                "%(content_blob)s,"
                "%(content_size)s,"
                "%(origin_name)s,"
                "%(origin_type)s,"
                "%(origin_url)s,"
                "%(metadata)s,"
                "%(vec_model)s,"
                "%(vec_data)s)"
            ).format(I(table_name)), {
                'vec_id': vec_id,
                'content_text': content_text,
                'content_type': content_type,
                'content_blob': content_blob,
                'content_size': content_size,
                'origin_name': origin_name,
                'origin_type': origin_type,
                'origin_url': origin_url,
                'metadata': common.to_str(metadata),
                'vec_model': vec_model,
                'vec_data': common.to_str(vec_data)
            })

    def select_docids(self, servicename:str, file:Path=None):
        """
        ドキュメントIDを取得します

        Args:
            servicename (str): サービス名
            file (Path): ファイル名
        """
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                where = None
                if servicename is not None and file is not None:
                    where = f"WHERE c.name = %(servicename)s AND e.cmetadata->>'source' = %(file)s"
                elif servicename is not None:
                    where = f"WHERE c.name = %(servicename)s"
                else:
                    raise ValueError(f"select_docids param invalid. savetype={savetype}, servicename={servicename}, file={file}")
                cur.execute(f"SELECT e.id FROM langchain_pg_embedding e inner join langchain_pg_collection c " + \
                            f"ON e.collection_id = c.uuid {where}",
                            dict(servicename=servicename, file=str(file)))
                return [record[0] for record in cur]

    def select_page_docids(self, servicename:str, file:Path=None, spage:int=0, epage=9999):
        """
        ページ範囲でドキュメントIDを取得します。
        spage <= 対象ページ < epage の範囲で取得します。

        Args:
            servicename (str): サービス名
            file (Path): ファイル名
            spage (int): 開始ページ
            epage (int): 終了ページ
        """
        with psycopg.connect(
            host=self.dbhost,
            port=self.dbport,
            dbname=self.dbname,
            user=self.dbuser,
            password=self.dbpass,
            connect_timeout=self.dbtimeout) as conn:
            conn.autocommit = True
            with conn.cursor() as cur:
                where = None
                if servicename is not None and file is not None:
                    where = f"WHERE c.name = %(servicename)s AND e.cmetadata->>'source' = %(file)s "
                elif servicename is not None:
                    where = f"WHERE c.name = %(servicename)s "
                else:
                    raise ValueError(f"select_docids param invalid. savetype={savetype}, servicename={servicename}, file={file}")
                where += f"AND CAST(e.cmetadata->>'page' AS INTEGER) >= %(spage)s AND CAST(e.cmetadata->>'page' AS INTEGER) <= %(epage)s "
                cur.execute(f"SELECT e.id FROM langchain_pg_embedding e inner join langchain_pg_collection c " + \
                            f"ON e.collection_id = c.uuid {where}",
                            dict(servicename=servicename, file=str(file), spage=spage, epage=epage))
                return [record[0] for record in cur]
