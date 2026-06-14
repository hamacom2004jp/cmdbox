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
        @app.post('/gui/user_data/load', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def load(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            if 'signin' not in req.session or req.session['signin'] is None:
                return dict(warn='Please sign in.')
            form = await req.form()
            categoly = form.get('categoly')
            key = form.get('key')
            if not categoly or not key:
                return dict(warn='Category and key are required.')
            sess = req.session['signin']

            im = req.headers.get('If-None-Match')
            hs = str(web.user_data_hash(sess['uid'], sess['name']))
            headers = {'Cache-Control':'private, no-cache', 'ETag': hs}
            if im == hs:
                return Response(status_code=304, headers=headers)
            ret = web.user_data(req, sess['uid'], sess['name'], categoly, key)
            res.headers.update(headers)
            return dict(success=ret)

        @app.post('/gui/user_data/save', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
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
            if not categoly or not key:
                return dict(warn='Category and key are required.')
            sess = req.session['signin']
            web.user_data(req, sess['uid'], sess['name'], categoly, key, val)
            return dict(success=f'user_data "{categoly}:{key}:val" saved.')

        @app.post('/gui/user_data/delete', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
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
            if not categoly or not key:
                return dict(warn='Category and key are required.')
            sess = req.session['signin']
            web.user_data(req, sess['uid'], sess['name'], categoly, key, delkey=True)
            return dict(success=f'user_data "{categoly}:{key}:val" deleted.')
