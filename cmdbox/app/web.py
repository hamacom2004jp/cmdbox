from cmdbox.app import common, options
from cmdbox.app.commons import module
from fastapi import FastAPI, Request, Response
from fastapi.responses import RedirectResponse
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from typing import Any, Dict, List
import ctypes
import gevent
import logging
import os
import requests
import queue
import signal
import threading
import traceback
import uvicorn
import webbrowser


class Web:
    def __init__(self, logger:logging.Logger, data:Path, redis_host:str = "localhost", redis_port:int = 6379, redis_password:str = None, svname:str = 'server',
                 client_only:bool=False, doc_root:Path=None, gui_html:str=None, filer_html:str=None,
                 assets:List[str]=None, signin_html:str=None, signin_file:str=None, gui_mode:bool=False,
                 web_features_packages:List[str]=None, web_features_prefix:List[str]=None):
        """
        cmdboxクライアント側のwebapiサービス

        Args:
            logger (logging): ロガー
            data (Path): コマンドやパイプラインの設定ファイルを保存するディレクトリ
            redis_host (str, optional): Redisサーバーのホスト名. Defaults to "localhost".
            redis_port (int, optional): Redisサーバーのポート番号. Defaults to 6379.
            redis_password (str, optional): Redisサーバーのパスワード. Defaults to None.
            svname (str, optional): 推論サーバーのサービス名. Defaults to 'server'.
            client_only (bool, optional): クライアントのみのサービスかどうか. Defaults to False.
            doc_root (Path, optional): カスタムファイルのドキュメントルート. フォルダ指定のカスタムファイルのパスから、doc_rootのパスを除去したパスでURLマッピングします。Defaults to None.
            gui_html (str, optional): GUIのHTMLファイル. Defaults to None.
            filer_html (str, optional): ファイラーのHTMLファイル. Defaults to None.
            anno_html (str, optional): アノテーション画面のHTMLファイル. Defaults to None.
            assets (List[str], optional): 静的ファイルのリスト. Defaults to None.
            signin_html (str, optional): ログイン画面のHTMLファイル. Defaults to None.
            signin_file (str, optional): ログイン情報のファイル. Defaults to args.signin_file.
            gui_mode (bool, optional): GUIモードかどうか. Defaults to False.
            web_features_packages (List[str], optional): webfeatureのパッケージ名のリスト. Defaults to None.
            web_features_prefix (List[str], optional): webfeatureのパッケージのモジュール名のプレフィックス. Defaults to None.
        """
        super().__init__()
        self.logger = logger
        self.data = data
        self.container = dict()
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.svname = svname
        self.client_only = client_only
        if self.client_only:
            self.svname = 'client'
        self.doc_root = Path(doc_root) if doc_root is not None else Path(__file__).parent.parent / 'web'
        self.gui_html = Path(gui_html) if gui_html is not None else Path(__file__).parent.parent / 'web' / 'gui.html'
        self.filer_html = Path(filer_html) if filer_html is not None else Path(__file__).parent.parent / 'web' / 'filer.html'
        self.assets = []
        if assets is not None:
            if not isinstance(assets, list):
                raise ValueError(f'assets is not list. ({assets})')
            for a in assets:
                asset = Path(a)
                if asset.is_dir():
                    self.assets += [p for p in asset.glob('**/*') if p.is_file()]
                elif asset.is_file():
                    self.assets.append(asset)
        self.signin_html = Path(signin_html) if signin_html is not None else Path(__file__).parent.parent / 'web' / 'signin.html'
        self.signin_file = Path(signin_file) if signin_file is not None else None
        self.gui_html_data = None
        self.filer_html_data = None
        self.assets_data = None
        self.signin_html_data = None
        self.signin_file_data = None
        self.gui_mode = gui_mode
        self.web_features_packages = web_features_packages
        self.web_features_prefix = web_features_prefix
        self.cmds_path = self.data / ".cmds"
        self.pipes_path = self.data / ".pipes"
        self.static_root = Path(__file__).parent.parent / 'web'
        common.mkdirs(self.cmds_path)
        common.mkdirs(self.pipes_path)
        self.pipe_th = None
        self.img_queue = queue.Queue(1000)
        self.cb_queue = queue.Queue(1000)
        self.options = options.Options.getInstance()
        self.webcap_client = requests.Session()
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"web init parameter: data={self.data} -> {self.data.absolute() if self.data is not None else None}")
            self.logger.debug(f"web init parameter: redis_host={self.redis_host}")
            self.logger.debug(f"web init parameter: redis_port={self.redis_port}")
            self.logger.debug(f"web init parameter: redis_password=********")
            self.logger.debug(f"web init parameter: svname={self.svname}")
            self.logger.debug(f"web init parameter: client_only={self.client_only}")
            self.logger.debug(f"web init parameter: gui_html={self.gui_html} -> {self.gui_html.absolute() if self.gui_html is not None else None}")
            self.logger.debug(f"web init parameter: filer_html={self.filer_html} -> {self.filer_html.absolute() if self.filer_html is not None else None}")
            self.logger.debug(f"web init parameter: assets={self.assets} -> {[a.absolute() for a in self.assets] if self.assets is not None else None}")
            self.logger.debug(f"web init parameter: signin_html={self.signin_html} -> {self.signin_html.absolute() if self.signin_html is not None else None}")
            self.logger.debug(f"web init parameter: signin_file={self.signin_file} -> {self.signin_file.absolute() if self.signin_file is not None else None}")
            self.logger.debug(f"web init parameter: gui_mode={self.gui_mode}")
            self.logger.debug(f"web init parameter: web_features_packages={self.web_features_packages}")
            self.logger.debug(f"web init parameter: web_features_prefix={self.web_features_prefix}")
            self.logger.debug(f"web init parameter: cmds_path={self.cmds_path} -> {self.cmds_path.absolute() if self.cmds_path is not None else None}")
            self.logger.debug(f"web init parameter: pipes_path={self.pipes_path} -> {self.pipes_path.absolute() if self.pipes_path is not None else None}")

    def enable_cors(self, req:Request, res:Response) -> None:
        """
        CORSを有効にする

        Args:
            req (Request): リクエスト
            res (Response): レスポンス
        """
        if req is None or not 'Origin' in req.headers.keys():
            return
        res.headers['Access-Control-Allow-Origin'] = res.headers['Origin']

    #security = OAuth2PasswordBearer(tokenUrl="token")

    def check_signin(self, req:Request, res:Response):
        """
        サインインをチェックする

        Args:
            req (Request): リクエスト
            res (Response): レスポンス

        Returns:
            Response: サインインエラーの場合はリダイレクトレスポンス
        """
        self.enable_cors(req, res)
        if self.signin_file is None:
            return None
        if self.signin_file_data is None:
            raise ValueError(f'signin_file_data is None. ({self.signin_file})')
        if 'signin' in req.session:
            userid = req.session['signin']['userid']
            passwd = req.session['signin']['password']
            if userid in self.signin_file_data and passwd == self.signin_file_data[userid]['password']:
                return None
        self.logger.warning(f"signin error.")
        return RedirectResponse(url=f'/signin{req.url.path}')

    def start(self, allow_host:str="0.0.0.0", listen_port:int=8081, session_timeout:int=600, outputs_key:List[str]=[]):
        """
        Webサーバを起動する

        Args:
            allow_host (str, optional): 許可ホスト. Defaults to "
            listen_port (int, optional): リスンポート. Defaults to 8081.
            session_timeout (int, optional): セッションタイムアウト. Defaults to 600.
            outputs_key (list, optional): 出力キー. Defaults to [].
        """
        self.allow_host = allow_host
        self.listen_port = listen_port
        self.outputs_key = outputs_key
        self.session_timeout = session_timeout
        if self.logger.level == logging.DEBUG:
            self.logger.debug(f"web start parameter: allow_host={self.allow_host}")
            self.logger.debug(f"web start parameter: listen_port={self.listen_port}")
            self.logger.debug(f"web start parameter: outputs_key={self.outputs_key}")
            self.logger.debug(f"web start parameter: session_timeout={self.session_timeout}")

        app = FastAPI()
        app.add_middleware(SessionMiddleware, secret_key=common.random_string())

        self.filemenu = dict()
        self.toolmenu = dict()
        self.viewmenu = dict()
        self.aboutmenu = dict()
        # webfeatureの読込み
        def wf_route(pk, prefix, w, app):
            for wf in module.load_webfeatures(pk, prefix):
                wf.route(self, app)
                self.filemenu |= wf.filemenu(w)
                self.toolmenu |= wf.toolmenu(w)
                self.viewmenu |= wf.viewmenu(w)
                self.aboutmenu |= wf.aboutmenu(w)

        if self.web_features_packages is not None:
            if self.web_features_prefix is None:
                raise ValueError(f"web_features_prefix is None. web_features_prefix={self.web_features_prefix}")
            if len(self.web_features_prefix) != len(self.web_features_packages):
                raise ValueError(f"web_features_prefix is not match. web_features_packages={self.web_features_packages}, web_features_prefix={self.web_features_prefix}")
            for i, pn in enumerate(self.web_features_packages):
                wf_route(pn, self.web_features_prefix[i], self, app)
        self.options.load_features_file('web', lambda pk, pn: wf_route(pk, pn, self, app))
        wf_route("cmdbox.app.features.web", "cmdbox_web_", self, app)

        # 読込んだrouteの内容をログに出力
        if self.logger.level == logging.DEBUG:
            for route in app.routes:
                self.logger.debug(f"loaded webfeature: {route}")

        self.is_running = True
        #uvicorn.run(app, host=self.allow_host, port=self.listen_port, workers=2)
        th = RaiseThread(target=uvicorn.run, kwargs=dict(app=app, host=self.allow_host, port=self.listen_port))
        th.start()
        try:
            if self.gui_mode:
                webbrowser.open(f'http://localhost:{self.listen_port}/gui')
            with open("web.pid", mode="w", encoding="utf-8") as f:
                f.write(str(os.getpid()))
            while self.is_running:
                gevent.sleep(1)
            th.raise_exception()
        except KeyboardInterrupt:
            th.raise_exception()

    def stop(self):
        """
        Webサーバを停止する
        """
        try:
            with open("web.pid", mode="r", encoding="utf-8") as f:
                pid = f.read()
                if pid != "":
                    os.kill(int(pid), signal.CTRL_C_EVENT)
                    self.logger.info(f"Stop bottle web. allow_host={self.allow_host} listen_port={self.listen_port}")
                else:
                    self.logger.warning(f"pid is empty.")
            Path("web.pid").unlink(missing_ok=True)
        except:
            traceback.print_exc()
        finally:
            self.logger.info(f"Exit web. allow_host={self.allow_host} listen_port={self.listen_port}")

class RaiseThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._run = self.run
        self.run = self.set_id_and_run

    def set_id_and_run(self):
        self.id = threading.get_native_id()
        self._run()

    def get_id(self):
        return self.id
        
    def raise_exception(self):
        res = ctypes.pythonapi.PyThreadState_SetAsyncExc(
            ctypes.c_long(self.get_id()), 
            ctypes.py_object(SystemExit)
        )
        if res > 1:
            ctypes.pythonapi.PyThreadState_SetAsyncExc(
                ctypes.c_long(self.get_id()), 
                0
            )
            print('Failure in raising exception')
