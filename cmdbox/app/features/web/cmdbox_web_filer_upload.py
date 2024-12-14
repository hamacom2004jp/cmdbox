from cmdbox.app.features.web import cmdbox_web_exec_cmd
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
from pathlib import Path
from starlette.datastructures import UploadFile
import tempfile
import shutil


class FilerUpload(cmdbox_web_exec_cmd.ExecCmd):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/filer/upload', response_class=PlainTextResponse)
        async def filer_upload(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            return await self.filer_upload(web, req, res)

    async def filer_upload(self, web:Web, req:Request, res:Response) -> str:
        """
        ファイルをアップロードする

        Args:
            web (Web): Webオブジェクト
            req (Request): リクエスト
            res (Response): レスポンス
        
        Returns:
            str: 結果
        """
        q = req.query_params
        svpath = q['svpath']
        web.logger.info(f"filer_upload: svpath={svpath}")
        opt = dict(mode='client', cmd='file_upload',
                   host=q['host'], port=q['port'], password=q['password'], svname=q['svname'],
                   scope=q["scope"], client_data=q['client_data'], orverwrite=('orverwrite' in q))
        form = await req.form()
        files = {key: value for key, value in form.items() if isinstance(value, UploadFile)}
        for fn in files.keys():
            with tempfile.TemporaryDirectory() as tmpdir:
                raw_filename = files[fn].filename.replace('\\','/').replace('//','/')
                raw_filename = raw_filename if not raw_filename.startswith('/') else raw_filename[1:]
                upload_file:Path = Path(tmpdir) / raw_filename
                if not upload_file.parent.exists():
                    upload_file.parent.mkdir(parents=True)
                opt['svpath'] = str(svpath / Path(raw_filename).parent)
                opt['upload_file'] = str(upload_file).replace('"','')
                opt['capture_stdout'] = True
                shutil.copyfileobj(files[fn].file, Path(opt['upload_file']).open('wb'))
                ret = self.exec_cmd(req, res, web, "file_upload", opt, nothread=True)
                if type(ret) is dict and 'success' not in ret:
                    return str(ret)
                if type(ret) is list and (len(ret) == 0 or 'success' not in ret[0]):
                    return str(ret)
        return 'upload success'
        #return f'upload {upload.filename}'
