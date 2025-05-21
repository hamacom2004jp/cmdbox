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
        opt = super().get_option()
        opt['discription_ja'] = "GUIモードを停止します。"
        opt['discription_en'] = "Stop GUI mode."
        return opt
