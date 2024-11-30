from cmdbox import version
from cmdbox.app.features.web import cmdbox_web_signin
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
import hashlib


class DoSignin(cmdbox_web_signin.Signin):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

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
            userid = form.get('userid')
            passwd = form.get('password')
            if userid == '' or passwd == '':
                return RedirectResponse(url=f'/signin/{next}?error=1')
            self.load_signin_file(web)
            if userid not in web.signin_file_data:
                return RedirectResponse(url=f'/signin/{next}?error=1')
            algname = web.signin_file_data[userid]['algname']
            if algname != 'plain':
                h = hashlib.new(algname)
                h.update(passwd.encode('utf-8'))
                passwd = h.hexdigest()
            if passwd != web.signin_file_data[userid]['password']:
                return RedirectResponse(url=f'/signin/{next}?error=1')

            req.session['signin'] = dict(userid=userid, password=passwd)
            return RedirectResponse(url=f'/{next}')
