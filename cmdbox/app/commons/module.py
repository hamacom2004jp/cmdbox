from cmdbox.app import feature
from typing import List, Dict, Any
import importlib.util
import inspect
import logging
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

def load_features(package_name:str, prefix:str="cmdbox_", appcls=None, ver=None) -> Dict[str, Any]:
    """
    フィーチャーを読み込みます。

    Args:
        package_name (str): パッケージ名
        prefix (str, optional): プレフィックス. Defaults to "cmdbox_".
        appcls ([type], optional): アプリケーションクラス. Defaults to None.
        ver ([type], optional): バージョンモジュール. Defaults to None.
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
                fobj = cls(appcls, ver)
                mode = fobj.get_mode()
                if type(mode) is str:
                    cmd = fobj.get_cmd()
                    if mode not in features:
                        features[mode] = dict()
                    features[mode][cmd] = fobj.get_option()
                    features[mode][cmd]['feature'] = fobj
                elif type(mode) is list:
                    for m in mode:
                        cmd = fobj.get_cmd()
                        if m not in features:
                            features[m] = dict()
                        features[m][cmd] = fobj.get_option()
                        features[m][cmd]['feature'] = fobj
    return features

def load_webfeatures(package_name:str, prefix:str="cmdbox_web_", appcls=None, ver=None, logger:logging.Logger=None) -> List[Any]:
    """
    Webフィーチャーを読み込みます。

    Args:
        package_name (str): パッケージ名
        prefix (str, optional): プレフィックス. Defaults to "cmdbox_web_".
        appcls ([type], optional): アプリケーションクラス. Defaults to None.
        ver ([type], optional): バージョンモジュール. Defaults to None.
        logger ([type], optional): ロガー. Defaults to None.
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
                fobj = cls(appcls, ver)
                if logger is not None and logger.level == logging.DEBUG:
                    logger.debug(f'load_webfeatures: {fobj}')
                webfeatures.append(fobj)
    return webfeatures

def class_for_name(class_full_name:str):
    """
    クラス名からクラスを取得します。

    Args:
        class_full_name (str): クラスフルパス名

    Returns:
        [type]: クラス
    """
    package_name = '.'.join(class_full_name.split('.')[:-1])
    class_name = class_full_name.split('.')[-1]
    m = importlib.import_module(package_name)
    c = getattr(m, class_name)
    return c