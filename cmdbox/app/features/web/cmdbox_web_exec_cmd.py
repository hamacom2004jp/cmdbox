from cmdbox.app import app, client, common, options, server
from cmdbox.app.auth import signin
from cmdbox.app.commons import convert
from cmdbox.app.features.cli import cmdbox_audit_search, cmdbox_audit_write
from cmdbox.app.features.web import cmdbox_web_load_cmd
from cmdbox.app.web import Web
from fastapi import FastAPI, Depends, Request, Response, HTTPException
from fastapi.responses import PlainTextResponse
from starlette.datastructures import UploadFile
from typing import Dict, Any, List, Tuple
import asyncio
import html
import io
import json
import threading
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
        async def exec_cmd(req:Request, res:Response, title:str=None, scope=Depends(signin.create_request_scope)):
            try:
                signin = web.signin.check_signin(req, res)
                if signin is not None:
                    raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
                opt = None
                content_type = req.headers.get('content-type')
                def _marge_opt(opt:Dict[str, Any], param:Dict[str, Any]) -> Dict[str, Any]:
                    opt.update(param)
                    return opt
                opt_def = self.load_cmd(web, title)
                if content_type is None:
                    opt = _marge_opt(opt_def, req.query_params)
                elif content_type.startswith('multipart/form-data'):
                    opt = _marge_opt(opt_def, req.query_params)
                    form = await req.form()
                    #files = {key: value for key, value in form.multi_items() if isinstance(value, UploadFile)}
                    for key, fv in form.multi_items():
                        if not isinstance(fv, UploadFile): continue
                        opt[key] = fv.file
                        if key == 'input_file': opt['stdin'] = False
                elif content_type.startswith('application/json'):
                    opt = await req.json()
                    opt = _marge_opt(opt_def, opt)
                elif content_type.startswith('application/octet-stream'):
                    opt = _marge_opt(opt_def, req.query_params)
                    opt['_stdin_body'] = await req.body()
                else:
                    opt = _marge_opt(opt_def, req.query_params)
                if 'mode' not in opt or 'cmd' not in opt:
                    raise HTTPException(status_code=404, detail='mode or cmd is not found.')
                opt['capture_stdout'] = nothread = True
                opt['stdout_log'] = False

                if options.Options.getInstance().get_cmd_attr(opt['mode'], opt['cmd'], "nouse_webmode"):
                    return dict(warn=f'Command "{title}" failed. This command is not available in web mode.')

                return await self.exec_cmd(req, res, web, title, opt, nothread)
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

    async def exec_cmd(self, req:Request, res:Response, web:Web,
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
        tags = []
        if 'tag' in opt and isinstance(opt['tag'], list):
            tags = [t for t in opt['tag'] if t is not None and t != '']
        web.options.audit_exec(req, res, web, tags=tags, title=title)
        appcls = self.appcls if appcls is None else appcls
        appcls = app.CmdBoxApp if appcls is None else appcls
        web.container['cmdbox_app'] = ap = appcls.getInstance(appcls=appcls, ver=self.ver)
        if 'mode' in opt and 'cmd' in opt:
            if not web.signin.check_cmd(req, res, opt['mode'], opt['cmd']):
                return dict(warn=f'Command "{title}" failed. Execute command denyed. mode={opt["mode"]}, cmd={opt["cmd"]}')
            _options = options.Options.getInstance()
            schema = _options.get_cmd_choices(opt['mode'], opt['cmd'], False)
            try:
                opt_path = web.cmds_path / f"cmd-{title}.json"
                feat = _options.get_cmd_attr(opt['mode'], opt['cmd'], "feature")
                loaded = common.loadopt(opt_path, False)
                for o in opt.keys():
                    found = False
                    for s in schema:
                        if 'opt' not in s or s['opt'] != o: continue
                        if 'web' not in s or s['web'] != 'mask': continue
                        found = True
                    if not found or o not in loaded: continue
                    opt[o] = loaded[o]
                    if isinstance(feat, cmdbox_audit_write.AuditWrite) and hasattr(_options, 'audit_write_args') and o in _options.audit_write_args:
                        opt[o] = _options.audit_write_args[o]
                    elif isinstance(feat, cmdbox_audit_search.AuditSearch) and hasattr(_options, 'audit_search_args') and o in _options.audit_search_args:
                        opt[o] = _options.audit_search_args[o]
            except:
                pass
        if 'host' in opt: opt['host'] = web.redis_host
        if 'port' in opt: opt['port'] = web.redis_port
        if 'password' in opt: opt['password'] = web.redis_password
        if 'svname' in opt: opt['svname'] = web.svname
        if not 'clmsg_id' in opt:  # optに含まれる場合は処理しない
            if req.session is not None and 'signin' in req.session and req.session['signin'] is not None:
                if 'clmsg_id' in req.session['signin'] and req.session['signin']['clmsg_id'] is not None:
                    opt['clmsg_id'] = req.session['signin']['clmsg_id']
        ap.sv = None
        ap.cl = None
        ap.web = None
        async def _exec_cmd(cmdbox_app:app.CmdBoxApp, title, opt, nothread=False) -> Any:
            _stdin_body = None
            if '_stdin_body' in opt:
                _stdin_body = opt['_stdin_body']
                del opt['_stdin_body']
            web.logger.info(f"exec_cmd: title={title}, opt={opt}")
            ret, output = self.chk_client_only(web, opt)
            if ret:
                if nothread: return output
                self.callback_return_pipe_exec_func(web, title, output)
                return output

            opt_list, file_dict = web.options.mk_opt_list(opt)
            old_stdout = sys.stdout
            old_stdin = sys.stdin
            if 'capture_stdout' in opt and opt['capture_stdout'] and 'stdin' in opt and opt['stdin'] and _stdin_body is None:
                output = dict(warn=f'The "stdin" and "capture_stdout" options cannot be enabled at the same time. This is because it may cause a memory squeeze.')
                if nothread: return output
                self.callback_return_pipe_exec_func(web, title, output)
                return output
            ret_main = {}
            logsize = 1024
            console = common.create_console(file=old_stdout)

            try:
                if _stdin_body is not None:
                    sys.stdin = io.BytesIO(_stdin_body)
                if 'capture_stdout' in opt and opt['capture_stdout']:
                    sys.stdout = captured_output = io.StringIO()
                capture_maxsize = opt['capture_maxsize'] if 'capture_maxsize' in opt else self.DEFAULT_CAPTURE_MAXSIZE
                def to_json(o):
                    res_json = json.loads(o)
                    if 'output_image' in res_json and 'output_image_shape' in res_json:
                        img_npy = convert.b64str2npy(res_json["output_image"], res_json["output_image_shape"])
                        img_bytes = convert.npy2imgfile(img_npy, image_type='png')
                        res_json["output_image"] = convert.bytes2b64str(img_bytes)
                        res_json['output_image_name'] = f"{res_json['output_image_name'].strip()}.png"
                    return res_json
                """
                def _main(args_list:List[str], file_dict:Dict[str, Any]=None, webcall:bool=False, ret:List=[]):
                    common.console_log(console, message=f'EXEC  - {opt_list}\n'[:logsize], highlight=(len(opt_list)<logsize-10))
                    try:
                        status, ret_main, obj = cmdbox_app.main(args_list=[common.chopdq(o) for o in opt_list], file_dict=file_dict, webcall=True)
                        ret += [status, ret_main, obj, None]
                    except Exception as e:
                        ret += [1, dict(warn=f'<pre>{html.escape(traceback.format_exc())}</pre>'), None, e]
                _ret = []
                _th_main = threading.Thread(target=_main, args=(opt_list, file_dict, True, _ret))
                _th_main.start()
                _th_main.join()
                """
                status, ret_main, obj = cmdbox_app.main(args_list=[common.chopdq(o) for o in opt_list], file_dict=file_dict, webcall=True)
                web.logger.disabled = False # ログ出力を有効にする
                """
                status, ret_main, obj, _err = _ret
                if _err is not None:
                    output = msg = ret_main
                    common.console_log(console, message=f'EXEC  - {msg}'[:logsize], highlight=(len(msg)<logsize-10))
                    web.logger.warning(msg)
                """
                if isinstance(obj, server.Server):
                    cmdbox_app.sv = obj
                elif isinstance(obj, client.Client):
                    cmdbox_app.cl = obj
                elif isinstance(obj, Web):
                    cmdbox_app.web = obj

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
                old_stdout.write(f'EXEC OUTPUT => {output}'[:logsize]+'\n') # コマンド実行時のアウトプットはカラーリングしない
            except Exception as e:
                msg = f'exec_cmd error. {traceback.format_exc()}'
                common.console_log(console, message=f'EXEC  - {msg}'[:logsize], highlight=(len(msg)<logsize-10))
                web.logger.warning(msg)
                output = [dict(warn=f'<pre>{html.escape(traceback.format_exc())}</pre>')]
            finally:
                web.logger.disabled = False # ログ出力を有効にする
                sys.stdout = old_stdout
                sys.stdin = old_stdin
            if 'stdout_log' in opt and opt['stdout_log']:
                self.callback_console_modal_log_func(web, output)
            try:
                try:
                    ret = [to_json(o) for o in output.split('\n') if o.strip() != '']
                except:
                    try:
                        ret = to_json(output)
                    except:
                        ret = ret_main
                if nothread:
                    if isinstance(ret, str):
                        return PlainTextResponse(ret, media_type='text/plain')
                    return ret
                self.callback_return_cmd_exec_func(web, title, ret)
            except:
                web.logger.warning(f'exec_cmd error.', exec_info=True)
                if nothread:
                    return output
                self.callback_return_cmd_exec_func(web, title, output)
        if nothread:
            return await _exec_cmd(ap, title, opt, True)
        asyncio.create_task(_exec_cmd(ap, title, opt, True))
        await asyncio.sleep(0)
        #th = _web.RaiseThread(target=_exec_cmd, args=(ap, title, opt, False))
        #th.start()
        return [dict(warn='start_cmd')]

