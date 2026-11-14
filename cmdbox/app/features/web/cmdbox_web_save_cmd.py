from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import Dict, Any
import json


class SaveCmd(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/save_cmd', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def save_cmd(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            title = form.get('title')
            opt = form.get('opt')
            if not title or not opt:
                return dict(warn='Title and opt are required.')
            ret = self.save_cmd(web, req, title, json.loads(opt))
            web.options.audit_exec(req, res, web, body=form)
            return ret

    def save_cmd(self, web:Web, req:Request, title:str, opt:Dict[str, Any]) -> Dict[str, str]:
        """
        コマンドファイルを保存する

        Args:
            web (Web): Webオブジェクト
            req (Request): リクエスト
            title (str): タイトル
            opt (dict): オプション
        
        Returns:
            dict: 結果
        """
        if common.check_fname(title):
            return dict(warn=f'The title contains invalid characters."{title}"')
        opt_path = web.cmds_path / f"cmd-{title}.json"
        web.logger.info(f"save_cmd: opt_path={opt_path}, opt={opt}")
        modal_mode = opt.get('modal_mode', False)
        if modal_mode == 'add' and opt_path.exists():
            return dict(warn=f'Command "{title}" already exists')

        signin_groups = []
        if req.session is not None and 'signin' in req.session and req.session['signin'] is not None:
            if 'groups' in req.session['signin'] and req.session['signin']['groups'] is not None:
                signin_groups = req.session['signin']['groups']

        allow_groups = opt['allow_groups']
        if isinstance(allow_groups, str):
            allow_groups = [allow_groups]
        allow_groups = [group for group in allow_groups if group and group.strip()]
        if allow_groups and not any(group in signin_groups for group in allow_groups):
            return dict(warn=f'Your own group has not been set up. (your groups: {signin_groups})')

        if modal_mode == 'edit' and opt_path.exists():
            org_opt = common.loadopt(opt_path, False)
            if 'allow_groups' in org_opt and org_opt['allow_groups']:
                org_allow_groups = org_opt['allow_groups']
                if isinstance(org_allow_groups, str):
                    org_allow_groups = [org_allow_groups]
                org_allow_groups = [group for group in org_allow_groups if group and group.strip()]
                if org_allow_groups and not any(group in signin_groups for group in org_allow_groups):
                    return dict(warn=f'You do not have permission to save this command. (your groups: {signin_groups})')

        if 'title_disabled' in opt: del opt['title_disabled']
        if 'mode_disabled' in opt: del opt['mode_disabled']
        if 'cmd_disabled' in opt: del opt['cmd_disabled']
        if 'name_disabled' in opt: del opt['name_disabled']
        if 'modal_mode' in opt: del opt['modal_mode']
        if 'help' in opt: del opt['help']
        common.saveopt(opt, opt_path, True)
        return dict(success=f'Command "{title}" saved.')
