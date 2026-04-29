from cmdbox.app import common, feature
from cmdbox.app.commons import validator
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import os
import platform
import signal
import traceback


class McpsvStop(feature.UnsupportEdgeFeature, validator.Validator):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'mcpsv'

    def get_cmd(self):
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'stop'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=True, use_agent=False,
            description_ja="MCP サーバーを停止します。",
            description_en="Stop MCP server.",
            choice=[
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HONE/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HONE/.{self.ver.__appid__}` is used."),
            ]
        )

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        st, msg, cl = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, cl
        try:
            def _r(f):
                pid = f.read()
                if pid != "":
                    try:
                        if platform.system() == "Windows":
                            os.system(f"taskkill /F /PID {pid}")
                        else:
                            os.kill(int(pid), signal.SIGKILL)
                        logger.info(f"Stop mcpsv.")
                    except Exception:
                        logger.warning(f"Failed to stop process pid={pid}")
                else:
                    logger.warning(f"pid is empty.")

            common.load_file("mcpsv.pid", _r, nolock=True)
            Path("mcpsv.pid").unlink(missing_ok=True)
            msg = dict(success="mcpsv complate.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SUCCESS, msg, None
        except Exception:
            traceback.print_exc()
            logger.error("Exit mcpsv.")
            msg = dict(warn="mcpsv stop error.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
