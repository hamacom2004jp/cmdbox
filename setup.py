from pathlib import Path
from setuptools import setup
from setuptools.command.build_py import build_py as _build_py
from setuptools.command.egg_info import egg_info as _egg_info
from setuptools.command.install import install
import io
import os
import platform
import re

def get_info(rel_path):
    fpath = Path(__file__).parent / rel_path
    version = ''
    with io.open(fpath, encoding='utf-8') as fp:
        content = fp.read()
        version = re.search(r"^__version__\s+=\s+'(.*)'", content, re.M).group(1)
    return version

VERSION = get_info('cmdbox/version.py')

# ------------------------------------------
# extensions フォルダを再帰的に収集する共通ロジック
# glob.glob の ** は Python 3.11 で . 始まりディレクトリを再帰しないため
# os.walk を使って全ファイルを明示的に列挙する
# ------------------------------------------
def _inject_extensions_data(distribution):
    pkg_dir = Path(__file__).parent / 'cmdbox'
    ext_dir = pkg_dir / 'extensions'
    extra = []
    for root, dirs, files in os.walk(ext_dir):
        for fname in files:
            rel = (Path(root) / fname).relative_to(pkg_dir)
            extra.append(str(rel).replace('\\', '/'))
    existing = distribution.package_data.get('cmdbox', [])
    distribution.package_data['cmdbox'] = list(set(existing + extra))


class BuildPyCommand(_build_py):
    """build_py 前に extensions を再帰収集して package_data に追加する。"""
    def run(self):
        _inject_extensions_data(self.distribution)
        super().run()


class EggInfoCommand(_egg_info):
    """egg_info (SOURCES.txt 生成) 前に extensions を再帰収集して package_data に追加する。"""
    def run(self):
        _inject_extensions_data(self.distribution)
        super().run()

# ------------------------------------------
# カスタムインストールのロジック (pyproject.tomlで置き換え不可)
# ------------------------------------------
class CustomInstallCommand(install):
    def run(self):
        super().run()
        if platform.system() != 'Linux':
            return
        bashrc = Path.home() / '.bashrc'
        if not bashrc.exists():
            return
        CMD = 'eval "$(register-python-argcomplete cmdbox)"'
        with open(bashrc, 'r') as fp:
            for line in fp:
                if line == CMD:
                    return
        with open(bashrc, 'a') as fp:
            fp.write('\n'+CMD)

# setup()関数の呼び出しは、残りの設定をpyproject.tomlから取得するために最小限に抑えます
# dynamic = [...] の設定を有効にするために、setuptoolsのversionは渡しません
setup(
    version=VERSION,  # pyproject.tomlの[project]のversionフィールドを無効化するために渡す
    # setup.cfg/pyproject.tomlと互換性を持たせるため、cmdclassとcmdclassに依存する
    # install_requires/versionを除く最小限の引数のみを保持
    cmdclass={'install': CustomInstallCommand, 'build_py': BuildPyCommand, 'egg_info': EggInfoCommand},
)