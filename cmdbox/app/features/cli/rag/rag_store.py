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
        raise NotImplementedError("delete_doc method is not implemented.")

    def select_doc(self, *, connection:Any=None, servicename:str=None,
                   vec_id:str=None, content_text:str=None, content_type:str=None,
                   origin_name:str=None, origin_type:str=None, origin_url:str=None,
                   metadata:Dict[str, Any]=None, vec_model:str=None) -> None:
        """
        ドキュメントを選択します

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

        Yields:
            record: ドキュメントレコード
        """
        raise NotImplementedError("select_doc method is not implemented.")
