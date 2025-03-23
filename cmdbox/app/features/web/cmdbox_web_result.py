from cmdbox.app import feature
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response
from fastapi.responses import HTMLResponse
from typing import Dict, Any
import json


class Result(feature.WebFeature):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        if web.result_html is not None:
            if not web.result_html.is_file():
                raise FileNotFoundError(f'result_html is not found. ({web.result_html})')
            with open(web.result_html, 'r', encoding='utf-8') as f:
                web.result_html_data = f.read()

        @app.post('/result/pub')
        async def result(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            form = await req.form()
            title = form.get('title')
            output = form.get('output')
            try:
                output = json.loads(output)
            except:
                pass
            web.cb_queue.put(('js_return_cmd_exec_func', title, output))
            return dict(success="result put to queue.")

        @app.post('/result', response_class=HTMLResponse)
        @app.get('/result', response_class=HTMLResponse)
        async def result_html(req:Request, res:Response):
            signin = web.signin.check_signin(req, res)
            if signin is not None:
                return signin
            res.headers['Access-Control-Allow-Origin'] = '*'
            return web.result_html_data

    def toolmenu(self, web:Web) -> Dict[str, Any]:
        """
        ツールメニューの情報を返します

        Args:
            web (Web): Webオブジェクト
        
        Returns:
            Dict[str, Any]: ツールメニュー情報
        
        Sample:
            {
                'filer': {
                    'html': 'Filer',
                    'href': 'filer',
                    'target': '_blank',
                    'css_class': 'dropdown-item'
                    'onclick': 'alert("filer")'
                }
            }
        """
        return dict(result=dict(html='Result', href='result', target='_blank', css_class='dropdown-item'))
