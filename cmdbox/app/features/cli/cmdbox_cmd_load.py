from cmdbox.app import common, feature
from cmdbox.app.auth import signin
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import glob
import logging


class CmdLoad(feature.OneshotResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'cmd'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'load'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False,
            discription_ja="データフォルダ配下のコマンドの内容を取得します。",
            discription_en="Obtains the contents of commands under the data folder.",
            choice=[
                dict(opt="data", type=Options.T_FILE, default=self.default_data, required=True, multi=False, hide=False, choice=None,
                     discription_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     discription_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="title", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja=f"読込みたいコマンド名を指定します。",
                     discription_en=f"Specify the name of the command to be read."),
                dict(opt="signin_file", type=Options.T_FILE, default=f".{self.ver.__appid__}/user_list.yml", required=False, multi=False, hide=True, choice=None,
                     discription_ja="サインイン可能なユーザーとパスワードを記載したファイルを指定します。",
                     discription_en="Specify a file containing users and passwords with which they can signin."),
                dict(opt="groups", type=Options.T_STR, default=None, required=False, multi=True, hide=True, choice=None,
                     discription_ja="`signin_file` を指定した場合に、このユーザーグループに許可されているコマンドリストを返すように指定します。",
                     discription_en="Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     discription_ja="処理結果jsonの保存先ファイルを指定。",
                     discription_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     discription_ja="処理結果jsonファイルを追記保存します。",
                     discription_en="Save the processing result json file by appending."),
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
        if args.title is None:
            msg = dict(warn=f"Please specify the --title option.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return 1, msg, None
        if not hasattr(self, 'signin_file_data') or self.signin_file_data is None:
            self.signin_file_data = signin.Signin.load_signin_file(args.signin_file, None)
        opt_path = Path(args.data) / ".cmds" / f"cmd-{args.title}.json"
        opt = common.loadopt(opt_path, True)
        ret = dict(success=opt)

        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return 1, ret, None

        return 0, ret, None
