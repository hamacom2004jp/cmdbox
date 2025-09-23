from cmdbox import version
from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class VisionStart(feature.UnsupportEdgeFeature):
    VISION_MODEL = dict()
    VISION_MODEL['092824/sam2.1_hiera_tiny'] = dict(type='sam2',
                                                    path='092824/sam2.1_hiera_tiny.pt',
                                                    conf='configs/sam2.1/sam2.1_hiera_t.yaml',
                                                    url='https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_tiny.pt')
    VISION_MODEL['092824/sam2.1_hiera_small'] = dict(type='sam2',
                                                     path='092824/sam2.1_hiera_small.pt',
                                                     conf='configs/sam2.1/sam2.1_hiera_s.yaml',
                                                     url='https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_small.pt')
    VISION_MODEL['092824/sam2.1_hiera_base_plus'] = dict(type='sam2',
                                                         path='092824/sam2.1_hiera_base_plus.pt',
                                                         conf='configs/sam2.1/sam2.1_hiera_b+.yaml',
                                                         url='https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_base_plus.pt')
    VISION_MODEL['092824/sam2.1_hiera_large'] = dict(type='sam2',
                                                     path='092824/sam2.1_hiera_large.pt',
                                                     conf='configs/sam2.1/sam2.1_hiera_l.yaml',
                                                     url='https://dl.fbaipublicfiles.com/segment_anything_2/092824/sam2.1_hiera_large.pt')

    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'vision'

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
            description_ja="画像/動画の推論を開始します。",
            description_en="Starts inference on images/videos.",
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
                dict(opt="vision_engine", type=Options.T_STR, default="sam2", required=True, multi=False, hide=False,
                     choice=["sam2"],
                     choice_show=dict(sam2=["sam2_model"]),
                     description_ja="使用するVisionエンジンを指定します。",
                     description_en="Specify the Vision engine to use."),
                dict(opt="sam2_model", type=Options.T_STR, default="092824/sam2.1_hiera_tiny.pt", required=True, multi=False, hide=False,
                     choice=[k for k in self.VISION_MODEL.keys() if self.VISION_MODEL[k]['type'] == 'sam2'],
                     choice_edit=True,
                     description_ja="使用するSAM2モデルを指定します。",
                     description_en="Specify the SAM2 model to use."),
            ]
        )

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'vision_start'

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
        if args.vision_engine is None:
            msg = dict(warn=f"Please specify the --vision_engine option.")
            common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if args.vision_engine == 'sam2':
            if args.sam2_model is None:
                msg = dict(warn=f"Please specify the --sam2_model option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

            vision_engine_b64 = convert.str2b64str(args.vision_engine)
            sam2_model_b64 = convert.str2b64str(args.sam2_model)
            cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
            ret = cl.redis_cli.send_cmd(self.get_svcmd(),
                                        [vision_engine_b64, sam2_model_b64],
                                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
            common.print_format(ret, False, tm, None, False, pf=pf)
            if 'success' not in ret:
                    return self.RESP_WARN, ret, cl
            return self.RESP_SUCCESS, ret, cl

        msg = dict(warn=f"Unsupported vision engine: {args.vision_engine}")
        common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
        return self.RESP_WARN, msg, None

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
        vision_engine = convert.b64str2str(msg[2])
        sam2_model = convert.b64str2str(msg[3])
        st = self.start(msg[1], vision_engine, sam2_model, data_dir, logger, redis_cli, sessions)
        return st

    def start(self, reskey:str, vision_engine:str, sam2_model:str, data_dir:Path, logger:logging.Logger,
              redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> int:
        """
        SAM2のモデルを開始します

        Args:
            reskey (str): レスポンスキー
            vision_engine (str): Visionエンジン
            sam2_model (str): SAM2モデル
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報

        Returns:
            int: レスポンスコード
        """
        try:
            if 'vision' not in sessions:
                sessions['vision'] = {}
            if vision_engine == 'sam2':
                #===============================================================
                # SAM2モデルの初期化
                from sam2.build_sam import build_sam2
                from sam2.sam2_image_predictor import SAM2ImagePredictor
                #from sam2.sam2_video_predictor import SAM2VideoPredictor
                import torch

                sam2_dir = Path(version.__file__).parent / '.sam2' / 'model'
                if not sam2_dir.exists():
                    logger.error(f"Failed to start SAM2 model: sam2 directory does not exist: {sam2_dir}")
                    redis_cli.rpush(reskey, dict(warn=f"Failed to start SAM2 model: sam2 directory does not exist: {sam2_dir}"))
                    return self.RESP_WARN

                model_file = sam2_dir / self.VISION_MODEL[sam2_model]['path']
                config_file = self.VISION_MODEL[sam2_model]['conf']
                if not model_file.exists():
                    logger.error(f"Failed to start SAM2 model: model file does not exist: {model_file}")
                    redis_cli.rpush(reskey, dict(warn=f"Failed to start SAM2 model: model file does not exist: {model_file}"))
                    return self.RESP_WARN

                device = 'cuda' if torch.cuda.is_available() else 'cpu'
                # vvmファイルの読込み
                predictor = SAM2ImagePredictor(build_sam2(config_file, model_file, device=device))
                if vision_engine not in sessions['vision']:
                    sessions['vision'][vision_engine] = {}
                sessions['vision'][vision_engine][sam2_model] = dict(
                    info=self.VISION_MODEL[sam2_model].copy(),
                    predictor=predictor,
                )
                #===============================================================
                # 成功時の処理
                rescode, msg = (self.RESP_SUCCESS, dict(success=f'Success to start SAM2. Model: {sam2_model}'))
                redis_cli.rpush(reskey, msg)
                return rescode
            else:
                logger.warning(f"Unsupported vision engine: {vision_engine}")
                redis_cli.rpush(reskey, dict(warn=f"Unsupported vision engine: {vision_engine}"))
                return self.RESP_WARN
        except Exception as e:
            logger.warning(f"Failed to start: {e}", exc_info=True)
            redis_cli.rpush(reskey, dict(warn=f"Failed to start: {e}"))
            return self.RESP_WARN
