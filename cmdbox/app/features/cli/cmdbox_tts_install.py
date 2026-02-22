from cmdbox import version
from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import glob
import logging
import pip
import requests
import shutil
import subprocess
import sys
import tarfile


class TtsInstall(feature.UnsupportEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'tts'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'install'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=False,
            description_ja="Text-to-Speech(TTS)エンジンをインストールします。",
            description_en="Installs the Text-to-Speech (TTS) engine.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                     description_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="300", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="client_only", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="サーバーへの接続を行わないようにします。",
                     description_en="Do not make connections to the server."),
                dict(opt="force_install", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="既にインストール済みであっても上書きインストールを行います。",
                     description_en="Overwrite the installation even if it is already installed."),
                dict(opt="tts_engine", type=Options.T_STR, default="voicevox", required=True, multi=False, hide=False,
                     choice=["", "voicevox"],
                     choice_show=dict(voicevox=["voicevox_ver", "voicevox_whl",
                                                "openjtalk_ver", "openjtalk_dic",
                                                "onnxruntime_ver", "onnxruntime_lib"]),
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
                dict(opt="openjtalk_ver", type=Options.T_STR, default='v1.11.1', required=False, multi=False, hide=False,
                     choice=['', 'v1.11.1'],
                     choice_edit=True,
                     description_ja="使用するopenjtalkのバージョンを指定します。",
                     description_en="Specify the version of openjtalk to use."),
                dict(opt="openjtalk_dic", type=Options.T_STR, default='open_jtalk_dic_utf_8-1.11.tar.gz', required=False, multi=False, hide=False,
                     choice=['', 'open_jtalk_dic_utf_8-1.11.tar.gz'],
                     choice_edit=True,
                     description_ja="使用するopenjtalkの辞書ファイルを指定します。",
                     description_en="Specify the openjtalk dictionary file to use."),
                dict(opt="onnxruntime_ver", type=Options.T_STR, default='voicevox_onnxruntime-1.17.3', required=False, multi=False, hide=False,
                     choice=['', 'voicevox_onnxruntime-1.17.3'],
                     choice_edit=True,
                     description_ja="使用するONNX Runtimeのバージョンを指定します。",
                     description_en="Specify the version of ONNX Runtime to use."),
                dict(opt="onnxruntime_lib", type=Options.T_STR, default='voicevox_onnxruntime-linux-x64-1.17.3.tgz', required=False, multi=False, hide=False,
                     choice=['',
                             'voicevox_onnxruntime-linux-arm64-1.17.3.tgz',
                             'voicevox_onnxruntime-linux-armhf-1.17.3.tgz',
                             'voicevox_onnxruntime-linux-x64-1.17.3.tgz',
                             'voicevox_onnxruntime-linux-x64-cuda-1.17.3.tgz',
                             'voicevox_onnxruntime-osx-arm64-1.17.3.tgz',
                             'voicevox_onnxruntime-osx-x86_64-1.17.3.tgz',
                             'voicevox_onnxruntime-win-x64-1.17.3.tgz',
                             'voicevox_onnxruntime-win-x64-cuda-1.17.3.tgz',
                             'voicevox_onnxruntime-win-x64-dml-1.17.3.tgz',
                             'voicevox_onnxruntime-win-x86-1.17.3.tgz',
                             ],
                     choice_edit=True,
                     description_ja="使用するONNX Runtimeのライブラリファイルを指定します。",
                     description_en="Specify the ONNX Runtime library file to use."),
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
        if args.data is None and not args.client_only:
            msg = dict(warn=f"Please specify the --data option.")
            common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if args.tts_engine is None:
            msg = dict(warn=f"Please specify the --tts_engine option.")
            common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if args.tts_engine == 'voicevox':
            if args.voicevox_ver is None:
                msg = dict(warn=f"Please specify the --voicevox_ver option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if args.voicevox_whl is None:
                msg = dict(warn=f"Please specify the --voicevox_whl option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if args.openjtalk_ver is None:
                msg = dict(warn=f"Please specify the --openjtalk_ver option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if args.openjtalk_dic is None:
                msg = dict(warn=f"Please specify the --openjtalk_dic option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if args.onnxruntime_ver is None:
                msg = dict(warn=f"Please specify the --onnxruntime_ver option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if args.onnxruntime_lib is None:
                msg = dict(warn=f"Please specify the --onnxruntime_lib option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        data = Path(args.data) if args.data is not None else None
        tts_engine = args.tts_engine
        voicevox_ver = args.voicevox_ver if args.voicevox_ver is not None else '-'
        voicevox_whl = args.voicevox_whl if args.voicevox_whl is not None else '-'
        openjtalk_ver = args.openjtalk_ver if args.openjtalk_ver is not None else '-'
        openjtalk_dic = args.openjtalk_dic if args.openjtalk_dic is not None else '-'
        onnxruntime_ver = args.onnxruntime_ver if args.onnxruntime_ver is not None else '-'
        onnxruntime_lib = args.onnxruntime_lib if args.onnxruntime_lib is not None else '-'
        force_install = args.force_install if args.force_install is not None else False

        if args.client_only:
            # クライアントのみの場合は、サーバーに接続せずに実行
            ret = self.install(common.random_string(), data, tts_engine, voicevox_ver, voicevox_whl,
                               openjtalk_ver, openjtalk_dic,
                               onnxruntime_ver, onnxruntime_lib, force_install, logger)
        else:
            tts_engine_b64 = convert.str2b64str(tts_engine)
            voicevox_ver_b64 = convert.str2b64str(voicevox_ver)
            voicevox_whl_b64 = convert.str2b64str(voicevox_whl)
            openjtalk_ver_b64 = convert.str2b64str(openjtalk_ver)
            openjtalk_dic_b64 = convert.str2b64str(openjtalk_dic)
            onnxruntime_ver_b64 = convert.str2b64str(onnxruntime_ver)
            onnxruntime_lib_b64 = convert.str2b64str(onnxruntime_lib)
            force_install_b64 = convert.str2b64str(str(force_install))
            cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
            ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                        [tts_engine_b64, voicevox_ver_b64, voicevox_whl_b64, openjtalk_ver_b64, openjtalk_dic_b64, onnxruntime_ver_b64, onnxruntime_lib_b64, force_install_b64],
                                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, False, tm, None, False, pf=pf)
        if 'success' not in ret:
                return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        この機能のサーバー側の実行を行います

        Args:
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            msg (List[str]): 受信メッセージ
            sessions (Dict[str, Dict[str, Any]]): セッション情報
        
        Returns:
            int: 終了コード
        """
        tts_engine = convert.b64str2str(msg[2])
        voicevox_ver = convert.b64str2str(msg[3])
        voicevox_whl = convert.b64str2str(msg[4])
        openjtalk_ver = convert.b64str2str(msg[5])
        openjtalk_dic = convert.b64str2str(msg[6])
        onnxruntime_ver = convert.b64str2str(msg[7])
        onnxruntime_lib = convert.b64str2str(msg[8])
        force_install = convert.b64str2str(msg[9]).lower() == 'true'
        ret = self.install(msg[1], data_dir, tts_engine, voicevox_ver, voicevox_whl,
                           openjtalk_ver, openjtalk_dic, onnxruntime_ver, onnxruntime_lib,
                           force_install, logger)

        redis_cli.rpush(msg[1], ret)
        if 'success' not in ret:
            return self.RESP_WARN
        return self.RESP_SUCCESS

    def install(self, reskey:str, data_dir:Path, tts_engine:str, voicevox_ver:str, voicevox_whl:str,
                openjtalk_ver:str, openjtalk_dic:str,
                onnxruntime_ver:str, onnxruntime_lib:str,
                force_install:bool, logger:logging.Logger) -> Dict[str, Any]:
        """
        TTSエンジンをインストールします

        Args:
            reskey (str): レスポンスキー
            data_dir (Path): データディレクトリ
            tts_engine (str): TTSエンジン
            voicevox_ver (str): VoiceVoxバージョン
            voicevox_whl (str): VoiceVox ホイールファイル
            openjtalk_ver (str): Open JTalk バージョン
            openjtalk_dic (str): Open JTalk 辞書
            onnxruntime_ver (str): ONNX Runtime バージョン
            onnxruntime_lib (str): ONNX Runtime ライブラリ
            force_install (bool): 強制インストールフラグ
            logger (logging.Logger): ロガー

        Returns:
            Dict[str, Any]: 結果
        """
        try:
            if tts_engine == 'voicevox':
                voicevox_dir = data_dir / '.voicevox' / 'voicevox_core'
                if voicevox_dir.exists() and force_install:
                    shutil.rmtree(voicevox_dir)
                voicevox_dir.mkdir(parents=True, exist_ok=True)

                #===============================================================
                # Open JTalk辞書のダウンロード (SourceForgeが不安定なためGitHubから)
                dic_url = f"https://github.com/r9y9/open_jtalk/releases/download/{openjtalk_ver}/{openjtalk_dic}"
                dic_file = voicevox_dir / 'dict' / openjtalk_dic
                if not dic_file.exists():
                    dic_file.parent.mkdir(parents=True, exist_ok=True)
                    if logger.level == logging.DEBUG:
                        logger.debug(f"Downloading dictionary.. : {dic_url}")
                    responce = requests.get(dic_url, allow_redirects=True)
                    if responce.status_code != 200:
                        _msg = f"Failed to download Open JTalk dictionary: {responce.status_code} {responce.reason}. {dic_url}"
                        logger.error(_msg, exc_info=True)
                        return dict(warn=_msg)
                    def _wd_dic(f):
                        f.write(responce.content)
                    common.save_file(dic_file, _wd_dic, mode='wb')
                    # 辞書の展開
                    if logger.level == logging.DEBUG:
                        logger.debug(f"Extracting dictionary.. : {dic_file}")
                    with tarfile.open(dic_file, 'r:gz') as tar:
                        tar.extractall(path=dic_file.parent)
                    src_dir = dic_file.parent / str(openjtalk_dic).replace('.tar.gz', '')
                    for src_file in src_dir.glob('*'):
                        shutil.move(src_file, dic_file.parent)
                    shutil.rmtree(src_dir)
                    if logger.level == logging.DEBUG:
                        logger.debug(f"Extracted dictionary. : {dic_file.parent}")
                else:
                    logger.info(f"Since it already existed, I skipped downloading Open JTalk dictionary. : {dic_file}")

                #===============================================================
                # モデルファイルをダウンロード
                model_url = "https://raw.githubusercontent.com/VOICEVOX/voicevox_vvm/main/vvms/"
                model_dir = voicevox_dir / 'models' / 'vvms'
                if not model_dir.exists():
                    model_dir.mkdir(parents=True, exist_ok=True)
                    for i in range(0, 22):
                        # モデルダウンロード
                        if logger.level == logging.DEBUG:
                            logger.debug(f"Downloading model. : {model_url}{i}.vvm")
                        responce = requests.get(f"{model_url}{i}.vvm", allow_redirects=True)
                        if responce.status_code != 200:
                            _msg = f"Failed to download vvm: {responce.status_code} {responce.reason}. {model_url}{i}.vvm"
                            logger.error(_msg, exc_info=True)
                            return dict(warn=_msg)
                        def _wd_model(f):
                            f.write(responce.content)
                        save_file = model_dir / f'{i}.vvm'
                        common.save_file(save_file, _wd_model, mode='wb')
                        if logger.level == logging.DEBUG:
                            logger.debug(f"Saved model. : {save_file}")
                    if logger.level == logging.DEBUG:
                        logger.debug(f"Downloading models Completed.")
                else:
                    logger.info(f"Since it already existed, I skipped downloading VOICEVOX models. : {model_dir}")

                #===============================================================
                # ONNX Runtimeをダウンロード
                onnx_url = f"https://github.com/VOICEVOX/onnxruntime-builder/releases/download/{onnxruntime_ver}/{onnxruntime_lib}"
                onnx_dir = voicevox_dir / 'onnxruntime'
                if not onnx_dir.exists():
                    onnx_dir.mkdir(parents=True, exist_ok=True)
                    # onnxruntimeダウンロード
                    if logger.level == logging.DEBUG:
                        logger.debug(f"Downloading onnxruntime. : {onnx_url}")
                    responce = requests.get(f"{onnx_url}", allow_redirects=True)
                    if responce.status_code != 200:
                        _msg = f"Failed to download onnxruntime: {responce.status_code} {responce.reason}. {onnx_url}"
                        logger.error(_msg, exc_info=True)
                        return dict(warn=_msg)
                    def _wd_model(f):
                        f.write(responce.content)
                    save_file = onnx_dir / f'{onnxruntime_lib}'
                    common.save_file(save_file, _wd_model, mode='wb')
                    if logger.level == logging.DEBUG:
                        logger.debug(f"Downloading onnxruntime Completed.")
                    # libの展開
                    if logger.level == logging.DEBUG:
                        logger.debug(f"Extracting dictionary.. : {save_file}")
                    with tarfile.open(save_file, 'r:gz') as tar:
                        tar.extractall(path=save_file.parent)
                    src_dir = Path(str(save_file).replace('.tgz', ''))
                    for src_file in src_dir.glob('*'):
                        shutil.move(src_file, onnx_dir)
                    shutil.rmtree(src_dir)
                    if logger.level == logging.DEBUG:
                        logger.debug(f"Extracted dictionary. : {onnx_dir}")
                else:
                    logger.info(f"Since it already existed, I skipped downloading ONNX Runtime. : {onnx_dir}")

                #===============================================================
                # voicevoxのpythonライブラリのインストール
                whl_url = f'https://github.com/VOICEVOX/voicevox_core/releases/download/{voicevox_ver}/{voicevox_whl}'
                voicevox_whl = voicevox_dir / voicevox_whl
                if not voicevox_whl.exists():
                    # whlファイルをダウンロード
                    if logger.level == logging.DEBUG:
                        logger.debug(f"Downloading.. : {whl_url}")
                    responce = requests.get(whl_url, allow_redirects=True)
                    if responce.status_code != 200:
                        _msg = f"Failed to download VoiceVox whl: {responce.status_code} {responce.reason}. {whl_url}"
                        logger.error(_msg, exc_info=True)
                        return dict(warn=_msg)
                    def _ww(f):
                        f.write(responce.content)
                    common.save_file(voicevox_whl, _ww, mode='wb')
                else:
                    logger.info(f"Since it already existed, I skipped downloading VOICEVOX whl. : {voicevox_whl}")
                # whlファイルをpipでインストール
                if logger.level == logging.DEBUG:
                    logger.debug(f"pip install {voicevox_whl}")
                rescode = pip.main(['install', str(voicevox_whl)])  # pipのインストール
                logger.info(f"Install wheel: {voicevox_whl}")
                if rescode != 0:
                    _msg = f"Failed to install VoiceVox python library: Possible whl not in the environment. {voicevox_whl}. {whl_url}"
                    logger.error(_msg, exc_info=True)
                    return dict(warn=_msg)
                #===============================================================
                # 成功時の処理
                rescode, _msg = (self.RESP_SUCCESS, dict(success=f'Success to install VoiceVox. {whl_url}'))
                return dict(success=_msg)
        except Exception as e:
            _msg = f"Failed to install VoiceVox: {e}"
            logger.warning(_msg, exc_info=True)
            return dict(warn=_msg)
