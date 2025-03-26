import urllib.parse
from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
import urllib


class Signin(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        web.signin.signin_file_data = web.signin.load_signin_file(web.signin_file, web.signin.get_data())
        if web.signin_html is not None:
            if not web.signin_html.is_file():
                raise HTTPException(status_code=500, detail=f'signin_html is not found. ({web.signin_html})')
            with open(web.signin_html, 'r', encoding='utf-8') as f:
                web.signin_html_data = f.read()

        @app.get('/signin/{next}', response_class=HTMLResponse)
        @app.post('/signin/{next}', response_class=HTMLResponse)
        async def _signin(next:str, req:Request, res:Response):
            web.signin.enable_cors(req, res)
            res.headers['Access-Control-Allow-Origin'] = '*'
            return web.signin_html_data

        # https://developers.google.com/identity/protocols/oauth2/web-server?hl=ja#httprest
        @app.get('/oauth2/google/{next}')
        async def oauth2_google(next:str, req:Request, res:Response):
            if web.signin_html_data is None:
                return RedirectResponse(url=f'../../{next}') # nginxのリバプロ対応のための相対パス
            conf = web.signin.get_data()['oauth2']['providers']['google']
            data = {'scope': ' '.join(conf['scope']),
                    'access_type': 'offline',
                    'response_type': 'code',
                    'redirect_uri': conf['redirect_uri'],
                    'client_id': conf['client_id'],
                    'state': next}
            query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
            return RedirectResponse(url=f'https://accounts.google.com/o/oauth2/auth?{query}')

        # https://docs.github.com/ja/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps#scopes
        @app.get('/oauth2/github/{next}')
        async def oauth2_github(next:str, req:Request, res:Response):
            if web.signin_html_data is None:
                return RedirectResponse(url=f'../../{next}') # nginxのリバプロ対応のための相対パス
            conf = web.signin.get_data()['oauth2']['providers']['github']
            data = {'scope': ' '.join(conf['scope']),
                    'access_type': 'offline',
                    'response_type': 'code',
                    'redirect_uri': conf['redirect_uri'],
                    'client_id': conf['client_id'],
                    'state': next}
            query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
            return RedirectResponse(url=f'https://github.com/login/oauth/authorize?{query}')

        # https://learn.microsoft.com/ja-jp/entra/identity-platform/v2-oauth2-auth-code-flow
        @app.get('/oauth2/azure/{next}')
        async def oauth2_azure(next:str, req:Request, res:Response):
            if web.signin_html_data is None:
                return RedirectResponse(url=f'../../{next}') # nginxのリバプロ対応のための相対パス
            conf = web.signin.get_data()['oauth2']['providers']['azure']
            data = {'scope': ' '.join(conf['scope']),
                    'access_type': 'offline',
                    'response_type': 'code',
                    'redirect_uri': conf['redirect_uri'],
                    'client_id': conf['client_id'],
                    'response_mode': 'query',
                    'state': next}
            query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
            return RedirectResponse(url=f'https://login.microsoftonline.com/{conf["tenant_id"]}/oauth2/v2.0/authorize?{query}')

        @app.get('/oauth2/enabled')
        async def oauth2_enabled(req:Request, res:Response):
            if web.signin_html_data is None:
                return dict(google=False, github=False, azure=False)
            signin_data = web.signin.get_data()
            return dict(google=signin_data['oauth2']['providers']['google']['enabled'],
                        github=signin_data['oauth2']['providers']['github']['enabled'],
                        azure=signin_data['oauth2']['providers']['azure']['enabled'],)
