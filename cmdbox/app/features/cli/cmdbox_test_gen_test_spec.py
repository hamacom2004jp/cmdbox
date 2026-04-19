from cmdbox.app import common, feature
from cmdbox.app.options import Options
from cmdbox.app.features.cli.test import gen_test_spec
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class TestGenTestSpec(feature.OneshotResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        return 'test'

    def get_cmd(self) -> str:
        return 'gen_test_spec'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="CLIコマンド仕様JSONを読み込みユニットテスト仕様書を生成します。",
            description_en="Reads CLI command specification JSON and generates unit test specification documents.",
            choice=[
                dict(opt="input_json", type=Options.T_FILE, default="./Specifications/cli-command-specifications.json", required=True, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="入力となる cli-command-specifications.json のパスを指定します。",
                     description_en="Specify the path to the input cli-command-specifications.json."),
                dict(opt="output_dir", type=Options.T_DIR, default="./Specifications_forUnitTest/", required=False, multi=False, hide=False, choice=None, fileio="out",
                     description_ja="テスト仕様書の出力先ディレクトリを指定します。省略時はカレントディレクトリ配下の Specifications_forUnitTest ディレクトリを使用します。",
                     description_en="Specify the output directory for test specifications. Defaults to ./Specifications_forUnitTest when omitted."),
                dict(opt="root_dir", type=Options.T_DIR, default="./", required=False, multi=False, hide=False, choice=None,
                     description_ja="プロジェクトルートディレクトリを指定します。詳細設計書マークダウンの参照に使用します。省略時はカレントディレクトリを使用します。",
                     description_en="Specify the project root directory used for referencing design document markdowns. Defaults to the current directory when omitted."),
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
        CLIコマンド仕様JSONを読み込みユニットテスト仕様書を生成します。

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        input_json = Path(args.input_json) if args.input_json else None
        if input_json is None:
            msg = dict(warn="Please specify the --input_json option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        if not input_json.exists():
            msg = dict(warn=f"input_json not found: {input_json}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        root_dir = Path(args.root_dir) if args.root_dir else Path.cwd()
        output_dir = Path(args.output_dir) if args.output_dir else root_dir / "Specifications_forUnitTest"

        try:
            documents = gen_test_spec.generate(
                input_json=input_json,
                output_dir=output_dir,
                root_dir=root_dir,
            )
        except Exception as e:
            logger.warning(f"gen_unit_test_spec failed: {e}", exc_info=True)
            msg = dict(warn=str(e))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        msg = dict(
            success=f"Generated {len(documents)} unit test specifications.",
            output_dir=str(output_dir),
            json_file=str(output_dir / "cli-unit-test-specifications.json"),
            count=len(documents),
        )
        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        return self.RESP_SUCCESS, msg, None

    def is_cluster_redirect(self) -> bool:
        return False

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        return self.RESP_SUCCESS
