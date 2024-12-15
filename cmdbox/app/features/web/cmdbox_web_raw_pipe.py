from cmdbox.app import common
from cmdbox.app.features.web import cmdbox_web_raw_cmd, cmdbox_web_load_cmd
from cmdbox.app.web import Web
from fastapi import FastAPI, Request, Response, HTTPException
from typing import Dict, Any, List
import logging
import json


class RawPipe(cmdbox_web_raw_cmd.RawCmd, cmdbox_web_load_cmd.LoadCmd):
    def route(self, web:Web, app:FastAPI) -> None:
        """
        webモードのルーティングを設定します

        Args:
            web (Web): Webオブジェクト
            app (FastAPI): FastAPIオブジェクト
        """
        @app.post('/gui/raw_pipe')
        async def raw_pipe(req:Request, res:Response):
            signin = web.check_signin(req, res)
            if signin is not None:
                raise HTTPException(status_code=401, detail=self.DEFAULT_401_MESSAGE)
            form = await req.form()
            title = form.get('title')
            opt = form.get('opt')
            ret = self.raw_pipe(web, title, json.loads(opt))
            return ret

    def raw_pipe(self, web:Web, title:str, opt:Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        パイプラインのコマンドライン文字列、curlコマンド文字列を作成する

        Args:
            title (str): タイトル
            opt (dict): オプション
        
        Returns:
            list[Dict[str, Any]]: コマンドライン文字列、curlコマンド文字列
        """
        if web.logger.level == logging.DEBUG:
            web.logger.debug(f"web.raw_pipe: title={title}, opt={opt}")
        cmdlines = []
        errormsg = []
        curl_cmd_file = ""
        for i, cmd_title in enumerate(opt['pipe_cmd']):
            if cmd_title == '':
                continue
            cmd_opt = self.load_cmd(web, cmd_title)
            cmd_ref = web.options.get_cmd_choices(cmd_opt['mode'], cmd_opt['cmd'])
            chk_stdin = len([ref for ref in cmd_ref if ref['opt'] == 'stdin']) > 0

            if 'debug' in cmd_opt and cmd_opt['debug']:
                errormsg.append(f'The "debug" option is not supported with the debug option "true". ({cmd_title})')
            if 'output_csv' in cmd_opt and cmd_opt['output_csv'] != '':
                errormsg.append(f'The "output_csv" option is not supported in pipe. ({cmd_title})')
            if i>0:
                if chk_stdin and ('stdin' not in cmd_opt or not cmd_opt['stdin']):
                    errormsg.append(f'The "stdin" option should be specified for the second and subsequent commands. ({cmd_title})')
                if chk_stdin and 'pred_input_type' in cmd_opt and cmd_opt['pred_input_type'] not in ['capture']:
                    errormsg.append(f'When using the "stdin" option, "pred_input_type" cannot be other than "capture". ({cmd_title})')
                for ref in cmd_ref:
                    if 'fileio' in ref and ref['fileio'] == 'in' and ref['opt'] in cmd_opt and cmd_opt[ref['opt']] != '' and len([v for v in cmd_opt[ref['opt']] if v != '']) > 0:
                        errormsg.append(f'The "{ref["opt"]}" option should not be specified in a second or subsequent command. ({cmd_title})')
            if i==0:
                if 'request_files' in opt and len(opt['request_files']) > 0:
                    for fn in opt['request_files']:
                        if fn in cmd_opt:
                            cmd_opt[fn] = opt['request_files'][fn]
                curl_cmd_file = self.mk_curl_fileup(web, cmd_opt)

            cmd_output = self.raw_cmd(web, cmd_title, cmd_opt)
            cmdlines.append(cmd_output[0]["raw"])

        curl_opt = json.dumps(opt, default=common.default_json_enc)
        curl_opt = curl_opt.replace('"', '\\"')
        ret = [dict(type='cmdline', raw=' | '.join(cmdlines)),
                dict(type='curlcmd', raw=f'curl {curl_cmd_file} http://localhost:{web.listen_port}/exec_pipe/{title}')]
        ret += [dict(type='warn', raw=em) for em in errormsg]
        return ret
