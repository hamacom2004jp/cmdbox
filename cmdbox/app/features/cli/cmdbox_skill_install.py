from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import io
import json
import logging
import pydantic
import shutil
import tempfile
import zipfile
import re


class SkillInstall(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'skill'

    def get_cmd(self) -> str:
        return 'install'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="Agent Skillsのzipアーカイブをdata配下へインストールします。",
            description_en="Install an Agent Skills zip archive into the data directory.",
            choice=[
                 dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                 dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                 dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                     description_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                 dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                     description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                 dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                 dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                 dict(opt="timeout", type=Options.T_INT, default=120, required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="skill_file", type=Options.T_FILE, default=None, required=True, multi=False, hide=False, choice=None, fileio="in",
                     description_ja="インストールするスキルzipファイルを指定します。",
                     description_en="Specify the skill zip file to install."),
                dict(opt="skill_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="インストール先スキル名を指定します。省略時はzip名から推定します。",
                     description_en="Specify destination skill name. If omitted, inferred from zip name."),
                dict(opt="overwrite", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="既存スキルがある場合に上書きします。",
                     description_en="Overwrite when the target skill already exists."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float,
               pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        skill_file = Path(str(args.skill_file)).resolve()
        if not skill_file.exists() or not skill_file.is_file():
            ret = dict(warn=f"Skill file not found: '{skill_file}'")
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, ret, None

        payload = dict(
            skill_file_name=skill_file.name,
            skill_file_data=convert.bytes2b64str(skill_file.read_bytes()),
            skill_name=args.skill_name,
            overwrite=bool(args.overwrite),
        )
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            skill_file_data = payload.get('skill_file_data')
            skill_name = payload.get('skill_name')
            overwrite = bool(payload.get('overwrite', False))
            if skill_file_data is None:
                redis_cli.rpush(reskey, dict(warn='skill_file_data is empty.'))
                return self.RESP_WARN

            zip_bytes = convert.b64str2bytes(skill_file_data)
            skill_dir = data_dir / '.skills' / skill_name
            if skill_dir.exists():
                if not overwrite:
                    redis_cli.rpush(reskey, dict(warn=f"Skill '{skill_name}' already exists at '{skill_dir}'."))
                    return self.RESP_WARN
                shutil.rmtree(skill_dir, ignore_errors=True)

            with tempfile.TemporaryDirectory(prefix='skill_install_') as tmp:
                tmpdir = Path(tmp)
                try:
                    with zipfile.ZipFile(io.BytesIO(zip_bytes), 'r') as zf:
                        dst_resolved = tmpdir.resolve()
                        for info in zf.infolist():
                            p = Path(info.filename)
                            if p.is_absolute() or '..' in p.parts:
                                raise ValueError(f"Unsafe path in archive: {info.filename}")
                            out_path = (tmpdir / p).resolve()
                            if not str(out_path).startswith(str(dst_resolved)):
                                raise ValueError(f"Unsafe extraction target: {info.filename}")
                        zf.extractall(tmpdir)
                except zipfile.BadZipFile:
                    redis_cli.rpush(reskey, dict(warn=f"Invalid zip archive."))
                    return self.RESP_WARN

                skill_root = None
                root_skill_md = tmpdir / 'SKILL.md'
                if root_skill_md.exists() and root_skill_md.is_file():
                    skill_root = tmpdir
                if skill_root is None:
                    children = [p for p in tmpdir.iterdir()]
                    if len(children) == 1 and children[0].is_dir() and (children[0] / 'SKILL.md').exists():
                        skill_root = children[0]
                if skill_root is None:
                    found = list(tmpdir.rglob('SKILL.md'))
                    found = [p for p in found if p.name == 'SKILL.md']
                    if len(found) == 1:
                        skill_root = found[0].parent
                    elif len(found) == 0:
                        redis_cli.rpush(reskey, dict(warn='SKILL.md was not found in archive.'))
                        return self.RESP_WARN
                    else:
                        redis_cli.rpush(reskey, dict(warn='Multiple SKILL.md files found in archive.'))
                        return self.RESP_WARN
                shutil.copytree(skill_root, skill_dir, dirs_exist_ok=True)

            ret = dict(success=dict(skill_name=skill_name, path=str(skill_dir), skill_md=str(skill_dir / 'SKILL.md')))
            logger.info(f"Installed skill '{skill_name}' to '{skill_dir}'.")
            redis_cli.rpush(reskey, ret)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN

    def output_schema(self) -> type:
        class Data(resdata.Data):
            skill_name: Union[str, None] = pydantic.Field(default=None, description="スキル名")
            path: Union[str, None] = pydantic.Field(default=None, description="インストール先パス")
            skill_md: Union[str, None] = pydantic.Field(default=None, description="SKILL.mdパス")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
