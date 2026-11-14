from cmdbox.app import common, feature
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
        @app.post('/gui/del_cmd', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def del_cmd(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
        
            form = await req.form()
            title = form.get('title')
            if not title:
                return dict(warn='Title is required.')

            opt_path = web.cmds_path / f"cmd-{title}.json"
            web.logger.info(f"del_cmd: opt_path={opt_path}")

            opt = common.loadopt(opt_path, False)
            if 'allow_groups' in opt and opt['allow_groups']:
                signin_groups = []
                if req.session is not None and 'signin' in req.session and req.session['signin'] is not None:
                    if 'groups' in req.session['signin'] and req.session['signin']['groups'] is not None:
                        signin_groups = req.session['signin']['groups']
                allow_groups = opt['allow_groups']
                if isinstance(allow_groups, str):
                    allow_groups = [allow_groups]
                allow_groups = [group for group in allow_groups if group and group.strip()]
                if allow_groups and not any(group in signin_groups for group in allow_groups):
                    return dict(warn=f'You do not have permission to delete this command. (your groups: {signin_groups})')

            opt_path.unlink()
            if 'signin' in req.session and req.session['signin'] is not None:
                sess = req.session['signin']
                web.user_data(req, sess['uid'], sess['name'], 'cmdpins', title, delkey=True)
            web.options.audit_exec(req, res, web)
            return {}