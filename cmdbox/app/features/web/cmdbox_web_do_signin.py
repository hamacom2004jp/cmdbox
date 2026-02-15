import urllib.parse
from cmdbox.app import common
from cmdbox.app.auth import signin, signin_saml, azure_signin, azure_signin_saml, github_signin, google_signin
from cmdbox.app.commons import convert
from cmdbox.app.features.web import cmdbox_web_signin
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from typing import Any, Dict
import copy
import datetime
import importlib
import inspect
import json
import logging
import urllib


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
            signin_data = web.signin.signin_file_data
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
                    web.options.audit_exec(req, res, web, body=dict(msg='signin failed.'), audit_type='auth')
                    return RedirectResponse(url=f'/signin/{next}?error=1')
                user = [u for u in signin_data['users'] if u['name'] == name and u['hash'] != 'oauth2' and u['hash'] != 'saml']
                if len(user) <= 0:
                    web.options.audit_exec(req, res, web, body=dict(msg='signin failed.'), audit_type='auth')
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
                    web.options.audit_exec(req, res, web, body=dict(msg='Accound lockout.'), audit_type='auth', user=name)
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
                    web.options.audit_exec(req, res, web, body=dict(msg='Wrong password.'), audit_type='auth', user=name)
                    return RedirectResponse(url=f'/signin/{next}?error=1')
            group_names = list(set(web.signin.__class__.correct_group(signin_data, user['groups'], None)))
            group_homes = list(set(web.signin.__class__.group_home(signin_data, group_names)))
            gids = [g['gid'] for g in signin_data['groups'] if g['name'] in group_names]
            email = user.get('email', '')
            # パスワード最終更新日時取得
            last_update = web.user_data(None, uid, name, 'password', 'last_update')
            notify_passchange = True if last_update is None else False
            # パスワード認証の場合はパスワード有効期限チェック
            if user['hash']!='oauth2' and user['hash']!='saml' and 'password' in signin_data and not notify_passchange:
                last_update = datetime.datetime.strptime(last_update, '%Y-%m-%dT%H:%M:%S')
                # パスワード有効期限
                expiration = signin_data['password']['expiration']
                if expiration['enabled']:
                    period = expiration['period']
                    notify = expiration['notify']
                    # パスワード有効期限チェック
                    if datetime.datetime.now() > last_update + datetime.timedelta(days=period):
                        web.options.audit_exec(req, res, web, body=dict(msg='Password is expired.'), audit_type='auth', user=name)
                        return RedirectResponse(url=f'/signin/{next}?error=expirationofpassword')
                    if datetime.datetime.now() > last_update + datetime.timedelta(days=notify):
                        # セッションに保存
                        _set_session(req, dict(uid=uid, name=name, apikeys=user.get('apikeys', None), home=user.get('home', None)),
                                     email, passwd, None, group_names, group_homes, gids)
                        next = f"../{next}" if token_ok else next
                        web.options.audit_exec(req, res, web, body=dict(msg='Signin succeeded. However, you should change your password.'), audit_type='auth', user=name)
                        return RedirectResponse(url=f'../{next}?warn=passchange', headers=dict(signin="success"))
            # セッションに保存
            _set_session(req, dict(uid=uid, name=name, apikeys=user.get('apikeys', None), home=user.get('home', None)),
                         email, passwd, None, group_names, group_homes, gids)
            next = f"../{next}" if token_ok else next
            if notify_passchange:
                web.options.audit_exec(req, res, web, body=dict(msg='Signin succeeded. However, you should change your password.'), audit_type='auth', user=name)
                return RedirectResponse(url=f'../{next}?warn=passchange', headers=dict(signin="success"))
            web.options.audit_exec(req, res, web, body=dict(msg='Signin succeeded.'), audit_type='auth', user=name)
            return RedirectResponse(url=f'../{next}', headers=dict(signin="success"))

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
                signin_data = web.signin.signin_file_data
                for name, cls in members:
                    if cls is signin.Signin or issubclass(cls, signin.Signin):
                        sobj = cls(web.logger, web.signin_file, signin_data, web.redis_cli, appcls, ver)
                        return sobj
                return None
            except Exception as e:
                web.logger.error(f'Failed to load signin. {e}', exc_info=True)
                raise e

        signin_data = web.signin.signin_file_data
        self.google_signin = google_signin.GoogleSignin(web.logger, web.signin_file, signin_data, web.redis_cli, self.appcls, self.ver)
        self.github_signin = github_signin.GithubSignin(web.logger, web.signin_file, signin_data, web.redis_cli, self.appcls, self.ver)
        self.azure_signin = azure_signin.AzureSignin(web.logger, web.signin_file, signin_data, web.redis_cli, self.appcls, self.ver)
        self.azure_saml_signin = azure_signin_saml.AzyreSigninSAML(web.logger, web.signin_file, signin_data, web.redis_cli, self.appcls, self.ver)
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
            if 'signin_module' in signin_data['saml']['providers']['azure']:
                sobj = _load_signin(web, signin_data['saml']['providers']['azure']['signin_module'], self.appcls, self.ver)
                self.azure_saml_signin = sobj if sobj is not None else self.azure_saml_signin

        def _set_session(req:Request, user:dict, email:str, hashed_password:str, access_token:str, group_names:list, group_homes:list, gids:list):
            """
            セッションに保存する

            Args:
                req (Request): Requestオブジェクト
                user (dict): ユーザー情報
                email (str): メールアドレス
                hashed_password (str): パスワード
                access_token (str): アクセストークン
                group_names (list): グループ名リスト
                group_homes (list): グループホームリスト
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
            req.session['signin'] = dict(uid=user['uid'], name=user['name'], home=user['home'],
                                         password=hashed_password, access_token=access_token, apikeys=user.get('apikeys', None),
                                         gids=gids, groups=group_names, group_homes=group_homes, email=email)
            # ユーザーフォルダチェック
            user_dir = web.data / user['home']
            if not user_dir.exists():
                user_dir.mkdir(parents=True, exist_ok=True)
            # グループフォルダチェック
            for group_home in group_homes:
                group_dir = web.data / group_home
                if not group_dir.exists():
                    group_dir.mkdir(parents=True, exist_ok=True)
            if web.logger.level == logging.DEBUG:
                web.logger.debug(f'Set session, uid={user["uid"]}, name={user["name"]}, home={user["home"]}, email={email}, gids={gids}, groups={group_names}, group_homes={group_homes}')

        @app.get('/oauth2/google/callback')
        async def oauth2_google_callback(req:Request, res:Response):
            conf = web.signin.signin_file_data['oauth2']['providers']['google']
            next = req.query_params['state']
            try:
                # アクセストークン取得
                access_token = self.google_signin.request_access_token(conf, req, res)
                return await oauth2_google_session(access_token, next, req, res)
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

        @app.get('/oauth2/google/session/{access_token}/{next}')
        async def oauth2_google_session(access_token:str, next:str, req:Request, res:Response):
            return await oauth2_login_session(self.google_signin, access_token, next, req, res)

        @app.get('/oauth2/github/callback')
        async def oauth2_github_callback(req:Request, res:Response):
            conf = web.signin.signin_file_data['oauth2']['providers']['github']
            next = req.query_params['state']
            try:
                # アクセストークン取得
                access_token = self.github_signin.request_access_token(conf, req, res)
                return await oauth2_github_session(access_token, next, req, res)
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

        @app.get('/oauth2/github/session/{access_token}/{next}')
        async def oauth2_github_session(access_token:str, next:str, req:Request, res:Response):
            return await oauth2_login_session(self.github_signin, access_token, next, req, res)

        @app.get('/oauth2/azure/callback')
        async def oauth2_azure_callback(req:Request, res:Response):
            conf = web.signin.signin_file_data['oauth2']['providers']['azure']
            next = req.query_params['state']
            try:
                # アクセストークン取得
                access_token = self.azure_signin.request_access_token(conf, req, res)
                return await oauth2_azure_session(access_token, next, req, res)
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

        @app.get('/oauth2/azure/session/{access_token}/{next}')
        async def oauth2_azure_session(access_token:str, next:str, req:Request, res:Response):
            return await oauth2_login_session(self.azure_signin, access_token, next, req, res)

        async def oauth2_login_session(signin:signin.Signin, access_token:str, next:str, req:Request, res:Response):
            try:
                # ユーザー情報取得(email)
                email = signin.get_email(access_token)
                # サインイン判定
                jadge, user = signin.jadge(email)
                if not jadge:
                    return RedirectResponse(url=f'/signin/{next}?error=appdeny')
                # グループ取得
                group_names, gids = signin.get_groups(access_token, user)
                group_homes = list(set(web.signin.__class__.group_home(signin_data, group_names)))
                # セッションに保存
                _set_session(req, user, email, None, access_token, group_names, group_homes, gids)
                return RedirectResponse(url=f'../../{next}', headers=dict(signin="success")) # nginxのリバプロ対応のための相対パス
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}', exc_info=True)
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

        @app.post('/saml/azure/callback')
        async def saml_azure_callback(req:Request, res:Response):
            form = await req.form()
            return await saml_login_callback('azure', self.azure_saml_signin, form, None, req, res)

        @app.get('/saml/azure/session/{saml_token}/{next}')
        async def saml_azure_session(saml_token:str, next:str, req:Request, res:Response):
            form = json.loads(convert.b64str2str(saml_token))
            return await saml_login_callback('azure', self.azure_saml_signin, form, next, req, res)

        async def saml_login_callback(prov, saml_signin:signin_saml.SigninSAML, form:Dict[str, Any], next:str, req:Request, res:Response):
            """
            SAML認証のコールバック処理を行います
            Args:
                prov (str): SAMLプロバイダ名
                saml_signin (signin_saml.SigninSAML): SAMLサインインオブジェクト
                form (Dict[str, Any]): フォームデータ
                req (Request): Requestオブジェクト
                res (Response): Responseオブジェクト
            """
            relay = form.get('RelayState')
            query = urllib.parse.urlparse(relay).query if relay is not None else None
            if next is None:
                next = urllib.parse.parse_qs(query).get('next', None) if query is not None else None
                next = next[0] if next is not None and len(next) > 0 else None
            auth = await saml_signin.make_saml(prov, next, form, req, res)
            auth.process_response() # Process IdP response
            errors = auth.get_errors() # This method receives an array with the errors
            if len(errors) == 0:
                if not auth.is_authenticated(): # This check if the response was ok and the user data retrieved or not (user authenticated)
                    return RedirectResponse(url=f'/signin/{next}?error=saml_not_auth')
                else:
                    # ユーザー情報取得
                    email = saml_signin.get_email(auth)
                    # サインイン判定
                    jadge, user = saml_signin.jadge(email)
                    if not jadge:
                        return RedirectResponse(url=f'/signin/{next}?error=appdeny')
                    # グループ取得
                    group_names, gids = saml_signin.get_groups(None, user)
                    group_homes = list(set(web.signin.__class__.group_home(signin_data, group_names)))
                    # セッションに保存
                    _set_session(req, user, email, None, None, group_names, group_homes, gids)
                    # SAML場合、ブラウザ制限によりリダイレクトでセッションクッキーが消えるので、HTMLで移動する
                    html = """
                    <html><head><meta http-equiv="refresh" content="0;url=../../{next}"></head>
                    <body style="background-color:#212529;color:#fff;">loading..</body>
                    <script type="text/javascript">window.location.href="../../{next}";</script></html>
                    """.format(next=next)
                    return HTMLResponse(content=html, headers=dict(signin="success"))
            else:
                msg = f"Error when processing SAML Response: {', '.join(errors)} {auth.get_last_error_reason()}"
                web.logger.warning(msg)
                raise HTTPException(status_code=500, detail=msg)
