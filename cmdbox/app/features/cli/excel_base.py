from cmdbox.app import common, client, filer, feature
from cmdbox.app.commons import convert
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import html
import re


class ExcelBase(feature.ResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'excel'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=True,
            description_ja="",
            description_en="",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="scope", type=Options.T_STR, default="client", required=True, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="参照先スコープを指定します。指定可能な画像タイプは `client` , `current` , `server` です。",
                     description_en="Specifies the scope to be referenced. When omitted, 'client' is used.",
                     choice_show=dict(client=["client_data"]),
                     test_true={"server":"server",
                                "client":"client",
                                "current":"current"}),
                dict(opt="svpath", type=Options.T_FILE, default="/", required=True, multi=False, hide=False, choice=None,
                     description_ja="サーバーのデータフォルダ以下のパスを指定します。省略時は `/` を使用します。",
                     description_en="Specify the directory path to get the list of files.",
                     test_true={"server":"/"}),
                dict(opt="client_data", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="ローカルを参照させる場合のデータフォルダのパスを指定します。",
                     description_en="Specify the path of the data folder when local is referenced.",
                     test_true={"server":None,
                                "client":common.HOME_DIR / f".{self.ver.__appid__}",
                                "current":None}),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="15", required=False, multi=False, hide=True, choice=None,
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
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

    OPENPYXL_TYPE_TO_STRING = {
        "n": "numeric",
        "s": "string",
        "f": "formula",
        "b": "boolean",
        "e": "error",
    }

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
        chk, msg, _ = self.chk_args(args, tm, pf)
        if chk != self.RESP_SUCCESS:
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        try:
            client_data = Path(args.client_data.replace('"','')) if args.client_data is not None else None
            if args.scope == "client":
                if client_data is not None:
                    f = filer.Filer(client_data, logger)
                    chk, abspath, msg = f._file_exists(args.svpath)
                    if not chk:
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, msg, None
                    res = self.excel_proc(abspath, args, logger, tm, pf)
                    if 'success' not in res:
                        common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, res, None
                    common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_SUCCESS, res, None
                else:
                    msg = dict(warn=f"client_data is empty.")
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
            elif args.scope == "current":
                f = filer.Filer(Path.cwd(), logger)
                chk, abspath, msg = f._file_exists(args.svpath)
                if not chk:
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
                res = self.excel_proc(abspath, args, logger, tm, pf)
                if 'success' not in res:
                    common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, res, None
                common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_SUCCESS, res, None
            elif args.scope == "server":
                cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
                res = cl.redis_cli.send_cmd(self.get_svcmd(), self.get_svparam(args),
                                                retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout)
                if 'success' not in res:
                    common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, res, None
                common.print_format(res, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_SUCCESS, res, None
            else:
                logger.warning(f"scope is invalid. {args.scope}")
                return dict(warn=f"scope is invalid. {args.scope}")
        except Exception as e:
            logger.warning(f"Exception occurred. {e}", exc_info=True)
            return self.RESP_WARN, dict(warn=f"Exception occurred. {e}"), None

    def chk_args(self, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[bool, str, Any]:
        """
        引数のチェックを行います

        Args:
            args (argparse.Namespace): 引数

        Returns:
            Tuple[bool, str]: チェック結果, メッセージ
        """
        if args.svname is None:
            msg = dict(warn=f"Please specify the --svname option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if args.scope is None:
            msg = dict(warn=f"Please specify the --scope option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if args.svpath is None:
            msg = dict(warn=f"Please specify the --svpath option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        return self.RESP_SUCCESS, None, None

    def excel_proc(self, abspath:Path, args:argparse.Namespace, logger:logging.Logger, tm:float, pf:List[Dict[str, float]]=[]) -> Dict[str, Any]:
        """
        Excel処理のベース

        Args:
            abspath (Path): Excelファイルの絶対パス
            args (argparse.Namespace): 引数
            logger (logging.Logger): ロガー
            tm (float): 処理時間
            pf (List[Dict[str, float]]): パフォーマンス情報

        Returns:
            Dict[str, Any]: 結果
        """
        raise NotImplementedError("Excel processing is not implemented.")

    def get_svparam(self, args:argparse.Namespace) -> List[str]:
        """
        サーバーに送信するパラメーターを返します

        Args:
            args (argparse.Namespace): 引数

        Returns:
            List[str]: サーバーに送信するパラメーター
        """
        raise NotImplementedError("Get svparam is not implemented.")

    def format_cell(self, output_cell_format:str, otxt:str, val:str, logger:logging.Logger) -> str:
        """
        テキストをフォーマットに応じて、valをフォーマットします

        Args:
            output_cell_format (str): 出力フォーマット
            otxt (str): 追加先のテキスト
            val (str): セルの値
            logger (logging.Logger): ロガー

        Returns:
            str: 追加後のテキスト
        """
        val = str(val) if val is not None else ""
        otxt = otxt if otxt is not None else ""
        ret = ""
        if output_cell_format == 'csv':
            ret = val.replace("\n", " ").replace("\r", "")
            ret = ret.replace('"', '""')
            ret = ret if ret.find(",")>-1 else f'"{ret}"'
            if otxt and not otxt.endswith("\n"):
                ret = f",{ret}"
        elif output_cell_format == 'md':
            ret = val.replace("\n", " ").replace("\r", "")
            ret = ret.replace('|', r'\|')
            if otxt and not otxt.endswith("\n"):
                ret = f"{ret}|"
            else:
                ret = f"|{ret}|"
        elif output_cell_format == 'html':
            ret = html.escape(val)
            ret = ret.replace("\n", "<br/>").replace("\r", "")
            ret = f"<td>{ret}</td>"
        return ret

    def format_newline(self, output_cell_format:str, otxt:str, logger:logging.Logger) -> str:
        """
        テキストをフォーマットに応じて改行を追加します

        Args:
            output_cell_format (str): 出力フォーマット
            otxt (str): 追加先のテキスト
            logger (logging.Logger): ロガー

        Returns:
            str: 追加後のテキスト
        """
        otxt = otxt if otxt is not None else ""
        ret = ""
        if output_cell_format == 'csv':
            ret = f"{otxt}\n" if otxt else "\n"
        elif output_cell_format == 'md':
            ret = f"{otxt}\n" if otxt else "\n"
        elif output_cell_format == 'html':
            if otxt and otxt.find(r"<TTRR/>") > -1:
                pre = re.sub(r'<TTRR/>.*', '', otxt, flags=re.DOTALL)
                post = re.sub(r'.+<TTRR/>', '', otxt, flags=re.DOTALL)
                ret = f"{pre}<tr>{post}</tr>\n<TTRR/>"
            elif otxt:
                ret = f"<tr>{otxt}</tr>\n<TTRR/>"
            elif not otxt:
                ret = "<tr></tr>\n<TTRR/>"
        return ret

    def format_table(self, output_cell_format:str, otxt:str, logger:logging.Logger) -> str:
        """
        テキストをフォーマットに応じてテーブルを構成します
        Args:
            output_cell_format (str): 出力フォーマット
            otxt (str): 追加先のテキスト
            logger (logging.Logger): ロガー
        Returns:
            str: 追加後のテキスト
        """
        otxt = otxt if otxt is not None else ""
        ret = ""
        if output_cell_format == 'csv':
            ret = f"{otxt}\n" if otxt else "\n"
        elif output_cell_format == 'md':
            ret = f"{otxt}\n" if otxt else "\n"
        elif output_cell_format == 'html':
            otxt = re.sub(r'<TTRR/>.*', '', otxt, flags=re.DOTALL)
            if otxt:
                ret = f"<table>{otxt}</table>\n"
            elif not otxt:
                ret = "\n"
        return ret
