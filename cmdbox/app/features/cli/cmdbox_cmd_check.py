from cmdbox.app import common, feature
from cmdbox.app.auth import signin
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import glob
import logging
import pydantic


class CmdCheck(feature.OneshotResultEdgeFeature, validator.Validator):
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
        return 'check'
    
    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        ref_opt = Options.getInstance(self.appcls, self.ver)
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="指定されたコマンドが指定されたグループで実行可能かどうかをチェックします。",
            description_en="Checks whether the specified command can be executed in the specified group.",
            choice=[
                dict(opt="chk_mode", type=Options.T_STR, default=None, required=True, multi=False, hide=False,
                     choice=[], choice_edit=True,
                     callcmd="async () => {"
                            + "const modes = await get_modes();"
                            + "const val = $(\"[name='chk_mode']\").val();"
                            + "$(\"[name='chk_mode']\").empty().append('<option></option>');"
                            + "modes.forEach(mode=>{$(\"[name='chk_mode']\").append('<option value=\"'+mode+'\">'+mode+'</option>');});"
                            + "$(\"[name='chk_mode']\").val(val);"
                            + "}",
                     description_ja="チェック対象のモードを指定します。",
                     description_en="Specifies the mode to be checked."),
                dict(opt="chk_cmd", type=Options.T_STR, default=None, required=True, multi=False, hide=False,
                     choice=[], choice_edit=True,
                     callcmd="async () => {const mode = $(\"[name='chk_mode']\").val();"
                            + "const cmds = await get_cmds(mode);"
                            + "const val = $(\"[name='chk_cmd']\").val();"
                            + "$(\"[name='chk_cmd']\").empty().append('<option></option>');"
                            + "cmds.forEach(cmd=>{$(\"[name='chk_cmd']\").append('<option value=\"'+cmd+'\">'+cmd+'</option>');});"
                            + "$(\"[name='chk_cmd']\").val(val);"
                            + "}",
                     description_ja="チェック対象のコマンドを指定します。",
                     description_en="Specifies the command to be checked."),
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=True, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="signin_file", type=Options.T_FILE, default=f'.{self.ver.__appid__}/user_list.yml', required=True, multi=False, hide=False, choice=None, fileio="in", web="mask",
                     description_ja=f"サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.{self.ver.__appid__}/user_list.yml' を指定します。",
                     description_en=f"Specify a file containing users and passwords with which they can signin.Typically, specify '.{self.ver.__appid__}/user_list.yml'."),
                dict(opt="groups", type=Options.T_STR, default=None, required=False, multi=True, hide=True, choice=None, web="mask",
                     description_ja="`signin_file` を指定した場合に、このユーザーグループに許可されているコマンドリストを返すように指定します。",
                     description_en="Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."),
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
        if not hasattr(self, 'signin_file_data') or self.signin_file_data is None:
            self.signin_file_data = signin.Signin.load_signin_file(args.signin_file, None, self=self, logger=logger)
        scope = signin.get_request_scope()
        user_session = scope["req"].session.get('signin', {}) if scope and scope["req"] is not None else {}
        if not signin.Signin._check_cmd(signin_file_data=self.signin_file_data, user_groups=args.groups, mode=args.chk_mode, cmd=args.chk_cmd,
                                        opt=args.__dict__, user_name="unknown", user_session=user_session, logger=logger,
                                        appcls=self.appcls, ver=self.ver, language=self.language):
            ret = dict(success=dict(data=False))
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, ret, None
        ret = dict(success=dict(data=True))
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: Union[bool, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
