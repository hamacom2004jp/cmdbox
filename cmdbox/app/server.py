from pathlib import Path
from cmdbox.app import common, filer, feature, options
from cmdbox.app.commons import redis_client
from redis import exceptions
from typing import List, Dict, Any
import logging
import redis
import time


class Server(filer.Filer):

    def __init__(self, data_dir:Path, logger:logging.Logger, redis_host:str="localhost", redis_port:int=6379, redis_password:str=None, svname:str='server'):
        """
        Redisサーバーに接続し、クライアントからのコマンドを受信し実行する

        Args:
            data_dir (Path): データフォルダのパス
            logger (logging): ロガー
            redis_host (str): Redisホスト名, by default "localhost"
            redis_port (int): Redisポート番号, by default 6379
            redis_password (str): Redisパスワード, by default None
            svname (str, optional): サーバーのサービス名. by default 'server'
        """
        super().__init__(data_dir, logger)
        if svname.find('-') >= 0:
            raise ValueError(f"Server name is invalid. '-' is not allowed. svname={svname}")
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.org_svname = svname
        self.svname = f"{svname}-{common.random_string(size=6)}"
        self.redis_cli = None
        self.sessions:Dict[str, Dict[str, Any]] = {}
        self.is_running = False
        self.train_thread = None
        self.cleaning_interval = 10
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"server init parameter: data={self.data_dir} -> {self.data_dir.absolute()}")
            self.logger.debug(f"server init parameter: redis_host={self.redis_host}")
            self.logger.debug(f"server init parameter: redis_port={self.redis_port}")
            self.logger.debug(f"server init parameter: redis_password=********")
            self.logger.debug(f"server init parameter: svname={self.svname}")
        self.options = options.Options.getInstance()

    def __enter__(self):
        self.start_server()
        return self

    def __exit__(self, a, b, c):
        self.terminate_server()

    def start_server(self, retry_count:int=20, retry_interval:int=5):
        """
        サーバー処理を開始する
        """
        self.is_running = False
        self.retry_count = retry_count
        self.retry_interval = retry_interval
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"server start parameter: retry_count={self.retry_count}")
            self.logger.debug(f"server start parameter: retry_interval={self.retry_interval}")
        self.redis_cli = redis_client.RedisClient(self.logger, host=self.redis_host, port=self.redis_port, password=self.redis_password, svname=self.svname)
        if self.redis_cli.check_server(find_svname=False, retry_count=self.retry_count, retry_interval=self.retry_interval, outstatus=True):
            self.is_running = True
            self._run_server()

    def list_server(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        起動しているサーバーリストを取得する

        Returns:
            Dict[str, List[Dict[str, Any]]]: サーバーのリスト
        """
        if self.redis_cli is None:
            self.redis_cli = redis_client.RedisClient(self.logger, host=self.redis_host, port=self.redis_port, password=self.redis_password, svname=self.svname)
        svlist = self.redis_cli.list_server()
        if len(svlist) <= 0:
            return {"warn": "No server is running."}
        return {"success": svlist}

    def _clean_server(self):
        """
        Redisサーバーに残っている停止済みのサーバーキーを削除する
        """
        hblist = self.redis_cli.keys("hb-*")
        for hb in hblist:
            hb = hb.decode()
            try:
                v = self.redis_cli.hget(hb, 'ctime')
                if v is None:
                    continue
            except exceptions.ResponseError:
                self.logger.warning(f"Failed to get ctime. {hb}", exc_info=True)
                continue
            tm = time.time() - float(v)
            if tm > self.cleaning_interval:
                self.redis_cli.delete(hb)
                self.redis_cli.delete(hb.replace("hb-", "sv-"))

    def _clean_reskey(self):
        """
        Redisサーバーに残っている停止済みのクライアントキーを削除する
        """
        rlist = self.redis_cli.keys("cl-*")
        for reskey in rlist:
            try:
                tm = int(reskey.decode().split("-")[2])
                if time.time() - tm > self.cleaning_interval:
                    self.redis_cli.delete(reskey)
            except Exception as e:
                self.redis_cli.delete(reskey)

    def _run_server(self):
        self.logger.info(f"start server. svname={self.svname}")
        ltime = time.time()
        receive_cnt = 0
        sccess_cnt = 0
        warn_cnt = 0
        error_cnt = 0
        self.redis_cli.hset(self.redis_cli.hbname, 'receive_cnt', receive_cnt)
        self.redis_cli.hset(self.redis_cli.hbname, 'sccess_cnt', sccess_cnt)
        self.redis_cli.hset(self.redis_cli.hbname, 'warn_cnt', warn_cnt)
        self.redis_cli.hset(self.redis_cli.hbname, 'error_cnt', error_cnt)

        def _publish(msg_str):
            # 各サーバーにメッセージを配布する
            hblist = self.redis_cli.keys(f"hb-{self.org_svname}-*")
            for hb in hblist:
                hb = hb.decode()
                sv = hb.replace("hb-", "sv-")
                self.redis_cli.rpush(sv, msg_str)

        while self.is_running:
            try:
                # ブロッキングリストから要素を取り出す
                ctime = time.time()
                self.redis_cli.hset(self.redis_cli.hbname, 'ctime', ctime)
                self.redis_cli.hset(self.redis_cli.hbname, 'status', 'ready')
                result = self.redis_cli.blpop(self.redis_cli.svname)
                if ctime - ltime > self.cleaning_interval:
                    self._clean_server()
                    self._clean_reskey()
                    ltime = ctime
                to_cluster = False
                if result is None or len(result) <= 0:
                    # クラスター宛メッセージがあるか確認する
                    result = self.redis_cli.blpop(f"sv-{self.org_svname}")
                    if result is None or len(result) <= 0:
                        time.sleep(1)
                        continue
                    to_cluster = True
                msg_str = result[1].decode()
                msg = msg_str.split(' ')
                if len(msg) <= 0:
                    time.sleep(1)
                    continue

                st = None
                receive_cnt += 1
                self.redis_cli.hset(self.redis_cli.hbname, 'receive_cnt', receive_cnt)
                self.redis_cli.hset(self.redis_cli.hbname, 'status', 'processing')

                svcmd_feature:feature.Feature = self.options.get_svcmd_feature(msg[0])
                if svcmd_feature is not None:
                    if to_cluster and svcmd_feature.is_cluster_redirect():
                        _publish(msg_str)
                        continue
                    if msg[0] == 'stop_server':
                        self.is_running = False
                    st = svcmd_feature.svrun(self.data_dir, self.logger, self.redis_cli, msg, self.sessions)
                else:
                    self.logger.warning(f"Unknown command {msg}")
                    st = self.RESP_WARN

                if st==self.RESP_SCCESS:
                    sccess_cnt += 1
                    self.redis_cli.hset(self.redis_cli.hbname, 'sccess_cnt', sccess_cnt)
                elif st==self.RESP_WARN:
                    warn_cnt += 1
                    self.redis_cli.hset(self.redis_cli.hbname, 'warn_cnt', warn_cnt)
                elif st==self.RESP_ERROR:
                    error_cnt += 1
                    self.redis_cli.hset(self.redis_cli.hbname, 'error_cnt', error_cnt)
                self.redis_cli.hset(self.redis_cli.hbname, 'ctime', time.time())
            except exceptions.TimeoutError:
                pass
            except exceptions.ConnectionError as e:
                self.logger.warning(f"Connection to the server was lost. {e}", exec_info=True)
                if not self.redis_cli.check_server(find_svname=False, retry_count=self.retry_count, retry_interval=self.retry_interval, outstatus=True):
                    self.is_running = False
                    break
            except OSError as e:
                self.logger.warning(f"OSError. {e}", exec_info=True)
                pass
            except KeyboardInterrupt as e:
                self.is_running = False
                break
            except Exception as e:
                self.logger.warning(f"Unknown error occurred. {e}", exc_info=True)
                self.is_running = False
                break
        self.redis_cli.delete(self.redis_cli.svname)
        self.redis_cli.delete(self.redis_cli.hbname)
        self.logger.info(f"stop server. svname={self.redis_cli.svname}")

    def terminate_server(self):
        """
        サーバー処理を終了する
        """
        self.redis_cli.close()
        self.logger.info(f"terminate server.")
