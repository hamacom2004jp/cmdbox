from enum import Enum
from typing import Dict, Set, Any
import importlib
import inspect


def get_RoleClass(signin_file_data:Dict[str, Any]):
    """
    指定されたsignin_file_dataからRoleクラスを取得します

    Args:
        signin_file_data (Dict[str, Any]): サインイン設定データ

    Returns:
        Type[Enum]: Roleクラス
    """
    if not signin_file_data or 'signin' not in signin_file_data or \
        'role_module' not in signin_file_data['signin'] or not signin_file_data['signin']['role_module']:
        raise ValueError("Invalid signin_file_data.")
    role_module = signin_file_data['signin']['role_module']
    try:
        mod = importlib.import_module(role_module)
        for name, cls in inspect.getmembers(mod, inspect.isclass):
            if name == "Role" and issubclass(cls, Enum):
                return cls
        return None
    except Exception as e:
        raise e

class Role(Enum):
    """
    Role definitions for the application.
    """
    PFDEVELOPER = (None, "PlatformDeveloper", "Platform Developer")
    PFMASTER = (None, "PlatformMaster", "Platform Master")
    USERADMIN = (None, "UserAdmin", "User Administrator")
    MANAGER = (None, "Manager", "Head of the Group")
    LEADER = (MANAGER, "Leader", "Leader of the Group")
    EXPERT = (LEADER, "Expert", "Expert of the Group")
    MEMBER = (LEADER, "Member", "Member of the Group")

    def __init__(self, parent=None, title=None, description=None) -> None:
        self._parent_ref = parent
        self.title = title
        self.description = description

    @property
    def parent(self) -> "Role":
        """
        親ロールを遅延初期化で取得する

        Enum初期化時にタプル全体が割り当てられるため、
        プロパティを使ってタプルから正しく親を抽出します

        Returns:
            Role: 親ロール、またはNone
        """
        if self._parent_ref is None:
            return None
        # Role値の場合
        if isinstance(self._parent_ref, Role):
            return self._parent_ref
        # タプルの場合、そのタプル全体が親のvalue値
        if isinstance(self._parent_ref, tuple):
            # そのタプルに対応するEnum値を探す
            for role in self.__class__:
                if role.value == self._parent_ref:
                    return role
        return None

    def has_children(self, child:"Role") -> bool:
        """
        指定したchildがこのロールの子孫であるかどうかを判定する

        Args:
            child (Role): 判定対象の子ロール
        Returns:
            bool: 指定したchildがこのロールの子孫であればTrue、それ以外はFalse
        """
        if child is None or not isinstance(child, Role):
            return False
        if child == self or child.parent == self:
            return True
        if child.parent is not None:
            return self.has_children(child.parent)
        return False

    def get_children(self) -> Set["Role"]:
        """
        このroleの子孫を取得する

        Returns:
            Set[Role]: このroleの子孫の集合
        """
        children = set()
        for r in self.__class__:
            if r.parent and r.parent == self:
                children.add(r)
                children.update(r.get_children())
        return children

    @classmethod
    def valid_role(cls, role_name:str) -> bool:
        """
        指定したrole_nameが有効なロールであるかどうかを判定する

        Args:
            role_name (str): 判定対象のロール名
        Returns:
            bool: 指定したrole_nameが有効なロールであればTrue、それ以外はFalse
        """
        if not isinstance(role_name, str):
            return False
        return role_name in cls.__members__
