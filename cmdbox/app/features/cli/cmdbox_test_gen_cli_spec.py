from cmdbox.app import common, feature
from cmdbox.app.commons import validator
from cmdbox.app.options import Options
from cmdbox.app.features.cli.test import gen_cli_spec
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import importlib
import logging
import shutil


class TestGenCliSpec(feature.OneshotResultEdgeFeature, validator.Validator):
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
                dict(opt="feature_package", type=Options.T_STR, default=f"{self.ver.__appid__}.app.features.cli", required=True, multi=False, hide=False, choice=None,
                     description_ja=f"フィーチャーを含むPythonパッケージ名を指定します。(例: {self.ver.__appid__}.app.features.cli, myapp.app.features.cli)",
                     description_en=f"Specify the Python package name containing features.(e.g. {self.ver.__appid__}.app.features.cli, myapp.app.features.cli)"),
                dict(opt="output_dir", type=Options.T_DIR, default="./Specifications/", required=False, multi=False, hide=False, choice=None, fileio="out",
                     description_ja="仕様書の出力先ディレクトリを指定します。省略時はカレントディレクトリ配下の Specifications ディレクトリを使用します。",
                     description_en="Specify the output directory for specifications.Defaults to ./Specifications when omitted."),
                dict(opt="root_dir", type=Options.T_DIR, default="./", required=False, multi=False, hide=False, choice=None,
                     description_ja="プロジェクトルートディレクトリを指定します。ソースファイルの相対パス計算に使用します。省略時はカレントディレクトリを使用します。",
                     description_en="Specify the project root directory used for computing relative source paths.Defaults to the current directory when omitted."),
                dict(opt="prefix", type=Options.T_STR, default=f"{self.ver.__appid__}_", required=False, multi=False, hide=False, choice=None,
                     description_ja="フィーチャーモジュールのファイル名プレフィックスを指定します。",
                     description_en="Specify the filename prefix of feature modules."),
                dict(opt="clear_output_dir", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="Trueを指定すると、出力先ディレクトリが既に存在する場合にクリア（削除して再作成）してから仕様書を生成します。Falseの場合、出力先ディレクトリが既に存在するとワーニングを返します。",
                     description_en="If True, clears (deletes and recreates) the output directory before generating specifications when it already exists. If False, returns a warning when the output directory already exists."),
                dict(opt="app_class", type=Options.T_STR, default=f"{self.appcls.__module__}.{self.appcls.__name__}", required=False, multi=False, hide=False, choice=None,
                     description_ja=f"アプリケーションクラスのモジュールパスを指定します。(例: myapp.app.MyApp) 省略時は {self.appcls.__module__}.{self.appcls.__name__} を使用します。",
                     description_en=f"Specify the module path of the application class.(e.g. myapp.app.MyApp) Defaults to {self.appcls.__module__}.{self.appcls.__name__} when omitted."),
                dict(opt="ver_module", type=Options.T_STR, default=f"{self.ver.__loader__.name}", required=False, multi=False, hide=False, choice=None,
                     description_ja=f"バージョンモジュールのパスを指定します。(例: myapp.version) 省略時は {self.ver.__loader__.name} を使用します。",
                     description_en=f"Specify the path of the version module.(e.g. myapp.version) Defaults to {self.ver.__loader__.name} when omitted."),
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
        st, msg, cl = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, cl

        feature_package = args.feature_package
        root_dir = Path(args.root_dir) if args.root_dir else Path.cwd()
        output_dir = Path(args.output_dir) if args.output_dir else root_dir / "Specifications"
        prefix = args.prefix or "cmdbox_"
        clear_output_dir = bool(args.clear_output_dir)

        if output_dir.exists():
            if not clear_output_dir:
                msg = dict(warn=f"Output directory already exists: '{output_dir}'. Use --clear_output_dir True to overwrite.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            shutil.rmtree(output_dir)

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
