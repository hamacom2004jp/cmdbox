from cmdbox.app import common, feature
from cmdbox.app.commons import resdata, validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import os
import platform
import pydantic
import signal
import traceback


class LlmProxyStop(feature.UnsupportEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'llm'

    def get_cmd(self) -> str:
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'proxy_stop'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=True, use_agent=False,
            description_ja="LiteLLM Proxyサービスを停止します。",
            description_en="Stop LiteLLM Proxy service.",
            choice=[
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HOME/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HOME/.{self.ver.__appid__}` is used."),
                dict(opt="proxy_listen_port", type=Options.T_INT, default=4000, required=False, multi=False, hide=False, choice=None,
                     description_ja="停止する LiteLLM Proxy の待ち受けポートを指定します。省略時は `4000` です。",
                     description_en="Specify the listening port of LiteLLM Proxy to stop. Default is `4000`."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]):
        """
        この機能の実行を行います

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        try:
            proxy_dir = Path(args.data) / ".agent" / f"llmproxy-{args.proxy_listen_port}"
            pid_path = proxy_dir / "llmproxy.pid"
            if not pid_path.is_file():
                msg = dict(warn=f"LiteLLM Proxy pid file is not found. path={pid_path}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

            def _r(f):
                return f.read().strip()

            pid = common.load_file(pid_path, _r, nolock=True)
            if pid == "":
                msg = dict(warn=f"LiteLLM Proxy pid is empty. path={pid_path}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

            try:
                if platform.system() == "Windows":
                    os.system(f"taskkill /F /PID {pid}")
                else:
                    os.kill(int(pid), signal.SIGKILL)
                logger.info(f"Stop LiteLLM Proxy. pid={pid}")
            except Exception:
                logger.warning(f"Failed to stop LiteLLM Proxy process pid={pid}")

            pid_path.unlink(missing_ok=True)
            msg = dict(success=dict(
                message="LiteLLM Proxy stopped.",
                pid=int(pid),
                proxy_listen_port=int(args.proxy_listen_port),
                pid_path=str(pid_path),
            ))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, msg, None
        except Exception:
            traceback.print_exc()
            logger.error("Exit LiteLLM Proxy stop.")
            msg = dict(warn="LiteLLM Proxy stop error.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

    def output_schema(self) -> type:
        class Data(resdata.Data):
            pid: Union[int, None] = pydantic.Field(default=None, description="停止したプロセスID")
            proxy_listen_port: Union[int, None] = pydantic.Field(default=None, description="停止対象ポート")
            pid_path: Union[str, None] = pydantic.Field(default=None, description="PIDファイルパス")
            message: Union[str, None] = pydantic.Field(default=None, description="実行結果メッセージ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
