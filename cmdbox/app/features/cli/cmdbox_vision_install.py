from cmdbox import version
from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from cmdbox.app.features.cli import cmdbox_vision_start
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


class VisionInstall(cmdbox_vision_start.VisionStart):
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
        return 'install'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=True, use_agent=False,
            description_ja="画像/動画の推論エンジンをインストールします。",
            description_en="Installs the image/video inference engine.",
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
                dict(opt="vision_engine", type=Options.T_STR, default="sam2", required=True, multi=False, hide=False,
                     choice=["sam2"],
                     description_ja="使用するVisionエンジンを指定します。",
                     description_en="Specify the Vision engine to use."),
            ]
        )

    def get_svcmd(self):
        """
        この機能のサーバー側のコマンドを返します

        Returns:
            str: サーバー側のコマンド
        """
        return 'vision_install'

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
            vision_engine_b64 = convert.str2b64str(args.vision_engine)
            if args.client_only:
                # クライアントのみの場合は、サーバーに接続せずに実行
                ret = self.install(common.random_string(), args.vision_engine, logger)
            else:
                cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
                ret = cl.redis_cli.send_cmd(self.get_svcmd(), [vision_engine_b64],
                                            retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
            common.print_format(ret, False, tm, None, False, pf=pf)
            if 'success' not in ret:
                    return self.RESP_WARN, ret, None
            return self.RESP_SUCCESS, ret, None

        msg = dict(warn=f"Unsupported vision engine: {args.vision_engine}")
        common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
        return self.RESP_WARN, msg, None

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
        vision_engine = convert.b64str2str(msg[2])
        ret = self.install(msg[1], vision_engine, logger)

        if 'success' not in ret:
            redis_cli.rpush(msg[1], ret)
            return self.RESP_WARN
        return self.RESP_SUCCESS

    def install(self, reskey:str, vision_engine:str, logger:logging.Logger) -> Dict[str, Any]:
        """
        SAML2をインストールします

        Args:
            reskey (str): レスポンスキー
            vision_engine (str): Visionエンジン
            logger (logging.Logger): ロガー

        Returns:
            Dict[str, Any]: 結果
        """
        try:
            if vision_engine == 'sam2':
                #===============================================================
                # SAM2のモデルファイルのダウンロード
                sam2_dir = Path(version.__file__).parent / '.sam2' / 'model'
                # すでにダウンローダーが存在する場合は削除
                if sam2_dir.exists():
                    shutil.rmtree(sam2_dir)
                for mk, mv in self.VISION_MODEL.items():
                    model_file = sam2_dir / mv['path']
                    model_file.parent.mkdir(parents=True, exist_ok=True)
                    # モデルファイルを保存
                    logger.info(f"Downloading.. : {mv['url']}")
                    responce = requests.get(f"{mv['url']}", allow_redirects=True)
                    if responce.status_code != 200:
                        _msg = f"Failed to download SAM2 model: {responce.status_code} {responce.reason}. {mv['url']}"
                        logger.error(_msg, exc_info=True)
                        return dict(warn=_msg)
                    with open(model_file, mode='wb') as f:
                        f.write(responce.content)
                #===============================================================
                # SAM2のpythonライブラリのインストール
                whl_url = f'git+https://github.com/facebookresearch/sam2.git'
                # whlファイルをpipでインストール
                if logger.level == logging.DEBUG:
                    logger.debug(f"pip install {whl_url}")
                rescode = pip.main(['install', str(whl_url)])  # pipのインストール
                logger.info(f"Install wheel: {whl_url}")
                if rescode != 0:
                    _msg = f"Failed to install SAM2 python library: Possible whl not in the environment. {whl_url}"
                    logger.error(_msg, exc_info=True)
                    return dict(warn=_msg)
                #===============================================================
                # 成功時の処理
                rescode, _msg = (self.RESP_SUCCESS, dict(success=f'Success to install SAM2 python library. {whl_url}'))
                return dict(success=_msg)
            else:
                _msg = f"Unsupported vision engine: {vision_engine}"
                logger.error(_msg, exc_info=True)
                return dict(warn=_msg)
        except Exception as e:
            _msg = f"Failed to install vision engine: {e}"
            logger.warning(_msg, exc_info=True)
            return dict(warn=_msg)
