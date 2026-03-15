from cmdbox.app import common
from cmdbox.app.features.cli.cmdbox import cmdbox_base
from cmdbox.app.options import Options
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class CmdboxDown(cmdbox_base.CmdboxBase):
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
        return 'down'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['description_ja'] = "コンテナを停止します。"
        opt['description_en'] = "Stops the container."
        opt['choice'] = [
            dict(short="C", opt="container", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                description_ja="コンテナ名を指定します。",
                description_en="Specify the container name."),
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
        ret = self.down(logger, args.container)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None
