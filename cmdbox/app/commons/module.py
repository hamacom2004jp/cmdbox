from cmdbox.app import feature
from typing import List, Dict, Any
import importlib.util
import inspect
import pkgutil


def get_module_list(package_name) -> List[str]:
    """
    パッケージ内のモジュール名のリストを取得します。

    Args:
        package_name (str): パッケージ名

    Returns:
        List[str]: モジュール名のリスト
    """
    package = __import__(package_name, fromlist=[''])
    return [name for _, name, _ in pkgutil.iter_modules(package.__path__)]

def load_features(package_name:str, prefix:str="cmdbox_") -> Dict[str, Any]:
    """
    フィーチャーを読み込みます。

    Args:
        package_name (str): パッケージ名
        prefix (str, optional): プレフィックス. Defaults to "cmdbox_".
    Returns:
        Dict[str, Any]: フィーチャーのリスト
    """
    features = dict()
    package = __import__(package_name, fromlist=[''])
    for finder, name, ispkg in pkgutil.iter_modules(package.__path__):
        if name.startswith(prefix):
            mod = importlib.import_module(f"{package_name}.{name}")
            members = inspect.getmembers(mod, inspect.isclass)
            for name, cls in members:
                if cls is feature.Feature or not issubclass(cls, feature.Feature):
                    continue
                fobj = cls()
                mode = fobj.get_mode()
                cmd = fobj.get_cmd()
                if mode not in features:
                    features[mode] = dict()
                features[mode][cmd] = fobj.get_option()
                features[mode][cmd]['feature'] = fobj
    return features

def load_webfeatures(package_name:str, prefix:str="cmdbox_web_") -> List[Any]:
    """
    Webフィーチャーを読み込みます。

    Args:
        package_name (str): パッケージ名
    Returns:
        Dict[feature.WebFeature]: Webフィーチャーのリスト
    """
    webfeatures = list()
    package = __import__(package_name, fromlist=[''])
    for finder, name, ispkg in pkgutil.iter_modules(package.__path__):
        if name.startswith(prefix):
            mod = importlib.import_module(f"{package_name}.{name}")
            members = inspect.getmembers(mod, inspect.isclass)
            for name, cls in members:
                if cls is feature.WebFeature or not issubclass(cls, feature.WebFeature):
                    continue
                fobj = cls()
                webfeatures.append(fobj)
    return webfeatures
