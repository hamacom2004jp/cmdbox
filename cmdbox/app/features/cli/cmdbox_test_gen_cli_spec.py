from cmdbox.app import common, feature
from cmdbox.app.options import Options
from cmdbox.app.features.cli.test import gen_cli_spec
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import importlib
import logging


class TestGenCliSpec(feature.OneshotResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        return 'test'

    def get_cmd(self) -> str:
        return 'gen_cli_spec'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="フィーチャーパッケージを解析してCLIコマンド詳細設計書を生成します。",
            description_en="Analyzes a feature package and generates CLI command detailed design documents.",
            choice=[
                dict(opt="feature_package", type=Options.T_STR, default="cmdbox.app.features.cli", required=True, multi=False, hide=False, choice=None,
                     description_ja="フィーチャーを含むPythonパッケージ名を指定します。(例: cmdbox.app.features.cli, myapp.app.features.cli)",
                     description_en="Specify the Python package name containing features.(e.g. cmdbox.app.features.cli, myapp.app.features.cli)"),
                dict(opt="output_dir", type=Options.T_DIR, default="./Specifications/", required=False, multi=False, hide=False, choice=None, fileio="out",
                     description_ja="仕様書の出力先ディレクトリを指定します。省略時はカレントディレクトリ配下の Specifications ディレクトリを使用します。",
                     description_en="Specify the output directory for specifications.Defaults to ./Specifications when omitted."),
                dict(opt="root_dir", type=Options.T_DIR, default="./", required=False, multi=False, hide=False, choice=None,
                     description_ja="プロジェクトルートディレクトリを指定します。ソースファイルの相対パス計算に使用します。省略時はカレントディレクトリを使用します。",
                     description_en="Specify the project root directory used for computing relative source paths.Defaults to the current directory when omitted."),
                dict(opt="prefix", type=Options.T_STR, default="cmdbox_", required=False, multi=False, hide=False, choice=None,
                     description_ja="フィーチャーモジュールのファイル名プレフィックスを指定します。",
                     description_en="Specify the filename prefix of feature modules."),
                dict(opt="app_class", type=Options.T_STR, default=f"{self.appcls.__module__}.{self.appcls.__name__}", required=False, multi=False, hide=False, choice=None,
                     description_ja=f"アプリケーションクラスのモジュールパスを指定します。(例: myapp.app.MyApp) 省略時は {self.appcls.__module__}.{self.appcls.__name__} を使用します。",
                     description_en=f"Specify the module path of the application class.(e.g. myapp.app.MyApp) Defaults to {self.appcls.__module__}.{self.appcls.__name__} when omitted."),
                dict(opt="ver_module", type=Options.T_STR, default=f"{self.ver.__loader__.name}", required=False, multi=False, hide=False, choice=None,
                     description_ja=f"バージョンモジュールのパスを指定します。(例: myapp.version) 省略時は {self.ver.__loader__.name} を使用します。",
                     description_en=f"Specify the path of the version module.(e.g. myapp.version) Defaults to {self.ver.__loader__.name} when omitted."),
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
        フィーチャーパッケージを解析してCLIコマンド詳細設計書を生成します。

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        feature_package = args.feature_package
        if not feature_package:
            msg = dict(warn="Please specify the --feature_package option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        root_dir = Path(args.root_dir) if args.root_dir else Path.cwd()
        output_dir = Path(args.output_dir) if args.output_dir else root_dir / "Specifications"
        prefix = args.prefix or "cmdbox_"

        appcls = None
        if args.app_class:
            try:
                module_path, _, class_name = args.app_class.rpartition(".")
                mod = importlib.import_module(module_path)
                appcls = getattr(mod, class_name)
            except Exception as e:
                msg = dict(warn=f"Failed to load app_class '{args.app_class}': {e}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        ver = None
        if args.ver_module:
            try:
                ver = importlib.import_module(args.ver_module)
            except Exception as e:
                msg = dict(warn=f"Failed to import ver_module '{args.ver_module}': {e}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        try:
            documents = gen_cli_spec.generate(
                feature_package=feature_package,
                output_dir=output_dir,
                root_dir=root_dir,
                prefix=prefix,
                appcls=appcls,
                ver=ver,
            )
        except Exception as e:
            logger.warning(f"generate_cli_spec failed: {e}", exc_info=True)
            msg = dict(warn=str(e))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        msg = dict(
            success=f"Generated {len(documents)} command specifications.",
            output_dir=str(output_dir),
            json_file=str(output_dir / "cli-command-specifications.json"),
            count=len(documents),
        )
        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        return self.RESP_SUCCESS, msg, None

    def is_cluster_redirect(self) -> bool:
        return False

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        return self.RESP_SUCCESS
