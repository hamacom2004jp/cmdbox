from cmdbox import version
from cmdbox.app import common
from importlib import resources
from pathlib import Path
import getpass
import logging
import platform
import re
import shutil
import yaml


class Install(object):
    def __init__(self, logger:logging.Logger, appcls=None, ver=version):
        self.logger = logger
        self.appcls = appcls
        self.ver = ver
        common.set_debug(self.logger, True)

    def redis_install(self):
        if platform.system() == 'Windows':
            return {"warn": f"install redis command is Unsupported in windows platform."}
        cmd = f"docker pull ubuntu/redis:latest"
        returncode, _, _cmd = common.cmd(f"{cmd}", self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install redis-server. cmd:{_cmd}")
            return {"error": f"Failed to install redis-server. cmd:{_cmd}"}
        return {"success": f"Success to install redis-server. cmd:{_cmd}"}

    def server_install(self, data:Path, install_cmdbox_tgt:str='cmdbox', install_from:str=None,
                       install_no_python:bool=False, install_compile_python:bool=False,
                       install_tag:str=None, install_use_gpu:bool=False,
                       tts_engine:str=None, voicevox_ver:str=None, voicevox_whl:str=None):
        """
        cmdboxが含まれるdockerイメージをインストールします。

        Args:
            data (Path): cmdbox-serverのデータディレクトリ
            install_cmdbox_tgt (str): cmdboxのインストール元
            install_from (str): インストール元dockerイメージ
            install_no_python (bool): pythonをインストールしない
            install_compile_python (bool): pythonをコンパイルしてインストール
            install_tag (str): インストールタグ
            install_use_gpu (bool): GPUを使用するモジュール構成でインストールします。
            tts_engine (str): TTSエンジンの指定
            voicevox_ver (str): VoiceVoxのバージョン
            voicevox_whl (str): VoiceVoxのwhlファイルの名前

        Returns:
            dict: 処理結果
        """
        if platform.system() == 'Windows':
            return {"warn": f"Build server command is Unsupported in windows platform."}
        user = getpass.getuser()
        if re.match(r'^[0-9]', user):
            user = f'_{user}' # ユーザー名が数字始まりの場合、先頭にアンダースコアを付与
        install_tag = f"_{install_tag}" if install_tag is not None else ''
        with open('Dockerfile', 'w', encoding='utf-8') as fp:
            text = resources.read_text(f'{self.ver.__appid__}.docker', 'Dockerfile')
            # cmdboxのインストール設定
            wheel_cmdbox = Path(install_cmdbox_tgt)
            if wheel_cmdbox.exists() and wheel_cmdbox.suffix == '.whl':
                shutil.copy(wheel_cmdbox, Path('.').resolve() / wheel_cmdbox.name)
                install_cmdbox_tgt = f'/home/{user}/{wheel_cmdbox.name}'
                text = text.replace('#{COPY_CMDBOX}', f'COPY {wheel_cmdbox.name} {install_cmdbox_tgt}')
            else:
                text = text.replace('#{COPY_CMDBOX}', '')

            start_sh_src = Path(__file__).parent.parent / 'docker' / 'scripts'
            start_sh_tgt = f'/opt/{self.ver.__appid__}/scripts'
            start_sh_hst = Path(self.ver.__appid__) / 'scripts'
            start_sh_hst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(start_sh_src, start_sh_hst, dirs_exist_ok=True)
            text = text.replace('#{COPY_CMDBOX_START}', f'RUN mkdir -p {start_sh_tgt}\nCOPY {start_sh_hst} {start_sh_tgt}')

            base_image = 'python:3.11.9-slim' #'python:3.8.18-slim'
            if install_use_gpu:
                #base_image = 'nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04'
                #base_image = 'pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime'
                #base_image = 'pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime'
                base_image = 'pytorch/pytorch:2.4.0-cuda12.1-cudnn9-runtime'
            if install_from is not None and install_from != '':
                base_image = install_from
            text = text.replace('#{FROM}', f'FROM {base_image}')
            text = text.replace('${MKUSER}', user)

            if install_compile_python:
                install_python = f'RUN apt-get update && apt-get install -y build-essential libbz2-dev libdb-dev libreadline-dev libffi-dev libgdbm-dev liblzma-dev ' + \
                                 f'libncursesw5-dev libsqlite3-dev libssl-dev zlib1g-dev uuid-dev tk-dev wget\n' + \
                                 f'RUN wget https://www.python.org/ftp/python/3.11.11/Python-3.11.11.tar.xz\n' + \
                                 f'RUN tar xJf Python-3.11.11.tar.xz && cd Python-3.11.11 && ./configure && make && make install\n' + \
                                 f'RUN update-alternatives --install /usr/bin/python python /usr/local/bin/python3.11 1'
                text = text.replace('#{INSTALL_PYTHON}', install_python)
            elif not install_no_python:
                text = text.replace('#{INSTALL_PYTHON}', '')
            else:
                text = text.replace('#{INSTALL_PYTHON}', '')
            install_voicevox = ''
            if tts_engine is not None and tts_engine.lower() == 'voicevox':
                install_voicevox = f'RUN pip install https://github.com/VOICEVOX/voicevox_core/releases/download/{voicevox_ver}/{voicevox_whl}'
            text = text.replace('#{INSTALL_TAG}', install_tag)
            text = text.replace('#{INSTALL_CMDBOX}', install_cmdbox_tgt)
            text = text.replace('#{INSTALL_VOICEVOX}', install_voicevox)
            fp.write(text)
        docker_compose_path = Path('docker-compose.yml')
        if not docker_compose_path.exists():
            with open(docker_compose_path, 'w', encoding='utf-8') as fp:
                text = resources.read_text(f'{self.ver.__appid__}.docker', 'docker-compose.yml')
                fp.write(text)
        with open(f'docker-compose.yml', 'r+', encoding='utf-8') as fp:
            comp = yaml.safe_load(fp)
            services = comp['services']
            services[f'{self.ver.__appid__}{install_tag}'] = dict(
                image=f'hamacom/{self.ver.__appid__}:{self.ver.__version__}{install_tag}',
                container_name=f'{self.ver.__appid__}{install_tag}',
                environment=dict(
                    TZ='Asia/Tokyo',
                    CMDBOX_DEBUG='false',
                    REDIS_HOST='${REDIS_HOST:-redis}',
                    REDIS_PORT='${REDIS_PORT:-6379}',
                    REDIS_PASSWORD='${REDIS_PASSWORD:-password}',
                    SVNAME='${SVNAME:-'+self.ver.__appid__+install_tag+'}',
                    LISTEN_PORT='${LISTEN_PORT:-8081}',
                    MCPSV_LISTEN_PORT='${MCPSV_LISTEN_PORT:-8091}',
                    A2ASV_LISTEN_PORT='${A2ASV_LISTEN_PORT:-8071}',
                    SVCOUNT='${SVCOUNT:-2}',
                ),
                user=user,
                ports=['${LISTEN_PORT:-8081}:${LISTEN_PORT:-8081}',
                       '${MCPSV_LISTEN_PORT:-8091}:${MCPSV_LISTEN_PORT:-8091}',
                       '${A2ASV_LISTEN_PORT:-8071}:${A2ASV_LISTEN_PORT:-8071}'],
                privileged=True,
                restart='always',
                working_dir=f'/opt/{self.ver.__appid__}',
                devices=['/dev/bus/usb:/dev/bus/usb'],
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
            fp.seek(0)
            yaml.dump(comp, fp)
        cmd = f'docker build -t hamacom/{self.ver.__appid__}:{self.ver.__version__}{install_tag} -f Dockerfile .'
        returncode, _, _cmd = common.cmd(f"{cmd}", self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to install {self.ver.__appid__}-server. cmd:{_cmd}")
            return {"error": f"Failed to install {self.ver.__appid__}-server. cmd:{_cmd}"}
        #os.remove('Dockerfile')
        return {"success": f"Success to install {self.ver.__appid__}-server. and docker-compose.yml is copied. cmd:{_cmd}"}

    def server_uninstall(self, install_tag:str=None):
        """
        cmdboxサーバーをアンインストールします。

        Args:
            install_tag (str): インストールタグ

        Returns:
            dict: 処理結果
        """
        if platform.system() == 'Windows':
            return {"warn": f"Uninstall server command is Unsupported in windows platform."}
        install_tag = f"_{install_tag}" if install_tag is not None else ''
        cmd = f"docker compose down {self.ver.__appid__}{install_tag}"
        returncode, _, _cmd = common.cmd(f"{cmd}", self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to down {self.ver.__appid__}-server. cmd:{_cmd}")
            return {"error": f"Failed to down {self.ver.__appid__}-server. cmd:{_cmd}"}
        cmd = f"docker rmi hamacom/{self.ver.__appid__}:{self.ver.__version__}{install_tag}"
        returncode, _, _cmd = common.cmd(f"{cmd}", self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to uninstall {self.ver.__appid__}-server. cmd:{_cmd}")
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

    def server_up(self):
        """
        cmdboxサーバーを起動します。

        Returns:
            dict: 処理結果
        """
        if platform.system() == 'Windows':
            return {"warn": f"Up server command is Unsupported in windows platform."}

        cmd = f"docker compose up -d {self.ver.__appid__}"
        returncode, _, _cmd = common.cmd(f"{cmd}", self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to up {self.ver.__appid__}-server. cmd:{_cmd}")
            return {"error": f"Failed to up {self.ver.__appid__}-server. cmd:{_cmd}"}
        return {"success": f"Success to up {self.ver.__appid__}-server. cmd:{_cmd}"}

    def server_down(self):
        """
        cmdboxサーバーを停止します。

        Returns:
            dict: 処理結果
        """
        if platform.system() == 'Windows':
            return {"warn": f"Up server command is Unsupported in windows platform."}
        cmd = f"docker compose down {self.ver.__appid__}"
        returncode, _, _cmd = common.cmd(f"{cmd}", self.logger, slise=-1)
        if returncode != 0:
            self.logger.warning(f"Failed to down {self.ver.__appid__}-server. cmd:{_cmd}")
            return {"error": f"Failed to down {self.ver.__appid__}-server. cmd:{_cmd}"}

        return {"success": f"Success to down {self.ver.__appid__}-server. cmd:{_cmd}"}
