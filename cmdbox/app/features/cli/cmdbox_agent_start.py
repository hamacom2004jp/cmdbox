from cmdbox.app import common, client, feature
from cmdbox.app.auth import signin
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re
import platform


class AgentStart(feature.OneshotResultEdgeFeature):

    def __init__(self, appcls, ver):
        super().__init__(appcls, ver)
        self.call_a2asv_start:bool = False

    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'start'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE,
            nouse_webmode=False,
            use_agent=True,
            description_ja="Runner を起動します。",
            description_en="Starts a runner.",
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
                     description_ja="サーバーのサービス名を指定します。",
                     description_en="Specify the service name of the inference server."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。",
                     description_en="Specifies the number of reconnections to the Redis server."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="120", required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="runner_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="Runner設定の名前を指定します。",
                    description_en="Specify the name of the Runner configuration."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                    description_ja="処理結果jsonの保存先ファイルを指定。",
                    description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="処理結果jsonファイルを追記保存します。",
                    description_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                    description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
                dict(opt="capture_stdout", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                    description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                    description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                    description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if not getattr(args, 'runner_name', None):
            msg = dict(warn="Please specify --runner_name")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not re.match(r'^[\w\-]+$', args.runner_name):
            msg = dict(warn="Runner name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        payload = dict(runner_name=args.runner_name)
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, False, tm, None, False, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def is_cluster_redirect(self):
        return True

    def _load_agent_config(self, data_dir:Path, agent_name:str) -> Dict[str, Any]:
        agent_conf_path = data_dir / ".agent" / f"agent-{agent_name}.json"
        if not agent_conf_path.exists():
            raise FileNotFoundError(f"Specified agent configuration '{agent_name}' not found on server at '{str(agent_conf_path)}'.")
        with agent_conf_path.open('r', encoding='utf-8') as f:
            agent_conf = json.load(f)
        return agent_conf

    def _load_llm_config(self, data_dir:Path, llm_name:str) -> Dict[str, Any]:
        llm_conf_path = data_dir / ".agent" / f"llm-{llm_name}.json"
        if not llm_conf_path.exists():
            raise FileNotFoundError(f"Specified llm configuration '{llm_name}' not found on server at '{str(llm_conf_path)}'.")
        with llm_conf_path.open('r', encoding='utf-8') as f:
            llm_conf = json.load(f)
        return llm_conf

    def _load_mcpsv_config(self, data_dir:Path, mcpservers:List[str]) -> List[Dict[str, Any]]:
        mcpsv_confs = []
        if isinstance(mcpservers, list):
            for mcpsv_name in mcpservers:
                mcpsv_conf_path = data_dir / ".agent" / f"mcpsv-{mcpsv_name}.json"
                if not mcpsv_conf_path.exists():
                    raise FileNotFoundError(f"Specified MCP server configuration '{mcpsv_name}' not found on server at '{str(mcpsv_conf_path)}'.")
                with mcpsv_conf_path.open('r', encoding='utf-8') as f:
                    mcpsv_conf = json.load(f)
                    mcpsv_confs.append(mcpsv_conf)
        return mcpsv_confs

    async def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
                    sessions:Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            if 'agents' not in sessions:
                sessions['agents'] = {}

            payload = json.loads(convert.b64str2str(msg[2]))
            name = payload.get('runner_name')
            if name in sessions['agents']:
                msg = dict(warn=f"Runner '{name}' is already running.", end=True)
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN

            runner_conf_path = data_dir / ".agent" / f"runner-{name}.json"
            if not runner_conf_path.exists():
                msg = dict(warn=f"Specified runner configuration '{name}' not found on server at '{str(runner_conf_path)}'.", end=True)
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN
            with runner_conf_path.open('r', encoding='utf-8') as f:
                runner_conf = json.load(f)

            try:
                agent_conf = self._load_agent_config(data_dir, runner_conf['agent'])
            except Exception as e:
                msg = dict(warn=str(e), end=True)
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN

            try:
                if agent_conf.get('llm', None) is not None:
                    llm_conf = self._load_llm_config(data_dir, agent_conf['llm'])
                else:
                    llm_conf = {}
            except Exception as e:
                msg = dict(warn=str(e), end=True)
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN

            try:
                if agent_conf.get('mcpservers', None) is not None:
                    mcpsv_confs = self._load_mcpsv_config(data_dir, agent_conf['mcpservers'])
                else:
                    mcpsv_confs = []
            except Exception as e:
                msg = dict(warn=str(e), end=True)
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN

            agent = self.create_agent(logger, data_dir, False, agent_conf, llm_conf, mcpsv_confs)
            from google.adk.runners import Runner
            runner = Runner(
                app_name=runner_conf.get('runner_name', self.ver.__appid__),
                agent=agent,
                session_service=self.create_session_service(data_dir, logger, runner_conf),
            )
            sessions['agents'][name] = dict(
                name=name,
                runner=runner
            )
            msg = dict(success=f"Runner '{name}' started successfully.", end=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}", end=True)
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN

    def create_agent(self, logger:logging.Logger, data_dir:Path, disable_remote_agent:bool,
                     agent_conf:Dict[str, Any], llm_conf:Dict[str, Any], mcpsv_confs:List[Dict[str, Any]]) -> Any:
        """
        エージェントを作成します

        Args:
            logger (logging.Logger): ロガー
            data_dir (Path): データディレクトリパス
            disable_remote_agent (bool): リモートエージェントを無効化するかどうか
            agent_conf (Dict[str, Any]): エージェント設定
            llm_conf (Dict[str, Any]): LLM設定
            mcpsv_confs (List[Dict[str, Any]]): MCPサーバー設定リスト

        Returns:
            Agent: エージェント
        """
        if logger.level == logging.DEBUG:
            logger.debug(f"create_agent processing..")
        description = agent_conf.get("agent_description", f"{self.ver.__appid__}に登録されているコマンド提供")
        instruction = agent_conf.get("agent_instruction", f"あなたはコマンドの意味を熟知しているエキスパートです。" + \
                      f"ユーザーがコマンドを実行したいとき、あなたは以下の手順に従ってコマンドを確実に実行してください。\n" + \
                      f"1. ユーザーのクエリからが実行したいコマンドを特定します。\n" + \
                      f"2. コマンド実行に必要なパラメータのなかで、ユーザーのクエリから取得できないものは、コマンド定義にあるデフォルト値を指定して実行してください。\n" + \
                      f"3. もしエラーが発生した場合は、ユーザーにコマンド名とパラメータとエラー内容を提示してください。\n" \
                      f"4. コマンドの実行結果は、json文字列で出力するようにしてください。この時json文字列は「```json」と「```」で囲んだ文字列にしてください。\n")

        if logger.level == logging.DEBUG:
            logger.debug(f"google-adk loading..")
        from google.adk.agents import Agent as AdkAgent

        # App name mismatch警告を回避するためのラッパークラス
        class Agent(AdkAgent):
            pass

        if logger.level == logging.DEBUG:
            logger.debug(f"litellm loading..")
        from google.adk.models import lite_llm
        from litellm import _logging
        _logging._turn_on_debug()

        # loggerの初期化
        common.reset_logger("LiteLLM Proxy")
        common.reset_logger("LiteLLM Router")
        common.reset_logger("LiteLLM")
        # 各種設定値の取得
        agent_name = agent_conf.get('agent_name', None)
        agent_type = agent_conf.get('agent_type', None)
        a2asv_baseurl = agent_conf.get('a2asv_baseurl', "http://localhost:8071/a2a")
        a2asv_delegated_auth = agent_conf.get('a2asv_delegated_auth', False)
        a2asv_apikey = agent_conf.get('a2asv_apikey', None)
        agent_subagents = agent_conf.get('subagents', None)
        llmprov = llm_conf.get('llmprov', None)
        llmprojectid = llm_conf.get('llmprojectid', None)
        llmsvaccountfile = llm_conf.get('llmsvaccountfile', None)
        llmsvaccountfile_data = llm_conf.get('llmsvaccountfile_data', {})
        llmlocation = llm_conf.get('llmlocation', None)
        llmapikey = llm_conf.get('llmapikey', None)
        llmapiversion = llm_conf.get('llmapiversion', None)
        llmendpoint = llm_conf.get('llmendpoint', None)
        llmmodel = llm_conf.get('llmmodel', None)
        llmseed = llm_conf.get('llmseed', None)
        llmtemperature = llm_conf.get('llmtemperature', None)

        def create_subagent(data_dir:Path, agent_name:str) -> Any:
            agent_conf = self._load_agent_config(data_dir, agent_name)
            if agent_conf.get('llm', None) is not None:
                llm_conf = self._load_llm_config(data_dir, agent_conf['llm'])
            else:
                llm_conf = {}

            if agent_conf.get('mcpservers', None) is not None:
                mcpsv_confs = self._load_mcpsv_config(data_dir, agent_conf['mcpservers'])
            else:
                mcpsv_confs = []
            return self.create_agent(logger, data_dir, disable_remote_agent, agent_conf, llm_conf, mcpsv_confs)

        agent_subagents = agent_subagents if agent_subagents is not None else []
        subagents = []
        if 'subagents' in agent_conf and isinstance(agent_subagents, list):
            for subagent_name in agent_subagents:
                subagent_obj = create_subagent(data_dir, subagent_name)
                if subagent_obj is not None:
                    subagents.append(subagent_obj)

        if agent_type == 'remote' and not disable_remote_agent:
            from google.adk.agents.remote_a2a_agent import RemoteA2aAgent, AGENT_CARD_WELL_KNOWN_PATH
            from a2a.client.client_factory import ClientConfig, ClientFactory
            import httpx

            def _create_dynamic_header_provider():
                async def add_auth_headers(request):
                    scope = signin.get_request_scope()
                    if scope is not None and a2asv_delegated_auth:
                        apikey = scope["a2asv_apikey"] if scope["a2asv_apikey"] is not None else a2asv_apikey
                        request.headers['Authorization'] = f'Bearer {apikey}'
                    if a2asv_apikey is not None:
                        request.headers['Authorization'] = f'Bearer {a2asv_apikey}'
                return add_auth_headers
            custom_httpx_client = httpx.AsyncClient(
                timeout=httpx.Timeout(600.0),
                event_hooks={'request': [_create_dynamic_header_provider()]}
            )
            config = ClientConfig(httpx_client=custom_httpx_client)
            factory = ClientFactory(config=config)
            agent = RemoteA2aAgent(
                name=agent_name,
                agent_card=a2asv_baseurl + AGENT_CARD_WELL_KNOWN_PATH,
                a2a_client_factory=factory,
            )
            if logger.level == logging.DEBUG:
                logger.debug(f"create_agent complate.")
            return agent
        elif llmprov == 'openai':
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmapikey is None: raise ValueError("llmapikey is required.")
            from google.adk.planners import PlanReActPlanner
            agent = Agent(
                name=agent_name,
                model=lite_llm.LiteLlm(
                    model=llmmodel,
                    api_key=llmapikey,
                    endpoint=llmendpoint,
                ),
                description=description,
                instruction=instruction,
                planner=PlanReActPlanner(),
                tools=self.create_tool_mcpsv(logger, mcpsv_confs),
                sub_agents=subagents
            )
        elif llmprov == 'azureopenai':
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmendpoint is None: raise ValueError("llmendpoint is required.")
            if "/openai/deployments" in llmendpoint:
                llmendpoint = llmendpoint.split("/openai/deployments")[0]
            if llmapikey is None: raise ValueError("llmapikey is required.")
            if llmapiversion is None: raise ValueError("llmapiversion is required.")
            from google.adk.planners import PlanReActPlanner
            if not llmmodel.startswith("azure/"):
                llmmodel = f"azure/{llmmodel}"
            agent = Agent(
                name=agent_name,
                model=lite_llm.LiteLlm(
                    model=llmmodel,
                    api_key=llmapikey,
                    api_base=llmendpoint,
                    api_version=llmapiversion,
                ),
                description=description,
                instruction=instruction,
                planner=PlanReActPlanner(),
                tools=self.create_tool_mcpsv(logger, mcpsv_confs),
                sub_agents=subagents
            )
        elif llmprov == 'vertexai':
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmlocation is None: raise ValueError("llmlocation is required.")
            if llmsvaccountfile_data is None: raise ValueError("llmsvaccountfile_data is required.")
            from google.adk.planners import BuiltInPlanner
            from google.genai import types
            agent = Agent(
                name=agent_name,
                model=lite_llm.LiteLlm(
                    model=llmmodel,
                    #vertex_project=llmprojectid,
                    vertex_credentials=llmsvaccountfile_data,
                    vertex_location=llmlocation,
                    seed=llmseed,
                    temperature=llmtemperature,
                ),
                description=description,
                instruction=instruction,
                planner=BuiltInPlanner(thinking_config=types.ThinkingConfig(
                    include_thoughts=True,
                    thinking_budget=1024,
                )),
                tools=self.create_tool_mcpsv(logger, mcpsv_confs),
                sub_agents=subagents
            )
        elif llmprov == 'ollama':
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmendpoint is None: raise ValueError("llmendpoint is required.")
            from google.adk.planners import PlanReActPlanner
            agent = Agent(
                name=agent_name,
                model=lite_llm.LiteLlm(
                    model=f"ollama/{llmmodel}",
                    api_base=llmendpoint,
                    temperature=llmtemperature,
                    stream=True
                ),
                description=description,
                instruction=instruction,
                planner=PlanReActPlanner(),
                tools=self.create_tool_mcpsv(logger, mcpsv_confs),
                sub_agents=subagents
            )
        elif disable_remote_agent:
            return None
        else:
            raise ValueError("llmprov is required.")
        if logger.level == logging.DEBUG:
            logger.debug(f"create_agent complate.")
        return agent


    def create_tool_mcpsv(self, logger:logging.Logger, mcpsv_confs:List[Dict[str, Any]]) -> List[Any]:
        """
        MCPサーバーツールを作成します
        Args:
            logger (logging.Logger): ロガー
            mcpsv_confs (List[Dict[str, Any]]): MCPサーバー設定リスト
        Returns:
            List[MCPToolset]: MCPToolsetのリスト
        """
        from fastapi.openapi.models import HTTPBearer, SecuritySchemeType
        from google.adk.auth.auth_credential import AuthCredential, AuthCredentialTypes
        from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset
        from google.adk.tools.mcp_tool.mcp_session_manager import SseConnectionParams, StreamableHTTPConnectionParams
        from google.adk.agents.readonly_context import ReadonlyContext

        auth_scheme = HTTPBearer()
        tools = []
        for mcpsv_conf in mcpsv_confs:
            mcpserver_url = mcpsv_conf.get('mcpserver_url', None)
            mcpserver_apikey = mcpsv_conf.get('mcpserver_apikey', None)
            mcpserver_delegated_auth = mcpsv_conf.get('mcpserver_delegated_auth', False)
            mcpserver_transport = mcpsv_conf.get('mcpserver_transport', 'streamable-http')  # sse
            auth_cred = AuthCredential(auth_type=AuthCredentialTypes.HTTP)
            if mcpserver_transport == 'sse':
                conn_params = SseConnectionParams(
                    url=mcpserver_url,
                    timeout=120,
                    sse_read_timeout=600,
                )
            else:
                conn_params = StreamableHTTPConnectionParams(
                    url=mcpserver_url,
                    timeout=120,
                    sse_read_timeout=600,
                )
            if self.call_a2asv_start and mcpserver_apikey is not None:
                conn_params.headers = dict(Authorization=f"Bearer {mcpserver_apikey}")
            def _warp(mcpserver_apikey:str, mcpserver_delegated_auth:bool):
                # mcpserver_delegated_auth=Trueの場合、chatコマンド実行時に、
                # Signin情報からapikeyを取得してMCPサーバーに転送するためのヘッダープロバイダー
                def header_provider(readonly_context:ReadonlyContext) -> Dict[str, str]:
                    scope = signin.get_request_scope()
                    if scope is not None and mcpserver_delegated_auth and scope.get("mcpserver_apikey") is not None:
                        return dict(Authorization=f"Bearer {scope['mcpserver_apikey']}")
                    elif not mcpserver_delegated_auth and mcpserver_apikey is not None:
                        # コンテキストが存在しない場合またはdelegated_authが無効な場合、設定済みのAPIKeyを使用
                        return dict(Authorization=f"Bearer {mcpserver_apikey}")
                    return {}
                return header_provider
            toolset = MCPToolset(
                connection_params=conn_params,
                tool_filter=mcpsv_conf.get('mcpserver_mcp_tools', []),
                auth_scheme=auth_scheme,
                auth_credential=auth_cred,
                header_provider=_warp(mcpserver_apikey, mcpserver_delegated_auth),
            )
            tools.append(toolset)
        return tools

    def create_session_service(self, data_dir:Path, logger:logging.Logger, runner_conf:Dict[str, Any]) -> Any:
        """
        セッションサービスを作成します

        Args:
            runner_conf (Dict[str, Any]): Runnerの設定

        Returns:
            BaseSessionService: セッションサービス
        """
        if runner_conf.get('session_store_type') == 'sqlite':
            uri = (data_dir / '.agent' / 'session.db').as_uri()
            if platform.system() == 'Windows':
                runner_conf['agent_session_dburl'] = f"sqlite+aiosqlite:{uri.replace('file:///', '///')}"
            else:
                runner_conf['agent_session_dburl'] = f"sqlite+aiosqlite:{uri.replace('file:///', '////')}"
        elif runner_conf.get('session_store_type') == 'postgresql':
            runner_conf['agent_session_dburl'] = f"postgresql+psycopg://{runner_conf['session_store_pguser']}:{runner_conf['session_store_pgpass']}@{runner_conf['session_store_pghost']}:{runner_conf['session_store_pgport']}/{runner_conf['session_store_pgdbname']}"
        else:
            runner_conf['agent_session_dburl'] = None
        from google.adk.sessions import InMemorySessionService
        from google.adk.sessions.database_session_service import DatabaseSessionService
        #from typing_extensions import override
        if runner_conf['agent_session_dburl'] is not None:
            logger.info(f"Using DatabaseSessionService: {runner_conf['agent_session_dburl']}")
            dss = DatabaseSessionService(db_url=runner_conf['agent_session_dburl'])
            return dss
        else:
            logger.info(f"Using InMemorySessionService")
            return InMemorySessionService()
