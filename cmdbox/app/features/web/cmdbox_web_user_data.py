from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import Dict, Any


class UserData(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/user_data/load')
        async def load(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            if 'signin' not in req.session or req.session['signin'] is None:
                return dict(warn='Please sign in.')
            form = await req.form()
            categoly = form.get('categoly')
            key = form.get('key')
            sess = req.session['signin']
            ret = web.user_data(req, sess['uid'], sess['name'], categoly, key)
            return dict(success=ret)

        @app.post('/gui/user_data/save')
        async def save(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            if 'signin' not in req.session or req.session['signin'] is None:
                return dict(warn='Please sign in.')
            form = await req.form()
            categoly = form.get('categoly')
            key = form.get('key')
            val = form.get('val')
            sess = req.session['signin']
            web.user_data(req, sess['uid'], sess['name'], categoly, key, val)
            return dict(success=f'user_data "{categoly}:{key}:val" saved.')

        @app.post('/gui/user_data/delete')
        async def delete(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            if 'signin' not in req.session or req.session['signin'] is None:
                return dict(warn='Please sign in.')
            form = await req.form()
            categoly = form.get('categoly')
            key = form.get('key')
            val = form.get('val')
            sess = req.session['signin']
            web.user_data(req, sess['uid'], sess['name'], categoly, key, delkey=True)
            return dict(success=f'user_data "{categoly}:{key}:val" deleted.')
