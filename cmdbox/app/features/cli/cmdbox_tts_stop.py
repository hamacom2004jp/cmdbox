from cmdbox.app.commons import convert, redis_client
from cmdbox.app.features.cli import cmdbox_tts_start
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import logging


class TtsStop(cmdbox_tts_start.TtsStart):

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'stop'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['description_ja'] = "Text-to-Speech(TTS)エンジンを停止します。"
        opt['description_en'] = "Stops the Text-to-Speech (TTS) engine."
        return opt

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'tts_stop'

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
        voicevox_model = convert.b64str2str(msg[3])
        st = self.stop(msg[1], tts_engine, voicevox_model, data_dir, logger, redis_cli, sessions)
        return st

    def stop(self, reskey:str, tts_engine:str, voicevox_model:str, data_dir:Path, logger:logging.Logger,
              redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        TTSエンジンのモデルを停止します

        Args:
            reskey (str): レスポンスキー
            tts_engine (str): TTSエンジン
            voicevox_model (str): VoiceVoxモデル
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報

        Returns:
            int: レスポンスコード
        """
        try:
            if tts_engine == 'voicevox':
                #===============================================================
                # voicevoxモデルの停止
                style_key = [k for k,v in cmdbox_tts_start.TtsStart.VOICEVOX_STYLE.items() if v['select'] == voicevox_model]
                if not style_key:
                    logger.error(f"Invalid voicevox_model specified: {voicevox_model}")
                    redis_cli.rpush(reskey, dict(warn=f"Invalid voicevox_model specified: {voicevox_model}"))
                    return self.RESP_WARN
                style = cmdbox_tts_start.TtsStart.VOICEVOX_STYLE[style_key[0]]
                model_key = style['model_key']
                if model_key not in sessions:
                    logger.warning(f"VoiceVox model is not running: {voicevox_model}")
                    redis_cli.rpush(reskey, dict(warn=f"VoiceVox model is not running: {voicevox_model}"))
                    return self.RESP_WARN
                # セッションの削除
                from voicevox_core.blocking import Synthesizer
                session = sessions[model_key]
                synthesizer:Synthesizer = session['synthesizer']
                synthesizer.unload_voice_model(session['model_id'])
                del sessions[model_key]
                #===============================================================
                # 成功時の処理
                rescode, msg = (self.RESP_SUCCESS, dict(success=f'Success to stop VoiceVox. Model: {voicevox_model}'))
                redis_cli.rpush(reskey, msg)
                return rescode
        except Exception as e:
            logger.warning(f"Failed to stop: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to stop: {e}"))
            return self.RESP_WARN
