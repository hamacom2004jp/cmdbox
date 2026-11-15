from cmdbox.app import common, feature, web
from cmdbox.app.auth import signin
from cmdbox.app.commons import convert, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pydantic
import pyotp
import qrcode
import json


class WebTotpSave(feature.UnsupportEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'web'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'totp_save'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=False,
            description_ja="Webモードのユーザーの多要素認証を追加します。",
            description_en="Add a multi-factor authentication for a user in Web mode.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HOME/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HOME/.{self.ver.__appid__}` is used."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定します。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="user_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="ユーザー名を指定します。パスワード管理しているユーザーのみ指定可能です。",
                     description_en="Specify a user name. Do not duplicate other users."),
                dict(opt="user_pass", type=Options.T_PASSWD, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="ユーザーの現在のパスワードを指定します。",
                     description_en="Specify the user password."),
                dict(opt="signin_file", type=Options.T_FILE, default=f'.{self.ver.__appid__}/user_list.yml', required=True, multi=False, hide=False, choice=None, fileio="in", web="mask",
                     description_ja=f"サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.{self.ver.__appid__}/user_list.yml' を指定します。",
                     description_en=f"Specify a file containing users and passwords with which they can signin.Typically, specify '.{self.ver.__appid__}/user_list.yml'."),
            ]
        )

    @validator.apprun_check
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
        _web = None
        try:
            if args.client_data is None:
                return self.RESP_WARN, dict(warn="Client data is not provided."), None
            client_data = Path(args.client_data)
            _web = web.Web.getInstance(logger, client_data, appcls=self.appcls, ver=self.ver,
                        redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout,
                        signin_file=args.signin_file)
            scope = signin.get_request_scope()
            req = scope["req"] if scope["req"] is not None else scope["websocket"]
            if req is None:
                return self.RESP_WARN, dict(warn="HTTPRequest is None."), None
            s = _web.signin.check_signin(req=req, res=scope["res"])
            if s: return self.RESP_WARN, dict(warn="User is not signed in."), None
            if "signin" not in req.session or req.session["signin"] is None or "name" not in req.session["signin"]:
                return self.RESP_WARN, dict(warn="User is not signed in."), None
            uid = req.session["signin"]["uid"]
            user_name = req.session["signin"]["name"]
            user_pass = req.session["signin"]["password"]
            hash_alg = req.session["signin"]["hash"]
            if user_name != args.user_name:
                return self.RESP_WARN, dict(warn="User name does not match."), None
            if hash_alg is None or user_pass in ['oauth2', 'saml']:
                return self.RESP_WARN, dict(warn="User password is not set or uses external authentication."), None
            hashed_passwd = args.user_pass
            if hash_alg != 'plain':
                hashed_passwd = common.hash_password(args.user_pass, hash_alg)
            if hashed_passwd != user_pass:
                return self.RESP_WARN, dict(warn="User password does not match."), None

            # TOTP用のシークレットキーを生成
            secret = pyotp.random_base32()
            totp = pyotp.TOTP(secret, name=args.user_name, issuer=self.ver.__title__, interval=30)
            uri = totp.provisioning_uri(name=args.user_name, issuer_name=self.ver.__title__)

            # QRコードを生成
            img = qrcode.make(uri)
            img_b64 = convert.bytes2b64str(convert.img2byte(img, format="PNG"))

            # TOTP情報を保存するパスを作成し保存
            totp_path = client_data / ".totp" / f"{common.safe_fname(uid)}_{common.safe_fname(user_name)}.json"
            totp_path.parent.mkdir(parents=True, exist_ok=True)
            totp_data = dict(uid=uid, user_name=user_name, secret=secret, uri=uri,
                             issuer_name=self.ver.__title__, interval=30, verify=False)
            common.save_file(totp_path, lambda f: json.dump(totp_data, f, indent=4, ensure_ascii=False),
                             encoding='utf-8', nolock=False)
            msg = dict(success=dict(data=dict(msg=f"User TOTP saved. user_name={args.user_name}",
                                              qr=f"data:image/png;base64,{img_b64}")))
            common.print_format(msg, args.format, tm, pf=pf)
            return self.RESP_SUCCESS, msg, None
        except Exception as e:
            msg = dict(warn=f"{e}")
            common.print_format(msg, args.format, tm, pf=pf)
            return self.RESP_WARN, msg, None

    def output_schema(self) -> type:
        class TOTPRecord(resdata.Base):
            msg: Union[str, None] = pydantic.Field(default=None, description="処理結果のメッセージ")
            qr: Union[str, None] = pydantic.Field(default=None, description="QRコードのBase64文字列")
        class Data(resdata.Data):
            data: Union[TOTPRecord, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
