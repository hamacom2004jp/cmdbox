from cmdbox.app import common, feature
from cmdbox.app.auth import signin
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pydantic
import typing


def _annotation_to_str(annotation) -> Any:
    """型アノテーションをシンプルな文字列またはネスト辞書に変換します。"""
    origin = getattr(annotation, '__origin__', None)
    args = getattr(annotation, '__args__', ()) or ()
    if origin is typing.Union:
        non_none = [a for a in args if a is not type(None)]
        has_none = type(None) in args
        if len(non_none) == 1:
            inner = _annotation_to_str(non_none[0])
            if isinstance(inner, dict):
                return inner
            return f"{inner} | null" if has_none else inner
        parts = [str(_annotation_to_str(a)) for a in non_none]
        joined = " | ".join(parts)
        return f"{joined} | null" if has_none else joined
    if origin is list:
        if args:
            return f"list[{_annotation_to_str(args[0])}]"
        return "list"
    if isinstance(annotation, type) and issubclass(annotation, pydantic.BaseModel):
        return _simplify_model_schema(annotation)
    return getattr(annotation, '__name__', str(annotation))


def _simplify_model_schema(cls: type) -> Dict[str, Any]:
    """pydanticモデルからフィールド名と型のシンプルな構造を返します。"""
    result = {}
    for field_name, field_info in cls.model_fields.items():
        result[field_name] = _annotation_to_str(field_info.annotation)
    return result


class CmdInfo(feature.OneshotResultEdgeFeature, validator.Validator):
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
        return 'info'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="指定したコマンドの指定可能な引数と実行結果のスキーマを返します。",
            description_en="Returns the list of arguments and the output schema for the specified command.",
            choice=[
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=True, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
                dict(opt="signin_file", type=Options.T_FILE, default=f'.{self.ver.__appid__}/user_list.yml', required=True, multi=False, hide=False, choice=None, fileio="in", web="mask",
                     description_ja=f"サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.{self.ver.__appid__}/user_list.yml' を指定します。",
                     description_en=f"Specify a file containing users and passwords with which they can signin. Typically, specify '.{self.ver.__appid__}/user_list.yml'."),
                dict(opt="groups", type=Options.T_STR, default=None, required=False, multi=True, hide=True, choice=None, web="mask",
                     description_ja="`signin_file` を指定した場合に、このユーザーグループに許可されているコマンドリストを返すように指定します。",
                     description_en="Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."),
                dict(opt="cmd_title", type=Options.T_STR, default=None, required=False, multi=False, hide=False,
                     choice=[], choice_edit=True,
                     callcmd="async () => {await cmdbox.callcmd('cmd','list',{},"
                            + "(res)=>{const val = $(\"[name='cmd_title']\").val();"
                            + "$(\"[name='cmd_title']\").empty().append('<option></option>');"
                            + "res['data'].forEach(elm=>{$(\"[name='cmd_title']\").append('<option value=\"'+elm[\"title\"]+'\">'+elm[\"title\"]+'</option>');});"
                            + "$(\"[name='cmd_title']\").val(val);"
                            + "},$(\"[name='cmd_title']\").val(),'cmd_title');"
                            + "}",
                     description_ja="情報を取得したいコマンド名を指定します。`target_mode` と `target_cmd` の代わりに指定できます。",
                     description_en="Specify the name of the command to get information for. Can be used instead of `target_mode` and `target_cmd`."),
                dict(opt="target_mode", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="`cmd_title` の代わりに使用できます。情報を取得したいコマンドのモードを指定します。",
                     description_en="Can be used instead of `cmd_title`. Specify the mode of the command to get information for."),
                dict(opt="target_cmd", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="`cmd_title` の代わりに使用できます。情報を取得したいコマンド名を指定します。",
                     description_en="Can be used instead of `cmd_title`. Specify the command name to get information for."),
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

        cmd_title = getattr(args, 'cmd_title', None)
        target_mode = getattr(args, 'target_mode', None)
        target_cmd = getattr(args, 'target_cmd', None)

        if cmd_title:
            # cmd_titleからmode/cmdを取得
            opt_path = Path(args.data) / ".cmds" / f"cmd-{cmd_title}.json"
            opt = common.loadopt(opt_path, True)
            if not opt or 'cmd' not in opt or 'mode' not in opt:
                ret = dict(warn=f"Command not found: '{cmd_title}'")
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, ret, None
            target_mode = opt['mode']
            target_cmd = opt['cmd']
        elif not target_mode or not target_cmd:
            ret = dict(warn="Either `cmd_title` or both `target_mode` and `target_cmd` must be specified.")
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, ret, None

        # 権限チェック
        scope = signin.get_request_scope()
        user_session = scope["req"].session.get('signin', {}) if scope and scope["req"] is not None else {}
        if not signin.Signin._check_cmd(signin_file_data=self.signin_file_data, user_groups=args.groups, mode=target_mode, cmd=target_cmd,
                                        opt=args.__dict__, user_name="unknown", user_session=user_session,
                                        logger=logger, appcls=self.appcls, ver=self.ver, language=self.language):
            ret = dict(warn=f"You do not have permission to execute this command.")
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, ret, None

        options = Options.getInstance()
        choices = options.get_cmd_choices(target_mode, target_cmd, False)
        if not choices:
            ret = dict(warn=f"Command not found: mode='{target_mode}', cmd='{target_cmd}'")
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, ret, None

        # callableな値(choice_fn等)を除去してJSONシリアライズ可能にする
        clean_choices = []
        for c in choices:
            if isinstance(c, dict):
                clean = {k: v for k, v in c.items() if not callable(v) and 
                         k in ['opt', 'type', 'default', 'required', 'multi', 'hide', 'description_ja', 'description_en']}
                clean_choices.append(clean)
            else:
                clean_choices.append(c)

        # output_schemaを取得
        output_schema_data = None
        feat = options.get_cmd_attr(target_mode, target_cmd, 'feature')
        if feat is not None and isinstance(feat, validator.Validator):
            try:
                schema_cls = feat.output_schema()
                if isinstance(schema_cls, type) and issubclass(schema_cls, pydantic.BaseModel):
                    output_schema_data = _simplify_model_schema(schema_cls)
            except Exception:
                pass

        data = dict(
            mode=target_mode,
            cmd=target_cmd,
            choices=clean_choices,
            output_schema=output_schema_data,
        )
        ret = dict(success=dict(data=data))
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

        if 'success' not in ret:
            return self.RESP_WARN, ret, None

        return self.RESP_SUCCESS, ret, None

    def output_schema(self) -> type:
        class ChoiceItem(resdata.Base):
            opt: Union[str, None] = pydantic.Field(default=None, description="オプション名")
            type: Union[str, None] = pydantic.Field(default=None, description="オプション型")
            default: Union[Any, None] = pydantic.Field(default=None, description="デフォルト値")
            required: Union[bool, None] = pydantic.Field(default=None, description="必須フラグ")
            multi: Union[bool, None] = pydantic.Field(default=None, description="複数指定フラグ")
            hide: Union[bool, None] = pydantic.Field(default=None, description="非表示フラグ")
            choice: Union[List[Any], None] = pydantic.Field(default=None, description="選択肢リスト")
            description_ja: Union[str, None] = pydantic.Field(default=None, description="説明(日本語)")
            description_en: Union[str, None] = pydantic.Field(default=None, description="説明(英語)")

        class Info(resdata.Base):
            mode: Union[str, None] = pydantic.Field(default=None, description="モード")
            cmd: Union[str, None] = pydantic.Field(default=None, description="コマンド")
            choices: Union[List[ChoiceItem], None] = pydantic.Field(default=None, description="指定可能な引数のリスト")
            output_schema: Union[Dict[str, Any], None] = pydantic.Field(default=None, description="実行結果のJSONスキーマ")

        class Data(resdata.Data):
            data: Union[Info, None] = pydantic.Field(default=None, description="コマンド情報")

        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")

        return Result
