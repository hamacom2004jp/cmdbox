from cmdbox.app import common, web
from cmdbox.app.feature import Feature
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class WebApikeyDel(Feature):
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
        return 'apikey_del'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            type="str", default=None, required=False, multi=False, hide=False, use_redis=self.USE_REDIS_MEIGHT,
            discription_ja="WebモードのユーザーのApiKeyを削除します。",
            discription_en="Del an ApiKey for a user in Web mode.",
            choice=[
                dict(opt="host", type="str", default=self.default_host, required=False, multi=False, hide=True, choice=None,
                     discription_ja="Redisサーバーのサービスホストを指定します。",
                     discription_en="Specify the service host of the Redis server."),
                dict(opt="port", type="int", default=self.default_port, required=False, multi=False, hide=True, choice=None,
                     discription_ja="Redisサーバーのサービスポートを指定します。",
                     discription_en="Specify the service port of the Redis server."),
                dict(opt="password", type="str", default=self.default_pass, required=False, multi=False, hide=True, choice=None,
                     discription_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     discription_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type="str", default="server", required=False, multi=False, hide=True, choice=None,
                     discription_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     discription_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="data", type="file", default=common.HOME_DIR / f".{self.ver.__appid__}", required=False, multi=False, hide=False, choice=None,
                     discription_ja="省略した時は `$HONE/.cmdbox` を使用します。",
                     discription_en="When omitted, `$HONE/.cmdbox` is used."),
                dict(opt="user_name", type="str", default=None, required=True, multi=False, hide=False, choice=None,
                     discription_ja="ユーザー名を指定します。他のユーザーと重複しないようにしてください。",
                     discription_en="Specify a user name. Do not duplicate other users."),
                dict(opt="apikey_name", type="str", default=None, required=True, multi=False, hide=False, choice=None,
                     discription_ja="このユーザーのApiKey名を指定します。",
                     discription_en="Specify the ApiKey name for this user."),
                dict(opt="signin_file", type="file", default=None, required=True, multi=False, hide=False, choice=None,
                     discription_ja="サインイン可能なユーザーとパスワードを記載したファイルを指定します。省略した時は認証を要求しません。",
                     discription_en="Specify a file containing users and passwords with which they can signin. If omitted, no authentication is required."),
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
        if args.data is None:
            msg = {"warn":f"Please specify the --data option."}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        w = None
        try:
            w = web.Web(logger, Path(args.data), appcls=self.appcls, ver=self.ver,
                        redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                        signin_file=args.signin_file)
            user = dict(name=args.user_name, apikey_name=args.apikey_name)
            w.apikey_del(user)
            msg = {"success": {"msg":f"User ApiKey deleted. user_name={args.user_name} apikey_name={args.apikey_name}"}}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 0, msg, w
        except Exception as e:
            msg = {"warn":f"{e}"}
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, w
