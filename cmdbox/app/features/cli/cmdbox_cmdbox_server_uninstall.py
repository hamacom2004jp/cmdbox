from cmdbox.app import common, feature
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import platform
import yaml


class CmdboxServerUninstall(feature.OneshotNotifyEdgeFeature):
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
        return 'server_uninstall'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True,
            description_ja="cmdboxサーバーをアンインストールします。",
            description_en="Uninstalls the cmdbox server.",
            choice=[
                dict(opt="install_tag", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="指定すると作成するdockerイメージのタグ名に追記出来ます。",
                     description_en="If specified, you can add to the tag name of the docker image to create."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="処理結果jsonファイルを追記保存します。",
                     description_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
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
        ret = self.server_uninstall(logger, install_tag=args.install_tag)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def server_uninstall(self, logger:logging.Logger, install_tag:str=None):
        """
        cmdboxサーバーをアンインストールします。

        Args:
            logger (logging.Logger): ロガー
            install_tag (str): インストールタグ

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Uninstall server command is Unsupported in windows platform."}
            install_tag = f"_{install_tag}" if install_tag is not None else ''
            cmd = f"docker compose down {self.ver.__appid__}{install_tag}"
            returncode, _, _cmd = common.cmd(f"{cmd}", logger, slise=-1)
            if returncode != 0:
                logger.warning(f"Failed to down {self.ver.__appid__}-server. cmd:{_cmd}")
                return {"error": f"Failed to down {self.ver.__appid__}-server. cmd:{_cmd}"}
            cmd = f"docker rmi hamacom/{self.ver.__appid__}:{self.ver.__version__}{install_tag}"
            returncode, _, _cmd = common.cmd(f"{cmd}", logger, slise=-1)
            if returncode != 0:
                logger.warning(f"Failed to uninstall {self.ver.__appid__}-server. cmd:{_cmd}")
                return {"error": f"Failed to uninstall {self.ver.__appid__}-server. cmd:{_cmd}"}

            docker_compose_path = Path('docker-compose.yml')
            if docker_compose_path.exists():
                with open(f'docker-compose.yml', 'r+', encoding='utf-8') as fp:
                    comp = yaml.safe_load(fp)
                    services:dict = comp['services']
                    services.pop(f'{self.ver.__appid__}{install_tag}', None)
                    fp.seek(0)
                    yaml.dump(comp, fp)
                    fp.truncate()

            return {"success": f"Success to uninstall {self.ver.__appid__}-server. cmd:{_cmd}"}
        finally:
            common.set_debug(logger, False)
