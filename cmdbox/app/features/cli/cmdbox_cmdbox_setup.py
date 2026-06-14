from cmdbox.app import common, feature
from cmdbox.app.commons import resdata, validator
from cmdbox.app.features.cli import cmdbox_server_start, cmdbox_server_stop
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import threading
import pydantic
import yaml


class CmdboxSetup(feature.OneshotEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language = None):
        super().__init__(appcls, ver, language)
        self.server_start = cmdbox_server_start.ServerStart(appcls, ver, language)
        self.server_stop = cmdbox_server_stop.ServerStop(appcls, ver, language)

    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'cmdbox'

    def get_cmd(self) -> str:
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'setup'

    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_MEIGHT, nouse_webmode=True, use_agent=False,
            description_ja=f"セットアップファイルを読み込み、記載されたコマンドを順番に実行します。",
            description_en=f"Reads a setup file and executes the listed commands in order.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。",
                     description_en="Specify the access password of the Redis server (optional). If omitted, `password` is used."),
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HOME/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HOME/.{self.ver.__appid__}` is used."),
                dict(opt="chopt", type=Options.T_DICT, default=None, required=False, multi=True, hide=True, choice=None,
                     description_ja="setup.ymlに記載しているコマンドのオプションを変更します。オプション名をキーに、変更後の値をバリューとする辞書を指定します。例: `--chopt host=redis`",
                     description_en="Change the options for the commands specified in the YML file. Specify a dictionary where the option name is the key and the new value is the value. Example: `--chopt host=redis`"),
                dict(opt="retry_count", type=Options.T_INT, default=20, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                     description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="setup_file", type=Options.T_FILE, default=f".{self.ver.__appid__}_initdata/setup.yml", required=True, multi=False, hide=False, choice=None, fileio="in",
                     description_ja=f"セットアップファイルのパスを指定します。デフォルトは `.{self.ver.__appid__}_initdata/setup.yml` です。",
                     description_en=f"Specify the path to the setup file. Default is `.{self.ver.__appid__}_initdata/setup.yml`."),
            ]
        )

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
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
        # サーバーを起動
        args.svname = f"{self.ver.__appid__}_setup"
        sv_start = threading.Thread(target=self.server_start.apprun, args=(logger, args, tm, pf))
        sv_start.start()
        has_warn = False
        try:
            # セットアップファイルをチェック
            setup_file = Path(args.setup_file)
            if not setup_file.exists():
                ret = dict(warn=f"Setup file not found: '{setup_file}'")
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, ret, None

            with open(setup_file, 'r', encoding='utf-8') as f:
                setup_data = yaml.safe_load(f)

            if not setup_data or 'setups' not in setup_data:
                ret = dict(warn=f"No 'setups' key found in setup file: '{setup_file}'")
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, ret, None

            setups = setup_data['setups']
            if not isinstance(setups, list):
                ret = dict(warn=f"'setups' must be a list in setup file: '{setup_file}'")
                common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, ret, None

            # セットアップを順番に実行
            results = []
            app = self.appcls.getInstance()
            def to_val(val):
                if isinstance(val, bool):
                    return val
                if isinstance(val, str):
                    ret = val.lower() == 'true'
                    if ret: return True
                return f"'{val}'"
            for i, setup in enumerate(setups):
                name = setup.get('name', f'setup_{i}')
                description = setup.get('description', '')
                exec_conf = setup.get('exec', {})
                chopt = args.chopt and {k:to_val(v) for k,v in args.chopt.items()} or {}
                exec_conf.update(chopt)  # コマンドラインのオプション変更を反映

                if not exec_conf:
                    logger.warning(f"Setup '{name}': No 'exec' configuration found. Skipping.")
                    results.append(dict(name=name, description=description, status='warn', result=dict(warn='No exec configuration found')))
                    has_warn = True
                    continue
                
                args_list = self._build_args_list(exec_conf)
                logger.info(f"Setup '{name}': Executing: {' '.join(str(a) for a in args_list)}")
                try:
                    status, res, _ = app.main(args_list)
                    status_str = 'success' if status == self.RESP_SUCCESS else 'warn'
                    if status != self.RESP_SUCCESS:
                        has_warn = True
                    results.append(dict(name=name, description=description, status=status_str, result=res))
                except Exception as e:
                    logger.warning(f"Setup '{name}': Exception: {e}", exc_info=True)
                    results.append(dict(name=name, description=description, status='error', result=dict(error=str(e))))
                    has_warn = True
        except Exception as e:
            logger.error(f"Exception during setup execution: {e}", exc_info=True)
            ret = dict(error=str(e))
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_ERROR, ret, None
        finally:
            # サーバーを停止
            sv_stop = threading.Thread(target=self.server_stop.apprun, args=(logger, args, tm, pf))
            sv_stop.start()
            sv_start.join()
            sv_stop.join()

        if not has_warn:
            ret = dict(success=dict(data=results))
        else:
            ret = dict(warn=dict(data=results))
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if has_warn:
            return self.RESP_WARN, ret, None
        return self.RESP_SUCCESS, ret, None

    def _build_args_list(self, exec_conf: Dict[str, Any]) -> List[str]:
        """
        exec設定辞書からコマンドライン引数リストを構築します。

        Args:
            exec_conf (Dict[str, Any]): exec設定辞書

        Returns:
            List[str]: コマンドライン引数リスト
        """
        args_list = []
        # mode と cmd を先頭に追加
        if 'mode' in exec_conf and exec_conf['mode'] is not None:
            args_list += ['-m', str(exec_conf['mode'])]
        if 'cmd' in exec_conf and exec_conf['cmd'] is not None:
            args_list += ['-c', str(exec_conf['cmd'])]
        mod_path = Path(self.ver.__file__).parent
        cur_path = mod_path.parent
        # それ以外のオプションを追加
        for key, value in exec_conf.items():
            local_env = dict(Path=Path, self=self, cur_path=cur_path, appid=self.ver.__appid__, mod_path=mod_path, key=key)
            if key in ('mode', 'cmd') or value is None:
                continue
            if isinstance(value, bool):
                if value:
                    args_list += [f'--{key}']
            elif isinstance(value, list):
                for v in value:
                    v = eval(v, dict(Path=Path), local_env) if isinstance(v, str) else v
                    args_list += [f'--{key}', v]
            else:
                value = eval(value, dict(Path=Path), local_env) if isinstance(value, str) else value
                args_list += [f'--{key}', value]
        return args_list

    def output_schema(self) -> type:
        class SetupResult(resdata.Base):
            model_config = resdata.Base.forbid_off()
            name: Union[str, None] = pydantic.Field(default=None, description="セットアップ名")
            description: Union[str, None] = pydantic.Field(default=None, description="説明文")
            status: Union[str, None] = pydantic.Field(default=None, description="実行結果ステータス (success/warn/error)")
            result: Union[Dict[str, Any], None] = pydantic.Field(default=None, description="実行結果")
        class Data(resdata.Data):
            data: Union[List[SetupResult], None] = pydantic.Field(default=None, description="各セットアップの実行結果リスト")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
