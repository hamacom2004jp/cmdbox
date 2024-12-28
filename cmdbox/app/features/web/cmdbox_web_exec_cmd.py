from cmdbox.app import app, client, server, web as _web
from cmdbox.app.commons import convert
from cmdbox.app.features.web import cmdbox_web_load_cmd
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from starlette.datastructures import UploadFile
from typing import Dict, Any, List
import html
import io
import json
import traceback
import sys


class ExecCmd(cmdbox_web_load_cmd.LoadCmd):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/exec_cmd')
        @app.get('/exec_cmd/{title}')
        @app.post('/exec_cmd/{title}')
        async def exec_cmd(req:Request, res:Response, title:str=None):
            try:
                signin = web.check_signin(req, res)
                if signin is not None:
                    raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
                opt = None
                if req.headers.get('content-type').startswith('multipart/form-data'):
                    opt = self.load_cmd(web, title)
                    form = await req.form()
                    files = {key: value for key, value in form.items() if isinstance(value, UploadFile)}
                    for fn in files.keys():
                        opt[fn] = files[fn].file
                        if fn == 'input_file': opt['stdin'] = False
                elif req.headers.get('content-type').startswith('application/json'):
                    opt = await req.json()
                else:
                    opt = self.load_cmd(web, title)
                opt['capture_stdout'] = nothread = True
                opt['stdout_log'] = False
                return self.exec_cmd(req, res, web, title, opt, nothread)
            except:
                return dict(warn=f'Command "{title}" failed. {traceback.format_exc()}')

    def chk_client_only(self, web:Web, opt):
        """
        クライアントのみのサービスかどうかをチェックする

        Args:
            web (Web): Webオブジェクト
            opt (dict): オプション

        Returns:
            tuple: (クライアントのみ場合はTrue, メッセージ)
        """
        if not web.client_only:
            return False, None
        use_redis = web.options.get_cmd_attr(opt['mode'], opt['cmd'], "use_redis")
        if use_redis == self.USE_REDIS_FALSE:
            return False, None
        output = dict(warn=f'Commands that require a connection to the cmdbox server are not available.'
                        +f' (mode={opt["mode"]}, cmd={opt["cmd"]}) '
                        +f'The cause is that the client_only option is specified when starting web mode.')
        if use_redis == self.USE_REDIS_TRUE:
            return True, output
        for c in web.options.get_cmd_attr(opt['mode'], opt['cmd'], "choice"):
            if c['opt'] == 'client_data' and 'client_data' in opt and opt['client_data'] is None:
                return True, output
        return False, None

    def exec_cmd(self, req:Request, res:Response, web:Web,
                 title:str, opt:Dict[str, Any], nothread:bool=False, appcls=None) -> List[Dict[str, Any]]:
        """
        コマンドを実行する

        Args:
            req (Request): リクエスト
            res (Response): レスポンス
            web (Web): Webオブジェクト
            title (str): タイトル
            opt (dict): オプション
            nothread (bool, optional): スレッドを使わないかどうか. Defaults to False.
        
        Returns:
            list: コマンド実行結果
        """
        appcls = self.appcls if appcls is None else appcls
        appcls = app.CmdBoxApp if appcls is None else appcls
        web.container['cmdbox_app'] = ap = appcls.getInstance(appcls=appcls, ver=self.ver)
        if 'mode' in opt and 'cmd' in opt:
            if not web.check_cmd(req, res, opt['mode'], opt['cmd']):
                return dict(warn=f'Command "{title}" failed. Execute command denyed. mode={opt["mode"]}, cmd={opt["cmd"]}')
        ap.sv = None
        ap.cl = None
        ap.web = None
        def _exec_cmd(cmdbox_app:app.CmdBoxApp, title, opt, nothread=False):
            web.logger.info(f"exec_cmd: title={title}, opt={opt}")
            ret, output = self.chk_client_only(web, opt)
            if ret:
                if nothread: return output
                self.callback_return_pipe_exec_func(web, title, output)
                return

            opt_list, file_dict = web.options.mk_opt_list(opt)
            old_stdout = sys.stdout

            if 'capture_stdout' in opt and opt['capture_stdout'] and 'stdin' in opt and opt['stdin']:
                output = dict(warn=f'The "stdin" and "capture_stdout" options cannot be enabled at the same time. This is because it may cause a memory squeeze.')
                if nothread: return output
                self.callback_return_pipe_exec_func(web, title, output)
                return
            if 'capture_stdout' in opt and opt['capture_stdout']:
                sys.stdout = captured_output = io.StringIO()
            try:
                status, ret, obj = cmdbox_app.main(args_list=opt_list, file_dict=file_dict, webcall=True)
                if isinstance(obj, server.Server):
                    cmdbox_app.sv = obj
                elif isinstance(obj, client.Client):
                    cmdbox_app.cl = obj
                elif isinstance(obj, Web):
                    cmdbox_app.web = obj

                web.logger.disabled = False # ログ出力を有効にする
                capture_maxsize = opt['capture_maxsize'] if 'capture_maxsize' in opt else self.DEFAULT_CAPTURE_MAXSIZE
                if 'capture_stdout' in opt and opt['capture_stdout']:
                    output = captured_output.getvalue().strip()
                    output_size = len(output)
                    if output_size > capture_maxsize:
                        o = output.split('\n')
                        if len(o) > 0:
                            osize = len(o[0])
                            oidx = int(capture_maxsize / osize)
                            if oidx > 0:
                                output = '\n'.join(o[-oidx:])
                            else:
                                output = [dict(warn=f'The captured stdout was discarded because its size was larger than {capture_maxsize} bytes.')]
                        else:
                            output = [dict(warn=f'The captured stdout was discarded because its size was larger than {capture_maxsize} bytes.')]
                else:
                    output = [dict(warn='capture_stdout is off.')]
            except Exception as e:
                web.logger.disabled = False # ログ出力を有効にする
                web.logger.info(f'exec_cmd error. {traceback.format_exc()}')
                output = [dict(warn=f'<pre>{html.escape(traceback.format_exc())}</pre>')]
            sys.stdout = old_stdout
            if 'stdout_log' in opt and opt['stdout_log']:
                self.callback_console_modal_log_func(web, output)
            try:
                def to_json(o):
                    res_json = json.loads(o)
                    if 'output_image' in res_json and 'output_image_shape' in res_json:
                        img_npy = convert.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
                        img_bytes = convert.npy2imgfile(img_npy, image_type='png')
                        res_json["output_image"] = convert.bytes2b64str(img_bytes)
                    return res_json
                try:
                    ret = [to_json(o) for o in output.split('\n') if o.strip() != '']
                except:
                    try:
                        ret = to_json(output)
                    except:
                        ret = output
                if nothread:
                    return ret
                self.callback_return_cmd_exec_func(web, title, ret)
            except:
                web.logger.warning(f'exec_cmd error.', exec_info=True)
                if nothread:
                    return output
                self.callback_return_cmd_exec_func(web, title, output)
        if nothread:
            return _exec_cmd(ap, title, opt, True)
        th = _web.RaiseThread(target=_exec_cmd, args=(ap, title, opt, False))
        th.start()
        return [dict(warn='start_cmd')]

