from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import argparse
import time


class Audit(feature.WebFeature):

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        if web.audit_html is not None:
            if not web.audit_html.is_file():
                raise FileNotFoundError(f'audit_html is not found. ({web.audit_html})')
            with open(web.audit_html, 'r', encoding='utf-8') as f:
                web.audit_html_data = f.read()

        @app.get('/audit', response_class=HTMLResponse)
        @app.post('/audit', response_class=HTMLResponse)
        async def audit(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            res.headers['Access-Control-Allow-Origin'] = '*'
            web.options.audit_exec(req, res, web)
            return web.audit_html_data

        @app.post('/audit/rawlog')
        async def audit_rawlog(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            if web.signin.get_data() is None:
                return dict(error='signin_file_data is None.')
            if not hasattr(web.options, 'audit_search') or web.options.audit_search is None:
                return dict(warn='audit feature is disabled.')
            opt = await req.json()
            opt = {**opt, **web.options.audit_search_args.copy()}
            opt['host'] = web.redis_host
            opt['port'] = web.redis_port
            opt['password'] = web.redis_password
            opt['svname'] = web.svname
            args = argparse.Namespace(**{k:common.chopdq(v) for k,v in opt.items()})
            status, ret_main, _ = web.options.audit_search.apprun(web.logger, args, time.perf_counter(), [])
            if status != 0:
                return dict(error=ret_main)
            return ret_main

        @app.get('/audit/mode_cmd')
        async def audit_mode_cmd(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            if not hasattr(web.options, 'audit_search_args'):
                return dict(warn='audit feature is disabled.')
            return dict(success=web.options.audit_search_args)

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
        return dict(audit=dict(html='Audit', href='audit', target='_blank', css_class='dropdown-item'))
