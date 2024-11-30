from cmdbox import version
from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pathlib import Path
import glob
import io
import mimetypes


class Assets(feature.WebFeature):
    def __init__(self, ver=version):
        super().__init__(ver=ver)

    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        def asset_func(asset_data, path):
            @app.get(f'/signin/assets/{path}')
            @app.get(f'/assets/{path}')
            def func():
                mime, enc = mimetypes.guess_type(path)
                return StreamingResponse(io.BytesIO(asset_data), media_type=mime)

        # assetsフォルダ内のファイルを全てマッピング
        for asset in glob.glob(str(Path(feature.__file__).parent.parent / 'web' / 'assets') + '/**/*', recursive=True):
            if not Path(asset).is_file():
                continue
            with open(asset, 'rb') as f:
                path = Path(asset).relative_to(Path(feature.__file__).parent.parent / 'web' / 'assets')
                asset_func(f.read(), str(path).replace('\\', '/'))

        # assetsパス指定をマッピング
        if web.assets is not None:
            for asset in web.assets:
                if not asset.is_file():
                    raise FileNotFoundError(f'asset is not found. ({asset})')
                with open(asset, 'rb') as f:
                    path = Path(asset).relative_to(web.doc_root / 'assets')
                    asset_func(f.read(), str(path).replace('\\', '/'))
