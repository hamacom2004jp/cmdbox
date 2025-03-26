from cmdbox.app import common
from cmdbox.app.auth.signin import Signin
from cmdbox.app.commons import convert
from cmdbox.app.features.web import cmdbox_web_signin
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import copy
import datetime
import importlib
import inspect
import json
import logging
import requests
import urllib.parse


class DoSignin(cmdbox_web_signin.Signin):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/dosignin/{next}', response_class=HTMLResponse)
        async def do_signin(next:str, req:Request, res:Response):
            return await do_signin_token(None, next, req, res)

        @app.get('/dosignin_token/{token}/{next}', response_class=HTMLResponse)
        async def do_signin_token(token:str, next:str, req:Request, res:Response):
            form = await req.form()
            name = form.get('name')
            passwd = form.get('password')
            # edgeからtokenによる認証の場合
            signin_data = web.signin.get_data()
            token_ok = False
            if token is not None:
                if web.logger.level == logging.DEBUG:
                    web.logger.debug(f'token={token}')
                token = convert.b64str2str(token)
                token = json.loads(token)
                name = token['user']
                user = [u for u in signin_data['users'] if u['name'] == name]
                if len(user) <= 0:
                    raise HTTPException(status_code=401, detail='Unauthorized')
                user = user[0]
                if token['auth_type'] =="idpw" and 'password' in user:
                    jg = common.decrypt(token['token'], user['password'])
                    token_ok = True if jg is not None else False
                elif token['auth_type'] =="apikey" and 'apikeys' in user:
                    for ak, at in user['apikeys'].items():
                        try:
                            jg = common.decrypt(token['token'], at)
                            token_ok = True if jg is not None else False
                        except:
                            pass
            if not token_ok:
                if name == '' or passwd == '':
                    return RedirectResponse(url=f'/signin/{next}?error=1')
                user = [u for u in signin_data['users'] if u['name'] == name and u['hash'] != 'oauth2']
                if len(user) <= 0:
                    return RedirectResponse(url=f'/signin/{next}?error=1')
                user = user[0]
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f'Try signin, uid={user["uid"]}, user_name={user["name"]}')
            uid = user['uid']
            # ロックアウトチェック
            pass_miss_count = web.user_data(None, uid, name, 'password', 'pass_miss_count')
            pass_miss_count = 0 if pass_miss_count is None else int(pass_miss_count)
            if 'password' in signin_data and signin_data['password']['lockout']['enabled']:
                threshold = signin_data['password']['lockout']['threshold']
                reset = signin_data['password']['lockout']['reset']
                pass_miss_last = web.user_data(None, uid, name, 'password', 'pass_miss_last')
                if pass_miss_last is None:
                    pass_miss_last = web.user_data(None, uid, name, 'password', 'pass_miss_last', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
                pass_miss_last = datetime.datetime.strptime(pass_miss_last, '%Y-%m-%dT%H:%M:%S')
                if datetime.datetime.now() > pass_miss_last + datetime.timedelta(minutes=reset):
                    # ロックアウトリセット
                    pass_miss_count = 0
                    web.user_data(None, uid, name, 'password', 'pass_miss_count', pass_miss_count)
                    web.logger.info(f'Reset pass_miss_count. name={name}')
                if pass_miss_count >= threshold:
                    # ロックアウト
                    web.user_data(None, uid, name, 'password', 'pass_miss_count', )
                    return RedirectResponse(url=f'/signin/{next}?error=lockout')

            if not token_ok:
                # パスワード認証
                hash = user['hash']
                if hash != 'plain':
                    passwd = common.hash_password(passwd, hash)
                if passwd != user['password']:
                    # パスワード間違いの日時と回数を記録
                    web.user_data(None, uid, name, 'password', 'pass_miss_last', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
                    web.user_data(None, uid, name, 'password', 'pass_miss_count', pass_miss_count+1)
                    web.logger.warning(f'Failed to signin. name={name}, pass_miss_count={pass_miss_count+1}')
                    return RedirectResponse(url=f'/signin/{next}?error=1')
            group_names = list(set(web.signin.__class__.correct_group(signin_data, user['groups'], None)))
            gids = [g['gid'] for g in signin_data['groups'] if g['name'] in group_names]
            email = user.get('email', '')
            # パスワード最終更新日時取得
            last_update = web.user_data(None, uid, name, 'password', 'last_update')
            notify_passchange = True if last_update is None else False
            # パスワード認証の場合はパスワード有効期限チェック
            if user['hash']!='oauth2' and 'password' in signin_data and not notify_passchange:
                last_update = datetime.datetime.strptime(last_update, '%Y-%m-%dT%H:%M:%S')
                # パスワード有効期限
                expiration = signin_data['password']['expiration']
                if expiration['enabled']:
                    period = expiration['period']
                    notify = expiration['notify']
                    # パスワード有効期限チェック
                    if datetime.datetime.now() > last_update + datetime.timedelta(days=period):
                        return RedirectResponse(url=f'/signin/{next}?error=expirationofpassword')
                    if datetime.datetime.now() > last_update + datetime.timedelta(days=notify):
                        # セッションに保存
                        _set_session(req, dict(uid=uid, name=name), email, passwd, None, group_names, gids)
                        next = f"../{next}" if token_ok else next
                        return RedirectResponse(url=f'../{next}?warn=passchange', headers=dict(signin="success")) # nginxのリバプロ対応のための相対パス
            # セッションに保存
            _set_session(req, dict(uid=uid, name=name), email, passwd, None, group_names, gids)
            next = f"../{next}" if token_ok else next
            return RedirectResponse(url=f'../{next}{"?warn=passchange" if notify_passchange else ""}', headers=dict(signin="success")) # nginxのリバプロ対応のための相対パス

        def _load_signin(web:Web, signin_module:str, appcls, ver):
            """
            サインインオブジェクトを読込む
            
            Args:
                signin_module (str): サインインオブジェクトのモジュール名
                appcls (class): アプリケーションクラス
                ver (str): バージョン
            Returns:
                signin.Signin: サインインオブジェクト
            """
            if signin_module is None:
                return None
            try:
                mod = importlib.import_module(signin_module)
                members = inspect.getmembers(mod, inspect.isclass)
                signin_data = web.signin.get_data()
                for name, cls in members:
                    if cls is Signin or issubclass(cls, Signin):
                        sobj = cls(web.logger, web.signin_file, signin_data, appcls, ver)
                        return sobj
                return None
            except Exception as e:
                web.logger.error(f'Failed to load signin. {e}', exc_info=True)
                raise e

        signin_data = web.signin.get_data()
        self.google_signin = Signin(web.logger, web.signin_file, signin_data, self.appcls, self.ver)
        self.github_signin = Signin(web.logger, web.signin_file, signin_data, self.appcls, self.ver)
        self.azure_signin = Signin(web.logger, web.signin_file, signin_data, self.appcls, self.ver)
        if signin_data is not None:
            # signinオブジェクトの指定があった場合読込む
            if 'signin_module' in signin_data['oauth2']['providers']['google']:
                sobj = _load_signin(web, signin_data['oauth2']['providers']['google']['signin_module'], self.appcls, self.ver)
                self.google_signin = sobj if sobj is not None else self.google_signin
            if 'signin_module' in signin_data['oauth2']['providers']['github']:
                sobj = _load_signin(web, signin_data['oauth2']['providers']['github']['signin_module'], self.appcls, self.ver)
                self.github_signin = sobj if sobj is not None else self.github_signin
            if 'signin_module' in signin_data['oauth2']['providers']['azure']:
                sobj = _load_signin(web, signin_data['oauth2']['providers']['azure']['signin_module'], self.appcls, self.ver)
                self.azure_signin = sobj if sobj is not None else self.azure_signin

        def _set_session(req:Request, user:dict, email:str, hashed_password:str, access_token:str, group_names:list, gids:list):
            """
            セッションに保存する

            Args:
                req (Request): Requestオブジェクト
                user (dict): ユーザー情報
                email (str): メールアドレス
                hashed_password (str): パスワード
                access_token (str): アクセストークン
                group_names (list): グループ名リスト
                gids (list): グループIDリスト
            """
            # 最終サインイン日時更新
            web.user_data(None, user['uid'], user['name'], 'signin', 'last_update', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
            if access_token is not None:
                # パスワード最終更新日時削除
                web.user_data(None, user['uid'], user['name'], 'password', 'last_update', delkey=True)
            else:
                # パスワード間違いの日時削除
                web.user_data(None, user['uid'], user['name'], 'password', 'pass_miss_last', None, delkey=True)
                # パスワード間違い回数削除
                web.user_data(None, user['uid'], user['name'], 'password', 'pass_miss_count', 0, delkey=True)
            # セッションに保存
            req.session['signin'] = dict(uid=user['uid'], name=user['name'],
                                         password=hashed_password, access_token=access_token,
                                         gids=gids, groups=group_names, email=email)
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f'Set session, uid={user["uid"]}, name={user["name"]}, email={email}, gids={gids}, groups={group_names}')

        @app.get('/oauth2/google/callback')
        async def oauth2_google_callback(req:Request, res:Response):
            conf = web.signin.get_data()['oauth2']['providers']['google']
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            next = req.query_params['state']
            data = {'code': req.query_params['code'],
                    'client_id': conf['client_id'],
                    'client_secret': conf['client_secret'],
                    'redirect_uri': conf['redirect_uri'],
                    'grant_type': 'authorization_code'}
            query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
            try:
                # アクセストークン取得
                token_resp = requests.post(url='https://oauth2.googleapis.com/token', headers=headers, data=query)
                token_resp.raise_for_status()
                token_json = token_resp.json()
                access_token = token_json['access_token']
                return await oauth2_google_session(access_token, next, req, res)
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

        @app.get('/oauth2/google/session/{access_token}/{next}')
        async def oauth2_google_session(access_token:str, next:str, req:Request, res:Response):
            try:
                # ユーザー情報取得(email)
                user_info_resp = requests.get(
                    url='https://www.googleapis.com/oauth2/v1/userinfo',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                user_info_resp.raise_for_status()
                user_info_json = user_info_resp.json()
                email = user_info_json['email']
                # サインイン判定
                jadge, user = self.google_signin.jadge(access_token, email)
                if not jadge:
                    return RedirectResponse(url=f'/signin/{next}?error=appdeny')
                # グループ取得
                group_names, gids = self.google_signin.get_groups(access_token, user)
                # セッションに保存
                _set_session(req, user, email, None, access_token, group_names, gids)
                return RedirectResponse(url=f'../../{next}', headers=dict(signin="success")) # nginxのリバプロ対応のための相対パス
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

        @app.get('/oauth2/github/callback')
        async def oauth2_github_callback(req:Request, res:Response):
            conf = web.signin.get_data()['oauth2']['providers']['github']
            headers = {'Content-Type': 'application/x-www-form-urlencoded',
                       'Accept': 'application/json'}
            next = req.query_params['state']
            data = {'code': req.query_params['code'],
                    'client_id': conf['client_id'],
                    'client_secret': conf['client_secret'],
                    'redirect_uri': conf['redirect_uri']}
            query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
            try:
                # アクセストークン取得
                token_resp = requests.post(url='https://github.com/login/oauth/access_token', headers=headers, data=query)
                token_resp.raise_for_status()
                token_json = token_resp.json()
                access_token = token_json['access_token']
                return await oauth2_github_session(access_token, next, req, res)
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

        @app.get('/oauth2/github/session/{access_token}/{next}')
        async def oauth2_github_session(access_token:str, next:str, req:Request, res:Response):
            try:
                # ユーザー情報取得(email)
                user_info_resp = requests.get(
                    url='https://api.github.com/user/emails',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                user_info_resp.raise_for_status()
                user_info_json = user_info_resp.json()
                if type(user_info_json) == list:
                    email = 'notfound'
                    for u in user_info_json:
                        if u['primary']:
                            email = u['email']
                            break
                # サインイン判定
                jadge, user = self.github_signin.jadge(access_token, email)
                if not jadge:
                    return RedirectResponse(url=f'/signin/{next}?error=appdeny')
                # グループ取得
                group_names, gids = self.github_signin.get_groups(access_token, user)
                # セッションに保存
                _set_session(req, user, email, None, access_token, group_names, gids)
                return RedirectResponse(url=f'../../{next}', headers=dict(signin="success")) # nginxのリバプロ対応のための相対パス
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

        @app.get('/oauth2/azure/callback')
        async def oauth2_azure_callback(req:Request, res:Response):
            conf = web.signin.get_data()['oauth2']['providers']['azure']
            headers = {'Content-Type': 'application/x-www-form-urlencoded',
                       'Accept': 'application/json'}
            next = req.query_params['state']
            data = {'tenant': conf['tenant_id'],
                    'code': req.query_params['code'],
                    'scope': " ".join(conf['scope']),
                    'client_id': conf['client_id'],
                    #'client_secret': conf['client_secret'],
                    'redirect_uri': conf['redirect_uri'],
                    'grant_type': 'authorization_code'}
            query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
            try:
                # アクセストークン取得
                token_resp = requests.post(url=f'https://login.microsoftonline.com/{conf["tenant_id"]}/oauth2/v2.0/token', headers=headers, data=query)
                token_resp.raise_for_status()
                token_json = token_resp.json()
                access_token = token_json['access_token']
                return await oauth2_azure_session(access_token, next, req, res)
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

        @app.get('/oauth2/azure/session/{access_token}/{next}')
        async def oauth2_azure_session(access_token:str, next:str, req:Request, res:Response):
            try:
                # ユーザー情報取得(email)
                user_info_resp = requests.get(
                    url='https://graph.microsoft.com/v1.0/me',
                    #url='https://graph.microsoft.com/v1.0/me/transitiveMemberOf?$Top=999',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                user_info_resp.raise_for_status()
                user_info_json = user_info_resp.json()
                if isinstance(user_info_json, dict):
                    email = user_info_json.get('mail', 'notfound')
                # サインイン判定
                jadge, user = self.azure_signin.jadge(access_token, email)
                if not jadge:
                    return RedirectResponse(url=f'/signin/{next}?error=appdeny')
                # グループ取得
                group_names, gids = self.azure_signin.get_groups(access_token, user)
                # セッションに保存
                _set_session(req, user, email, None, access_token, group_names, gids)
                return RedirectResponse(url=f'../../{next}', headers=dict(signin="success")) # nginxのリバプロ対応のための相対パス
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')
