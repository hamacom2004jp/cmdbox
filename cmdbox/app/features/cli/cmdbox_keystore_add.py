from cmdbox.app import common, client, feature, web
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.features.cli import cmdbox_client_file_download
from cmdbox.app.options import Options
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import jwt
import pydantic
import uuid


class KeystoreAdd(feature.OneshotResultEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language:str=None):
        super().__init__(appcls, ver, language)
        self.file_download = cmdbox_client_file_download.ClientFileDownload(appcls, ver, language)

    def get_mode(self) -> Union[str, List[str]]:
        return 'keystore'

    def get_cmd(self) -> str:
        return 'add'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="キー情報をキーストアへ追加します。",
            description_en="Add a key information to keystore.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                     description_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HOME/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HOME/.{self.ver.__appid__}` is used."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定します。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="key_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="キーの名前で識別しやすい名称。",
                     description_en="Readable key name."),
                dict(opt="key_type", type=Options.T_STR, default="apikey", required=True, multi=False, hide=False,
                     choice=["apikey", "signkey", "enckey", "cacert"],
                     choice_show=dict(
                        apikey=["key_value", "claims"],
                        signkey=["sign_key", "sign_cert", "key_pass"],
                        enckey=["enc_key"],
                        cacert=["ca_cert"],
                     ),
                     description_ja="登録するキー情報の種類を指定します。",
                     description_en="Specify the type of key information to register."),
                dict(opt="key_id", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="キーのIDですべてのキーの一意な値。省略した場合自動生成します。",
                     description_en="Unique key identifier across all keys. If omitted, it will be auto-generated."),
                dict(opt="key_provider", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja=f"キーの発行者で通常ドメイン名などを指定。省略した場合 `{self.ver.__appid__}` を使用します。",
                     description_en=f"Key provider, usually a domain name. If omitted, `{self.ver.__appid__}` is used."),
                dict(opt="key_value", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="キーの実体。省略した場合、現在のユーザーでjwtトークンを自動生成します。",
                     description_en="Actual key value. If omitted, a JWT token will be auto-generated for the current user."),
                dict(opt="key_usage", type=Options.T_STR, default=None, required=True, multi=True, hide=False, choice=[],
                     choice_edit=True, choice_fn=self.list_svcmd,
                     description_ja="キーを使用するコマンド（get_svcmd相当）を指定。複数指定可能。",
                     description_en="Target commands (get_svcmd values) that can use this key. Multiple values allowed."),
                dict(opt="scope", type=Options.T_STR, default="client", required=False, multi=False, hide=False, choice=["client", "current", "server"],
                     description_ja="スコープを指定します。`client` はクライアント側、`server` はサーバー側です。`current` は実行時ディレクトリです。",
                     description_en="Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory.",),
                dict(opt="fwpath", type=Options.T_FILE, default=None, required=True, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが範囲外であるかどうかを判定するパスを指定します。このパスの配下でない場合エラーにします。",
                     description_en="Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error.",),
                dict(opt="rjpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが要求されたパスにマッチする場合、アクセスが拒否されます。正規表現として解釈します。",
                     description_en="If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."),
                dict(opt="sign_key", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="公開鍵証明書の秘密鍵のファイル。",
                     description_en="Private key file for the public key certificate."),
                dict(opt="sign_cert", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="公開鍵証明書のファイル。",
                     description_en="Public key certificate file."),
                dict(opt="key_pass", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="秘密鍵のパスワード。",
                     description_en="Password for the private key."),
                dict(opt="enc_key", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="BASE64エンコードされた暗号キーの内容。",
                     description_en="Base64-encoded encryption key content."),
                dict(opt="ca_cert", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="CA証明書のファイル。",
                     description_en="CA certificate file."),
                dict(opt="key_period_start", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="キーが使用可能になる日時。省略時は即時有効。",
                     description_en="Datetime when the key becomes valid. If omitted, effective immediately."),
                dict(opt="key_period_end", type=Options.T_DATETIME, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="キーが使用不可になる日時。省略時は期限なし。",
                     description_en="Datetime when the key expires. If omitted, no expiration."),
                dict(opt="groups", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="キーが利用可能なグループ。複数指定可能。",
                     description_en="Groups that can use this key. Multiple values allowed."),
                dict(opt="owner", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="キーの所有者となるユーザー名。複数指定可能。",
                     description_en="Owner user names of this key. Multiple values allowed."),
                dict(opt="claims", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="キーが要求する項目と値。",
                     description_en="Claim requirements for this key."),
                dict(opt="signin_file", type=Options.T_FILE, default=f'.{self.ver.__appid__}/user_list.yml', required=True, multi=False, hide=True, choice=None, fileio="in", web="mask",
                     description_ja=f"サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.{self.ver.__appid__}/user_list.yml' を指定します。",
                     description_en=f"Specify a file containing users and passwords with which they can signin.Typically, specify '.{self.ver.__appid__}/user_list.yml'."),
            ]
        )

    def list_svcmd(self, o, webmode, opt) -> List[str]:
        _options = Options.getInstance(self.appcls, self.ver)
        modes = _options.get_mode_keys()
        svcmds = []
        for mode in modes:
            if not mode: continue
            cmds = _options.get_cmd_keys(mode)
            for cmd in cmds:
                if not cmd: continue
                svcmds.append(f"{mode}_{cmd}")
        svcmds = sorted(svcmds)
        return svcmds

    @validator.async_apprun_check
    async def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        key_type = args.key_type if hasattr(args, 'key_type') and args.key_type else 'apikey'

        if key_type == 'signkey':
            if not args.sign_key or not args.sign_cert:
                msg = dict(warn="Please specify --sign_key and --sign_cert when --key_type signkey.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            # sign_keyファイルの取得
            args.svpath = args.sign_key
            st, msg, cl = self.file_download.apprun(logger, args, tm, pf)
            if st != self.RESP_SUCCESS:
                return st, msg, cl
            success = msg.get("success", None)
            args.sign_key = success.get("data", None) if success else None
            # sign_certファイルの取得
            args.svpath = args.sign_cert
            st, msg, cl = self.file_download.apprun(logger, args, tm, pf)
            if st != self.RESP_SUCCESS:
                return st, msg, cl
            success = msg.get("success", None)
            args.sign_cert = success.get("data", None) if success else None
        elif key_type == 'enckey':
            if not args.enc_key:
                msg = dict(warn="Please specify --enc_key when --key_type enckey.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
        elif key_type == 'cacert':
            if not args.ca_cert:
                msg = dict(warn="Please specify --ca_cert when --key_type cacert.")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            # ca_certファイルの取得
            args.svpath = args.ca_cert
            st, msg, cl = self.file_download.apprun(logger, args, tm, pf)
            if st != self.RESP_SUCCESS:
                return st, msg, cl
            success = msg.get("success", None)
            args.ca_cert = success.get("data", None) if success else None

        if hasattr(args, 'key_id') and args.key_id is None:
            args.key_id = str(uuid.uuid4())
        if hasattr(args, 'key_provider') and args.key_provider is None:
            args.key_provider = self.ver.__appid__
        if key_type == 'apikey' and hasattr(args, 'key_value') and args.key_value is None:
            w = web.Web.getInstance(logger, args.data, appcls=self.appcls, ver=self.ver,
                        redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout,
                        signin_file=args.signin_file)
            claims = args.claims if hasattr(args, 'claims') and type(args.claims) is dict else {}
            claims['name'] = args.signin_user if hasattr(args, 'signin_user') else ''
            claims['groups'] = args.signin_groups if hasattr(args, 'signin_groups') else []
            claims['apikey_name'] = args.key_name
            args.key_value = jwt.encode(claims, w.signin.gen_jwt_privatekey, algorithm=w.signin.gen_jwt_algorithm)

        key_usage = [v for v in args.key_usage if v] if isinstance(args.key_usage, list) else args.key_usage
        groups = [v for v in args.groups if v] if hasattr(args, 'groups') and isinstance(args.groups, list) else args.groups if hasattr(args, 'groups') else None
        owner = [v for v in args.owner if v] if hasattr(args, 'owner') and isinstance(args.owner, list) and args.owner else []
        if hasattr(args, 'signin_user') and args.signin_user and args.signin_user not in owner:
            owner.append(args.signin_user)
        if not hasattr(args, 'claims') or not isinstance(args.claims, dict):
            args.claims = {}
        payload = dict(
            key_id=args.key_id,
            key_name=args.key_name,
            key_provider=args.key_provider if hasattr(args, 'key_provider') else None,
            key_type=key_type,
            key_usage=key_usage,
            key_value=args.key_value,
            sign_key=args.sign_key,
            sign_cert=args.sign_cert,
            key_pass=args.key_pass if hasattr(args, 'key_pass') else None,
            enc_key=args.enc_key if hasattr(args, 'enc_key') else None,
            ca_cert=args.ca_cert,
            key_period_start=str(args.key_period_start) if hasattr(args, 'key_period_start') and args.key_period_start is not None else None,
            key_period_end=str(args.key_period_end) if hasattr(args, 'key_period_end') and args.key_period_end is not None else None,
            groups=groups,
            owner=owner,
            claims=args.claims,
            description=args.description if hasattr(args, 'description') else None
        )
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = await cl.redis_cli.asend_cmd(self.get_svcmd(), [payload_b64],
                                           retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            key_id: Union[str, None] = pydantic.Field(default=None, description="キーID")
            key_name: Union[str, None] = pydantic.Field(default=None, description="キー名")
            msg: Union[str, None] = pydantic.Field(default=None, description="処理結果メッセージ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            keystore_dir = data_dir / '.keystore'
            keystore_dir.mkdir(parents=True, exist_ok=True)

            key_id = payload.get('key_id')
            key_name = payload.get('key_name')
            key_path = keystore_dir / f"key_{key_id}_{key_name}.json"

            if key_path.exists():
                result = dict(warn=f"Key file '{str(key_path)}' already exists.")
                redis_cli.rpush(reskey, result)
                return self.RESP_WARN

            key_data = dict(
                key_id=key_id,
                key_name=key_name,
                key_provider=payload.get('key_provider'),
                key_type=payload.get('key_type'),
                key_usage=payload.get('key_usage') if payload.get('key_usage') else [],
                key_value=payload.get('key_value'),
                sign_key=payload.get('sign_key'),
                sign_cert=payload.get('sign_cert'),
                key_pass=payload.get('key_pass'),
                enc_key=payload.get('enc_key'),
                ca_cert=payload.get('ca_cert'),
                key_period_start=payload.get('key_period_start'),
                key_period_end=payload.get('key_period_end'),
                groups=payload.get('groups') if payload.get('groups') else [],
                owner=payload.get('owner') if payload.get('owner') else [],
                claims=payload.get('claims') if payload.get('claims') else {},
                description=payload.get('description') if payload.get('description') else None,
                created_at=datetime.utcnow().isoformat() + 'Z'
            )
            common.save_file(key_path, lambda f: json.dump(key_data, f, indent=4), encoding='utf-8', nolock=False)

            result = dict(success=dict(
                key_id=key_id,
                key_name=key_name,
                msg=f"Keystore entry saved to '{key_path.name}'.",
            ))
            redis_cli.rpush(reskey, result)
            return self.RESP_SUCCESS
        except Exception as e:
            result = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, result)
            return self.RESP_WARN
