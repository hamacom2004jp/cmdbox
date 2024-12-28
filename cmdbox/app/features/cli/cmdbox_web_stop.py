from cmdbox.app import common, web
from cmdbox.app.feature import Feature
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class WebStop(Feature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'web'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'stop'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="Webモードを停止します。",
            discription_en="Stop Web mode.",
            choice=[
                dict(opt="data", type="file", default=common.HOME_DIR / f'.{self.ver.__appid__}', required=False, multi=False, hide=False, choice=None,
                        discription_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                        discription_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choice=[True, False],
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                        discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type="int", default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                        discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                        discription_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
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
        w = web.Web(logger, Path(args.data), appcls=self.appcls, ver=self.ver)
        w.stop()
        msg = {"success":"web complate."}
        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        return 0, msg, w
