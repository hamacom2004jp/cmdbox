from cmdbox.app import common, feature
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import platform


class CmdboxServerUp(feature.OneshotNotifyEdgeFeature):
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
        return 'server_up'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True,
            description_ja="cmdboxサーバーを起動します。",
            description_en="Starts the cmdbox server.",
            choice=[
                dict(opt="compose_path", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                     description_ja="`docker-compose.yml` ファイルを指定します。",
                     description_en="Specify the `docker-compose.yml` file."),
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
        ret = self.server_up(logger, args.compose_path)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def server_up(self, logger:logging.Logger, compose_path:str=None) -> Dict[str, Any]:
        """
        cmdboxサーバーを起動します。

        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Up server command is Unsupported in windows platform."}

            container = self.ver.__appid__
            newenv = common.newenv(container, self.ver)
            if Path(f'{newenv["CWD"]}{container}/scripts/up.sh').exists():
                if not compose_path:
                    logger.warning("compose_path is specified but not used because up.sh exists.")
                returncode, _, cmd = common.cmd(f'bash {newenv["CWD"]}{container}/scripts/up.sh', logger=logger, newenv=newenv)
                if returncode != 0:
                    logger.error(f"Failed to up {container}. command: {cmd}")
                    return {"error": f"Failed to up {container}. command: {cmd}"}
                return {"success": f"Success to up {container}. cmd:{cmd}"}
            else:
                if not compose_path:
                    compose_path = 'docker-compose.yml'
                docker_compose_path = Path(compose_path)
                if not docker_compose_path.exists():
                    logger.error(f"compose_path file not found: {docker_compose_path}")
                    return {"error": f"compose_path file not found: {docker_compose_path}"}
                returncode, _, cmd = common.cmd(f"docker compose -f {docker_compose_path} up -d {container}", logger=logger, slise=-1)
                if returncode != 0:
                    logger.warning(f"Failed to up {container}. cmd:{cmd}")
                    return {"error": f"Failed to up {container}. cmd:{cmd}"}
                return {"success": f"Success to up {container}. cmd:{cmd}"}
        finally:
            common.set_debug(logger, False)
