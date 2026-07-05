from cmdbox.app import feature
from typing import Any, Callable, Dict, List, Tuple, Union
import argparse
import logging
import time


def apprun_cache(func:Callable=None, args_key:str=None, exclude_fn:Callable=None) -> Callable:
    """
    list系コマンドの実行結果をキャッシュするデコレーター。
    list系コマンド実行関数に適用することで、コマンドの実行前にキャッシュを確認し、実行後にキャッシュを更新します。

    Args:
        func (Callable): コマンドの実行関数。引数なしで使用された場合はNone。
        args_key (str): キャッシュキーを決定するための引数名。argsからこの引数の値を取得してキャッシュキーとして使用します。指定しなかった場合はデフォルトのキャッシュキー 'default' が使用されます。
        exclude_fn (Callable): キャッシュから除外する条件を判定する関数。引数はargsでTrueを返すと除外します。指定しなかった場合は全ての結果がキャッシュされます。
    Returns:
        Callable: デコレーターでラップされた関数
    """
    def decorator(f: Callable) -> Callable:
        #@functools.wraps(f)
        def wrapper(self:feature.Feature, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
            if not hasattr(self, '_apprun_cache'):
                self._apprun_cache = MemoryCache()

            # キャッシュクリアが指定されている場合はキャッシュをクリアして、以降の処理を実行します
            if getattr(args, 'cache_clear', False):
                logger.info(f"Cache cleared for {self.get_mode()}_{self.get_cmd()}")
                self._apprun_cache.clear()

            # キャッシュから除外する条件を判定する関数が指定されている場合は、除外条件を判定します
            exclude = False
            if exclude_fn is not None:
                exclude = exclude_fn(args)
            if exclude:
                return f(self, logger, args, tm, pf)

            # args_keyが指定されている場合は、argsからキャッシュキーを取得し、指定されていない場合はデフォルトのキャッシュキー 'default' を使用します
            cache_key = getattr(args, args_key) if args_key is not None else str(f)
            if not cache_key:
                logger.warning(f"Cache key is empty for args_key '{args_key}'. no cache will be used.")
                return f(self, logger, args, tm, pf)

            # キャッシュが有効で、かつキャッシュが存在し、有効期限が切れていない場合はキャッシュを返す
            cached = self._apprun_cache.get(cache_key)
            if not cached:
                st, msg, obj = f(self, logger, args, tm, pf)
                if st == feature.Feature.RESP_SUCCESS:
                    self._apprun_cache.set(cache_key, msg, getattr(args, 'cache_timeout', 60))
                return st, msg, obj

            if 'success' not in cached:
                return feature.Feature.RESP_WARN, cached, None
            return feature.Feature.RESP_SUCCESS, cached, None
        return wrapper
    
    # 引数なしで使用された場合 @apprun_cache
    if func is not None and callable(func):
        return decorator(func)
    # 引数ありで使用された場合 @apprun_cache(exclude_fn=...)
    else:
        return decorator

class MemoryCache:
    """
    メモリ上にデータをキャッシュするクラス。
    キャッシュは識別キーごとに管理され、有効期限（秒）を設定できます。
    """

    def __init__(self):
        self._cache: Dict[str, Any] = {}
        self._timeout: Dict[str, float] = {}

    def get(self, key: str) -> Union[Any, None]:
        """
        キャッシュからデータを取得します。
        キャッシュが存在しない、または有効期限切れの場合は None を返します。

        Args:
            key (str): キャッシュキー

        Returns:
            Union[Any, None]: キャッシュされたデータ、または None
        """
        if key not in self._cache:
            return None
        if key not in self._timeout or time.time() >= self._timeout[key]:
            self.delete(key)
            return None
        value = self._cache[key]
        if isinstance(value, (list, dict)):
            value = value.copy()  # キャッシュから取得する際もコピーして、外部からの変更を防止
        if isinstance(value, dict) and 'performance' in value:
            del value['performance']
        return value

    def set(self, key: str, value: Any, timeout: float) -> None:
        """
        データをキャッシュに保存します。

        Args:
            key (str): キャッシュキー
            value (Any): キャッシュするデータ
            timeout (float): 有効期限（秒）
        """
        if value is not None and isinstance(value, (list, dict)):
            value = value.copy()  # キャッシュに保存する前にコピーして、外部からの変更を防止
        self._cache[key] = value
        self._timeout[key] = time.time() + timeout

    def refresh(self, key: str, timeout: float) -> bool:
        """
        キャッシュの有効期限を更新します。

        Args:
            key (str): キャッシュキー
            timeout (float): 延長する有効期限（秒）

        Returns:
            bool: キャッシュが存在した場合は True、存在しない場合は False
        """
        if key not in self._cache:
            return False
        self._timeout[key] = time.time() + timeout
        return True

    def exists(self, key: str) -> bool:
        """
        有効なキャッシュが存在するかどうかを確認します。

        Args:
            key (str): キャッシュキー

        Returns:
            bool: 有効なキャッシュが存在する場合は True
        """
        if key not in self._cache:
            return False
        if key not in self._timeout or time.time() >= self._timeout[key]:
            self.delete(key)
            return False
        return True

    def delete(self, key: str) -> None:
        """
        キャッシュからデータを削除します。

        Args:
            key (str): キャッシュキー
        """
        self._cache.pop(key, None)
        self._timeout.pop(key, None)

    def clear(self) -> None:
        """
        全キャッシュを削除します。
        """
        self._cache.clear()
        self._timeout.clear()
