from cmdbox.app import common, client, feature, filer
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class ExtractPdfplumber(feature.OneshotResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return "extract"

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'pdfplumber'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            description_ja="指定されたドキュメントファイルからテキストを抽出します。",
            description_en="Extracts text from the specified document file.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                     description_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。",
                     description_en="Specify the service name of the inference server."),
                dict(opt="scope", type=Options.T_STR, default="current", required=True, multi=False, hide=False, choice=["", "client", "current", "server"],
                     description_ja="参照先スコープを指定します。指定可能な画像タイプは `client` , `current` , `server` です。",
                     description_en="Specifies the scope to be referenced. When omitted, 'client' is used.",
                     choice_show=dict(client=["client_data"]),),
                dict(opt="loadpath", type=Options.T_FILE, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="読み込みファイルパスを指定します。",
                     description_en="Specify the source file path."),
                dict(opt="client_data", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja="ローカルを参照させる場合のデータフォルダのパスを指定します。",
                     description_en="Specify the path of the data folder when local is referenced."),
                dict(opt="chunk_table", type=Options.T_STR, default="table", required=False, multi=False, hide=False, choice=["none", "table", "row_with_header"],
                    description_ja="PDFファイル内の表のチャンク方法を指定します。 `none` :表単位でチャンクしない、 `table` :表単位、 `row_with_header` :行単位(ヘッダ付き)",
                    description_en="Specifies how to chunk tables in the PDF file. `none` :do not chunk by table, `table` :by table, `row_with_header` :by row (with header)",
                    choice_show={"none":["chunk_separator", "chunk_exclude"],
                                "table":["chunk_exclude"],
                                "row_with_header":["chunk_table_header","chunk_exclude","chunk_in_metadata"]}),
                dict(opt="chunk_table_header", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                    description_ja="PDFファイル内の表のヘッダー項目名を、左から順に指定し既存のヘッダー項目を置き換えます。",
                    description_en="Replaces existing header items by specifying the names of the table header items in the PDF file, from left to right. "),
                dict(opt="chunk_exec", type=Options.T_TEXT, default=None, required=False, multi=True, hide=False, choice=None,
                    description_ja="チャンクのコンテンツに対してexec文を指定します。" \
                        "現在の行のコンテンツの変数名は `doc` (langchain_core.documents.Document型) 、" \
                        "前の行のコンテンツの変数名は `prev` (langchain_core.documents.Document型) 、" \
                        "コンテンツリストの変数名は `docs` 、" \
                        "ツールの変数名は `tool` (witshape.app.tools.Tools)、" \
                        "DBアクセス変数名は `db` (langchain_postgres.PGVector) です。",
                    description_en="Specify an exec statement for the contents of the chunk. " \
                        "The variable name for the contents of the current row is `doc` (langchain_core.documents.Document type), " \
                        "The variable name for the contents of the previous line is `prev` (langchain_core.documents.Document type), " \
                        "the variable name for the contents list is `docs`, " \
                        "the variable name for the tools is `tool` (witshape.app.tools.Tools), " \
                        "and the DB access variable name is `db` (langchain_postgres.PGVector)."),
                dict(opt="chunk_exclude", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                    description_ja="チャンクに含めない文字列を正規表現で指定します。この指定にマッチした場合はembeddingされません。",
                    description_en="A regular expression specifying a string that should not be included in the chunk. If this specification is matched, embedding will not be performed."),
                dict(opt="chunk_tag", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                    description_ja="チャンクのメタデータに登録するタグを指定します。",
                    description_en="Specify tags to be registered in the chunk metadata."),
                dict(opt="chunk_size", type=Options.T_INT, default=1000, required=False, multi=False, hide=False, choice=None,
                    description_ja="チャンクサイズを指定します。",
                    description_en="Specifies the chunk size."),
                dict(opt="chunk_overlap", type=Options.T_INT, default=50, required=False, multi=False, hide=False, choice=None,
                    description_ja="チャンクのオーバーラップサイズを指定します。",
                    description_en="Specifies the overlap size of the chunk."),
                dict(opt="chunk_separator", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                    description_ja="チャンク化するための区切り文字を指定します。",
                    description_en="Specifies the delimiter character for chunking."),
                dict(opt="chunk_in_metadata", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                    description_ja="チャンクのコンテンツに含めるメタデータを指定します。",
                    description_en="Specifies metadata to be included in the contents of the chunk."),
                dict(opt="chunk_spage", type=Options.T_INT, default=0, required=False, multi=False, hide=False, choice=None,
                    description_ja="エンベディング範囲の開始ページを指定します。",
                    description_en="Specifies the starting page of the embedding range."),
                dict(opt="chunk_epage", type=Options.T_INT, default=9999, required=False, multi=False, hide=False, choice=None,
                    description_ja="エンベディング範囲の終了ページを指定します。",
                    description_en="Specifies the ending page of the embedding range."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。",
                     description_en="Specifies the number of reconnections to the Redis server."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default=120, required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="処理結果jsonファイルを追記保存します。",
                     description_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
            ])

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
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if args.scope is None:
            msg = dict(warn=f"Please specify the --scope option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if args.loadpath is None:
            msg = dict(warn=f"Please specify the --loadpath option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        try:
            client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
            if args.scope == "client":
                if client_data is not None:
                    f = filer.Filer(client_data, logger)
                    chk, abspath, msg = f._file_exists(args.loadpath)
                    if not chk:
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, msg, None
                    res = self.extract(abspath, args, logger, tm, pf)
                    common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    if 'success' not in res:
                        return self.RESP_WARN, res, None
                    return self.RESP_SUCCESS, res, None
                else:
                    msg = dict(warn=f"client_data is empty.")
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
            elif args.scope == "current":
                f = filer.Filer(Path.cwd(), logger)
                chk, abspath, msg = f._file_exists(args.loadpath)
                if not chk:
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
                res = self.extract(abspath, args, logger, tm, pf)
                common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                if 'success' not in res:
                    return self.RESP_WARN, res, None
                return self.RESP_SUCCESS, res, None
            elif args.scope == "server":
                cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
                payload = dict(
                    loadpath=args.loadpath,
                    client_data=args.client_data,
                    chunk_lang=args.chunk_lang,
                    chunk_max_tokens=args.chunk_max_tokens,
                    chunk_max_sentences=args.chunk_max_sentences,
                    chunk_overlap_percent=args.chunk_overlap_percent,
                )
                payload_b64 = convert.str2b64str(common.to_str(payload))
                res = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                            retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                if 'success' not in res:
                    return self.RESP_WARN, res, None
                return self.RESP_SUCCESS, res, None
            else:
                logger.warning(f"scope is invalid. {args.scope}")
                return dict(warn=f"scope is invalid. {args.scope}")
        except Exception as e:
            logger.warning(f"Exception occurred. {e}", exc_info=True)
            return self.RESP_WARN, dict(warn=f"Exception occurred. {e}"), None

    def is_cluster_redirect(self):
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
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            f = filer.Filer(data_dir, logger)
            chk, abspath, res = f._file_exists(payload.get('loadpath'))
            if not chk:
                logger.warning(f"File not found. {payload.get('loadpath')}")
                redis_cli.rpush(reskey, res)
                return self.RESP_WARN
            args = argparse.Namespace(**payload)
            res = self.extract(abspath, args, logger, 0, [])
            redis_cli.rpush(reskey, res)
        except Exception as e:
            logger.warning(f"Failed to {self.get_svcmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to {self.get_svcmd()}: {e}", end=True))
            return self.RESP_WARN
        return self.RESP_SUCCESS

    def extract(self, abspath:Path, args:argparse.Namespace, logger:logging.Logger, tm:float, pf:List[Dict[str, float]]=[]) -> Dict[str, Any]:
        """
        指定されたファイルからテキストを抽出します

        Args:
            abspath (Path): 抽出対象ファイルの絶対パス
            args (argparse.Namespace): 引数
            logger (logging.Logger): ロガー
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報
        Returns:
            Dict[str, Any]: 抽出結果
        """
        try:
            if abspath is not None and not abspath.is_file():
                raise IOError(f"File not found. {abspath}")
            if args.chunk_size is None: raise ValueError("chunk_size is required.")
            if args.chunk_overlap is None: raise ValueError("chunk_overlap is required.")
            from langchain_text_splitters import (
                MarkdownTextSplitter,
                RecursiveCharacterTextSplitter,
            )
            import pdfplumber
            chunk_separator = None if args.chunk_separator is None or len(args.chunk_separator)<=0 else args.chunk_separator
            md_splitter = MarkdownTextSplitter(chunk_size=args.chunk_size,
                                               chunk_overlap=args.chunk_overlap)
            txt_splitter = RecursiveCharacterTextSplitter(chunk_size=args.chunk_size,
                                                          chunk_overlap=args.chunk_overlap,
                                                          separators=chunk_separator)
            excludes = args.chunk_exclude if args.chunk_exclude is not None else []
            excludes = [re.compile(ex) for ex in excludes]
            docs = []
            doc_tables = []
            with pdfplumber.open(abspath) as pdf:
                #tset = TableSettings.resolve(table_settings)
                for page in pdf.pages:
                    if logger.level == logging.DEBUG:
                        logger.debug(f"  page_number: {page.page_number}")
                    if args.chunk_spage > page.page_number or args.chunk_epage < page.page_number:
                        continue
                    text = page.extract_text()
                    texts = txt_splitter.split_text(text)
                    if logger.level == logging.DEBUG:
                        logger.debug(f"  text: {text}")
                        logger.debug(f"  texts: {texts}")
                    # チャンク方法がテーブル単位又は行単位の場合の処理
                    if "chunk_table" in args and args.chunk_table is not None and args.chunk_table in ["table", "row_with_header"]:
                        tables = page.extract_tables()
                        with_header = True if args.chunk_table == "row_with_header" else False
                        # テーブル抽出できた場合
                        if tables is not None and len(tables) > 0:
                            header_md = ""
                            table_meta_idx = {}
                            table_md = ""
                            for table in tables:
                                rowidx = 1
                                for row in table:
                                    if row is None or type(row) is not list:
                                        continue
                                    row = [('' if r is None else r.replace('\n', ' ')) for r in row] # セル内の改行をスペースに変換
                                    if len(row) != len([r for r in row if all([not ex.search(r) for ex in excludes])]):
                                        continue # 除外パターンにマッチするセルがある行はスキップ
                                    row_md = f'|{"|".join(row)}|\n'
                                    # チャンク単位のmd生成
                                    if with_header:
                                        if header_md == '':
                                            ah = args.chunk_table_header
                                            if ah is not None and isinstance(ah, list):
                                                row = [r for r in (ah+row[len(ah):])[:len(row)]]
                                                row_md = f'|{"|".join(row)}|\n'
                                                table_meta_idx = {r:i for i,r in enumerate(row) if r in ah}
                                            header_md = row_md
                                            continue
                                        try:
                                            tmeta = {r:row[i] for r,i in table_meta_idx.items()}
                                        except IndexError:
                                            tmeta = dict()
                                        row_chunk = md_splitter.split_text(header_md+row_md)
                                        if logger.level == logging.DEBUG:
                                            logger.debug(f"    addrow: {header_md+row_md}")

                                        doc_tables += [dict(content=r, metadata=dict(source=str(abspath),
                                                                                page=page.page_number,
                                                                                table=True,
                                                                                row=True,
                                                                                rowidx=rowidx,
                                                                                **tmeta)) for r in row_chunk]
                                        rowidx += 1
                                        continue
                                    # テーブル単位のmd生成
                                    table_md += row_md
                            table_chunk = md_splitter.split_text(table_md)
                            doc_tables += [dict(content=header_md+t, metadata=dict(source=str(abspath), page=page.page_number, table=True)) for t in table_chunk]
                    else:
                        docs += [dict(content=t, metadata=dict(source=str(abspath), page=page.page_number)) for t in texts]
            ret = dict(success=dict(file=abspath, data=docs+doc_tables))
            logger.info(f"extract success. abspath={abspath}")
            return ret
        except Exception as e:
            logger.error(f"extract error: {str(e)}", exc_info=True)
            ret = dict(error=f"extract error: {str(e)}")
            return ret
