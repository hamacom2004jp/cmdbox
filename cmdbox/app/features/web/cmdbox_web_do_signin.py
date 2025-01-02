from cmdbox.app.features.web import cmdbox_web_signin
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
import hashlib


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
            user = [u for u in web.signin_file_data['users'] if u['name'] == name]
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
            req.session['signin'] = dict(uid=user[0]['uid'], name=name, password=passwd, gids=gids, groups=group_names)
            return RedirectResponse(url=f'../{next}') # nginxのリバプロ対応のための相対パス

