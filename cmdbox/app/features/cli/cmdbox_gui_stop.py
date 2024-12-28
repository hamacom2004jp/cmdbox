from cmdbox.app import common
from cmdbox.app.features.cli import cmdbox_web_stop
from typing import List, Union


class GuiStop(cmdbox_web_stop.WebStop):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'gui'

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
            discription_ja="GUIモードを停止します。",
            discription_en="Stop GUI mode.",
            choice=[
                dict(opt="data", type="file", default=common.HOME_DIR / f".{self.ver.__appid__}", required=False, multi=False, hide=False, choice=None,
                     discription_ja="省略した時は f`$HONE/.{version.__appid__}` を使用します。",
                     discription_en="When omitted, f`$HONE/.{version.__appid__}` is used."),
                dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type="int", default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     discription_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )
