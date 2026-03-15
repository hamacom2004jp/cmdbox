from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.options import Options
from importlib import resources
from pathlib import Path
from typing import Dict, Any, List
import argparse
import logging
import platform
import yaml


class CmdboxBase(feature.OneshotEdgeFeature):
    def __init__(self, appcls, ver, language:str=None):
        super().__init__(appcls, ver, language=language)

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True, use_agent=False,
            description_ja="-",
            description_en="-",
            choice=[
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

    def _load_base_compose(self) -> str:
        return resources.read_text(f'{self.ver.__appid__}.docker.cmdbox', 'docker-compose.yml')

    def _load_dockerfile(self, container:str) -> str:
        try:
            return resources.read_text(f'{self.ver.__appid__}.docker.{container}', 'Dockerfile')
        except:
            return resources.read_text(f'{version.__appid__}.docker.{container}', 'Dockerfile')

    def up(self, logger:logging.Logger, compose_path:str=None, container:str=None) -> Dict[str, Any]:
        """
        コンテナを起動します。

        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス
            container (str): コンテナ名

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Up server command is Unsupported in windows platform."}

            newenv = common.newenv(container, self.ver)
            app_path = f'{newenv["CWD"]}{self.ver.__appid__}/{container}'
            if Path(f'{app_path}/scripts/up.sh').exists():
                returncode, _, cmd = common.cmd(f'bash {app_path}/scripts/up.sh', logger=logger, newenv=newenv)
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

    def down(self, logger:logging.Logger, container:str=None) -> Dict[str, Any]:
        """
        コンテナを停止します。

        Args:
            logger (logging.Logger): ロガー
            container (str): コンテナ名

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Down server command is Unsupported in windows platform."}

            newenv = common.newenv(container, self.ver)
            app_path = f'{newenv["CWD"]}{self.ver.__appid__}/{container}'
            if Path(f'{app_path}/scripts/down.sh').exists():
                returncode, _, cmd = common.cmd(f'bash {app_path}/scripts/down.sh', logger=logger, newenv=newenv)
                if returncode != 0:
                    logger.error(f"Failed to down {container}. command: {cmd}")
                    return {"error": f"Failed to down {container}. command: {cmd}"}
                return {"success": f"Success to down {container}. cmd:{cmd}"}
            else:
                returncode, _, cmd = common.cmd(f"docker stop {container}", logger=logger, slise=-1)
                if returncode != 0:
                    logger.warning(f"Failed to stop {container}. cmd:{cmd}")
                    return {"error": f"Failed to stop {container}. cmd:{cmd}"}
                returncode, _, cmd = common.cmd(f"docker rm -f {container}", logger=logger, slise=-1)
                if returncode != 0:
                    logger.warning(f"Failed to rm {container}. cmd:{cmd}")
                    return {"error": f"Failed to rm {container}. cmd:{cmd}"}
                return {"success": f"Success to down {container}. cmd:{cmd}"}
        finally:
            common.set_debug(logger, False)

    def reboot(self, logger:logging.Logger, args:argparse.Namespace, container:str, tm:float=0.0, pf:List=[]) -> Dict[str, Any]:
        """
        コンテナを再起動します。

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List): 呼出元のパフォーマンス情報
        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            down_ret = self.down(logger, container)
            common.print_format(down_ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            if 'success' not in down_ret:
                return down_ret
            up_ret = self.up(logger, args.compose_path, container)
            common.print_format(up_ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            if 'success' not in up_ret:
                return up_ret
            return up_ret
        finally:
            common.set_debug(logger, False)

    def exec(self, logger:logging.Logger, compose_path:str=None, container:str=None, command:str=None) -> Dict[str, Any]:
        """
        cmdboxサーバーコンテナ内で任意のコマンドを実行します。

        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス
            container (str): コンテナ名
            command (str): 実行するコマンド

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Server exec command is Unsupported in windows platform."}

            newenv = common.newenv(container, self.ver)
            app_path = f'{newenv["CWD"]}{self.ver.__appid__}/{container}'
            if Path(f'{app_path}/scripts/exec.sh').exists():
                if not compose_path:
                    logger.warning("compose_path is specified but not used because down.sh exists.")
                returncode, _, cmd = common.cmd(f'bash {app_path}/scripts/exec.sh {command}', logger=logger, newenv=newenv)
                if returncode != 0:
                    logger.error(f"Failed to exec {container}. command: {cmd}")
                    return {"error": f"Failed to exec {container}. command: {cmd}"}
                return {"success": f"Success to exec {container}. cmd:{cmd}"}
            else:
                if not compose_path:
                    compose_path = 'docker-compose.yml'
                docker_compose_path = Path(compose_path)
                if not docker_compose_path.exists():
                    logger.error(f"compose_path file not found: {docker_compose_path}")
                    return {"error": f"compose_path file not found: {docker_compose_path}"}
                cmd = f'docker compose -f {docker_compose_path} exec {container} {command}'
                returncode, _, cmd = common.cmd(cmd, logger=logger, slise=-1)
                if returncode != 0:
                    logger.warning(f"Failed to exec {container}. cmd:{cmd}")
                    return {"error": f"Failed to exec {container}. cmd:{cmd}"}
                return {"success": f"Success to exec {container}. cmd:{cmd}"}
        finally:
            common.set_debug(logger, False)

    def logs(self, logger:logging.Logger, compose_path:str=None, container:str=None, follow:bool=False, number:int=20) -> Dict[str, Any]:
        """
        cmdboxサーバーのログを表示します。

        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス
            container (str): コンテナ名
            follow (bool): ログ出力をフォローするかどうか
            number (int): ログの最後から指定行数出力する

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Logs server command is Unsupported in windows platform."}
            newenv = common.newenv(container, self.ver)
            app_path = f'{newenv["CWD"]}{self.ver.__appid__}/{container}'
            if Path(f'{app_path}/scripts/logs.sh').exists():
                if not compose_path:
                    logger.warning("compose_path is specified but not used because logs.sh exists.")
                returncode, _, cmd = common.cmd(f'bash {app_path}/scripts/logs.sh', logger=logger, newenv=newenv)
                if returncode != 0:
                    logger.error(f"Failed to logs {container}. command: {cmd}")
                    return {"error": f"Failed to logs {container}. command: {cmd}"}
                return {"success": f"Success to logs {container}. cmd:{cmd}"}
            else:
                if not compose_path:
                    compose_path = 'docker-compose.yml'
                docker_compose_path = Path(compose_path)
                if not docker_compose_path.exists():
                    logger.error(f"compose_path file not found: {docker_compose_path}")
                    return {"error": f"compose_path file not found: {docker_compose_path}"}
                cmd = f'docker compose -f {docker_compose_path} logs {container} {"-f" if follow else ""} {f"-n {number}" if number > 0 else ""}'
                returncode, _, cmd = common.cmd(cmd, logger=logger, slise=-1)
                if returncode != 0:
                    logger.warning(f"Failed to logs {container}. cmd:{cmd}")
                    return {"error": f"Failed to logs {container}. cmd:{cmd}"}
                return {"success": f"Success to logs {container}. cmd:{cmd}"}
        finally:
            common.set_debug(logger, False)

    def uninstall(self, logger:logging.Logger, compose_path:str=None, container:str=None, install_tag:str="") -> Dict[str, Any]:
        """
        コンテナをアンインストールします。

        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス
            install_tag (str): インストールタグ

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Uninstall server command is Unsupported in windows platform."}

            self.down(logger, container)

            newenv = common.newenv(container, self.ver)
            app_path = f'{newenv["CWD"]}{self.ver.__appid__}/{container}'
            if Path(f'{app_path}/scripts/rmi.sh').exists():
                returncode, _, cmd = common.cmd(f'bash {app_path}/scripts/rmi.sh', logger=logger, newenv=newenv)
                if returncode != 0:
                    logger.error(f"Failed to uninstall {container}. command: {cmd}")
                    return {"error": f"Failed to uninstall {container}. command: {cmd}"}
            else:
                install_tag = f"_{install_tag}" if install_tag else ''
                cmd = f"docker rmi hamacom/{self.ver.__appid__}/{container}:{self.ver.__version__}{install_tag}"
                returncode, _, _cmd = common.cmd(cmd, logger=logger, slise=-1)
                if returncode != 0:
                    logger.warning(f"Failed to uninstall {container}. cmd:{_cmd}")
                    return {"error": f"Failed to uninstall {container}. cmd:{_cmd}"}

            if not compose_path:
                compose_path = 'docker-compose.yml'
            docker_compose_path = Path(compose_path)
            if not docker_compose_path.exists():
                logger.error(f"docker-compose.yml file not found: {docker_compose_path}")
                return {"error": f"docker-compose.yml file not found: {compose_path}"}

            with open(f'{docker_compose_path}', 'r', encoding='utf-8') as fp:
                comp = yaml.safe_load(fp)
            with open(f'{docker_compose_path}', 'w', encoding='utf-8') as fp:
                services:dict = comp['services']
                services.pop(container, None)
                yaml.dump(comp, fp)

            return {"success": f"Success to uninstall {container}. cmd:{_cmd}"}
        finally:
            common.set_debug(logger, False)
