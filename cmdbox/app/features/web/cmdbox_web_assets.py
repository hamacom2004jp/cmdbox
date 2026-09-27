from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import StreamingResponse
from pathlib import Path
from typing import Union
import glob
import io
import mimetypes
import logging
import re


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
                    force_cache = self.is_force_cache_path(web, req, f'assets/{path}')
                    em, headers = self.etag(web, req, str(asset.stat().st_mtime_ns), force_cache=force_cache)
                    if em:
                        return Response(status_code=304, headers=headers)
                    with open(asset, 'rb') as f:
                        asset_data = f.read()
                        return StreamingResponse(io.BytesIO(asset_data), media_type=mime, headers=headers)
            else:
                hs = str(asset.stat().st_mtime_ns)
                @app.get(f'/signin/assets/{path}')
                @app.get(f'/assets/{path}')
                async def func(req:Request, res:Response):
                    mime, enc = mimetypes.guess_type(path)
                    force_cache = self.is_force_cache_path(web, req, f'assets/{path}')
                    em, headers = self.etag(web, req, hs, force_cache=force_cache)
                    if em:
                        return Response(status_code=304, headers=headers)
                    return StreamingResponse(io.BytesIO(asset_data), media_type=mime, headers=headers)

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

    regs_force_cache_path = [re.compile(r"assets/apexcharts"),
                             re.compile(r"assets/bootstrap"),
                             re.compile(r"assets/dompurify"),
                             re.compile(r"assets/encodingjs"),
                             re.compile(r"assets/highlight"),
                             re.compile(r"assets/jquery"),
                             re.compile(r"assets/lightbox2"),
                             re.compile(r"assets/marked"),
                             re.compile(r"assets/split-pane"),
                             re.compile(r"assets/tree-menu")]

    def is_force_cache_path(self, web:Web, req:Request, path:Union[str, Path]) -> bool:
        """
        指定されたパスが強制キャッシュ対象かどうかを判定します。

        Args:
            web (Web): Webオブジェクト
            req (Request): クライアントからのリクエストオブジェクト
            path (Union[str, Path]): 判定対象のパス

        Returns:
            bool: 強制キャッシュ対象であればTrue、そうでなければFalse
        """
        return any(reg.search(str(path)) for reg in self.regs_force_cache_path)
