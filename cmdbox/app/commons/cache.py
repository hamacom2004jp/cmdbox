from typing import Any, Dict, Union
import time


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
