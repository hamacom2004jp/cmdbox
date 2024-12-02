from cmdbox import version
from cmdbox.app import common, options
from pathlib import Path
from typing import List
import argparse
import argcomplete
import logging
import time
import sys


def main(args_list:list=None):
    app = CmdBoxApp.getInstance()
    return app.main(args_list)[0]

class CmdBoxApp:
    _instance = None
    @staticmethod
    def getInstance():
        if CmdBoxApp._instance is None:
            CmdBoxApp._instance = CmdBoxApp()
        return CmdBoxApp._instance

    def __init__(self, ver=version, cli_features_packages:List[str]=None, cli_features_prefix:List[str]=None):
        """
        コンストラクタ

        Args:
            ver (version, optional): バージョンモジュール. Defaults to version.
            cli_package_name (str, optional): プラグインのパッケージ名. Defaults to None.
            cli_features_prefix (List[str], optional): プラグインのパッケージのモジュール名のプレフィックス. Defaults to None.
        """
        self.options = options.Options.getInstance()
        self.ver = ver
        self.cli_features_packages = cli_features_packages
        self.cli_features_prefix = cli_features_prefix

    def main(self, args_list:list=None, file_dict:dict=dict(), webcall:bool=False):
        """
        コマンドライン引数を処理し、サーバーまたはクライアントを起動し、コマンドを実行する。
        """
        parser = argparse.ArgumentParser(prog=self.ver.__appid__, description=self.ver.__logo__ + '\n\n' + self.ver.__description__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter, exit_on_error=False)

        # プラグイン読込み
        self.options.load_svcmd('cmdbox.app.features.cli')
        if self.cli_features_packages is not None:
            if self.cli_features_prefix is None:
                raise ValueError(f"cli_features_prefix is None. cli_features_packages={self.cli_features_packages}")
            if len(self.cli_features_prefix) != len(self.cli_features_packages):
                raise ValueError(f"cli_features_prefix is not match. cli_features_packages={self.cli_features_packages}, cli_features_prefix={self.cli_features_prefix}")
            for i, pn in enumerate(self.cli_features_packages):
                self.options.load_svcmd(pn, prefix=self.cli_features_prefix[i])
        self.options.load_features_file('cli', self.options.load_svcmd)

        # コマンド引数の生成
        opts = self.options.list_options()
        for opt in opts.values():
            default = opt["default"] if opt["default"] is not None and opt["default"] != "" else None
            if opt["action"] is None:
                parser.add_argument(*opt["opts"], help=opt["help"], type=opt["type"], default=default, choices=opt["choices"])
            else:
                parser.add_argument(*opt["opts"], help=opt["help"], default=default, action=opt["action"])

        argcomplete.autocomplete(parser)
        # mainメソッドの起動時引数がある場合は、その引数を解析する
        try:
            if args_list is not None:
                args = parser.parse_args(args=args_list)
            else:
                args = parser.parse_args()
        except argparse.ArgumentError as e:
            msg = {"error":f"ArgumentError: {e}"}
            common.print_format(msg, False, 0, None, False)
            return 1, msg, None
        # 起動時引数で指定されたオプションをファイルから読み込んだオプションで上書きする
        args_dict = vars(args)
        for key, val in file_dict.items():
            args_dict[key] = val
        # useoptオプションで指定されたオプションファイルを読み込む
        opt = common.loadopt(args.useopt)
        # 最終的に使用するオプションにマージする
        for key, val in args_dict.items():
            args_dict[key] = common.getopt(opt, key, preval=args_dict, withset=True)
        args = argparse.Namespace(**args_dict)

        tm = time.perf_counter()
        ret = {"success":f"Start command. {args}"}

        if args.saveopt:
            if args.useopt is None:
                msg = {"warn":f"Please specify the --useopt option."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
                return 1, msg, None
            common.saveopt(opt, args.useopt)
            ret = {"success":f"Save options file. {args.useopt}"}

        if args.version:
            v = self.ver.__logo__ + '\n' + self.ver.__description__
            common.print_format(v, False, tm, None, False)
            return 0, v, None

        if args.mode is None:
            msg = {"warn":f"mode is None. Please specify the --help option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, None

        common.mklogdir(args.data)
        common.copy_sample(args.data)
        common.copy_sample(Path.cwd())

        logger, _ = common.load_config(args.mode, debug=args.debug, data=args.data, webcall=webcall if args.cmd != 'webcap' else True, appid=self.ver.__appid__)
        if logger.level == logging.DEBUG:
            logger.debug(f"args.mode={args.mode}, args.cmd={args.cmd}")
            for m, mo in self.options._options["cmd"].items():
                if type(mo) is not dict: continue
                for c, co in mo.items():
                    if type(co) is not dict: continue
                    logger.debug(f"loaded features: mode={m}, cmd={c}, {co['feature']}")

        feature = self.options.get_cmd_attr(args.mode, args.cmd, 'feature')
        if feature is not None:
            status, ret, obj = feature.apprun(logger, args, tm)
            return status, ret, obj
        else:
            msg = {"warn":f"Unkown mode or cmd. mode={args.mode}, cmd={args.cmd}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, None
