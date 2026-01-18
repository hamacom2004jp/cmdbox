from cmdbox import version
from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from pathlib import Path
import cmdbox


class VersionsCmdbox(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/versions')
        async def versions(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            ret = dict()
            if hasattr(self.ver, '__version__'): ret['version'] = self.ver.__version__
            if hasattr(self.ver, '__appid__'): ret['appid'] = self.ver.__appid__
            if hasattr(self.ver, '__title__'): ret['title'] = self.ver.__title__
            if hasattr(self.ver, '__copyright__'): ret['copyright'] = self.ver.__copyright__
            if hasattr(self.ver, '__logo__'): ret['logo'] = self.ver.__logo__
            if hasattr(self.ver, '__description__'): ret['description'] = self.ver.__description__.split('\n')
            if hasattr(self.ver, '__pypiurl__'): ret['pyurl'] = self.ver.__pypiurl__
            if hasattr(self.ver, '__srcurl__'): ret['srcurl'] = self.ver.__srcurl__
            if hasattr(self.ver, '__docurl__'): ret['docurl'] = self.ver.__docurl__
            return ret

        @app.get('/versions_cmdbox')
        async def versions_cmdbox(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            logo = [version.__logo__]
            return logo + version.__description__.split('\n')

        @app.get('/versions_used')
        async def versions_used(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            ret = []
            with open(Path(cmdbox.__file__).parent / 'licenses' / 'files.txt', 'r', encoding='utf-8') as f:
                for i, line in enumerate(f.readlines()):
                    parts = line.strip().split('\t')
                    ret.append(parts)
            with open(Path(cmdbox.__file__).parent / 'web' / 'voicevox_license_list.txt', 'r', encoding='utf-8') as f:
                for i, line in enumerate(f.readlines()):
                    parts = line.strip().split('\t')
                    ret.append(parts)
            with open(Path(cmdbox.__file__).parent / 'web' / 'assets_license_list.txt', 'r', encoding='utf-8') as f:
                for i, line in enumerate(f.readlines()):
                    parts = line.strip().split('\t')
                    ret.append(parts)
            return ret
