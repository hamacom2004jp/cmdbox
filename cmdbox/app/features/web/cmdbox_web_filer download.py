from cmdbox.app import common
from cmdbox.app.commons import convert
from cmdbox.app.features.web import cmdbox_web_exec_cmd
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse
from pathlib import Path
from typing import Dict, Any
import io
import urllib.parse


class FilerDownload(cmdbox_web_exec_cmd.ExecCmd):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.get('/filer/download/{constr:str}', response_class=StreamingResponse)
        async def filer_download(constr:str, req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            try:
                host, port, svname, password, path, scope, img_thumbnail = convert.b64str2str(constr).split('\t')
                path = urllib.parse.unquote(path)
                data_dir = web.data if scope == 'client' else Path.cwd()
                data_dir = None if scope == 'server' else data_dir
                opt = dict(host=host, port=port, svname=svname, password=password, svpath=path, scope=scope,
                           img_thumbnail=img_thumbnail, mode='client', cmd='file_download', client_data=data_dir, stdout_log=False)
                opt['capture_stdout'] = nothread = True
                ret = self.exec_cmd(req, res, web, 'file_download', opt, nothread, self.appcls)
                if len(ret) == 0 or 'success' not in ret[0] or 'data' not in ret[0]['success']:
                    return common.to_str(ret)
                mime = ret[0]['success']['mime_type']
                return StreamingResponse(io.BytesIO(convert.b64str2bytes(ret[0]['success']['data'])),
                                         headers={'Cache-Control':'no-cache'},
                                         media_type=mime)
            except Exception as e:
                raise HTTPException(status_code=404, detail='Missing specified file or not an image.') from e
