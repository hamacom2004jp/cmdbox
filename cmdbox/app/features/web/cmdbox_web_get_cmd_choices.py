from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException


class GetCmdChoices(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/get_cmd_choices', responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def get_cmd_choices(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            try:
                opt:dict = await req.json()
            except Exception as e:
                raise HTTPException(status_code=400, detail=f'Invalid JSON: {e}')
            opt['mode'] = mode = opt.get('mode', None)
            opt['cmd'] = cmd = opt.get('cmd', None)
            opt['host'] = web.redis_host
            opt['port'] = web.redis_port
            opt['password'] = web.redis_password
            opt['svname'] = web.svname
            opt['retry_count'] = opt.get('retry_count', web.retry_count)
            opt['retry_interval'] = opt.get('retry_interval', web.retry_interval)
            opt['timeout'] = opt.get('timeout', web.timeout)
            opt['language'] = language = opt.get('language', web.language)
            if not opt.get('mode', None) or not opt.get('cmd', None):
                return dict(warn='Mode and cmd are required.')
            ret = web.options.get_cmd_choices(mode, cmd, True, opt).copy()
            fobj = web.options.get_cmd_feature(mode, cmd)
            desc = web.options.get_cmd_attr(mode, cmd, 'description_en' if not common.is_japan(language=language) else 'description_ja')
            desc_nouse_webmode = '\U00002B55 Web' if not web.options.get_cmd_attr(mode, cmd, 'nouse_webmode') else '\U0000274C Web'
            desc_use_agent = '\U00002B55 Agent' if web.options.get_cmd_attr(mode, cmd, 'use_agent') else '\U0000274C Agent'
            desc_edge = '\U00002B55 Edge' if not isinstance(fobj, feature.UnsupportEdgeFeature) else '\U0000274C Edge'
            help = dict(opt="help", type=web.options.T_TEXT, default=f"\U00002B55 CLI, {desc_nouse_webmode}, {desc_use_agent}, {desc_edge}, {desc}",
                        required=False, multi=False, hide=False, choice=None, description_ja="-", description_en="-")
            ret.insert(0, help)
            return ret
