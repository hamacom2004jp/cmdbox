from cmdbox.app import common, feature, options, web
from cmdbox.app.commons import cache, convert, redis_client
from cmdbox.app.features.cli import cmdbox_keystore_load
from pathlib import Path
from typing import Any, Callable, Dict, Tuple, List, Optional, Union
import argparse
import datetime
import functools
import logging
import pydantic
import re


def apprun_keyset(func:Callable, key_opts:Optional[List[str]]=None) -> Callable:
    """
    機能の引数に対して、Keystoreの値を設定するデコレータです。
    key_optsで指定されたオプションに対して、Keystoreから値を取得して設定します。
    key_optsが指定されていない場合、オプションスキーマからplaceholder=Trueのオプションを自動的に取得します。

    Args:
        func (Callable): デコレートする非同期関数
        key_opts (List[str], optional): Keystoreの値を設定するオプションのリスト。省略可能。
    
    Returns:
        Callable: デコレータ関数
    """
    def decorator(f: Callable) -> Callable:
        #@functools.wraps(func)
        def wrapper(self:feature.Feature, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
            resolved_key_opts = key_opts
            # key_optsが指定されていない場合、オプションスキーマから取得する
            if not resolved_key_opts:
                resolved_key_opts = []
                schema = self.get_option()
                if not schema or not schema.get('choice', None):
                    return f(self, logger, args, tm, pf)
                for schema_opt in schema.get('choice'):
                    if not schema_opt.get('placeholder', False):
                        continue
                    resolved_key_opts.append(schema_opt.get('opt'))

            # key_optsに従って、引数の値を置換する
            for opt in resolved_key_opts:
                value = getattr(args, opt, None)
                if not value:
                    continue
                if type(value) is list:
                    for val in value:
                        _set_val(self, args, opt, val)
                elif type(value) is dict:
                    for k, v in value.items():
                        _set_val(self, args, opt, v)
                elif type(value) is str:
                    _set_val(self, args, opt, value)
            return f(self, logger, args, tm, pf)
        return wrapper
    # 引数なしで使用された場合 @apprun_cache
    if func is not None and callable(func):
        return decorator(func)
    # 引数ありで使用された場合 @apprun_cache(exclude_fn=...)
    else:
        return decorator

def async_apprun_keyset(func:Callable, key_opts:Optional[List[str]]=None) -> Callable:
    """
    非同期で実行される機能の引数に対して、Keystoreの値を設定するデコレータです。
    key_optsで指定されたオプションに対して、Keystoreから値を取得して設定します。
    key_optsが指定されていない場合、オプションスキーマからplaceholder=Trueのオプションを自動的に取得します。

    Args:
        func (Callable): デコレートする非同期関数
        key_opts (List[str], optional): Keystoreの値を設定するオプションのリスト。省略可能。
    
    Returns:
        Callable: デコレータ関数
    """
    def decorator(f: Callable) -> Callable:
        #@functools.wraps(func)
        async def wrapper(self:feature.Feature, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
            resolved_key_opts = key_opts
            # key_optsが指定されていない場合、オプションスキーマから取得する
            if not resolved_key_opts:
                resolved_key_opts = []
                schema = self.get_option()
                if not schema or not schema.get('choice', None):
                    return await f(self, logger, args, tm, pf)
                for schema_opt in schema.get('choice'):
                    if not schema_opt.get('placeholder', False):
                        continue
                    resolved_key_opts.append(schema_opt.get('opt'))

            # key_optsに従って、引数の値を置換する
            for opt in resolved_key_opts:
                value = getattr(args, opt, None)
                if not value:
                    continue
                if type(value) is list:
                    for val in value:
                        _set_val(self, args, opt, val)
                elif type(value) is dict:
                    for k, v in value.items():
                        _set_val(self, args, opt, v)
                elif type(value) is str:
                    _set_val(self, args, opt, value)
            return await f(self, logger, args, tm, pf)
        return wrapper

    # 引数なしで使用された場合 @apprun_cache
    if func is not None and callable(func):
        return decorator(func)
    # 引数ありで使用された場合 @apprun_cache(exclude_fn=...)
    else:
        return decorator

def _set_val(self, args, opt, val):
    if not val or type(val) is not str:
        return
    data_dir = None
    if hasattr(self, 'data_dir'):
        data_dir = self.data_dir
    if hasattr(args, 'data_dir'):
        data_dir = args.data_dir
    val = replace_value(
        data_dir=data_dir,
        string_value=val,
        key_usage=self.get_svcmd(),
        signin_user=args.signin_user,
        signin_groups=args.signin_groups,
        default_val_type='key_value',
        cache_clear=False,
        cache_timeout=60
    )
    setattr(args, opt, val)

ptn_key = re.compile(r'\$\{(?P<key_name>.+)@keystore\.(?P<key_provider>[^\[]+)\[?(?P<val_type>[^\]]+)?\]?\}')
def replace_value(*, data_dir:Path, string_value:str, key_usage:str,
                  signin_user:str, signin_groups:List[str], default_val_type:str='key_value',
                  cache_clear:bool=False, cache_timeout:int=60) -> str:
    """
    string_valueの中からkeystore参照形式の文字列を検出し、対応する値に置換する。
    キャッシュが存在する場合はそれを利用し、存在しない場合はkeystore_loadコマンドから取得する。
    
    Args:
        data_dir (Path): データディレクトリ
        string_value (str): 置換対象の文字列
        key_usage (str): キーの使用目的
        signin_user (str): サインインしているユーザー
        signin_groups (List[str]): サインインしているユーザーの所属グループ
        default_val_type (str, optional): デフォルトの値の種類. Defaults to 'key_value'.
        cache_clear (bool, optional): キャッシュをクリアするかどうか. Defaults to False.
        cache_timeout (int, optional): キャッシュの有効期限（秒）. Defaults to 60.
    Returns:
        str: 置換後の文字列
    """
    mt = ptn_key.match(string_value)
    if not mt:
        return string_value
    for m in [mt]:  # Iterate over the match object to extract groups
        key_name = m.group('key_name')
        key_provider = m.group('key_provider')
        val_type = m.group('val_type') if m.group('val_type') else default_val_type

        key_value = get_value(
            data_dir=data_dir,
            key_name=key_name,
            key_provider=key_provider,
            val_type=val_type,
            key_usage=key_usage,
            signin_user=signin_user,
            signin_groups=signin_groups,
            cache_clear=cache_clear,
            cache_timeout=cache_timeout
        )
        string_value = string_value.replace(m.group(0), key_value)
    return string_value

mod_cache = cache.MemoryCache()
val_types = ['key_value', 'sign_key', 'sign_cert', 'key_pass', 'enc_key', 'ca_cert', 'claims']

def get_value(*, data_dir:Path,
                    key_name:str, key_provider:str, val_type:str, key_usage:str,
                    signin_user:str, signin_groups:List[str],
                    cache_clear:bool=False, cache_timeout:int=60) -> str:
    """
    指定されたキーの値を取得する。

    Args:
        data_dir (Path): データディレクトリ
        key_name (str): キーの名前
        key_provider (str): キーの提供者
        val_type (str): 値の種類
        key_usage (str): キーの使用目的
        signin_user (str): サインインしているユーザー
        signin_groups (List[str]): サインインしているユーザーの所属グループ
        cache_clear (bool, optional): キャッシュをクリアするかどうか. Defaults to False.
        cache_timeout (int, optional): キャッシュの有効期限（秒）. Defaults to 60.

    Returns:
        str: 取得した値
    """
    if not key_name: raise ValueError("Key name is required.")
    if not key_provider: raise ValueError("Key provider is required.")
    if not val_type: raise ValueError("Value type is required.")
    if not key_usage: raise ValueError("Key usage is required.")
    if not signin_user: raise ValueError("Signin user is required.")
    if not signin_groups: raise ValueError("Signin groups are required.")
    if cache_clear:
        mod_cache.clear()
    if val_type not in val_types:
        raise ValueError(f"Invalid val_type: {val_type} Allowed types are: {', '.join(val_types)}")
    if mod_cache.exists(f'{key_name}@{key_provider}'):
        cfg = mod_cache.get(f'{key_name}@{key_provider}')
        cmdbox_keystore_load.check_key(cfg, key_name, key_provider, signin_user, signin_groups, val_type)
        return cfg.get(val_type)

    if data_dir:
        cfg = cmdbox_keystore_load.load_key(data_dir, key_name, key_provider, signin_user, signin_groups, val_type)
    else:
        _web:web.Web = web.Web.getInstance()
        redis_cli:redis_client.RedisClient = _web.redis_cli
        payload = dict(
            key_name=key_name,
            key_provider=key_provider,
            val_type=val_type,
            signin_user=signin_user,
            signin_groups=signin_groups,
        )
        payload_b64 = convert.str2b64str(common.to_str(payload))
        ret = redis_cli.send_cmd("keystore_load", [payload_b64],
                                 retry_count=1, retry_interval=4, timeout=15, nowait=False)
        if 'success' not in ret:
            raise ValueError(str(ret))
        cfg = ret.get('success', {}).get('data', {})
        if not cfg:
            raise ValueError("Failed to load key data.")

    mod_cache.set(f'{key_name}@{key_provider}', cfg, cache_timeout)
    return cfg.get(val_type)

def check_key_usage(cfg: Dict[str, Any], usage: str) -> bool:
    """
    指定されたキーの使用目的が許可されているかを確認する。

    Args:
        cfg (Dict[str, Any]): キーの設定情報
        usage (str): 使用目的

    Returns:
        bool: 許可されていればTrue、そうでなければFalse
    """
    if not cfg: return False
    key_usage = cfg.get('key_usage', None)
    if not key_usage: return False
    return usage in key_usage

def check_period(cfg: Dict[str, Any]) -> bool:
    """
    指定されたキーが有効期間内にあるかを確認する。

    Args:
        cfg (Dict[str, Any]): キーの設定情報

    Returns:
        bool: 有効期間内であればTrue、そうでなければFalse
    """
    if not cfg: return False
    key_period_start = cfg.get('key_period_start', None)
    key_period_end = cfg.get('key_period_end', None)
    if not key_period_start and not key_period_end:
        return True
    try:
        start = datetime.datetime.fromisoformat(key_period_start)
    except ValueError:
        start = None
    try:
        end = datetime.datetime.fromisoformat(key_period_end)
    except ValueError:
        end = None
    now = datetime.datetime.now()
    if start and not end:
        return start <= now
    elif end and not start:
        return now <= end
    return start <= now <= end
