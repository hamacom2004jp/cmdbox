from cmdbox.app import common, options
from fastapi import Request, Response, HTTPException
from fastapi.responses import RedirectResponse
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import copy
import logging


class Signin(object):

    def __init__(self, logger:logging.Logger, signin_file:Path, signin_file_data:Dict[str, Any], appcls, ver):
        self.logger = logger
        self.signin_file = signin_file
        self.signin_file_data = signin_file_data
        self.options = options.Options.getInstance(appcls, ver)
        self.ver = ver
        self.appcls = appcls

    def get_data(self) -> Dict[str, Any]:
        """
        サインインデータを返します

        Returns:
            Dict[str, Any]: サインインデータ
        """
        return self.signin_file_data

    def jadge(self, access_token:str, email:str) -> Tuple[bool, Dict[str, Any]]:
        """
        サインインを成功させるかどうかを判定します。
        返すユーザーデータには、uid, name, email, groups, hash が必要です。

        Args:
            access_token (str): アクセストークン
            email (str): メールアドレス

        Returns:
            Tuple[bool, Dict[str, Any]]: (成功かどうか, ユーザーデータ)
        """
        copy_signin_data = copy.deepcopy(self.signin_file_data)
        users = [u for u in copy_signin_data['users'] if u['email'] == email and u['hash'] == 'oauth2']
        return len(users) > 0, users[0] if len(users) > 0 else None

    def get_groups(self, access_token:str, user:Dict[str, Any]) -> Tuple[List[str], List[int]]:
        """
        ユーザーのグループを取得します

        Args:
            access_token (str): アクセストークン
            user (Dict[str, Any]): ユーザーデータ
            signin_file_data (Dict[str, Any]): サインインファイルデータ（変更不可）

        Returns:
            Tuple[List[str], List[int]]: (グループ名, グループID)
        """
        copy_signin_data = copy.deepcopy(self.signin_file_data)
        group_names = list(set(self.__class__.correct_group(copy_signin_data, user['groups'], None)))
        gids = [g['gid'] for g in copy_signin_data['groups'] if g['name'] in group_names]
        return group_names, gids

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
        if self.signin_file_data is None:
            return None
        if 'signin' in req.session:
            self.signin_file_data = self.load_signin_file(self.signin_file, self.signin_file_data) # サインインファイルの更新をチェック
            path_jadge = self.check_path(req, req.url.path)
            if path_jadge is not None:
                return path_jadge
            return None
        self.logger.info(f"Not found siginin session. Try check_apikey. path={req.url.path}")
        ret = self.check_apikey(req, res)
        if ret is not None and self.logger.level == logging.DEBUG:
            self.logger.debug(f"Not signed in.")
        return ret

    def check_apikey(self, req:Request, res:Response):
        """
        ApiKeyをチェックする

        Args:
            req (Request): リクエスト
            res (Response): レスポンス

        Returns:
            Response: サインインエラーの場合はリダイレクトレスポンス
        """
        self.enable_cors(req, res)
        if self.signin_file_data is None:
            res.headers['signin'] = 'success'
            return None
        if 'Authorization' not in req.headers:
            self.logger.warning(f"Authorization not found. headers={req.headers}")
            return RedirectResponse(url=f'/signin{req.url.path}?error=noauth')
        auth = req.headers['Authorization']
        if not auth.startswith('Bearer '):
            self.logger.warning(f"Bearer not found. headers={req.headers}")
            return RedirectResponse(url=f'/signin{req.url.path}?error=apikeyfail')
        bearer, apikey = auth.split(' ')
        apikey = common.hash_password(apikey.strip(), 'sha1')
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"hashed apikey: {apikey}")
        find_user = None
        self.signin_file_data = self.load_signin_file(self.signin_file, self.signin_file_data) # サインインファイルの更新をチェック
        for user in self.signin_file_data['users']:
            if 'apikeys' not in user:
                continue
            for ak, key in user['apikeys'].items():
                if apikey == key:
                    find_user = user
        if find_user is None:
            self.logger.warning(f"No matching user found for apikey.")
            return RedirectResponse(url=f'/signin{req.url.path}?error=apikeyfail')

        group_names = list(set(self.__class__.correct_group(self.get_data(), find_user['groups'], None)))
        gids = [g['gid'] for g in self.signin_file_data['groups'] if g['name'] in group_names]
        req.session['signin'] = dict(uid=find_user['uid'], name=find_user['name'], password=find_user['password'],
                                     gids=gids, groups=group_names)
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"find user: name={find_user['name']}, group_names={group_names}")
        # パスルールチェック
        user_groups = find_user['groups']
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
            res.headers['signin'] = 'success'
            return None
        self.logger.warning(f"Unauthorized site. user={find_user['name']}, path={req.url.path}")
        return RedirectResponse(url=f'/signin{req.url.path}?error=unauthorizedsite')

    @classmethod
    def load_signin_file(cls, signin_file:Path, signin_file_data:Dict[str, Any]=None) -> Dict[str, Any]:
        """
        サインインファイルを読み込む

        Args:
            signin_file (Path): サインインファイル
            signin_file_data (Dict[str, Any]): サインインファイルデータ

        Raises:
            HTTPException: サインインファイルのフォーマットエラー

        Returns:
            Dict[str, Any]: サインインファイルデータ
        """
        if signin_file is not None:
            if not signin_file.is_file():
                raise HTTPException(status_code=500, detail=f'signin_file is not found. ({signin_file})')
            # サインインファイル読込み済みなら返すが、別プロセスがサインインファイルを更新していたら読込みを実施する。
            if not hasattr(cls, 'signin_file_last'):
                cls.signin_file_last = signin_file.stat().st_mtime
            if cls.signin_file_last >= signin_file.stat().st_mtime and signin_file_data is not None:
                return signin_file_data
            cls.signin_file_last = signin_file.stat().st_mtime
            yml = common.load_yml(signin_file)
            # usersのフォーマットチェック
            if 'users' not in yml:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "users" not found. ({signin_file})')
            uids = set()
            unames = set()
            groups = [g['name'] for g in yml['groups']]
            for user in yml['users']:
                if 'uid' not in user or user['uid'] is None:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "uid" not found or empty. ({signin_file})')
                if user['uid'] in uids:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. Duplicate uid found. ({signin_file}). uid={user["uid"]}')
                if 'name' not in user or user['name'] is None:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "name" not found or empty. ({signin_file})')
                if user['name'] in unames:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. Duplicate name found. ({signin_file}). name={user["name"]}')
                if 'password' not in user:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "password" not found or empty. ({signin_file})')
                if 'hash' not in user or user['hash'] is None:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "hash" not found or empty. ({signin_file})')
                if user['hash'] not in ['oauth2', 'plain', 'md5', 'sha1', 'sha256']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. Algorithms not supported. ({signin_file}). hash={user["hash"]} "oauth2", "plain", "md5", "sha1", "sha256" only.')
                if 'groups' not in user or type(user['groups']) is not list:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not found or not list type. ({signin_file})')
                if len([ug for ug in user['groups'] if ug not in groups]) > 0:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. Group not found. ({signin_file}). {user["groups"]}')
                uids.add(user['uid'])
                unames.add(user['name'])
            # groupsのフォーマットチェック
            if 'groups' not in yml:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not found. ({signin_file})')
            gids = set()
            gnames = set()
            for group in yml['groups']:
                if 'gid' not in group or group['gid'] is None:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "gid" not found or empty. ({signin_file})')
                if group['gid'] in gids:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. Duplicate gid found. ({signin_file}). gid={group["gid"]}')
                if 'name' not in group or group['name'] is None:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "name" not found or empty. ({signin_file})')
                if group['name'] in gnames:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. Duplicate name found. ({signin_file}). name={group["name"]}')
                if 'parent' in group:
                    if group['parent'] not in groups:
                        raise HTTPException(status_code=500, detail=f'signin_file format error. Parent group not found. ({signin_file}). parent={group["parent"]}')
                gids.add(group['gid'])
                gnames.add(group['name'])
            # cmdruleのフォーマットチェック
            if 'cmdrule' not in yml:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "cmdrule" not found. ({signin_file})')
            if 'policy' not in yml['cmdrule']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "policy" not found in "cmdrule". ({signin_file})')
            if yml['cmdrule']['policy'] not in ['allow', 'deny']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "policy" not supported in "cmdrule". ({signin_file}). "allow" or "deny" only.')
            if 'rules' not in yml['cmdrule']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "rules" not found in "cmdrule". ({signin_file})')
            if type(yml['cmdrule']['rules']) is not list:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "rules" not list type in "cmdrule". ({signin_file})')
            for rule in yml['cmdrule']['rules']:
                if 'groups' not in rule:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not found in "cmdrule.rules" ({signin_file})')
                if type(rule['groups']) is not list:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not list type in "cmdrule.rules". ({signin_file})')
                rule['groups'] = list(set(copy.deepcopy(cls.correct_group(yml, rule['groups'], yml['groups']))))
                if 'rule' not in rule:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "rule" not found in "cmdrule.rules" ({signin_file})')
                if rule['rule'] not in ['allow', 'deny']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "rule" not supported in "cmdrule.rules". ({signin_file}). "allow" or "deny" only.')
                if 'mode' not in rule:
                    rule['mode'] = None
                if 'cmds' not in rule:
                    rule['cmds'] = []
                if rule['mode'] is not None and len(rule['cmds']) <= 0:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. When “cmds” is specified, “mode” must be specified. ({signin_file})')
                if type(rule['cmds']) is not list:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "cmds" not list type in "cmdrule.rules". ({signin_file})')
            # pathruleのフォーマットチェック
            if 'pathrule' not in yml:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "pathrule" not found. ({signin_file})')
            if 'policy' not in yml['pathrule']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "policy" not found in "pathrule". ({signin_file})')
            if yml['pathrule']['policy'] not in ['allow', 'deny']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "policy" not supported in "pathrule". ({signin_file}). "allow" or "deny" only.')
            if 'rules' not in yml['pathrule']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "rules" not found in "pathrule". ({signin_file})')
            if type(yml['pathrule']['rules']) is not list:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "rules" not list type in "pathrule". ({signin_file})')
            for rule in yml['pathrule']['rules']:
                if 'groups' not in rule:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not found in "pathrule.rules" ({signin_file})')
                if type(rule['groups']) is not list:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "groups" not list type in "pathrule.rules". ({signin_file})')
                rule['groups'] = list(set(copy.deepcopy(cls.correct_group(yml, rule['groups'], yml['groups']))))
                if 'rule' not in rule:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "rule" not found in "pathrule.rules" ({signin_file})')
                if rule['rule'] not in ['allow', 'deny']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "rule" not supported in "pathrule.rules". ({signin_file}). "allow" or "deny" only.')
                if 'paths' not in rule:
                    rule['paths'] = []
                if type(rule['paths']) is not list:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "paths" not list type in "pathrule.rules". ({signin_file})')
            # passwordのフォーマットチェック
            if 'password' in yml:
                if 'policy' not in yml['password']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "policy" not found in "password". ({signin_file})')
                if 'enabled' not in yml['password']['policy']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not found in "password.policy". ({signin_file})')
                if type(yml['password']['policy']['enabled']) is not bool:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not bool type in "password.policy". ({signin_file})')
                if type(yml['password']['policy']['not_same_before']) is not bool:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "not_same_before" not bool type in "password.policy". ({signin_file})')
                if 'min_length' not in yml['password']['policy']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "min_length" not found in "password.policy". ({signin_file})')
                if type(yml['password']['policy']['min_length']) is not int:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "min_length" not int type in "password.policy". ({signin_file})')
                if 'max_length' not in yml['password']['policy']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "max_length" not found in "password.policy". ({signin_file})')
                if type(yml['password']['policy']['max_length']) is not int:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "max_length" not int type in "password.policy". ({signin_file})')
                if 'min_lowercase' not in yml['password']['policy']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "min_lowercase" not found in "password.policy". ({signin_file})')
                if type(yml['password']['policy']['min_lowercase']) is not int:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "min_lowercase" not int type in "password.policy". ({signin_file})')
                if 'min_uppercase' not in yml['password']['policy']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "min_uppercase" not found in "password.policy". ({signin_file})')
                if type(yml['password']['policy']['min_uppercase']) is not int:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "min_uppercase" not int type in "password.policy". ({signin_file})')
                if 'min_digit' not in yml['password']['policy']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "min_digit" not found in "password.policy". ({signin_file})')
                if type(yml['password']['policy']['min_digit']) is not int:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "min_digit" not int type in "password.policy". ({signin_file})')
                if 'min_symbol' not in yml['password']['policy']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "min_symbol" not found in "password.policy". ({signin_file})')
                if type(yml['password']['policy']['min_symbol']) is not int:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "min_symbol" not int type in "password.policy". ({signin_file})')
                if 'not_contain_username' not in yml['password']['policy']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "not_contain_username" not found in "password.policy". ({signin_file})')
                if type(yml['password']['policy']['not_contain_username']) is not bool:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "not_contain_username" not bool type in "password.policy". ({signin_file})')
                if 'expiration' not in yml['password']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "expiration" not found in "password". ({signin_file})')
                if 'enabled' not in yml['password']['expiration']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not found in "password.expiration". ({signin_file})')
                if type(yml['password']['expiration']['enabled']) is not bool:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not bool type in "password.expiration". ({signin_file})')
                if 'period' not in yml['password']['expiration']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "period" not found in "password.expiration". ({signin_file})')
                if type(yml['password']['expiration']['period']) is not int:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "period" not int type in "password.expiration". ({signin_file})')
                if 'notify' not in yml['password']['expiration']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "notify" not found in "password.expiration". ({signin_file})')
                if type(yml['password']['expiration']['notify']) is not int:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "notify" not int type in "password.expiration". ({signin_file})')
                if 'lockout' not in yml['password']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "lockout" not found in "password". ({signin_file})')
                if 'enabled' not in yml['password']['lockout']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not found in "password.lockout". ({signin_file})')
                if type(yml['password']['lockout']['enabled']) is not bool:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not bool type in "password.lockout". ({signin_file})')
                if 'threshold' not in yml['password']['lockout']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "threshold" not found in "password.lockout". ({signin_file})')
                if type(yml['password']['lockout']['threshold']) is not int:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "threshold" not int type in "password.lockout". ({signin_file})')
                if 'reset' not in yml['password']['lockout']:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "reset" not found in "password.lockout". ({signin_file})')
                if type(yml['password']['lockout']['reset']) is not int:
                    raise HTTPException(status_code=500, detail=f'signin_file format error. "reset" not int type in "password.lockout". ({signin_file})')
            # oauth2のフォーマットチェック
            if 'oauth2' not in yml:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "oauth2" not found. ({signin_file})')
            if 'providers' not in yml['oauth2']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "providers" not found in "oauth2". ({signin_file})')
            # google
            if 'google' not in yml['oauth2']['providers']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "google" not found in "providers". ({signin_file})')
            if 'enabled' not in yml['oauth2']['providers']['google']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not found in "google". ({signin_file})')
            if type(yml['oauth2']['providers']['google']['enabled']) is not bool:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not bool type in "google". ({signin_file})')
            if 'client_id' not in yml['oauth2']['providers']['google']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "client_id" not found in "google". ({signin_file})')
            if 'client_secret' not in yml['oauth2']['providers']['google']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "client_secret" not found in "google". ({signin_file})')
            if 'redirect_uri' not in yml['oauth2']['providers']['google']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "redirect_uri" not found in "google". ({signin_file})')
            if 'scope' not in yml['oauth2']['providers']['google']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "scope" not found in "google". ({signin_file})')
            if type(yml['oauth2']['providers']['google']['scope']) is not list:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "scope" not list type in "google". ({signin_file})')
            if 'signin_module' not in yml['oauth2']['providers']['google']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "signin_module" not found in "google". ({signin_file})')
            # github
            if 'github' not in yml['oauth2']['providers']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "github" not found in "providers". ({signin_file})')
            if 'enabled' not in yml['oauth2']['providers']['github']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not found in "github". ({signin_file})')
            if type(yml['oauth2']['providers']['github']['enabled']) is not bool:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not bool type in "github". ({signin_file})')
            if 'client_id' not in yml['oauth2']['providers']['github']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "client_id" not found in "github". ({signin_file})')
            if 'client_secret' not in yml['oauth2']['providers']['github']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "client_secret" not found in "github". ({signin_file})')
            if 'redirect_uri' not in yml['oauth2']['providers']['github']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "redirect_uri" not found in "github". ({signin_file})')
            if 'scope' not in yml['oauth2']['providers']['github']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "scope" not found in "github". ({signin_file})')
            if type(yml['oauth2']['providers']['github']['scope']) is not list:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "scope" not list type in "github". ({signin_file})')
            if 'signin_module' not in yml['oauth2']['providers']['github']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "signin_module" not found in "github". ({signin_file})')
            # azure
            if 'azure' not in yml['oauth2']['providers']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "azure" not found in "providers". ({signin_file})')
            if 'enabled' not in yml['oauth2']['providers']['azure']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not found in "azure". ({signin_file})')
            if type(yml['oauth2']['providers']['azure']['enabled']) is not bool:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "enabled" not bool type in "azure". ({signin_file})')
            if 'tenant_id' not in yml['oauth2']['providers']['azure']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "tenant_id" not found in "azure". ({signin_file})')
            if 'client_id' not in yml['oauth2']['providers']['azure']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "client_id" not found in "azure". ({signin_file})')
            if 'client_secret' not in yml['oauth2']['providers']['azure']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "client_secret" not found in "azure". ({signin_file})')
            if 'redirect_uri' not in yml['oauth2']['providers']['azure']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "redirect_uri" not found in "azure". ({signin_file})')
            if 'scope' not in yml['oauth2']['providers']['azure']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "scope" not found in "azure". ({signin_file})')
            if type(yml['oauth2']['providers']['azure']['scope']) is not list:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "scope" not list type in "azure". ({signin_file})')
            if 'signin_module' not in yml['oauth2']['providers']['azure']:
                raise HTTPException(status_code=500, detail=f'signin_file format error. "signin_module" not found in "azure". ({signin_file})')
            # フォーマットチェックOK
            return yml

    @classmethod
    def correct_group(cls, signin_file_data:Dict[str, Any], group_names:List[str], master_groups:List[Dict[str, Any]]) -> List[str]:
        """
        指定されたグループ名に属する子グループ名を収集します

        Args:
            signin_file_data (Dict[str, Any]): サインインファイルデータ
            group_names (List[str]): グループ名リスト
            master_groups (List[Dict[str, Any]], optional): 親グループ名. Defaults to None.
        """
        copy_signin_data = copy.deepcopy(signin_file_data)
        master_groups = copy_signin_data['groups'] if master_groups is None else master_groups
        gns = []
        for gn in group_names.copy():
            gns = [gr['name'] for gr in master_groups if 'parent' in gr and gr['parent']==gn]
            gns += cls.correct_group(copy_signin_data, gns, master_groups)
        return group_names + gns

    def check_path(self, req:Request, path:str) -> Union[None, RedirectResponse]:
        """
        パスの認可をチェックします

        Args:
            req (Request): リクエスト
            path (str): パス

        Returns:
            Union[None, RedirectResponse]: 認可された場合はNone、認可されなかった場合はリダイレクトレスポンス
        """
        if self.signin_file_data is None:
            return None
        if 'signin' not in req.session:
            return None
        path = path if path.startswith('/') else f'/{path}'
        # パスルールチェック
        user_groups = req.session['signin']['groups']
        jadge = self.signin_file_data['pathrule']['policy']
        for rule in self.signin_file_data['pathrule']['rules']:
            if len([g for g in rule['groups'] if g in user_groups]) <= 0:
                continue
            if len([p for p in rule['paths'] if path.startswith(p)]) <= 0:
                continue
            jadge = rule['rule']
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"rule: {path}: {jadge}")
        if jadge == 'allow':
            return None
        else:
            self.logger.warning(f"Unauthorized site. user={req.session['signin']['name']}, path={path}")
            return RedirectResponse(url=f'/signin{path}?error=unauthorizedsite')

    def check_cmd(self, req:Request, res:Response, mode:str, cmd:str):
        """
        コマンドの認可をチェックします

        Args:
            req (Request): リクエスト
            res (Response): レスポンス
            mode (str): モード
            cmd (str): コマンド

        Returns:
            bool: 認可されたかどうか
        """
        if self.signin_file_data is None:
            return True
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

    def get_enable_modes(self, req:Request, res:Response) -> List[str]:
        """
        認可されたモードを取得します

        Args:
            req (Request): リクエスト
            res (Response): レスポンス

        Returns:
            List[str]: 認可されたモード
        """
        if self.signin_file_data is None:
            return self.options.get_modes().copy()
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

    def get_enable_cmds(self, mode:str, req:Request, res:Response) -> List[str]:
        """
        認可されたコマンドを取得します

        Args:
            mode (str): モード
            req (Request): リクエスト
            res (Response): レスポンス

        Returns:
            List[str]: 認可されたコマンド
        """
        if self.signin_file_data is None:
            cmds = self.options.get_cmds(mode).copy()
            return cmds
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

    def check_password_policy(self, user_name:str, password:str, new_password:str) -> Tuple[bool, str]:
        """
        パスワードポリシーをチェックする

        Args:
            user_name (str): ユーザー名
            password (str): 元パスワード
            new_password (str): 新しいパスワード
        Returns:
            bool: True:ポリシーOK, False:ポリシーNG
            str: メッセージ
        """
        if self.signin_file_data is None or 'password' not in self.signin_file_data:
            return True, "There is no password policy set."
        policy = self.signin_file_data['password']['policy']
        if not policy['enabled']:
            return True, "Password policy is disabled."
        if policy['not_same_before'] and password == new_password:
            self.logger.warning(f"Password policy error. The same password cannot be changed.")
            return False, f"Password policy error. The same password cannot be changed."
        if len(new_password) < policy['min_length'] or len(new_password) > policy['max_length']:
            self.logger.warning(f"Password policy error. min_length={policy['min_length']}, max_length={policy['max_length']}")
            return False, f"Password policy error. min_length={policy['min_length']}, max_length={policy['max_length']}"
        if len([c for c in new_password if c.islower()]) < policy['min_lowercase']:
            self.logger.warning(f"Password policy error. min_lowercase={policy['min_lowercase']}")
            return False, f"Password policy error. min_lowercase={policy['min_lowercase']}"
        if len([c for c in new_password if c.isupper()]) < policy['min_uppercase']:
            self.logger.warning(f"Password policy error. min_uppercase={policy['min_uppercase']}")
            return False, f"Password policy error. min_uppercase={policy['min_uppercase']}"
        if len([c for c in new_password if c.isdigit()]) < policy['min_digit']:
            self.logger.warning(f"Password policy error. min_digit={policy['min_digit']}")
            return False, f"Password policy error. min_digit={policy['min_digit']}"
        if len([c for c in new_password if c in string.punctuation]) < policy['min_symbol']:
            self.logger.warning(f"Password policy error. min_symbol={policy['min_symbol']}")
            return False, f"Password policy error. min_symbol={policy['min_symbol']}"
        if policy['not_contain_username'] and (user_name is None or user_name in new_password):
            self.logger.warning(f"Password policy error. not_contain_username=True")
            return False, f"Password policy error. not_contain_username=True"
        self.logger.info(f"Password policy OK.")
        return True, "Password policy OK."
