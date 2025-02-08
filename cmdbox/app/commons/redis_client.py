from cmdbox.app import common
from cmdbox.app.commons import convert
from PIL import Image
from typing import List, Dict, Any
import datetime
import logging
import json
import redis
import time


class RedisClient(object):
    def __init__(self, logger:logging.Logger, host:str = "localhost", port:int = 6379, password:str = None, svname:str="server"):
        """
        Redisクライアントを初期化します。
        
        Args:
            logger (Logger): ロガー
            host (str): Redisのホスト名
            port (int): Redisのポート番号
            password (str): Redisのパスワード
            svname (str): サーバー名
        """
        self.logger = logger
        self.host = host
        self.port = port
        self.password = password
        self.svname = f"sv-{svname}"
        self.hbname = f"hb-{svname}"
        self.siname = f"showimg-{svname}"
        self.redis_cli = self.connect()

    def connect(self):
        """
        Redisに接続します。
        """
        return redis.Redis(host=self.host, port=self.port, db=0, password=self.password)
    
    def close(self):
        if self.redis_cli is not None:
            self.redis_cli.close()
            self.redis_cli = None
    
    def rpush(self, name:str, value:dict):
        if type(value) is dict or type(value) is list:
            self.redis_cli.rpush(name, json.dumps(value, default=common.default_json_enc))
        elif type(value) is str:
            self.redis_cli.rpush(name, value)
        else:
            self.logger.warning(f"Unsupported type. {type(value)}")
            raise Exception(f"Unsupported type. {type(value)}")

    def blpop(self, name:str, timeout:int=1):
        return self.redis_cli.blpop(name, timeout=timeout)

    def lpop(self, name:str):
        return self.redis_cli.lpop(name)

    def hset(self, name:str, key:str, value):
        self.redis_cli.hset(name, key, str(value))

    def delete(self, name:str):
        self.redis_cli.delete(name)
    
    def hexists(self, name:str, key:str):
        return self.redis_cli.hexists(name, key)
    
    def hget(self, name:str, key:str):
        return self.redis_cli.hget(name, key)

    def keys(self, pattern:str):
        return self.redis_cli.keys(pattern)

    def check_server(self, find_svname:bool=False, retry_count:int=20, retry_interval:int=5, outstatus:bool=False):
        """
        Redisサーバーにpingを送信し、応答があるか確認する

        Args:
            find_svname (bool, optional): サーバー名が存在するか確認する. Defaults to False.
            retry_count (int, optional): リトライ回数. Defaults to 20.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            outstatus (bool, optional): ステータスを出力する. Defaults to False.

        Returns:
            bool: 接続成功時はTrue、失敗時はFalse
        """
        if retry_interval <= 0:
            self.logger.warning(f"retry_interval must be greater than 0. retry_interval={retry_interval}", exc_info=True)
            return False

        i = 0
        while i < retry_count or retry_count <= 0:
            try:
                if outstatus:
                    self.logger.info(f"({i+1}/{retry_count if retry_count>0 else '-'}) connecting to the redis server. {self.host}:{self.port}")
                self.redis_cli.ping()
                if find_svname:
                    _hbname = f"{self.hbname}-*" if len(self.hbname.split('-')) < 3 else self.hbname
                    found = self.redis_cli.keys(_hbname)
                    if len(found) <= 0:
                        self.logger.warning(f"Server not found. svname={self.svname.split('-')[1]}")
                        return False
                i = 0
                return True
            except redis.exceptions.ConnectionError as e:
                self.logger.warning(f"fail to ping server. {e}")
                if i >= retry_count and retry_count > 0:
                    return False
                time.sleep(retry_interval if retry_interval > 0 else 5)
                i += 1
            except KeyboardInterrupt as e:
                return False

    def send_cmd(self, cmd:str, params:List[str], retry_count:int=20, retry_interval:int=5, outstatus:bool=False, timeout:int = 60):
        """
        コマンドをRedisサーバーに送信し、応答を取得する

        Args:
            cmd (str): コマンド
            params (List[str]): コマンドのパラメータ
            retry_count (int, optional): リトライ回数. Defaults to 20.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            outstatus (bool, optional): ステータスを出力する. Defaults to False.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        try:
            if timeout <= 0:
                raise ValueError(f"timeout must be greater than 0. timeout={timeout}")
            sreqtime = time.perf_counter()
            if not self.check_server(find_svname=True, retry_count=retry_count, retry_interval=retry_interval, outstatus=outstatus):
                return dict(error=f"Connected server failed or server not found. svname={self.svname.split('-')[1]}")
            reskey = common.random_string()
            reskey = f"cl-{reskey}-{int(time.time())}"
            self.redis_cli.rpush(self.svname, f"{cmd} {reskey} {' '.join([str(p) for p in params])}")
            self.is_running = True
            stime = time.time()
            while self.is_running:
                ctime = time.time()
                if ctime - stime > timeout:
                    raise Exception(f"Response timed out.")
                res = self.redis_cli.lpop(reskey)
                if res is None or len(res) <= 0:
                    time.sleep(0.001)
                    continue
                return self._res_cmd(reskey, res, sreqtime)
            raise KeyboardInterrupt(f"Stop command.")
        except KeyboardInterrupt as e:
            self.logger.warning(f"Stop command. cmd={cmd}", exc_info=True)
            return dict(error=f"Stop command. cmd={cmd}")
        except Exception as e:
            self.logger.warning(f"fail to execute command. cmd={cmd}, msg={e}", exc_info=True)
            return dict(error=f"fail to execute command. cmd={cmd}, msg={e}")

    def _res_cmd(self, reskey:str, res_msg:bytes, sreqtime:float):
        """
        Redisサーバーからの応答を解析する

        Args:
            reskey (str): Redisサーバーからの応答のキー
            res_msg (bytes): Redisサーバーからの応答

        Returns:
            dict: 解析された応答
        """
        self.redis_cli.delete(reskey)
        reskbyte = len(res_msg) / 1024
        msg = res_msg.decode('utf-8')
        res_json = json.loads(msg)
        msg_json = res_json.copy()
        if "output_image" in msg_json:
            msg_json["output_image"] = "binary"
        if "error" in res_json:
            self.logger.warning(common.to_str(msg_json))
        if "warn" in res_json:
            self.logger.warning(common.to_str(msg_json))
        if "success" in res_json:
            if self.logger.level == logging.DEBUG:
                msg_str = common.to_str(msg_json, slise=100)
                self.logger.debug(f"redis_client._res_cmd: msg={msg_str}")
            if type(res_json["success"]) is not dict:
                res_json["success"] = dict(data=res_json["success"])
            if "performance" not in res_json["success"]:
                res_json["success"]["performance"] = []
            performance = res_json["success"]["performance"]
            performance.append(dict(key="cl_svreqest", val=f"{time.perf_counter()-sreqtime:.3f}s"))
            performance.append(dict(key="cl_reskbyte", val=f"{reskbyte:.3f}KB"))
        return res_json

    def receive_showimg(self):
        if not self.check_server(find_svname=False):
            return None, None
        result = self.lpop(self.siname)
        if result is None or len(result) <= 0:
            return None, None
        msg = result.decode().split(' ')
        if self.logger.level == logging.DEBUG:
            msg_str = common.to_str(msg, slise=100)
            self.logger.debug(f"redis_client.receive_showimg: self.siname={self.siname}, msg={msg_str}")
        if len(msg) <= 0:
            return None, None
        cmd = msg[0]
        if cmd == "text":
            value = convert.b64str2str(msg[1])
            return cmd, value
        elif cmd == "outputs":
            value = convert.b64str2str(msg[1])
            ret = cmd, json.loads(value)
            return ret
        elif cmd == "output_image":
            line = convert.b64str2str(msg[1])
            capture_data = line.split(',')
            t = capture_data[0]
            img = capture_data[1]
            h = int(capture_data[2])
            w = int(capture_data[3])
            c = int(capture_data[4])
            filename = capture_data[5]
            img_npy = convert.b64str2npy(img, shape=(h, w, c) if c > 0 else (h, w))
            img_bytes = convert.npy2imgfile(img_npy)
            return cmd, (filename, img_bytes)
        else:
            self.logger.warning(f"Unsupported cmd. cmd={cmd}")
            return None, None

    def send_showimg(self, cmd:str, outputs:Dict[str, Any], output_image:Image.Image=None, maxrecsize:int=200):
        """
        後処理結果をRedisサーバーに送信する

        Args:
            cmd (str): コマンド
            outputs (Dict[str, Any]): 後処理結果
            output_image (Image.Image, optional): 画像データ. Defaults to None.
            maxrecsize (int, optional): 最大レコードサイズ. Defaults to 200.
        """
        if cmd not in ["text", "outputs", "output_image"]:
            self.logger.warning(f"Unsupported cmd. cmd={cmd}")
            return dict(warn=f"Unsupported cmd. cmd={cmd}")
        if not self.check_server(find_svname=True):
            return dict(error=f"Server chack failed. svname={self.svname.split('-')[1]}")
        llen = self.redis_cli.llen(self.siname)
        if llen > maxrecsize:
            self.logger.warning(f"Cancelled execution of showimg. '{self.siname}' list is full. llen={llen} maxrecsize={maxrecsize}")
            return dict(warn=f"Cancelled execution of showimg. '{self.siname}' list is full. llen={llen} maxrecsize={maxrecsize}")
        try:
            if cmd == "outputs":
                if self.logger.level == logging.DEBUG:
                    outputs_str = common.to_str(outputs, slise=100)
                    self.logger.debug(f"redis_client.send_showimg: self.siname={self.siname}, cmd={cmd}, outputs={outputs_str}")
                value = convert.str2b64str(json.dumps(outputs, default=common.default_json_enc))
                self.redis_cli.rpush(self.siname, f"{cmd} {value}")
            elif cmd == "output_image":
                img_npy = convert.img2npy(output_image)
                img_b64 = convert.npy2b64str(img_npy)
                output_image_name = outputs['output_image_name'] if 'output_image_name' in outputs else f'{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}.capture'
                img_line = f"capture,{img_b64},{img_npy.shape[0]},{img_npy.shape[1]},{img_npy.shape[2] if len(img_npy.shape) > 2 else -1}, {output_image_name}"
                value = convert.str2b64str(img_line)
                self.redis_cli.rpush(self.siname, f"{cmd} {value}")
            elif cmd == "text":
                value = convert.str2b64str(outputs)
                self.redis_cli.rpush(self.siname, f"{cmd} {value}")
            else:
                self.logger.warning(f"outputs are not supported type. {type(outputs)} cmd='{cmd}' llen={llen}. outputs={outputs}")
                return dict(warn=f"outputs are not supported type. {type(outputs)} cmd='{cmd}' llen={llen}. outputs={outputs}")
        except Exception as e:
            self.logger.warning(f"Failed to publish to Redis server. cmd='{cmd}' llen={llen}. {e}", exc_info=True)
            return dict(warn=f"Failed to publish to Redis server. cmd='{cmd}' llen={llen}. {e}")
        return dict(success=f"Success execution of showimg. cmd='{cmd}' llen={llen+1}.")

    def list_server(self) -> List[Dict[str, Any]]:
        """
        起動しているサーバーリストを取得する

        Returns:
            List[Dict[str, Any]]: サーバーのリスト
        """
        hblist = self.keys("hb-*")
        svlist = []
        for hb in hblist:
            hb = hb.decode()
            svname = hb.replace("hb-", "")
            try:
                val = self.hget(hb, 'receive_cnt')
                receive_cnt = int(val.decode()) if val is not None else 0
                val = self.hget(hb, 'sccess_cnt')
                sccess_cnt = int(val.decode()) if val is not None else 0
                val = self.hget(hb, 'warn_cnt')
                warn_cnt = int(val.decode()) if val is not None else 0
                val = self.hget(hb, 'error_cnt')
                error_cnt = int(val.decode()) if val is not None else 0
                val = self.hget(hb, 'status')
                status = val.decode() if val is not None else "unknown"
                val = self.hget(hb, 'ctime')
                ctime = time.strftime('%Y/%m/%d %H:%M:%S', time.localtime(float(val.decode()))) if val is not None else "-"
            except redis.exceptions.ResponseError:
                self.logger.warn(f"ResponseError. {hb}", exc_info=True)
            svlist.append(dict(svname=svname, status=status, ctime=ctime,
                               receive_cnt=receive_cnt, sccess_cnt=sccess_cnt, warn_cnt=warn_cnt, error_cnt=error_cnt))
        return svlist