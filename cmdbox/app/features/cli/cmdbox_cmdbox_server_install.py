from cmdbox import version
from cmdbox.app import common
from cmdbox.app.commons import validator
from cmdbox.app.features.cli.cmdbox import cmdbox_base
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import getpass
import logging
import platform
import re
import shutil
import yaml


class CmdboxServerInstall(cmdbox_base.CmdboxBase, validator.Validator):
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
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True, use_agent=False,
            description_ja="cmdboxのコンテナをインストールします。",
            description_en="Install the cmdbox container.",
            choice=[
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="install_cmdbox", type=Options.T_STR, default=f'cmdbox=={version.__version__}', required=False, multi=False, hide=True, choice=None,
                     description_ja=f"省略した時は `cmdbox=={version.__version__}` を使用します。",
                     description_en=f"When omitted, `cmdbox=={version.__version__}` is used."),
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
                     choice_show=dict(voicevox=["voicevox_ver", "voicevox_whl"]),
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
                dict(opt="init_extra", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="from直後に実行するコマンドを指定します。",
                     description_en="Specify the command to be executed immediately after “from”."),
                dict(opt="run_extra_pre", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="install_extraの実行前に実行するコマンドを指定します。",
                     description_en="Specify additional commands to run before install_extra execution."),
                dict(opt="run_extra_post", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="install_extraの実行後に実行するコマンドを指定します。",
                     description_en="Specify additional commands to run after install_extra execution."),
                dict(opt="install_extra", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="追加でインストールするパッケージを指定します。",
                     description_en="Specify additional packages to install."),
                dict(opt="compose_path", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                     description_ja="`docker-compose.yml` ファイルを指定します。",
                     description_en="Specify the `docker-compose.yml` file."),
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
        st, msg, obj = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, obj

        ret = self.server_install(logger, args, Path(args.data),
                                  install_cmdbox_tgt=args.install_cmdbox,
                                  install_from=args.install_from,
                                  install_no_python=args.install_no_python,
                                  install_compile_python=args.install_compile_python,
                                  install_tag=args.install_tag,
                                  install_use_gpu=args.install_use_gpu,
                                  tts_engine=args.tts_engine,
                                  voicevox_ver=args.voicevox_ver,
                                  voicevox_whl=args.voicevox_whl,
                                  init_extra=args.init_extra,
                                  run_extra_pre=args.run_extra_pre,
                                  run_extra_post=args.run_extra_post,
                                  install_extra=args.install_extra,
                                  compose_path=args.compose_path,
                                  language=args.language)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def server_install(self, logger:logging.Logger, args:argparse.Namespace,
                       data:Path, install_cmdbox_tgt:str=None, install_from:str=None,
                       install_no_python:bool=False, install_compile_python:bool=False,
                       install_tag:str=None, install_use_gpu:bool=False,
                       tts_engine:str=None, voicevox_ver:str=None, voicevox_whl:str=None,
                       init_extra:List[str]=None,
                       run_extra_pre:List[str]=None, run_extra_post:List[str]=None, install_extra:List[str]=None,
                       compose_path:str=None, language:str=None) -> Dict[str, Any]:
        """
        cmdboxが含まれるdockerイメージをインストールします。

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
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
            init_extra (List[str]): from直後に実行するコマンド
            run_extra_pre (List[str]): install_extraの実行前に実行するコマンド
            run_extra_post (List[str]): install_extraの実行後に実行するコマンド
            install_extra (List[str]): 追加でインストールするパッケージ
            compose_path (str): docker-compose.ymlファイルパス
            language (str): 言語コード

        Returns:
            dict: 処理結果
        """
        common.set_debug(logger, True)
        try:
            if platform.system() == 'Windows':
                return {"warn": f"Build server command is Unsupported in windows platform."}
            container = args.container if hasattr(args, 'container') and args.container else self.ver.__appid__
            user = getpass.getuser()
            if re.match(r'^[0-9]', user):
                user = f'_{user}' # ユーザー名が数字始まりの場合、先頭にアンダースコアを付与
            install_tag = f"_{install_tag}" if install_tag else ''
            imgname = self.get_imgname(container, args)
            dockerfile = Path(f'Dockerfile.{container}')
            with open(dockerfile, 'w', encoding='utf-8') as fp:
                text = self._load_dockerfile(container)
                # cmdboxのインストール設定
                if install_cmdbox_tgt is None:
                    install_cmdbox_tgt = f'cmdbox=={self.ver.__version__}'
                wheel_cmdbox = Path(install_cmdbox_tgt)
                if wheel_cmdbox.exists() and wheel_cmdbox.suffix == '.whl':
                    try:
                        shutil.copy(wheel_cmdbox, Path('.').resolve() / wheel_cmdbox.name)
                    except shutil.SameFileError:
                        pass
                    install_cmdbox_tgt = f'/home/{user}/{wheel_cmdbox.name}'
                    text = text.replace('#{COPY_CMDBOX}', f'COPY {wheel_cmdbox.name} {install_cmdbox_tgt}')
                else:
                    text = text.replace('#{COPY_CMDBOX}', '')

                start_sh_hst = self.copy_scripts(logger, container)
                start_sh_tgt = f'/opt/{self.ver.__appid__}/{container}/scripts'
                text = text.replace('#{COPY_CMDBOX_START}', f'RUN mkdir -p {start_sh_tgt}\nCOPY {start_sh_hst} {start_sh_tgt}')

                base_image = 'python:3.12.12-slim' #'python:3.11.9-slim' #'python:3.8.18-slim'
                install_torch = 'RUN pip install --upgrade pip && pip install torch "torchvision>=0.25.0"'
                if install_use_gpu:
                    #base_image = 'nvidia/cuda:11.8.0-cudnn8-runtime-ubuntu22.04'
                    #base_image = 'pytorch/pytorch:2.7.0-cuda12.8-cudnn9-runtime'
                    #base_image = 'pytorch/pytorch:2.1.0-cuda12.1-cudnn8-runtime'
                    base_image = 'pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel'
                    install_torch = ''
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
                if install_extra is not None and type(install_extra) == list and install_extra != []:
                    whls = []
                    for r in install_extra:
                        tp = Path('.') / Path(r).name
                        if not r.endswith('.whl'): continue
                        if not tp.exists() or not Path(r).samefile(tp):
                            shutil.copy(r, tp)
                        whls.append(tp)
                    ie = "\n".join([f'COPY {r} {r}' for r in whls])
                    install_extra = f"{ie}\n" + f'RUN pip install {" ".join([str(r) for r in whls])}'
                    #whls = [r for r in install_extra if r.endswith('.whl')]
                    #ie = "\n".join([f'COPY {r} {Path(r).name}' for r in whls])
                    #install_extra = f"{ie}\n" + f'RUN pip install {" ".join([Path(r).name for r in whls])}'
                else:
                    install_extra = ''
                if init_extra is not None and type(init_extra) == list and init_extra != []:
                    init_extra = "\n".join(init_extra)
                else:
                    init_extra = ''
                if run_extra_pre is not None and type(run_extra_pre) == list and run_extra_pre != []:
                    run_extra_pre = f'RUN {" && ".join(run_extra_pre)}'
                else:
                    run_extra_pre = ''
                if run_extra_post is not None and type(run_extra_post) == list and run_extra_post != []:
                    run_extra_post = f'RUN {" && ".join(run_extra_post)}'
                else:
                    run_extra_post = ''
                text = text.replace('#{INSTALL_TAG}', install_tag)
                text = text.replace('#{INSTALL_CMDBOX}', install_cmdbox_tgt)
                text = text.replace('#{INSTALL_VOICEVOX}', install_voicevox)
                text = text.replace('#{INSTALL_TORCH}', install_torch)
                text = text.replace('#{INSTALL_EXTRA}', install_extra)
                text = text.replace('#{RUN_EXTRA_PRE}', run_extra_pre)
                text = text.replace('#{RUN_EXTRA_POST}', run_extra_post)
                text = text.replace('#{INIT_EXTRA}', init_extra)
                text = text.replace('#{ENV_EXTRA}', f'ENV APPID={self.ver.__appid__}')
                text = text.replace('#{MK_DATA_DIR}',
                                    'RUN mkdir -p /home/${MKUSER}/.'+self.ver.__appid__ + \
                                    ' && chown -R ${MKUSER}:${MKUSER} /home/${MKUSER}/.'+self.ver.__appid__)
                fp.write(text)

            cmd = f"docker build ./ --rm -t {imgname} -f {dockerfile}"
            returncode, _, _cmd = common.cmd(f"{cmd}", logger, slise=-1)
            if returncode != 0:
                logger.warning(f"Failed to install {self.ver.__appid__}-server. cmd:{_cmd}")
                return {"error": f"Failed to install {self.ver.__appid__}-server. cmd:{_cmd}"}
            dockerfile.unlink(missing_ok=True)

            comp, docker_compose_path = self.make_compose_server(logger, compose_path, container, imgname, user, data,
                                                                 start_sh_tgt, install_use_gpu, install_tag, language)
            with open(docker_compose_path, 'w', encoding='utf-8') as fp:
                yaml.dump(comp, fp)
            if returncode != 0:
                logger.warning(f"Failed to install {self.ver.__appid__} server. cmd:{_cmd}")
                return {"error": f"Failed to install {self.ver.__appid__} server. cmd:{_cmd}"}
            return {"success": f"Success to install {self.ver.__appid__} server. cmd:{_cmd}"}
        finally:
            common.set_debug(logger, False)
