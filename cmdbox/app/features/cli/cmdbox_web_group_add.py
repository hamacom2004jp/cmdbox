from cmdbox.app import common, feature, web
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class WebGroupAdd(feature.UnsupportEdgeFeature):
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
        return 'group_add'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=False,
            discription_ja="Webモードのグループを追加します。",
            discription_en="Add a group in Web mode.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのサービスホストを指定します。",
                     discription_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのサービスポートを指定します。",
                     discription_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_STR, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     discription_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     discription_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="svname", type=Options.T_STR, default="server", required=True, multi=False, hide=True, choice=None, web="readonly",
                     discription_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     discription_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="data", type=Options.T_FILE, default=common.HOME_DIR / f".{self.ver.__appid__}", required=False, multi=False, hide=False, choice=None,
                     discription_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     discription_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="group_id", type=Options.T_INT, default=None, required=True, multi=False, hide=False, choice=None,
                     discription_ja="グループIDを指定します。他のグループと重複しないようにしてください。",
                     discription_en="Specify the group ID. Do not duplicate other groups."),
                dict(opt="group_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     discription_ja="グループ名を指定します。他のグループと重複しないようにしてください。",
                     discription_en="Specify a group name. Do not duplicate other groups."),
                dict(opt="group_parent", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="親グループ名を指定します。",
                     discription_en="Specifies the parent group name."),
                dict(opt="signin_file", type=Options.T_FILE, default=None, required=True, multi=False, hide=False, choice=None,
                     discription_ja="サインイン可能なユーザーとパスワードを記載したファイルを指定します。省略した時は認証を要求しません。",
                     discription_en="Specify a file containing users and passwords with which they can signin. If omitted, no authentication is required."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     discription_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     discription_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     discription_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     discription_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

    @Options.audit(audit_type=Options.AT_EVENT)
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
            w = web.Web(logger, Path(args.data), appcls=self.appcls, ver=self.ver,
                        redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname,
                        signin_file=args.signin_file)
            group = dict(gid=args.group_id, name=args.group_name, parent=args.group_parent)
            w.group_add(group)
            msg = dict(success=f"group ID {args.group_id} has been added.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 0, msg, w
        except Exception as e:
            msg = dict(warn=f"{e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, w
