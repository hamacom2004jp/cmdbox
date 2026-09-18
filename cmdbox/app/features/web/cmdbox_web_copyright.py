from cmdbox.app import feature
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
            em, headers = self.etag(web, req, str(self.ver.__copyright__))
            headers.update({'Access-Control-Allow-Origin': '*'})
            if em:
                return Response(status_code=304, headers=headers)
            return PlainTextResponse(self.ver.__copyright__, headers=headers)

