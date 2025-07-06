from cmdbox.app import common, edge_tool, feature, options, web
from cmdbox.app.commons import convert
from cmdbox.app.options import Options
from fastapi import FastAPI, Request, HTTPException
from pathlib import Path
from PIL import Image
from typing import Dict, List, Tuple, Any, Union
from uvicorn.config import Config
import argparse
import json
import logging
import locale
import queue
import requests
import time
import threading
import webbrowser
import urllib.parse
import urllib3


class Edge(object):
    def __init__(self, logger:logging.Logger, data:str, appcls=None, ver=None):
        self.logger = logger
        self.data = data
        self.appcls = appcls
        self.ver = ver
        self.options = options.Options.getInstance()
        self.tool = edge_tool.Tool(logger, appcls, ver)
        if self.ver is None:
            raise ValueError('ver is None')
        if self.appcls is None:
            raise ValueError('appcls is None')
        if self.logger is None:
            raise ValueError('logger is None')
        if self.data is None:
            raise ValueError('data is None')
        self.user_info = None
        self.svcert_no_verify = False

    def configure(self, edge_mode:str, edge_cmd:str, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Dict[str, str]:
        """
        端末モードの設定を行います

        Args:
            edge_mode (str): edgeモード
            edge_cmd (str): edgeコマンド
        
        Returns:
            Dict[str, str]: メッセージ
        """
        v = self.ver.__logo__ + '\n' + self.ver.__description__
        common.print_format(v, False, tm, None, False, pf=pf)

        import questionary
        ref_opts = self.options.get_cmd_choices(edge_mode, edge_cmd)
        language, _ = locale.getlocale()
        edge_dir = Path(self.data) / '.edge'
        common.mkdirs(edge_dir)
        conf_file = edge_dir / 'edge.conf'
        if conf_file.is_file():
            # 設定ファイルが存在する場合は読み込む
            conf = common.loadopt(conf_file)
        else:
            conf = dict()
        skip_opts = []
        input_opts = []
        def _show_opts(choice_show:Dict[str, List[str]], value:str, ref_opts:List[Dict[str, Any]]) -> None:
            for k, v in choice_show.items():
                if k == value:
                    input_opts.extend(v)
                else:
                    skip_opts.extend(v)
                for r in ref_opts:
                    for opt in v:
                        if 'opt' not in r or r['opt'] is None:
                            continue
                        if 'choice_show' not in r or r['choice_show'] is None:
                            continue
                        _show_opts(r['choice_show'], '', [o for o in ref_opts if o['opt'] == opt])
        for r in ref_opts:
            if 'opt' not in r or r['opt'] is None:
                continue
            opt = r['opt']
            if opt in ['tag', 'clmsg_id', 'output_json', 'output_json_append', 'stdout_log', 'capture_stdout', 'capture_maxsize']:
                continue
            if opt in skip_opts and opt not in input_opts:
                continue
            choice_show = r['choice_show'] if 'choice_show' in r else dict()
            default = conf[opt] if opt in conf else None
            default = r['default'] if default is None and 'default' in r else default
            default = default if default is not None else ''
            default = args.__dict__[opt] if opt in args.__dict__ and args.__dict__[opt] is not None and args.__dict__[opt] != r['default'] else default
            default = str(default) if isinstance(default, Path) else default
            default = str(default) if isinstance(default, bool) else default
            default = str(default) if isinstance(default, int) or isinstance(default, float) else default
            description_ja = r['description_ja'] if 'description_ja' in r else None
            description_en = r['description_en'] if 'description_en' in r else None
            help = description_en if language.find('Japan') < 0 and language.find('ja_JP') < 0 else description_ja
            choice = r['choice'] if 'choice' in r else None
            choice = [str(c) for c in choice] if choice is not None else None
            required = r['required'] if 'required' in r else False
            if choice is not None:
                value = questionary.select(f"{opt}:({help}):", choice, default=default).ask()
            else:
                value = questionary.text(f"{opt}:({help}):", default=default, validate=lambda v:not required or len(v)>0).ask()
            _show_opts(choice_show, value, ref_opts)
            if r['type'] == Options.T_BOOL: value = value=='True'
            if r['type'] == Options.T_INT: value = int(value)
            if r['type'] == Options.T_FLOAT: value = float(value)
            conf[opt] = value
        # 設定ファイルに保存
        common.saveopt(conf, conf_file)
        msg = dict(success="configure complate.")
        return msg

    def start(self, resignin:bool=False) -> Dict[str, str]:
        """
        Edgeを起動します

        Args:
            resignin (bool): サインインを再実行する

        Returns:
            Dict[str, str]: メッセージ
        """
        msg = None
        try:
            edge_dir = Path(self.data) / '.edge'
            common.mkdirs(edge_dir)
            conf_file = edge_dir / 'edge.conf'
            if not conf_file.is_file():
                msg = dict(warn=f"Please run the `edge config` command first.")
                return msg

            opt = common.loadopt(conf_file)

            if 'icon_path' not in opt or opt['icon_path'] is None:
                msg = dict(warn=f"Please run the `edge config` command. And please set the icon_path.")
                return msg
            self.icon_path = Path(opt['icon_path'])
            if not self.icon_path.is_file():
                msg = dict(warn=f"icon file not found. icon_path={self.icon_path}")
                return msg
            if 'endpoint' not in opt or opt['endpoint'] is None:
                msg = dict(warn=f"Please run the `edge config` command. And please set the endpoint.")
                return msg
            if 'auth_type' not in opt or opt['auth_type'] is None:
                msg = dict(warn=f"Please run the `edge config` command. And please set the auth_type.")
                return msg
            if opt['auth_type'] == 'idpw':
                if 'user' not in opt or opt['user'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the user.")
                    return msg
                if 'password' not in opt or opt['password'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the password.")
                    return msg
            if opt['auth_type'] == 'apikey':
                if 'apikey' not in opt or opt['apikey'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the apikey.")
                    return msg
            if opt['auth_type'] == 'oauth2':
                if 'oauth2' not in opt or opt['oauth2'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the oauth2.")
                    return msg
                if 'oauth2_port' not in opt or opt['oauth2_port'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the oauth2_port.")
                    return msg
                if isinstance(opt['oauth2_port'], str):
                    if not opt['oauth2_port'].isdigit():
                        msg = dict(warn=f"Please set the numeric value in the oauth2_port. oauth2_port={opt['oauth2_port']}")
                        return msg
                    opt['oauth2_port'] = int(opt['oauth2_port'])
                if opt['oauth2'] == 'azure':
                    if 'oauth2_tenant_id' not in opt or opt['oauth2_tenant_id'] is None:
                        msg = dict(warn=f"Please run the `edge config` command. And please set the oauth2_tenant_id.")
                        return msg
                if 'oauth2_client_id' not in opt or opt['oauth2_client_id'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the oauth2_client_id.")
                    return msg
                if 'oauth2_client_secret' not in opt or opt['oauth2_client_secret'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the oauth2_client_secret.")
                    return msg
                if 'oauth2_timeout' not in opt or opt['oauth2_timeout'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the oauth2_timeout.")
                    return msg
                if isinstance(opt['oauth2_timeout'], str):
                    if not opt['oauth2_timeout'].isdigit():
                        msg = dict(warn=f"Please set the numeric value in the oauth2_timeout. oauth2_timeout={opt['oauth2_timeout']}")
                        return msg
                    opt['oauth2_timeout'] = int(opt['oauth2_timeout'])
            if opt['auth_type'] == 'saml':
                if 'saml' not in opt or opt['saml'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the saml.")
                    return msg
                if 'saml_port' not in opt or opt['saml_port'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the saml.")
                    return msg
                if isinstance(opt['saml_port'], str):
                    if not opt['saml_port'].isdigit():
                        msg = dict(warn=f"Please set the numeric value in the saml_port. saml_port={opt['saml_port']}")
                        return msg
                    opt['saml_port'] = int(opt['saml_port'])
                if opt['saml'] == 'azure':
                    if 'saml_tenant_id' not in opt or opt['saml_tenant_id'] is None:
                        msg = dict(warn=f"Please run the `edge config` command. And please set the saml_tenant_id.")
                        return msg
                if 'saml_timeout' not in opt or opt['saml_timeout'] is None:
                    msg = dict(warn=f"Please run the `edge config` command. And please set the saml_timeout.")
                    return msg
                if isinstance(opt['saml_timeout'], str):
                    if not opt['saml_timeout'].isdigit():
                        msg = dict(warn=f"Please set the numeric value in the saml_timeout. saml_timeout={opt['saml_timeout']}")
                        return msg
                    opt['saml_timeout'] = int(opt['saml_timeout'])
            if 'svcert_no_verify' not in opt or opt['svcert_no_verify'] is not True:
                opt['svcert_no_verify'] = False
            if 'timeout' not in opt or opt['timeout'] is None:
                msg = dict(warn=f"Please run the `edge config` command. And please set the timeout.")
                return msg
            if isinstance(opt['timeout'], str):
                if not opt['timeout'].isdigit():
                    msg = dict(warn=f"Please set the numeric value in the timeout. timeout={opt['timeout']}")
                    return msg
                opt['timeout'] = int(opt['timeout'])

            # サインイン
            self.endpoint = opt['endpoint']
            self.timeout = int(opt['timeout'])
            self.svcert_no_verify = opt['svcert_no_verify']
            if self.svcert_no_verify:
                urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
            status, msg = self.signin(opt.get('auth_type'), opt.get('user'), opt.get('password'), opt.get('apikey'),
                                      opt.get('oauth2'), int(opt.get('oauth2_port', 8091)),
                                      opt.get('oauth2_tenant_id'), opt.get('oauth2_client_id'), opt.get('oauth2_client_secret'),
                                      int(opt.get('oauth2_timeout', 60)),
                                      opt.get('saml'), int(opt.get('saml_port', 8091)),
                                      opt.get('saml_tenant_id'), int(opt.get('saml_timeout', 60)))

            if status != 0:
                return msg

            if not resignin:
                # 常駐開始
                self.start_tray()
            msg = dict(success="Complate.")
            return msg
        except Exception as e:
            self.logger.error(f"{e}", exc_info=True)
            msg = dict(error=f"{e}")
            return msg
        finally:
            if msg is not None:
                self.tool.notify(msg)

    def site_request(self, func, path:str, headers:Dict[str, str]=None, data:Any=None,
                     allow_redirects:bool=False, ok_status:List[int]=[200]) -> Tuple[int, Any, Dict[str, str]]:
        path = f"/{path}" if not path.startswith('/') else path
        res = func(f"{self.endpoint}{path}", headers=headers, data=data,
                    verify=not self.svcert_no_verify, timeout=self.timeout, allow_redirects=allow_redirects)
        if res.status_code not in ok_status:
            msg = dict(warn=f"Access failed. status_code={res.status_code}")
            self.tool.notify(msg)
            return 1, msg, res.headers
        return 0, res.content, res.headers

    def exec_pipe(self, opt:Dict[str, str]) -> Dict[str, str]:
        """
        パイプを実行します

        Args:
            opt (Dict[str, str]): パイプオプション

        Returns:
            Dict[str, str]: メッセージ
        """
        # パイプラインを読み込む
        status, res, _ = self.site_request(self.session.post, f"/gui/load_pipe", data=dict(title=opt['title']))
        if status != 0: return res
        res = json.loads(res)
        if 'pipe_cmd' not in res:
            msg = dict(warn=f"pipe_cmd not found. title={opt['title']}")
            self.tool.notify(msg)
            return 1, msg
        pipeline = []
        for cmd_title in res['pipe_cmd']:
            if cmd_title == '':
                continue
            status, cmd_opt, _ = self.site_request(self.session.post, f"/gui/load_cmd", data=dict(title=cmd_title))
            cmd_opt = json.loads(cmd_opt)
            if status != 0 or 'mode' not in cmd_opt or 'cmd' not in cmd_opt:
                return cmd_opt
            timeout = cmd_opt['timeout'] if 'timeout' in cmd_opt else self.timeout
            pipeline.append({**cmd_opt, **dict(title=cmd_title, timeout=timeout, resq=queue.Queue())})

        # パイプラインを実行
        def _job(thevent:threading.Event, pipe_cmd, prevq:queue.Queue):
            resq:queue.Queue = pipe_cmd['resq']
            del pipe_cmd['resq']
            tool = edge_tool.Tool(self.logger, self.appcls, self.ver)
            tool.set_session(self.session, self.svcert_no_verify, self.endpoint, self.icon_path, self.user_info, self.oauth2, self.saml)
            feat:feature.Feature = self.options.get_cmd_attr(pipe_cmd['mode'], pipe_cmd['cmd'], 'feature')
            while not thevent.is_set():
                prevres = None if prevq is None else prevq.get(pipe_cmd['timeout'])
                if prevres is False:
                    resq.put(False)
                    break
                for status, ret in feat.edgerun(pipe_cmd, tool, self.logger, self.timeout, prevres):
                    if status != 0 or thevent.is_set():
                        resq.put(ret)
                        resq.put(False)
                        return
                    resq.put(ret)

        self.stop_jobs(True)
        for i, pipe_cmd in enumerate(pipeline):
            prevq = None if i == 0 else pipeline[i-1]['resq']
            th = threading.Thread(target=_job, name=pipe_cmd['title'], args=(self.threading_event, pipe_cmd, prevq), daemon=True)
            th.start()
            self.threadings.append(th)
        msg = dict(success="Pipeline start.")
        return 0, msg

    def stop_jobs(self, no_notify:bool) -> None:
        if hasattr(self, 'threading_event'):
            self.threading_event.set()
        if hasattr(self, 'threadings'):
            while True:
                run_found = False
                for th in self.threadings:
                    th:threading.Thread = th
                    if th.is_alive():
                        run_found = True
                        break
                if not run_found:
                    break
            if not no_notify:
                if len(self.threadings) > 0:
                    self.tool.notify(dict(success="Jobs stopped."))
                else:
                    self.tool.notify(dict(warn="Jobs not running."))
        elif not no_notify:
            self.tool.notify(dict(warn="Jobs not running."))
        self.threading_event = threading.Event()
        self.threadings = []

    def start_tray(self) -> Dict[str, str]:
        # トレイアイコンを起動
        import pystray
        def list_cmd():
            _, res, _ = self.site_request(self.session.post, f"/gui/list_cmd")
            opts = json.loads(res)
            items = []
            for opt in opts:
                def mkcmd(opt):
                    def _ex():
                        tool = edge_tool.Tool(self.logger, self.appcls, self.ver)
                        tool.set_session(self.session, self.svcert_no_verify, self.endpoint, self.icon_path, self.user_info, self.oauth2, self.saml)
                        feat:feature.Feature = self.options.get_cmd_attr(opt['mode'], opt['cmd'], 'feature')
                        for status, ret in feat.edgerun(opt, tool, self.logger, self.timeout):
                            pass
                    return _ex
                items.append(pystray.MenuItem(opt['title'], mkcmd(opt)))
            return items
        def list_pipe():
            status, res, _ = self.site_request(self.session.post, "/gui/list_pipe", allow_redirects=False)
            if status != 0: return status, res
            opts = json.loads(res)
            items = []
            for opt in opts:
                def mkpipe(opt):
                    return lambda: self.exec_pipe(opt)
                items.append(pystray.MenuItem(opt['title'], mkpipe(opt)))
            return items
        def list_opens():
            status, res, _ = self.site_request(self.session.get, "/gui/toolmenu", allow_redirects=False)
            if status != 0: return status, res
            opens = json.loads(res)
            items = []
            items.append(pystray.MenuItem('Gui', lambda: self.tool.open_browser('/gui')))
            for k, op in opens.items():
                def mkop(tool:edge_tool.Tool, href):
                    return lambda: tool.open_browser(href)
                items.append(pystray.MenuItem(op['html'], mkop(self.tool, op['href'])))
            return items
        menu = pystray.Menu(
                pystray.MenuItem('Open', pystray.Menu(*list_opens())),
                pystray.MenuItem('Commands',pystray.Menu(*list_cmd())),
                pystray.MenuItem('Pipelines',pystray.Menu(*list_pipe())),
                pystray.MenuItem('Actions', pystray.Menu(
                    pystray.MenuItem('Retry signin', lambda: self.start(True)),
                    pystray.MenuItem('Stop jobs', lambda: self.stop_jobs(False)),)),
                pystray.MenuItem('Quit', lambda: icon.stop()),)
        icon = pystray.Icon(self.ver.__appid__, Image.open(self.icon_path), self.ver.__title__, menu)
        msg = dict(success="Edge start.")
        self.tool.notify(msg)
        icon.run()

    def load_user_info(self) -> Tuple[int, Dict[str, Any]]:
        status, res, _ = self.site_request(self.session.get, "/gui/user_info", allow_redirects=False)
        if status != 0: return status, res
        return status, json.loads(res)

    def signin(self, auth_type:str, user:str, password:str, apikey:str,
               oauth2:str, oauth2_port:int, oauth2_tenant_id:str, oauth2_client_id:str, oauth2_client_secret:str,
               oauth2_timeout:int,
               saml:str, saml_port:int, saml_tenant_id:str,
               saml_timeout:int) -> Tuple[int, Dict[str, Any]]:
        """
        サインインを行います

        Args:
            auth_type (str): 認証タイプ
            user (str): ユーザー名
            password (str): パスワード
            apikey (str): APIキー
            oauth2 (str): OAuth2
            oauth2_port (int): OAuth2ポート
            oauth2_tenant_id (str): OAuth2テナントID
            oauth2_client_id (str): OAuth2クライアントID
            oauth2_client_secret (str): OAuth2クライアントシークレット
            oauth2_timeout (int): OAuth2タイムアウト
            saml (str): SAML
            saml_port (int): SAMLポート
            saml_tenant_id (str): SAMLテナントID
            saml_timeout (int): SAMLタイムアウト

        Returns:
            Tuple[int, Dict[str, Any]]: 終了コード, メッセージ
        """
        self.session = requests.Session()
        self.signed_in = False
        self.oauth2 = oauth2
        self.saml = saml
        if auth_type == "noauth":
            status, res, _ = self.site_request(self.session.get, "/gui")
            if status != 0: return status, res
            status, self.user_info = self.load_user_info()
            self.user_info['auth_type'] = auth_type
            if status != 0: return status, res
            self.tool.set_session(self.session, self.svcert_no_verify, self.endpoint, self.icon_path, self.user_info, self.oauth2, self.saml)
            return 0, dict(success="No auth.")

        # ID/PW認証を使用する場合
        elif auth_type == "idpw":
            if user is None:
                return 1, dict(warn="Please specify the --user option.")
            if password is None:
                return 1, dict(warn="Please specify the --password option.")

            status, res, headers = self.site_request(self.session.post, "/dosignin/gui", data=dict(name=user, password=password), ok_status=[200, 307])
            if status != 0 or headers.get('signin') is None:
                return 1, dict(warn=f"Signin failed.", headers=headers)
            status, self.user_info = self.load_user_info()
            self.user_info['auth_type'] = auth_type
            self.user_info['password'] = password
            if status != 0: return status, res
            self.tool.set_session(self.session, self.svcert_no_verify, self.endpoint, self.icon_path, self.user_info, self.oauth2, self.saml)
            return 0, dict(success="Signin Success.")

        # APIKEY認証を使用する場合
        elif auth_type == "apikey":
            if apikey is None:
                return 1, dict(warn="Please specify the --apikey option.")
            headers = {"Authorization": f"Bearer {apikey}"}
            status, res, headers = self.site_request(self.session.get, "/gui", headers=headers)
            if status != 0 or headers.get('signin') is None:
                return 1, dict(warn=f"Signin failed.")
            status, self.user_info = self.load_user_info()
            self.user_info['auth_type'] = auth_type
            self.user_info['apikey'] = apikey
            if status != 0: return status, res
            self.tool.set_session(self.session, self.svcert_no_verify, self.endpoint, self.icon_path, self.user_info, self.oauth2, self.saml)
            return 0, dict(success="Signin Success.")

        # OAuth2認証を使用する場合
        elif auth_type == "oauth2":
            # Google OAuth2を使用する場合
            if oauth2 == "google":
                if oauth2_client_id is None:
                    return 1, dict(warn="Please specify the --oauth2_client_id option.")
                if oauth2_client_secret is None:
                    return 1, dict(warn="Please specify the --oauth2_client_secret option.")
                if oauth2_timeout is None:
                    return 1, dict(warn="Please specify the --oauth2_timeout option.")
                redirect_uri = f'http://localhost:{oauth2_port}/oauth2/google/callback'
                # OAuth2認証のコールバックを受けるFastAPIサーバーを起動
                fastapi = FastAPI()
                @fastapi.get('/oauth2/google/callback')
                async def oauth2_google_callback(req:Request):
                    if req.query_params['state'] != 'edge':
                        return dict(warn="Invalid state.")
                    # アクセストークン取得
                    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
                    data = {'code': req.query_params['code'],
                            'client_id': oauth2_client_id,
                            'client_secret': oauth2_client_secret,
                            'redirect_uri': redirect_uri,
                            'grant_type': 'authorization_code'}
                    query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
                    try:
                        token_resp = self.session.post(url='https://oauth2.googleapis.com/token', headers=headers, data=query,
                                                       verify=not self.svcert_no_verify)
                        token_resp.raise_for_status()
                        token_json = token_resp.json()
                        access_token = token_json['access_token']
                        status, res, headers = self.site_request(self.session.get, f"/oauth2/google/session/{access_token}/gui", ok_status=[200, 307])
                        if status != 0 or headers.get('signin') is None:
                            return dict(warn=f"Signin failed.")
                        status, self.user_info = self.load_user_info()
                        self.user_info['auth_type'] = auth_type
                        self.user_info['access_token'] = access_token
                        if status != 0: return res
                        self.signed_in = True
                        self.tool.set_session(self.session, self.svcert_no_verify, self.endpoint, self.icon_path, self.user_info, self.oauth2, self.saml)
                        return dict(success="Signin success. Please close your browser.")
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

                if not hasattr(self, 'thUvicorn') or not self.thUvicorn.is_alive():
                    self.thUvicorn = web.ThreadedUvicorn(config=Config(app=fastapi, host='localhost', port=oauth2_port))
                    self.thUvicorn.start()
                    time.sleep(1)

                # OAuth2認証のリクエストを送信
                data = {'scope': 'email',
                        'access_type': 'offline',
                        'response_type': 'code',
                        'redirect_uri': redirect_uri,
                        'client_id': oauth2_client_id,
                        'state': 'edge'}
                query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
                webbrowser.open(f'https://accounts.google.com/o/oauth2/auth?{query}')

                # 認証完了まで指定秒数待つ
                tm = time.time()
                while not self.signed_in:
                    if time.time() - tm > oauth2_timeout:
                        return 1, dict(warn="Signin Timeout.")
                    time.sleep(1)
                return 0, dict(success="Signin success.")

            # GitHub OAuth2を使用する場合
            elif oauth2 == "github":
                if oauth2_client_id is None:
                    return 1, dict(warn="Please specify the --oauth2_client_id option.")
                if oauth2_client_secret is None:
                    return 1, dict(warn="Please specify the --oauth2_client_secret option.")
                if oauth2_timeout is None:
                    return 1, dict(warn="Please specify the --oauth2_timeout option.")

                redirect_uri = f'http://localhost:{oauth2_port}/oauth2/github/callback'
                # OAuth2認証のコールバックを受けるFastAPIサーバーを起動
                fastapi = FastAPI()
                @fastapi.get('/oauth2/github/callback')
                async def oauth2_github_callback(req:Request):
                    if req.query_params['state'] != 'edge':
                        return dict(warn="Invalid state.")
                    # アクセストークン取得
                    headers = {'Content-Type': 'application/x-www-form-urlencoded',
                               'Accept': 'application/json'}
                    data = {'code': req.query_params['code'],
                            'client_id': oauth2_client_id,
                            'client_secret': oauth2_client_secret,
                            'redirect_uri': redirect_uri}
                    query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
                    try:
                        token_resp = self.session.post(url='https://github.com/login/oauth/access_token', headers=headers, data=query,
                                                       verify=not self.svcert_no_verify)
                        token_resp.raise_for_status()
                        token_json = token_resp.json()
                        access_token = token_json['access_token']
                        status, res, headers = self.site_request(self.session.get, f"/oauth2/github/session/{access_token}/gui", ok_status=[200, 307])
                        if status != 0 or headers.get('signin') is None:
                            return dict(warn=f"Signin failed.")
                        status, self.user_info = self.load_user_info()
                        self.user_info['auth_type'] = auth_type
                        self.user_info['access_token'] = access_token
                        if status != 0: return res
                        self.signed_in = True
                        self.tool.set_session(self.session, self.svcert_no_verify, self.endpoint, self.icon_path, self.user_info, self.oauth2, self.saml)
                        return dict(success="Signin success. Please close your browser.")
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

                if not hasattr(self, 'thUvicorn') or not self.thUvicorn.is_alive():
                    self.thUvicorn = web.ThreadedUvicorn(config=Config(app=fastapi, host='localhost', port=oauth2_port))
                    self.thUvicorn.start()
                    time.sleep(1)

                # OAuth2認証のリクエストを送信
                data = {'scope': 'user',
                        'access_type': 'offline',
                        'response_type': 'code',
                        'redirect_uri': redirect_uri,
                        'client_id': oauth2_client_id,
                        'state': 'edge'}
                query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
                webbrowser.open(f'https://github.com/login/oauth/authorize?{query}')

                # 認証完了まで指定秒数待つ
                tm = time.time()
                while not self.signed_in:
                    if time.time() - tm > oauth2_timeout:
                        return 1, dict(warn="Signin Timeout.")
                    time.sleep(1)
                return 0, dict(success="Signin success.")

            # Azure OAuth2を使用する場合
            elif oauth2 == "azure":
                if oauth2_tenant_id is None:
                    return 1, dict(warn="Please specify the --oauth2_tenant_id option.")
                if oauth2_client_id is None:
                    return 1, dict(warn="Please specify the --oauth2_client_id option.")
                if oauth2_client_secret is None:
                    return 1, dict(warn="Please specify the --oauth2_client_secret option.")
                if oauth2_timeout is None:
                    return 1, dict(warn="Please specify the --oauth2_timeout option.")

                redirect_uri = f'http://localhost:{oauth2_port}/oauth2/azure/callback'
                # OAuth2認証のコールバックを受けるFastAPIサーバーを起動
                fastapi = FastAPI()
                @fastapi.get('/oauth2/azure/callback')
                async def oauth2_azure_callback(req:Request):
                    if req.query_params['state'] != 'edge':
                        return dict(warn="Invalid state.")
                    # アクセストークン取得
                    headers = {'Content-Type': 'application/x-www-form-urlencoded',
                               'Accept': 'application/json'}
                    data = {'tenant': oauth2_tenant_id,
                            'code': req.query_params['code'],
                            'scope': " ".join(['openid', 'profile', 'email']),
                            'client_id': oauth2_client_id,
                            #'client_secret': oauth2_client_secret,
                            'redirect_uri': redirect_uri,
                            'grant_type': 'authorization_code'}
                    query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
                    try:
                        token_resp = self.session.post(url=f'https://login.microsoftonline.com/{oauth2_tenant_id}/oauth2/v2.0/token', headers=headers, data=query,
                                                       verify=not self.svcert_no_verify)
                        token_resp.raise_for_status()
                        token_json = token_resp.json()
                        access_token = token_json['access_token']
                        status, res, headers = self.site_request(self.session.get, f"/oauth2/azure/session/{access_token}/gui", ok_status=[200, 307])
                        if status != 0 or headers.get('signin') is None:
                            return dict(warn=f"Signin failed.")
                        status, self.user_info = self.load_user_info()
                        self.user_info['auth_type'] = auth_type
                        self.user_info['access_token'] = access_token
                        if status != 0: return res
                        self.signed_in = True
                        self.tool.set_session(self.session, self.svcert_no_verify, self.endpoint, self.icon_path, self.user_info, self.oauth2, self.saml)
                        return dict(success="Signin success. Please close your browser.")
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

                if not hasattr(self, 'thUvicorn') or not self.thUvicorn.is_alive():
                    self.thUvicorn = web.ThreadedUvicorn(self.logger, Config(app=fastapi, host='localhost', port=oauth2_port), {})
                    self.thUvicorn.start()
                    time.sleep(1)

                # OAuth2認証のリクエストを送信
                data = {'scope': " ".join(['openid', 'profile', 'email']),
                        'access_type': 'offline',
                        'response_type': 'code',
                        'redirect_uri': redirect_uri,
                        'client_id': oauth2_client_id,
                        'response_mode': 'query',
                        'state': 'edge'}
                query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
                webbrowser.open(f'https://login.microsoftonline.com/{oauth2_tenant_id}/oauth2/v2.0/authorize?{query}')

                # 認証完了まで指定秒数待つ
                tm = time.time()
                while not self.signed_in:
                    if time.time() - tm > oauth2_timeout:
                        return 1, dict(warn="Signin Timeout.")
                    time.sleep(1)
                return 0, dict(success="Signin success.")

        # saml認証を使用する場合
        elif auth_type == "saml":
            # Azure samlを使用する場合
            if saml == "azure":
                if saml_tenant_id is None:
                    return 1, dict(warn="Please specify the --saml_tenant_id option.")
                saml_settings = dict(
                    strict=False,
                    debug=self.logger.level==logging.DEBUG,
                    idp=dict(
                        entityId=f'https://sts.windows.net/{saml_tenant_id}/',
                        singleSignOnService=dict(
                            url=f'https://login.microsoftonline.com/{saml_tenant_id}/saml2',
                            binding=f'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'),
                        certFingerprint='',
                        certFingerprintAlgorithm='sha1',
                        singleLogoutService=dict()),
                    sp=dict(
                        entityId=self.endpoint,
                        assertionConsumerService=dict(
                            url=f'http://localhost:{saml_port}/saml/azure/callback',
                            binding=f'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-POST'),
                        attributeConsumingService=dict(),
                        singleLogoutService=dict(
                            binding=f'urn:oasis:names:tc:SAML:2.0:bindings:HTTP-Redirect'),
                        NameIDFormat=f'urn:oasis:names:tc:SAML:1.1:nameid-format:unspecified',
                        x509cert='',
                        privateKey=''))
                request_data = dict(
                    https='off',
                    http_host='localhost',
                    server_port=saml_port,
                    script_name=f'/saml/azure/gui?next=gui',
                    post_data=dict(),
                    get_data=dict(n=common.random_string(8)),
                )
                from onelogin.saml2.auth import OneLogin_Saml2_Auth
                auth = OneLogin_Saml2_Auth(request_data=request_data, old_settings=saml_settings)

                # SAML認証のコールバックを受けるFastAPIサーバーを起動
                fastapi = FastAPI()
                @fastapi.post('/saml/azure/callback')
                async def saml_azure_callback(req:Request):
                    form_data = await req.form()
                    try:
                        status, res, headers = self.site_request(self.session.post, f"/saml/azure/callback", data=form_data, ok_status=[200, 307])
                        if status != 0 or headers.get('signin') is None:
                            return dict(warn=f"Signin failed.")
                        status, self.user_info = self.load_user_info()
                        self.user_info['auth_type'] = auth_type
                        if status != 0: return res
                        self.signed_in = True
                        self.user_info['saml_token'] = convert.str2b64str(common.to_str(form_data._dict))
                        self.tool.set_session(self.session, self.svcert_no_verify, self.endpoint, self.icon_path, self.user_info, self.oauth2, self.saml)
                        return dict(success="Signin success. Please close your browser.")
                    except Exception as e:
                        raise HTTPException(status_code=500, detail=f'Failed to get token. {e}')

                if not hasattr(self, 'thUvicorn') or not self.thUvicorn.is_alive():
                    self.thUvicorn = web.ThreadedUvicorn(self.logger, Config(app=fastapi, host='localhost', port=saml_port), {})
                    self.thUvicorn.start()
                    time.sleep(1)

                # SAML認証のリクエストを送信
                webbrowser.open(auth.login())

                # 認証完了まで指定秒数待つ
                tm = time.time()
                while not self.signed_in:
                    if time.time() - tm > saml_timeout:
                        return 1, dict(warn="Signin Timeout.")
                    time.sleep(1)
                return 0, dict(success="Signin success.")

        return 1, dict(warn="unsupported auth_type.")
