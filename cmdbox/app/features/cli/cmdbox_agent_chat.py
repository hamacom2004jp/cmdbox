from cmdbox.app import common, client, options
from cmdbox.app.auth import signin
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.features.cli import cmdbox_tts_say
from cmdbox.app.features.cli.agent import agant_base
from cmdbox.app.options import Options
from contextlib import aclosing
from pathlib import Path
from typing import Callable, Dict, Any, Optional, Tuple, List, Union
import argparse
import logging
import json
import pydantic


class AgentOutput(pydantic.BaseModel):
    """Agentの出力スキーマ。

    google-adk の output_schema には dict も渡せますが、SetModelResponseTool は
    type[BaseModel] のときだけフィールド毎の型付きツール宣言を生成します。dict を渡すと
    google-adk<=2.3.0 では宣言生成時に例外、2.4.0 以降は検証なしの単一パラメータ
    (response: object) に退化し、モデルは埋めるべき構造を知らされません。

    全フィールドを Optional にしています。必須にすると、コマンドを実行しない通常の
    会話ターンでモデルが command / result_json を捏造せざるを得なくなり、捏造しなければ
    pydantic の検証エラーがそのまま最終回答として利用者に返ります。

    なお tool 経路では SetModelResponseTool がツール宣言を model_fields[].annotation
    だけから組み立て直すため、下記の description と既定値はモデルに渡りません
    (フィールド名6個が、すべて required として提示されます)。いずれも実害はありません:
    フィールド名自体が内容を表しており、どのフィールドに何を入れるかは agent_instruction
    側で指示するのが本来の役割で、応答の検証は従来どおり本モデルで行われます。
    native 経路ではスキーマがそのまま送られ、description も届きます。
    """
    success: Optional[bool] = pydantic.Field(
        default=None, description="コマンド実行が成功したかどうか")
    command: Optional[str] = pydantic.Field(
        default=None, description="実行したコマンド名")
    parameters_json: Optional[str] = pydantic.Field(
        default=None, description="コマンドに指定したパラメータ(JSON文字列)")
    result_json: Optional[str] = pydantic.Field(
        default=None, description="コマンド実行結果(JSON文字列)")
    error: Optional[str] = pydantic.Field(
        default=None, description="エラーが発生した場合のエラーメッセージ")
    message: Optional[str] = pydantic.Field(
        default=None, description="実行結果のメッセージ")

    @classmethod
    def _none_junk(cls, v: Any) -> Any:
        """モデルが「値なし」の意味で入れてくる文字列を None に正規化します。

        ローカルモデルはフィールドを省略せず "None" / "null" / "" を入れてくることがあり、
        そのまま検証すると SetModelResponseTool.run_async が検証エラーを最終回答として
        返してしまいます。
        """
        if isinstance(v, str) and v.strip() in ('', 'None', 'null'):
            return None
        return v

    _normalize_none_junk = pydantic.field_validator('*', mode='before')(_none_junk)


class AgentChat(agant_base.AgentBase, validator.Validator, limiter.LimitedFeature):

    def __init__(self, appcls, ver, language:str=None):
        super().__init__(appcls, ver, language=language)
        self.call_a2asv_start:bool = False

    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'chat'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=True,
            description_ja="Agentとチャットを行います。",
            description_en="Chat with the agent.",
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
                dict(opt="timeout", type=Options.T_INT, default=600, required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="runner_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="Runner設定の名前を指定します。",
                    description_en="Specify the name of the Runner configuration."),
                dict(opt="user_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="ユーザー名を指定します。",
                     description_en="Specify a user name."),
                dict(opt="session_id", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="Runnerに送信するセッションIDを指定します。",
                    description_en="Specify the session ID to send to the Runner."),
                dict(opt="a2asv_apikey", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="A2A ServerのAPI Keyを指定します。",
                    description_en="Specify the API Key of the A2A Server.",),
                dict(opt="mcpserver_apikey", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="リモートMCPサーバーのAPI Keyを指定します。",
                    description_en="Specify the API Key of the remote MCP server.",),
                dict(opt="message", type=Options.T_TEXT, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="Runnerに送信するメッセージを指定します。",
                    description_en="Specify the message to send to the Runner."),
                dict(opt="call_tts", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="TTS(Text-to-Speech)機能を実行するかどうかを指定します。",
                    description_en="Specify whether to execute the TTS (Text-to-Speech) feature."),
                dict(opt="reasoning_effort", type=Options.T_STR, default="auto", required=False, multi=False, hide=False,
                     choice=["auto", "off", "on", "low", "medium", "high", "xhigh"],
                    description_ja="エージェントで思考の連鎖の深さを指定します。使用するモデルによってはサポートされていない場合があります。",
                    description_en="Specify the depth of the thought chain in the agent. Depending on the model you are using, this feature may not be supported."),
            ]
        )

    @limiter.apprun_check_limit
    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        msg = dict(success=[], warn=[])
        for st, res in self.apprun_generate(logger, host=args.host, port=args.port, password=args.password, svname=args.svname,
                                            retry_interval=args.retry_interval, retry_count=args.retry_count, timeout=args.timeout,
                                            runner_name=args.runner_name, user_name=args.user_name, session_id=args.session_id,
                                            a2asv_apikey=args.a2asv_apikey, mcpserver_apikey=args.mcpserver_apikey, message=args.message,
                                            call_tts=args.call_tts, reasoning_effort=args.reasoning_effort):
            if st == self.RESP_SUCCESS:
                msg['success'].append(res)
            else:
                msg['warn'].append(res)

        if len(msg['success']) <= 0:
            del msg['success']
        if len(msg['warn']) > 0:
            return self.RESP_WARN, msg, cl
        return self.RESP_SUCCESS, msg, cl

    def apprun_generate(self, logger:logging.Logger, host:str, port:int, password:str, svname:str, retry_interval:int, retry_count:int, timeout:int,
                        runner_name:str, user_name:str, session_id:str, a2asv_apikey:str, mcpserver_apikey:str, message:str,
                        call_tts:bool, reasoning_effort:str):
        """
        Agentチャットを実行します
        
        Args:
            logger (logging.Logger): ロガー
            host (str): Redisホスト
            port (int): Redisポート
            password (str): Redisパスワード
            svname (str): サービス名
            retry_interval (int): 再接続インターバル秒数
            retry_count (int): 再接続回数
            timeout (int): タイムアウト秒数
            runner_name (str): Runner設定名
            user_name (str): ユーザー名
            session_id (str): セッションID
            a2asv_apikey (str): A2A Server API Key
            mcpserver_apikey (str): MCPサーバーAPI Key
            message (str): メッセージ
            call_tts (bool): TTS機能を呼び出すかどうか
            reasoning_effort (str): エージェントで思考の深さ
        Yields:
            Tuple[int, Any]: 処理結果ステータスと内容
        """
        payload = dict(runner_name=runner_name, user_name=user_name, session_id=session_id,
                       a2asv_apikey=a2asv_apikey, mcpserver_apikey=mcpserver_apikey, message=message,
                       call_tts=call_tts, reasoning_effort=reasoning_effort)
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=host, redis_port=port, redis_password=password, svname=svname)
        for res in cl.redis_cli.send_cmd_sse(self.get_svcmd(), [payload_b64],
                                             retry_count=retry_count, retry_interval=retry_interval, timeout=timeout, nowait=False):
            cls = self.output_schema()
            try:
                cls.model_validate(res)  # 結果のスキーマ検証
            except Exception as e:
                info = cls.get_model_info()
                res = dict(warn=dict(msg=f"Invalid result format: {e}.", output=res, output_schema=info))
                logger.warning(f"Invalid result format: {res}", exc_info=True)
            if 'success' in res:
                yield self.RESP_SUCCESS, res
            else:
                yield self.RESP_WARN, res

    def output_schema(self) -> type:
        class Ids(resdata.Base):
            agent_session_id: str = pydantic.Field(default=None, description="エージェントセッションID")
            event_id: str = pydantic.Field(default=None, description="イベントID")
            invocation_id: str = pydantic.Field(default=None, description="呼び出しID")
        class Flags(resdata.Base):
            final_response: bool = pydantic.Field(default=False, description="最終レスポンスフラグ")
            function_call: bool = pydantic.Field(default=False, description="関数呼び出しフラグ")
            function_response: bool = pydantic.Field(default=False, description="関数レスポンスフラグ")
            turn_complete: bool = pydantic.Field(default=False, description="ターン完了フラグ")
            interrupted: bool = pydantic.Field(default=False, description="割り込みフラグ")
        class FunctionCall(resdata.Base):
            id: Union[str, None] = pydantic.Field(default=None, description="関数呼び出しID")
            name: Union[str, None] = pydantic.Field(default=None, description="関数名")
            args: Union[Dict[str, Any], None] = pydantic.Field(default=None, description="関数引数")
        class FunctionResponse(resdata.Base):
            id: Union[str, None] = pydantic.Field(default=None, description="関数応答ID")
            name: Union[str, None] = pydantic.Field(default=None, description="関数名")
            response: Union[Dict[str, Any], str, None] = pydantic.Field(default=None, description="関数応答内容")
        class Artifact(resdata.Base):
            filename: Union[str, None] = pydantic.Field(default=None, description="アーティファクト名")
            version: Union[int, None] = pydantic.Field(default=None, description="バージョン")
            text: Union[str, None] = pydantic.Field(default=None, description="テキスト本文")
            mime_type: Union[str, None] = pydantic.Field(default=None, description="MIMEタイプ")
            inline_data_size: Union[int, None] = pydantic.Field(default=None, description="inline_dataサイズ")
            file_uri: Union[str, None] = pydantic.Field(default=None, description="ファイルURI")
        class Message(resdata.Base):
            role: Union[str, None] = pydantic.Field(default=None, description="メッセージの役割")
            content: Union[str, None] = pydantic.Field(default=None, description="メッセージの内容")
        class Data(resdata.Data):
            ids: Union[Ids, None] = pydantic.Field(default=None, description="セッション・イベントID情報")
            flags: Union[Flags, None] = pydantic.Field(default=None, description="フラグ情報")
            message: Union[Message, AgentOutput, str, None] = pydantic.Field(default=None, description="メッセージ")
            function_calls: Union[List[FunctionCall], None] = pydantic.Field(default=None, description="関数呼び出し一覧")
            function_responses: Union[List[FunctionResponse], None] = pydantic.Field(default=None, description="関数応答一覧")
            artifact_delta: Union[Dict[str, int], None] = pydantic.Field(default=None, description="更新されたアーティファクト一覧")
            artifacts: Union[List[Artifact], None] = pydantic.Field(default=None, description="アーティファクト内容")
            wav_b64: Union[str, None] = pydantic.Field(default=None, description="Base64エンコードされたWAVデータ")
            ressize: Union[int, None] = pydantic.Field(default=None, description="Agentが返したレスポンスのサイズ")
        class SubResult(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        class Result(resdata.Result):
            success: Union[Data, List[SubResult], None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return False

    def create_agent_output_schema(self) -> type:
        """
        Agentの出力スキーマを作成します。
        JSON形式での出力構造を定義します。

        Returns:
            type: pydantic BaseModel のサブクラス (AgentOutput)
        """
        return AgentOutput

    def supports_native_output_schema_with_tools(self, llm_conf:Dict[str, Any]) -> bool:
        """
        output_schema を tools と同一リクエストで送れるプロバイダーかどうかを返します。

        google-adk は output_schema の適用方法を2通り持ちます。native 経路は
        response_format(json_schema) としてリクエストに載せる方法、tool 経路は
        スキーマをパラメータに持つ set_model_response ツールとして公開する方法です。
        google.adk.utils.output_schema_utils.can_use_output_schema_with_tools() は
        LiteLlm インスタンスに対して常に True を返すため、常に native が選ばれます。

        しかし native 経路が使えるのは OpenAI / Azure OpenAI のようなマネージド API に
        限られます。ローカル推論サーバー(ollama / vLLM 等)は response_format を
        guided decoding で実装しており、その文法はツール呼び出し形式の生成を禁止するため、
        両方を同時に送るとツール呼び出しが一切できなくなります(モデルはスキーマだけを
        埋めて回答し、実行していないツールの結果を捏造します)。

        False を返したプロバイダーには create_agent_before_model_callback() が
        tool 経路へ切り替えるコールバックを設定します。

        Args:
            llm_conf (Dict[str, Any]): LLM設定

        Returns:
            bool: native 経路が使えるなら True
        """
        return llm_conf.get('llmprov', None) != 'ollama'

    # google-adk の _OutputSchemaRequestProcessor が set_model_response ツールを追加する際に
    # 付与する指示と同じ内容。native 経路から手動で切り替える場合も同じ指示を出す。
    SET_MODEL_RESPONSE_INSTRUCTION = (
        'IMPORTANT: You have access to other tools, but you must provide '
        'your final response using the set_model_response tool with the '
        'required structured format. After using any other tools needed '
        'to complete the task, always call set_model_response with your '
        'final answer in the specified schema format.'
    )

    def create_agent_before_model_callback(self, llm_conf:Dict[str, Any]) -> Optional[Callable]:
        """
        Agentに設定する before_model_callback を作成します。

        supports_native_output_schema_with_tools() が False のプロバイダーに対して、
        google-adk が選んだ native 経路を取り消し、set_model_response ツール経路へ
        切り替えるコールバックを返します。google-adk 側の後処理は set_model_response
        という名前の function response だけを見ているため、ツールを手動で足しても
        最終回答の組み立ては通常どおり動作します。

        Args:
            llm_conf (Dict[str, Any]): LLM設定

        Returns:
            Optional[Callable]: before_model_callback。切り替え不要なら None
        """
        if self.supports_native_output_schema_with_tools(llm_conf):
            return None
        from google.adk.tools.set_model_response_tool import SetModelResponseTool
        output_schema = self.create_agent_output_schema()

        def swap_native_output_schema_to_tool(callback_context:Any, llm_request:Any) -> None:
            config = getattr(llm_request, 'config', None)
            if config is None or config.response_schema is None:
                # native 経路が選ばれていない = google-adk 側が既に tool 経路を組んでいる
                # (または output_schema なし)。取り消すものが無いので何もしない。
                return None
            config.response_schema = None
            config.response_mime_type = None
            llm_request.append_tools([SetModelResponseTool(output_schema)])
            llm_request.append_instructions([self.SET_MODEL_RESPONSE_INSTRUCTION])
            return None

        return swap_native_output_schema_to_tool

    def create_agent(self, logger:logging.Logger, data_dir:Path, disable_remote_agent:bool,
                     agent_conf:Dict[str, Any], llm_conf:Dict[str, Any], mcpsv_confs:List[Dict[str, Any]],
                     payload:Dict[str, Any]) -> Any:
        """
        エージェントを作成します

        Args:
            logger (logging.Logger): ロガー
            data_dir (Path): データディレクトリパス
            disable_remote_agent (bool): リモートエージェントを無効化するかどうか
            agent_conf (Dict[str, Any]): エージェント設定
            llm_conf (Dict[str, Any]): LLM設定
            mcpsv_confs (List[Dict[str, Any]]): MCPサーバー設定リスト
            payload (Dict[str, Any]): クライアントからのリクエスト情報

        Returns:
            Agent: エージェント
        """
        if logger.level == logging.DEBUG:
            logger.debug(f"create_agent processing..")
        description = agent_conf.get("agent_description", self.agent_description)
        instruction = agent_conf.get("agent_instruction", '')
        agent_system_instruction = agent_conf.get("agent_system_instruction", self.agent_system_instruction)
        prompt_param = agent_conf.get("prompt_param", None)

        # prompt_param によるプレースホルダー置換
        instruction = self.apply_prompt_param(instruction, prompt_param)
        agent_system_instruction = self.apply_prompt_param(agent_system_instruction, prompt_param)

        # agent_system_instruction を instruction の先頭に結合
        if agent_system_instruction:
            instruction = agent_system_instruction + ("\n" + instruction if instruction else "")

        if logger.level == logging.DEBUG:
            logger.debug(f"google-adk loading..")
        from google.adk.agents import Agent as AdkAgent
        # App name mismatch警告を回避するためのラッパークラス
        class Agent(AdkAgent):
            pass

        if logger.level == logging.DEBUG:
            logger.debug(f"litellm loading..")
        from google.adk.models import lite_llm
        import litellm
        litellm.drop_params = True
        #from litellm import _logging
        #_logging._turn_on_debug()

        # loggerの初期化
        common.reset_logger("LiteLLM Proxy")
        common.reset_logger("LiteLLM Router")
        common.reset_logger("LiteLLM")
        common.reset_logger("litellm")
        common.reset_logger("httpcore")
        common.reset_logger("httpx")
        common.reset_logger("openai")
        #litellm.suppress_debug_info = True
        # 各種設定値の取得
        agent_name = agent_conf.get('agent_name', None)
        agent_type = agent_conf.get('agent_type', None)
        a2asv_baseurl = agent_conf.get('a2asv_baseurl', "http://localhost:8071/a2a")
        a2asv_delegated_auth = agent_conf.get('a2asv_delegated_auth', False)
        a2asv_apikey = agent_conf.get('a2asv_apikey', None)
        agent_subagents = agent_conf.get('subagents', None)

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
            return self.create_agent(logger, data_dir, disable_remote_agent, agent_conf, llm_conf, mcpsv_confs, payload)

        agent_subagents = agent_subagents if agent_subagents is not None else []
        subagents = []
        if 'subagents' in agent_conf and isinstance(agent_subagents, list):
            for subagent_name in agent_subagents:
                subagent_obj = create_subagent(data_dir, subagent_name)
                if subagent_obj is not None:
                    subagents.append(subagent_obj)

        llmprov = llm_conf.get('llmprov', None)
        reasoning_effort = self.get_reasoning_effort(agent_conf, payload)
        planner = self.create_agent_planner(agent_conf, llm_conf, reasoning_effort)
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
                follow_redirects=True,
                timeout=httpx.Timeout(600.0),
                event_hooks={'request': [_create_dynamic_header_provider()]},
            )
            if a2asv_baseurl is None:
                raise ValueError("a2asv_baseurl is required for remote agent.")
            if a2asv_baseurl.endswith('/'):
                a2asv_baseurl = a2asv_baseurl[:-1]
            config = ClientConfig(httpx_client=custom_httpx_client)
            factory = ClientFactory(config=config)
            agent = RemoteA2aAgent(
                name=agent_name,
                agent_card=f"{a2asv_baseurl}{AGENT_CARD_WELL_KNOWN_PATH}",
                a2a_client_factory=factory,
            )
            if logger.level == logging.DEBUG:
                logger.debug(f"create_agent complate.")
            return agent
        elif llmprov == 'openai':
            llmmodel = llm_conf.get('llmmodel', None)
            llmapikey = llm_conf.get('llmapikey', None)
            llmendpoint = llm_conf.get('llmendpoint', None)
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmapikey is None: raise ValueError("llmapikey is required.")
            tools = self.create_agent_tools(logger, data_dir, agent_conf, mcpsv_confs, payload)
            agent = Agent(
                name=agent_name,
                model=lite_llm.LiteLlm(
                    model=llmmodel,
                    api_key=llmapikey,
                    endpoint=llmendpoint,
                ),
                description=description,
                instruction=instruction,
                planner=planner,
                tools=tools,
                sub_agents=subagents,
                output_schema=self.create_agent_output_schema(),
                before_model_callback=self.create_agent_before_model_callback(llm_conf),
            )
        elif llmprov == 'azureopenai':
            llmmodel = llm_conf.get('llmmodel', None)
            llmapikey = llm_conf.get('llmapikey', None)
            llmendpoint = llm_conf.get('llmendpoint', None)
            llmapiversion = llm_conf.get('llmapiversion', None)
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmendpoint is None: raise ValueError("llmendpoint is required.")
            if "/openai/deployments" in llmendpoint:
                llmendpoint = llmendpoint.split("/openai/deployments")[0]
            if llmapikey is None: raise ValueError("llmapikey is required.")
            if llmapiversion is None: raise ValueError("llmapiversion is required.")
            if not llmmodel.startswith("azure/"):
                llmmodel = f"azure/{llmmodel}"
            tools = self.create_agent_tools(logger, data_dir, agent_conf, mcpsv_confs, payload)
            agent = Agent(
                name=agent_name,
                model=lite_llm.LiteLlm(
                    model=llmmodel,
                    api_key=llmapikey,
                    api_base=llmendpoint,
                    api_version=llmapiversion,
                    base_url=llmendpoint,
                ),
                description=description,
                instruction=instruction,
                planner=planner,
                tools=tools,
                sub_agents=subagents,
                output_schema=self.create_agent_output_schema(),
                before_model_callback=self.create_agent_before_model_callback(llm_conf),
            )
        elif llmprov == 'vertexai':
            llmprojectid = llm_conf.get('llmprojectid', None)
            llmsvaccountfile = llm_conf.get('llmsvaccountfile', None)
            llmmodel = llm_conf.get('llmmodel', None)
            llmlocation = llm_conf.get('llmlocation', None)
            llmsvaccountfile_data = llm_conf.get('llmsvaccountfile_data', {})
            llmtemperature = llm_conf.get('llmtemperature', None)
            llmseed = llm_conf.get('llmseed', None)
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmlocation is None: raise ValueError("llmlocation is required.")
            if llmsvaccountfile_data is None: raise ValueError("llmsvaccountfile_data is required.")
            tools = self.create_agent_tools(logger, data_dir, agent_conf, mcpsv_confs, payload)
            agent = Agent(
                name=agent_name,
                model=lite_llm.LiteLlm(
                    model=llmmodel,
                    #vertex_project=llmprojectid,
                    vertex_credentials=llmsvaccountfile_data,
                    vertex_location=llmlocation,
                    seed=llmseed,
                    temperature=llmtemperature
                ),
                description=description,
                instruction=instruction,
                planner=planner,
                tools=tools,
                sub_agents=subagents,
                output_schema=self.create_agent_output_schema(),
                before_model_callback=self.create_agent_before_model_callback(llm_conf),
            )
        elif llmprov == 'ollama':
            llmmodel = llm_conf.get('llmmodel', None)
            llmendpoint = llm_conf.get('llmendpoint', None)
            llmtemperature = llm_conf.get('llmtemperature', None)
            if llmmodel is None: raise ValueError("llmmodel is required.")
            if llmendpoint is None: raise ValueError("llmendpoint is required.")
            tools = self.create_agent_tools(logger, data_dir, agent_conf, mcpsv_confs, payload)
            agent = Agent(
                name=agent_name,
                model=lite_llm.LiteLlm(
                    model=f"ollama/{llmmodel}",
                    api_base=llmendpoint,
                    temperature=llmtemperature,
                    stream=True,
                ),
                description=description,
                instruction=instruction,
                planner=planner,
                tools=tools,
                sub_agents=subagents,
                output_schema=self.create_agent_output_schema(),
                before_model_callback=self.create_agent_before_model_callback(llm_conf),
            )
        elif disable_remote_agent:
            return None
        else:
            raise ValueError("llmprov is required.")
        if logger.level == logging.DEBUG:
            logger.debug(f"create_agent complate.")
        return agent

    def get_reasoning_effort(self, agent_conf:Dict[str, Any], payload:Dict[str, Any]) -> str:
        """
        エージェントの思考の深さを取得します
        Args:
            agent_conf (Dict[str, Any]): エージェント設定
            payload (Dict[str, Any]): クライアントからのリクエスト情報
        Returns:
            str: reasoning_effortの設定
        """
        pay_reasoning_effort = payload.get('reasoning_effort', 'off')
        if not pay_reasoning_effort or pay_reasoning_effort=='off':
            return 'off'
        conf_reasoning_effort = agent_conf.get('reasoning_effort', 'off')
        if pay_reasoning_effort=='auto':
            if not conf_reasoning_effort or conf_reasoning_effort=='off':
                return 'off'
            pay_reasoning_effort = conf_reasoning_effort
        return pay_reasoning_effort

    def create_agent_planner(self, agent_conf:Dict[str, Any], llm_conf:Dict[str, Any], reasoning_effort:str) -> Any:
        """
        エージェントのプランナーを作成します
        Args:
            agent_conf (Dict[str, Any]): エージェント設定
            llm_conf (Dict[str, Any]): LLM設定
            reasoning_effort (str): エージェントの思考の深さ
        Returns:
            Planner: プランナー
        """
        if reasoning_effort == 'off':
            return None

        from google.adk.planners import PlanReActPlanner, BuiltInPlanner
        from google.genai import types
        llmprov = llm_conf.get('llmprov', None)
        if llmprov == 'openai':
            return PlanReActPlanner()
        elif llmprov == 'azureopenai':
            return PlanReActPlanner()
        elif llmprov == 'vertexai':
            return BuiltInPlanner(thinking_config=types.ThinkingConfig(
                include_thoughts=True,
                thinking_budget=1024,
            ))
        elif llmprov == 'ollama':
            return PlanReActPlanner()
        else:
            raise ValueError(f"Unknown llmprov: {llmprov}")

    def create_tool_mcpsv(self, logger:logging.Logger, mcpsv_confs:List[Dict[str, Any]], payload:Dict[str, Any]) -> List[Any]:
        """
        MCPサーバーツールを作成します
        Args:
            logger (logging.Logger): ロガー
            mcpsv_confs (List[Dict[str, Any]]): MCPサーバー設定リスト
            payload (Dict[str, Any]): クライアントからのリクエスト情報
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
                    # delegated_authが有効な場合、Signin情報からapikeyを取得して使用
                    if scope is not None and mcpserver_delegated_auth and scope.get("mcpserver_apikey", None) is not None:
                        return dict(Authorization=f"Bearer {scope['mcpserver_apikey']}")
                    # delegated_authが無効な場合、設定済みのAPIKeyを使用
                    elif not mcpserver_delegated_auth and mcpserver_apikey is not None:
                        return dict(Authorization=f"Bearer {mcpserver_apikey}")
                    # fastmcp経由で来たときはreqヘッダーからAuthorizationを取得して転送
                    elif mcpserver_delegated_auth and 'req' in scope and 'headers' in scope['req']:
                        req_headers = scope['req'].headers
                        if 'authorization' in req_headers:
                            return dict(Authorization=req_headers['authorization'])
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

    def create_tool_skills(self, logger:logging.Logger, data_dir:Path, agent_conf:Dict[str, Any]) -> List[Any]:
        """
        SkillToolset を作成します

        Args:
            logger (logging.Logger): ロガー
            data_dir (Path): データディレクトリパス
            agent_conf (Dict[str, Any]): エージェント設定

        Returns:
            List[Any]: SkillToolset のリスト
        """
        skill_names = agent_conf.get('skill_name', None)
        if skill_names is None:
            return []
        if not isinstance(skill_names, list):
            skill_names = [skill_names]
        skill_names = list(dict.fromkeys([s for s in skill_names if isinstance(s, str) and s.strip() != '']))
        if len(skill_names) <= 0:
            return []

        from google.adk.skills import load_skill_from_dir
        from google.adk.tools.skill_toolset import SkillToolset

        skills = []
        for skill_name in skill_names:
            skill_dir = data_dir / '.skills' / skill_name
            if not skill_dir.exists() or not skill_dir.is_dir() or not (skill_dir / 'SKILL.md').exists():
                raise FileNotFoundError(f"Specified skill '{skill_name}' not found at '{skill_dir}'.")
            skill = load_skill_from_dir(skill_dir)
            skills.append(skill)
            if logger.level == logging.DEBUG:
                logger.debug(f"Loaded skill '{skill_name}' from '{skill_dir}'.")

        if len(skills) <= 0:
            return []

        return [SkillToolset(skills=skills)]

    def create_agent_tools(self, logger:logging.Logger, data_dir:Path, agent_conf:Dict[str, Any],
                           mcpsv_confs:List[Dict[str, Any]], payload:Dict[str, Any]) -> List[Any]:
        """
        Agent用ツール群(MCP + Skill)を作成します

        Args:
            logger (logging.Logger): ロガー
            data_dir (Path): データディレクトリパス
            agent_conf (Dict[str, Any]): エージェント設定
            mcpsv_confs (List[Dict[str, Any]]): MCPサーバー設定リスト
            payload (Dict[str, Any]): クライアントからのリクエスト情報

        Returns:
            List[Any]: Agentへ渡すツール一覧
        """
        tools = self.create_tool_mcpsv(logger, mcpsv_confs, payload)
        tools.extend(self.create_tool_skills(logger, data_dir, agent_conf))
        return tools

    @limiter.async_svrun_check_limit
    async def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
                    sessions:Dict[str, Dict[str, Any]]):
        return await self._svrun_chat(data_dir, logger, redis_cli, msg, sessions)

    async def _svrun_chat(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient,
                          msg:List[str], sessions:Dict[str, Dict[str, Any]]):
        reskey = msg[1]
        runner = None
        tts_engine_obj = None
        enable_tts = True
        try:
            payload = json.loads(convert.b64str2str(msg[2]))
            runner_name = payload.get('runner_name')
            user_name = payload.get('user_name')
            session_id = payload.get('session_id')
            message = payload.get('message')

            import litellm
            litellm.drop_params = True
            # 設定をロードする
            runner_conf, agent_conf, llm_conf, mcpsv_confs, ds_conf = self.load_conf(runner_name, data_dir, logger)
            artifact_root_dir = data_dir / '.users' / user_name / 'artifacts' / runner_name
            # Agentを作成する
            agent = self.create_agent(logger, data_dir, False, agent_conf, llm_conf, mcpsv_confs, payload)
            # Runnerを作成する
            runner = self._create_runner(logger, runner_conf, agent, ds_conf, artifact_root_dir)
            # Agentに送信するメッセージを作成
            from google.genai import types
            content = types.Content(role='user', parts=[types.Part(text=message)])
            # TTSエンジンのセットアップ
            enable_tts, tts_engine_obj = self._setup_tts_engine(logger, data_dir, payload, runner_conf)
            # セッションを作成する
            agent_session = await self.create_agent_session(runner.session_service, runner.app_name,
                                                            user_name, session_id=session_id)
            # チャットを実行する
            await self._svrun_chat_exec(redis_cli, payload, runner, agent_session, content,
                                        enable_tts, tts_engine_obj, reskey)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}", end=True)
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN
        finally:
            if enable_tts:
                # TTSモデルの停止
                cmdbox_tts_say.TtsSay.tts_stop(tts_engine_obj)
            if runner:
                if hasattr(runner.session_service, 'db_engine'):
                    await runner.session_service.db_engine.dispose()
                await runner.close()

    def _create_runner(self, logger:logging.Logger, runner_conf:Dict[str, Any], agent:Any, ds_conf:Dict[str, Any], artifact_root_dir:Path) -> Any:
        """
        Runnerを作成します

        Args:
            logger (logging.Logger): ロガー
            runner_conf (Dict[str, Any]): Runner設定
            agent (Any): エージェント
            ds_conf (Dict[str, Any]): データソース設定
            artifact_root_dir (Path): アーティファクトのルートディレクトリ

        Returns:
            Runner: Runnerオブジェクト
        """
        from google.adk.runners import Runner
        artifact_service = self._create_artifact_service(logger, artifact_root_dir)
        runner = Runner(
            app_name=runner_conf.get('runner_name', self.ver.__appid__),
            agent=agent,
            session_service=self.create_session_service(logger, ds_conf),
            artifact_service=artifact_service,
        )
        return runner

    def _create_artifact_service(self, logger:logging.Logger, artifact_root_dir:Path) -> Any:
        """
        Artifactサービスを作成します

        Args:
            logger (logging.Logger): ロガー
            artifact_root_dir (Path): アーティファクトのルートディレクトリ

        Returns:
            BaseArtifactService: Artifactサービス
        """
        if artifact_root_dir is not None:
            from google.adk.artifacts.file_artifact_service import FileArtifactService
            try:
                artifact_root_dir.mkdir(parents=True, exist_ok=True)
                return FileArtifactService(artifact_root_dir)
            except Exception as e:
                logger.warning(f"Failed to initialize FileArtifactService: {e}. Falling back to InMemoryArtifactService.", exc_info=True)
        from google.adk.artifacts.in_memory_artifact_service import InMemoryArtifactService
        return InMemoryArtifactService()

    def _setup_tts_engine(self, logger:logging.Logger, data_dir:Path,
                          payload:Dict[str, Any], runner_conf:Dict[str, Any]) -> Tuple[bool, Any]:
        """
        TTSエンジンをセットアップします

        Args:
            logger (logging.Logger): ロガー
            data_dir (Path): データディレクトリパス
            payload (Dict[str, Any]): リクエストペイロード
            runner_conf (Dict[str, Any]): Runner設定

        Returns:
            Tuple[bool, Any]: TTSが有効かどうかとTTSエンジンオブジェクト
        """
        tts_engine = runner_conf.get('tts_engine', None)
        voicevox_model = runner_conf.get('voicevox_model', None)
        call_tts = payload.get('call_tts', False)
        enable_tts = call_tts and tts_engine and voicevox_model
        tts_engine_obj = None
        if enable_tts:
            try:
                # TTSモデルの準備
                tts_engine_obj = cmdbox_tts_say.TtsSay.tts_start(data_dir, tts_engine, voicevox_model)
            except Exception as e:
                logger.warning(f"Failed to prepare TTS model: {e}", exc_info=True)
                enable_tts = False
                return enable_tts, None
        return enable_tts, tts_engine_obj

    async def _svrun_chat_exec(self, redis_cli:redis_client.RedisClient, payload:Dict[str, Any],
                               runner:Any, agent_session:Any, content:Any,
                               enable_tts:bool, tts_engine_obj:Any, reskey:str) -> None:
        """
        チャットの実行を行います

        Args:
            redis_cli (redis_client.RedisClient): Redisクライアント
            payload (Dict[str, Any]): リクエストペイロード
            runner (Any): Runnerオブジェクト
            agent_session (Any): エージェントセッション
            content (Any): チャットメッセージ内容
            enable_tts (bool): TTSが有効かどうか
            tts_engine_obj (Any): TTSエンジンオブジェクト
            reskey (str): Redisの結果キー
        """
        runner_name = payload.get('runner_name')
        user_name = payload.get('user_name')
        a2asv_apikey = payload.get('a2asv_apikey')
        mcpserver_apikey = payload.get('mcpserver_apikey')

        from google.adk.agents.run_config import RunConfig, StreamingMode
        from google.adk.events import Event
        signin.set_request_scope(dict(mcpserver_apikey=mcpserver_apikey, a2asv_apikey=a2asv_apikey))
        run_config = RunConfig(streaming_mode=StreamingMode.NONE)
        resval = []
        async with aclosing(runner.run_async(user_id=user_name,
                                                session_id=agent_session.id,
                                                new_message=content,
                                                state_delta=None,
                                                run_config=run_config)) as run_iter:
            try:
                async for event in run_iter:
                    ev:Event = event
                    outputs = dict(success=dict(),)
                    success = outputs['success']
                    ids = outputs['success']['ids'] = dict()
                    ids['agent_session_id'] = agent_session.id
                    ids['event_id'] = event.id
                    ids['invocation_id'] = event.invocation_id
                    flags = outputs['success']['flags'] = dict()
                    flags['turn_complete'] = bool(event.turn_complete)
                    flags['interrupted'] = bool(event.interrupted)
                    msg, is_func_call, is_func_response, is_final_response = self.__class__.gen_msg(event)
                    flags['final_response'] = is_final_response
                    flags['function_call'] = is_func_call
                    flags['function_response'] = is_func_response

                    calls = event.get_function_calls() or []
                    if calls:
                        success['function_calls'] = [self._serialize_function_call(c) for c in calls]

                    responses = event.get_function_responses() or []
                    if responses:
                        success['function_responses'] = [self._serialize_function_response(r) for r in responses]

                    artifacts = []
                    if event.actions and event.actions.artifact_delta:
                        success['artifact_delta'] = dict(event.actions.artifact_delta)
                        if hasattr(runner, 'artifact_service') and runner.artifact_service is not None:
                            for filename, version in event.actions.artifact_delta.items():
                                try:
                                    artifact_part = await runner.artifact_service.load_artifact(
                                        app_name=runner_name,
                                        user_id=user_name,
                                        session_id=agent_session.id,
                                        filename=filename,
                                        version=version,
                                    )
                                    artifacts.append(self._serialize_artifact(filename, version, artifact_part))
                                except Exception as e:
                                    artifacts.append(dict(filename=filename, version=version, text=f"Failed to load artifact: {e}"))
                    if artifacts:
                        success['artifacts'] = artifacts

                    if msg:
                        success['message'] = msg
                        options.Options.getInstance().audit_exec(body=dict(agent_session=agent_session.id, result=msg),
                                                                    audit_type=options.Options.AT_USER, user=user_name)
                        if enable_tts and tts_engine_obj and not is_func_call and not is_func_response:
                            try:
                                try:
                                    msg_json = json.loads(msg) if isinstance(msg, str) else msg
                                    msg = msg_json['message'] if isinstance(msg_json, dict) and 'message' in msg_json else msg
                                except Exception:
                                    pass
                                wav_b64 = cmdbox_tts_say.TtsSay.tts_say(tts_engine_obj, msg) \
                                    if msg is not None and msg.strip() != '' else None
                                success['wav_b64'] = wav_b64
                            except Exception as e:
                                success['wav_b64'] = None

                    has_output = any([
                        success.get('message') is not None and str(success.get('message')).strip() != '',
                        bool(success.get('function_calls')),
                        bool(success.get('function_responses')),
                        bool(success.get('artifact_delta')),
                        bool(success.get('artifacts')),
                    ])

                    resval.append(outputs)
                    if has_output:
                        redis_cli.rpush(reskey, outputs)
                    if flags['final_response']:
                        break

            except Exception as e:
                outputs = dict(success=dict(flags=dict(final_response=True, function_call=False, function_response=False),
                                            message=str(e),
                                            ids=dict(agent_session_id=agent_session.id)),)
                redis_cli.rpush(reskey, outputs)
                raise e
        msg = dict(success=dict(message=f"Chat '{runner_name}' successfully.",
                                ressize=len(convert.str2b64str(common.to_str(resval)))),
                                end=True)
        redis_cli.rpush(reskey, msg)
        await run_iter.aclose()

    @staticmethod
    def _to_primitive(value: Any) -> Any:
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool, list, dict)):
            return value
        if hasattr(value, "model_dump"):
            return value.model_dump(mode='json')
        if hasattr(value, "dict"):
            return value.dict()
        return common.to_str(value)

    @classmethod
    def _serialize_function_call(cls, call: Any) -> Dict[str, Any]:
        return dict(
            id=getattr(call, 'id', None),
            name=getattr(call, 'name', None),
            args=cls._to_primitive(getattr(call, 'args', None)),
        )

    @classmethod
    def _serialize_function_response(cls, response: Any) -> Dict[str, Any]:
        return dict(
            id=getattr(response, 'id', None),
            name=getattr(response, 'name', None),
            response=cls._to_primitive(getattr(response, 'response', None)),
        )

    @classmethod
    def _serialize_artifact(cls, filename: str, version: int, artifact_part: Any) -> Dict[str, Any]:
        row = dict(filename=filename, version=version)
        if artifact_part is None:
            return row
        text = getattr(artifact_part, 'text', None)
        if text:
            row['text'] = text
        inline_data = getattr(artifact_part, 'inline_data', None)
        if inline_data is not None:
            row['mime_type'] = getattr(inline_data, 'mime_type', None)
            data = getattr(inline_data, 'data', None)
            row['inline_data_size'] = len(data) if data is not None else 0
        file_data = getattr(artifact_part, 'file_data', None)
        if file_data is not None:
            row['mime_type'] = row.get('mime_type', getattr(file_data, 'mime_type', None))
            row['file_uri'] = getattr(file_data, 'file_uri', None)
        return row

    def svrun_output_bytes(self, data_dir, logger, opt, msg, msg_size):
        msg_size = msg.get('success', {}).get('ressize', msg_size)
        return msg_size

    def svrun_credit(self, data_dir, logger, opt, msg):
        return 1
