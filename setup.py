from pathlib import Path
from setuptools import setup
from setuptools.command.install import install
import io
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
    cmdclass={'install': CustomInstallCommand},
)