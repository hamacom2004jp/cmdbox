from cmdbox.app import common, edge, feature
from cmdbox.app.options import Options
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class EdgeStart(feature.UnsupportEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'edge'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'start'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True,
            discription_ja="端末モードを起動します。",
            discription_en="Start Edge mode.",
            choice=[
                dict(opt="data", type=Options.T_FILE, default=common.HOME_DIR / f".{self.ver.__appid__}", required=True, multi=False, hide=True, choice=None,
                     discription_ja=f"省略した時は f`$HONE/.{self.ver.__appid__}` を使用します。",
                     discription_en=f"When omitted, f`$HONE/.{self.ver.__appid__}` is used."),
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
        if args.data is None:
            args.data = common.HOME_DIR / f".{self.ver.__appid__}"
        app = edge.Edge(logger, args.data, self.appcls, self.ver)
        msg = app.start()

        msg = dict(success="edge complate.")
        common.print_format(msg, True, tm, None, False, pf=pf)
        return 0, msg, None

    def load_cmds(self, logger:logging.Logger, args:argparse.Namespace) -> Tuple[int, List[Dict[str, Any]]]:
        """
        コマンドファイルのタイトル一覧を取得する

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            status_code (int): ステータスコード
            List[Dict[str, Any]]: コマンドファイルのタイトル一覧
        """
        res = self.session.post(f"{args.endpoint}/gui/list_cmd", data="kwd=*", allow_redirects=False)
        if res.status_code != 200:
            return res.status_code, dict(warn=f"Access failed. status_code={res.status_code}")
        cmds = res.json()
        return 0, cmds

    def load_pipes(self, logger:logging.Logger, args:argparse.Namespace) -> Tuple[int, List[Dict[str, Any]]]:
        """
        パイプファイルのタイトル一覧を取得する

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            status_code (int): ステータスコード
            List[Dict[str, Any]]: コマンドファイルのタイトル一覧
        """
        res = self.session.post(f"{args.endpoint}/gui/list_pipe", data="kwd=*", allow_redirects=False)
        if res.status_code != 200:
            return res.status_code, dict(warn=f"Access failed. status_code={res.status_code}")
        pipes = res.json()
        return 0, pipes
    
