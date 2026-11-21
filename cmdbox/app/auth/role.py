from enum import Enum
from typing import Dict, Any
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
    PFDEVELOPER = (None, "PlatformDeveloper", "Platform Developer", False)
    PFMASTER = (None, "PlatformMaster", "Platform Master", False)
    USERADMIN = (None, "UserAdmin", "User Administrator", False)
    MANAGER = (None, "Manager", "Head of the Group", False)
    LEADER = (MANAGER, "Leader", "Leader of the Group", False)
    EXPERT = (LEADER, "Expert", "Expert of the Group", False)
    MEMBER = (LEADER, "Member", "Member of the Group", False)

    def __init__(self, parent=None, title=None, description=None, hidden=False) -> None:
        self.parent = parent
        self.title = title
        self.description = description
        self.hidden = hidden

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
        if child==self or child.parent == self:
            return True
        if child.parent is not None:
            return self.has_children(child.parent)
        return False

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
