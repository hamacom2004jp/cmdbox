from cmdbox.app import common
from cmdbox.app.commons import validator
from cmdbox.app.features.cli.cmdbox import cmdbox_base
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import getpass
import logging
import platform
import re
import shutil
import yaml


class CmdboxServerLoad(cmdbox_base.CmdboxBase, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'cmdbox'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'server_load'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True, use_agent=False,
            description_ja="cmdboxのコンテナイメージをロードします。",
            description_en="Load the cmdbox container image.",
            choice=[
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="image_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="読込元イメージファイルを指定します。",
                     description_en="Specify the source image file."),
                dict(opt="install_tag", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="指定すると作成するdockerイメージのタグ名に追記出来ます。",
                     description_en="If specified, you can add to the tag name of the docker image to create."),
                dict(opt="install_use_gpu", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="GPUを使用するモジュール構成でインストールします。",
                     description_en="Install with a module configuration that uses the GPU."),
                dict(opt="compose_path", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                     description_ja="`docker-compose.yml` ファイルを指定します。",
                     description_en="Specify the `docker-compose.yml` file."),
            ]
        )

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
        st, msg, obj = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, obj

        if platform.system() == 'Windows':
            msg = dict(warn=f"Load command is Unsupported in windows platform.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        try:
            container = args.container if hasattr(args, 'container') and args.container else self.ver.__appid__
            user = getpass.getuser()
            if re.match(r'^[0-9]', user):
                user = f'_{user}' # ユーザー名が数字始まりの場合、先頭にアンダースコアを付与
            start_sh_hst = self.copy_scripts(logger, container)
            start_sh_tgt = f'/opt/{self.ver.__appid__}/{container}/scripts'
            install_tag = f"_{args.install_tag}" if hasattr(args, 'install_tag') and args.install_tag else ''
            imgname = self.get_imgname(container, args)
            comp, docker_compose_path = self.make_compose_server(logger, args.compose_path, container, imgname, user, args.data,
                                                                 start_sh_tgt, args.install_use_gpu, install_tag, args.language)
            with open(docker_compose_path, 'w', encoding='utf-8') as fp:
                yaml.dump(comp, fp)
            ret = self.load(logger, args.compose_path, container, install_tag, args.image_file)
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            if 'success' not in ret:
                return self.RESP_WARN, ret, None
            return self.RESP_SUCCESS, ret, None
        except Exception as e:
            logger.warning("An error occurred while executing the load command.", exc_info=True)
            msg = dict(WARN=str(e))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
