from cmdbox.app import common, signin
from cmdbox.app.features.web import cmdbox_web_signin
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import copy
import datetime
import importlib
import inspect
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
            form = await req.form()
            name = form.get('name')
            passwd = form.get('password')
            if name == '' or passwd == '':
                return RedirectResponse(url=f'/signin/{next}?error=1')
            user = [u for u in web.signin_file_data['users'] if u['name'] == name and u['hash'] != 'oauth2']
            if len(user) <= 0:
                return RedirectResponse(url=f'/signin/{next}?error=1')
            hash = user[0]['hash']
            if hash != 'plain':
                passwd = common.hash_password(passwd, hash)
            if passwd != user[0]['password']:
                return RedirectResponse(url=f'/signin/{next}?error=1')
            group_names = list(set(web.correct_group(user[0]['groups'])))
            gids = [g['gid'] for g in web.signin_file_data['groups'] if g['name'] in group_names]
            uid = user[0]['uid']
            email = user[0].get('email', '')
            # 最終サインイン日時更新
            web.user_data(req, uid, name, 'signin', 'last_update', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
            # パスワード認証の場合はパスワード有効期限チェック
            if user[0]['hash']!='oauth2' and 'password' in web.signin_file_data:
                # パスワード最終更新日時
                last_update = web.user_data(req, uid, name, 'password', 'last_update')
                if last_update is None:
                    last_update = web.user_data(req, uid, name, 'password', 'last_update', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
                last_update = datetime.datetime.strptime(last_update, '%Y-%m-%dT%H:%M:%S')
                # パスワード有効期限
                expiration = web.signin_file_data['password']['expiration']
                if expiration['enabled']:
                    period = expiration['period']
                    notify = expiration['notify']
                    # パスワード有効期限チェック
                    if datetime.datetime.now() > last_update + datetime.timedelta(days=period):
                        return RedirectResponse(url=f'/signin/{next}?error=expirationofpassword')
                    if datetime.datetime.now() > last_update + datetime.timedelta(days=notify):
                        # セッションに保存
                        req.session['signin'] = dict(uid=uid, name=name, password=passwd, gids=gids,
                                                     groups=group_names, email=email)
                        return RedirectResponse(url=f'../{next}?warn=passchange') # nginxのリバプロ対応のための相対パス
            # セッションに保存
            req.session['signin'] = dict(uid=uid, name=name, password=passwd, gids=gids,
                                         groups=group_names, email=email)
            return RedirectResponse(url=f'../{next}') # nginxのリバプロ対応のための相対パス

        def _load_signin(signin_module:str, appcls, ver):
            if signin_module is None:
                return None
            try:
                mod = importlib.import_module(signin_module)
                members = inspect.getmembers(mod, inspect.isclass)
                for name, cls in members:
                    if cls is not signin.Signin or not issubclass(cls, signin.Signin):
                        continue
                    sobj = cls(appcls, ver)
                    return sobj
                return None
            except Exception as e:
                web.logger.error(f'Failed to load signin. {e}', exc_info=True)
                raise e

        self.google_signin = signin.Signin(app, web.ver)
        self.github_signin = signin.Signin(app, web.ver)
        if web.signin_file_data is not None:
            # signinオブジェクトの指定があった場合読込む
            if 'signin_module' in web.signin_file_data['oauth2']['providers']['google']:
                sobj = _load_signin(web.signin_file_data['oauth2']['providers']['google']['signin_module'], self.appcls, self.ver)
                self.google_signin = sobj if sobj is not None else self.google_signin
            if 'signin_module' in web.signin_file_data['oauth2']['providers']['google']:
                sobj = _load_signin(web.signin_file_data['oauth2']['providers']['github']['signin_module'], self.appcls, self.ver)
                self.github_signin = sobj if sobj is not None else self.github_signin

        @app.get('/oauth2/google/callback')
        async def oauth2_google_callback(req:Request):
            conf = web.signin_file_data['oauth2']['providers']['google']
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
                # ユーザー情報取得(email)
                user_info_resp = requests.get(
                    url='https://www.googleapis.com/oauth2/v1/userinfo',
                    headers={'Authorization': f'Bearer {access_token}'}
                )
                user_info_resp.raise_for_status()
                user_info_json = user_info_resp.json()
                email = user_info_json['email']
                # サインイン判定
                copy_signin_data = copy.deepcopy(web.signin_file_data)
                jadge, user = self.google_signin.jadge(access_token, email, copy_signin_data)
                if not jadge:
                    return RedirectResponse(url=f'/signin/{next}?error=appdeny')
                # グループ取得
                group_names, gids = self.google_signin.get_groups(access_token, user, copy_signin_data)
                # 最終サインイン日時更新
                web.user_data(req, user['uid'], user['name'], 'signin', 'last_update', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
                # パスワード最終更新日時削除
                web.user_data(req, user['uid'], user['name'], 'password', 'last_update', delkey=True)
                # セッションに保存
                req.session['signin'] = dict(uid=user['uid'], name=user['name'], gids=gids,
                                            groups=group_names, email=email)
                return RedirectResponse(url=f'../../{next}') # nginxのリバプロ対応のための相対パス
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

        @app.get('/oauth2/github/callback')
        async def oauth2_github_callback(req:Request):
            conf = web.signin_file_data['oauth2']['providers']['github']
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
                copy_signin_data = copy.deepcopy(web.signin_file_data)
                jadge, user = self.github_signin.jadge(access_token, email, copy_signin_data)
                if not jadge:
                    return RedirectResponse(url=f'/signin/{next}?error=appdeny')
                # グループ取得
                group_names, gids = self.github_signin.get_groups(user, copy_signin_data)
                # 最終サインイン日時更新
                web.user_data(req, user['uid'], user['name'], 'signin', 'last_update', datetime.datetime.now().strftime('%Y-%m-%dT%H:%M:%S'))
                # パスワード最終更新日時削除
                web.user_data(req, user['uid'], user['name'], 'password', 'last_update', delkey=True)
                # セッションに保存
                req.session['signin'] = dict(uid=user['uid'], name=user['name'], gids=gids,
                                            groups=group_names, email=email)
                return RedirectResponse(url=f'../../{next}') # nginxのリバプロ対応のための相対パス
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}')
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')
