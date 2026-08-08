from cmdbox.app import common, feature
from cmdbox.app.features.web import cmdbox_web_exec_cmd
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import RedirectResponse


class LoadUrl(cmdbox_web_exec_cmd.ExecCmd):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/ru/{url_id}', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        @app.post('/ru/{url_id}', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def load_cmd(req:Request, res:Response, url_id:str):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            opt = dict(mode='url', cmd='load', url_id=url_id)
            ret = await self.exec_cmd(req, res, web, None, opt, True, self.appcls)
            if 'success' not in ret or 'data' not in ret['success'] or 'target_url' not in ret['success']['data']:
                return common.to_str(ret)
            target_url = ret['success']['data']['target_url']
            web.options.audit_exec(req, res, web, body=opt)
            return RedirectResponse(url=target_url, status_code=302)
