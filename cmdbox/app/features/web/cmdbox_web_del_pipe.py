from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException


class DelPipe(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/del_pipe')
        async def del_pipe(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            title = form.get('title')

            opt_path = web.pipes_path / f"pipe-{title}.json"
            web.logger.info(f"del_pipe: opt_path={opt_path}")
            opt_path.unlink()
            if 'signin' in req.session and req.session['signin'] is not None:
                sess = req.session['signin']
                web.user_data(req, sess['uid'], sess['name'], 'pipepins', title, delkey=True)
            web.options.audit_exec(req, res)
            return {}

