from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.options import Options
from importlib import resources
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import getpass
import logging
import platform
import re
import shutil
import yaml


class CmdboxServerInstall(feature.OneshotEdgeFeature):
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
        return 'server_install'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True,
            description_ja="cmdboxのコンテナをインストールします。",
            description_en="Install the cmdbox container.",
            choice=[
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None,
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="install_cmdbox", type=Options.T_STR, default='cmdbox', required=False, multi=False, hide=True, choice=None,
                     description_ja=f"省略した時は `cmdbox` を使用します。 `cmdbox=={version.__version__}` といった指定も可能です。",
                     description_en=f"When omitted, `cmdbox` is used. You can also specify `cmdbox=={version.__version__}`."),
                dict(opt="install_from", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="作成するdockerイメージの元となるFROMイメージを指定します。",
                     description_en="Specify the FROM image that will be the source of the docker image to be created."),
                dict(opt="install_no_python", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="pythonのインストールを行わないようにします。",
                     description_en="Do not install python."),
                dict(opt="install_compile_python", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="python3をコンパイルしてインストールします。install_no_pythonが指定されるとそちらを優先します。",
                     description_en="Compile and install python3; if install_no_python is specified, it is preferred."),
                dict(opt="install_tag", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="指定すると作成するdockerイメージのタグ名に追記出来ます。",
                     description_en="If specified, you can add to the tag name of the docker image to create."),
                dict(opt="install_use_gpu", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="GPUを使用するモジュール構成でインストールします。",
                     description_en="Install with a module configuration that uses the GPU."),
                dict(opt="tts_engine", type=Options.T_STR, default="voicevox", required=True, multi=False, hide=False,
                     choice=["", "voicevox"],
                     choice_show=dict(voicevox=["voicevox_ver", "voicevox_os", "voicevox_arc", "voicevox_device", "voicevox_whl"]),
                     description_ja="使用するTTSエンジンを指定します。",
                     description_en="Specify the TTS engine to use."),
                dict(opt="voicevox_ver", type=Options.T_STR, default='0.16.3', required=False, multi=False, hide=False,
                     choice=['', '0.16.3'],
                     choice_edit=True,
                     description_ja="使用するVOICEVOXのバージョンを指定します。",
                     description_en="Specify the version of VOICEVOX to use."),
                dict(opt="voicevox_whl", type=Options.T_STR, default='voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl', required=False, multi=False, hide=False,
                     choice=['',
                             'voicevox_core-0.16.3-cp310-abi3-win32.whl',
                             'voicevox_core-0.16.3-cp310-abi3-win_amd64.whl',
                             'voicevox_core-0.16.3-cp310-abi3-macosx_10_12_x86_64.whl',
                             'voicevox_core-0.16.3-cp310-abi3-macosx_11_0_arm64.whl',
                             'voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_aarch64.whl',
                             'voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl',
                             ],
                     choice_edit=True,
                     description_ja="使用するVOICEVOXのホイールファイルを指定します。",
                     description_en="Specify the VOICEVOX wheel file to use."),
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
        if args.data is None:
            msg = dict(warn=f"Please specify the --data option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        ret = self.server_install(logger, Path(args.data),
                                  install_cmdbox_tgt=args.install_cmdbox,
                                  install_from=args.install_from,
                                  install_no_python=args.install_no_python,
                                  install_compile_python=args.install_compile_python,
                                  install_tag=args.install_tag,
                                  install_use_gpu=args.install_use_gpu,
                                  tts_engine=args.tts_engine,
                                  voicevox_ver=args.voicevox_ver,
                                  voicevox_whl=args.voicevox_whl)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def server_install(self, logger:logging.Logger,
                       data:Path, install_cmdbox_tgt:str='cmdbox', install_from:str=None,
                       install_no_python:bool=False, install_compile_python:bool=False,
                       install_tag:str=None, install_use_gpu:bool=False,
                       tts_engine:str=None, voicevox_ver:str=None, voicevox_whl:str=None):
        """
        cmdboxが含まれるdockerイメージをインストールします。

        Args:
            logger (logging.Logger): ロガー
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
        common.set_debug(logger, True)
        try:
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

                start_sh_src = Path(self.get_version_module().__file__).parent / 'docker' / 'scripts'
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
                        CMDBOX_DEBUG=False,
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
            returncode, _, _cmd = common.cmd(f"{cmd}", logger, slise=-1)
            if returncode != 0:
                logger.warning(f"Failed to install {self.ver.__appid__}-server. cmd:{_cmd}")
                return {"error": f"Failed to install {self.ver.__appid__}-server. cmd:{_cmd}"}
            #os.remove('Dockerfile')
            return {"success": f"Success to install {self.ver.__appid__}-server. and docker-compose.yml is copied. cmd:{_cmd}"}
        finally:
            common.set_debug(logger, False)

    def get_version_module(self):
        """
        バージョンモジュールを返します

        Returns:
            module: バージョンモジュール
        """
        return version