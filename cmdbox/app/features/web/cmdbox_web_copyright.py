from cmdbox.app import common, feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse


class Copyright(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/copyright', response_class=PlainTextResponse, responses=feature.WebFeature.DEFAULT_RESPONCE_STATES)
        async def copyright(req:Request, res:Response):
            hash_value = int(common.hash_password(self.ver.__copyright__, 'md5')[:16], 16)
            em, headers = self.etag(web, req, str(hash_value), force_cache=True)
            if em:
                return Response(status_code=304, headers=headers)
            return PlainTextResponse(self.ver.__copyright__, headers=headers)

