from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.features.cli import cmdbox_tts_start
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import requests
import subprocess
import sys


class TtsSay(cmdbox_tts_start.TtsStart):

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'say'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['description_ja'] = "Text-to-Speech(TTS)エンジンを使ってテキストを音声に変換します。"
        opt['description_en'] = "Converts text to speech using the Text-to-Speech (TTS) engine."
        opt['choice'] += [
            dict(opt="tts_text", type=Options.T_TEXT, default=None, required=True, multi=False, hide=False, choice=None,
                 description_ja="変換するテキストを指定します。",
                 description_en="Specifies the text to convert."),
            dict(opt="tts_output", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="out",
                 description_ja="変換後の音声ファイルの出力先を指定します。",
                 description_en="Specifies the output file for the converted audio."),
        ]
        return opt

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
            if args.voicevox_model is None:
                msg = dict(warn=f"Please specify the --voicevox_model option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
        if args.tts_text is None:
            msg = dict(warn=f"Please specify the --tts_text option.")
            common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        tts_engine_b64 = convert.str2b64str(args.tts_engine)
        voicevox_model_b64 = convert.str2b64str(args.voicevox_model) if args.voicevox_model is not None else '-'
        tts_text_b64 = convert.str2b64str(args.tts_text)

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                    [tts_engine_b64, voicevox_model_b64, tts_text_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        if args.tts_output:
            if 'success' in ret and 'data' in ret['success']:
                wav_b64 = ret['success']['data']
                wav_data = convert.b64str2bytes(wav_b64)
                def _w(f):
                    f.write(wav_data)
                common.save_file(args.tts_output, _w, mode='wb')
                del ret['success']['data'] # 音声データは削除
        common.print_format(ret, False, tm, None, False, pf=pf)
        if 'success' not in ret:
                return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'tts_say'

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
        voicevox_model = convert.b64str2str(msg[3])
        tts_text = convert.b64str2str(msg[4])
        st = self.say(msg[1], tts_engine, voicevox_model, tts_text, data_dir, logger, redis_cli, sessions)
        return st

    def say(self, reskey:str, tts_engine:str, voicevox_model:str, tts_text:str, data_dir:Path, logger:logging.Logger,
              redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        TTSエンジンを使ってテキストを音声に変換します

        Args:
            reskey (str): レスポンスキー
            tts_engine (str): TTSエンジン
            voicevox_model (str): VoiceVoxモデル
            tts_text (str): TTSテキスト
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
                # voicevoxモデルを使ってテキストを音声に変換
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
                wav_b64 = convert.bytes2b64str(synthesizer.tts(text=tts_text, style_id=session['style_id']))
                #===============================================================
                # 成功時の処理
                rescode, msg = (self.RESP_SUCCESS, dict(success=dict(data=wav_b64, format='wav', model=voicevox_model)))
                redis_cli.rpush(reskey, msg)
                return rescode
        except Exception as e:
            logger.warning(f"Failed to say: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to say: {e}"))
            return self.RESP_WARN
