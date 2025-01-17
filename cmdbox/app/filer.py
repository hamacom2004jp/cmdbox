from cmdbox.app import common
from cmdbox.app.commons import convert
from pathlib import Path
from typing import Dict, Any, Tuple
import logging
import datetime
import mimetypes
import shutil

class Filer(object):
    RESP_SCCESS:int = 0
    RESP_WARN:int = 1
    RESP_ERROR:int = 2
    def __init__(self, data_dir: Path, logger: logging.Logger,):
        self.data_dir = data_dir
        self.logger = logger
        common.mkdirs(self.data_dir)

    def _file_exists(self, current_path:str, not_exists:bool=False, exists_chk:bool=True) -> Tuple[bool, Path, Dict[str, Any]]:
        """
        パスが存在するかどうかを確認する

        Args:
            current_path (str): パス
            not_exists (bool, optional): パスが存在しないことを確認するかどうか, by default False
            exists_chk (bool, optional): パス存在チェックを行うかどうか, by default True
        
        Returns:
            bool: not_existsがFalseの時パスが存在すればTrue、存在しなければFalse。not_existsがTrueの時パスが存在しなければTrue、存在すればFalse。
            Path: データフォルダ以下のcurrent_pathを含めた絶対パス
            dict: メッセージ
        """
        if current_path is None or current_path == "":
            self.logger.warning(f"current_path is empty.")
            return False, None, {"warn": f"current_path is empty."}
        current_path = current_path.replace("\\","/").replace("//","/")
        cp = current_path[1:] if current_path.startswith('/') else current_path
        abspath:Path = (self.data_dir / cp).resolve()
        if not str(abspath).startswith(str(self.data_dir)):
            self.logger.warning(f"Path {abspath} is out of data directory. current_path={current_path}")
            return False, abspath, {"warn": f"Path {abspath} is out of data directory. current_path={current_path}"}
        if not exists_chk:
            return True, abspath, {"success": f"Path {abspath} not exists."}
        if not not_exists and not abspath.exists():
            self.logger.warning(f"Path {abspath} does not exist. param={current_path}")
            return False, abspath, {"warn": f"Path {abspath} does not exist. param={current_path}"}
        if not_exists and abspath.exists():
            self.logger.warning(f"Path {abspath} exist. param={current_path}")
            return False, abspath, {"warn": f"Path {abspath} exist. param={current_path}"}
        return True, abspath, {"success": f"Path {abspath} exists."}

    def file_list(self, current_path:str, recursive:bool=False) -> Tuple[int, Dict[str, Any]]:
        """
        ファイルリストを取得する

        Args:
            path (str): ファイルパス
            recursive (bool, optional): 再帰的に取得するかどうか, by default False

        Returns:
            int: レスポンスコード
            dict: メッセージ
        """
        chk, _, msg = self._file_exists(current_path)
        if not chk:
            return self.RESP_WARN, msg
        
        def _ts2str(ts):
            return datetime.datetime.fromtimestamp(ts)

        #current_path = f'/{current_path}' if not current_path.startswith('/') else current_path
        current_path_parts = current_path.replace('\\', '/').split("/")
        current_path_parts = current_path_parts[1:] if current_path=='/' else current_path_parts
        current_path_parts = ['.'] + current_path_parts if current_path_parts[0] not in ['','.'] else current_path_parts
        path_tree = {}
        data_dir_len = len(str(self.data_dir))

        def _path_tree(file_list:Path, cpart:str, i, recursive:bool=False):
            children = dict()
            if not file_list.is_dir():
                tparts = str(file_list)[data_dir_len:].replace("\\","/").split("/")
                tpath = "/".join(tparts[0:i+1])
                tpath = f'.{tpath}' if current_path_parts[0] == '.' else tpath
                #tpath = '/'.join(current_path_parts[:i+1])
                tpath = '/' if tpath=='' else tpath
                tpath_key = common.safe_fname(tpath)
                cpart = '/' if cpart=='' else cpart
                return tpath_key, dict(name=cpart,
                                   is_dir=False,
                                   path=tpath,
                                   children=children,
                                   size=file_list.stat().st_size,
                                   last=_ts2str(file_list.stat().st_mtime),
                                   depth=len(tparts))
            for f in sorted(list(file_list.iterdir())):
                parts = str(f)[data_dir_len:].replace("\\","/").split("/")
                path = "/".join(parts[0:i+2])
                path = f'.{path}' if current_path_parts[0] == '.' else path
                key = common.safe_fname(path)
                if key in children:
                    continue
                mime_type, encoding = mimetypes.guess_type(str(f))
                if recursive and f.is_dir():
                    _, path_tree = _path_tree(f, f.name, i+1, recursive)
                    children[key] = path_tree
                    continue
                children[key] = dict(name=f.name,
                                    is_dir=f.is_dir(),
                                    path=path,
                                    mime_type=mime_type,
                                    size=f.stat().st_size,
                                    last=_ts2str(f.stat().st_mtime),
                                    depth=len(parts))

            tparts = str(file_list)[data_dir_len:].replace("\\","/").split("/")
            tpath = "/".join(tparts[0:i+1])
            tpath = f'.{tpath}' if current_path_parts[0] == '.' else tpath
            #tpath = '/'.join(current_path_parts[:i+1])
            tpath = '/' if tpath=='' else tpath
            tpath_key = common.safe_fname(tpath)
            cpart = '/' if cpart=='' else cpart
            return tpath_key, dict(name=cpart,
                                   is_dir=True,
                                   path=tpath,
                                   children=children,
                                   size=0,
                                   last="",
                                   depth=len(tparts))
    
        for i, cpart in enumerate(current_path_parts):
            cpath = '/'.join(current_path_parts[1:i+1])
            file_list:Path = self.data_dir / cpath
            tpath_key, pt = _path_tree(file_list, cpart, i, recursive if i+1==len(current_path_parts) else False)
            path_tree[tpath_key] = pt
        return self.RESP_SCCESS, {"success": path_tree}
    
    def file_mkdir(self, current_path:str) -> Tuple[int, Dict[str, Any]]:
        """
        ディレクトリを作成する

        Args:
            current_path (str): ディレクトリパス

        Returns:
            int: レスポンスコード
            dict: メッセージ
        """
        chk, abspath, msg = self._file_exists(current_path, not_exists=True)
        if not chk:
            return self.RESP_WARN, msg

        try:
            abspath.mkdir(parents=True)
            ret_path = str(Path(current_path).parent).replace("\\","/")
            return self.RESP_SCCESS, {"success": {"path":f"{ret_path}","msg":f"Created {abspath}"}}
        except Exception as e:
            self.logger.warning(f"Failed to create {abspath}. {e}")
            return self.RESP_WARN, {"warn": f"Failed to create {abspath}. {e}"}
    
    def file_rmdir(self, current_path:str) -> Tuple[int, Dict[str, Any]]:
        """
        ディレクトリを削除する

        Args:
            current_path (str): ディレクトリパス

        Returns:
            int: レスポンスコード
            dict: メッセージ
        """
        chk, abspath, msg = self._file_exists(current_path)
        if not chk:
            return self.RESP_WARN, msg
        if abspath == self.data_dir:
            self.logger.warning(f"Path {abspath} is root directory.")
            return self.RESP_WARN, {"warn": f"Path {abspath} is root directory."}

        try:
            common.rmdirs(abspath, ignore_errors=False)
            ret_path = str(Path(current_path).parent).replace("\\","/")
            return self.RESP_SCCESS, {"success": {"path":f"{ret_path}","msg":f"Removed {abspath}"}}
        except Exception as e:
            self.logger.warning(f"Failed to remove {abspath}. {e}")
            return self.RESP_WARN, {"warn": f"Failed to remove {abspath}. {e}"}

    def file_download(self, current_path:str, img_thumbnail:float=0.0) -> Tuple[int, Dict[str, Any]]:
        """
        ファイルをダウンロードする

        Args:
            current_path (str): ファイルパス
            img_thumbnail (float, optional): サムネイルのサイズ, by default 0.0

        Returns:
            int: レスポンスコード
            dict: メッセージ
        """
        img_thumbnail = 0.0 if img_thumbnail is None else img_thumbnail
        chk, abspath, msg = self._file_exists(current_path)
        if not chk:
            return self.RESP_WARN, msg
        if abspath.is_dir():
            self.logger.warning(f"Path {abspath} is directory.")
            return self.RESP_WARN, {"warn": f"Path {abspath} is directory."}

        try:
            mime_type, encoding = mimetypes.guess_type(str(abspath))
            fname = abspath.name
            with open(abspath, "rb") as f:
                fd = f.read()
                if mime_type is not None and mime_type != 'image/svg+xml' and mime_type.startswith('image') and img_thumbnail > 0:
                    img = convert.imgbytes2thumbnail(fd, (img_thumbnail, img_thumbnail))
                    fd = convert.img2byte(img, "jpeg")
                    fname = f"{fname}.thumbnail.jpg"
                data = convert.bytes2b64str(fd)
            return self.RESP_SCCESS, {"success":{"name":fname, "data":data, "mime_type":mime_type}}
        except Exception as e:
            self.logger.warning(f"Failed to download {abspath}. {e}")
            return self.RESP_WARN, {"warn": f"Failed to download {abspath}. {e}"}

    def file_upload(self, current_path:str, file_name:str, file_data:bytes, mkdir:bool, orverwrite:bool) -> Tuple[int, Dict[str, Any]]:
        """
        ファイルをアップロードする

        Args:
            current_path (str): ファイルパス
            file_name (str): ファイル名
            file_data (bytes): ファイルデータ
            mkdir (bool): ディレクトリを作成するかどうか
            orverwrite (bool): 上書きするかどうか

        Returns:
            int: レスポンスコード
            dict: メッセージ
        """
        chk, abspath, msg = self._file_exists(current_path, exists_chk=False)
        if not chk:
            return self.RESP_WARN, msg

        if abspath.exists():
            if abspath.is_dir():
                abspath = abspath / file_name
            if abspath.is_file() and not orverwrite:
                self.logger.warning(f"Path {abspath} already exist. param={current_path}")
                return self.RESP_WARN, {"warn": f"Path {abspath} already exist. param={current_path}"}
            save_path = abspath
        elif abspath.suffix == '':
            abspath.mkdir(parents=True, exist_ok=True)
            save_path = abspath / file_name
        else:
            save_path = abspath
        try:
            if mkdir:
                save_path.parent.mkdir(parents=True, exist_ok=True)
            with open(save_path, "wb") as f:
                f.write(file_data)
            return self.RESP_SCCESS, {"success": f"Uploaded {save_path}"}
        except Exception as e:
            self.logger.warning(f"Failed to upload {save_path}. {e}")
            return self.RESP_WARN, {"warn": f"Failed to upload {save_path}. {e}"}

    def file_remove(self, current_path:str) -> Tuple[int, Dict[str, Any]]:
        """
        ファイルを削除する

        Args:
            current_path (str): ファイルパス

        Returns:
            int: レスポンスコード
            dict: メッセージ
        """
        chk, abspath, msg = self._file_exists(current_path)
        if not chk:
            return self.RESP_WARN, msg
        if abspath.is_dir():
            self.logger.warning(f"Path {abspath} is directory.")
            return self.RESP_WARN, {"warn": f"Path {abspath} is directory."}

        try:
            abspath.unlink()
            ret_path = str(Path(current_path).parent).replace("\\","/")
            return self.RESP_SCCESS, {"success": {"path":f"{ret_path}","msg":f"Removed {abspath}"}}
        except Exception as e:
            self.logger.warning(f"Failed to remove {abspath}. {e}")
            return self.RESP_WARN, {"warn": f"Failed to remove {abspath}. {e}"}

    def file_copy(self, from_path:str, to_path:str, orverwrite:bool) -> Tuple[int, Dict[str, Any]]:
        """
        ファイルをコピーする

        Args:
            from_path (str): コピー元パス
            to_path (str): コピー先パス
            orverwrite (bool): 上書きするかどうか

        Returns:
            int: レスポンスコード
            dict: メッセージ
        """
        chk, from_abspath, msg = self._file_exists(from_path)
        if not chk:
            return self.RESP_WARN, msg

        chk, to_abspath, msg = self._file_exists(to_path, not_exists=True)
        if not chk and not orverwrite:
            return self.RESP_WARN, msg
        if orverwrite and not to_abspath.parent.exists():
            to_abspath.parent.mkdir(parents=True, exist_ok=True)

        if from_abspath.is_dir():
            ret_path = shutil.copytree(from_abspath, to_abspath, dirs_exist_ok=True)
        elif from_abspath.is_file():
            ret_path = shutil.copy(from_abspath, to_abspath)
        else:
            self.logger.warning(f"Path {from_abspath} is not file or directory.")
            return self.RESP_WARN, {"warn": f"Path {from_abspath} is not file or directory."}

        return self.RESP_SCCESS, {"success": {"path":f"{Path(to_path).parent}",
                                              "to_path":f"{to_path}",
                                              "from_path":f"{from_path}",
                                              "ret_path":f"{ret_path}",
                                              "msg":f"Copy from '{from_path}' to '{to_path}'. write '{ret_path}'"}}

    def file_move(self, from_path:str, to_path:str) -> Tuple[int, Dict[str, Any]]:
        """
        ファイルを移動する

        Args:
            from_path (str): 移動元パス
            to_path (str): 移動先パス

        Returns:
            int: レスポンスコード
            dict: メッセージ
        """
        chk, from_abspath, msg = self._file_exists(from_path)
        if not chk:
            return self.RESP_WARN, msg

        chk, to_abspath, msg = self._file_exists(to_path, not_exists=True)
        if not chk:
            return self.RESP_WARN, msg

        ret_path = shutil.move(from_abspath, to_abspath)

        return self.RESP_SCCESS, {"success": {"path":f"{Path(to_path).parent}",
                                              "to_path":f"{to_path}",
                                              "from_path":f"{from_path}",
                                              "ret_path":f"{ret_path}",
                                              "msg":f"Move from '{from_path}' to '{to_path}'. write '{ret_path}'"}}
