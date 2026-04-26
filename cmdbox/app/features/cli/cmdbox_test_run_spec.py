from cmdbox.app import common, feature
from cmdbox.app.commons import validator
from cmdbox.app.options import Options
from cmdbox.app.features.cli.test import run_spec
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import importlib
import logging
import shutil


class TestRunSpec(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'test'

    def get_cmd(self) -> str:
        return 'run_spec'

    def get_option(self) -> Dict[str, Any]:
        op = Options.getInstance(self.appcls, self.ver)
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="テスト仕様JSONに基づいてテストを実行し、結果を報告します。",
            description_en="Runs tests based on the unit test specification JSON and reports results.",
            choice=[
                dict(opt="mode_filter", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     choice_fn=lambda o, webmode, opt: ['']+op.get_mode_keys(),
                     description_ja="実行対象をモード名でフィルタします。省略時は全モードを実行します。(例: server, test)",
                     description_en="Filter test targets by mode name. Runs all modes when omitted. (e.g. server, test)"),
                dict(opt="cmd_filter", type=Options.T_MLIST, default=None, required=False, multi=False, hide=False, choice=[],
                     callcmd="async () => {"
                             + "const res = await get_cmds($(\"[name='mode_filter']\").val());"
                             + "const py_load_cmd = await cmdbox.load_cmd($(\"[name='title']\").val());"
                             + "const val = py_load_cmd['cmd_filter'];"
                             + "$(\"[name='cmd_filter']\").empty();"
                             + "res.map(elm=>{$(\"[name='cmd_filter']\").append('<option value=\"'+elm+'\">'+elm+'</option>');});"
                             + "$(\"[name='cmd_filter']\").val(val);"
                             + "}",
                     description_ja="実行対象をコマンド名でフィルタします。省略時は全コマンドを実行します。(例: list, start)",
                     description_en="Filter test targets by command name. Runs all commands when omitted. (e.g. list, start)"),
                dict(opt="input_json", type=Options.T_FILE, default="./Specifications_forUnitTest/cli-unit-test-specifications.json",
                     required=True, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="入力となる cli-unit-test-specifications.json のパスを指定します。",
                     description_en="Specify the path to the input cli-unit-test-specifications.json."),
                dict(opt="use_tempdir", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="出力系パラメータを一時ディレクトリに置換してテストを実行します。Trueにすると既存ファイルを上書きしません。",
                     description_en="Replace output parameters with temporary directories during test execution. When True, avoids overwriting existing files."),
                dict(opt="output_dir", type=Options.T_DIR, default="./Specifications_forUnitTest_results/", required=False, multi=False, hide=False, choice=None, fileio="out",
                     description_ja="テスト実行結果（JSONおよびMD）の出力先ディレクトリを指定します。省略時は ./Specifications_forUnitTest_results を使用します。",
                     description_en="Specify the output directory for test run results (JSON and MD). Defaults to ./Specifications_forUnitTest_results when omitted."),
                dict(opt="clear_output_dir", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="Trueを指定すると、出力先ディレクトリが既に存在する場合にクリア（削除して再作成）してから結果を出力します。Falseの場合（デフォルト）、既存の結果ファイルに今回のテストケース結果をマージして上書きします。",
                     description_en="If True, clears (deletes and recreates) the output directory before writing results when it already exists. If False (default), merges the current test case results into the existing result files, overwriting only the executed test cases."),
                dict(opt="app_class", type=Options.T_STR, default=f"{self.appcls.__module__}.{self.appcls.__name__}", required=False, multi=False, hide=False, choice=None,
                     description_ja=f"テスト対象のアプリケーションクラスのモジュールパスを指定します。(例: myapp.app.MyApp) 省略時は {self.appcls.__module__}.{self.appcls.__name__} を使用します。",
                     description_en=f"Specify the module path of the application class to test. (e.g. myapp.app.MyApp) Defaults to {self.appcls.__module__}.{self.appcls.__name__} when omitted."),
                dict(opt="ver_module", type=Options.T_STR, default=f"{self.ver.__loader__.name}", required=False, multi=False, hide=False, choice=None,
                     description_ja=f"バージョンモジュールのパスを指定します。(例: myapp.version) 省略時は {self.ver.__loader__.name} を使用します。",
                     description_en=f"Specify the path of the version module. (e.g. myapp.version) Defaults to {self.ver.__loader__.name} when omitted."),
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
        テスト仕様JSONに基づいてテストを実行し、結果を報告します。

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

        input_json = Path(args.input_json)
        if not input_json.exists():
            msg = dict(warn=f"input_json not found: {input_json}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        mode_filter = args.mode_filter or None
        cmd_filter = args.cmd_filter or None
        use_tempdir = args.use_tempdir if hasattr(args, 'use_tempdir') else False

        output_dir = Path(args.output_dir) if args.output_dir else None
        clear_output_dir = bool(args.clear_output_dir)
        merge_existing = False

        if output_dir is not None and output_dir.exists():
            if clear_output_dir:
                shutil.rmtree(output_dir)
            else:
                merge_existing = True

        # app_class の解決
        appcls = self.appcls
        if args.app_class:
            try:
                module_path, _, class_name = args.app_class.rpartition(".")
                mod = importlib.import_module(module_path)
                appcls = getattr(mod, class_name)
            except Exception as e:
                msg = dict(warn=f"Failed to load app_class '{args.app_class}': {e}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        # ver_module の解決
        ver = self.ver
        if args.ver_module:
            try:
                ver = importlib.import_module(args.ver_module)
            except Exception as e:
                msg = dict(warn=f"Failed to import ver_module '{args.ver_module}': {e}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        try:
            result = run_spec.run(
                input_json=input_json,
                mode_filter=mode_filter,
                cmd_filter=cmd_filter,
                appcls=appcls,
                ver=ver,
                use_tempdir=use_tempdir,
                output_dir=output_dir,
                merge_existing=merge_existing,
            )
        except Exception as e:
            logger.warning(f"run_spec failed: {e}", exc_info=True)
            msg = dict(warn=str(e))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        summary = result["summary"]
        failed_count = summary["failed"]
        success_data: Dict[str, Any] = dict(
            message="Test completed",
            **summary,
            results=result["results"],
        )
        if output_dir is not None:
            success_data["output_dir"] = str(output_dir)
            success_data["json_file"] = str(output_dir / "test-run-results.json")
            success_data["index_md_file"] = str(output_dir / "README.md")
            success_data["error_json_file"] = str(output_dir / "test-run-errors.json")
            success_data["error_md_file"] = str(output_dir / "ERRORS.md")
        msg: Dict[str, Any] = dict(success=dict(data=success_data))
        if failed_count > 0:
            msg["warn"] = f"{failed_count} test case(s) failed."

        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        return self.RESP_SUCCESS if failed_count == 0 else self.RESP_WARN, msg, None

    def is_cluster_redirect(self) -> bool:
        return False

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        return self.RESP_SUCCESS
