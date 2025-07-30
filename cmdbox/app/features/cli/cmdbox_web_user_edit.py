from cmdbox.app import common, feature, web
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class WebUserEdit(feature.UnsupportEdgeFeature):
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
        return 'user_edit'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False,
            description_ja="Webモードのユーザーを編集します。",
            description_en="Edit users in Web mode.",
            choice=[
                dict(opt="user_id", type=Options.T_INT, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="ユーザーIDを指定します。",
                     description_en="Specify the user ID."),
                dict(opt="user_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="ユーザー名を指定します。他のユーザーと重複しないようにしてください。",
                     description_en="Specify a user name. Do not duplicate other users."),
                dict(opt="user_pass", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="ユーザーパスワードを指定します。",
                     description_en="Specify the user password."),
                dict(opt="user_pass_hash", type=Options.T_STR, default='sha1', required=False, multi=False, hide=False, choice=['oauth2', 'saml', 'plain', 'md5', 'sha1', 'sha256'],
                     description_ja="ユーザーパスワードのハッシュアルゴリズムを指定します。",
                     description_en="Specifies the hash algorithm for user passwords."),
                dict(opt="user_email", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="ユーザーメールアドレスを指定します。 `user_pass_hash` が `oauth2` 又は `saml` の時は必須です。",
                     description_en="Specify the user email. Required when `user_pass_hash` is `oauth2` or `saml`."),
                dict(opt="user_group", type=Options.T_STR, default=None, required=True, multi=True, hide=False, choice=None,
                     description_ja="ユーザーが所属するグループを指定します。",
                     description_en="Specifies the groups to which the user belongs."),
                dict(opt="signin_file", type=Options.T_FILE, default=f".{self.ver.__appid__}/user_list.yml", required=True, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="サインイン可能なユーザーとパスワードを記載したファイルを指定します。省略した時は認証を要求しません。",
                     description_en="Specify a file containing users and passwords with which they can signin. If omitted, no authentication is required."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
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
            msg = dict(warn=f"Please specify the --data option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        w = None
        try:
            w = web.Web(logger, self.default_data, appcls=self.appcls, ver=self.ver,
                        redis_host=self.default_host, redis_port=self.default_port, redis_password=self.default_pass, svname=self.default_svname,
                        signin_file=args.signin_file)
            user = dict(uid=args.user_id, name=args.user_name, password=args.user_pass, hash=args.user_pass_hash,
                        email=args.user_email, groups=args.user_group)
            w.user_edit(user)
            msg = dict(success=f"User ID {args.user_id} has been edited.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 0, msg, w
        except Exception as e:
            msg = dict(warn=f"{e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, w
