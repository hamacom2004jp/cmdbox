from cmdbox.app import common, feature
from cmdbox.app.commons import resdata, validator
from cmdbox.app.features.cli import cmdbox_llm_load
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import os
import platform
import pydantic
import shutil
import subprocess
import time
import yaml


class LlmProxyStart(feature.UnsupportEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language:str=None):
        super().__init__(appcls, ver, language)
        self.llm_loader = cmdbox_llm_load.LLMLoad(appcls, ver, language)

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
        return 'proxy_start'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
              use_redis=self.USE_REDIS_TRUE, nouse_webmode=True, use_agent=False,
            description_ja="LiteLLM Proxyサービスを起動します。",
            description_en="Start LiteLLM Proxy service.",
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
                     description_en="Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."),
                 dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                 dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="data", type=Options.T_DIR, default=self.default_data, required=False, multi=False, hide=False, choice=None, web="mask",
                     description_ja=f"省略した時は `$HOME/.{self.ver.__appid__}` を使用します。",
                     description_en=f"When omitted, `$HOME/.{self.ver.__appid__}` is used."),
                dict(opt="proxy_allow_host", type=Options.T_STR, default="0.0.0.0", required=False, multi=False, hide=False, choice=None,
                     description_ja="バインドするホスト名を指定します。省略時は `0.0.0.0` です。",
                     description_en="Specify the bind host name. Default is `0.0.0.0`."),
                dict(opt="proxy_listen_port", type=Options.T_INT, default=4000, required=False, multi=False, hide=False, choice=None,
                     description_ja="LiteLLM Proxy の待ち受けポートを指定します。省略時は `4000` です。",
                     description_en="Specify the listening port of LiteLLM Proxy. Default is `4000`."),
                 dict(opt="proxy_workers", type=Options.T_INT, default=3, required=False, multi=False, hide=False, choice=None,
                     description_ja="LiteLLM Proxy のワーカー数を指定します。省略時は `3` です。",
                     description_en="Specify the number of workers for LiteLLM Proxy. Default is `3`."),
                dict(opt="proxy_apikey", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="LiteLLM Proxy の API キーを指定します。必ず「sk-」で始まる値を使用してください。",
                     description_en="Specify the API key for LiteLLM Proxy. It must start with 'sk-'."),
                dict(opt="llm", type=Options.T_STR, default=None, required=True, multi=True, hide=False, choice=[],
                     callcmd="async () => {await cmdbox.callcmd('llm','list',{},(res)=>{"
                             + "const val = $(\"[name='llm']\").val() || [];"
                             + "$(\"[name='llm']\").empty();"
                             + "res['data'].map(elm=>{$(\"[name='llm']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                             + "$(\"[name='llm']\").val(val);"
                             + "},$(\"[name='title']\").val(),'llm');"
                             + "}",
                     description_ja="Proxyに登録するLLM設定名を複数指定します。指定順をフェイルオーバー優先順として扱います。",
                     description_en="Specify multiple LLM configuration names to register to the proxy. The specified order is used as failover priority."),
                dict(opt="num_retries", type=Options.T_INT, default=2, required=False, multi=False, hide=False, choice=None,
                     description_ja="LiteLLM Router の再試行回数を指定します。",
                     description_en="Specify retry count for LiteLLM Router."),
                dict(opt="request_timeout", type=Options.T_INT, default=60, required=False, multi=False, hide=False, choice=None,
                     description_ja="LiteLLM Proxy のリクエストタイムアウト秒を指定します。",
                     description_en="Specify request timeout seconds for LiteLLM Proxy."),
                dict(opt="allowed_fails", type=Options.T_INT, default=3, required=False, multi=False, hide=False, choice=None,
                     description_ja="クールダウン判定の失敗回数しきい値を指定します。",
                     description_en="Specify failure threshold for cooldown."),
                dict(opt="cooldown_time", type=Options.T_INT, default=30, required=False, multi=False, hide=False, choice=None,
                     description_ja="クールダウン時間(秒)を指定します。",
                     description_en="Specify cooldown duration in seconds."),
            ]
        )

    @validator.apprun_check
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
        if args.proxy_apikey is None or not args.proxy_apikey.startswith("sk-"):
            msg = dict(warn="Please specify a valid LiteLLM Proxy API key starting with 'sk-'.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        llm_names = args.llm if isinstance(args.llm, list) else [args.llm]
        llm_names = list(set([n for n in llm_names if isinstance(n, str) and n.strip() != ""]))

        if len(llm_names) <= 0:
            msg = dict(warn="Please specify one or more --llm options.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        litellm_exe = shutil.which("litellm")
        if litellm_exe is None:
            msg = dict(warn="LiteLLM command was not found. Install litellm and ensure `litellm` is in PATH.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        try:
            data_dir = Path(args.data)
            cfg = self._build_proxy_config(logger, data_dir, llm_names, args)
            proxy_dir = data_dir / ".agent" / f"llmproxy-{args.proxy_listen_port}"
            proxy_dir.mkdir(parents=True, exist_ok=True)
            config_path = proxy_dir / "config.yaml"
            pid_path = proxy_dir / "llmproxy.pid"
            common.save_file(config_path, lambda f: yaml.safe_dump(cfg, f, allow_unicode=False, sort_keys=False),
                             encoding='utf-8', nolock=False)
            
            # Check if proxy is already running on the same port
            if pid_path.is_file():
                def _read_pid(f):
                    return f.read().strip()
                try:
                    existing_pid_str = common.load_file(pid_path, _read_pid, nolock=True)
                    if existing_pid_str and existing_pid_str != "":
                        try:
                            existing_pid = int(existing_pid_str)
                            is_running = False
                            if platform.system() == "Windows":
                                # Windows: tasklist で確認
                                result = subprocess.run(['tasklist', '/FI', f'PID eq {existing_pid}'], 
                                                      capture_output=True, text=True, timeout=5)
                                is_running = str(existing_pid) in result.stdout
                            else:
                                # Linux/Mac: os.kill で signal.0 を送信してプロセス存在確認
                                try:
                                    os.kill(existing_pid, 0)
                                    is_running = True
                                except (ProcessLookupError, OSError):
                                    is_running = False
                            
                            if is_running:
                                msg = dict(warn=f"LiteLLM Proxy is already running on port {args.proxy_listen_port}. pid={existing_pid}")
                                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                                return self.RESP_WARN, msg, None
                        except ValueError:
                            # PID が数値でない場合はスキップ
                            pass
                except Exception as e:
                    logger.warning(f"Failed to check existing process. {e}")
            
            cmd = [
                litellm_exe,
                "--config", str(config_path),
                "--host", str(args.proxy_allow_host),
                "--port", str(args.proxy_listen_port),
            ]
            if platform.system() != "Windows":
                cmd.extend(["--num_workers", str(args.proxy_workers)])
            proc = subprocess.Popen(cmd)
            common.save_file(pid_path, lambda f: f.write(str(proc.pid)), encoding='utf-8', nolock=False)
            msg = dict(success=dict(
                message="LiteLLM Proxy started. Press Ctrl+C to stop.",
                pid=proc.pid,
                config_path=str(config_path),
                proxy_allow_host=str(args.proxy_allow_host),
                proxy_listen_port=int(args.proxy_listen_port),
                proxy_workers=int(args.proxy_workers),
                llm=llm_names,
            ))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            try:
                while proc.poll() is None:
                    time.sleep(1)
            except KeyboardInterrupt:
                proc.terminate()
                try:
                    proc.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    proc.kill()

            return self.RESP_SUCCESS, msg, proc
        except Exception as e:
            logger.warning(f"Failed to start LiteLLM Proxy. {e}", exc_info=True)
            msg = dict(warn=f"Failed to start LiteLLM Proxy. {e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

    def _build_proxy_config(self, logger:logging.Logger, data_dir:Path, llm_names:List[str], args:argparse.Namespace) -> Dict[str, Any]:
        model_list: List[Dict[str, Any]] = []
        for llm_name in llm_names:
            llm_conf = self._load_llm_config_via_apprun(logger=logger, args=args, llm_name=llm_name)
            deployment = self._to_proxy_deployment(llm_name, llm_conf)
            model_list.append(deployment)
        # 指定順を優先しつつ、障害時には他候補へフォールバックする。
        fallbacks = []
        for name in llm_names:
            others = [n for n in llm_names if n != name]
            if others:
                fallbacks.append({name: others})
        return dict(
            model_list=model_list,
            litellm_settings=dict(
                num_retries=int(args.num_retries),
                request_timeout=int(args.request_timeout),
                allowed_fails=int(args.allowed_fails),
                cooldown_time=int(args.cooldown_time),
                fallbacks=fallbacks,
            ),
            general_settings=dict(
                master_key=args.proxy_apikey,
            ),
        )

    def _load_llm_config_via_apprun(self, logger:logging.Logger, args:argparse.Namespace, llm_name:str) -> Dict[str, Any]:
        load_args = argparse.Namespace(
            host=args.host,
            port=args.port,
            password=args.password,
            svname=args.svname,
            retry_count=args.retry_count,
            retry_interval=args.retry_interval,
            timeout=args.timeout,
            llmname=llm_name,
            format=False,
            output_json=None,
            output_json_append=False,
        )
        st, ret, _ = self.llm_loader.apprun(logger, load_args, tm=0.0, pf=[])
        if st != self.RESP_SUCCESS or 'success' not in ret:
            warn = ret.get('warn', f"Failed to load llm configuration by llm load command. llm={llm_name}")
            raise RuntimeError(str(warn))
        return ret['success']

    def _to_proxy_deployment(self, llm_name:str, llm_conf:Dict[str, Any]) -> Dict[str, Any]:
        llmprov = llm_conf.get('llmprov', None)
        llmmodel = llm_conf.get('llmmodel', None)
        llmendpoint = llm_conf.get('llmendpoint', None)
        llmapikey = llm_conf.get('llmapikey', None)
        llmapiversion = llm_conf.get('llmapiversion', None)
        llmlocation = llm_conf.get('llmlocation', None)
        llmseed = llm_conf.get('llmseed', None)
        llmtemperature = llm_conf.get('llmtemperature', None)
        llmsvaccountfile_data = llm_conf.get('llmsvaccountfile_data', None)

        if llmprov is None:
            raise ValueError(f"llmprov is required. llm={llm_name}")
        if llmmodel is None:
            raise ValueError(f"llmmodel is required. llm={llm_name}")

        litellm_params: Dict[str, Any] = dict(model=llmmodel)
        # LiteLLM側でキャッシュ課金情報が未設定だと警告が出るため、明示的に設定する。
        model_info = dict(
            cache_creation_input_token_cost=float(llm_conf.get('cache_creation_input_token_cost', 0.0) or 0.0),
            cache_read_input_token_cost=float(llm_conf.get('cache_read_input_token_cost', 0.0) or 0.0),
        )
        if llmprov == 'openai':
            if llmapikey is None:
                raise ValueError(f"llmapikey is required for openai. llm={llm_name}")
            litellm_params['api_key'] = llmapikey
            if llmendpoint is not None:
                litellm_params['api_base'] = llmendpoint
        elif llmprov == 'azureopenai':
            if llmapikey is None:
                raise ValueError(f"llmapikey is required for azureopenai. llm={llm_name}")
            if llmendpoint is None:
                raise ValueError(f"llmendpoint is required for azureopenai. llm={llm_name}")
            if llmapiversion is None:
                raise ValueError(f"llmapiversion is required for azureopenai. llm={llm_name}")
            if "/openai/deployments" in llmendpoint:
                llmendpoint = llmendpoint.split("/openai/deployments")[0]
            if not llmmodel.startswith("azure/"):
                llmmodel = f"azure/{llmmodel}"
            litellm_params['model'] = llmmodel
            litellm_params['api_key'] = llmapikey
            litellm_params['api_base'] = llmendpoint
            litellm_params['api_version'] = llmapiversion
            model_info['base_model'] = llmmodel
        elif llmprov == 'ollama':
            if llmendpoint is None:
                raise ValueError(f"llmendpoint is required for ollama. llm={llm_name}")
            if not llmmodel.startswith("ollama/"):
                llmmodel = f"ollama/{llmmodel}"
            litellm_params['model'] = llmmodel
            litellm_params['api_base'] = llmendpoint
            if llmtemperature is not None:
                litellm_params['temperature'] = llmtemperature
        elif llmprov == 'vertexai':
            if llmlocation is None:
                raise ValueError(f"llmlocation is required for vertexai. llm={llm_name}")
            if llmsvaccountfile_data is None:
                raise ValueError(f"llmsvaccountfile_data is required for vertexai. llm={llm_name}")
            litellm_params['vertex_location'] = llmlocation
            litellm_params['vertex_credentials'] = llmsvaccountfile_data
            if llmseed is not None:
                litellm_params['seed'] = llmseed
            if llmtemperature is not None:
                litellm_params['temperature'] = llmtemperature
        elif llmprov == 'custom':
            if llmapikey is not None:
                litellm_params['api_key'] = llmapikey
            if llmendpoint is not None:
                litellm_params['api_base'] = llmendpoint
            if llmapiversion is not None:
                litellm_params['api_version'] = llmapiversion
            if llmtemperature is not None:
                litellm_params['temperature'] = llmtemperature
            if llmseed is not None:
                litellm_params['seed'] = llmseed
        else:
            raise ValueError(f"Unsupported llm provider: {llmprov}. llm={llm_name}")
        return dict(model_name=llm_name, litellm_params=litellm_params, model_info=model_info)

    def output_schema(self) -> type:
        class Data(resdata.Data):
            pid: Union[int, None] = pydantic.Field(default=None, description="起動したプロセスID")
            config_path: Union[str, None] = pydantic.Field(default=None, description="生成したLiteLLM設定ファイルパス")
            proxy_allow_host: Union[str, None] = pydantic.Field(default=None, description="待ち受けホスト")
            proxy_listen_port: Union[int, None] = pydantic.Field(default=None, description="待ち受けポート")
            proxy_workers: Union[int, None] = pydantic.Field(default=None, description="LiteLLM Proxy ワーカー数")
            llm: List[str] = pydantic.Field(default_factory=list, description="登録したLLM設定名")
            message: Union[str, None] = pydantic.Field(default=None, description="実行結果メッセージ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result
