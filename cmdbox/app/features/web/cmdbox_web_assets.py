from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
import glob
import io
import mimetypes
import logging


class Assets(feature.WebFeature):

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        ondemand_load = web.logger.level == logging.DEBUG
        def asset_func(asset_data, asset, path):
            if ondemand_load:
                @app.get(f'/signin/assets/{path}')
                @app.get(f'/assets/{path}')
                async def func(req:Request, res:Response):
                    if not asset.is_file():
                        raise HTTPException(status_code=404, detail=f'asset is not found. ({asset})')
                    mime, enc = mimetypes.guess_type(path)
                    im = req.headers.get('If-None-Match')
                    md5 = str(asset.stat().st_mtime_ns)
                    if im == md5:
                        return Response(status_code=304, headers={'Cache-Control':'no-cache', 'ETag': md5})
                    with open(asset, 'rb') as f:
                        asset_data = f.read()
                        return StreamingResponse(io.BytesIO(asset_data), media_type=mime,
                                                 headers={'Cache-Control':'no-cache', 'ETag': md5})
            else:
                md5 = str(asset.stat().st_mtime_ns)
                @app.get(f'/signin/assets/{path}')
                @app.get(f'/assets/{path}')
                async def func(req:Request, res:Response):
                    mime, enc = mimetypes.guess_type(path)
                    im = req.headers.get('If-None-Match')
                    if im == md5:
                        return Response(status_code=304, headers={'Cache-Control':'no-cache', 'ETag': md5})
                    return StreamingResponse(io.BytesIO(asset_data), media_type=mime,
                                             headers={'Cache-Control':'no-cache', 'ETag': md5})

        # assetsフォルダ内のファイルを全てマッピング
        for asset in glob.glob(str(Path(feature.__file__).parent.parent / 'web' / 'assets') + '/**/*', recursive=True):
            asset = Path(asset)
            if not asset.is_file():
                continue
            with open(asset, 'rb') as f:
                path = asset.relative_to(Path(feature.__file__).parent.parent / 'web' / 'assets')
                asset_func(f.read() if not ondemand_load else None, asset, str(path).replace('\\', '/'))

        # assetsパス指定をマッピング
        if web.assets is not None:
            for asset in web.assets:
                if not asset.is_file():
                    raise FileNotFoundError(f'asset is not found. ({asset})')
                with open(asset, 'rb') as f:
                    try:
                        path = asset.relative_to(web.doc_root / 'assets')
                    except ValueError:
                        path = Path(str(asset)[str(asset).find('assets')+len('assets/'):])
                    for r in app.routes.copy():
                        p = str(path).replace('\\', '/')
                        if r.path==f'/signin/assets/{p}' or r.path==f'/assets/{p}':
                            app.routes.remove(r)
                    asset_func(f.read() if not ondemand_load else None, asset, str(path).replace('\\', '/'))
