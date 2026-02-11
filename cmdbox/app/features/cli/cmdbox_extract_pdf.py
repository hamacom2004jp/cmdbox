from cmdbox.app import common, client, feature, filer
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class ExtractPdf(feature.OneshotResultEdgeFeature):
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
        return 'pdf'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            description_ja="指定されたファイルからテキストを抽出します。",
            description_en="Extracts text from the specified file.",
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
                dict(opt="loadpath", type=Options.T_DIR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="読み込み元パスを指定します。",
                     description_en="Specify the source path."),
                dict(opt="loadgrep", type=Options.T_STR, default="*", required=True, multi=False, hide=False, choice=None,
                     description_ja="読込みgrepパターンを指定します。",
                     description_en="Specifies a load grep pattern."),
                dict(opt="client_data", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="ローカルを参照させる場合のデータフォルダのパスを指定します。",
                     description_en="Specify the path of the data folder when local is referenced."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。",
                     description_en="Specifies the number of reconnections to the Redis server."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default=120, required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="pdf_table", type=Options.T_STR, default="table", required=False, multi=False, hide=False, choice=["none", "table",],
                    description_ja="PDFファイル内の表の抽出方法を指定します。 `none` :表を抽出しない、 `table` :表単を抽出する.",
                    description_en="Specify how to extract tables in PDF files. `none` :do not extract tables, `table` :extract tables alone.",),
                dict(opt="pdf_exclude", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                    description_ja="コンテンツに含めない文字列を正規表現で指定します。この指定にマッチした場合はembeddingされません。",
                    description_en="A regular expression specifying a string that should not be included in the content. If this specification is matched, embedding will not be performed."),
                dict(opt="pdf_spage", type=Options.T_INT, default=0, required=False, multi=False, hide=False, choice=None,
                    description_ja="エンベディング範囲の開始ページを指定します。",
                    description_en="Specifies the starting page of the embedding range."),
                dict(opt="pdf_epage", type=Options.T_INT, default=9999, required=False, multi=False, hide=False, choice=None,
                    description_ja="エンベディング範囲の終了ページを指定します。",
                    description_en="Specifies the ending page of the embedding range."),
                dict(opt="output_type", type=Options.T_STR, default='markdown', required=False, multi=False, hide=False, choice=['json','csv','markdown'],
                    description_ja="出力するテキストの形式を指定します。",
                    description_en="Specifies the format of the output text."),
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
        if args.loadgrep is None:
            msg = dict(warn=f"Please specify the --loadgrep option.")
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
                    rets = []
                    for file in abspath.glob(args.loadgrep):
                        res = self.extract(file, args, logger, tm, pf)
                        if 'success' not in res:
                            common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                            rets.append(res)
                        common.print_format(res.get('success'), args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        rets.append(res.get('success'))
                    return self.RESP_SUCCESS, dict(success=rets), None
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
                rets = []
                for file in abspath.glob(args.loadgrep):
                    res = self.extract(file, args, logger, tm, pf)
                    if 'success' not in res:
                        common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        rets.append(res)
                    common.print_format(res.get('success'), args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    rets.append(res.get('success'))
                return self.RESP_SUCCESS, dict(success=rets), None
            elif args.scope == "server":
                cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
                payload = dict(
                    loadpath=args.loadpath,
                    loadgrep=args.loadgrep,
                    client_data=args.client_data,
                    pdf_exclude=args.pdf_exclude,
                    pdf_spage=args.pdf_spage,
                    pdf_epage=args.pdf_epage,
                    output_type=args.output_type,
                )
                payload_b64 = convert.str2b64str(common.to_str(payload))
                rets = []
                for res in cl.redis_cli.send_cmd_sse(self.get_svcmd(), [payload_b64],
                                                     retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout):
                    if 'success' not in res:
                        common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        rets.append(res)
                    rets.append(res.get('success'))
                    common.print_format(res.get('success'), args.format, tm, args.output_json, args.output_json_append, pf=pf)
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
            for file in abspath.glob(payload.get('loadgrep')):
                res = self.extract(file, args, logger, 0, [])
                redis_cli.rpush(reskey, res)
            redis_cli.rpush(reskey, dict(success="", end=True))
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
            excludes = args.pdf_exclude if args.pdf_exclude is not None else []
            excludes = [re.compile(ex) for ex in excludes]

            doc_md = self.extract_pdf(abspath, logger, args, excludes)
            ret = dict(success=dict(file=abspath, data=doc_md))

            logger.info(f"extract success. abspath={abspath}")
            return ret
        except Exception as e:
            logger.error(f"extract error: {str(e)}", exc_info=True)
            ret = dict(error=f"extract error: {str(e)}")
            return ret

    def extract_pdf(self, file:Path, logger:logging.Logger, args:argparse.Namespace, excludes:List[re.Pattern]) -> str:
        """
        PDFファイルからテキストを抽出します

        Args:
            file (Path): ファイル
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            excludes (List[re.Pattern]): 除外パターン

        Returns:
            str: 抽出テキスト
        """ 
        doc_md = ""
        doc_json = []
        import pdfplumber
        with pdfplumber.open(file) as pdf:
            #tset = TableSettings.resolve(table_settings)
            for page in pdf.pages:
                if logger.level == logging.DEBUG:
                    logger.debug(f"  page_number: {page.page_number}")
                if args.pdf_spage > page.page_number or args.pdf_epage < page.page_number:
                    continue
                text = page.extract_text()
                # チャンク方法がテーブル単位又は行単位の場合の処理
                if args.pdf_table == "table":
                    tables = page.extract_tables()
                    # テーブル抽出できた場合
                    if tables is not None and len(tables) > 0:
                        table_md = ""
                        table_json = []
                        for table in tables:
                            rowidx = 1
                            for row in table:
                                if row is None or type(row) is not list:
                                    continue
                                row = [('' if r is None else r.replace('\n', ' ')) for r in row] # セル内の改行をスペースに変換
                                if len(row) != len([r for r in row if all([not ex.search(r) for ex in excludes])]):
                                    continue # 除外パターンにマッチするセルがある行はスキップ
                                if args.output_type == 'markdown':
                                    row_md = f'|{"|".join(row)}|\n'
                                elif args.output_type == 'csv':
                                    r = "\",\"".join(r)
                                    row_md = f'"{r}"\n'
                                elif args.output_type == 'json':
                                    table_json.append(row)
                                # テーブル単位のmd生成
                                table_md += row_md
                        doc_md += table_md
                        doc_json.append(table_json)
                else:
                    doc_md += text
        if args.output_type == 'json' and args.pdf_table == "table":
            doc_md = common.to_str(doc_json)
        return doc_md
