from cmdbox import version
from cmdbox.app import common, feature, options
from pathlib import Path
from typing import List
import argparse
import argcomplete
import logging
import time
import sys


def main(args_list:list=None):
    app = CmdBoxApp.getInstance(appcls=CmdBoxApp, ver=version)
    return app.main(args_list)[0]

class CmdBoxApp:
    _instance = None
    @staticmethod
    def getInstance(appcls=None, ver=version, cli_features_packages:List[str]=None, cli_features_prefix:List[str]=None):
        if CmdBoxApp._instance is None:
            CmdBoxApp._instance = CmdBoxApp(appcls=appcls, ver=ver, cli_features_packages=cli_features_packages, cli_features_prefix=cli_features_prefix)
        return CmdBoxApp._instance

    def __init__(self, appcls=None, ver=version, cli_features_packages:List[str]=None, cli_features_prefix:List[str]=None):
        """
        コンストラクタ

        Args:
            ver (version, optional): バージョンモジュール. Defaults to version.
            cli_package_name (str, optional): プラグインのパッケージ名. Defaults to None.
            cli_features_prefix (List[str], optional): プラグインのパッケージのモジュール名のプレフィックス. Defaults to None.
        """
        self.appcls = self.__class__ if appcls is None else appcls
        self.ver = ver
        self.options = options.Options.getInstance(self.appcls, self.ver)
        self.cli_features_packages = cli_features_packages
        self.cli_features_prefix = cli_features_prefix

    def main(self, args_list:list=None, file_dict:dict=dict(), webcall:bool=False):
        """
        コマンドライン引数を処理し、サーバーまたはクライアントを起動し、コマンドを実行する。
        """
        smaintime = time.perf_counter()
        parser = argparse.ArgumentParser(prog=self.ver.__appid__, description=self.ver.__logo__ + '\n\n' + self.ver.__description__,
                                         formatter_class=argparse.RawDescriptionHelpFormatter, exit_on_error=False)
        if args_list is not None and '--debug' in args_list:
            self.default_logger = common.default_logger(True, ver=self.ver, webcall=webcall)
        elif sys.argv is not None and '--debug' in sys.argv:
            self.default_logger = common.default_logger(True, ver=self.ver, webcall=webcall)
        else:
            self.default_logger = common.default_logger(False, ver=self.ver, webcall=webcall)

        # プラグイン読込み
        sfeatureloadtime = time.perf_counter()
        self.options.load_svcmd('cmdbox.app.features.cli', appcls=self.appcls, ver=self.ver, logger=self.default_logger)
        if self.cli_features_packages is not None:
            if self.cli_features_prefix is None:
                raise ValueError(f"cli_features_prefix is None. cli_features_packages={self.cli_features_packages}")
            if len(self.cli_features_prefix) != len(self.cli_features_packages):
                raise ValueError(f"cli_features_prefix is not match. cli_features_packages={self.cli_features_packages}, cli_features_prefix={self.cli_features_prefix}")
            for i, pn in enumerate(self.cli_features_packages):
                self.options.load_svcmd(pn, prefix=self.cli_features_prefix[i], appcls=self.appcls, ver=self.ver, logger=self.default_logger)
        self.options.load_features_file('cli', self.options.load_svcmd, self.appcls, self.ver, self.default_logger)
        efeatureloadtime = time.perf_counter()

        # コマンド引数の生成
        sargsparsetime = time.perf_counter()
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
            if args_list is not None and len(args_list) > 0:
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
        # featuresの初期値を適用する
        self.options.load_features_args(args_dict)
        args = argparse.Namespace(**args_dict)
        eargsparsetime = time.perf_counter()

        ret = {"success":f"Start command. {args}"}
        if args.saveopt:
            if args.useopt is None:
                msg = {"warn":f"Please specify the --useopt option."}
                common.print_format(msg, args.format, smaintime, args.output_json, args.output_json_append)
                return 1, msg, None
            common.saveopt(opt, args.useopt)
            ret = {"success":f"Save options file. {args.useopt}"}

        smakesampletime = time.perf_counter()
        common.mklogdir(args.data)
        common.copy_sample(args.data, ver=self.ver)
        common.copy_sample(Path.cwd(), ver=self.ver)
        emakesampletime = time.perf_counter()

        if args.version:
            v = self.ver.__logo__ + '\n' + self.ver.__description__
            common.print_format(v, False, smaintime, None, False)
            return 0, v, None

        if args.mode is None:
            msg = {"warn":f"mode is None. Please specify the --help option."}
            common.print_format(msg, args.format, smaintime, args.output_json, args.output_json_append)
            return 1, msg, None

        sloggerinittime = time.perf_counter()
        logger, _ = common.load_config(args.mode, debug=args.debug, data=args.data, webcall=webcall if args.cmd != 'webcap' else True, ver=self.ver)
        eloggerinittime = time.perf_counter()
        if logger.level == logging.DEBUG:
            logger.debug(f"args.mode={args.mode}, args.cmd={args.cmd}")

        #scmdexectime = time.perf_counter()
        feat = self.options.get_cmd_attr(args.mode, args.cmd, 'feature')
        if feat is not None or isinstance(feat, feature.Feature):
            pf = []
            pf.append(dict(key="app_featureload", val=f"{efeatureloadtime-sfeatureloadtime:.03f}s"))
            pf.append(dict(key="app_argsparse", val=f"{eargsparsetime-sargsparsetime:.03f}s"))
            pf.append(dict(key="app_makesample", val=f"{emakesampletime-smakesampletime:.03f}s"))
            pf.append(dict(key="app_loggerinit", val=f"{eloggerinittime-sloggerinittime:.03f}s"))
            status, ret, obj = feat.apprun(logger, args, smaintime, pf)
            return status, ret, obj
        else:
            msg = {"warn":f"Unkown mode or cmd. mode={args.mode}, cmd={args.cmd}"}
            common.print_format(msg, args.format, smaintime, args.output_json, args.output_json_append)
            return 1, msg, None

