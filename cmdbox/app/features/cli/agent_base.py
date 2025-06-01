from cmdbox.app import common, feature
from cmdbox.app.auth import signin
from cmdbox.app.features.cli import cmdbox_cmd_list
from cmdbox.app.options import Options
from pathlib import Path
from typing import Any, Callable, Dict, Tuple, List
import argparse
import asyncio
import locale
import logging
import json
import re
import time


class AgentBase(feature.ResultEdgeFeature):

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            discription_ja="-",
            discription_en="-",
            choice=[
                dict(opt="agent", type=Options.T_STR, default="no", required=False, multi=False, hide=False, choice=["no", "use"],
                     discription_ja="エージェントを使用するかどうかを指定します。",
                     discription_en="Specifies whether the agent is used.",
                     choice_show=dict(use=["agent_name", "agent_description", "agent_instruction", "agent_session_store", "llmprov",
                                           "mcp_listen_port", "mcp_ssl_listen_port"],)),
                dict(opt="agent_name", type=Options.T_STR, default=self.ver.__appid__, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エージェント名を指定します。",
                     discription_en="Specifies the agent name."),
                dict(opt="agent_description", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エージェントの説明を指定します。",
                     discription_en="Specify agent description."),
                dict(opt="agent_instruction", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エージェントのシステム指示を指定します。",
                     discription_en="Specifies the agent's system instructions."),
                dict(opt="agent_session_store", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=['memory', 'sqlite', 'postgresql'],
                     discription_ja="エージェントのセッションを保存する方法を指定します。",
                     discription_en="Specify how the agent's session is to be saved.",
                     choice_show=dict(postgresql=["agent_pg_host", "agent_pg_port", "agent_pg_user", "agent_pg_password", "agent_pg_dbname"]),),
                dict(opt="mcp_listen_port", type=Options.T_INT, default="9081", required=False, multi=False, hide=False, choice=None,
                     discription_ja="省略した時は `9081` を使用します。",
                     discription_en="If omitted, `9081` is used."),
                dict(opt="mcp_ssl_listen_port", type=Options.T_INT, default="9443", required=False, multi=False, hide=False, choice=None,
                     discription_ja="省略した時は `9443` を使用します。",
                     discription_en="If omitted, `9443` is used."),
                dict(opt="agent_pg_host", type=Options.T_STR, default='localhost', required=False, multi=False, hide=False, choice=None, web="mask",
                     discription_ja="postgresqlホストを指定する。",
                     discription_en="Specify the postgresql host."),
                dict(opt="agent_pg_port", type=Options.T_INT, default=5432, required=False, multi=False, hide=False, choice=None, web="mask",
                     discription_ja="postgresqlのポートを指定する。",
                     discription_en="Specify the postgresql port."),
                dict(opt="agent_pg_user", type=Options.T_STR, default='postgres', required=False, multi=False, hide=False, choice=None, web="mask",
                     discription_ja="postgresqlのユーザー名を指定する。",
                     discription_en="Specify the postgresql user name."),
                dict(opt="agent_pg_password", type=Options.T_STR, default='postgres', required=False, multi=False, hide=False, choice=None, web="mask",
                     discription_ja="postgresqlのパスワードを指定する。",
                     discription_en="Specify the postgresql password."),
                dict(opt="agent_pg_dbname", type=Options.T_STR, default='agent', required=False, multi=False, hide=False, choice=None,
                     discription_ja="postgresqlデータベース名を指定します。",
                     discription_en="Specify the postgresql database name."),
                dict(opt="llmprov", type=Options.T_STR, default=None, required=False, multi=False, hide=False,
                     choice=["", "azureopenai", "openai", "vertexai", "ollama"],
                     discription_ja="llmのプロバイダを指定します。",
                     discription_en="Specify llm provider.",
                     choice_show=dict(azureopenai=["llmapikey", "llmendpoint", "llmmodel", "llmapiversion"],
                                      openai=["llmapikey", "llmendpoint", "llmmodel"],
                                      vertexai=["llmprojectid", "llmsvaccountfile", "llmlocation", "llmmodel", "llmseed", "llmtemperature"],
                                      ollama=["llmendpoint", "llmmodel", "llmtemperature"],),
                     ),
                dict(opt="llmprojectid", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのプロジェクトIDを指定します。",
                     discription_en="Specify the project ID for llm's provider connection."),
                dict(opt="llmsvaccountfile", type=Options.T_FILE, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのサービスアカウントファイルを指定します。",
                     discription_en="Specifies the service account file for llm's provider connection."),
                dict(opt="llmlocation", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのロケーションを指定します。",
                     discription_en="Specifies the location for llm provider connections."),
                dict(opt="llmapikey", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのAPIキーを指定します。",
                     discription_en="Specify API key for llm provider connection."),
                dict(opt="llmapiversion", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのAPIバージョンを指定します。",
                     discription_en="Specifies the API version for llm provider connections."),
                dict(opt="llmendpoint", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのプロバイダ接続のためのエンドポイントを指定します。",
                     discription_en="Specifies the endpoint for llm provider connections."),
                dict(opt="llmmodel", type=Options.T_STR, default="text-multilingual-embedding-002", required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmモデルを指定します。",
                     discription_en="Specifies the llm model."),
                dict(opt="llmseed", type=Options.T_INT, default=13, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmモデルを使用するときのシード値を指定します。",
                     discription_en="Specifies the seed value when using llm model."),
                dict(opt="llmtemperature", type=Options.T_FLOAT, default=0.1, required=False, multi=False, hide=False, choice=None,
                     discription_ja="llmのモデルを使用するときのtemperatureを指定します。",
                     discription_en="Specifies the temperature when using llm model."),
            ])

    def create_mcpserver(self, args:argparse.Namespace) -> Any:
        """
        mcpserverを作成します

        Args:
            args (argparse.Namespace): 引数

        Returns:
            Any: FastMCP
        """
        from mcp.server.fastmcp import FastMCP
        mcp = FastMCP(name=self.ver.__appid__)
        return mcp

    def create_session_service(self, args:argparse.Namespace) -> Any:
        """
        セッションサービスを作成します

        Args:
            args (argparse.Namespace): 引数

        Returns:
            BaseSessionService: セッションサービス
        """
        from google.adk.events import Event
        from google.adk.sessions import DatabaseSessionService, InMemorySessionService, session
        from typing_extensions import override
        if hasattr(args, 'agent_session_dburl') and args.agent_session_dburl is not None:
            class _DatabaseSessionService(DatabaseSessionService):
                @override
                async def append_event(self, session: session.Session, event: Event) -> Event:
                    # 永続化されるセッションには <important> タグを含めない
                    bk_parts = event.content.parts.copy()
                    for part in event.content.parts:
                        if not part.text: continue
                        part.text = re.sub(r"<important>.*</important>", "", part.text)
                    for part in bk_parts:
                        if not part.text: continue
                        part.text = part.text.replace("<important>", "").replace("</important>", "")
                    ret = await super().append_event(session, event)
                    ret.content.parts = bk_parts
                    return ret
            dss = _DatabaseSessionService(db_url=args.agent_session_dburl)
            #dss.db_engine.echo = True
            return dss
        else:
            return InMemorySessionService()

    def create_agent(self, logger:logging.Logger, args:argparse.Namespace, tools:List[Callable]) -> Any:
        """
        エージェントを作成します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tools (List[Callable]): 関数

        Returns:
            Agent: エージェント
        """
        if logger.level == logging.DEBUG:
            logger.debug(f"create_agent processing..")
        language, _ = locale.getlocale()
        is_japan = language.find('Japan') >= 0 or language.find('ja_JP') >= 0
        description = f"{self.ver.__appid__}に登録されているコマンド提供"
        instruction = f"あなたはコマンドの意味を熟知しているエキスパートです。" + \
                      f"ユーザーがコマンドを実行したいとき、あなたは以下の手順に従ってコマンドを確実に実行してください。\n" + \
                      f"1. ユーザーのクエリからが実行したいコマンドを特定します。\n" + \
                      f"2. コマンド実行に必要なパラメータのなかで、ユーザーのクエリから取得できないものは、コマンド定義にあるデフォルト値を指定して実行してください。\n" + \
                      f"3. もしエラーが発生した場合は、ユーザーにコマンド名とパラメータとエラー内容を提示してください。\n"
        """
                    f"2. コマンド実行に必要なパラメータを特定します。\n" + \
                    f"3. ユーザーのクエリから指定しているパラメータを取得します。\n" + \
                    f"4. ユーザーが指定しているパラメータと、コマンド実行に必要なパラメータを比較し、不足しているパラメータを取得します。\n" + \
                    f"5. 以下に「パラメータ = デフォルト値」を示しているので、不足しているパラメータはデフォルト値を使用します。\n" + \
                    f"   但しコマンドが実行に必要のないパラメータは指定しないようにしてください。\n" + \
                    f" host = {args.host if hasattr(args, 'host') and args.host else self.default_host}\n" + \
                    f" port = {args.port if hasattr(args, 'port') and args.port else self.default_port}\n" + \
                    f" password = {args.password if hasattr(args, 'password') and args.password else self.default_pass}\n" + \
                    f" svname = {args.svname if hasattr(args, 'svname') and args.svname else self.default_svname}\n" + \
                    f" data = {args.data if hasattr(args, 'data') and args.data else self.default_data}\n" + \
                    f" retry_count = {args.retry_count if hasattr(args, 'retry_count') and args.retry_count else 3}\n" + \
                    f" retry_interval = {args.retry_interval if hasattr(args, 'retry_interval') and args.retry_interval else 3}\n" + \
                    f" timeout = {args.timeout if hasattr(args, 'timeout') and args.timeout else 15}\n" + \
                    f" output_json = {args.output_json if hasattr(args, 'output_json') and args.output_json else None}\n" + \
                    f" output_json_append = {args.output_json_append if hasattr(args, 'output_json_append') and args.output_json_append else False}\n" + \
                    f" stdout_log = {args.stdout_log if hasattr(args, 'stdout_log') and args.stdout_log else False}\n" + \
                    f" capture_stdout = {args.capture_stdout if hasattr(args, 'capture_stdout') and args.capture_stdout else False}\n" + \
                    f" capture_maxsize = {args.capture_maxsize if hasattr(args, 'capture_maxsize') and args.capture_maxsize else 100}\n" + \
                    f" tag = {args.tag if hasattr(args, 'tag') and args.tag else None}\n" + \
                    f" clmsg_id = {args.clmsg_id if hasattr(args, 'clmsg_id') and args.clmsg_id else None}\n" + \
                    f" signin_file = {args.signin_file if hasattr(args, 'signin_file') and args.signin_file else f'.{self.ver.__appid__}/user_list.yml'}\n" + \
                    f"6. 以上のパラメータを使用しても不足するパラメータは、Noneを使用します。\n" + \
                    f"7. 以上のパラメータを使用してコマンドを実行して、コマンドの結果はJSONでユーザーに提示してください。\n" + \
                    f"8. もし予期しないパラメータを受け取ったという旨のエラーが発生した場合は、そのパラメータを指定せずに再実行してください。\n" + \
                    f"9. もしエラーが発生した場合は、ユーザーにコマンド名とパラメータとエラー内容を提示してください。\n"
        """

        description = description if is_japan else \
                      f"Command offer registered in {self.ver.__appid__}."
        instruction = instruction if is_japan else \
                      f"You are the expert who knows what the commands mean." + \
                      f"When a user wants to execute a command, you follow these steps to ensure that the command is executed.\n" + \
                      f"1. Identify the command you want to execute from the user's query.\n" + \
                      f"2. Any parameters required to execute the command that cannot be obtained from the user's query should be executed with the default values provided in the command definition.\n" + \
                      f"3. If an error occurs, provide the user with the command name, parameters, and error description.\n"
        """
                      f"2. Identify the parameters required to execute the command.\n" + \
                      f"3. Retrieve the specified parameters from the user's query.\n" + \
                      f"4. It compares the parameters specified by the user with those required to execute the command and obtains the missing parameters.\n" + \
                      f"5. The “Parameter = Default Value” is shown below, so use default values for missing parameters.\n" + \
                      f"   However, do not specify parameters that the command does not require for execution.\n" + \
                      f" host = {args.host if hasattr(args, 'host') and args.host else self.default_host}\n" + \
                      f" port = {args.port if hasattr(args, 'port') and args.port else self.default_port}\n" + \
                      f" password = {args.password if hasattr(args, 'password') and args.password else self.default_pass}\n" + \
                      f" svname = {args.svname if hasattr(args, 'svname') and args.svname else self.default_svname}\n" + \
                      f" data = {args.data if hasattr(args, 'data') and args.data else self.default_data}\n" + \
                      f" retry_count = {args.retry_count if hasattr(args, 'retry_count') and args.retry_count else 3}\n" + \
                      f" retry_interval = {args.retry_interval if hasattr(args, 'retry_interval') and args.retry_interval else 3}\n" + \
                      f" timeout = {args.timeout if hasattr(args, 'timeout') and args.timeout else 15}\n" + \
                      f" output_json = {args.output_json if hasattr(args, 'output_json') and args.output_json else None}\n" + \
                      f" output_json_append = {args.output_json_append if hasattr(args, 'output_json_append') and args.output_json_append else False}\n" + \
                      f" stdout_log = {args.stdout_log if hasattr(args, 'stdout_log') and args.stdout_log else False}\n" + \
                      f" capture_stdout = {args.capture_stdout if hasattr(args, 'capture_stdout') and args.capture_stdout else False}\n" + \
                      f" capture_maxsize = {args.capture_maxsize if hasattr(args, 'capture_maxsize') and args.capture_maxsize else 100}\n" + \
                      f" tag = {args.tag if hasattr(args, 'tag') and args.tag else None}\n" + \
                      f" clmsg_id = {args.clmsg_id if hasattr(args, 'clmsg_id') and args.clmsg_id else None}\n" + \
                      f"6. Use None for parameters that are missing even with the above parameters.\n" + \
                      f"7. Execute the command using the above parameters and present the results of the command to the user in JSON.\n" + \
                      f"8. If you receive an error stating that an unexpected parameter was received, rerun the program without that parameter.\n" + \
                      f"9. If an error occurs, provide the user with the command name, parameters, and error description.\n"
        """

        description = args.agent_description if args.agent_description else description
        instruction = args.agent_instruction if args.agent_instruction else instruction
        if logger.level == logging.DEBUG:
            logger.debug(f"google-adk loading..")
        from google.adk.agents import Agent
        if logger.level == logging.DEBUG:
            logger.debug(f"litellm loading..")
        from google.adk.models.lite_llm import LiteLlm
        # loggerの初期化
        common.reset_logger("LiteLLM Proxy")
        common.reset_logger("LiteLLM Router")
        common.reset_logger("LiteLLM")
        if args.llmprov == 'openai':
            if args.llmmodel is None: raise ValueError("llmmodel is required.")
            if args.llmapikey is None: raise ValueError("llmapikey is required.")
            agent = Agent(
                name=args.agent_name,
                model=LiteLlm(
                    model=args.llmmodel,
                    api_key=args.llmapikey,
                    endpoint=args.llmendpoint,
                ),
                description=description,
                instruction=instruction,
                tools=tools,
            )
        elif args.llmprov == 'azureopenai':
            if args.llmmodel is None: raise ValueError("llmmodel is required.")
            if args.llmendpoint is None: raise ValueError("llmendpoint is required.")
            if args.llmapikey is None: raise ValueError("llmapikey is required.")
            if args.llmapiversion is None: raise ValueError("llmapiversion is required.")
            agent = Agent(
                name=args.agent_name,
                model=LiteLlm(
                    model=args.llmmodel,
                    api_key=args.llmapikey,
                    endpoint=args.llmendpoint,
                    api_version=args.llmapiversion,
                ),
                description=description,
                instruction=instruction,
                tools=tools,
            )
        elif args.llmprov == 'vertexai':
            if args.llmmodel is None: raise ValueError("llmmodel is required.")
            if args.llmlocation is None: raise ValueError("llmlocation is required.")
            if args.llmsvaccountfile is not None: 
                with open(args.llmsvaccountfile, "r", encoding="utf-8") as f:
                    vertex_credentials = json.load(f)
            elif args.llmprojectid is None: raise ValueError("llmprojectid is required.")
            agent = Agent(
                name=args.agent_name,
                model=LiteLlm(
                    model=args.llmmodel,
                    #vertex_project=args.llmprojectid,
                    vertex_credentials=vertex_credentials,
                    vertex_location=args.llmlocation,
                    #seed=args.llmseed,
                    #temperature=args.llmtemperature,
                ),
                description=description,
                instruction=instruction,
                tools=tools,
            )
        elif args.llmprov == 'ollama':
            if args.llmmodel is None: raise ValueError("llmmodel is required.")
            if args.llmendpoint is None: raise ValueError("llmendpoint is required.")
            agent = Agent(
                name=args.agent_name,
                model=LiteLlm(
                    model=f"ollama/{args.llmmodel}",
                    api_base=args.llmendpoint,
                    temperature=args.llmtemperature,
                    stream=True
                ),
                description=description,
                instruction=instruction,
                tools=tools,
            )
        else:
            raise ValueError("llmprov is required.")
        if logger.level == logging.DEBUG:
            logger.debug(f"create_agent complate.")
        return agent

    def create_runner(self, logger:logging.Logger, args:argparse.Namespace, session_service, agent) -> Any:
        """
        ランナーを作成します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            session_service (BaseSessionService): セッションサービス
            agent (Agent): エージェント

        Returns:
            Runner: ランナー
        """
        from google.adk.runners import Runner
        return Runner(
            app_name=self.ver.__appid__,
            agent=agent,
            session_service=session_service,
        )

    def init_agent_runner(self, logger:logging.Logger, args:argparse.Namespace) -> Tuple[Any, Any]:
        """
        エージェントの初期化を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            Tuple[Any, Any]: ランナーとFastMCP
        """
        if logger.level == logging.DEBUG:
            logger.debug(f"init_agent_runner processing..")
        # loggerの初期化
        common.reset_logger("httpx")
        common.reset_logger("google_adk.google.adk.sessions.database_session_service")
        common.reset_logger("mcp.server.streamable_http_manager")
        # モジュールインポート
        from mcp.server.fastmcp import FastMCP
        from google.adk.sessions import BaseSessionService
        mcp:FastMCP = self.create_mcpserver(args)
        session_service:BaseSessionService = self.create_session_service(args)
        options = Options.getInstance()
        tools:Callable[[logging.Logger, argparse.Namespace, float, Dict], Tuple[int, Dict[str, Any], Any]] = []

        def _ds(d:str) -> str:
            return f'"{d}"' if d is not None else 'None'
        def _t2s(o:Dict[str, Any], req=True) -> str:
            t, m, d, r = o["type"], o["multi"], o["default"], o["required"]
            if t == Options.T_BOOL: return ("List[bool]=[]" if m else f"bool={d}") if req else ("List[bool]" if m else f"bool")
            if t == Options.T_DATE: return ("List[str]=[]" if m else f"str={_ds(d)}") if req else ("List[str]" if m else f"str")
            if t == Options.T_DATETIME: return ("List[str]=[]" if m else f"str={_ds(d)}") if req else ("List[str]" if m else f"str")
            if t == Options.T_DICT: return ("List[dict]=[]" if m else f"dict={d}") if req else ("List[dict]" if m else f"dict")
            if t == Options.T_DIR or t == Options.T_FILE:
                if d is not None: d = str(d).replace('\\', '/')
                return ("List[str]=[]" if m else f"str={_ds(d)}") if req else ("List[str]" if m else f"str")
            if t == Options.T_FLOAT: return ("List[float]=[]" if m else f"float={d}") if req else ("List[float]" if m else f"float")
            if t == Options.T_INT: return ("List[int]=[]" if m else f"int={d}") if req else ("List[int]" if m else f"int")
            if t == Options.T_STR: return ("List[str]=[]" if m else f"str={_ds(d)}") if req else ("List[str]" if m else f"str")
            if t == Options.T_TEXT: return ("List[str]=[]" if m else f"str={_ds(d)}") if req else ("List[str]" if m else f"str")
            raise ValueError(f"Unknown type: {t} for option {o['opt']}")
        def _arg(o:Dict[str, Any], is_japan) -> str:
            t, d = o["type"], o["default"]
            s = f'        {o["opt"]}:'
            if t == Options.T_DIR or t == Options.T_FILE:
                d = str(d).replace("\\", "/")
            s += f'Optional[{_t2s(o, False)}]={d}:'
            s += f'{o["discription_ja"] if is_japan else o["discription_en"]}'
            return s
        def _coercion(a:argparse.Namespace, key:str, dval) -> str:
            dval = f'opt["{key}"] if "{key}" in opt else ' + f'"{dval}"' if isinstance(dval, str) else dval
            aval = args.__dict__[key] if hasattr(args, key) and args.__dict__[key] else None
            aval = f'"{aval}"' if isinstance(aval, str) else aval
            ret = f'opt["{key}"] = {aval}' if aval is not None else f'opt["{key}"] = {dval}'
            return ret
        language, _ = locale.getlocale()
        is_japan = language.find('Japan') >= 0 or language.find('ja_JP') >= 0
        for mode in options.get_mode_keys():
            for cmd in options.get_cmd_keys(mode):
                if not options.get_cmd_attr(mode, cmd, 'use_agent'):
                    continue
                discription = options.get_cmd_attr(mode, cmd, 'discription_ja' if is_japan else 'discription_en')
                choices = options.get_cmd_choices(mode, cmd, False)
                if len([opt for opt in choices if 'opt' in opt and opt['opt'] == 'signin_file']) <= 0:
                    choices.append(dict(opt="signin_file", type=Options.T_FILE, default=f'.{self.ver.__appid__}/user_list.yml', required=True, multi=False, hide=True, choice=None,
                        discription_ja="サインイン可能なユーザーとパスワードを記載したファイルを指定します。省略した時は認証を要求しません。",
                        discription_en="Specify a file containing users and passwords with which they can signin. If omitted, no authentication is required."),)
                fn = f"{mode}_{cmd}"
                func_txt =  f'@mcp.tool()\n'
                func_txt += f'def {fn}(' + ", ".join([f'{o["opt"]}:{_t2s(o, False)}' for o in choices]) + '):\n'
                func_txt += f'    """\n'
                func_txt += f'    {discription}\n'
                func_txt += f'    Args:\n'
                func_txt += "\n".join([_arg(o, is_japan) for o in choices])
                func_txt += f'\n'
                func_txt += f'    Returns:\n'
                func_txt += f'        Dict[str, Any]:{"処理結果" if is_japan else "Processing Result"}\n'
                func_txt += f'    """\n'
                func_txt += f'    scope = signin.get_request_scope()\n'
                func_txt += f'    logger = common.default_logger()\n'
                func_txt += f'    opt = dict()\n'
                func_txt += f'    opt["mode"] = "{mode}"\n'
                func_txt += f'    opt["cmd"] = "{cmd}"\n'
                func_txt += f'    opt["data"] = opt["data"] if hasattr(opt, "data") else common.HOME_DIR / ".{self.ver.__appid__}"\n'
                func_txt += f'    opt["format"] = False\n'
                func_txt += f'    opt["output_json"] = None\n'
                func_txt += f'    opt["output_json_append"] = False\n'
                func_txt += f'    opt["debug"] = logger.level == logging.DEBUG\n'
                func_txt += '\n'.join([f'    opt["{o["opt"]}"] = {o["opt"]}' for o in choices])+'\n'
                func_txt += f'    {_coercion(args, "host", self.default_host)}\n'
                func_txt += f'    {_coercion(args, "port", self.default_port)}\n'
                func_txt += f'    {_coercion(args, "password", self.default_pass)}\n'
                func_txt += f'    {_coercion(args, "svname", self.default_svname)}\n'
                func_txt += f'    {_coercion(args, "retry_count", 3)}\n'
                func_txt += f'    {_coercion(args, "retry_interval", 3)}\n'
                func_txt += f'    {_coercion(args, "timeout", 15)}\n'
                func_txt += f'    {_coercion(args, "output_json", None)}\n'
                func_txt += f'    {_coercion(args, "output_json_append", False)}\n'
                func_txt += f'    {_coercion(args, "stdout_log", False)}\n'
                func_txt += f'    {_coercion(args, "capture_stdout", False)}\n'
                func_txt += f'    {_coercion(args, "capture_maxsize", 1024*1024)}\n'
                func_txt += f'    {_coercion(args, "tag", None)}\n'
                func_txt += f'    {_coercion(args, "clmsg_id", None)}\n'
                func_txt += f'    opt["signin_file"] = signin_file if signin_file else ".{self.ver.__appid__}/user_list.yml"\n'
                func_txt += f'    args = argparse.Namespace(**opt)\n'
                func_txt += f'    signin_data = signin.Signin.load_signin_file(args.signin_file)\n'
                func_txt += f'    req = scope["req"] if scope["req"] is not None else scope["websocket"]\n'
                func_txt += f'    sign = signin.Signin._check_signin(req, scope["res"], signin_data, logger)\n'
                func_txt += f'    if sign is not None:\n'
                func_txt += f'        logger.warning("Unable to execute command because authentication information cannot be obtained")\n'
                func_txt += f'        return dict(warn="Unable to execute command because authentication information cannot be obtained")\n'
                func_txt += f'    groups = req.session["signin"]["groups"]\n'
                func_txt += f'    logger.info("Call agent tool `{mode}_{cmd}`:user="+str(req.session["signin"]["name"])+" groups="+str(groups)+" args="+str(args))\n'
                func_txt += f'    if not signin.Signin._check_cmd(signin_data, groups, "{mode}", "{cmd}", logger):\n'
                func_txt += f'        logger.warning("You do not have permission to execute this command.")\n'
                func_txt += f'        return dict(warn="You do not have permission to execute this command.")\n'
                func_txt += f'    feat = Options.getInstance().get_cmd_attr("{mode}", "{cmd}", "feature")\n'
                func_txt += f'    try:\n'
                func_txt += f'        st, ret, _ = feat.apprun(logger, args, time.perf_counter(), [])\n'
                func_txt += f'        return ret\n'
                func_txt += f'    except Exception as e:\n'
                func_txt += f'        logger.error("Error occurs when tool is executed:", exc_info=True)\n'
                func_txt += f'        raise e\n'
                func_txt += f'tools.append({fn})\n'
                if logger.level == logging.DEBUG:
                    logger.debug(f"generating agent tool: {fn}")

                exec(func_txt,
                     dict(time=time,List=List, argparse=argparse, common=common, Options=Options, logging=logging, signin=signin,),
                     dict(tools=tools, mcp=mcp))
        root_agent = self.create_agent(logger, args, tools)
        runner = self.create_runner(logger, args, session_service, root_agent)
        if logger.level == logging.DEBUG:
            logger.debug(f"init_agent_runner complate.")
        return runner, mcp
