from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.options import Options
from importlib import resources
from pathlib import Path
from typing import Dict, Any, List
import argparse
import logging
import platform
import shutil
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
            choice=[]
        )

    def _load_base_compose(self, container:str) -> str:
        return self._load_file(container, 'docker-compose.yml')

    def _load_dockerfile(self, container:str) -> str:
        return self._load_file(container, 'Dockerfile')

    def _load_file(self, container:str, file:str) -> str:
        try:
            return resources.read_text(f'{self.ver.__appid__}.docker.{container}', file)
        except:
            pass
        try:
            return resources.read_text(f'{self.ver.__appid__}.docker', file)
        except:
            pass
        try:
            return resources.read_text(f'{version.__appid__}.docker.{container}', file)
        except:
            pass
        try:
            return resources.read_text(f'{version.__appid__}.docker.{version.__appid__}', file)
        except:
            pass
        return resources.read_text(f'{version.__appid__}.docker', file)

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
        except:
            return {"success": f"Success to logs {container}."}
        finally:
            common.set_debug(logger, False)

    def uninstall(self, logger:logging.Logger, args:argparse.Namespace) -> Dict[str, Any]:
        """
        コンテナをアンインストールします。

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Uninstall server command is Unsupported in windows platform."}
            if not hasattr(args, 'container') or not args.container:
                return {"warn": "container is not specified."}

            self.down(logger, args.container)

            newenv = common.newenv(args.container, self.ver)
            app_path = f'{newenv["CWD"]}{self.ver.__appid__}/{args.container}'
            if Path(f'{app_path}/scripts/rmi.sh').exists():
                returncode, _, cmd = common.cmd(f'bash {app_path}/scripts/rmi.sh', logger=logger, newenv=newenv)
                if returncode != 0:
                    logger.error(f"Failed to uninstall {args.container}. command: {cmd}")
                    return {"error": f"Failed to uninstall {args.container}. command: {cmd}"}
            else:
                imgname = self.get_imgname(args.container, args)
                cmd = f"docker rmi {imgname}"
                returncode, _, _cmd = common.cmd(cmd, logger=logger, slise=-1)
                if returncode != 0:
                    logger.warning(f"Failed to uninstall {args.container}. cmd:{_cmd}")
                    return {"error": f"Failed to uninstall {args.container}. cmd:{_cmd}"}

            if not hasattr(args, 'compose_path') or not args.compose_path:
                args.compose_path = 'docker-compose.yml'
            docker_compose_path = Path(args.compose_path)
            if not docker_compose_path.exists():
                logger.error(f"docker-compose.yml file not found: {docker_compose_path}")
                return {"error": f"docker-compose.yml file not found: {args.compose_path}"}

            with open(f'{docker_compose_path}', 'r', encoding='utf-8') as fp:
                comp = yaml.safe_load(fp)
            with open(f'{docker_compose_path}', 'w', encoding='utf-8') as fp:
                services:dict = comp['services']
                services.pop(args.container, None)
                yaml.dump(comp, fp)

            return {"success": f"Success to uninstall {args.container}. cmd:{_cmd}"}
        finally:
            common.set_debug(logger, False)

    def save(self, logger:logging.Logger, compose_path:str=None, container:str=None, install_tag:str=None, file:str=None) -> Dict[str, Any]:
        """
        cmdboxサーバーのイメージをtar形式で保存します。

        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス
            container (str): コンテナ名
            install_tag (str): インストールタグ
            file (str): 保存先ファイルパス

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Save server command is Unsupported in windows platform."}
            newenv = common.newenv(container, self.ver)
            app_path = f'{newenv["CWD"]}{self.ver.__appid__}/{container}'
            if Path(f'{app_path}/scripts/save.sh').exists():
                if not compose_path:
                    logger.warning("compose_path is specified but not used because save.sh exists.")
                returncode, _, cmd = common.cmd(f'bash {app_path}/scripts/save.sh', logger=logger, newenv=newenv)
                if returncode != 0:
                    logger.error(f"Failed to save {container}. command: {cmd}")
                    return {"error": f"Failed to save {container}. command: {cmd}"}
                return {"success": f"Success to save {container}. cmd:{cmd}"}
            else:
                if not compose_path:
                    compose_path = 'docker-compose.yml'
                docker_compose_path = Path(compose_path)
                if not docker_compose_path.exists():
                    logger.error(f"compose_path file not found: {docker_compose_path}")
                    return {"error": f"compose_path file not found: {docker_compose_path}"}
                with open(docker_compose_path, 'r', encoding='utf-8') as fp:
                    comp = yaml.safe_load(fp)
                    services:dict = comp.get('services', {})
                    if container not in services:
                        logger.error(f"Container {container} not found in compose file.")
                        return {"error": f"Container {container} not found in compose file."}
                    imgname = services[container].get('image', None)
                    if not imgname:
                        logger.error(f"Image name for container {container} not found in compose file.")
                        return {"error": f"Image name for container {container} not found in compose file."}
                    file = file if file else f'{container}_{self.ver.__version__}{f"_{install_tag}" if install_tag else ""}.tar.gz'
                    cmd = f'docker save {imgname} | gzip > {file}'
                    returncode, _, cmd = common.cmd(cmd, logger=logger, slise=-1)
                    if returncode != 0:
                        logger.warning(f"Failed to save {container}. cmd:{cmd}")
                        return {"error": f"Failed to save {container}. cmd:{cmd}"}
                    return {"success": f"Success to save {container}. cmd:{cmd}"}
        finally:
            common.set_debug(logger, False)

    def load(self, logger:logging.Logger, compose_path:str=None, container:str=None, install_tag:str=None, file:str=None) -> Dict[str, Any]:
        """
        tar形式で保存されたcmdboxサーバーのイメージをロードします。

        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス
            container (str): コンテナ名
            install_tag (str): インストールタグ
            file (str): ロードするtarファイルパス

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Load server command is Unsupported in windows platform."}
            newenv = common.newenv(container, self.ver)
            app_path = f'{newenv["CWD"]}{self.ver.__appid__}/{container}'
            if Path(f'{app_path}/scripts/load.sh').exists():
                if not compose_path:
                    logger.warning("compose_path is specified but not used because load.sh exists.")
                returncode, _, cmd = common.cmd(f'bash {app_path}/scripts/load.sh', logger=logger, newenv=newenv)
                if returncode != 0:
                    logger.error(f"Failed to load {container}. command: {cmd}")
                    return {"error": f"Failed to load {container}. command: {cmd}"}
                return {"success": f"Success to load {container}. cmd:{cmd}"}
            else:
                if not compose_path:
                    compose_path = 'docker-compose.yml'
                docker_compose_path = Path(compose_path)
                if not docker_compose_path.exists():
                    logger.error(f"compose_path file not found: {docker_compose_path}")
                    return {"error": f"compose_path file not found: {docker_compose_path}"}
                with open(docker_compose_path, 'r', encoding='utf-8') as fp:
                    comp = yaml.safe_load(fp)
                    services:dict = comp.get('services', {})
                    if container not in services:
                        logger.error(f"Container {container} not found in compose file.")
                        return {"error": f"Container {container} not found in compose file."}
                    imgname = services[container].get('image', None)
                    if not imgname:
                        logger.error(f"Image name for container {container} not found in compose file.")
                        return {"error": f"Image name for container {container} not found in compose file."}

                    file = file if file else f'{container}_{self.ver.__version__}{f"_{install_tag}" if install_tag else ""}.tar.gz'
                    cmd = f'docker load -i {file}'
                    returncode, _, cmd = common.cmd(cmd, logger=logger, slise=-1)
                    if returncode != 0:
                        logger.warning(f"Failed to load {container}. cmd:{cmd}")
                        return {"error": f"Failed to load {container}. cmd:{cmd}"}
                    return {"success": f"Success to load {container}. cmd:{cmd}"}
        finally:
            common.set_debug(logger, False)

    def copy_scripts(self, logger:logging.Logger, container:str) -> Path:
        """
        モジュール内のスクリプトをホストにコピーします。
        Args:
            logger (logging.Logger): ロガー
            container (str): コンテナ名
        Returns:
            Path: コピー先のパス
        """
        start_sh_hst = Path(self.ver.__appid__) / container / 'scripts'
        start_sh_hst.parent.mkdir(parents=True, exist_ok=True)
        scripts_src = Path(self.ver.__file__).parent / 'docker' / container / 'scripts'
        if not scripts_src.exists():
            scripts_src = Path(self.ver.__file__).parent / 'docker' / 'scripts'
        if not scripts_src.exists():
            scripts_src = Path(version.__file__).parent / 'docker' / container / 'scripts'
        if not scripts_src.exists():
            scripts_src = Path(version.__file__).parent / 'docker' / version.__appid__ / 'scripts'
        if not scripts_src.exists():
            scripts_src = Path(version.__file__).parent / 'docker' / 'scripts'
        try:
            shutil.copytree(scripts_src, start_sh_hst, dirs_exist_ok=True)
        except:
            pass
        return start_sh_hst


    def make_compose_default(self, logger:logging.Logger, compose_path:str, container:str, imgname:str) -> tuple[Dict[str, Any], Path]:
        """
        デフォルトのdocker-compose.ymlを作成します。
        
        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス
            container (str): コンテナ名
            imgname (str): イメージ名

        Returns:
            dict: composeファイルの内容
            Path: compose_path
        """
        if not compose_path:
            compose_path = 'docker-compose.yml'
        docker_compose_path = Path(compose_path)
        base_comp_str = None
        try:
            base_comp_str = self._load_base_compose(container)
            base_comp = yaml.safe_load(base_comp_str)
        except:
            pass
        if not docker_compose_path.exists():
            with open(docker_compose_path, 'w', encoding='utf-8') as fp:
                if base_comp_str:
                    fp.write(base_comp_str)
                else:
                    fp.write(yaml.safe_dump(dict(version='3', services={})))
        with open(docker_compose_path, 'r', encoding='utf-8') as fp:
            comp = yaml.safe_load(fp)

            services = comp['services']
            sv = base_comp.get('services', None) if base_comp else None
            if sv:
                for k, v in sv.items():
                    services[k] = v
            else:
                services[container] = dict(
                    image=imgname,
                    container_name=container,
                    environment=dict(
                        APPID='${APPID:-'+self.ver.__appid__+'}',
                        TZ='Asia/Tokyo',
                    ),
                    restart='always',
                    working_dir=f'/opt/{self.ver.__appid__}/{container}',
                )
        return comp, docker_compose_path

    def make_compose_redis(self, logger:logging.Logger, compose_path:str, container:str, imgname:str) -> tuple[Dict[str, Any], Path]:
        """
        redis用のdocker-compose.ymlを作成します。
        
        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス
            container (str): コンテナ名
            imgname (str): イメージ名

        Returns:
            dict: composeファイルの内容
            Path: compose_path
        """
        if not compose_path:
            compose_path = 'docker-compose.yml'
        docker_compose_path = Path(compose_path)
        if not docker_compose_path.exists():
            with open(docker_compose_path, 'w', encoding='utf-8') as fp:
                fp.write(self._load_base_compose(container))
        with open(docker_compose_path, 'r', encoding='utf-8') as fp:
            comp = yaml.safe_load(fp)

            services = comp['services']
            services[container] = dict(
                image=imgname,
                container_name=container,
                environment=dict(
                    APPID='${APPID:-'+self.ver.__appid__+'}',
                    TZ='Asia/Tokyo',
                    REDIS_PORT=6379,
                    REDIS_PASSWORD='password',
                ),
                ports=['6379:6379'],
                restart='always',
                working_dir=f'/opt/{self.ver.__appid__}/{container}',
            )

        return comp, docker_compose_path

    def make_compose_pgsql(self, logger:logging.Logger, compose_path:str, container:str, imgname:str, install_pgsqlver:str) -> tuple[Dict[str, Any], Path]:
        """
        pgsql用のdocker-compose.ymlを作成します。
        
        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス
            container (str): コンテナ名
            imgname (str): イメージ名
            install_pgsqlver (str): インストールするPostgreSQLのバージョン

        Returns:
            dict: composeファイルの内容
            Path: compose_path
        """
        if not compose_path:
            compose_path = 'docker-compose.yml'
        docker_compose_path = Path(compose_path)
        if not docker_compose_path.exists():
            with open(docker_compose_path, 'w', encoding='utf-8') as fp:
                fp.write(self._load_base_compose(container))
        with open(docker_compose_path, 'r', encoding='utf-8') as fp:
            comp = yaml.safe_load(fp)
        with open(docker_compose_path, 'w', encoding='utf-8') as fp:
            dbname = 'pgsql'
            services = comp['services']
            services[container] = dict(
                image=imgname,
                container_name=container,
                environment=dict(
                    APPID='${APPID:-'+self.ver.__appid__+'}',
                    POSTGRES_USER=dbname,
                    POSTGRES_PASSWORD=dbname,
                    POSTGRES_DB=dbname,
                    POSTGRES_HOST_AUTH_METHOD='trust',
                    POSTGRES_PORT='5432',
                    #PGDATA='/var/lib/postgresql/data/pgdata',
                ),
                ports=['5432:5432'],
                restart='always',
                working_dir=f'/opt/{self.ver.__appid__}/{container}',
                volumes=[
                    f'./{self.ver.__appid__}/{container}:/opt/{self.ver.__appid__}/{container}',
                    f'./{self.ver.__appid__}/{container}/data:/var/lib/postgresql/{install_pgsqlver}/docker',
                    #f'./{self.ver.__appid__}/{container}:/var/lib/postgresql/data',
                ],
            )
        return comp, docker_compose_path

    def make_compose_server(self, logger:logging.Logger, compose_path:str, container:str,
                            imgname:str, user:str, data:str, start_sh_tgt:str, install_use_gpu:bool,
                            install_tag:str, language:str) -> tuple[Dict[str, Any], Path]:
        """
        server用のdocker-compose.ymlを作成します。
        
        Args:
            logger (logging.Logger): ロガー
            compose_path (str): docker-compose.ymlファイルパス
            container (str): コンテナ名
            imgname (str): イメージ名
            user (str): ホストのユーザー名
            data (str): ホストのデータ保存先ディレクトリパス
            start_sh_tgt (str): コンテナ内のstart.shのパス
            install_use_gpu (bool): GPUを使用してインストールするかどうか
            install_tag (str): インストールタグ
            language (str): 言語

        Returns:
            dict: composeファイルの内容
            Path: compose_path
        """
        if not compose_path:
            compose_path = 'docker-compose.yml'
        docker_compose_path = Path(compose_path)
        if not docker_compose_path.exists():
            with open(docker_compose_path, 'w', encoding='utf-8') as fp:
                fp.write(self._load_base_compose(container))
        with open(docker_compose_path, 'r', encoding='utf-8') as fp:
            comp = yaml.safe_load(fp)

            services = comp['services']
            services[container] = dict(
                image=imgname,
                container_name=container,
                environment=dict(
                    TZ='Asia/Tokyo',
                    CMDBOX_DEBUG=False,
                    APPID='${APPID:-'+self.ver.__appid__+'}',
                    REDIS_HOST='${REDIS_HOST:-redis}',
                    REDIS_PORT='${REDIS_PORT:-6379}',
                    REDIS_PASSWORD='${REDIS_PASSWORD:-password}',
                    SVNAME='${SVNAME:-'+self.ver.__appid__+install_tag+'}',
                    LISTEN_PORT='${LISTEN_PORT:-8081}',
                    MCPSV_LISTEN_PORT='${MCPSV_LISTEN_PORT:-8091}',
                    A2ASV_LISTEN_PORT='${A2ASV_LISTEN_PORT:-8071}',
                    SSL_LISTEN_PORT='${SSL_LISTEN_PORT:-8443}',
                    SSL_MCPSV_LISTEN_PORT='${SSL_MCPSV_LISTEN_PORT:-8453}',
                    SSL_A2ASV_LISTEN_PORT='${SSL_A2ASV_LISTEN_PORT:-8433}',
                    SVCOUNT='${SVCOUNT:-2}',
                    LANGUAGE='${LANGUAGE:-'+(language if language else 'ja_JP')+'}'
                ),
                user=user,
                ports=['${LISTEN_PORT:-8081}:${LISTEN_PORT:-8081}',
                    '${MCPSV_LISTEN_PORT:-8091}:${MCPSV_LISTEN_PORT:-8091}',
                    '${A2ASV_LISTEN_PORT:-8071}:${A2ASV_LISTEN_PORT:-8071}',
                    '${SSL_LISTEN_PORT:-8443}:${SSL_LISTEN_PORT:-8443}',
                    '${SSL_MCPSV_LISTEN_PORT:-8453}:${SSL_MCPSV_LISTEN_PORT:-8453}',
                    '${SSL_A2ASV_LISTEN_PORT:-8433}:${SSL_A2ASV_LISTEN_PORT:-8433}'],
                privileged=True,
                restart='always',
                working_dir=f'/opt/{self.ver.__appid__}',
                #devices=['/dev/bus/usb:/dev/bus/usb'],
                volumes=[
                    f'{data}:/home/{user}/.{self.ver.__appid__}',
                    f'/home/{user}:/home/{user}',
                    f'./{self.ver.__appid__}:/opt/{self.ver.__appid__}'
                ],
                command=f'bash {start_sh_tgt}/start.sh'
            )
            if install_use_gpu:
                services[f'{self.ver.__appid__}{install_tag}']['deploy'] = dict(
                    resources=dict(reservations=dict(devices=[dict(
                        driver='nvidia',
                        count=1,
                        capabilities=['gpu']
                    )]))
                )
        return comp, docker_compose_path

    def get_imgname(self, container:str, args:argparse.Namespace) -> str:
        """
        イメージ名を取得します

        Args:
            container (str): コンテナ名
            args (argparse.Namespace): 引数

        Returns:
            str: イメージ名
        """
        imgname = f"hamacom/{self.ver.__appid__}/{container}:{self.ver.__version__}{f'_{args.install_tag}' if args.install_tag else ''}"
        return imgname
