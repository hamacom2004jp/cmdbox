from cmdbox import version
from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.features.cli import cmdbox_vision_start
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import datetime
import logging
import json
import numpy as np
import time
import sys



class VisionPredict(cmdbox_vision_start.VisionStart):

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
        return 'predict'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=True,
            description_ja="画像/動画の推論を実行します。",
            description_en="Executes inference on images/videos.",
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
                     choice_show=dict(sam2=["sam2_model", "sam2_point"]),
                     description_ja="使用するVisionエンジンを指定します。",
                     description_en="Specify the Vision engine to use."),
                dict(opt="sam2_model", type=Options.T_STR, default="092824/sam2.1_hiera_tiny.pt", required=True, multi=False, hide=False,
                     choice=[k for k in self.VISION_MODEL.keys() if self.VISION_MODEL[k]['type'] == 'sam2'],
                     choice_edit=True,
                     description_ja="使用するSAM2モデルを指定します。",
                     description_en="Specify the SAM2 model to use."),
                dict(opt="sam2_point", type=Options.T_STR, default=None, required=True, multi=True, hide=False, choice=None,
                     description_ja="使用するSAM2モデルのポイントを指定します。 `x,y` の形式で指定してください。",
                     description_en="Specify the SAM2 model points to use. Please specify in the format `x,y`."),
                dict(opt="sam2_label", type=Options.T_INT, default=1, required=False, multi=True, hide=False, choice=None,
                     description_ja="使用するSAM2モデルのラベルを指定します。",
                     description_en="Specify the SAM2 model label to use."),
                dict(opt="img_input_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="入力画像ファイルを指定します。",
                     description_en="Specify the input image file."),
                dict(opt="img_input_type", type=Options.T_STR, default="jpeg", required=True, multi=False, hide=False,
                     choice=['bmp', 'png', 'jpeg', 'capture'],
                     description_ja="入力画像の形式を指定します。",
                     description_en="Specify the format of the input image."),
                dict(opt="img_stdin", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="標準入力から画像を読み込みます。",
                     description_en="Read images from standard input."),
                dict(opt="img_output_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="out",
                     description_ja="推論結果画像の保存先ファイルを指定します。",
                     description_en="Specify the destination file for saving the inference result image.",
                     test_true={"yolox":"pred.jpg"}),
                dict(opt="nodraw", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="指定すると推論結果を画像に描き込みしません。",
                     description_en="If specified, inference results will not be drawn on the image."),
                dict(opt="output_json", short="o" , type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a" , type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
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
        if args.vision_engine is None:
            msg = dict(warn=f"Please specify the --vision_engine option.")
            common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        model_param = dict()
        if args.vision_engine == 'sam2':
            if args.sam2_model is None:
                msg = dict(warn=f"Please specify the --sam2_model option.")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            try:
                model_param['sam2_model'] = args.sam2_model
                model_param['sam2_point'] = [row.split(',') for row in args.sam2_point]
                model_param['sam2_label'] = args.sam2_label
            except Exception as e:
                msg = dict(warn=f"Invalid --sam2_point option. {str(e)}")
                common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
        else:
            msg = dict(warn=f"Unsupported vision engine: {args.vision_engine}")
            common.print_format(msg, False, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        if args.img_input_file is not None:
            if logger.level == logging.DEBUG:
                logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, args.name={args.name}, args.img_input_file={args.img_input_file}")
            ret = self.predict(cl, args.vision_engine, model_param=model_param, img_input_file=args.img_input_file, img_input_type=args.img_input_type,
                                img_output_file=args.img_output_file, nodraw=args.nodraw,
                                retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout,
                                logger=logger)
            if type(ret) is list:
                for r in ret:
                    common.print_format(r, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    if logger.level == logging.DEBUG:
                        ret_str = common.to_str(r, slise=100)
                        logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, ret={ret_str}")
                    tm = time.perf_counter()
                    args.output_json_append = True
            else:
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        elif args.stdin:
            if args.img_input_type is None:
                msg = {"warn":f"Please specify the --img_input_type option."}
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                if logger.level == logging.DEBUG:
                    msg_str = common.to_str(msg, slise=100)
                    logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, msg={msg_str}")
                return self.RESP_WARN, msg, None
            if args.img_input_type in ['capture']:
                def _pred(args, line, tm):
                    if logger.level == logging.DEBUG:
                        line_str = common.to_str(line, slise=100)
                        logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, args.name={args.name}, image={line_str}")
                    ret = self.predict(cl, args.vision_engine, model_param=model_param, image=line, img_input_type=args.img_input_type,
                                        img_output_file=args.img_output_file, nodraw=args.nodraw,
                                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout,
                                        logger=logger)
                    common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    if logger.level == logging.DEBUG:
                        ret_str = common.to_str(ret, slise=100)
                        logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, ret={ret_str}")
                for line in sys.stdin:
                    # 標準入力による推論処理は非同期で行う(同名複数serverの場合にスループットを向上させるため)
                    #thread = threading.Thread(target=_pred, args=(args, line, tm))
                    #thread.start()
                    _pred(args, line, tm)
                    tm = time.perf_counter()
                    args.output_json_append = True
            else:
                if logger.level == logging.DEBUG:
                    logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, args.name={args.name}, image=<stdin>")
                ret = self.predict(cl, args.vision_engine, model_param=model_param, image=sys.stdin.buffer.read(), img_input_type=args.img_input_type,
                                    img_output_file=args.img_output_file, nodraw=args.nodraw,
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout,
                                    logger=logger)
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                if logger.level == logging.DEBUG:
                    ret_str = common.to_str(ret, slise=100)
                    logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, ret={ret_str}")
                tm = time.perf_counter()
        else:
            msg = {"warn":f"Image file or stdin is empty."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            if logger.level == logging.DEBUG:
                msg_str = common.to_str(msg, slise=100)
                logger.debug(f"app.main: args.mode={args.mode}, args.cmd={args.cmd}, msg={msg_str}")
            return self.RESP_WARN, msg, None

        common.print_format(ret, False, tm, None, False, pf=pf)
        if 'success' not in ret:
                return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def predict(self, cl:client.Client, vision_engine:str, model_param:Dict[str, Any]=None,
                image=None, img_input_file=None, img_input_file_enable:bool=True, img_input_type:str='jpeg',
                img_output_file:str=None, nodraw:bool=False,
                retry_count:int=3, retry_interval:int=5, timeout:int=60, logger:logging.Logger=None) -> Dict[str, Any]:
        """
        画像をRedisサーバーに送信し、推論結果を取得する

        Args:
            cl (client.Client): Redisサーバーへの接続クライアント
            vision_engine (str): 使用するVisionエンジン
            model_param (Dict[str, Any], optional): モデルのパラメータ. Defaults to None.
            image (np.ndarray | bytes, optional): 画像データ. Defaults to None. np.ndarray型の場合はデコードしない(RGBであること).
            img_input_file (str|file-like object, optional): 画像ファイルのパス. Defaults to None.
            img_input_file_enable (bool, optional): 画像ファイルを使用するかどうか. Defaults to True. img_input_fileがNoneでなく、このパラメーターがTrueの場合はimg_input_fileを使用する.
            img_input_type (str, optional): 画像の形式. Defaults to 'jpeg'.
            img_output_file (str, optional): 予測結果の画像ファイルのパス. Defaults to None.
            nodraw (bool, optional): 描画フラグ. Defaults to False.
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.
            logger (logging.Logger, optional): ロガー. Defaults to None.

        Returns:
            dict: Redisサーバーからの応答
        """
        spredtime = time.perf_counter()
        if vision_engine is None or vision_engine == "":
            logger.warning(f"vision_engine is empty.")
            return {"error": f"vision_engine is empty."}
        if image is None and img_input_file is None:
            logger.warning(f"image and img_input_file is empty.")
            return {"error": f"image and img_input_file is empty."}
        npy_b64 = None
        simgloadtime = time.perf_counter()
        if img_input_file is not None and img_input_file_enable:
            if type(img_input_file) == str:
                if not Path(img_input_file).exists():
                    logger.warning(f"Not found img_input_file. {img_input_file}.")
                    return {"error": f"Not found img_input_file. {img_input_file}."}
            if img_input_type == 'jpeg' or img_input_type == 'png' or img_input_type == 'bmp':
                f = None
                try:
                    f = img_input_file if type(img_input_file) is not str else open(img_input_file, "rb")
                    img_npy = convert.imgfile2npy(f)
                finally:
                    if f is not None: f.close()
            elif img_input_type == 'capture':
                f = None
                try:
                    f = img_input_file if type(img_input_file) is not str else open(img_input_file, "r", encoding='utf-8')
                    res_list = []
                    for line in f:
                        if type(line) is bytes:
                            line = line.decode('utf-8')
                        capture_data = line.strip().split(',')
                        t = capture_data[0]
                        img = capture_data[1]
                        h = int(capture_data[2])
                        w = int(capture_data[3])
                        c = int(capture_data[4])
                        fn = Path(capture_data[5].strip())
                        if t == 'capture':
                            img_npy = convert.b64str2npy(img, shape=(h, w, c) if c > 0 else (h, w))
                        else:
                            img_npy = convert.imgbytes2npy(convert.b64str2bytes(img))
                        res_json = self.predict(cl, vision_engine, model_param=model_param,
                                                image=img_npy, img_input_file=fn, img_input_file_enable=False,
                                                img_output_file=img_output_file, nodraw=nodraw,
                                                retry_count=retry_count, retry_interval=retry_interval, timeout=timeout,
                                                logger=logger)
                        res_list.append(res_json)
                    if len(res_list) <= 0:
                        return {"warn": f"capture file is no data."}
                    elif len(res_list) == 1:
                        return res_list[0]
                    return res_list
                except UnicodeDecodeError as e:
                    logger.error(f"capture file or img_input_type setting is invalid. img_input_type={img_input_type}. {e}", exc_info=True)
                    return {"error": f"capture file or img_input_type setting is invalid. img_input_type={img_input_type}. {e}"}
                finally:
                    if f is not None: f.close()
            else:
                logger.warning(f"img_input_type is invalid. {img_input_type}.")
                return {"error": f"img_input_type is invalid. {img_input_type}."}
        else:
            if type(image) == np.ndarray:
                img_npy = image
                if img_input_file is None: img_input_file = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.capture'
                img_input_file_enable = False
            elif img_input_type == 'capture':
                image = image.decode(encoding="utf-8") if type(image) is bytes else image
                capture_data = image.split(',')
                if len(capture_data) < 6:
                    logger.warning(f"capture data is invalid. {image}.")
                    return {"error": f"capture data is invalid. {image}."}
                t = capture_data[0]
                img = capture_data[1]
                h = int(capture_data[2])
                w = int(capture_data[3])
                c = int(capture_data[4])
                if img_input_file is None: img_input_file = capture_data[5]
                img_input_file_enable = False
                if t == 'capture':
                    img_npy = convert.b64str2npy(img, shape=(h, w, c) if c > 0 else (h, w))
                else:
                    img_npy = convert.imgbytes2npy(convert.b64str2bytes(img))
            elif img_input_type == 'output_json':
                res_json = json.loads(image)
                if not ("output_image" in res_json and "output_image_shape" in res_json and "output_image_name" in res_json):
                    logger.warning(f"img_input_file data is invalid. Not found output_image or output_image_shape or output_image_name key.")
                    return {"error": f"img_input_file data is invalid. Not found output_image or output_image_shape or output_image_name key."}
                if res_json["output_image_name"].endswith(".capture"):
                    img_npy = convert.b64str2npy(res_json["output_image"], shape=res_json["output_image_shape"])
                else:
                    img_bytes = convert.b64str2bytes(res_json["output_image"])
                    img_npy = convert.imgbytes2npy(img_bytes)
                if img_input_file is None: img_input_file = res_json["output_image_name"]
                img_input_file_enable = False
            elif img_input_type == 'jpeg' or img_input_type == 'png' or img_input_type == 'bmp':
                img_npy = convert.imgbytes2npy(image)
                if img_input_file is None: img_input_file = f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S%f")}.{img_input_type}'
                img_input_file_enable = False
            else:
                logger.warning(f"img_input_type is invalid. {img_input_type}.")
                return {"error": f"img_input_type is invalid. {img_input_type}."}

        eimgloadtime = time.perf_counter()
        img_npy_b64 = convert.npy2b64str(img_npy)
        model_param_b64 = convert.str2b64str(common.to_str(model_param))
        img_input_file_b64 = convert.str2b64str(img_input_file)
        res_json = cl.redis_cli.send_cmd('predict',
                                [vision_engine, model_param_b64,
                                 img_npy_b64, str(img_npy.shape[0]), str(img_npy.shape[1]), str(img_npy.shape[2] if len(img_npy.shape) > 2 else '-1'),
                                 img_input_file_b64, str(nodraw),],
                                retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)

        soutputtime = time.perf_counter()
        if "output_image" in res_json and "output_image_shape" in res_json:
            img_npy = convert.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
            if img_output_file is not None:
                exp = Path(img_output_file).suffix
                exp = exp[1:] if exp[0] == '.' else exp
                convert.npy2imgfile(img_npy, output_image_file=img_output_file, image_type=exp)
        eoutputtime = time.perf_counter()
        epredtime = time.perf_counter()
        if "success" in res_json:
            if "performance" not in res_json["success"]:
                res_json["success"]["performance"] = []
            performance = res_json["success"]["performance"]
            performance.append(dict(key="cl_imgload", val=f"{eimgloadtime-simgloadtime:.3f}s"))
            performance.append(dict(key="cl_output", val=f"{eoutputtime-soutputtime:.3f}s"))
            performance.append(dict(key="cl_pred", val=f"{epredtime-spredtime:.3f}s"))
        return res_json

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
        reskey = msg[1]
        vision_engine = convert.b64str2str(msg[2])
        model_param = json.loads(convert.b64str2str(msg[3]))
        shape = [int(msg[5]), int(msg[6])]
        if int(msg[7]) > 0: shape.append(int(msg[7]))
        img_npy = convert.b64str2npy(msg[4], shape=shape)
        img_input_file = convert.b64str2str(msg[8])
        nodraw = convert.b64str2str(msg[9]) == 'True'

        if vision_engine == 'sam2':
            sam2_model = model_param['sam2_model']
            sam2_point = model_param['sam2_point']
            sam2_label = model_param['sam2_label']
            st = self.sam2_predict(reskey, sam2_model, img_npy, sam2_point, sam2_label, data_dir, logger, redis_cli, sessions)
            raise NotImplementedError("SAM2 model is not implemented yet.")
        else:
            logger.warning(f"Unsupported vision engine: {vision_engine}")
            redis_cli.rpush(reskey, dict(warn=f"Unsupported vision engine: {vision_engine}"))
            return self.RESP_WARN

    def sam2_predict(self, reskey:str, sam2_model:str, img_npy:np.ndarray, sam2_point:List[List[int]], sam2_label:List[int],
                     data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, sessions:Dict[str, Dict[str, Any]]) -> Tuple[int, Dict[str, Any]]:
        """
        SAM2のモデルを使用して指定したポイントのマスクを取得します

        Args:
            reskey (str): レスポンスキー
            vision_engine (str): Visionエンジン
            sam2_model (str): SAM2モデル
            img_npy (np.ndarray): 入力画像
            sam2_point (List[List[int,int]]): SAM2モデルのポイント
            sam2_label (List[int]): SAM2モデルのラベル
            data_dir (Path): データディレクトリ
            logger (logging.Logger): ロガー
            redis_cli (redis_client.RedisClient): Redisクライアント
            sessions (Dict[str, Dict[str, Any]]): セッション情報

        Returns:
            Tuple[int, Dict[str, Any]]
        """
        if 'vision' not in sessions or 'sam2' not in sessions['vision'] or sam2_model not in sessions['vision']['sam2'] or sessions['vision']['sam2'][sam2_model] is None:
            return self.RESP_WARN, dict(warn=f"The vision session has not started.Unsupported SAM2 model: {sam2_model}")
        session = sessions['vision']['sam2'][sam2_model]
        from sam2.sam2_image_predictor import SAM2ImagePredictor
        info = session.get('info', None)
        predictor:SAM2ImagePredictor = session.get('predictor', None)
        if info is None or predictor is None:
            return self.RESP_WARN, dict(warn=f"The vision session has not started.Unsupported SAM2 model: {sam2_model}")
        predictor.set_image(img_npy)
        input_point = np.array(sam2_point, dtype=np.float32)
        input_label = np.array(sam2_label, dtype=np.int32)
        masks, scores, logits = predictor.predict(
            point_coords=input_point,
            point_labels=input_label,
            multimask_output=True,
        )
        raise NotImplementedError("SAM2 model is not implemented yet.")

    def draw_mask(img_npy:np.ndarray, mask_npy:np.ndarray):
        """
        マスクを描画する関数

        """
        from PIL import Image, ImageDraw
        img = convert.npy2img(img_npy)
        img = img.convert("RGBA")
        draw = ImageDraw.Draw(img)
        #h, w = img.size
        #mask_npy = mask_npy.reshape(h, w, 1) * color.reshape(1, 1, -1)
        mask_pil = Image.fromarray((mask_npy * 255).astype(np.uint8)).convert("L")
        mask_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
        mask_color = np.array([*cmap(cmap_idx)[:3], 0.6])
        
        for x in range(mask_pil.width):
            for y in range(mask_pil.height):
                if mask_pil.getpixel((x, y)) > 0:
                    mask_img.putpixel((x, y), (mask_color[0], mask_color[1], mask_color[2], int(255 * mask_color[3])))
        img_comb = Image.alpha_composite(img, mask_img)
        return img_comb
