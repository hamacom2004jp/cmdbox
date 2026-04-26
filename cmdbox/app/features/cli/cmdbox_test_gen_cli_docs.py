from cmdbox.app import common, feature
from cmdbox.app.commons import validator
from cmdbox.app.options import Options
from cmdbox.app.features.cli.test import gen_cli_docs
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class TestGenCliDocs(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'test'

    def get_cmd(self) -> str:
        return 'gen_cli_docs'

    def get_option(self) -> Dict[str, Any]:
        op = Options.getInstance(self.appcls, self.ver)
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="詳細設計書の内容を元にコマンドリファレンスRSTファイルを生成します。",
            description_en="Generates command reference RST files from detailed design documents.",
            choice=[
                dict(opt="specs_dir", type=Options.T_DIR, default="./Specifications/", required=False, multi=False, hide=False, choice=None,
                     description_ja="cli-command-specifications.json が存在するSpecificationsディレクトリを指定します。省略時はカレントディレクトリ配下の Specifications ディレクトリを使用します。",
                     description_en="Specify the Specifications directory containing cli-command-specifications.json. Defaults to ./Specifications when omitted."),
                dict(opt="docs_dir", type=Options.T_DIR, default="./docs_src/docs/", required=False, multi=False, hide=False, choice=None,
                     description_ja="cmd_*.rst を出力するディレクトリを指定します。省略時はカレントディレクトリ配下の docs_src/docs ディレクトリを使用します。",
                     description_en="Specify the output directory for cmd_*.rst files. Defaults to ./docs_src/docs when omitted."),
                dict(opt="mode_filter", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     choice_fn=lambda o, webmode, opt: ['']+op.get_mode_keys(),
                     description_ja="生成対象をモード名でフィルタします。省略時は全モードが対象になります。(例: server, client)",
                     description_en="Filter generation targets by mode name. All modes are targeted when omitted. (e.g. server, client)"),
                dict(opt="cmd_filter", type=Options.T_MLIST, default=None, required=False, multi=False, hide=False, choice=[],
                     callcmd="async () => {"
                             + "const res = await get_cmds($(\"[name='mode_filter']\").val());"
                             + "const py_load_cmd = await cmdbox.load_cmd($(\"[name='title']\").val());"
                             + "const val = py_load_cmd['cmd_filter'];"
                             + "$(\"[name='cmd_filter']\").empty();"
                             + "res.map(elm=>{$(\"[name='cmd_filter']\").append('<option value=\"'+elm+'\">'+elm+'</option>');});"
                             + "$(\"[name='cmd_filter']\").val(val);"
                             + "}",
                     description_ja="生成対象をコマンド名でフィルタします。省略時は全コマンドが対象になります。(例: list, start)",
                     description_en="Filter generation targets by command name. All commands are targeted when omitted. (e.g. list, start)"),
                dict(opt="dry_run", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="Trueを指定すると実際にはファイルを書き込まず、生成内容のみ確認できます。",
                     description_en="If True, does not actually write files but only shows what would be generated."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="処理結果jsonファイルを追記保存します。",
                     description_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float,
               pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        """
        詳細設計書の内容を元にコマンドリファレンスRSTファイルを生成します。

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        st, msg, cl = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, cl

        specs_dir = Path(args.specs_dir) if args.specs_dir else Path.cwd() / "Specifications"
        docs_dir = Path(args.docs_dir) if args.docs_dir else Path.cwd() / "docs_src" / "docs"
        mode_filter = args.mode_filter or None
        cmd_filter = args.cmd_filter if isinstance(args.cmd_filter, list) and args.cmd_filter else None
        dry_run = bool(args.dry_run)

        try:
            result = gen_cli_docs.generate(
                specs_dir=specs_dir,
                docs_dir=docs_dir,
                mode_filter=mode_filter,
                cmd_filter=cmd_filter,
                dry_run=dry_run,
            )
        except Exception as e:
            logger.warning(f"gen_cli_docs failed: {e}", exc_info=True)
            msg = dict(warn=str(e))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        errors = result.get("errors", [])
        if errors:
            msg = dict(warn=f"Completed with errors: {errors}", **result)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        msg = dict(
            success=dict(
                message=f"Generated {len(result['generated'])} RST file(s).",
                generated=result["generated"],
                skipped=result["skipped"],
                dry_run=dry_run,
            )
        )
        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        return self.RESP_SUCCESS, msg, None
