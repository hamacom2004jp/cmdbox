from cmdbox import version
from cmdbox.app import common, feature
from cmdbox.app.commons import resdata, validator
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import pydantic
import subprocess


PYTHON_IMAGE = 'cmdbox-python-sandbox:latest'


class CmdboxPythonInstall(feature.OneshotEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        return 'cmdbox'

    def get_cmd(self) -> str:
        return 'python_install'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True, use_agent=False,
            description_ja="Pythonサンドボックス用Dockerイメージをビルド/インストールします。",
            description_en="Builds/installs the Docker image for the Python sandbox.",
            choice=[]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        common.set_debug(logger, True)
        try:
            compose_path = str(Path(self.ver.__file__).parent / 'docker' / 'python' / 'docker-compose.yml')
            if not Path(compose_path).exists():
                compose_path = str(Path(version.__file__).parent / 'docker' / 'python' / 'docker-compose.yml')
            cmd = f"docker compose -f {compose_path} build"
            returncode, _, _cmd = common.cmd(f"{cmd}", logger, slise=-1)
            if returncode != 0:
                ret = dict(warn=f"Failed to build image: {_cmd[:500]}")
            else:
                ret = dict(success=f"Image built successfully using {compose_path}.: {_cmd[:500]}")
        except Exception as e:
            ret = dict(warn=f"Failed to build image: {e}")
        finally:
            common.set_debug(logger, False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: Union[str, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
