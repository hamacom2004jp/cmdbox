from typing import Dict, Any, Generator, List
import logging


class RagStore:
    @classmethod
    def create(cls, ds_conf:dict, logger:logging.Logger, appcls, ver, language:str=None) -> 'RagStore':
        """
        RagStoreのインスタンスを作成します

        Args:
            ds_conf (dict): データソース設定
            logger (logging.Logger): ロガー

        Returns:
            RagStore: RagStoreのインスタンス
        """
        from cmdbox.app.features.cli import cmdbox_datasource_load
        dbtype = ds_conf.get('dbtype')
        if dbtype=='postgresql':
            from cmdbox.app.features.cli.rag import rag_postgresql
            ret = rag_postgresql.RagPostgresql(dbhost=ds_conf.get('db_host'),
                                    dbport=ds_conf.get('db_port'),
                                    dbname=ds_conf.get('db_name'),
                                    dbuser=ds_conf.get('db_user'),
                                    dbpass=ds_conf.get('db_password'),
                                    dbtimeout=ds_conf.get('db_timeout', 120),
                                    logger=logger)
        elif dbtype=='sqlite':
            from cmdbox.app.features.cli.rag import rag_sqlite
            ret = rag_sqlite.RagSqlite(dbpath=ds_conf.get('db_path'),
                                        dbtimeout=ds_conf.get('db_timeout', 120),
                                        logger=logger)
        else:
            raise NotImplementedError(f"Unsupported datasource type: {dbtype}")
        ret.ds_load = cmdbox_datasource_load.DatasourceLoad(appcls, ver=ver, language=language)
        ret.ds_conf = ds_conf
        return ret

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
        conn, dbtype = self.ds_load.get_connection(self.ds_conf)
        return conn

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
        raise NotImplementedError("select_doc method is not implemented.")
