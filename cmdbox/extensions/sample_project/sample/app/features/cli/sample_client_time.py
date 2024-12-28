from cmdbox.app import common, feature
from typing import Dict, Any, Tuple, Union, List
import argparse
import datetime
import logging


class ClientTime(feature.Feature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return "client"

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'time'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_FALSE,
            discription_ja="クライアント側の現在時刻を表示します。",
            discription_en="Displays the current time at the client side.",
            choice=[
                dict(opt="timedelta", type="int", default=9, required=False, multi=False, hide=False, choice=None,
                        discription_ja="時差の時間数を指定します。",
                        discription_en="Specify the number of hours of time difference."),
            ])

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
        tz = datetime.timezone(datetime.timedelta(hours=args.timedelta))
        dt = datetime.datetime.now(tz)
        ret = dict(success=dict(data=dt.strftime('%Y-%m-%d %H:%M:%S')))
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return 1, ret, None
        return 0, ret, None
