from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import Dict, Any
import json


class LoadPin(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/load_cmd_pin')
        async def load_cmd_pin(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            if 'signin' not in req.session or req.session['signin'] is None:
                return dict(warn='Please sign in.')
            form = await req.form()
            title = form.get('title')
            sess = req.session['signin']
            data = web.user_data(req, sess['uid'], sess['name'], 'cmdpins', title)
            if data is None:
                return dict(success='off')
            return dict(success=data)

        @app.post('/gui/load_pipe_pin')
        async def load_pipe_pin(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            if 'signin' not in req.session or req.session['signin'] is None:
                return dict(warn='Please sign in.')
            form = await req.form()
            title = form.get('title')
            sess = req.session['signin']
            data = web.user_data(req, sess['uid'], sess['name'], 'pipepins', title)
            if data is None:
                return dict(success='off')
            return dict(success=data)
