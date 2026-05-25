from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import os
import pydantic
import subprocess
import tempfile


class CmdboxPythonRun(feature.OneshotEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'cmdbox'

    def get_cmd(self) -> str:
        return 'python_run'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True, use_agent=True,
            description_ja="任意のPythonコードをサンドボックス内で実行します。",
            description_en="Executes arbitrary Python code in a sandbox.",
            choice=[
                dict(opt="code", type=Options.T_TEXT, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="実行するPythonコードを指定します。",
                    description_en="Specify the Python code to execute."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        common.set_debug(logger, True)
        try:
            compose_path = str(Path(self.ver.__file__).parent / 'docker' / 'python' / 'docker-compose.yml')
            if not Path(compose_path).exists():
                compose_path = str(Path(version.__file__).parent / 'docker' / 'python' / 'docker-compose.yml')
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', encoding='utf-8') as f:
                f.write(args.code)
                cmd = f"docker compose -f {compose_path} run -v {f.name}:/sandbox/{f.name} --rm cmdbox-python-sandbox python3 /sandbox/{f.name}"
                returncode, _, _cmd = common.cmd(f"{cmd}", logger, slise=-1)
                if returncode != 0:
                    ret = dict(warn=f"Python execution failed (rc={returncode}): {_cmd[:500]}")
                else:
                    ret = dict(success=dict(data=f"Image run successfully using {compose_path}.: {_cmd[:500]}"))
        except subprocess.TimeoutExpired:
            ret = dict(warn="Python execution timed out (300s).")
        except Exception as e:
            ret = dict(warn=f"Python execution failed: {e}")
        finally:
            common.set_debug(logger, False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: str = pydantic.Field(default='', description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
