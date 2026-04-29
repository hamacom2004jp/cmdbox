from cmdbox.app import common, feature
from cmdbox.app.auth import signin
from cmdbox.app.commons import validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import glob
import logging


class CmdLoad(feature.OneshotResultEdgeFeature, validator.Validator):
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
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="データフォルダ配下のコマンドの内容を取得します。",
            description_en="Obtains the contents of commands under the data folder.",
            choice=[
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=True, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="signin_file", type=Options.T_FILE, default=f'.{self.ver.__appid__}/user_list.yml', required=True, multi=False, hide=False, choice=None, fileio="in", web="mask",
                     description_ja=f"サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.{self.ver.__appid__}/user_list.yml' を指定します。",
                     description_en=f"Specify a file containing users and passwords with which they can signin.Typically, specify '.{self.ver.__appid__}/user_list.yml'."),
                dict(opt="groups", type=Options.T_STR, default=None, required=False, multi=True, hide=True, choice=None, web="mask",
                     description_ja="`signin_file` を指定した場合に、このユーザーグループに許可されているコマンドリストを返すように指定します。",
                     description_en="Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."),
                dict(opt="cmd_title", type=Options.T_STR, default=None, required=True, multi=False, hide=False,
                     choice=[], choice_edit=True,
                     callcmd="async () => {await cmdbox.callcmd('cmd','list',{},"
                            + "(res)=>{const val = $(\"[name='cmd_title']\").val();"
                            + "$(\"[name='cmd_title']\").empty().append('<option></option>');"
                            + "res['data'].forEach(elm=>{$(\"[name='cmd_title']\").append('<option value=\"'+elm[\"title\"]+'\">'+elm[\"title\"]+'</option>');});"
                            + "$(\"[name='cmd_title']\").val(val);"
                            + "},$(\"[name='cmd_title']\").val(),'cmd_title');"
                            + "}",
                     description_ja=f"読込みたいコマンド名を指定します。",
                     description_en=f"Specify the name of the command to be read."),
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
        st, msg, cl = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, cl

        if not hasattr(self, 'signin_file_data') or self.signin_file_data is None:
            self.signin_file_data = signin.Signin.load_signin_file(args.signin_file, None, self=self, logger=logger)
        opt_path = Path(args.data) / ".cmds" / f"cmd-{args.cmd_title}.json"
        opt = common.loadopt(opt_path, True)
        if not opt or 'cmd' not in opt or 'mode' not in opt:
            ret = dict(warn=f"Command not found: '{args.cmd_title}'")
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, ret, None
        if not signin.Signin._check_cmd(self.signin_file_data, args.groups, opt['mode'], opt['cmd'], args.__dict__, "unknown", logger,
                                        self.appcls, self.ver, self.language):
            ret = dict(warn=f"You do not have permission to execute this command.")
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, ret, None
        ret = dict(success=opt)

        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None

        return self.RESP_SUCCESS, ret, None
