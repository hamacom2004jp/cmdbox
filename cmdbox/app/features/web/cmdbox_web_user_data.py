from cmdbox.app import feature
from cmdbox.app.commons import convert
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

        @app.get('/gui/user_data/icon', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def user_icon(req:Request, res:Response):
            svg = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 640" fill="gray"><path d="M463 448.2C440.9 409.8 399.4 384 352 384L288 384C240.6 384 199.1 409.8 177 448.2C212.2 487.4 263.2 512 320 512C376.8 512 427.8 487.3 463 448.2zM64 320C64 178.6 178.6 64 320 64C461.4 64 576 178.6 576 320C576 461.4 461.4 576 320 576C178.6 576 64 461.4 64 320zM320 336C359.8 336 392 303.8 392 264C392 224.2 359.8 192 320 192C280.2 192 248 224.2 248 264C248 303.8 280.2 336 320 336z"/></svg>'
            svg_b64 = convert.bytes2b64str(svg.encode('utf-8'))
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return Response(status_code=200, content=svg, media_type='image/svg+xml')
            if 'signin' not in req.session or req.session['signin'] is None:
                return Response(status_code=200, content=svg, media_type='image/svg+xml')
            sess = req.session['signin']
            im = req.headers.get('If-None-Match')
            hs = str(web.user_data_hash(sess['uid'], sess['name']))
            headers = {'Cache-Control':'private, no-cache', 'ETag': hs}
            if im == hs:
                return Response(status_code=200, content=svg, media_type='image/svg+xml')
            ret_b64:str = web.user_data(req, sess['uid'], sess['name'], 'profile', 'icon')
            mimetype = ret_b64[5:ret_b64.index(';base64,')] if ret_b64 and len(ret_b64)>5 else 'image/svg+xml'
            ret_b64 = ret_b64[ret_b64.index(';base64,')+8:] if ret_b64 and len(ret_b64)>8 else svg_b64
            res.headers.update(headers)
            return Response(status_code=200, content=convert.b64str2bytes(ret_b64), media_type=mimetype)
