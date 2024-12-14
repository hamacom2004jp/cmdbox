from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException


class DelCmd(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/del_cmd')
        async def del_cmd(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            title = form.get('title')

            opt_path = web.cmds_path / f"cmd-{title}.json"
            web.logger.info(f"del_cmd: opt_path={opt_path}")
            opt_path.unlink()
            return {}
