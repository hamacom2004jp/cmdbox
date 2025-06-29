from cmdbox.app import common
from cmdbox.app.commons import convert
from pathlib import Path
from typing import Dict, Any, Tuple
import logging
import requests
import webbrowser
import urllib.parse
import urllib3


class Tool(object):
    def __init__(self, logger:logging.Logger, appcls=None, ver=None):
        self.logger = logger
        self.appcls = appcls
        self.ver = ver

    def notify(self, message:dict):
        """
        通知メッセージを表示します

        Args:
            message (dict): メッセージ
        """
        if type(message) is list:
            message = message[0]
        if type(message) is not dict:
            message = {"info":str(message)}
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"notify: {common.to_str(message, slise=256)}")
        try:
            if 'success' in message and type(message['success']) == dict:
                message = "\n".join([f"{k}:{v}" for k, v in message['success'].items()])
                message = f'Success\n{message}'
            else:
                message = "\n".join([f"{k} : {v}" for k, v in message.items()])
            import plyer
            if hasattr(self, 'icon_path') and self.icon_path is not None:
                plyer.notification.notify(title=self.ver.__title__, message=str(message)[:256], app_icon=str(self.icon_path))
            else:
                plyer.notification.notify(title=self.ver.__title__, message=str(message)[:256])
        except Exception as e:
            self.logger.error(f"notify error. {e}", exc_info=True)

    def set_session(self, session:requests.Session, svcert_no_verify:bool, endpoint:str, icon_path:Path, user_info:Dict[str, Any], oauth2:str, saml:str):
        """
        セッションを設定します

        Args:
            session (requests.Session): セッション
            svcert_no_verify (bool): サーバー証明書の検証を行わない
            endpoint (str): エンドポイント
            icon_path (Path): アイコン画像のパス
            user_info (Dict[str, Any]): ユーザー情報
            oauth2 (str): OAuth2
        """
        self.session = session
        self.svcert_no_verify = svcert_no_verify
        self.endpoint = endpoint.rstrip('/')
        self.icon_path = icon_path
        self.user = user_info
        self.oauth2 = oauth2
        self.saml = saml

    def exec_cmd(self, opt:Dict[str, Any], logger:logging.Logger, timeout:int, prevres:Any=None) -> Tuple[int, Dict[str, Any]]:
        """
        この機能のエッジ側の実行を行います

        Args:
            opt (Dict[str, Any]): オプション
            logger (logging.Logger): ロガー
            timeout (int): タイムアウト時間
            prevres (Any): 前コマンドの結果。pipeline実行の実行結果を参照する時に使用します。

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果
        """
        if logger.level == logging.DEBUG:
            logger.debug(f"exec_cmd: {self.endpoint}/exec_cmd/{opt['title']}")
        if prevres is not None:
            headers = {'content-type':'application/octet-stream'}
            prevres = common.to_str(prevres)
            res = self.session.post(f"{self.endpoint}/exec_cmd/{opt['title']}", headers=headers, data=prevres,
                                    verify=not self.svcert_no_verify, timeout=timeout, allow_redirects=False)
        else:
            res = self.session.post(f"{self.endpoint}/exec_cmd/{opt['title']}",
                                    verify=not self.svcert_no_verify, timeout=timeout, allow_redirects=False)

        if res.status_code != 200:
            msg = dict(warn=f"Access failed. status_code={res.status_code}")
            logger.warning(f"Access failed. status_code={res.status_code}")
            return 1, msg
        else:
            ret = msg = res.json()
            if isinstance(msg, list):
                if len(msg) == 0:
                    logger.warning(f"No result.")
                    return 1, dict(warn="No result.")
                msg = msg[0]
            if isinstance(msg, dict) and 'success' not in msg:
                logger.warning(f"{msg}")
                return 1, ret
            if logger.level == logging.DEBUG:
                logger.debug(f"{common.to_str(ret, slise=255)}")
            return 0, ret

    def pub_result(self, title:str, output:str, timeout:int) -> Tuple[int, Dict[str, Any]]:
        """
        結果を公開します

        Args:
            title (str): タイトル
            output (str): 出力
            logger (logging.Logger): ロガー
            timeout (int): タイムアウト時間

        Returns:
            Tuple[int, Dict[str, Any]]: 終了コード, メッセージ
        """
        output = common.to_str(output)
        data = f'title={urllib.parse.quote(title)}&output={urllib.parse.quote(output)}'
        headers = {'content-type':'application/x-www-form-urlencoded'}
        res = self.session.post(f"{self.endpoint}/result/pub", headers=headers, data=data,
                                verify=not self.svcert_no_verify, timeout=timeout, allow_redirects=False)
        if res.status_code != 200:
            msg = dict(warn=f"Access failed. status_code={res.status_code}")
            return 1, msg
        else:
            msg = res.json()
            return 0, msg

    def open_browser(self, path:str) -> Tuple[int, Dict[str, str]]:
        """
        指定したパスをブラウザで開きます。
        この時認証情報を含めて開きます。

        Args:
            path (str): パス

        Returns:
            Tuple[int, Dict[str, str]]: 終了コード, メッセージ
        """
        path = f"/{path}" if not path.startswith('/') else path
        if not hasattr(self, 'user'):
            webbrowser.open(f"{self.endpoint}{path}")
            return 0, dict(success="Open browser.")
        token = dict(auth_type=self.user['auth_type'])
        if self.user['auth_type'] == "noauth":
            webbrowser.open(f"{self.endpoint}{path}")
            return 0, dict(success="Open browser.")
        elif self.user['auth_type'] == "idpw":
            hashed = self.user['password'] if self.user['hash']=='plain' else common.hash_password(self.user['password'], self.user['hash'])
            token = dict(**token, **dict(user=self.user['name'], token=common.encrypt(path, hashed)))
            token = convert.str2b64str(common.to_str(token))
            webbrowser.open(f"{self.endpoint}/dosignin_token/{token}{path}")
            return 0, dict(success="Open browser.")
        elif self.user['auth_type'] == "apikey":
            hashed = common.hash_password(self.user['apikey'], 'sha1')
            token = dict(**token, **dict(user=self.user['name'], token=common.encrypt(path, hashed)))
            token = convert.str2b64str(common.to_str(token))
            webbrowser.open(f"{self.endpoint}/dosignin_token/{token}{path}")
            return 0, dict(success="Open browser.")
        elif self.user['auth_type'] == "oauth2":
            if self.oauth2 == 'google':
                webbrowser.open(f"{self.endpoint}/oauth2/google/session/{self.user['access_token']}{path}")
                return 0, dict(success="Open browser.")
            if self.oauth2 == 'github':
                webbrowser.open(f"{self.endpoint}/oauth2/github/session/{self.user['access_token']}{path}")
                return 0, dict(success="Open browser.")
            if self.oauth2 == 'azure':
                webbrowser.open(f"{self.endpoint}/oauth2/azure/session/{self.user['access_token']}{path}")
                return 0, dict(success="Open browser.")
        elif self.user['auth_type'] == "saml":
            if self.saml == 'azure':
                webbrowser.open(f"{self.endpoint}/saml/azure/session/{self.user['saml_token']}{path}")
                return 0, dict(success="Open browser.")
        return 1, dict(warn="unsupported auth_type.")
