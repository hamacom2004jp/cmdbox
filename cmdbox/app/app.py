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
    app = CmdBoxApp()
    return app.main(args_list)[0]

class CmdBoxApp:
    def __init__(self, appid:str=version.__appid__, description:str=None, cli_features_packages:List[str]=None):
        """
        コンストラクタ

        Args:
            appid (str, optional): アプリケーションID. Defaults to version.__appid__.
            description (str, optional): アプリケーションの説明. Defaults to None.
            cli_package_name (str, optional): プラグインのパッケージ名. Defaults to None.
        """
        self.options = options.Options.getInstance()
        self.appid = appid
        self.description = description
        self.cli_features_packages = cli_features_packages

    def main(self, args_list:list=None, file_dict:dict=dict(), webcall:bool=False):
        """
        コマンドライン引数を処理し、サーバーまたはクライアントを起動し、コマンドを実行する。
        """
        parser = argparse.ArgumentParser(prog=self.appid, description=self.description, exit_on_error=False)

        # プラグイン読込み
        self.options.load_svcmd('cmdbox.app.features.cli')
        if self.cli_features_packages is not None:
            for cli_features_package in self.cli_features_packages:
                self.options.load_svcmd(cli_features_package)
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
            v = version.__logo__ + '\n' + version.__description__
            common.print_format(v, False, tm, None, False)
            return 0, v, None

        if args.mode is None:
            msg = {"warn":f"mode is None. Please specify the --help option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append)
            return 1, msg, None

        common.mklogdir(args.data)
        common.copy_sample(args.data)
        common.copy_sample(Path.cwd())

        logger, _ = common.load_config(args.mode, debug=args.debug, data=args.data, webcall=webcall if args.cmd != 'webcap' else True)
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
