from cmdbox import version
from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from pathlib import Path
import cmdbox


class VersionsUsed(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/versions_used')
        async def versions_used(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                return str(dict(warn=f'Please log in to retrieve session.'))

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
