from pathlib import Path
from cmdbox.app import filer
from cmdbox.app.commons import convert, redis_client
import base64
import logging


class Client(object):
    def __init__(self, logger:logging.Logger, redis_host:str = "localhost", redis_port:int = 6379, redis_password:str = None, svname:str = 'server'):
        """
        Redisサーバーとの通信を行うクラス

        Args:
            logger (logging): ロガー
            redis_host (str, optional): Redisサーバーのホスト名. Defaults to "localhost".
            redis_port (int, optional): Redisサーバーのポート番号. Defaults to 6379.
            redis_password (str, optional): Redisサーバーのパスワード. Defaults to None.
            svname (str, optional): サーバーのサービス名. Defaults to 'server'.
        """
        self.logger = logger
        if svname is None or svname == "":
            raise Exception("svname is empty.")
        if svname.find('-') >= 0:
            raise ValueError(f"Server name is invalid. '-' is not allowed. svname={svname}")
        self.redis_cli = redis_client.RedisClient(logger, host=redis_host, port=redis_port, password=redis_password, svname=svname)
        self.is_running = False

    def __exit__(self, a, b, c):
        pass

    def stop_server(self, retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        Redisサーバーを停止する

        Args:
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        res_json = self.redis_cli.send_cmd('stop_server', [], retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
        return res_json
    
    def file_list(self, svpath:str, recursive:bool, scope:str="client", client_data:Path = None,
                  retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        サーバー上のファイルリストを取得する

        Args:
            svpath (Path): サーバー上のファイルパス
            recursive (bool): 再帰的に取得するかどうか
            scope (str, optional): 参照先のスコープ. Defaults to "client".
            client_data (Path, optional): ローカルを参照させる場合のデータフォルダ. Defaults to None.
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if scope == "client":
            if client_data is not None:
                f = filer.Filer(client_data, self.logger)
                _, res_json = f.file_list(svpath, recursive)
                return res_json
            else:
                self.logger.warning(f"client_data is empty.")
                return {"error": f"client_data is empty."}
        elif scope == "current":
            f = filer.Filer(Path.cwd(), self.logger)
            _, res_json = f.file_list(svpath, recursive)
            return res_json
        elif scope == "server":
            res_json = self.redis_cli.send_cmd('file_list', [convert.str2b64str(str(svpath)), str(recursive)],
                                            retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
            return res_json
        else:
            self.logger.warning(f"scope is invalid. {scope}")
            return {"error": f"scope is invalid. {scope}"}

    def file_mkdir(self, svpath:str, scope:str="client", client_data:Path = None,
                   retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        サーバー上にディレクトリを作成する

        Args:
            svpath (Path): サーバー上のディレクトリパス
            scope (str, optional): 参照先のスコープ. Defaults to "client".
            client_data (Path, optional): ローカルを参照させる場合のデータフォルダ. Defaults to None.
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if scope == "client":
            if client_data is not None:
                f = filer.Filer(client_data, self.logger)
                _, res_json = f.file_mkdir(svpath)
                return res_json
            else:
                self.logger.warning(f"client_data is empty.")
                return {"error": f"client_data is empty."}
        elif scope == "current":
            f = filer.Filer(Path.cwd(), self.logger)
            _, res_json = f.file_mkdir(svpath)
            return res_json
        elif scope == "server":
            res_json = self.redis_cli.send_cmd('file_mkdir', [convert.str2b64str(str(svpath))],
                                            retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
            return res_json
        else:
            self.logger.warning(f"scope is invalid. {scope}")
            return {"error": f"scope is invalid. {scope}"}
    
    def file_rmdir(self, svpath:str, scope:str="client", client_data:Path = None,
                   retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        サーバー上のディレクトリを削除する

        Args:
            svpath (Path): サーバー上のディレクトリパス
            scope (str, optional): 参照先のスコープ. Defaults to "client".
            client_data (Path, optional): ローカルを参照させる場合のデータフォルダ. Defaults to None.
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if scope == "client":
            if client_data is not None:
                f = filer.Filer(client_data, self.logger)
                _, res_json = f.file_rmdir(svpath)
                return res_json
            else:
                self.logger.warning(f"client_data is empty.")
                return {"error": f"client_data is empty."}
        elif scope == "current":
            f = filer.Filer(Path.cwd(), self.logger)
            _, res_json = f.file_rmdir(svpath)
            return res_json
        elif scope == "server":
            res_json = self.redis_cli.send_cmd('file_rmdir', [convert.str2b64str(str(svpath))],
                                            retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
            return res_json
        else:
            self.logger.warning(f"scope is invalid. {scope}")
            return {"error": f"scope is invalid. {scope}"}
    
    def file_download(self, svpath:str, download_file:Path, scope:str="client", client_data:Path = None, rpath:str="", img_thumbnail:float=0.0,
                      retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        サーバー上のファイルをダウンロードする

        Args:
            svpath (Path): サーバー上のファイルパス
            download_file (Path): ローカルのファイルパス
            scope (str, optional): 参照先のスコープ. Defaults to "client".
            client_data (Path, optional): ローカルを参照させる場合のデータフォルダ. Defaults to None.
            rpath (str, optional): リクエストパス. Defaults to "".
            img_thumbnail (float, optional): サムネイル画像のサイズ. Defaults to 0.0.
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            bytes: ダウンロードファイルの内容
        """
        if scope == "client":
            if client_data is not None:
                f = filer.Filer(client_data, self.logger)
                _, res_json = f.file_download(svpath, img_thumbnail)
            else:
                self.logger.warning(f"client_data is empty.")
                return {"error": f"client_data is empty."}
        elif scope == "current":
            f = filer.Filer(Path.cwd(), self.logger)
            _, res_json = f.file_download(svpath, img_thumbnail)
        elif scope == "server":
            res_json = self.redis_cli.send_cmd('file_download', [convert.str2b64str(str(svpath)), str(img_thumbnail)],
                                               retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
        else:
            self.logger.warning(f"scope is invalid. {scope}")
            return {"error": f"scope is invalid. {scope}"}
        if "success" in res_json:
            res_json["success"]["rpath"] = rpath
            res_json["success"]["svpath"] = svpath
            if download_file is not None:
                if download_file.is_dir():
                    download_file = download_file / res_json["success"]["name"]
                if download_file.exists():
                    self.logger.warning(f"download_file {download_file} already exists.")
                    return {"error": f"download_file {download_file} already exists."}
                with open(download_file, "wb") as f:
                    f.write(base64.b64decode(res_json["success"]["data"]))
                    del res_json["success"]["data"]
                    res_json["success"]["download_file"] = str(download_file.absolute())
        return res_json
    
    def file_upload(self, svpath:str, upload_file:Path, scope:str="client", client_data:Path=None, mkdir:bool=False, orverwrite:bool=False,
                    retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        サーバー上にファイルをアップロードする

        Args:
            svpath (Path): サーバー上のファイルパス
            upload_file (Path): ローカルのファイルパス
            scope (str, optional): 参照先のスコープ. Defaults to "client".
            mkdir (bool, optional): ディレクトリを作成するかどうか. Defaults to False.
            orverwrite (bool, optional): 上書きするかどうか. Defaults to False.
            client_data (Path, optional): ローカルを参照させる場合のデータフォルダ. Defaults to None.
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if upload_file is None:
            self.logger.warning(f"upload_file is empty.")
            return {"error": f"upload_file is empty."}
        if not upload_file.exists():
            self.logger.warning(f"input_file {upload_file} does not exist.")
            return {"error": f"input_file {upload_file} does not exist."}
        if upload_file.is_dir():
            self.logger.warning(f"input_file {upload_file} is directory.")
            return {"error": f"input_file {upload_file} is directory."}
        with open(upload_file, "rb") as f:
            if scope == "client":
                if client_data is not None:
                    fi = filer.Filer(client_data, self.logger)
                    _, res_json = fi.file_upload(svpath, upload_file.name, f.read(), mkdir, orverwrite)
                    return res_json
                else:
                    self.logger.warning(f"client_data is empty.")
                    return {"error": f"client_data is empty."}
            elif scope == "current":
                fi = filer.Filer(Path.cwd(), self.logger)
                _, res_json = fi.file_upload(svpath, upload_file.name, f.read(), mkdir, orverwrite)
                return res_json
            elif scope == "server":
                res_json = self.redis_cli.send_cmd('file_upload',
                                    [convert.str2b64str(str(svpath)),
                                    convert.str2b64str(upload_file.name),
                                    convert.bytes2b64str(f.read()),
                                    str(mkdir),
                                    str(orverwrite)],
                                    retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
                return res_json
            else:
                self.logger.warning(f"scope is invalid. {scope}")
                return {"error": f"scope is invalid. {scope}"}

    def file_remove(self, svpath:str, scope:str="client", client_data:Path = None,
                    retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        サーバー上のファイルを削除する

        Args:
            svpath (Path): サーバー上のファイルパス
            scope (str, optional): 参照先のスコープ. Defaults to "client".
            client_data (Path, optional): ローカルを参照させる場合のデータフォルダ. Defaults to None.
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        if scope == "client":
            if client_data is not None:
                f = filer.Filer(client_data, self.logger)
                _, res_json = f.file_remove(svpath)
                return res_json
            else:
                self.logger.warning(f"client_data is empty.")
                return {"error": f"client_data is empty."}
        elif scope == "current":
            f = filer.Filer(Path.cwd(), self.logger)
            _, res_json = f.file_remove(svpath)
            return res_json
        elif scope == "server":
            res_json = self.redis_cli.send_cmd('file_remove', [convert.str2b64str(str(svpath))],
                                            retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
            return res_json
        else:
            self.logger.warning(f"scope is invalid. {scope}")
            return {"error": f"scope is invalid. {scope}"}

    def file_copy(self, from_path:str, to_path:str, orverwrite:bool=False, scope:str="client", client_data:Path = None,
                    retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        サーバー上のファイルをコピーする

        Args:
            from_path (Path): コピー元のファイルパス
            to_path (Path): コピー先のファイルパス
            orverwrite (bool, optional): 上書きするかどうか. Defaults to False.
            scope (str, optional): 参照先のスコープ. Defaults to "client".
            client_data (Path, optional): ローカルを参照させる場合のデータフォルダ. Defaults to None.
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.
        
        Returns:
            dict: Redisサーバーからの応答
        """
        if scope == "client":
            if client_data is not None:
                f = filer.Filer(client_data, self.logger)
                _, res_json = f.file_copy(from_path, to_path, orverwrite)
                return res_json
            else:
                self.logger.warning(f"client_data is empty.")
                return {"error": f"client_data is empty."}
        elif scope == "current":
            f = filer.Filer(Path.cwd(), self.logger)
            _, res_json = f.file_copy(from_path, to_path, orverwrite)
            return res_json
        elif scope == "server":
            res_json = self.redis_cli.send_cmd('file_copy', [convert.str2b64str(str(from_path)), convert.str2b64str(str(to_path)), str(orverwrite)],
                                            retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
            return res_json
        else:
            self.logger.warning(f"scope is invalid. {scope}")
            return {"error": f"scope is invalid. {scope}"}

    def file_move(self, from_path:str, to_path:str, scope:str="client", client_data:Path = None,
                    retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        サーバー上のファイルを移動する

        Args:
            from_path (Path): 移動元のファイルパス
            to_path (Path): 移動先のファイルパス
            scope (str, optional): 参照先のスコープ. Defaults to "client".
            client_data (Path, optional): ローカルを参照させる場合のデータフォルダ. Defaults to None.
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.
        
        Returns:
            dict: Redisサーバーからの応答
        """
        if scope == "client":
            if client_data is not None:
                f = filer.Filer(client_data, self.logger)
                _, res_json = f.file_move(from_path, to_path)
                return res_json
            else:
                self.logger.warning(f"client_data is empty.")
                return {"error": f"client_data is empty."}
        elif scope == "current":
            f = filer.Filer(Path.cwd(), self.logger)
            _, res_json = f.file_move(from_path, to_path)
            return res_json
        elif scope == "server":
            res_json = self.redis_cli.send_cmd('file_move', [convert.str2b64str(str(from_path)), convert.str2b64str(str(to_path))],
                                            retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
            return res_json
        else:
            self.logger.warning(f"scope is invalid. {scope}")
            return {"error": f"scope is invalid. {scope}"}

    def server_info(self, retry_count:int=3, retry_interval:int=5, timeout:int = 60):
        """
        サーバーの情報を取得する

        Args:
            retry_count (int, optional): リトライ回数. Defaults to 3.
            retry_interval (int, optional): リトライ間隔. Defaults to 5.
            timeout (int, optional): タイムアウト時間. Defaults to 60.

        Returns:
            dict: Redisサーバーからの応答
        """
        res_json = self.redis_cli.send_cmd('server_info', [], retry_count=retry_count, retry_interval=retry_interval, timeout=timeout)
        return res_json
