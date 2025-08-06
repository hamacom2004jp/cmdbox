from cmdbox import version
from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class TtsStart(feature.OneshotNotifyEdgeFeature):
    VOICEVOX_STYLE = dict()
    VOICEVOX_STYLE['0.vvm_2'] = dict(fn='0.vvm',ch='四国めたん',md='ノーマル',st=2)
    VOICEVOX_STYLE['0.vvm_0'] = dict(fn='0.vvm',ch='四国めたん',md='あまあま',st=0)
    VOICEVOX_STYLE['0.vvm_6'] = dict(fn='0.vvm',ch='四国めたん',md='ツンツン',st=6)
    VOICEVOX_STYLE['0.vvm_4'] = dict(fn='0.vvm',ch='四国めたん',md='セクシー',st=4)
    VOICEVOX_STYLE['0.vvm_3'] = dict(fn='0.vvm',ch='ずんだもん',md='ノーマル',st=3)
    VOICEVOX_STYLE['0.vvm_1'] = dict(fn='0.vvm',ch='ずんだもん',md='あまあま',st=1)
    VOICEVOX_STYLE['0.vvm_7'] = dict(fn='0.vvm',ch='ずんだもん',md='ツンツン',st=7)
    VOICEVOX_STYLE['0.vvm_5'] = dict(fn='0.vvm',ch='ずんだもん',md='セクシー',st=5)
    VOICEVOX_STYLE['0.vvm_8'] = dict(fn='0.vvm',ch='春日部つむぎ',md='ノーマル',st=8)
    VOICEVOX_STYLE['0.vvm_10'] = dict(fn='0.vvm',ch='雨晴はう',md='ノーマル',st=10)
    VOICEVOX_STYLE['1.vvm_14'] = dict(fn='1.vvm',ch='冥鳴ひまり',md='ノーマル',st=14)
    VOICEVOX_STYLE['2.vvm_16'] = dict(fn='2.vvm',ch='九州そら',md='ノーマル',st=16)
    VOICEVOX_STYLE['2.vvm_15'] = dict(fn='2.vvm',ch='九州そら',md='あまあま',st=15)
    VOICEVOX_STYLE['2.vvm_18'] = dict(fn='2.vvm',ch='九州そら',md='ツンツン',st=18)
    VOICEVOX_STYLE['2.vvm_17'] = dict(fn='2.vvm',ch='九州そら',md='セクシー',st=17)
    VOICEVOX_STYLE['3.vvm_9'] = dict(fn='3.vvm',ch='波音リツ',md='ノーマル',st=9)
    VOICEVOX_STYLE['3.vvm_65'] = dict(fn='3.vvm',ch='波音リツ',md='クイーン',st=65)
    VOICEVOX_STYLE['3.vvm_61'] = dict(fn='3.vvm',ch='中国うさぎ',md='ノーマル',st=61)
    VOICEVOX_STYLE['3.vvm_62'] = dict(fn='3.vvm',ch='中国うさぎ',md='おどろき',st=62)
    VOICEVOX_STYLE['3.vvm_63'] = dict(fn='3.vvm',ch='中国うさぎ',md='こわがり',st=63)
    VOICEVOX_STYLE['3.vvm_64'] = dict(fn='3.vvm',ch='中国うさぎ',md='へろへろ',st=64)
    VOICEVOX_STYLE['4.vvm_11'] = dict(fn='4.vvm',ch='玄野武宏',md='ノーマル',st=11)
    VOICEVOX_STYLE['4.vvm_21'] = dict(fn='4.vvm',ch='剣崎雌雄',md='ノーマル',st=21)
    VOICEVOX_STYLE['5.vvm_36'] = dict(fn='5.vvm',ch='四国めたん',md='ささやき',st=36)
    VOICEVOX_STYLE['5.vvm_37'] = dict(fn='5.vvm',ch='四国めたん',md='ヒソヒソ',st=37)
    VOICEVOX_STYLE['5.vvm_22'] = dict(fn='5.vvm',ch='ずんだもん',md='ささやき',st=22)
    VOICEVOX_STYLE['5.vvm_38'] = dict(fn='5.vvm',ch='ずんだもん',md='ヒソヒソ',st=38)
    VOICEVOX_STYLE['5.vvm_19'] = dict(fn='5.vvm',ch='九州そら',md='ささやき',st=19)
    VOICEVOX_STYLE['6.vvm_29'] = dict(fn='6.vvm',ch='No.7',md='ノーマル',st=29)
    VOICEVOX_STYLE['6.vvm_30'] = dict(fn='6.vvm',ch='No.7',md='アナウンス',st=30)
    VOICEVOX_STYLE['6.vvm_31'] = dict(fn='6.vvm',ch='No.7',md='読み聞かせ',st=31)
    VOICEVOX_STYLE['7.vvm_27'] = dict(fn='7.vvm',ch='後鬼',md='人間ver.',st=27)
    VOICEVOX_STYLE['7.vvm_28'] = dict(fn='7.vvm',ch='後鬼',md='ぬいぐるみver.',st=28)
    VOICEVOX_STYLE['8.vvm_23'] = dict(fn='8.vvm',ch='WhiteCUL',md='ノーマル',st=23)
    VOICEVOX_STYLE['8.vvm_24'] = dict(fn='8.vvm',ch='WhiteCUL',md='たのしい',st=24)
    VOICEVOX_STYLE['8.vvm_25'] = dict(fn='8.vvm',ch='WhiteCUL',md='かなしい',st=25)
    VOICEVOX_STYLE['8.vvm_26'] = dict(fn='8.vvm',ch='WhiteCUL',md='びえーん',st=26)
    VOICEVOX_STYLE['9.vvm_12'] = dict(fn='9.vvm',ch='白上虎太郎',md='ふつう',st=12)
    VOICEVOX_STYLE['9.vvm_32'] = dict(fn='9.vvm',ch='白上虎太郎',md='わーい',st=32)
    VOICEVOX_STYLE['9.vvm_33'] = dict(fn='9.vvm',ch='白上虎太郎',md='びくびく',st=33)
    VOICEVOX_STYLE['9.vvm_34'] = dict(fn='9.vvm',ch='白上虎太郎',md='おこ',st=34)
    VOICEVOX_STYLE['9.vvm_35'] = dict(fn='9.vvm',ch='白上虎太郎',md='びえーん',st=35)
    VOICEVOX_STYLE['10.vvm_39'] = dict(fn='10.vvm',ch='玄野武宏',md='喜び',st=39)
    VOICEVOX_STYLE['10.vvm_40'] = dict(fn='10.vvm',ch='玄野武宏',md='ツンギレ',st=40)
    VOICEVOX_STYLE['10.vvm_41'] = dict(fn='10.vvm',ch='玄野武宏',md='悲しみ',st=41)
    VOICEVOX_STYLE['10.vvm_42'] = dict(fn='10.vvm',ch='ちび式じい',md='ノーマル',st=42)
    VOICEVOX_STYLE['11.vvm_43'] = dict(fn='11.vvm',ch='櫻歌ミコ',md='ノーマル',st=43)
    VOICEVOX_STYLE['11.vvm_44'] = dict(fn='11.vvm',ch='櫻歌ミコ',md='第二形態',st=44)
    VOICEVOX_STYLE['11.vvm_45'] = dict(fn='11.vvm',ch='櫻歌ミコ',md='ロリ',st=45)
    VOICEVOX_STYLE['11.vvm_47'] = dict(fn='11.vvm',ch='ナースロボ＿タイプＴ',md='ノーマル',st=47)
    VOICEVOX_STYLE['11.vvm_48'] = dict(fn='11.vvm',ch='ナースロボ＿タイプＴ',md='楽々',st=48)
    VOICEVOX_STYLE['11.vvm_49'] = dict(fn='11.vvm',ch='ナースロボ＿タイプＴ',md='恐怖',st=49)
    VOICEVOX_STYLE['11.vvm_50'] = dict(fn='11.vvm',ch='ナースロボ＿タイプＴ',md='内緒話',st=50)
    VOICEVOX_STYLE['12.vvm_51'] = dict(fn='12.vvm',ch='†聖騎士 紅桜†',md='ノーマル',st=51)
    VOICEVOX_STYLE['12.vvm_52'] = dict(fn='12.vvm',ch='雀松朱司',md='ノーマル',st=52)
    VOICEVOX_STYLE['12.vvm_53'] = dict(fn='12.vvm',ch='麒ヶ島宗麟',md='ノーマル',st=53)
    VOICEVOX_STYLE['13.vvm_54'] = dict(fn='13.vvm',ch='春歌ナナ',md='ノーマル',st=54)
    VOICEVOX_STYLE['13.vvm_55'] = dict(fn='13.vvm',ch='猫使アル',md='ノーマル',st=55)
    VOICEVOX_STYLE['13.vvm_56'] = dict(fn='13.vvm',ch='猫使アル',md='おちつき',st=56)
    VOICEVOX_STYLE['13.vvm_57'] = dict(fn='13.vvm',ch='猫使アル',md='うきうき',st=57)
    VOICEVOX_STYLE['13.vvm_58'] = dict(fn='13.vvm',ch='猫使ビィ',md='ノーマル',st=58)
    VOICEVOX_STYLE['13.vvm_59'] = dict(fn='13.vvm',ch='猫使ビィ',md='おちつき',st=59)
    VOICEVOX_STYLE['13.vvm_60'] = dict(fn='13.vvm',ch='猫使ビィ',md='人見知り',st=60)
    VOICEVOX_STYLE['14.vvm_67'] = dict(fn='14.vvm',ch='栗田まろん',md='ノーマル',st=67)
    VOICEVOX_STYLE['14.vvm_68'] = dict(fn='14.vvm',ch='あいえるたん',md='ノーマル',st=68)
    VOICEVOX_STYLE['14.vvm_69'] = dict(fn='14.vvm',ch='満別花丸',md='ノーマル',st=69)
    VOICEVOX_STYLE['14.vvm_70'] = dict(fn='14.vvm',ch='満別花丸',md='元気',st=70)
    VOICEVOX_STYLE['14.vvm_71'] = dict(fn='14.vvm',ch='満別花丸',md='ささやき',st=71)
    VOICEVOX_STYLE['14.vvm_72'] = dict(fn='14.vvm',ch='満別花丸',md='ぶりっ子',st=72)
    VOICEVOX_STYLE['14.vvm_73'] = dict(fn='14.vvm',ch='満別花丸',md='ボーイ',st=73)
    VOICEVOX_STYLE['14.vvm_74'] = dict(fn='14.vvm',ch='琴詠ニア',md='ノーマル',st=74)
    VOICEVOX_STYLE['15.vvm_75'] = dict(fn='15.vvm',ch='ずんだもん',md='ヘロヘロ',st=75)
    VOICEVOX_STYLE['15.vvm_76'] = dict(fn='15.vvm',ch='ずんだもん',md='なみだめ',st=76)
    VOICEVOX_STYLE['15.vvm_13'] = dict(fn='15.vvm',ch='青山龍星',md='ノーマル',st=13)
    VOICEVOX_STYLE['15.vvm_81'] = dict(fn='15.vvm',ch='青山龍星',md='熱血',st=81)
    VOICEVOX_STYLE['15.vvm_82'] = dict(fn='15.vvm',ch='青山龍星',md='不機嫌',st=82)
    VOICEVOX_STYLE['15.vvm_83'] = dict(fn='15.vvm',ch='青山龍星',md='喜び',st=83)
    VOICEVOX_STYLE['15.vvm_84'] = dict(fn='15.vvm',ch='青山龍星',md='しっとり',st=84)
    VOICEVOX_STYLE['15.vvm_85'] = dict(fn='15.vvm',ch='青山龍星',md='かなしみ',st=85)
    VOICEVOX_STYLE['15.vvm_86'] = dict(fn='15.vvm',ch='青山龍星',md='囁き',st=86)
    VOICEVOX_STYLE['15.vvm_20'] = dict(fn='15.vvm',ch='もち子さん',md='ノーマル',st=20)
    VOICEVOX_STYLE['15.vvm_66'] = dict(fn='15.vvm',ch='もち子さん',md='セクシー／あん子',st=66)
    VOICEVOX_STYLE['15.vvm_77'] = dict(fn='15.vvm',ch='もち子さん',md='泣き',st=77)
    VOICEVOX_STYLE['15.vvm_78'] = dict(fn='15.vvm',ch='もち子さん',md='怒り',st=78)
    VOICEVOX_STYLE['15.vvm_79'] = dict(fn='15.vvm',ch='もち子さん',md='喜び',st=79)
    VOICEVOX_STYLE['15.vvm_80'] = dict(fn='15.vvm',ch='もち子さん',md='のんびり',st=80)
    VOICEVOX_STYLE['15.vvm_46'] = dict(fn='15.vvm',ch='小夜/SAYO',md='ノーマル',st=46)
    VOICEVOX_STYLE['16.vvm_87'] = dict(fn='16.vvm',ch='後鬼',md='人間（怒り）ver.',st=87)
    VOICEVOX_STYLE['16.vvm_88'] = dict(fn='16.vvm',ch='後鬼',md='鬼ver.',st=88)
    VOICEVOX_STYLE['17.vvm_89'] = dict(fn='17.vvm',ch='Voidoll',md='ノーマル',st=89)
    VOICEVOX_STYLE['18.vvm_90'] = dict(fn='18.vvm',ch='ぞん子',md='ノーマル',st=90)
    VOICEVOX_STYLE['18.vvm_91'] = dict(fn='18.vvm',ch='ぞん子',md='低血圧',st=91)
    VOICEVOX_STYLE['18.vvm_92'] = dict(fn='18.vvm',ch='ぞん子',md='覚醒',st=92)
    VOICEVOX_STYLE['18.vvm_93'] = dict(fn='18.vvm',ch='ぞん子',md='実況風',st=93)
    VOICEVOX_STYLE['18.vvm_94'] = dict(fn='18.vvm',ch='中部つるぎ',md='ノーマル',st=94)
    VOICEVOX_STYLE['18.vvm_95'] = dict(fn='18.vvm',ch='中部つるぎ',md='怒り',st=95)
    VOICEVOX_STYLE['18.vvm_96'] = dict(fn='18.vvm',ch='中部つるぎ',md='ヒソヒソ',st=96)
    VOICEVOX_STYLE['18.vvm_97'] = dict(fn='18.vvm',ch='中部つるぎ',md='おどおど',st=97)
    VOICEVOX_STYLE['18.vvm_98'] = dict(fn='18.vvm',ch='中部つるぎ',md='絶望と敗北',st=98)
    VOICEVOX_STYLE['19.vvm_99'] = dict(fn='19.vvm',ch='離途',md='ノーマル',st=99)
    VOICEVOX_STYLE['19.vvm_101'] = dict(fn='19.vvm',ch='離途',md='シリアス',st=101)
    VOICEVOX_STYLE['19.vvm_100'] = dict(fn='19.vvm',ch='黒沢冴白',md='ノーマル',st=100)
    VOICEVOX_STYLE['20.vvm_102'] = dict(fn='20.vvm',ch='ユーレイちゃん',md='ノーマル',st=102)
    VOICEVOX_STYLE['20.vvm_103'] = dict(fn='20.vvm',ch='ユーレイちゃん',md='甘々',st=103)
    VOICEVOX_STYLE['20.vvm_104'] = dict(fn='20.vvm',ch='ユーレイちゃん',md='哀しみ',st=104)
    VOICEVOX_STYLE['20.vvm_105'] = dict(fn='20.vvm',ch='ユーレイちゃん',md='ささやき',st=105)
    VOICEVOX_STYLE['20.vvm_106'] = dict(fn='20.vvm',ch='ユーレイちゃん',md='ツクモちゃん',st=106)
    VOICEVOX_STYLE['21.vvm_110'] = dict(fn='21.vvm',ch='猫使アル',md='つよつよ',st=110)
    VOICEVOX_STYLE['21.vvm_111'] = dict(fn='21.vvm',ch='猫使アル',md='へろへろ',st=111)
    VOICEVOX_STYLE['21.vvm_112'] = dict(fn='21.vvm',ch='猫使ビィ',md='つよつよ',st=112)
    VOICEVOX_STYLE['21.vvm_107'] = dict(fn='21.vvm',ch='東北ずん子',md='ノーマル',st=107)
    VOICEVOX_STYLE['21.vvm_108'] = dict(fn='21.vvm',ch='東北きりたん',md='ノーマル',st=108)
    VOICEVOX_STYLE['21.vvm_109'] = dict(fn='21.vvm',ch='東北イタコ',md='ノーマル',st=109)
    for k, v in VOICEVOX_STYLE.items():
        v['model_key'] = f'voicevox_{v["fn"]}_{v["st"]}'
        v['select'] = f'{v["ch"]}{v["md"]}'

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
        return 'start'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=True,
            description_ja="Text-to-Speech(TTS)エンジンを開始します。",
            description_en="Starts the Text-to-Speech (TTS) engine.",
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
                dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="tts_engine", type=Options.T_STR, default="voicevox", required=True, multi=False, hide=False,
                     choice=["voicevox"],
                     choice_show=dict(voicevox=["voicevox_model"]),
                     description_ja="使用するTTSエンジンを指定します。",
                     description_en="Specify the TTS engine to use."),
                dict(opt="voicevox_model", type=Options.T_STR, default=None, required=False, multi=False, hide=False,
                     choice=[v['select'] for v in TtsStart.VOICEVOX_STYLE.values()],
                     choice_edit=True,
                     description_ja="使用するTTSエンジンのモデルを指定します。",
                     description_en="Specify the model of the TTS engine to use."),
            ]
        )
    
    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'tts_start'

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

        tts_engine_b64 = convert.str2b64str(args.tts_engine)
        voicevox_model_b64 = convert.str2b64str(args.voicevox_model) if args.voicevox_model is not None else '-'

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                    [tts_engine_b64, voicevox_model_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, False, tm, None, False, pf=pf)
        if 'success' not in ret:
                return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def is_cluster_redirect(self):
        """
        クラスター宛のメッセージの場合、メッセージを転送するかどうかを返します

        Returns:
            bool: メッセージを転送する場合はTrue
        """
        return True

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
        st = self.start(msg[1], tts_engine, voicevox_model, data_dir, logger, redis_cli, sessions)
        return st

    def start(self, reskey:str, tts_engine:str, voicevox_model:str, data_dir:Path, logger:logging.Logger,
              redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        TTSエンジンのモデルを開始します

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
                # voicevoxの初期化
                from voicevox_core.blocking import Onnxruntime, OpenJtalk, Synthesizer, VoiceModelFile
                voicevox_dir = Path(version.__file__).parent / '.voicevox' / 'voicevox_core'
                if not voicevox_dir.exists():
                    logger.error(f"Failed to start VoiceVox core: voicevox directory does not exist: {voicevox_dir}")
                    redis_cli.rpush(reskey, dict(warn=f"Failed to start VoiceVox core: voicevox directory does not exist: {voicevox_dir}"))
                    return self.RESP_WARN
                voicevox_onnxruntime_path = voicevox_dir / 'onnxruntime' / 'lib' / Onnxruntime.LIB_VERSIONED_FILENAME
                open_jtalk_dict_dir = voicevox_dir / 'dict' / 'open_jtalk_dic_utf_8-1.11'
                # voicevox_modelのチェック
                style_key = [k for k,v in TtsStart.VOICEVOX_STYLE.items() if v['select'] == voicevox_model]
                if not style_key:
                    logger.error(f"Invalid voicevox_model specified: {voicevox_model}")
                    redis_cli.rpush(reskey, dict(warn=f"Invalid voicevox_model specified: {voicevox_model}"))
                    return self.RESP_WARN
                style = TtsStart.VOICEVOX_STYLE[style_key[0]]
                model_key = style['model_key']
                if model_key in sessions:
                    logger.warning(f"VoiceVox model is already running: {voicevox_model}")
                    redis_cli.rpush(reskey, dict(warn=f"VoiceVox model is already running: {voicevox_model} ({model_key})"))
                    return self.RESP_WARN
                # vvmファイルの読込み
                synthesizer = Synthesizer(Onnxruntime.load_once(filename=str(voicevox_onnxruntime_path)), OpenJtalk(open_jtalk_dict_dir))
                with VoiceModelFile.open(voicevox_dir / 'models' / 'vvms' / style['fn']) as model:
                    synthesizer.load_voice_model(model)
                    # セッションに登録
                    sessions[model_key] = dict(
                        model_id=model.id,
                        model_key=model_key,
                        synthesizer=synthesizer,
                        style_id=style['st'],
                    )
                #===============================================================
                # 成功時の処理
                rescode, msg = (self.RESP_SUCCESS, dict(success=f'Success to start VoiceVox. Model: {voicevox_model}'))
                redis_cli.rpush(reskey, msg)
                return rescode
        except Exception as e:
            logger.warning(f"Failed to start: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to start: {e}"))
            return self.RESP_WARN
