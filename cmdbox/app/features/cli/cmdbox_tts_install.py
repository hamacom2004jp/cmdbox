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
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=True, use_agent=False,
            description_ja="Text-to-Speech(TTS)エンジンをインストールします。",
            description_en="Installs the Text-to-Speech (TTS) engine.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                     description_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
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
                dict(opt="tts_engine", type=Options.T_STR, default="voicevox", required=True, multi=False, hide=False,
                     choice=["voicevox"],
                     choice_show=dict(voicevox=["voicevox_ver", "voicevox_os", "voicevox_arc", "voicevox_device", "voicevox_whl"]),
                     description_ja="使用するTTSエンジンを指定します。",
                     description_en="Specify the TTS engine to use."),
                dict(opt="voicevox_ver", type=Options.T_STR, default='0.16.0', required=False, multi=False, hide=False, choice=['0.16.0'],
                     description_ja="使用するTTSエンジンのバージョンを指定します。",
                     description_en="Specify the version of the TTS engine to use."),
                dict(opt="voicevox_os", type=Options.T_STR, default='windows', required=False, multi=False, hide=False, choice=['windows', 'osx', 'linux'],
                     description_ja="使用するTTSエンジンのOSを指定します。",
                     description_en="Specify the OS for the TTS engine."),
                dict(opt="voicevox_arc", type=Options.T_STR, default='x64', required=False, multi=False, hide=False, choice=['x64', 'arm64'],
                     description_ja="使用するTTSエンジンのアーキテクチャを指定します。",
                     description_en="Specify the architecture for the TTS engine."),
                dict(opt="voicevox_device", type=Options.T_STR, default='cpu', required=False, multi=False, hide=False, choice=['cpu', 'directml', 'cuda'],
                     description_ja="使用するTTSエンジンのデバイスを指定します。",
                     description_en="Specify the device for the TTS engine."),
                dict(opt="voicevox_whl", type=Options.T_STR, default='voicevox_core-0.16.0-cp310-abi3-win32.whl', required=False, multi=False, hide=False,
                     choice=['voicevox_core-0.16.0-cp310-abi3-win32.whl',
                             'voicevox_core-0.16.0-cp310-abi3-win_amd64.whl',
                             'voicevox_core-0.16.0-cp310-abi3-macosx_10_12_x86_64.whl',
                             'voicevox_core-0.16.0-cp310-abi3-macosx_11_0_arm64.whl',
                             'voicevox_core-0.16.0-cp310-abi3-manylinux_2_34_aarch64.whl',
                             'voicevox_core-0.16.0-cp310-abi3-manylinux_2_34_x86_64.whl'],
                     choice_edit=True,
                     description_ja="使用するTTSエンジンのホイールファイルを指定します。",
                     description_en="Specify the wheel file for the TTS engine."),
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
        if args.tts_engine is None:
            msg = dict(warn=f"Please specify the --tts_engine option.")
            common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if args.tts_engine == 'voicevox':
            if args.voicevox_ver is None:
                msg = dict(warn=f"Please specify the --voicevox_ver option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if args.voicevox_os is None:
                msg = dict(warn=f"Please specify the --voicevox_os option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if args.voicevox_arc is None:
                msg = dict(warn=f"Please specify the --voicevox_arc option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if args.voicevox_device is None:
                msg = dict(warn=f"Please specify the --voicevox_device option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if args.voicevox_whl is None:
                msg = dict(warn=f"Please specify the --voicevox_whl option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        tts_engine = args.tts_engine
        voicevox_ver = args.voicevox_ver if args.voicevox_ver is not None else '-'
        voicevox_os = args.voicevox_os if args.voicevox_os is not None else '-'
        voicevox_arc = args.voicevox_arc if args.voicevox_arc is not None else '-'
        voicevox_device = args.voicevox_device if args.voicevox_device is not None else '-'
        voicevox_whl = args.voicevox_whl if args.voicevox_whl is not None else '-'

        if args.client_only:
            # クライアントのみの場合は、サーバーに接続せずに実行
            ret = self.install(common.random_string(), tts_engine, voicevox_ver, voicevox_os, voicevox_arc,
                               voicevox_device, voicevox_whl, logger)
        else:
            tts_engine_b64 = convert.str2b64str(tts_engine)
            voicevox_ver_b64 = convert.str2b64str(voicevox_ver)
            voicevox_os_b64 = convert.str2b64str(voicevox_os)
            voicevox_arc_b64 = convert.str2b64str(voicevox_arc)
            voicevox_device_b64 = convert.str2b64str(voicevox_device)
            voicevox_whl_b64 = convert.str2b64str(voicevox_whl)
            cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
            ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                        [tts_engine_b64, voicevox_ver_b64, voicevox_os_b64, voicevox_arc_b64, voicevox_device_b64, voicevox_whl_b64],
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
        if logger.level == logging.DEBUG:
            logger.debug(f"audit write svrun msg: {msg}")
        tts_engine = convert.b64str2str(msg[2])
        voicevox_ver = convert.b64str2str(msg[3])
        voicevox_os = convert.b64str2str(msg[4])
        voicevox_arc = convert.b64str2str(msg[5])
        voicevox_device = convert.b64str2str(msg[6])
        voicevox_whl = convert.b64str2str(msg[7])
        ret = self.install(msg[1], tts_engine, voicevox_ver, voicevox_os, voicevox_arc, voicevox_device, voicevox_whl, logger)

        if 'success' not in ret:
            redis_cli.rpush(msg[1], ret)
            return self.RESP_WARN
        return self.RESP_SUCCESS

    def install(self, reskey:str, tts_engine:str, voicevox_ver:str, voicevox_os:str, voicevox_arc:str,
              voicevox_device:str, voicevox_whl:str, logger:logging.Logger) -> Dict[str, Any]:
        """
        TTSエンジンをインストールします

        Args:
            reskey (str): レスポンスキー
            tts_engine (str): TTSエンジン
            voicevox_ver (str): VoiceVoxバージョン
            voicevox_os (str): VoiceVox OS
            voicevox_arc (str): VoiceVox アーキテクチャ
            voicevox_device (str): VoiceVox デバイス
            voicevox_whl (str): VoiceVox ホイールファイル
            logger (logging.Logger): ロガー

        Returns:
            Dict[str, Any]: 結果
        """
        try:
            if tts_engine == 'voicevox':
                #===============================================================
                # voicevoxのダウンローダーのダウンロード
                if voicevox_os == 'windows':
                    dlfile = f"download-{voicevox_os}-{voicevox_arc}.exe"
                else:
                    dlfile = f"download-{voicevox_os}-{voicevox_arc}"
                downloader_url = f"https://github.com/VOICEVOX/voicevox_core/releases/download/{voicevox_ver}/{dlfile}"
                voicevox_dir = Path(version.__file__).parent / '.voicevox' / 'voicevox_core'
                # すでにダウンローダーが存在する場合は削除
                if voicevox_dir.exists():
                    shutil.rmtree(voicevox_dir)
                voicevox_dir.mkdir(parents=True, exist_ok=True)
                dlfile = voicevox_dir / dlfile
                # ダウンローダーを保存
                if logger.level == logging.DEBUG:
                    logger.debug(f"Downloading.. : {downloader_url}")
                responce = requests.get(downloader_url, allow_redirects=True)
                if responce.status_code != 200:
                    _msg = f"Failed to download VoiceVox core: {responce.status_code} {responce.reason}. {downloader_url}"
                    logger.error(_msg, exc_info=True)
                    return dict(warn=_msg)
                def _wd(f):
                    f.write(responce.content)
                common.save_file(dlfile, _wd, mode='wb')
                # ダウンローダーの実行権限を付与
                if voicevox_os != 'windows':
                    dlfile.chmod(dlfile.stat().st_mode | 0o111)
                #===============================================================
                # ダウンローダーを実行してVoiceVox coreをダウンロード
                cmd_line = [str(dlfile), '-o', '.', '--exclude', 'c-api']
                if voicevox_device == 'directml':
                    cmd_line.extend(['--devices', 'directml'])
                elif voicevox_device == 'cuda':
                    cmd_line.extend(['--devices', 'cuda'])
                if logger.level == logging.DEBUG:
                    logger.debug(f"EXEC - {cmd_line}")
                proc = subprocess.Popen(cmd_line, cwd=str(voicevox_dir), stdout=subprocess.PIPE, stdin=subprocess.PIPE, shell=True)
                outs, errs = proc.communicate(input=b'y\ny\n')  # 'y' to confirm installation
                if proc.returncode != 0:
                    _msg = outs.decode('utf-8') if outs else ''
                    _msg += errs.decode('utf-8') if errs else _msg
                    _msg += f"Failed to install VoiceVox core: {_msg}"
                    logger.error(_msg, exc_info=True)
                    return dict(warn=_msg)
                if logger.level == logging.DEBUG:
                    logger.debug(f"Completed - {cmd_line}")
                if (voicevox_dir / 'voicevox_core').exists():
                    for file in glob.glob(str(voicevox_dir / 'voicevox_core' / '*')):
                        shutil.move(file, voicevox_dir)
                    shutil.rmtree(voicevox_dir / 'voicevox_core')
                logger.info(outs.decode('utf-8'))
                logger.info(f"VoiceVox core download successfully. {dlfile}")
                #===============================================================
                # voicevoxのpythonライブラリのインストール
                whl_url = f'https://github.com/VOICEVOX/voicevox_core/releases/download/{voicevox_ver}/{voicevox_whl}'
                voicevox_whl = voicevox_dir / voicevox_whl
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
                rescode, _msg = (self.RESP_SUCCESS, dict(success=f'Success to install VoiceVox python library. {whl_url}'))
                return dict(success=_msg)
        except Exception as e:
            _msg = f"Failed to install VoiceVox: {e}"
            logger.warning(_msg, exc_info=True)
            return dict(warn=_msg)
