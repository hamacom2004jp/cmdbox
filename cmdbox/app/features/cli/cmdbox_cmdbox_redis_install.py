from cmdbox import version
from cmdbox.app import common
from cmdbox.app.features.cli.cmdbox import cmdbox_base
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import platform
import shutil
import yaml


class CmdboxRedisInstall(cmdbox_base.CmdboxBase):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'cmdbox'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'redis_install'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        opt = super().get_option()
        opt['description_ja'] = "cmdboxのRedisをインストールします。"
        opt['description_en'] = "Installs the cmdbox Redis."
        opt['choice'] = [
            dict(opt="install_from", type=Options.T_STR, default="ubuntu/redis:latest", required=False, multi=False, hide=False, choice=None,
                description_ja="インストール元のRedisイメージを指定します。",
                description_en="Specify the source Redis image to install."),
            dict(opt="install_tag", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                description_ja="指定すると作成するdockerイメージのタグ名に追記出来ます。",
                description_en="If specified, you can add to the tag name of the docker image to create."),
            dict(opt="compose_path", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                description_ja="`docker-compose.yml` ファイルを指定します。",
                description_en="Specify the `docker-compose.yml` file."),
        ]
        return opt

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        common.set_debug(logger, True)
        try:
            ret = self.redis_install(logger, args)
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

            if 'success' not in ret:
                return self.RESP_WARN, ret, None
            return self.RESP_SUCCESS, ret, None
        finally:
            common.set_debug(logger, False)

    def redis_install(self, logger:logging.Logger, args:argparse.Namespace) -> Dict[str, str]:
        """
        redisサーバーをインストールします

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            Dict[str, str]: 結果
        """
        if platform.system() == 'Windows':
            return {"warn": f"install Redis command is Unsupported in windows platform."}

        container = "redis"
        dockerfile = Path(f'.Dockerfile.{container}')
        with open(dockerfile, 'w', encoding='utf-8') as fp:
            text = self._load_dockerfile(container)
            start_sh_hst = Path(self.ver.__appid__) / container / 'scripts'
            start_sh_hst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(Path(version.__file__).parent / 'docker' / container / 'scripts', start_sh_hst, dirs_exist_ok=True)
            try:
                shutil.copytree(Path(self.ver.__file__).parent / 'docker' / container / 'scripts', start_sh_hst, dirs_exist_ok=True)
            except:
                pass
            imgname = f"hamacom/{self.ver.__appid__}/{container}:{self.ver.__version__}{f'_{args.install_tag}' if args.install_tag else ''}"
            text = text.replace('#{FROM}', f'FROM {args.install_from if args.install_from else "ubuntu/redis:latest"}')
            fp.write(text)

        cmd = f"docker build ./ --rm -t {imgname} -f {dockerfile}"
        returncode, _, _cmd = common.cmd(f"{cmd}", logger, slise=-1)
        dockerfile.unlink(missing_ok=True)

        # docker_compose.ymlの設定
        compose_path = args.compose_path
        if not compose_path:
            compose_path = 'docker-compose.yml'
        docker_compose_path = Path(compose_path)
        if not docker_compose_path.exists():
            with open(docker_compose_path, 'w', encoding='utf-8') as fp:
                fp.write(self._load_base_compose(container))
        with open(docker_compose_path, 'r', encoding='utf-8') as fp:
            comp = yaml.safe_load(fp)
        with open(docker_compose_path, 'w', encoding='utf-8') as fp:
            services = comp['services']
            services[container] = dict(
                image=imgname,
                container_name=container,
                environment=dict(
                    APPID='${APPID:-'+self.ver.__appid__+'}',
                    TZ='Asia/Tokyo',
                    REDIS_PORT=6379,
                    REDIS_PASSWORD='password',
                ),
                ports=['6379:6379'],
                restart='always',
                working_dir=f'/opt/{self.ver.__appid__}/{container}',
            )
            yaml.dump(comp, fp)

        if returncode != 0:
            logger.warning(f"Failed to install Redis server. cmd:{_cmd}")
            return {"error": f"Failed to install Redis server. cmd:{_cmd}"}
        return {"success": f"Success to install Redis server. cmd:{_cmd}"}
