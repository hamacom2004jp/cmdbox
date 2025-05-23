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
                     choice_show=dict(use=["agent_name", "agent_description", "agent_instruction", "llmprov"],)),
                dict(opt="agent_name", type=Options.T_STR, default=self.ver.__appid__, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エージェント名を指定します。",
                     discription_en="Specifies the agent name."),
                dict(opt="agent_description", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エージェントの説明を指定します。",
                     discription_en="Specify agent description."),
                dict(opt="agent_instruction", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エージェントのシステム指示を指定します。",
                     discription_en="Specifies the agent's system instructions."),
                dict(opt="agent_session_dburl", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                     discription_ja="エージェントのセッションを保存するDBのURLを指定します。",
                     discription_en="Specify the URL of the DB where the agent's sessions are stored."),
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
                dict(opt="llmtemperature", type=Options.T_FLOAT, default=None, required=False, multi=False, hide=False, choice=None,
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
        from google.adk.sessions import DatabaseSessionService, InMemorySessionService
        if hasattr(args, 'agent_session_dburl') and args.agent_session_dburl is not None:
            return DatabaseSessionService(db_url=args.agent_session_dburl)
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
                      f"ユーザーがコマンドを実行したいとき、あなたは以下の手順に従ってコマンドを実行してください。\n" + \
                      f"1. ユーザーのクエリからが実行したいコマンドを特定します。\n" + \
                      f"2. コマンド実行に必要なパラメータを特定します。\n" + \
                      f"3. ユーザーのクエリから指定しているパラメータを取得します。\n" + \
                      f"4. コマンド実行に必要なパラメータの中で、ユーザーが指定しているパラメータが不足しているものを特定します。\n" + \
                      f"5. 以下に「パラメータ = デフォルト値」を示しているので、不足しているパラメータはデフォルト値を使用します。\n" + \
                      f"   但しコマンドが実行に必要のないパラメータは指定しないようにします。\n" + \
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

        description = description if is_japan else \
                      f"Command offer registered in {self.ver.__appid__}."
        instruction = instruction if is_japan else \
                      f"You are the expert who knows what the commands mean." + \
                      f"When a user wants to execute a command, you follow these steps to execute the command.\n" + \
                      f"1. Identify the command you want to execute from the user's query.\n" + \
                      f"2. Identify the parameters required to execute the command.\n" + \
                      f"3. Retrieve the specified parameters from the user's query.\n" + \
                      f"4. Identifies missing user-specified parameters required to execute the command.\n" + \
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
                    model=args.llmmodel,
                    endpoint=args.llmendpoint,
                    temperature=args.llmtemperature,
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
        common.reset_logger("google.adk.sessions.database_session_service")
        # モジュールインポート
        from mcp.server.fastmcp import FastMCP
        from google.adk.sessions import BaseSessionService
        mcp:FastMCP = self.create_mcpserver(args)
        session_service:BaseSessionService = self.create_session_service(args)
        options = Options.getInstance()
        tools:Callable[[logging.Logger, argparse.Namespace, float, Dict], Tuple[int, Dict[str, Any], Any]] = []

        def _t2s(t:str, m:bool, d) -> str:
            if t == Options.T_BOOL: return (":List[bool]" if m else f":bool")
            if t == Options.T_DATE: return (":List[str]" if m else f":str")
            if t == Options.T_DATETIME: return (":List[str]" if m else f":str")
            if t == Options.T_DICT: return (":List[dict]" if m else ":dict")
            if t == Options.T_DIR: return (":List[str]" if m else f":str")
            if t == Options.T_FILE: return (":List[str]" if m else f":str")
            if t == Options.T_FLOAT: return (":List[float]" if m else ":float")
            if t == Options.T_INT: return (":List[int]" if m else f":int")
            if t == Options.T_STR: return (":List[str]" if m else f":str")
            if t == Options.T_TEXT: return (":List[str]" if m else f":str")
            return ""
            """
            s = f'="{d}"' if d is not None else '=""'
            if t == Options.T_BOOL: return (":List[bool]=[]" if m else f":bool={d}")
            if t == Options.T_DATE: return (":List[str]=[]" if m else f":str{s}")
            if t == Options.T_DATETIME: return (":List[str]=[]" if m else f":str{s}")
            if t == Options.T_DICT: return (":List[dict]=[]" if m else ":dict={}")
            if t == Options.T_DIR: return (":List[str]=[]" if m else f":str"+s.replace("\\", "/"))
            if t == Options.T_FILE: return (":List[str]=[]" if m else f":str"+s.replace("\\", "/"))
            if t == Options.T_FLOAT: return (":List[float]=[]" if m else ":float"+(f'={d}' if d is not None else '=0.0'))
            if t == Options.T_INT: return (":List[int]=[]" if m else f":int"+(f'={d}' if d is not None else '=0'))
            if t == Options.T_STR: return (":List[str]=[]" if m else f":str{s}")
            if t == Options.T_TEXT: return (":List[str]=[]" if m else f":str{s}")
            return "=None"
            """
        def _t2d(t:str, m:bool, d) -> str:
            s = None
            if t == Options.T_BOOL: s = "List[bool]" if m else "bool"
            if t == Options.T_DATE: s = "List[str]" if m else "str"
            if t == Options.T_DATETIME: s = "List[str]" if m else "str"
            if t == Options.T_DICT: s = "List[dict]" if m else "dict"
            if t == Options.T_DIR: s = "List[str]" if m else "str"
            if t == Options.T_FILE: s = "List[str]" if m else "str"
            if t == Options.T_FLOAT: s = "List[float]" if m else "float"
            if t == Options.T_INT:  s = "List[int]" if m else "int"
            if t == Options.T_STR: s = "List[str]" if m else "str"
            if t == Options.T_TEXT: s = "List[str]" if m else "str"
            if s is None: return " "
            return f" Optional[{s}]" if d is not None else f" {s}"
        def _arg(o:Dict[str, Any], is_japan) -> str:
            #f'        {o["opt"]}{_t2d(o["type"], o["multi"], o["default"])}: {o["discription_ja"] if is_japan else o["discription_en"]}\n'
            s = f'        {o["opt"]}{_t2d(o["type"], o["multi"], o["default"])}: '
            if o["required"] == True:
                s += f'{"必須パラメータ: " if is_japan else "Required Parameter: "}'
            else:
                s += f'{"オプションパラメータ: " if is_japan else "Optional Parameter: "}'
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
                    choices.append(dict(opt="signin_file", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None,
                        discription_ja="サインイン可能なユーザーとパスワードを記載したファイルを指定します。省略した時は認証を要求しません。",
                        discription_en="Specify a file containing users and passwords with which they can signin. If omitted, no authentication is required."),)
                if len([opt for opt in choices if 'opt' in opt and opt['opt'] == 'groups']) <= 0:
                    choices.append(dict(opt="groups", type=Options.T_STR, default=None, required=False, multi=True, hide=True, choice=None,
                        discription_ja="`signin_file` を指定した場合に、このユーザーグループに許可されているコマンドかどうかをチェックします。",
                        discription_en="If `signin_file` is specified, checks if the command is allowed for this user group."),)
                fn = f"{mode}_{cmd}"
                func_txt =  f'@mcp.tool()\n'
                func_txt += f'def {fn}('+", ".join([f'{o["opt"]}{_t2s(o["type"], o["multi"], o["default"])}' for o in choices])+'):\n'
                func_txt += f'    """\n'
                func_txt += f'    {discription}\n'
                func_txt += f'    Args:\n'
                func_txt += "".join([_arg(o, is_japan) for o in choices])
                func_txt += f'    Returns:\n'
                func_txt += f'        Dict[str, Any]:{"処理結果" if is_japan else "Processing Result"}\n'
                func_txt += f'    """\n'
                func_txt += f'    logger = logging.getLogger("agent")\n'
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
                func_txt += f'    groups = groups if groups else []\n'
                func_txt += f'    args = argparse.Namespace(**opt)\n'
                func_txt += f'    signin_data = signin.Signin.load_signin_file(args.signin_file)\n'
                func_txt += f'    if not signin.Signin._check_cmd(signin_data, groups, "{mode}", "{cmd}", logger):\n'
                func_txt += f'        return dict(warn="You do not have permission to execute this command.")\n'
                func_txt += f'    feat = Options.getInstance().get_cmd_attr("{mode}", "{cmd}", "feature")\n'
                func_txt += f'    st, ret, _ = feat.apprun(logger, args, time.perf_counter(), [])\n'
                func_txt += f'    return ret\n'
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
