from cmdbox.app import common, feature, options
from cmdbox.app.commons import resdata
from pathlib import Path
from typing import Any, Callable, Dict, Tuple, List, Union
import argparse
import functools
import logging
import pydantic
import re


def apprun_check(func:Callable) -> Callable:
    """
    コマンドの引数の妥当性を検証するデコレーター

    Args:
        func (Callable): コマンドの実行関数
    Returns:
        Callable: デコレーターでラップされた関数
    """
    @functools.wraps(func)
    def wrapper(self:Validator, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        コマンドの引数の妥当性を検証し、実行結果のスキーマを検証します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報
        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if not isinstance(self, Validator):
            logger.warning(f"apprun_check decorator is applied to a function whose self is not an instance of Validator. Skipping validation. args: {args}")
            return func(self, logger, args, tm, pf)
        
        # 引数の妥当性検証
        st, msg, obj = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, obj
        # コマンドの実行
        st, msg, obj = func(self, logger, args, tm, pf)
        if getattr(args, 'output_no_validate', False):
            return st, msg, obj
        # 結果のスキーマ検証
        cls = self.output_schema()
        try:
            if issubclass(cls, pydantic.BaseModel):
                cls.model_validate(msg)
            return st, msg, obj
        except Exception as e:
            if issubclass(cls, resdata.Base):
                info = cls.get_model_info()
                msg = dict(warn=f"Invalid result format: {e}", output=msg, schema=info)
            else:
                msg = dict(warn=f"Invalid result format: {e}", output=msg)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
    return wrapper

def async_apprun_check(func:Callable) -> Callable:
    """
    コマンドの引数の妥当性を検証するデコレーター

    Args:
        func (Callable): コマンドの実行関数
    Returns:
        Callable: デコレーターでラップされた関数
    """
    @functools.wraps(func)
    async def wrapper(self:Validator, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        コマンドの引数の妥当性を検証し、実行結果のスキーマを検証します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報
        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if not isinstance(self, Validator):
            logger.warning(f"async_apprun_check decorator is applied to a function whose self is not an instance of Validator. Skipping validation. args: {args}")
            return await func(self, logger, args, tm, pf)
        # 引数の妥当性検証
        st, msg, obj = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, obj
        # コマンドの実行
        st, msg, obj = await func(self, logger, args, tm, pf)
        if getattr(args, 'output_no_validate', False):
            return st, msg, obj
        # 結果のスキーマ検証
        cls = self.output_schema()
        try:
            if issubclass(cls, pydantic.BaseModel):
                cls.model_validate(msg)
            return st, msg, obj
        except Exception as e:
            if issubclass(cls, resdata.Base):
                info = cls.get_model_info()
                msg = dict(warn=f"Invalid result format: {e}", output=msg, schema=info)
            else:
                msg = dict(warn=f"Invalid result format: {e}", output=msg)
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
    return wrapper

LONG_TEXT_BOUNDARY = 512
class Validator(feature.Feature):
    def output_schema(self) -> type:
        """
        コマンドの実行結果スキーマを表すクラスを返します

        Returns:
            type: 結果のスキーマクラス
        """
        return resdata.Result

    def parse_output(self, output:Any) -> Any:
        """
        コマンドの実行結果をパースします

        Args:
            output (Any): コマンドの実行結果
        Returns:
            Any: パース後の結果
        """
        cls = self.output_schema()
        return cls.model_validate(output)

    def valid(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        コマンドの引数の妥当性を検証します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス
        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        def_opt = self.get_option()
        choices = def_opt.get('choice',[])
        validators = {
            'data': self.valid_data,
            'signin_file': self.valid_signin_file,
        }
        # 共通の引数のデフォルト値を設定
        if not hasattr(args, 'format'): setattr(args, 'format', False)
        if not hasattr(args, 'output_json'): setattr(args, 'output_json', None)
        if not hasattr(args, 'output_json_append'): setattr(args, 'output_json_append', False)
        # 引数の検証
        for choice in choices:
            opt = choice.get('opt', None)
            default = choice.get('default', None)
            required = choice.get('required', False)
            type = choice.get('type', None)
            multi = choice.get('multi', False)
            fileio = choice.get('fileio', None)
            if not opt:
                continue
            if not hasattr(args, opt):
                setattr(args, opt, default)
            val = getattr(args, opt)
            # 必須オプションの検証
            if required and type != options.Options.T_BOOL:
                if not val:
                    msg = dict(warn=f"Please specify --{opt}")
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
            # 型の検証
            if type == options.Options.T_BOOL and val is not None:
                if not isinstance(val, bool):
                    msg = dict(warn=f"Invalid value for --{opt}: {val} (must be a boolean)")
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
            if type == options.Options.T_INT and val is not None:
                try:
                    if multi and isinstance(val, list):
                        val = [int(v) for v in val]
                    else:
                        val = int(val)
                except Exception as e:
                    msg = dict(warn=f"Invalid value for --{opt}: {val} (must be an integer)")
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
            if type == options.Options.T_FLOAT and val is not None:
                try:
                    if multi and isinstance(val, list):
                        val = [float(v) for v in val]
                    else:
                        val = float(val)
                except Exception as e:
                    msg = dict(warn=f"Invalid value for --{opt}: {val} (must be a float)")
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
            if type in [options.Options.T_STR] and val is not None:
                if multi and isinstance(val, list):
                    if val and not all(isinstance(v, str) for v in val):
                        msg = dict(warn=f"Invalid value for --{opt}: {val} (must be a list of strings)")
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, msg, None
                    if val and all(len(v)>=LONG_TEXT_BOUNDARY for v in val):
                        msg = dict(warn=f"Invalid value for --{opt}: {val} (each string must be less than {LONG_TEXT_BOUNDARY} characters)")
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, msg, None
                    if 'name' in opt and all(not re.match(r'^[\w\-]+$', v) for v in val):
                        msg = dict(warn=f"{opt} can only contain alphanumeric characters, underscores, and hyphens.")
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, msg, None
                elif not isinstance(val, str):
                    msg = dict(warn=f"Invalid value for --{opt}: {val} (must be a string)")
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
                elif len(val)>=LONG_TEXT_BOUNDARY:
                    msg = dict(warn=f"Invalid value for --{opt}: {val} (must be less than {LONG_TEXT_BOUNDARY} characters)")
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
                elif 'name' in opt and not re.match(r'^[\w\-]+$', val):
                    msg = dict(warn=f"{opt} can only contain alphanumeric characters, underscores, and hyphens.")
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None

            if type in [options.Options.T_TEXT, options.Options.T_PASSWD] and val is not None:
                if multi and isinstance(val, list):
                    if val and not all(isinstance(v, str) for v in val):
                        msg = dict(warn=f"Invalid value for --{opt}: {val} (must be a list of strings)")
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, msg, None
                elif not isinstance(val, str):
                    msg = dict(warn=f"Invalid value for --{opt}: {val} (must be a string)")
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return self.RESP_WARN, msg, None
            if type == options.Options.T_FILE and val is not None and fileio in ['in']:
                if not isinstance(val, list):
                    _val = [val,]
                for v in _val:
                    path = Path(v)
                    if not path.exists():
                        msg = dict(warn=f"Invalid value for --{opt}: {v} (file does not exist)")
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, msg, None
                    if not path.is_file():
                        msg = dict(warn=f"Invalid value for --{opt}: {v} (not a file)")
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, msg, None
            if type == options.Options.T_DIR and val is not None and fileio in ['in']:
                if not isinstance(val, list):
                    _val = [val,]
                for v in _val:
                    path = Path(v)
                    if not path.exists():
                        msg = dict(warn=f"Invalid value for --{opt}: {v} (directory does not exist)")
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, msg, None
                    if not path.is_dir():
                        msg = dict(warn=f"Invalid value for --{opt}: {v} (not a directory)")
                        common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                        return self.RESP_WARN, msg, None
            # TODO: type==T_DATE, T_DATETIME, T_MLISTの検証

            # Choicesの検証 TODO:type==T_DICTのときのchoice検証が必要
            if type != options.Options.T_DICT:
                opt_choices = choice.get('choice', None)
                choice_edit_flag = choice.get('choice_edit', False)
                if opt_choices is not None and not choice_edit_flag and val is not None:
                    valid_values = []
                    for c in opt_choices:
                        if isinstance(c, dict):
                            valid_values.append(c.get('opt'))
                        else:
                            valid_values.append(c)
                    check_vals = val if (multi and isinstance(val, list)) else [val]
                    if len(valid_values) > 0:
                        for v in check_vals:
                            if v not in valid_values:
                                msg = dict(warn=f"Invalid value for --{opt}: {v} (must be one of {valid_values})")
                                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                                return self.RESP_WARN, msg, None
            # オプション固有のバリデーション
            validator = validators.get(opt, None)
            if validator:
                st, msg, obj = validator(logger, opt, val)
                if st != self.RESP_SUCCESS:
                    common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                    return st, msg, None
        return self.RESP_SUCCESS, {}, None

    def valid_data(self, logger:logging.Logger, opt:str, val:Any) -> Tuple[int, Dict[str, Any], Any]:
        """
        --dataオプションの値の妥当性を検証します

        Args:
            logger (logging.Logger): ロガー
            opt (str): オプション名
            val (Any): オプションの値
        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if opt!='data': return self.RESP_SUCCESS, {}, None
        path = Path(val)
        if not path.exists():
            msg = dict(warn=f"The path specified for '--data' does not exist.")
            return self.RESP_WARN, msg, None
        if not path.is_dir():
            msg = dict(warn=f"The path specified for '--data' is not a directory.")
            return self.RESP_WARN, msg, None
        return self.RESP_SUCCESS, {}, None

    def valid_signin_file(self, logger:logging.Logger, opt:str, val:Any) -> Tuple[int, Dict[str, Any], Any]:
        """
        --signin_fileオプションの値の妥当性を検証します

        Args:
            logger (logging.Logger): ロガー
            opt (str): オプション名
            val (Any): オプションの値
        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        if opt!='signin_file': return self.RESP_SUCCESS, {}, None
        path = Path(val)
        if not path.exists():
            msg = dict(warn=f"The path specified for '--signin_file' does not exist.")
            return self.RESP_WARN, msg, None
        if not path.is_file():
            msg = dict(warn=f"The path specified for '--signin_file' is not a file.")
            return self.RESP_WARN, msg, None
        return self.RESP_SUCCESS, {}, None

    def init_test(self) -> None:
        """
        テスト用の初期化処理を行います
        """
        pass

    def cleaning_test(self) -> None:
        """
        テスト用のクリーンアップ処理を行います
        """
        pass
