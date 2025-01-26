from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse
from typing import Dict, Any
import logging


class Users(feature.WebFeature):

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        if web.users_html is not None:
            if not web.users_html.is_file():
                raise FileNotFoundError(f'users_html is not found. ({web.users_html})')
            with open(web.users_html, 'r', encoding='utf-8') as f:
                web.users_html_data = f.read()

        @app.get('/users', response_class=HTMLResponse)
        @app.post('/users', response_class=HTMLResponse)
        async def users(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            res.headers['Access-Control-Allow-Origin'] = '*'
            return web.users_html_data

        @app.get('/users/list')
        async def users_list(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            return web.user_list(None)

        @app.post('/users/add')
        async def users_add(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            form = await req.json()
            try:
                web.user_add(form)
                return dict(success='add user')
            except Exception as e:
                return dict(error=str(e))

        @app.post('/users/edit')
        async def users_edit(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            form = await req.json()
            try:
                web.user_edit(form)
                return dict(success='edit user')
            except Exception as e:
                return dict(error=str(e))

        @app.post('/users/del')
        async def users_del(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            form = await req.json()
            try:
                if req.session['signin']['uid'] == form.get('uid', None):
                    raise ValueError('You cannot delete yourself.')
                web.user_del(form.get('uid', None))
                return dict(success='delete user')
            except Exception as e:
                return dict(error=str(e))

        @app.post('/users/apikey/add')
        async def users_apikey_add(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            form = await req.json()
            try:
                apikey = web.apikey_add(form)
                return dict(success=apikey)
            except Exception as e:
                return dict(error=str(e))

        @app.post('/users/apikey/del')
        async def users_apikey_del(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            form = await req.json()
            try:
                apikey = web.apikey_del(form)
                return dict(success=apikey)
            except Exception as e:
                return dict(error=str(e))

        @app.get('/groups/list')
        async def groups_list(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            try:
                return web.group_list(None)
            except Exception as e:
                return dict(error=str(e))

        @app.post('/groups/add')
        async def groups_add(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            form = await req.json()
            try:
                web.group_add(form)
                return dict(success='add group')
            except Exception as e:
                return dict(error=str(e))

        @app.post('/groups/edit')
        async def groups_edit(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            form = await req.json()
            try:
                web.group_edit(form)
                return dict(success='edit group')
            except Exception as e:
                return dict(error=str(e))

        @app.post('/groups/del')
        async def groups_del(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            form = await req.json()
            try:
                if form.get('gid', None) in req.session['signin']['gids']:
                    raise ValueError('You cannot delete yourself group.')
                web.group_del(form.get('gid', None))
                return dict(success='delete group')
            except Exception as e:
                return dict(error=str(e))

        @app.get('/cmdrules/list')
        async def cmdrules_list(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            try:
                return web.signin_file_data['cmdrule']
            except Exception as e:
                return dict(error=str(e))

        @app.get('/pathrules/list')
        async def pathrules_list(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            try:
                return web.signin_file_data['pathrule']
            except Exception as e:
                return dict(error=str(e))

        @app.get('/passsetting/list')
        async def passsetting_list(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            try:
                return web.signin_file_data['password']
            except Exception as e:
                return dict(error=str(e))

        @app.post('/password/change')
        async def password_change(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin_file_data is None:
                return dict(error='signin_file_data is None.')
            form = await req.json()
            try:
                ret = web.change_password(form.get('user_name', None), form.get('password', None),
                                    form.get('new_password', None), form.get('confirm_password', None))
                return ret
            except Exception as e:
                return dict(error=str(e))

    def toolmenu(self, web:Web) -> Dict[str, Any]:
        """
        ツールメニューの情報を返します

        Args:
            web (Web): Webオブジェクト
        
        Returns:
            Dict[str, Any]: ツールメニュー情報
        
        Sample:
            {
                'filer': {
                    'html': 'Filer',
                    'href': 'filer',
                    'target': '_blank',
                    'css_class': 'dropdown-item'
                    'onclick': 'alert("filer")'
                }
            }
        """
        return dict(users=dict(html='Users', href='users', target='_blank', css_class='dropdown-item'))
