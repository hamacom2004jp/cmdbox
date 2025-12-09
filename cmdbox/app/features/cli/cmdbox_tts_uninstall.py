from cmdbox import version
from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pip
import shutil


class TtsUninstall(feature.UnsupportEdgeFeature):
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
        return 'uninstall'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=False,
            description_ja="Text-to-Speech(TTS)エンジンをアンインストールします。",
            description_en="Uninstalls the Text-to-Speech (TTS) engine.",
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
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None,
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
                dict(opt="tts_engine", type=Options.T_STR, default="voicevox", required=True, multi=False, hide=False,
                     choice=["", "voicevox"],
                     choice_show=dict(voicevox=["voicevox_ver", "voicevox_os", "voicevox_arc", "voicevox_device", "voicevox_whl"]),
                     description_ja="使用するTTSエンジンを指定します。",
                     description_en="Specify the TTS engine to use."),
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

        data = Path(args.data) if args.data is not None else None
        tts_engine = args.tts_engine

        if args.client_only:
            # クライアントのみの場合は、サーバーに接続せずに実行
            ret = self.uninstall(common.random_string(), data, tts_engine, logger)
        else:
            tts_engine_b64 = convert.str2b64str(tts_engine)
            cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
            ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                        [tts_engine_b64],
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
        ret = self.uninstall(msg[1], data_dir, tts_engine, logger)

        redis_cli.rpush(msg[1], ret)
        if 'success' not in ret:
            return self.RESP_WARN
        return self.RESP_SUCCESS

    def uninstall(self, reskey:str, data_dir:Path, tts_engine:str, logger:logging.Logger) -> Dict[str, Any]:
        """
        TTSエンジンをアンインストールします

        Args:
            reskey (str): レスポンスキー
            data_dir (Path): データディレクトリ
            tts_engine (str): TTSエンジン
            logger (logging.Logger): ロガー

        Returns:
            Dict[str, Any]: 結果
        """
        try:
            if tts_engine == 'voicevox':
                #===============================================================
                # voicevoxのpythonライブラリのアンインストール
                if logger.level == logging.DEBUG:
                    logger.debug(f"pip uninstall voicevox_core")
                
                rescode = pip.main(['uninstall', '-y', 'voicevox_core'])
                logger.info(f"Uninstall voicevox_core: {rescode}")
                
                #===============================================================
                # .voicevox ディレクトリの削除
                voicevox_dir = data_dir / '.voicevox'
                if voicevox_dir.exists():
                    shutil.rmtree(voicevox_dir)
                    logger.info(f"Removed directory: {voicevox_dir}")

                #===============================================================
                # pipのアンインストール
                rescode = pip.main(['uninstall', '-y', 'voicevox_core'])
                logger.info(f"Uninstall voicevox: {rescode}")
                if rescode != 0:
                    _msg = f"Failed to uninstall VoiceVox python library: Possible whl not in the environment."
                    logger.error(_msg, exc_info=True)
                    return dict(warn=_msg)

                #===============================================================
                # 成功時の処理
                rescode, _msg = (self.RESP_SUCCESS, dict(success=f'Success to uninstall VoiceVox.'))
                return dict(success=_msg)
            else:
                 return dict(warn=f"Unknown tts_engine: {tts_engine}")
        except Exception as e:
            _msg = f"Failed to uninstall VoiceVox: {e}"
            logger.warning(_msg, exc_info=True)
            return dict(warn=_msg)
