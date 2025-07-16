from cmdbox.app import common, options
from cmdbox.app.commons import module
from fastapi import FastAPI, Request, Response
from pathlib import Path
from starlette.applications import Starlette
from starlette.middleware.sessions import SessionMiddleware
from typing import Any, Dict, List
from uvicorn.config import Config
import asyncio
import copy
import ctypes
import datetime
import gevent
import jwt
import logging
import multiprocessing
import os
import platform
import requests
import queue
import signal
import time
import threading
import traceback
import uvicorn
import webbrowser


class Web:
    @classmethod
    def getInstance(cls, *args, **kwargs) -> 'Web':
        """
        Webクラスのインスタンスを取得する
        Args:
            *args: 可変長引数
            **kwargs: キーワード引数

        Returns:
            Web: Webクラスのインスタンス
        """
        if not hasattr(cls, '_instance'):
            cls._instance = cls(*args, **kwargs)
        return cls._instance

    def __init__(self, logger:logging.Logger, data:Path, appcls=None, ver=None,
                 redis_host:str="localhost", redis_port:int=6379, redis_password:str=None, svname:str='server',
                 client_only:bool=False, doc_root:Path=None, gui_html:str=None, filer_html:str=None, result_html:str=None, users_html:str=None,
                 audit_html:str=None, agent_html:str=None, assets:List[str]=None, signin_html:str=None, signin_file:str=None, gui_mode:bool=False,
                 web_features_packages:List[str]=None, web_features_prefix:List[str]=[]):
        """
        cmdboxクライアント側のwebapiサービス

        Args:
            logger (logging): ロガー
            data (Path): コマンドやパイプラインの設定ファイルを保存するディレクトリ
            appcls ([type], optional): アプリケーションクラス. Defaults to None.
            ver ([type], optional): バージョン. Defaults to None.
            redis_host (str, optional): Redisサーバーのホスト名. Defaults to "localhost".
            redis_port (int, optional): Redisサーバーのポート番号. Defaults to 6379.
            redis_password (str, optional): Redisサーバーのパスワード. Defaults to None.
            svname (str, optional): サーバーのサービス名. Defaults to 'server'.
            client_only (bool, optional): クライアントのみのサービスかどうか. Defaults to False.
            doc_root (Path, optional): カスタムファイルのドキュメントルート. フォルダ指定のカスタムファイルのパスから、doc_rootのパスを除去したパスでURLマッピングします。Defaults to None.
            gui_html (str, optional): GUIのHTMLファイル. Defaults to None.
            filer_html (str, optional): ファイラーのHTMLファイル. Defaults to None.
            result_html (str, optional): 結果のHTMLファイル. Defaults to None.
            users_html (str, optional): ユーザーのHTMLファイル. Defaults to None.
            audit_html (str, optional): 監査のHTMLファイル. Defaults to None.
            agent_html (str, optional): エージェントのHTMLファイル. Defaults to None.
            assets (List[str], optional): 静的ファイルのリスト. Defaults to None.
            signin_html (str, optional): ログイン画面のHTMLファイル. Defaults to None.
            signin_file (str, optional): ログイン情報のファイル. Defaults to args.signin_file.
            gui_mode (bool, optional): GUIモードかどうか. Defaults to False.
            web_features_packages (List[str], optional): webfeatureのパッケージ名のリスト. Defaults to None.
            web_features_prefix (List[str], optional): webfeatureのパッケージのモジュール名のプレフィックス. Defaults to None.
        """
        super().__init__()
        self.logger = logger
        self.data = data
        self.appcls = appcls
        self.ver = ver
        self.container = dict()
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.svname = svname
        self.client_only = client_only
        if self.client_only:
            self.svname = 'client'
        self.doc_root = Path(doc_root) if doc_root is not None else Path(__file__).parent.parent / 'web'
        self.gui_html = Path(gui_html) if gui_html is not None else Path(__file__).parent.parent / 'web' / 'gui.html'
        self.filer_html = Path(filer_html) if filer_html is not None else Path(__file__).parent.parent / 'web' / 'filer.html'
        self.result_html = Path(result_html) if result_html is not None else Path(__file__).parent.parent / 'web' / 'result.html'
        self.users_html = Path(users_html) if users_html is not None else Path(__file__).parent.parent / 'web' / 'users.html'
        self.audit_html = Path(audit_html) if audit_html is not None else Path(__file__).parent.parent / 'web' / 'audit.html'
        self.agent_html = Path(agent_html) if agent_html is not None else Path(__file__).parent.parent / 'web' / 'agent.html'
        self.assets = []
        if assets is not None:
            if not isinstance(assets, list):
                raise ValueError(f'assets is not list. ({assets})')
            for a in assets:
                asset = Path(a)
                if asset.is_dir():
                    self.assets += [p for p in asset.glob('**/*') if p.is_file()]
                elif asset.is_file():
                    self.assets.append(asset)
                else:
                    logger.warning(f'assets not found. ({asset})')
        self.signin_html = Path(signin_html) if signin_html is not None else Path(__file__).parent.parent / 'web' / 'signin.html'
        self.signin_file = Path(signin_file) if signin_file is not None else None
        self.gui_html_data = None
        self.filer_html_data = None
        self.result_html_data = None
        self.users_html_data = None
        self.audit_html_data = None
        self.agent_html_data = None
        self.assets_data = None
        self.signin_html_data = None
        self.gui_mode = gui_mode
        self.web_features_packages = web_features_packages
        self.web_features_prefix = web_features_prefix
        self.cmds_path = self.data / ".cmds"
        self.pipes_path = self.data / ".pipes"
        self.users_path = self.data / ".users"
        self.audit_path = self.data / '.audit'
        self.agent_path = self.data / '.agent'
        self.static_root = Path(__file__).parent.parent / 'web'
        common.mkdirs(self.cmds_path)
        common.mkdirs(self.pipes_path)
        common.mkdirs(self.users_path)
        common.mkdirs(self.audit_path)
        common.mkdirs(self.agent_path)
        self.pipe_th = None
        self.img_queue = queue.Queue(1000)
        self.cb_queue = queue.Queue(1000)
        self.options = options.Options.getInstance()
        self.webcap_client = requests.Session()
        from cmdbox.app.auth import signin, signin_saml
        signin_file_data = signin.Signin.load_signin_file(self.signin_file, self=self)
        self.signin = signin.Signin(self.logger, self.signin_file, signin_file_data, self.appcls, self.ver)
        self.signin_saml = signin_saml.SigninSAML(self.logger, self.signin_file, signin_file_data, self.appcls, self.ver)

        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"web init parameter: data={self.data} -> {self.data.absolute() if self.data is not None else None}")
            self.logger.debug(f"web init parameter: redis_host={self.redis_host}")
            self.logger.debug(f"web init parameter: redis_port={self.redis_port}")
            self.logger.debug(f"web init parameter: redis_password=********")
            self.logger.debug(f"web init parameter: svname={self.svname}")
            self.logger.debug(f"web init parameter: client_only={self.client_only}")
            self.logger.debug(f"web init parameter: gui_html={self.gui_html} -> {self.gui_html.absolute() if self.gui_html is not None else None}")
            self.logger.debug(f"web init parameter: filer_html={self.filer_html} -> {self.filer_html.absolute() if self.filer_html is not None else None}")
            self.logger.debug(f"web init parameter: result_html={self.result_html} -> {self.result_html.absolute() if self.result_html is not None else None}")
            self.logger.debug(f"web init parameter: users_html={self.users_html} -> {self.users_html.absolute() if self.users_html is not None else None}")
            self.logger.debug(f"web init parameter: audit_html={self.audit_html} -> {self.audit_html.absolute() if self.audit_html is not None else None}")
            self.logger.debug(f"web init parameter: agent_html={self.agent_html} -> {self.agent_html.absolute() if self.agent_html is not None else None}")
            self.logger.debug(f"web init parameter: assets={self.assets} -> {[a.absolute() for a in self.assets] if self.assets is not None else None}")
            self.logger.debug(f"web init parameter: signin_html={self.signin_html} -> {self.signin_html.absolute() if self.signin_html is not None else None}")
            self.logger.debug(f"web init parameter: signin_file={self.signin_file} -> {self.signin_file.absolute() if self.signin_file is not None else None}")
            self.logger.debug(f"web init parameter: gui_mode={self.gui_mode}")
            self.logger.debug(f"web init parameter: web_features_packages={self.web_features_packages}")
            self.logger.debug(f"web init parameter: web_features_prefix={self.web_features_prefix}")
            self.logger.debug(f"web init parameter: cmds_path={self.cmds_path} -> {self.cmds_path.absolute() if self.cmds_path is not None else None}")
            self.logger.debug(f"web init parameter: pipes_path={self.pipes_path} -> {self.pipes_path.absolute() if self.pipes_path is not None else None}")
            self.logger.debug(f"web init parameter: users_path={self.users_path} -> {self.users_path.absolute() if self.users_path is not None else None}")
            self.logger.debug(f"web init parameter: audit_path={self.audit_path} -> {self.audit_path.absolute() if self.audit_path is not None else None}")
            self.logger.debug(f"web init parameter: agent_path={self.agent_path} -> {self.agent_path.absolute() if self.agent_path is not None else None}")

    def init_webfeatures(self, app:FastAPI):
        self.filemenu = dict()
        self.toolmenu = dict()
        self.viewmenu = dict()
        self.aboutmenu = dict()
        if self.options.is_features_loaded('web'):
            return
        # webfeatureの読込み
        self.wf_dep = []
        def wf_route(pk, prefix, excludes, w, app, appcls, ver, logger):
            if pk in w.wf_dep: return
            w.wf_dep.append(pk)
            for wf in module.load_webfeatures(pk, prefix, excludes, appcls=appcls, ver=ver, logger=logger):
                wf.route(self, app)
                self.filemenu = {**self.filemenu, **wf.filemenu(w)}
                self.toolmenu = {**self.toolmenu, **wf.toolmenu(w)}
                self.viewmenu = {**self.viewmenu, **wf.viewmenu(w)}
                self.aboutmenu = {**self.aboutmenu, **wf.aboutmenu(w)}

        if self.web_features_packages is not None:
            if self.web_features_prefix is None:
                raise ValueError(f"web_features_prefix is None. web_features_prefix={self.web_features_prefix}")
            if len(self.web_features_prefix) != len(self.web_features_packages):
                raise ValueError(f"web_features_prefix is not match. web_features_packages={self.web_features_packages}, web_features_prefix={self.web_features_prefix}")
            for i, pn in enumerate(self.web_features_packages):
                wf_route(pn, self.web_features_prefix[i], [], self, app, self.appcls, self.ver, self.logger)
        self.options.load_features_file('web', lambda pk, pn, excludes, appcls, ver, logger, _: wf_route(pk, pn, excludes, self, app, appcls, ver, logger), self.appcls, self.ver, self.logger)
        wf_route("cmdbox.app.features.web", "cmdbox_web_", [], self, app, self.appcls, self.ver, self.logger)
        # エイリアスの登録
        self.options.load_features_aliases_web(app.routes, self.logger)
        # 読込んだrouteの内容をログに出力
        if self.logger.level == logging.DEBUG:
            for route in app.routes:
                self.logger.debug(f"loaded webfeature: {route}")

    def change_password(self, user_name:str, password:str, new_password:str, confirm_password:str):
        """
        パスワードを変更する

        Args:
            user_name (str): ユーザー名
            new_password (str): 新しいパスワード
            confirm_password (str): 確認用パスワード

        Raises:
            HTTPException: パスワードが一致しない場合
            HTTPException: ユーザーが存在しない場合
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if user_name is None or user_name == '':
            return dict(warn="User name is empty.")
        if password is None or password == '':
            return dict(warn="Password is empty.")
        if new_password is None or new_password == '':
            return dict(warn="New password is empty.")
        if confirm_password is None or confirm_password == '':
            return dict(warn="Confirm password is empty.")
        if new_password != confirm_password:
            return dict(warn="Password does not match.")
        for u in signin_data['users']:
            if u['name'] == user_name:
                p = password if u['hash'] == 'plain' else common.hash_password(password, u['hash'])
                if u['password'] != p:
                    return dict(warn="Password does not match.")
                jadge, msg = self.signin.check_password_policy(user_name, password, new_password)
                if not jadge:
                    return dict(warn=msg)
                u['password'] = new_password if u['hash'] == 'plain' else common.hash_password(new_password, u['hash'])
                # パスワード更新日時の保存
                self.user_data(None, u['uid'], user_name, 'password', 'last_update', datetime.datetime.now())
                # サインインファイルの保存
                common.save_yml(self.signin_file, signin_data)
                return dict(success="Password changed.")
        return dict(warn="User not found.")

    def user_list(self, name:str=None) -> List[Dict[str, Any]]:
        """
        サインインファイルのユーザー一覧を取得する

        Args:
            name (str, optional): ユーザー名. Defaults to None.

        Returns:
            List[Dict[str, Any]]: ユーザー一覧
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        ret = []
        for u in copy.deepcopy(signin_data['users']):
            u['password'] = '********'
            if 'apikeys' in u:
                for an, ak in u['apikeys'].items():
                    exp = '-'
                    try:
                        cls = self.signin.__class__
                        publickey = None
                        if cls.verify_jwt_certificate is not None:
                            publickey = cls.verify_jwt_certificate.public_key()
                        if publickey is None and cls.verify_jwt_publickey is not None:
                            publickey = cls.verify_jwt_publickey
                        t = jwt.decode(ak, publickey, algorithms=[cls.verify_jwt_algorithm],
                                       issuer=cls.verify_jwt_issuer, audience=cls.verify_jwt_audience,
                                       options={'verify_iss': cls.verify_jwt_issuer is not None,
                                                'verify_aud': cls.verify_jwt_audience is not None})
                        exp = datetime.datetime.fromtimestamp(t['exp']).strftime('%Y-%m-%d %H:%M:%S')
                        u['apikeys'][an] = (ak, exp, '-')
                    except jwt.exceptions.InvalidTokenError as e:
                        u['apikeys'][an] = (ak, '-', str(e))
                    except Exception as e:
                        u['apikeys'][an] = (ak, '-', '-')
            if u['name'] == name:
                return [u]
            signin_last = self.user_data(None, u['uid'], u['name'], 'signin', 'last_update')
            pass_last_update = self.user_data(None, u['uid'], u['name'], 'password', 'last_update')
            pass_miss_count = self.user_data(None, u['uid'], u['name'], 'password', 'pass_miss_count')
            pass_miss_last = self.user_data(None, u['uid'], u['name'], 'password', 'pass_miss_last')

            if name is None:
                ret.append({**u, **dict(last_signin=signin_last, pass_last_update=pass_last_update,
                                pass_miss_count=pass_miss_count, pass_miss_last=pass_miss_last)})
        return ret

    def apikey_add(self, user:Dict[str, Any]) -> str:
        """
        サインインファイルにユーザーのApiKeyを追加する

        Args:
            user (Dict[str, Any]): ユーザー情報

        Returns:
            str: ApiKey
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if 'name' not in user:
            raise ValueError(f"User name is not found. ({user})")
        if 'apikey_name' not in user:
            raise ValueError(f"ApiKey name is not found. ({user})")
        if len([u for u in signin_data['users'] if u['name'] == user['name']]) <= 0:
            raise ValueError(f"User name is not exists. ({user})")
        apikey:str = None
        for u in signin_data['users']:
            if u['name'] == user['name']:
                if 'apikeys' not in u:
                    u['apikeys'] = dict()
                if user['apikey_name'] in u['apikeys']:
                    raise ValueError(f"ApiKey name is already exists. ({user})")
                apikey = common.random_string(64)
                u['apikeys'][user['apikey_name']] = apikey
                if signin_data['apikey']['gen_jwt']['enabled']:
                    cls = self.signin.__class__
                    claims = cls.gen_jwt_claims.copy() if cls.gen_jwt_claims is not None else dict()
                    claims['exp'] = int(time.time()) + int(claims.get('exp', 3600))
                    claims['uid'] = u['uid']
                    claims['name'] = u['name']
                    claims['groups'] = u['groups']
                    claims['email'] = u['email']
                    claims['apikey_name'] = user['apikey_name']
                    apikey = jwt.encode(claims, cls.gen_jwt_privatekey, algorithm=cls.gen_jwt_algorithm)
                    u['apikeys'][user['apikey_name']] = apikey

        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"apikey_add: {user} -> {self.signin_file}")
        common.save_yml(self.signin_file, signin_data)
        return apikey

    def apikey_del(self, user:Dict[str, Any]):
        """
        サインインファイルのユーザーのApiKeyを削除する

        Args:
            user (Dict[str, Any]): ユーザー情報
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if 'name' not in user:
            raise ValueError(f"User name is not found. ({user})")
        if 'apikey_name' not in user:
            raise ValueError(f"ApiKey name is not found. ({user})")
        if len([u for u in signin_data['users'] if u['name'] == user['name']]) <= 0:
            raise ValueError(f"User name is not exists. ({user})")
        apikey:str = None
        for u in signin_data['users']:
            if u['name'] == user['name']:
                if 'apikeys' not in u:
                    continue
                if user['apikey_name'] not in u['apikeys']:
                    continue
                apikey = u['apikeys'][user['apikey_name']]
                del u['apikeys'][user['apikey_name']]
                if len(u['apikeys']) <= 0:
                    del u['apikeys']
        if apikey is None:
            raise ValueError(f"ApiKey name is not exists. ({user})")

        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"apikey_del: {user} -> {self.signin_file}")
        common.save_yml(self.signin_file, signin_data)

    def user_add(self, user:Dict[str, Any]):
        """
        サインインファイルにユーザーを追加する

        Args:
            user (Dict[str, Any]): ユーザー情報
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if 'uid' not in user or user['uid'] == '':
            raise ValueError(f"User uid is not found or empty. ({user})")
        try:
            user['uid'] = int(user['uid'])
        except:
            raise ValueError(f"User uid is not number. ({user})")
        if 'name' not in user or user['name'] == '':
            raise ValueError(f"User name is not found or empty. ({user})")
        if 'hash' not in user or user['hash'] == '':
            raise ValueError(f"User hash is not found or empty. ({user})")
        hash = user['hash']
        if hash!='oauth2' and hash!='saml' and ('password' not in user or user['password'] == ''):
            raise ValueError(f"User password is not found or empty. ({user})")
        if 'email' not in user:
            raise ValueError(f"User email is not found. ({user})")
        if (hash=='oauth2' or hash=='saml') and (user['email'] is None or user['email']==''):
            raise ValueError(f"Required when `email` is `oauth2` or `saml`. ({user})")
        if 'groups' not in user or type(user['groups']) is not list:
            raise ValueError(f"User groups is not found or empty. ({user})")
        for gn in user['groups']:
            if len(self.group_list(gn)) <= 0:
                raise ValueError(f"Group is not found. ({gn})")
        if len([u for u in signin_data['users'] if u['uid'] == user['uid']]) > 0:
            raise ValueError(f"User uid is already exists. ({user})")
        if len([u for u in signin_data['users'] if u['name'] == user['name']]) > 0:
            raise ValueError(f"User name is already exists. ({user})")
        if hash not in ['oauth2', 'saml', 'plain', 'md5', 'sha1', 'sha256']:
            raise ValueError(f"User hash is not supported. ({user})")
        jadge, msg = self.signin.check_password_policy(user['name'], '', user['password'])
        if not jadge:
            raise ValueError(msg)
        if hash != 'plain':
            user['password'] = common.hash_password(user['password'], hash if hash != 'oauth2' and hash != 'saml' else 'sha1')
        else:
            user['password'] = user['password']
        signin_data['users'].append(user)
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"user_add: {user} -> {self.signin_file}")
        # パスワード更新日時の保存
        self.user_data(None, user['uid'], user['name'], 'password', 'last_update', datetime.datetime.now())
        # サインインファイルの保存
        common.save_yml(self.signin_file, signin_data)

    def user_edit(self, user:Dict[str, Any]):
        """
        サインインファイルのユーザー情報を編集する

        Args:
            user (Dict[str, Any]): ユーザー情報
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if 'uid' not in user or user['uid'] == '':
            raise ValueError(f"User uid is not found or empty. ({user})")
        try:
            user['uid'] = int(user['uid'])
        except:
            raise ValueError(f"User uid is not number. ({user})")
        if 'name' not in user or user['name'] == '':
            raise ValueError(f"User name is not found or empty. ({user})")
        if 'hash' not in user or user['hash'] == '':
            raise ValueError(f"User hash is not found or empty. ({user})")
        if 'email' not in user:
            raise ValueError(f"User email is not found. ({user})")
        hash = user['hash']
        if (hash=='oauth2' or hash=='saml') and (user['email'] is None or user['email']==''):
            raise ValueError(f"Required when `email` is `oauth2` or `saml`. ({user})")
        if 'groups' not in user or type(user['groups']) is not list:
            raise ValueError(f"User groups is not found or empty. ({user})")
        for gn in user['groups']:
            if len(self.group_list(gn)) <= 0:
                raise ValueError(f"Group is not found. ({gn})")
        if len([u for u in signin_data['users'] if u['uid'] == user['uid']]) <= 0:
            raise ValueError(f"User uid is not found. ({user})")
        if len([u for u in signin_data['users'] if u['name'] == user['name']]) <= 0:
            raise ValueError(f"User name is not found. ({user})")
        if hash not in ['oauth2', 'saml', 'plain', 'md5', 'sha1', 'sha256']:
            raise ValueError(f"User hash is not supported. ({user})")
        for u in signin_data['users']:
            if u['uid'] == user['uid']:
                u['name'] = user['name']
                if 'password' in user and user['password'] != '':
                    jadge, msg = self.signin.check_password_policy(user['name'], u['password'], user['password'])
                    if not jadge:
                        raise ValueError(msg)
                    if hash != 'plain':
                        u['password'] = common.hash_password(user['password'], hash if hash != 'oauth2' and hash != 'saml' else 'sha1')
                    else:
                        u['password'] = user['password']
                    # パスワード更新日時の保存
                    self.user_data(None, user['uid'], user['name'], 'password', 'last_update', datetime.datetime.now())
                u['hash'] = user['hash']
                u['groups'] = user['groups']
                u['email'] = user['email']
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"user_edit: {user} -> {self.signin_file}")
        # サインインファイルの保存
        common.save_yml(self.signin_file, signin_data)

    def user_del(self, uid:int):
        """
        サインインファイルからユーザーを削除する

        Args:
            uid (int): ユーザーID
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        try:
            uid = int(uid)
        except:
            raise ValueError(f"User uid is not number. ({uid})")
        users = [u for u in signin_data['users'] if u['uid'] != uid]
        if len(users) == len(signin_data['users']):
            raise ValueError(f"User uid is not found. ({uid})")
        signin_data['users'] = users
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"user_del: {uid} -> {self.signin_file}")
        common.save_yml(self.signin_file, signin_data)

    def group_list(self, name:str=None) -> List[Dict[str, Any]]:
        """
        サインインファイルのグループ一覧を取得する

        Args:
            name (str, optional): グループ名. Defaults to None.

        Returns:
            List[Dict[str, Any]]: グループ一覧
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if name is None:
            return copy.deepcopy(signin_data['groups'])
        for g in copy.deepcopy(signin_data['groups']):
            if g['name'] == name:
                return [g]
        return []

    def group_add(self, group:Dict[str, Any]):
        """
        サインインファイルにグループを追加する

        Args:
            group (Dict[str, Any]): グループ情報
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if 'gid' not in group:
            raise ValueError(f"Group gid is not found. ({group})")
        try:
            group['gid'] = int(group['gid'])
        except:
            raise ValueError(f"Group gid is not number. ({group})")
        if 'name' not in group:
            raise ValueError(f"Group name is not found. ({group})")
        if 'parent' in group and (group['parent'] is None or group['parent'] == ''):
            del group['parent']
        elif 'parent' in group and group['parent'] not in [g['name'] for g in signin_data['groups']]:
            raise ValueError(f"Group parent is not found. ({group})")
        if 'parent' in group and group['parent'] == group['name']:
            raise ValueError(f"Group parent is same as group name. ({group})")
        if len([g for g in signin_data['groups'] if g['gid'] == group['gid']]) > 0:
            raise ValueError(f"Group gid is already exists. ({group})")
        if len([g for g in signin_data['groups'] if g['name'] == group['name']]) > 0:
            raise ValueError(f"Group name is already exists. ({group})")
        signin_data['groups'].append(group)
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"group_add: {group} -> {self.signin_file}")
        common.save_yml(self.signin_file, signin_data)

    def group_edit(self, group:Dict[str, Any]):
        """
        サインインファイルのグループ情報を編集する

        Args:
            group (Dict[str, Any]): グループ情報
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if 'gid' not in group:
            raise ValueError(f"Group gid is not found. ({group})")
        try:
            group['gid'] = int(group['gid'])
        except:
            raise ValueError(f"Group gid is not number. ({group})")
        if 'name' not in group:
            raise ValueError(f"Group name is not found. ({group})")
        if 'parent' in group and (group['parent'] is None or group['parent'] == ''):
            del group['parent']
        elif 'parent' in group and group['parent'] not in [g['name'] for g in signin_data['groups']]:
            raise ValueError(f"Group parent is not found. ({group})")
        if 'parent' in group and group['parent'] == group['name']:
            raise ValueError(f"Group parent is same as group name. ({group})")
        if len([g for g in signin_data['groups'] if g['gid'] == group['gid']]) <= 0:
            raise ValueError(f"Group gid is not found. ({group})")
        if len([g for g in signin_data['groups'] if g['name'] == group['name']]) <= 0:
            raise ValueError(f"Group name is not found. ({group})")
        for g in signin_data['groups']:
            if g['gid'] == group['gid']:
                g['name'] = group['name']
                g['parent'] = group['parent']
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"group_edit: {group} -> {self.signin_file}")
        common.save_yml(self.signin_file, signin_data)

    def group_del(self, gid:int):
        """
        サインインファイルからグループを削除する

        Args:
            gid (int): グループID
        """
        signin_data = self.signin.get_data()
        if signin_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        try:
            gid = int(gid)
        except:
            raise ValueError(f"Group gid is not number. ({gid})")
        # グループがユーザーに使用されているかチェック
        user_group_ids = []
        for user in signin_data['users']:
            for group in user['groups']:
                user_group_ids += [g['gid'] for g in signin_data['groups'] if g['name'] == group]
        if gid in user_group_ids:
            raise ValueError(f"Group gid is used by user. ({gid})")
        # グループが親グループに使用されているかチェック
        parent_group_ids = []
        for group in signin_data['groups']:
            if 'parent' in group:
                parent_group_ids += [g['gid'] for g in signin_data['groups'] if g['name'] == group['parent']]
        if gid in parent_group_ids:
            raise ValueError(f"Group gid is used by parent group. ({gid})")
        # グループがcmdruleグループに使用されているかチェック
        cmdrule_group_ids = []
        for rule in signin_data['cmdrule']['rules']:
            for group in rule['groups']:
                cmdrule_group_ids += [g['gid'] for g in signin_data['groups'] if g['name'] == group]
        if gid in cmdrule_group_ids:
            raise ValueError(f"Group gid is used by cmdrule group. ({gid})")
        # グループがpathruleグループに使用されているかチェック
        pathrule_group_ids = []
        for rule in signin_data['pathrule']['rules']:
            for group in rule['groups']:
                pathrule_group_ids += [g['gid'] for g in signin_data['groups'] if g['name'] == group]
        if gid in pathrule_group_ids:
            raise ValueError(f"Group gid is used by pathrule group. ({gid})")

        # グループ削除
        groups = [g for g in signin_data['groups'] if g['gid'] != gid]
        if len(groups) == len(signin_data['groups']):
            raise ValueError(f"Group gid is not found. ({gid})")
        signin_data['groups'] = groups
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"group_del: {gid} -> {self.signin_file}")
        common.save_yml(self.signin_file, signin_data)

    def user_data(self, req:Request, uid:str, user_name:str, categoly:str, key:str=None, val:Any=None, delkey:bool=False) -> Any:
        """
        ユーザーデータを取得または設定する

        Args:
            req (Request): リクエスト
            uid (str): ユーザーID
            user_name (str): ユーザー名
            categoly (str): カテゴリ
            key (str, optional): キー. Defaults to None.
            val (Any, optional): 値. Defaults to None.
            delkey (bool, optional): キー削除. Defaults to False.

        Returns:
            Any: 値 or カテゴリのデータ
        """
        user_path = self.users_path / f"user-{uid}_{user_name}.json"
        # ユーザーデータの取得
        if req is not None and 'user_data' in req.session:
            # セッションにユーザーデータがある場合はそれを使用する
            user_data = req.session['user_data']
        else:
            # セッションにユーザーデータがない場合はファイルから読み込む
            if user_path.is_file():
                user_data = common.loaduser(user_path)
            else:
                user_data = dict()
            if req is not None:
                # セッションにユーザーデータを保存する
                req.session['user_data'] = user_data
        if categoly not in user_data:
            user_data[categoly] = dict()
        # キー削除の場合
        if delkey:
            if key is not None and key in user_data[categoly]:
                del user_data[categoly][key]
                common.saveuser(user_data, user_path)
            return None
        # キーが指定されていない場合はカテゴリのデータを返す
        if key is None:
            return user_data[categoly] if categoly in user_data else None
        # キーが指定されている場合は値を設定または取得する
        if val is None:
            return user_data[categoly][key] if key in user_data[categoly] else None
        user_data[categoly][key] = val
        common.saveuser(user_data, user_path)
        return val

    def start(self, allow_host:str="0.0.0.0", listen_port:int=8081, ssl_listen_port:int=8443,
              ssl_cert:Path=None, ssl_key:Path=None, ssl_keypass:str=None, ssl_ca_certs:Path=None,
              session_domain:str=None, session_path:str='/', session_secure:bool=False, session_timeout:int=900, outputs_key:List[str]=[],
              guvicorn_workers:int=-1, guvicorn_timeout:int=30,
              agent_runner=None, mcp=None,):
        """
        Webサーバを起動する

        Args:
            allow_host (str, optional): 許可ホスト. Defaults to "
            listen_port (int, optional): リスンポート. Defaults to 8081.
            ssl_listen_port (int, optional): SSLリスンポート. Defaults to 8443.
            ssl_cert (Path, optional): SSL証明書ファイル. Defaults to None.
            ssl_key (Path, optional): SSL秘密鍵ファイル. Defaults to None.
            ssl_keypass (str, optional): SSL秘密鍵パスワード. Defaults to None.
            ssl_ca_certs (Path, optional): SSL CA証明書ファイル. Defaults to None.
            session_domain (str, optional): セッションドメイン. Defaults to None.
            session_path (str, optional): セッションパス. Defaults to '/'.
            session_secure (bool, optional): セッションセキュア. Defaults to False.
            session_timeout (int, optional): セッションタイムアウト. Defaults to 900.
            outputs_key (list, optional): 出力キー. Defaults to [].
            guvicorn_workers (int, optional): Gunicornワーカー数. Defaults to -1.
            guvicorn_timeout (int, optional): Gunicornタイムアウト. Defaults to 30.
            agent_runner (Runner, optional): エージェントランナー. Defaults to None.
            mcp (MCP, optional): MCP. Defaults to None.
        """
        self.allow_host = allow_host
        self.listen_port = listen_port
        self.ssl_listen_port = ssl_listen_port
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.ssl_keypass = ssl_keypass
        self.ssl_ca_certs = ssl_ca_certs
        self.outputs_key = outputs_key
        self.session_domain = session_domain
        self.session_path = session_path
        self.session_secure = session_secure
        self.session_timeout = session_timeout
        self.guvicorn_workers = guvicorn_workers
        self.guvicorn_timeout = guvicorn_timeout
        self.agent_runner = agent_runner
        self.mcp = mcp
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"web start parameter: allow_host={self.allow_host}")
            self.logger.debug(f"web start parameter: listen_port={self.listen_port}")
            self.logger.debug(f"web start parameter: ssl_listen_port={self.ssl_listen_port}")
            self.logger.debug(f"web start parameter: ssl_cert={self.ssl_cert} -> {self.ssl_cert.absolute() if self.ssl_cert is not None else None}")
            self.logger.debug(f"web start parameter: ssl_key={self.ssl_key} -> {self.ssl_key.absolute() if self.ssl_key is not None else None}")
            self.logger.debug(f"web start parameter: ssl_keypass={self.ssl_keypass}")
            self.logger.debug(f"web start parameter: ssl_ca_certs={self.ssl_ca_certs} -> {self.ssl_ca_certs.absolute() if self.ssl_ca_certs is not None else None}")
            self.logger.debug(f"web start parameter: outputs_key={self.outputs_key}")
            self.logger.debug(f"web start parameter: session_domain={self.session_domain}")
            self.logger.debug(f"web start parameter: session_path={self.session_path}")
            self.logger.debug(f"web start parameter: session_secure={self.session_secure}")
            self.logger.debug(f"web start parameter: session_timeout={self.session_timeout}")
            self.logger.debug(f"web start parameter: guvicorn_worker={self.guvicorn_workers}")
            self.logger.debug(f"web start parameter: guvicorn_timeout={self.guvicorn_timeout}")
            self.logger.debug(f"web start parameter: agent_runner={self.agent_runner}")
            self.logger.debug(f"web start parameter: mcp={self.mcp}")

        if self.agent_runner is not None:
            # google.adkが大きいので必要な時にだけ読込む
            from google.adk.sessions import BaseSessionService, Session
            async def create_agent_session(session_service:BaseSessionService, user_id:str, session_id:str=None) -> Session:
                """
                セッションを作成します

                Args:
                    session_service (BaseSessionService): セッションサービス
                    user_id (str): ユーザーID
                    session_id (str): セッションID

                Returns:
                    Any: セッション
                """
                if session_id is None:
                    session_id = common.random_string(32)
                session = await session_service.get_session(app_name=self.ver.__appid__, user_id=user_id, session_id=session_id)
                if session is None:
                    session = await session_service.create_session(app_name=self.ver.__appid__, user_id=user_id, session_id=session_id)
                return session
            self.create_agent_session = create_agent_session
            async def list_agent_sessions(session_service:BaseSessionService, user_id:str, session_id:str=None) -> List[Session]:
                """
                セッションをリストします

                Args:
                    session_service (BaseSessionService): セッションサービス
                    user_id (str): ユーザーID

                Returns:
                    List[Session]: セッションリスト
                """
                if session_id is None:
                    sessions = await session_service.list_sessions(app_name=self.ver.__appid__, user_id=user_id)
                    ret = []
                    for s in sessions.sessions:
                        session = await session_service.get_session(app_name=self.ver.__appid__, user_id=user_id, session_id=s.id)
                        if session is None:
                            continue
                        ret.append(session)
                    return ret
                else:
                    session = await session_service.get_session(app_name=self.ver.__appid__, user_id=user_id, session_id=session_id)
                    if session is None:
                        return []
                    return [session]
            self.list_agent_sessions = list_agent_sessions
            async def delete_agent_session(session_service:BaseSessionService, user_id:str, session_id:str) -> bool:
                """
                セッションを削除します

                Args:
                    session_service (BaseSessionService): セッションサービス
                    user_id (str): ユーザーID
                    session_id (str): セッションID

                Returns:
                    bool: 成功した場合はTrue, 失敗した場合はFalse
                """
                return await session_service.delete_session(app_name=self.ver.__appid__, user_id=user_id, session_id=session_id)
            self.delete_agent_session = delete_agent_session

        mcp_app:Starlette = None
        if self.mcp is not None:
            mcp_app:Starlette = self.mcp.streamable_http_app()
            #mcp_app:Starlette = self.mcp.http_app()
        if mcp_app is not None:
            app = FastAPI(lifespan=mcp_app.lifespan)
        else:
            app = FastAPI()

        @app.middleware("http")
        async def set_context_cookie(req:Request, call_next):
            res:Response = await call_next(req)
            res.set_cookie("context_path", self.session_path, path=self.session_path, domain=self.session_domain)
            return res

        mwparam = dict(path=self.session_path, max_age=self.session_timeout, secret_key=common.random_string())
        if self.session_domain is not None:
            mwparam['domain'] = self.session_domain
        if self.session_secure:
            mwparam['https_only'] = True # セッションハイジャック対策
        app.add_middleware(SessionMiddleware, **mwparam)
        if mcp_app is not None:
            app.mount("/mcpsv", mcp_app, name="mcp")
            self.logger.info(f"mcp server mount: mount_path=/mcpsv app={mcp_app} routes={mcp_app.routes}")
        self.init_webfeatures(app)

        self.is_running = True
        th = None
        th_ssl = None
        if self.ssl_cert is not None and self.ssl_key is not None:
            https_config = Config(app=app, host=self.allow_host, port=self.ssl_listen_port,
                                  ssl_certfile=self.ssl_cert, ssl_keyfile=self.ssl_key,
                                  ssl_keyfile_password=self.ssl_keypass, ssl_ca_certs=self.ssl_ca_certs)
            th_ssl = ThreadedUvicorn(self.logger, config=https_config,
                                     guvicorn_config=dict(workers=self.guvicorn_workers, timeout=self.guvicorn_timeout))
            th_ssl.start()
            browser_port = self.ssl_listen_port
        else:
            http_config = Config(app=app, host=self.allow_host, port=self.listen_port)
            th = ThreadedUvicorn(self.logger, config=http_config,
                                guvicorn_config=dict(workers=self.guvicorn_workers, timeout=self.guvicorn_timeout))
            th.start()
            browser_port = self.listen_port
        try:
            if self.gui_mode:
                webbrowser.open(f'http://localhost:{browser_port}/gui')
            with open("web.pid", mode="w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
            while self.is_running:
                gevent.sleep(1)
            if th is not None:
                th.stop()
            if th_ssl is not None:
                th_ssl.stop()
        except KeyboardInterrupt:
            if th is not None:
                th.stop()
            if th_ssl is not None:
                th_ssl.stop()

    def stop(self):
        """
        Webサーバを停止する
        """
        try:
            with open("web.pid", mode="r", encoding="utf-8") as f:
                pid = f.read()
                if pid != "":
                    os.kill(int(pid), signal.CTRL_C_EVENT)
                    self.logger.info(f"Stop web.")
                else:
                    self.logger.warning(f"pid is empty.")
            Path("web.pid").unlink(missing_ok=True)
        except:
            traceback.print_exc()
        finally:
            self.logger.info(f"Exit web.")

class ThreadedUvicorn:
    def __init__(self, logger:logging.Logger, config:Config, guvicorn_config:Dict[str, Any]=None, force_uvicorn:bool=False):
        self.logger = logger
        self.guvicorn_config = guvicorn_config
        self.force_uvicorn = True if platform.system() == "Windows" else force_uvicorn
        # loggerの設定
        common.reset_logger("uvicorn")
        common.reset_logger("uvicorn.error")
        common.reset_logger("uvicorn.access")
        #common.reset_logger("gunicorn.error")
        #common.reset_logger("gunicorn.access")
        if self.force_uvicorn:
            self.server = uvicorn.Server(config)
            self.thread = RaiseThread(daemon=True, target=self.server.run)
        else:

            from gunicorn.app.wsgiapp import WSGIApplication
            class App(WSGIApplication):
                def __init__(self, app, options):
                    self.options = options
                    self.application = app
                    self.started = True
                    super().__init__()
                def load_config(self):
                    config = {k: v for k, v in self.options.items() if k in self.cfg.settings and v is not None}
                    for key, value in config.items():
                        self.cfg.set(key.lower(), value)
                def load(self):
                    return self.application
            opt = dict(bind=f"{config.host}:{config.port}",
                       worker_class="uvicorn.workers.UvicornWorker",
                       access_log_format='[%(t)s] %(p)s %(l)s %(h)s "%(r)s" %(s)s',
                       loglevel=logging.getLevelName(self.logger.level),
                       keyfile=config.ssl_keyfile, certfile=config.ssl_certfile,
                       ca_certs=config.ssl_ca_certs, keyfile_password=config.ssl_keyfile_password,
                       limit_request_line=8190, limit_request_fields=100, limit_request_field_size=8190)

            self.guvicorn_config = self.guvicorn_config or {}
            if 'workers' not in self.guvicorn_config:
                self.guvicorn_config['workers'] = None
            if self.guvicorn_config['workers'] is None or self.guvicorn_config['workers'] <= 0:
                self.guvicorn_config['workers'] = multiprocessing.cpu_count()*2
            if 'timeout' not in self.guvicorn_config:
                self.guvicorn_config['timeout'] = None
            if self.guvicorn_config['timeout'] is None or self.guvicorn_config['timeout'] <= 0:
                self.guvicorn_config['timeout'] = 30

            opt = {**opt, **self.guvicorn_config}
            self.server = App(config.app, opt)
            #self.thread = RaiseThread(daemon=True, target=self.server.run)

    def start(self):
        if self.force_uvicorn:
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
            self.thread.start()
            asyncio.run(self.wait_for_started())
        else:
            async def run():
                self.server.run()
            asyncio.run(run())

    async def wait_for_started(self):
        while not self.server.started:
            await asyncio.sleep(0.1)

    def stop(self):
        if self.force_uvicorn:
            if self.thread.is_alive():
                self.server.should_exit = True
                self.thread.raise_exception()
                while self.thread.is_alive():
                    time.sleep(0.1)
        else:
            self.server.started = False

    def is_alive(self):
        if self.force_uvicorn:
            return self.thread.is_alive()
        else:
            return self.server.started

class RaiseThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._run = self.run
        self.run = self.set_id_and_run

    def set_id_and_run(self):
        self.id = threading.get_native_id()
        self._run()

    def get_id(self):
        return self.id

    def raise_exception(self):
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self.get_id()), 
            ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.get_id()), 
                0
            )
            print('Failure in raising exception')
