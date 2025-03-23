from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from pathlib import Path
import cmdbox


class VersionsUsed(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
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
            with open(Path(cmdbox.__file__).parent / 'web' / 'assets_license_list.txt', 'r', encoding='utf-8') as f:
                for i, line in enumerate(f.readlines()):
                    parts = line.strip().split('\t')
                    ret.append(parts)
            return ret
