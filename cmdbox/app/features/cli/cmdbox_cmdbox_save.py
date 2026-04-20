from cmdbox.app import common
from cmdbox.app.commons import validator
from cmdbox.app.features.cli.cmdbox import cmdbox_base
from cmdbox.app.options import Options
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class CmdboxSave(cmdbox_base.CmdboxBase, validator.Validator):
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
        return 'save'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['description_ja'] = "コンテナイメージを保存します。"
        opt['description_en'] = "Saves the container image."
        opt['choice'] = [
            dict(short="C", opt="container", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                description_ja="コンテナ名を指定します。",
                description_en="Specify the container name."),
            dict(opt="image_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="out",
                description_ja="保存先イメージファイルを指定します。",
                description_en="Specify the destination image file."),
            dict(opt="install_tag", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                description_ja="指定すると作成するdockerイメージのタグ名に追記出来ます。",
                description_en="If specified, you can add to the tag name of the docker image to create."),
            dict(opt="compose_path", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                description_ja="`docker-compose.yml` ファイルを指定します。",
                description_en="Specify the `docker-compose.yml` file."),
        ]
        return opt

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

        ret = self.save(logger, args.compose_path, args.container, args.install_tag, args.image_file)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None
