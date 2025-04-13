from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import Dict, Any
import json


class AuditMetrics(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/audit/metrics/save')
        async def save_metrics(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            title = form.get('title')
            opt = json.loads(form.get('opt'))
            if common.check_fname(title):
                return dict(warn=f'The title contains invalid characters."{title}"')
            opt_path = web.audit_path / f"metrics-{title}.json"
            web.logger.info(f"save_metrics: opt_path={opt_path}, opt={opt}")
            common.saveopt(opt, opt_path, True)
            ret = dict(success=f'Metrics "{title}" saved in "{opt_path}".')
            web.options.audit_exec(req, res, web, title=title)
            return ret

        @app.post('/audit/metrics/load')
        async def load_metrics(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            title = form.get('title')
            opt_path = web.audit_path / f"metrics-{title}.json"
            if not opt_path.is_file():
                return dict(warn=f'The metrics file is not found."{opt_path}"')
            with open(opt_path, 'r', encoding='utf-8') as f:
                opt = json.load(f)
            return dict(success=opt)

        @app.post('/audit/metrics/delete')
        async def delete_metrics(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            title = form.get('title')
            opt_path = web.audit_path / f"metrics-{title}.json"
            if not opt_path.is_file():
                return dict(warn=f'The metrics file is not found."{opt_path}"')
            opt_path.unlink()
            return dict(success=f'Metrics "{title}" deleted.')

        @app.post('/audit/metrics/list')
        async def list_metrics(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            files = web.audit_path.glob('metrics-*.json')
            ret = []
            for f in files:
                with open(f, 'r', encoding='utf-8') as f:
                    opt = json.load(f)
                    ret.append(opt)
            return dict(success=ret)
