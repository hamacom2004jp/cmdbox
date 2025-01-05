from cmdbox.app.features.web import cmdbox_web_signin
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import hashlib
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
                h = hashlib.new(hash)
                h.update(passwd.encode('utf-8'))
                passwd = h.hexdigest()
            if passwd != user[0]['password']:
                return RedirectResponse(url=f'/signin/{next}?error=1')
            group_names = list(set(web.correct_group(user[0]['groups'])))
            gids = [g['gid'] for g in web.signin_file_data['groups'] if g['name'] in group_names]
            email = user[0].get('email', '')
            req.session['signin'] = dict(uid=user[0]['uid'], name=name, password=passwd, gids=gids,
                                         groups=group_names, email=email)
            return RedirectResponse(url=f'../{next}') # nginxのリバプロ対応のための相対パス

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
                # ユーザーリストと比較
                user = [u for u in web.signin_file_data['users'] if u['email'] == email and u['hash'] == 'oauth2']
                if len(user) <= 0:
                    return RedirectResponse(url=f'/signin/{next}?error=2')
                # セッションに保存
                group_names = list(set(web.correct_group(user[0]['groups'])))
                gids = [g['gid'] for g in web.signin_file_data['groups'] if g['name'] in group_names]
                req.session['signin'] = dict(uid=user[0]['uid'], name=user[0]['name'], gids=gids,
                                            groups=group_names, email=email)
                return RedirectResponse(url=f'../../{next}') # nginxのリバプロ対応のための相対パス
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}')
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
                # ユーザーリストと比較
                user = [u for u in web.signin_file_data['users'] if u['email'] == email and u['hash'] == 'oauth2']
                if len(user) <= 0:
                    return RedirectResponse(url=f'/signin/{next}?error=2')
                # セッションに保存
                group_names = list(set(web.correct_group(user[0]['groups'])))
                gids = [g['gid'] for g in web.signin_file_data['groups'] if g['name'] in group_names]
                req.session['signin'] = dict(uid=user[0]['uid'], name=user[0]['name'], gids=gids,
                                            groups=group_names, email=email)
                return RedirectResponse(url=f'../../{next}') # nginxのリバプロ対応のための相対パス
            except Exception as e:
                web.logger.warning(f'Failed to get token. {e}')
                raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')
