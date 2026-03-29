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


class CmdboxPgSQLInstall(cmdbox_base.CmdboxBase):
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
        return 'pgsql_install'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True, use_agent=False,
            description_ja="PostgreSQLサーバーをインストールします。",
            description_en="Installs the PostgreSQL server.",
            choice=[
                dict(opt="install_pgsqlver", type=Options.T_STR, default="18", required=True, multi=False, hide=False, choice=None,
                     description_ja="PostgreSQLバージョンを指定します。",
                     description_en="Specify the PostgreSQL version."),
                dict(opt="install_from", type=Options.T_STR, default="postgres:18.2", required=False, multi=False, hide=False, choice=None,
                     description_ja="インストール元のPostgreSQLイメージを指定します。",
                     description_en="Specify the source PostgreSQL image to install."),
                dict(opt="install_tag", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="指定すると作成するdockerイメージのタグ名に追記出来ます。",
                     description_en="If specified, you can add to the tag name of the docker image to create."),
                dict(opt="no_install_pgvector", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=None,
                     description_ja="pgvector拡張機能をインストールしないかどうかを指定します。",
                     description_en="Specify whether not to install the pgvector extension."),
                dict(opt="install_pgvector_tag", type=Options.T_STR, default="v0.8.2", required=False, multi=False, hide=False, choice=None,
                     description_ja="pgvector拡張機能のリポジトリ `https://github.com/pgvector/pgvector.git` のtag名を指定します。",
                     description_en="Specify the tag name in the pgvector extension repository `https://github.com/pgvector/pgvector.git`."),
                dict(opt="no_install_age", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=None,
                     description_ja="Apache AGE拡張機能をインストールしないかどうかを指定します。",
                     description_en="Specify whether not to install the Apache AGE extension."),
                dict(opt="install_age_tag", type=Options.T_STR, default="release/PG18/1.7.0", required=False, multi=False, hide=False, choice=None,
                     description_ja="Apache AGE拡張機能のリポジトリ `https://github.com/apache/age.git` のtag名を指定します。",
                     description_en="Specify the tag name in the Apache AGE extension repository `https://github.com/apache/age.git`."),
                dict(opt="no_install_pgcron", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=None,
                     description_ja="pg_cron拡張機能をインストールしないかどうかを指定します。",
                     description_en="Specify whether not to install the pg_cron extension."),
                dict(opt="install_pgcron_tag", type=Options.T_STR, default="v1.6.7", required=False, multi=False, hide=False, choice=None,
                     description_ja="pg_cron拡張機能のリポジトリ `https://github.com/citusdata/pg_cron.git` のtag名を指定します。",
                     description_en="Specify the tag name in the pg_cron extension repository `https://github.com/citusdata/pg_cron.git`."),
                dict(opt="compose_path", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="in",
                     description_ja="`docker-compose.yml` ファイルを指定します。",
                     description_en="Specify the `docker-compose.yml` file."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                     description_ja="処理結果jsonの保存先ファイルを指定。",
                     description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="処理結果jsonファイルを追記保存します。",
                     description_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                     description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                     description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                     description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                     description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

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
            ret = self.pgsql_install(logger, args)
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)

            if 'success' not in ret:
                return self.RESP_WARN, ret, None
            return self.RESP_SUCCESS, ret, None
        finally:
            common.set_debug(logger, False)

    def pgsql_install(self, logger:logging.Logger, args:argparse.Namespace) -> Dict[str, str]:
        """
        PostgreSQLサーバーをインストールします

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
        Returns:
            Dict[str, str]: 結果
        """
        if platform.system() == 'Windows':
            return {"warn": f"install PostgreSQL command is Unsupported in windows platform."}

        container = "pgsql"
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
            imgname = f"hamacom/{self.ver.__appid__}/{container}:{self.ver.__version__}_{args.install_pgsqlver}{f'_{args.install_tag}' if args.install_tag else ''}"
            text = text.replace('#{FROM}', f'FROM {args.install_from if args.install_from else "postgres:18.2"}')
            text = text.replace('#{PGSQLVER}', args.install_pgsqlver)
            if not args.no_install_pgvector:
                text = text.replace('#{INSTALL_PGVECTOR}', \
                                    f"RUN cd /tmp && " + \
                                    f"git clone --branch {args.install_pgvector_tag} https://github.com/pgvector/pgvector.git && " + \
                                    f"cd pgvector && make && make install && cd .. && rm -rf pgvector " + \
                                    f"\n")
            if not args.no_install_age:
                text = text.replace('#{INSTALL_AGE}', \
                                    f"RUN cd /tmp && " + \
                                    f"git clone --branch {args.install_age_tag} --depth 1 https://github.com/apache/age.git && " + \
                                    f"cd age && make && make install && cd .. && rm -rf age " + \
                                    f"\n")
            if not args.no_install_pgcron:
                text = text.replace('#{INSTALL_PGCRON}', \
                                    f"RUN cd /tmp && " + \
                                    f"git clone --branch {args.install_pgcron_tag} https://github.com/citusdata/pg_cron.git && " + \
                                    f"cd pg_cron && make && make install && cd .. && rm -rf pg_cron " + \
                                    f"\n")
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
            dbname = 'pgsql'
            services = comp['services']
            services[container] = dict(
                image=imgname,
                container_name=container,
                environment=dict(
                    APPID='${APPID:-'+self.ver.__appid__+'}',
                    POSTGRES_USER=dbname,
                    POSTGRES_PASSWORD=dbname,
                    POSTGRES_DB=dbname,
                    POSTGRES_HOST_AUTH_METHOD='trust',
                    POSTGRES_PORT='5432',
                    #PGDATA='/var/lib/postgresql/data/pgdata',
                ),
                ports=['5432:5432'],
                restart='always',
                working_dir=f'/opt/{self.ver.__appid__}/{container}',
                volumes=[
                    f'./{self.ver.__appid__}/{container}:/opt/{self.ver.__appid__}/{container}',
                    f'./{self.ver.__appid__}/{container}/data:/var/lib/postgresql/{args.install_pgsqlver}/docker',
                    #f'./{self.ver.__appid__}/{container}:/var/lib/postgresql/data',
                ],
            )
            yaml.dump(comp, fp)

        if returncode != 0:
            logger.warning(f"Failed to install PostgreSQL server. cmd:{_cmd}")
            return {"error": f"Failed to install PostgreSQL server. cmd:{_cmd}"}
        return {"success": f"Success to install PostgreSQL server. cmd:{_cmd}"}

    def audited_by(self, logger:logging.Logger, args:argparse.Namespace) -> bool:
        """
        この機能が監査ログを記録する対象かどうかを返します

        Returns:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            bool: 監査ログを記録する場合はTrue
        """
        return False
