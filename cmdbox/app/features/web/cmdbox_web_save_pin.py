from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import Dict, Any


class SavePin(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/save_cmd_pin')
        async def save_cmd_pin(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            if 'signin' not in req.session or req.session['signin'] is None:
                return dict(warn='Please sign in.')
            form = await req.form()
            title = form.get('title')
            pin = form.get('pin')
            sess = req.session['signin']
            web.user_data(req, sess['uid'], sess['name'], 'cmdpins', title, pin)
            return dict(success=f'Command pin "{title}:{pin}" saved.')

        @app.post('/gui/save_pipe_pin')
        async def save_pipe_pin(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            if 'signin' not in req.session or req.session['signin'] is None:
                return dict(warn='Please sign in.')
            form = await req.form()
            title = form.get('title')
            pin = form.get('pin')
            sess = req.session['signin']
            web.user_data(req, sess['uid'], sess['name'], 'pipepins', title, pin)
            return dict(success=f'Pipe pin "{title}:{pin}" saved.')
