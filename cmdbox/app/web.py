from cmdbox.app import common, options
from cmdbox.app.commons import module
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from typing import Any, Dict, List
from uvicorn.config import Config
import asyncio
import copy
import ctypes
import gevent
import logging
import os
import requests
import queue
import signal
import threading
import traceback
import uvicorn
import webbrowser


class Web:
    def __init__(self, logger:logging.Logger, data:Path, appcls=None, ver=None,
                 redis_host:str = "localhost", redis_port:int = 6379, redis_password:str = None, svname:str = 'server',
                 client_only:bool=False, doc_root:Path=None, gui_html:str=None, filer_html:str=None,
                 assets:List[str]=None, signin_html:str=None, signin_file:str=None, gui_mode:bool=False,
                 web_features_packages:List[str]=None, web_features_prefix:List[str]=None):
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
            anno_html (str, optional): アノテーション画面のHTMLファイル. Defaults to None.
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
        self.signin_html = Path(signin_html) if signin_html is not None else Path(__file__).parent.parent / 'web' / 'signin.html'
        self.signin_file = Path(signin_file) if signin_file is not None else None
        self.gui_html_data = None
        self.filer_html_data = None
        self.assets_data = None
        self.signin_html_data = None
        self.signin_file_data = None
        self.gui_mode = gui_mode
        self.web_features_packages = web_features_packages
        self.web_features_prefix = web_features_prefix
        self.cmds_path = self.data / ".cmds"
        self.pipes_path = self.data / ".pipes"
        self.static_root = Path(__file__).parent.parent / 'web'
        common.mkdirs(self.cmds_path)
        common.mkdirs(self.pipes_path)
        self.pipe_th = None
        self.img_queue = queue.Queue(1000)
        self.cb_queue = queue.Queue(1000)
        self.options = options.Options.getInstance()
        self.webcap_client = requests.Session()
        self.load_signin_file()
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"web init parameter: data={self.data} -> {self.data.absolute() if self.data is not None else None}")
            self.logger.debug(f"web init parameter: redis_host={self.redis_host}")
            self.logger.debug(f"web init parameter: redis_port={self.redis_port}")
            self.logger.debug(f"web init parameter: redis_password=********")
            self.logger.debug(f"web init parameter: svname={self.svname}")
            self.logger.debug(f"web init parameter: client_only={self.client_only}")
            self.logger.debug(f"web init parameter: gui_html={self.gui_html} -> {self.gui_html.absolute() if self.gui_html is not None else None}")
            self.logger.debug(f"web init parameter: filer_html={self.filer_html} -> {self.filer_html.absolute() if self.filer_html is not None else None}")
            self.logger.debug(f"web init parameter: assets={self.assets} -> {[a.absolute() for a in self.assets] if self.assets is not None else None}")
            self.logger.debug(f"web init parameter: signin_html={self.signin_html} -> {self.signin_html.absolute() if self.signin_html is not None else None}")
            self.logger.debug(f"web init parameter: signin_file={self.signin_file} -> {self.signin_file.absolute() if self.signin_file is not None else None}")
            self.logger.debug(f"web init parameter: gui_mode={self.gui_mode}")
            self.logger.debug(f"web init parameter: web_features_packages={self.web_features_packages}")
            self.logger.debug(f"web init parameter: web_features_prefix={self.web_features_prefix}")
            self.logger.debug(f"web init parameter: cmds_path={self.cmds_path} -> {self.cmds_path.absolute() if self.cmds_path is not None else None}")
            self.logger.debug(f"web init parameter: pipes_path={self.pipes_path} -> {self.pipes_path.absolute() if self.pipes_path is not None else None}")

    def enable_cors(self, req:Request, res:Response) -> None:
        """
        CORSを有効にする

        Args:
            req (Request): リクエスト
            res (Response): レスポンス
        """
        if req is None or not 'Origin' in req.headers.keys():
            return
        res.headers['Access-Control-Allow-Origin'] = res.headers['Origin']

    #security = OAuth2PasswordBearer(tokenUrl="token")

    def check_signin(self, req:Request, res:Response):
        """
        サインインをチェックする

        Args:
            req (Request): リクエスト
            res (Response): レスポンス

        Returns:
            Response: サインインエラーの場合はリダイレクトレスポンス
        """
        self.enable_cors(req, res)
        if self.signin_file is None:
            return None
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if 'signin' in req.session:
            userid = req.session['signin']['userid']
            passwd = req.session['signin']['password']
            if userid in self.signin_file_data and passwd == self.signin_file_data[userid]['password']:
                return None
            # パスルールチェック
            user_groups = req.session['signin']['groups']
            jadge = self.signin_file_data['pathrule']['policy']
            for rule in self.signin_file_data['pathrule']['rules']:
                if len([g for g in rule['groups'] if g in user_groups]) <= 0:
                    continue
                if len([p for p in rule['paths'] if req.url.path.startswith(p)]) <= 0:
                    continue
                jadge = rule['rule']
            if self.logger.level == logging.DEBUG:
                self.logger.debug(f"rule: {req.url.path}: {jadge}")
            if jadge == 'allow':
                return None
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"Not signed in.")
        return RedirectResponse(url=f'/signin{req.url.path}?error=1')

    def check_cmd(self, req:Request, res:Response, mode:str, cmd:str):
        if self.signin_file is None:
            return True
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if 'signin' not in req.session or 'groups' not in req.session['signin']:
            return False
        # コマンドチェック
        user_groups = req.session['signin']['groups']
        jadge = self.signin_file_data['cmdrule']['policy']
        for rule in self.signin_file_data['cmdrule']['rules']:
            if len([g for g in rule['groups'] if g in user_groups]) <= 0:
                continue
            if rule['mode'] is not None:
                if rule['mode'] != mode:
                    continue
                if len([c for c in rule['cmds'] if cmd == c]) <= 0:
                    continue
            jadge = rule['rule']
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"rule: mode={mode}, cmd={cmd}: {jadge}")
        return jadge == 'allow'
    
    def get_enable_modes(self, req:Request, res:Response):
        if self.signin_file is None:
            return self.options.get_modes().copy()
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if 'signin' not in req.session or 'groups' not in req.session['signin']:
            return []
        modes = self.options.get_modes().copy()
        user_groups = req.session['signin']['groups']
        jadge = self.signin_file_data['cmdrule']['policy']
        jadge_modes = []
        if jadge == 'allow':
            for m in modes:
                jadge_modes += list(m.keys()) if type(m) is dict else [m]
        for rule in self.signin_file_data['cmdrule']['rules']:
            if len([g for g in rule['groups'] if g in user_groups]) <= 0:
                continue
            if 'mode' not in rule:
                continue
            if rule['mode'] is not None:
                if rule['rule'] == 'allow':
                    jadge_modes.append(rule['mode'])
                elif rule['rule'] == 'deny':
                    jadge_modes.remove(rule['mode'])
            elif rule['mode'] is None and len(rule['cmds']) <= 0:
                if rule['rule'] == 'allow':
                    for m in modes:
                        jadge_modes += list(m.keys()) if type(m) is dict else [m]
                elif rule['rule'] == 'deny':
                    jadge_modes = []
        return sorted(list(set(['']+jadge_modes)), key=lambda m: m)

    def get_enable_cmds(self, mode:str, req:Request, res:Response):
        if self.signin_file is None:
            return self.options.get_cmds(mode).copy()
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if 'signin' not in req.session or 'groups' not in req.session['signin']:
            return []
        cmds = self.options.get_cmds(mode).copy()
        if mode == '':
            return cmds
        user_groups = req.session['signin']['groups']
        jadge = self.signin_file_data['cmdrule']['policy']
        jadge_cmds = []
        if jadge == 'allow':
            for c in cmds:
                jadge_cmds += list(c.keys()) if type(c) is dict else [c]
        for rule in self.signin_file_data['cmdrule']['rules']:
            if len([g for g in rule['groups'] if g in user_groups]) <= 0:
                continue
            if 'mode' not in rule:
                continue
            if 'cmds' not in rule:
                continue
            if rule['mode'] is not None and rule['mode'] != mode:
                continue
            if len(rule['cmds']) > 0:
                if rule['rule'] == 'allow':
                    jadge_cmds += rule['cmds']
                elif rule['rule'] == 'deny':
                    for c in rule['cmds']:
                        jadge_cmds.remove[c]
            elif rule['mode'] is None and len(rule['cmds']) <= 0:
                if rule['rule'] == 'allow':
                    for c in cmds:
                        jadge_cmds += list(c.keys()) if type(c) is dict else [c]
                elif rule['rule'] == 'deny':
                    jadge_cmds = []
        return sorted(list(set(['']+jadge_cmds)), key=lambda c: c)

    def correct_group(self, group_names, master_groups=None):
        master_groups = self.signin_file_data['groups'] if master_groups is None else master_groups
        gns = []
        for gn in group_names.copy():
            gns = [gr['name'] for gr in master_groups if 'parent' in gr and gr['parent']==gn]
            gns += self.correct_group(gns, master_groups)
        return group_names + gns

    def init_webfeatures(self, app:FastAPI):
        self.filemenu = dict()
        self.toolmenu = dict()
        self.viewmenu = dict()
        self.aboutmenu = dict()
        # webfeatureの読込み
        def wf_route(pk, prefix, w, app, appcls, ver, logger):
            for wf in module.load_webfeatures(pk, prefix, appcls=appcls, ver=ver, logger=logger):
                wf.route(self, app)
                self.filemenu |= wf.filemenu(w)
                self.toolmenu |= wf.toolmenu(w)
                self.viewmenu |= wf.viewmenu(w)
                self.aboutmenu |= wf.aboutmenu(w)

        if self.web_features_packages is not None:
            if self.web_features_prefix is None:
                raise ValueError(f"web_features_prefix is None. web_features_prefix={self.web_features_prefix}")
            if len(self.web_features_prefix) != len(self.web_features_packages):
                raise ValueError(f"web_features_prefix is not match. web_features_packages={self.web_features_packages}, web_features_prefix={self.web_features_prefix}")
            for i, pn in enumerate(self.web_features_packages):
                wf_route(pn, self.web_features_prefix[i], self, app, self.appcls, self.ver, self.logger)
        self.options.load_features_file('web', lambda pk, pn, appcls, ver, logger: wf_route(pk, pn, self, app, appcls, ver, logger), self.appcls, self.ver, self.logger)
        wf_route("cmdbox.app.features.web", "cmdbox_web_", self, app, self.appcls, self.ver, self.logger)
        # 読込んだrouteの内容をログに出力
        if self.logger.level == logging.DEBUG:
            for route in app.routes:
                self.logger.debug(f"loaded webfeature: {route}")

    def load_signin_file(self):
        if self.signin_file is not None:
            if not self.signin_file.is_file():
                raise HTTPException(status_code=500, detail=f'signin_file is not found. ({self.signin_file})')
            yml = common.load_yml(self.signin_file)
            # usersのフォーマットチェック
            if 'users' not in yml:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "users" not found. ({self.signin_file})')
            uids = set()
            groups = [g['name'] for g in yml['groups']]
            for user in yml['users']:
                if 'uid' not in user or user['uid'] == '':
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "uid" not found or empty. ({self.signin_file})')
                if user['uid'] in uids:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. Duplicate uid found. ({self.signin_file}). uid={user["uid"]}')
                if 'name' not in user or user['name'] == '':
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "name" not found or empty. ({self.signin_file})')
                if 'password' not in user or user['password'] == '':
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "password" not found or empty. ({self.signin_file})')
                if 'hash' not in user or user['hash'] == '':
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "hash" not found or empty. ({self.signin_file})')
                if user['hash'] not in ['plain', 'md5', 'sha1', 'sha256']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. Algorithms not supported. ({self.signin_file}). hash={user["hash"]} "plain", "md5", "sha1", "sha256" only.')
                if 'groups' not in user or type(user['groups']) is not list:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not found or not list type. ({self.signin_file})')
                if len([ug for ug in user['groups'] if ug not in groups]) > 0:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. Group not found. ({self.signin_file}). {user["groups"]}')
                uids.add(user['uid'])
            # groupsのフォーマットチェック
            if 'groups' not in yml:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not found. ({self.signin_file})')
            gids = set()
            for group in yml['groups']:
                if 'gid' not in group or group['gid'] == '':
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "gid" not found or empty. ({self.signin_file})')
                if group['gid'] in gids:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. Duplicate gid found. ({self.signin_file}). gid={group["gid"]}')
                if 'name' not in group or group['name'] == '':
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "name" not found or empty. ({self.signin_file})')
                if 'parent' in group:
                    if group['parent'] not in groups:
                        raise HTTPException(status_code=500, detail=f'signin_file format error. Parent group not found. ({self.signin_file}). parent={group["parent"]}')
                gids.add(group['gid'])
            # cmdruleのフォーマットチェック
            if 'cmdrule' not in yml:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "cmdrule" not found. ({self.signin_file})')
            if 'policy' not in yml['cmdrule']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "policy" not found in "cmdrule". ({self.signin_file})')
            if yml['cmdrule']['policy'] not in ['allow', 'deny']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "policy" not supported in "cmdrule". ({self.signin_file}). "allow" or "deny" only.')
            if 'rules' not in yml['cmdrule']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "rules" not found in "cmdrule". ({self.signin_file})')
            if type(yml['cmdrule']['rules']) is not list:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "rules" not list type in "cmdrule". ({self.signin_file})')
            for rule in yml['cmdrule']['rules']:
                if 'groups' not in rule:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not found in "cmdrule.rules" ({self.signin_file})')
                if type(rule['groups']) is not list:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not list type in "cmdrule.rules". ({self.signin_file})')
                rule['groups'] = list(set(self.correct_group(rule['groups'], yml['groups'])))
                if 'rule' not in rule:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "rule" not found in "cmdrule.rules" ({self.signin_file})')
                if rule['rule'] not in ['allow', 'deny']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "rule" not supported in "cmdrule.rules". ({self.signin_file}). "allow" or "deny" only.')
                if 'mode' not in rule:
                    rule['mode'] = None
                if 'cmds' not in rule:
                    rule['cmds'] = []
                if rule['mode'] is not None and len(rule['cmds']) <= 0:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. When “cmds” is specified, “mode” must be specified. ({self.signin_file})')
                if type(rule['cmds']) is not list:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "cmds" not list type in "cmdrule.rules". ({self.signin_file})')
            # pathruleのフォーマットチェック
            if 'pathrule' not in yml:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "pathrule" not found. ({self.signin_file})')
            if 'policy' not in yml['pathrule']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "policy" not found in "pathrule". ({self.signin_file})')
            if yml['pathrule']['policy'] not in ['allow', 'deny']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "policy" not supported in "pathrule". ({self.signin_file}). "allow" or "deny" only.')
            if 'rules' not in yml['pathrule']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "rules" not found in "pathrule". ({self.signin_file})')
            if type(yml['pathrule']['rules']) is not list:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "rules" not list type in "pathrule". ({self.signin_file})')
            for rule in yml['pathrule']['rules']:
                if 'groups' not in rule:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not found in "pathrule.rules" ({self.signin_file})')
                if type(rule['groups']) is not list:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not list type in "pathrule.rules". ({self.signin_file})')
                rule['groups'] = list(set(self.correct_group(rule['groups'], yml['groups'])))
                if 'rule' not in rule:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "rule" not found in "pathrule.rules" ({self.signin_file})')
                if rule['rule'] not in ['allow', 'deny']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "rule" not supported in "pathrule.rules". ({self.signin_file}). "allow" or "deny" only.')
                if 'paths' not in rule:
                    rule['paths'] = []
                if type(rule['paths']) is not list:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "paths" not list type in "pathrule.rules". ({self.signin_file})')
            # フォーマットチェックOK
            self.signin_file_data = yml

    def user_list(self, name:str=None) -> List[Dict[str, Any]]:
        """
        サインインファイルのユーザー一覧を取得する

        Args:
            name (str, optional): ユーザー名. Defaults to None.

        Returns:
            List[Dict[str, Any]]: ユーザー一覧
        """
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        ret = []
        for u in copy.deepcopy(self.signin_file_data['users']):
            del u['password']
            if u['name'] == name:
                return [u]
            if name is None:
                ret.append(u)
        return ret

    def user_add(self, user:Dict[str, Any]):
        """
        サインインファイルにユーザーを追加する

        Args:
            user (Dict[str, Any]): ユーザー情報
        """
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if 'uid' not in user:
            raise ValueError(f"User uid is not found. ({user})")
        if 'name' not in user:
            raise ValueError(f"User name is not found. ({user})")
        if 'password' not in user:
            raise ValueError(f"User password is not found. ({user})")
        if 'hash' not in user:
            raise ValueError(f"User hash is not found. ({user})")
        if 'groups' not in user:
            raise ValueError(f"User groups is not found. ({user})")
        for gn in user['groups']:
            if len(self.group_list(gn)) <= 0:
                raise ValueError(f"Group is not found. ({gn})")
        if len([u for u in self.signin_file_data['users'] if u['uid'] == user['uid']]) > 0:
            raise ValueError(f"User uid is already exists. ({user})")
        if len([u for u in self.signin_file_data['users'] if u['name'] == user['name']]) > 0:
            raise ValueError(f"User name is already exists. ({user})")
        if user['hash'] not in ['plain', 'md5', 'sha1', 'sha256']:
            raise ValueError(f"User hash is not supported. ({user})")
        user['password'] = common.hash_password(user['password'], user['hash'])
        self.signin_file_data['users'].append(user)
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"user_add: {user} -> {self.signin_file}")
        common.save_yml(self.signin_file, self.signin_file_data)

    def user_edit(self, user:Dict[str, Any]):
        """
        サインインファイルのユーザー情報を編集する

        Args:
            user (Dict[str, Any]): ユーザー情報
        """
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if 'uid' not in user:
            raise ValueError(f"User uid is not found. ({user})")
        if 'name' not in user:
            raise ValueError(f"User name is not found. ({user})")
        if 'password' not in user:
            raise ValueError(f"User password is not found. ({user})")
        if 'hash' not in user:
            raise ValueError(f"User hash is not found. ({user})")
        if 'groups' not in user:
            raise ValueError(f"User groups is not found. ({user})")
        for gn in user['groups']:
            if len(self.group_list(gn)) <= 0:
                raise ValueError(f"Group is not found. ({gn})")
        if len([u for u in self.signin_file_data['users'] if u['uid'] == user['uid']]) <= 0:
            raise ValueError(f"User uid is not found. ({user})")
        if len([u for u in self.signin_file_data['users'] if u['name'] == user['name']]) > 0:
            raise ValueError(f"User name is already exists. ({user})")
        if user['hash'] not in ['plain', 'md5', 'sha1', 'sha256']:
            raise ValueError(f"User hash is not supported. ({user})")
        for u in self.signin_file_data['users']:
            if u['uid'] == user['uid']:
                u['name'] = user['name']
                u['password'] = common.hash_password(user['password'], user['hash'])
                u['hash'] = user['hash']
                u['groups'] = user['groups']
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"user_edit: {user} -> {self.signin_file}")
        common.save_yml(self.signin_file, self.signin_file_data)

    def user_del(self, uid:int):
        """
        サインインファイルからユーザーを削除する

        Args:
            uid (int): ユーザーID
        """
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        users = [u for u in self.signin_file_data['users'] if u['uid'] != uid]
        if len(users) == len(self.signin_file_data['users']):
            raise ValueError(f"User uid is not found. ({uid})")
        self.signin_file_data['users'] = users
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"user_del: {uid} -> {self.signin_file}")
        common.save_yml(self.signin_file, self.signin_file_data)

    def group_list(self, name:str=None) -> List[Dict[str, Any]]:
        """
        サインインファイルのグループ一覧を取得する

        Args:
            name (str, optional): グループ名. Defaults to None.

        Returns:
            List[Dict[str, Any]]: グループ一覧
        """
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if name is None:
            return copy.deepcopy(self.signin_file_data['groups'])
        for g in copy.deepcopy(self.signin_file_data['groups']):
            if g['name'] == name:
                return [g]
        return []

    def group_add(self, group:Dict[str, Any]):
        """
        サインインファイルにグループを追加する

        Args:
            group (Dict[str, Any]): グループ情報
        """
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if 'gid' not in group:
            raise ValueError(f"Group gid is not found. ({group})")
        if 'name' not in group:
            raise ValueError(f"Group name is not found. ({group})")
        if 'parent' not in group:
            raise ValueError(f"Group parent is not found. ({group})")
        if group['parent'] not in [g['name'] for g in self.signin_file_data['groups']]:
            raise ValueError(f"Group parent is not found. ({group})")
        if len([g for g in self.signin_file_data['groups'] if g['gid'] == group['gid']]) > 0:
            raise ValueError(f"Group gid is already exists. ({group})")
        if len([g for g in self.signin_file_data['groups'] if g['name'] == group['name']]) > 0:
            raise ValueError(f"Group name is already exists. ({group})")
        self.signin_file_data['groups'].append(group)
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"group_add: {group} -> {self.signin_file}")
        common.save_yml(self.signin_file, self.signin_file_data)

    def group_edit(self, group:Dict[str, Any]):
        """
        サインインファイルのグループ情報を編集する

        Args:
            group (Dict[str, Any]): グループ情報
        """
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if 'gid' not in group:
            raise ValueError(f"Group gid is not found. ({group})")
        if 'name' not in group:
            raise ValueError(f"Group name is not found. ({group})")
        if 'parent' not in group:
            raise ValueError(f"Group parent is not found. ({group})")
        if group['parent'] not in [g['name'] for g in self.signin_file_data['groups']]:
            raise ValueError(f"Group parent is not found. ({group})")
        if len([g for g in self.signin_file_data['groups'] if g['gid'] == group['gid']]) <= 0:
            raise ValueError(f"Group gid is not found. ({group})")
        if len([g for g in self.signin_file_data['groups'] if g['name'] == group['name']]) > 0:
            raise ValueError(f"Group name is already exists. ({group})")
        for g in self.signin_file_data['groups']:
            if g['gid'] == group['gid']:
                g['name'] = group['name']
                g['parent'] = group['parent']
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"group_edit: {group} -> {self.signin_file}")
        common.save_yml(self.signin_file, self.signin_file_data)

    def group_del(self, gid:int):
        """
        サインインファイルからグループを削除する

        Args:
            gid (int): グループID
        """
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        groups = [g for g in self.signin_file_data['groups'] if g['gid'] != gid]
        if self.signin_file is None:
            raise ValueError(f"signin_file is None.")
        if len(groups) == len(self.signin_file_data['groups']):
            raise ValueError(f"Group gid is not found. ({gid})")
        self.signin_file_data['groups'] = groups
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"group_del: {gid} -> {self.signin_file}")
        common.save_yml(self.signin_file, self.signin_file_data)

    def start(self, allow_host:str="0.0.0.0", listen_port:int=8081,
              ssl_cert:Path=None, ssl_key:Path=None, ssl_keypass:str=None, ssl_ca_certs:Path=None,
              session_timeout:int=600, outputs_key:List[str]=[]):
        """
        Webサーバを起動する

        Args:
            allow_host (str, optional): 許可ホスト. Defaults to "
            listen_port (int, optional): リスンポート. Defaults to 8081.
            ssl_cert (Path, optional): SSL証明書ファイル. Defaults to None.
            ssl_key (Path, optional): SSL秘密鍵ファイル. Defaults to None.
            ssl_keypass (str, optional): SSL秘密鍵パスワード. Defaults to None.
            ssl_ca_certs (Path, optional): SSL CA証明書ファイル. Defaults to None.
            session_timeout (int, optional): セッションタイムアウト. Defaults to 600.
            outputs_key (list, optional): 出力キー. Defaults to [].
        """
        self.allow_host = allow_host
        self.listen_port = listen_port
        self.ssl_cert = ssl_cert
        self.ssl_key = ssl_key
        self.ssl_keypass = ssl_keypass
        self.ssl_ca_certs = ssl_ca_certs
        self.outputs_key = outputs_key
        self.session_timeout = session_timeout
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"web start parameter: allow_host={self.allow_host}")
            self.logger.debug(f"web start parameter: listen_port={self.listen_port}")
            self.logger.debug(f"web start parameter: ssl_cert={self.ssl_cert} -> {self.ssl_cert.absolute() if self.ssl_cert is not None else None}")
            self.logger.debug(f"web start parameter: ssl_key={self.ssl_key} -> {self.ssl_key.absolute() if self.ssl_key is not None else None}")
            self.logger.debug(f"web start parameter: ssl_keypass={self.ssl_keypass}")
            self.logger.debug(f"web start parameter: ssl_ca_certs={self.ssl_ca_certs} -> {self.ssl_ca_certs.absolute() if self.ssl_ca_certs is not None else None}")
            self.logger.debug(f"web start parameter: outputs_key={self.outputs_key}")
            self.logger.debug(f"web start parameter: session_timeout={self.session_timeout}")

        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key=common.random_string())
        self.init_webfeatures(app)

        self.is_running = True
        #uvicorn.run(app, host=self.allow_host, port=self.listen_port, workers=2)
        th = ThreadedUvicorn(config=Config(app=app, host=self.allow_host, port=self.listen_port,
                                           ssl_certfile=self.ssl_cert, ssl_keyfile=self.ssl_key,
                                           ssl_keyfile_password=self.ssl_keypass, ssl_ca_certs=self.ssl_ca_certs))
        th.start()
        try:
            if self.gui_mode:
                webbrowser.open(f'http://localhost:{self.listen_port}/gui')
            with open("web.pid", mode="w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
            while self.is_running:
                gevent.sleep(1)
            th.stop()
        except KeyboardInterrupt:
            th.stop()

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
    def __init__(self, config: Config):
        self.server = uvicorn.Server(config)
        self.thread = threading.Thread(daemon=True, target=self.server.run)

    def start(self):
        self.thread.start()
        asyncio.run(self.wait_for_started())

    async def wait_for_started(self):
        while not self.server.started:
            await asyncio.sleep(0.1)

    def stop(self):
        if self.thread.is_alive():
            self.server.should_exit = True
            while self.thread.is_alive():
                continue

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
