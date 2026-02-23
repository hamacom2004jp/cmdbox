from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import logging
import psycopg


class RagStore:
    @classmethod
    def create(cls, rag_conf:dict, logger:logging.Logger) -> 'RagStore':
        """
        RagStoreのインスタンスを作成します

        Args:
            rag_conf (dict): RAG設定
            logger (logging.Logger): ロガー

        Returns:
            RagStore: RagStoreのインスタンス
        """
        rag_type = rag_conf.get('rag_type')
        if rag_type=='vector_pg':
            from . import rag_pgvector
            return rag_pgvector.RagPgvector(dbhost=rag_conf.get('vector_store_pghost'),
                                    dbport=rag_conf.get('vector_store_pgport'),
                                    dbname=rag_conf.get('vector_store_pgdbname'),
                                    dbuser=rag_conf.get('vector_store_pguser'),
                                    dbpass=rag_conf.get('vector_store_pgpass'),
                                    dbtimeout=rag_conf.get('vector_store_pgtimeout', 120),
                                    logger=logger)
        elif rag_type=='vector_sqlite':
            raise NotImplementedError(f"Unsupported RAG type: {rag_type}")
        elif rag_type=='graph_n4j':
            raise NotImplementedError(f"Unsupported RAG type: {rag_type}")
        elif rag_type=='graph_pg':
            raise NotImplementedError(f"Unsupported RAG type: {rag_type}")
        else:
            raise NotImplementedError(f"Unsupported RAG type: {rag_type}")

    def install(self) -> None:
        """
        必要なモジュールのインストールを行います
        """
        raise NotImplementedError("install method is not implemented.")

    def create_tables(self, servicename:str, embed_vector_dim:int=256) -> None:
        """
        テーブルを作成します

        Args:
            servicename (str): サービス名
            embed_vector_dim (int): 埋め込みベクトルの次元数
        """
        raise NotImplementedError("create_tables method is not implemented.")

    def connect(self) -> Any:
        """
        データベースに接続します
        """
        raise NotImplementedError("connect method is not implemented.")

    def insert_doc(self, *, connection:Any=None, servicename:str=None,
                   content_text:str=None, content_type:str=None, content_blob:bytes=None,
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
        raise NotImplementedError("insert_doc method is not implemented.")

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
