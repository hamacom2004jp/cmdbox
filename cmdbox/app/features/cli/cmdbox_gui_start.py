from cmdbox.app.features.cli import cmdbox_web_start
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class GuiStart(cmdbox_web_start.WebStart):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'gui'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['use_agent'] = False
        opt['discription_ja'] = "GUIモードを起動します。"
        opt['discription_en'] = "Start GUI mode."
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
        args.gui_mode = True
        return super().apprun(logger, args, tm, pf)
