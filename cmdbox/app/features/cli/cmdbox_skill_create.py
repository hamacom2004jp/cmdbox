from cmdbox.app import common, feature
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import json
import logging
import pydantic
import re
import tempfile
import zipfile


class SkillCreate(feature.OneshotResultEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'skill'

    def get_cmd(self) -> str:
        return 'create'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="コマンド定義ファイルを元に Agent Skill の zip を作成します。",
            description_en="Create an Agent Skill zip from a command definition file.",
            choice=[
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HOME/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HOME/.{self.ver.__appid__}` is used."),
                dict(opt="from_cmd_title", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                     callcmd="async () => {await cmdbox.callcmd('cmd','list',{},"
                            + "(res)=>{const val = $(\"[name='from_cmd_title']\").val();"
                            + "$(\"[name='from_cmd_title']\").empty().append('<option></option>');"
                            + "res['data'].forEach(elm=>{$(\"[name='from_cmd_title']\").append('<option value=\"'+elm[\"title\"]+'\">'+elm[\"title\"]+'</option>');});"
                            + "$(\"[name='from_cmd_title']\").val(val);"
                            + "},$(\"[name='from_cmd_title']\").val(),'from_cmd_title');"
                            + "}",
                     description_ja="スキル化するコマンドタイトルを指定します。",
                     description_en="Specify the command title to convert into a skill."),
                dict(opt="skill_name", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="作成するスキル名を指定します。省略時は from_cmd_title から生成します。",
                     description_en="Specify the skill name. If omitted, generated from from_cmd_title."),
                dict(opt="skill_instruction", type=Options.T_TEXT, default=None, required=False, multi=False, hide=True, choice=None,
                     description_ja="SKILL.md 本文の instruction を指定します。",
                     description_en="Specify the instruction body in SKILL.md."),
                dict(opt="output_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None, fileio="out",
                     description_ja="出力する zip ファイルパスを指定します。省略時はカレントに `<skill_name>.zip` を作成します。",
                     description_en="Output zip file path. If omitted, creates `<skill_name>.zip` in current directory."),
                dict(opt="overwrite", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="出力先が既に存在する場合に上書きします。",
                     description_en="Overwrite when output file already exists."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float,
               pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        data_dir = Path(args.data).resolve() if args.data is not None else Path(self.default_data).resolve()
        instruction = getattr(args, 'skill_instruction', None)

        ret = self._create_skill_zip(
            logger=logger,
            data_dir=data_dir,
            from_cmd_title=str(args.from_cmd_title),
            skill_name=getattr(args, 'skill_name', None),
            skill_instruction=instruction,
            output_file=getattr(args, 'output_file', None),
            overwrite=bool(getattr(args, 'overwrite', False)),
        )
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def _create_skill_zip(self, logger: logging.Logger, data_dir: Path, from_cmd_title: str,
                          skill_name: str = None,
                          skill_instruction: str = None,
                          output_file: str = None,
                          overwrite: bool = False) -> Dict[str, Any]:
        try:
            cmd_path = data_dir / '.cmds' / f'cmd-{from_cmd_title}.json'
            if not cmd_path.exists() or not cmd_path.is_file():
                raise FileNotFoundError(f"Command file not found: '{cmd_path}'")
            cmd_opt = common.loadopt(cmd_path, True)
            if not isinstance(cmd_opt, dict) or 'mode' not in cmd_opt or 'cmd' not in cmd_opt:
                raise ValueError(f"Invalid command file format: '{cmd_path}'")
        except Exception as e:
            return dict(warn=str(e))

        # ADK compatibility: prefer lowercase kebab-case.
        name_src = skill_name if skill_name else from_cmd_title
        name = name_src.strip().lower().replace('_', '-')
        name = re.sub(r'[^a-z0-9-]+', '-', name)
        name = re.sub(r'-{2,}', '-', name)
        name = name.strip('-')
        if not name:
            return dict(warn='skill_name is empty after normalization.')

        mode = cmd_opt.get('mode', '')
        cmd = cmd_opt.get('cmd', '')
        description = cmd_opt.get('description', '')
        if not description:
            options = Options.getInstance()
            description = options.get_cmd_attr(mode, cmd, 'description_ja')
            if not description:
                description = options.get_cmd_attr(mode, cmd, 'description_en')
            if not description:
                description = f"Execute cmdbox command '{from_cmd_title}'."
        if skill_instruction:
            instruction = skill_instruction
        else:
            instruction = (
                "このスキルは cmdbox の登録済みコマンドを実行するための補助スキルです。\n\n"
                "実行手順:\n"
                "1. 必要な引数を利用者に確認する。\n"
                "2. モードとコマンドを固定し、必要に応じて追加オプションを組み立てる。\n"
                "3. 実行前に破壊的操作かどうかを確認する。\n\n"
                f"- from_cmd_title: {from_cmd_title}\n"
                f"- mode: {mode}\n"
                f"- cmd: {cmd}\n\n"
                "詳細な既定パラメータは `references/command.json` を参照してください。"
            )

        out_path = Path(output_file).resolve() if output_file else (Path.cwd() / f'{name}.zip').resolve()
        out_path.parent.mkdir(parents=True, exist_ok=True)
        if out_path.exists():
            if not overwrite:
                return dict(warn=f"Output file already exists: '{out_path}'")
            out_path.unlink()

        with tempfile.TemporaryDirectory(prefix='skill_create_') as tmp:
            tmpdir = Path(tmp)
            root = tmpdir / name
            refs = root / 'references'
            refs.mkdir(parents=True, exist_ok=True)

            (refs / 'command.json').write_text(
                json.dumps(cmd_opt, ensure_ascii=False, indent=2),
                encoding='utf-8',
            )
            desc = str(description).replace('\r\n', '\n').replace('\n', ' ').strip()
            desc = desc.replace('"', '\\"')
            skill_md = (
                "---\n"
                f"name: {name}\n"
                f"description: \"{desc}\"\n"
                "---\n\n"
                f"{instruction}\n"
            )
            (root / 'SKILL.md').write_text(
                skill_md,
                encoding='utf-8',
            )

            with zipfile.ZipFile(out_path, 'w', compression=zipfile.ZIP_DEFLATED) as zf:
                for p in root.rglob('*'):
                    if not p.is_file():
                        continue
                    arcname = (Path(root.name) / p.relative_to(root)).as_posix()
                    zf.write(p, arcname)

        logger.info(f"Created skill zip '{out_path}' from from_cmd_title='{from_cmd_title}'.")
        return dict(success=dict(
            from_cmd_title=from_cmd_title,
            skill_name=name,
            output_file=str(out_path),
            skill_md='SKILL.md',
            command_ref='references/command.json',
        ))

    def output_schema(self) -> type:
        class Data(resdata.Data):
            from_cmd_title: Union[str, None] = pydantic.Field(default=None, description="元コマンドタイトル")
            skill_name: Union[str, None] = pydantic.Field(default=None, description="作成したスキル名")
            output_file: Union[str, None] = pydantic.Field(default=None, description="作成したzipファイル")
            skill_md: Union[str, None] = pydantic.Field(default=None, description="zip内SKILL.mdパス")
            command_ref: Union[str, None] = pydantic.Field(default=None, description="zip内コマンド参照JSONパス")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
