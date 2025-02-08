from cmdbox import version
from cmdbox.app import common, options
from cmdbox.app.feature import Feature
from fastapi import FastAPI, Request, Response, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from pathlib import Path
from PIL import Image
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import requests
import urllib.parse
import uvicorn
import webbrowser


class EdgeStart(Feature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'edge'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'start'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_MEIGHT,
            discription_ja="端末モードを起動します。",
            discription_en="Start Edge mode.",
            choice=[
                dict(opt="endpoint", type="str", default="http://localhost:8081", required=False, multi=False, hide=False, choice=None,
                     discription_ja="エンドポイントのURLを指定します。",
                     discription_en="Specify the URL of the endpoint."),
                dict(opt="auth_type", type="str", default="idpw", required=False, multi=False, hide=False, choice=["noauth", "idpw", "apikey", "oauth2"],
                     discription_ja="エンドポイント接続じの認証方式を指定します。",
                     discription_en="Specifies the authentication method for endpoint connections.",
                     choice_show=dict(idpw=["user","password"],
                                      apikey=["apikey"],
                                      oauth2=["oauth2","oauth2_port","oauth2_client_id","oauth2_client_secret"]),),
                dict(opt="user", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エンドポイントへの接続ユーザーを指定します。",
                     discription_en="Specifies the user connecting to the endpoint."),
                dict(opt="password", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エンドポイントへの接続パスワードを指定します。",
                     discription_en="Specify the password for connecting to the endpoint."),
                dict(opt="apikey", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エンドポイントへの接続するためのAPIKEYを指定します。",
                     discription_en="Specify the APIKEY to connect to the endpoint."),
                dict(opt="oauth2", type="str", default=None, required=False, multi=False, hide=False, choice=["google", "github"],
                     discription_ja="OAuth2認証を使用してエンドポイントに接続します。",
                     discription_en="Connect to the endpoint using OAuth2 authentication."),
                dict(opt="oauth2_port", type="int", default="8091", required=False, multi=False, hide=True, choice=None,
                     discription_ja="OAuth2認証を使用する場合のコールバックポートを指定します。省略した時は `8091` を使用します。",
                     discription_en="Specifies the callback port when OAuth2 authentication is used. If omitted, `8091` is used."),
                dict(opt="oauth2_client_id", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="OAuth2認証を使用するときのクライアントIDを指定します。",
                     discription_en="Specifies the client ID when OAuth2 authentication is used."),
                dict(opt="oauth2_client_secret", type="str", default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="OAuth2認証を使用するときのクライアントシークレットを指定します。",
                     discription_en="Specifies the client secret when OAuth2 authentication is used."),
                dict(opt="data", type="file", default=common.HOME_DIR / f".{self.ver.__appid__}", required=False, multi=False, hide=True, choice=None,
                     discription_ja=f"省略した時は f`$HONE/.{self.ver.__appid__}` を使用します。",
                     discription_en=f"When omitted, f`$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="output_json", short="o", type="file", default="", required=False, multi=False, hide=True, choice=None, fileio="out",
                     discription_ja="処理結果jsonの保存先ファイルを指定。",
                     discription_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type="bool", default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="処理結果jsonファイルを追記保存します。",
                     discription_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type="bool", default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     discription_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type="bool", default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type="int", default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     discription_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
                ]
        )

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        import plyer
        if args.endpoint is None:
            msg = {"warn":f"Please specify the --endpoint option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            plyer.notification.notify(title=self.ver.__title__, message=str(msg), app_icon=str(icon_path))
            return 1, msg, None
        if args.auth_type is None:
            msg = {"warn":f"Please specify the --auth_type option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            plyer.notification.notify(title=self.ver.__title__, message=str(msg), app_icon=str(icon_path))
            return 1, msg, None
        if args.data is None:
            msg = {"warn":f"Please specify the --data option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            plyer.notification.notify(title=self.ver.__title__, message=str(msg), app_icon=str(icon_path))
            return 1, msg, None

        edge_dir = Path(args.data) / '.edge'
        common.mkdirs(edge_dir)
        conf_file = edge_dir / 'edge.conf'
        if conf_file.is_file():
            # 設定ファイルが存在する場合は読み込む
            opt = common.loadopt(conf_file)
            # コマンド引数を優先し設定ファイルの内容をマージ
            args_dict = {o['opt']:args.__dict__[o['opt']] for o in self.get_option().get('choice')}
            for key, val in args_dict.items():
                args_dict[key] = common.getopt(opt, key, preval=args_dict, withset=True)
            # featureの引数を設定
            options.Options.getInstance().load_features_args(args_dict)
            args = argparse.Namespace(**{**args.__dict__, **args_dict})

        # アイコン画像を取得
        icon_path = Path(self.ver.__file__).parent / 'edge' / 'assets' / 'favicon.ico'
        appid = self.ver.__appid__
        title = self.ver.__title__
        if not icon_path.is_file():
            icon_path = Path(version.__file__).parent / 'edge' / 'assets' / 'favicon.ico'
            appid = version.__appid__
            title = version.__title__
        if not icon_path.is_file():
            msg = {"error":f"icon file not found."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            plyer.notification.notify(title=self.ver.__title__, message=str(msg), app_icon=str(icon_path))
            return 1, msg, None
        
        try:
            # サインイン
            status, msg = self.signin(logger, args)
            if status != 0:
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                plyer.notification.notify(title=self.ver.__title__, message=str(msg), app_icon=str(icon_path))
                return status, msg, None
            plyer.notification.notify(title=self.ver.__title__, message=f"Successful connection to the endpoint.", app_icon=str(icon_path))
        except Exception as e:
            msg = {"error":f"{e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            plyer.notification.notify(title=self.ver.__title__, message=str(e)[:256], app_icon=str(icon_path))
            return 1, msg, None

        # 設定ファイルに引数を保存
        opt = {o['opt']:args.__dict__[o['opt']] for o in self.get_option().get('choice')}
        common.saveopt(opt, conf_file)

        # トレイアイコンを起動
        import pystray
        menu = pystray.Menu(
                pystray.MenuItem('Commands',
                    pystray.Menu(
                        pystray.MenuItem('Start', lambda: print('Start')))),
                pystray.MenuItem('Setting', lambda: print('Settings')),
                pystray.MenuItem('Quit', lambda: icon.stop()),)
        icon = pystray.Icon(appid, Image.open(icon_path), title, menu)
        icon.run()

        msg = {"success":"gui complate."}
        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        return 0, msg, None

    def signin(self, logger:logging.Logger, args:argparse.Namespace) -> Tuple[int, Dict[str, Any]]:
        """
        この機能のサインインを行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            Tuple[int, Dict[str, Any]]: 終了コード, 結果
        """
        self.session = requests.Session()
        if args.auth_type == "noauth":
            res = self.session.get(f"{args.endpoint}/gui", allow_redirects=False)
            if res.status_code != 200:
                return res.status_code, dict(warn=f"Access failed. status_code={res.status_code}")
            return 0, dict(success="No auth.")

        # ID/PW認証を使用する場合
        elif args.auth_type == "idpw":
            if args.user is None:
                return 1, dict(warn="Please specify the --user option.")
            if args.password is None:
                return 1, dict(warn="Please specify the --password option.")

            res = self.session.post(f"{args.endpoint}/dosignin/gui",
                                    data={"name":args.user, "password":args.password},
                                    allow_redirects=False)
            if res.status_code != 200:
                return res.status_code, dict(warn=f"Signin failed. status_code={res.status_code}")
            return 0, dict(success="Signin success.")

        # APIKEY認証を使用する場合
        elif args.auth_type == "apikey":
            if args.apikey is None:
                return 1, dict(warn="Please specify the --apikey option.")
            headers = {"Authorization": f"Bearer {args.apikey}"}
            res = self.session.post(f"{args.endpoint}/gui",
                                    headers=headers,
                                    allow_redirects=False)
            if res.status_code != 200:
                return res.status_code, dict(warn=f"Signin failed. status_code={res.status_code}")
            return 0, dict(success="Signin success.")

        # OAuth2認証を使用する場合
        elif args.auth_type == "oauth2":
            # Google OAuth2を使用する場合
            if args.oauth2 == "google":
                if args.oauth2_client_id is None:
                    return 1, dict(warn="Please specify the --oauth2_client_id option.")
                if args.oauth2_client_secret is None:
                    return 1, dict(warn="Please specify the --oauth2_client_secret option.")
                redirect_uri = f'http://localhost:{args.oauth2_port}/oauth2/google/callback'
                # OAuth2認証のコールバックを受けるFastAPIサーバーを起動
                fastapi = FastAPI()
                @fastapi.get('/oauth2/google/callback')
                async def oauth2_google_callback(req:Request):
                    if req.query_params['state'] != 'edge':
                        return dict(warn="Invalid state.")
                    # 受信したcodeを使用してエンドポイントにリクエスト
                    req = self.session.get(f"{args.endpoint}/oauth2/google/callback", params=req.query_params)
                    if req.status_code != 200:
                        return dict(warn=f"Signin failed. status_code={req.status_code}")
                    return dict(success="Signin success.")
                uvicorn.run(fastapi, host='localhost', port=args.oauth2_port)

                # OAuth2認証のリクエストを送信
                data = {'scope': 'email',
                        'access_type': 'offline',
                        'response_type': 'code',
                        'redirect_uri': redirect_uri,
                        'client_id': args.oauth2_client_id,
                        'state': 'edge'}
                query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
                webbrowser.open(f'https://accounts.google.com/o/oauth2/auth?{query}')

                return 0, dict(success="Signin success.")
            
            # GitHub OAuth2を使用する場合
            elif args.oauth2 == "github":
                if args.oauth2_client_id is None:
                    return 1, dict(warn="Please specify the --oauth2_client_id option.")
                if args.oauth2_client_secret is None:
                    return 1, dict(warn="Please specify the --oauth2_client_secret option.")

                redirect_uri = f'http://localhost:{args.oauth2_port}/oauth2/github/callback'
                # OAuth2認証のコールバックを受けるFastAPIサーバーを起動
                fastapi = FastAPI()
                @fastapi.get('/oauth2/github/callback')
                async def oauth2_github_callback(req:Request):
                    if req.query_params['state'] != 'edge':
                        return dict(warn="Invalid state.")
                    # 受信したcodeを使用してエンドポイントにリクエスト
                    req = self.session.get(f"{args.endpoint}/oauth2/github/callback", params=req.query_params)
                    if req.status_code != 200:
                        return dict(warn=f"Signin failed. status_code={req.status_code}")
                    return dict(success="Signin success.")
                uvicorn.run(fastapi, host='localhost', port=args.oauth2_port)

                # OAuth2認証のリクエストを送信
                data = {'scope': 'user',
                        'access_type': 'offline',
                        'response_type': 'code',
                        'redirect_uri': redirect_uri,
                        'client_id': args.oauth2_client_id,
                        'state': 'edge'}
                query = '&'.join([f'{k}={urllib.parse.quote(v)}' for k, v in data.items()])
                webbrowser.open(f'https://github.com/login/oauth/authorize?{query}')

        return 1, dict(warn="unsupported auth_type.")
