from cmdbox.app import common, feature, web
from cmdbox.app.auth import signin
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pydantic
import pyotp
import json


class WebTotpValid(feature.UnsupportEdgeFeature, validator.Validator):
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
        return 'totp_valid'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False, use_agent=False,
            description_ja="Webモードのユーザーの多要素認証コードを検証します。",
            description_en="Validate a multi-factor authentication code for a user in Web mode.",
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
                     description_ja="ユーザー名を指定します。",
                     description_en="Specify a user name."),
                dict(opt="totp_code", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="検証するTOTPコード(6桁の数字)を指定します。",
                     description_en="Specify the TOTP code (6 digits) to validate."),
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
            # TOTPコードの検証を行う
            st, msg, _ = self.valid_info(client_data, args.user_name, uid, user_name, args.totp_code)
            if st != self.RESP_SUCCESS:
                return st, msg, None
            common.print_format(msg, args.format, tm, pf=pf)
            return self.RESP_SUCCESS, msg, None
        except Exception as e:
            msg = dict(warn=f"{e}")
            common.print_format(msg, args.format, tm, pf=pf)
            return self.RESP_WARN, msg, None

    def output_schema(self) -> type:
        class TOTPRecord(resdata.Base):
            msg: Union[str, None] = pydantic.Field(default=None, description="処理結果のメッセージ")
        class Data(resdata.Data):
            data: Union[TOTPRecord, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def valid_info(self, client_data:Path, arg_user_name:str, uid:str, user_name:str, totp_code:str):
        if user_name != arg_user_name:
            return self.RESP_WARN, dict(warn="User name does not match."), None

        # TOTP情報ファイルのパスを取得
        totp_path = client_data / ".totp" / f"{common.safe_fname(uid)}_{common.safe_fname(user_name)}.json"
        if not totp_path.exists():
            return self.RESP_WARN, dict(warn="TOTP is not configured for this user."), None

        # TOTP情報を読み込む
        totp_data = common.load_file(totp_path, lambda f: json.load(f), 'r', encoding='utf-8')
        secret = totp_data.get('secret')
        if not secret:
            return self.RESP_WARN, dict(warn="TOTP secret not found."), None

        name = totp_data.get('user_name', user_name)
        interval = totp_data.get('interval', 30)
        issuer = totp_data.get('issuer_name', self.ver.__title__)
        # TOTPコードを検証
        totp = pyotp.TOTP(secret, name=name, issuer=issuer, interval=interval)
        if not totp.verify(totp_code):
            return self.RESP_WARN, dict(warn="TOTP code is invalid."), None

        # 検証成功：verifyをTrueに更新して保存
        if not totp_data.get('verify', False):
            totp_data['verify'] = True
            common.save_file(totp_path, lambda f: json.dump(totp_data, f, indent=4, ensure_ascii=False),
                                encoding='utf-8', nolock=False)

        msg = dict(success=dict(data=dict(msg=f"TOTP verification successful. user_name={user_name}")))
        return self.RESP_SUCCESS, msg, None