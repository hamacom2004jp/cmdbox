from cmdbox.app import common, feature
from cmdbox.app.options import Options
from cmdbox.app.auth import signin
from pathlib import Path
from typing import Callable, List, Dict, Any, Tuple
import argparse
import glob
import logging
import locale
import json
import time
import re
import os


class Mcp:
    default_host:str = os.environ.get('REDIS_HOST', 'localhost')
    default_port:int = int(os.environ.get('REDIS_PORT', '6379'))
    default_pass:str = os.environ.get('REDIS_PASSWORD', 'password')
    default_svname:str = os.environ.get('SVNAME', 'server')

    def __init__(self, logger:logging.Logger, data:Path, sign:signin.Signin, appcls=None, ver=None,):
        """
        MCP (Multi-Channel Protocol) クラスの初期化

        Args:
            logger (logging.Logger): ロガー
            data (Path): データのパス
            sign (signin.Signin): サインインオブジェクト
            appcls (type, optional): アプリケーションクラス. Defaults to None.
            ver (module, optional): バージョンモジュール. Defaults to None.
        """
        self.logger = logger
        self.data = data
        self.appcls = appcls
        self.ver = ver
        self.signin = sign

    def create_mcpserver(self, logger:logging.Logger, args:argparse.Namespace, tools) -> Any:
        """
        mcpserverを作成します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tools (List[Callable]): ツールのリスト

        Returns:
            Any: FastMCP
        """
        from fastmcp import FastMCP
        from fastmcp.server.auth import BearerAuthProvider
        cls = self.signin.__class__
        publickey_str = cls.verify_jwt_publickey_str if hasattr(cls, 'verify_jwt_publickey_str') else None
        issuer = cls.verify_jwt_issuer if hasattr(cls, 'verify_jwt_issuer') else None
        audience = cls.verify_jwt_audience if hasattr(cls, 'verify_jwt_audience') else None
        if publickey_str is not None and issuer is not None and audience is not None:
            self.logger.info(f"Using BearerAuthProvider with public key, issuer: {issuer}, audience: {audience}")
            auth = BearerAuthProvider(
                public_key=publickey_str,
                issuer=issuer,
                audience=audience
            )
            mcp = FastMCP(name=self.ver.__appid__, auth=auth, tools=tools)
        else:
            self.logger.info(f"Using BearerAuthProvider without public key, issuer, or audience.")
            mcp = FastMCP(name=self.ver.__appid__)
        mcp.add_middleware(self.create_mw_logging(self.logger, args))
        mcp.add_middleware(self.create_mw_reqscope(self.logger, args))
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
        is_japan = common.is_japan()
        description = f"{self.ver.__appid__}に登録されているコマンド提供"
        instruction = f"あなたはコマンドの意味を熟知しているエキスパートです。" + \
                      f"ユーザーがコマンドを実行したいとき、あなたは以下の手順に従ってコマンドを確実に実行してください。\n" + \
                      f"1. ユーザーのクエリからが実行したいコマンドを特定します。\n" + \
                      f"2. コマンド実行に必要なパラメータのなかで、ユーザーのクエリから取得できないものは、コマンド定義にあるデフォルト値を指定して実行してください。\n" + \
                      f"3. もしエラーが発生した場合は、ユーザーにコマンド名とパラメータとエラー内容を提示してください。\n" \
                      f"4. コマンドの実行結果は、json文字列で出力するようにしてください。この時json文字列は「```json」と「```」で囲んだ文字列にしてください。\n"

        description = description if is_japan else \
                      f"Command offer registered in {self.ver.__appid__}."
        instruction = instruction if is_japan else \
                      f"You are the expert who knows what the commands mean." + \
                      f"When a user wants to execute a command, you follow these steps to ensure that the command is executed.\n" + \
                      f"1. Identify the command you want to execute from the user's query.\n" + \
                      f"2. Any parameters required to execute the command that cannot be obtained from the user's query should be executed with the default values provided in the command definition.\n" + \
                      f"3. If an error occurs, provide the user with the command name, parameters, and error description.\n" \
                      f"4. The result of the command execution should be output as a json string. The json string should be a string enclosed in '```json' and '```'."

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

    def _to_schema(self, o:Dict[str, Any], is_japan:bool) -> Dict[str, Any]:
        t, m = o["type"], o["multi"]
        title = o['opt'].title().replace('_', ' ')
        description = o['description_ja'] if is_japan else o['description_en']
        if t == Options.T_BOOL:
            return dict(title=title, type="array", items=dict(type="boolean"), description=description) if m \
                else dict(title=title, type="boolean", description=description)
        if t == Options.T_DATE:
            return dict(title=title, type="array", items=dict(type="string"), description=description) if m \
                else dict(title=title, type="string", description=description)
        if t == Options.T_DATETIME:
            return dict(title=title, type="array", items=dict(type="string"), description=description) if m \
                else dict(title=title, type="string", description=description)
        if t == Options.T_DICT:
            return dict(title=title, type="array", items=dict(additionalProperties=True, type="object"), description=description) if m \
                else dict(title=title, type="object", description=description)
        if t == Options.T_DIR or t == Options.T_FILE:
            return dict(title=title, type="array", items=dict(type="string"), description=description) if m \
                else dict(title=title, type="string", description=description)
        if t == Options.T_FLOAT:
            return dict(title=title, type="array", items=dict(type="number"), description=description) if m \
                else dict(title=title, type="number", description=description)
        if t == Options.T_INT:
            return dict(title=title, type="array", items=dict(type="integer"), description=description) if m \
                else dict(title=title, type="integer", description=description)
        if t == Options.T_STR or t == Options.T_TEXT:
            return dict(title=title, type="array", items=dict(type="string"), description=description) if m \
                    else dict(title=title, type="string", description=description)
        raise ValueError(f"Unknown type: {t} for option {o['opt']}")

    def _ds(self, d:str) -> str:
        return f'"{d}"' if d is not None else 'None'
    
    def _doc_arg_type(self, o:Dict[str, Any], use_default:True) -> str:
        t, m, d, r = o["type"], o["multi"], o["default"], o["required"]
        ret = ""
        dft = "None"
        if t == Options.T_BOOL:
            ret = "List[bool]" if m else f"bool"
            dft = "[]" if m else f"{d}"
        elif t == Options.T_DATE:
            ret = "List[str]" if m else f"str"
            dft = "[]" if m else self._ds(d)
        elif t == Options.T_DATETIME:
            ret = "List[str]" if m else f"str"
            dft = "[]" if m else self._ds(d)
        elif t == Options.T_DICT:
            ret = "Dict" if m else f"Dict"
            dft = "{}" if m else self._ds(d)
        elif t == Options.T_DIR or t == Options.T_FILE:
            if d is not None: d = str(d).replace('\\', '/')
            ret = "List[str]" if m else f"str"
            dft = "[]" if m else self._ds(d)
        elif t == Options.T_FLOAT:
            ret ="List[float]" if m else f"float"
            dft ="[]" if m else f"{d}"
        elif t == Options.T_INT:
            ret = "List[int]" if m else f"int"
            dft = "[]" if m else f"{d}"
        elif t == Options.T_STR or t == Options.T_TEXT:
            ret = "List[str]" if m else f"str"
            dft = "[]" if m else self._ds(d)
        else:
            raise ValueError(f"Unknown type: {t} for option {o['opt']}")
        return f"{ret}={dft}" if use_default else ret

    def _doc_arg(self, o:Dict[str, Any], is_japan) -> str:
        s = f'        {o["opt"]}:{self._doc_arg_type(o, True)} '
        s += f'{o["description_ja"] if is_japan else o["description_en"]}'
        return s

    def _create_func_txt(self, func_name:str, mode:str, cmd:str, is_japan:bool, options:Options, title:str='') -> str:
        description = options.get_cmd_attr(mode, cmd, 'description_ja' if is_japan else 'description_en')
        choices = options.get_cmd_choices(mode, cmd, False)
        func_doc_args = "\n".join([self._doc_arg(o, is_japan) for o in choices])
        func_txt  = f"def {func_name}(*args, **kwargs):\n"
        func_txt += f'    """\n'
        func_txt += f'    {func_name} - MCP Tool Function\n'
        func_txt += f'    {description}\n'
        func_txt += f'\n'
        func_txt += f'    Args:\n'
        func_txt += f'        {func_doc_args}\n'
        func_txt += f'\n'
        func_txt += f'    Returns:\n'
        func_txt += f'        Dict[str, Any]: 実行結果\n'
        func_txt += f'    """\n'
        func_txt += f'    logger = logging.getLogger("web")\n'
        func_txt +=  '    opt = {o["opt"]: kwargs.get(o["opt"], o["default"]) for o in options.get_cmd_choices("'+mode+'", "'+cmd+'", False)}\n'
        func_txt += f'    opt["data"] = Path(opt["data"]) if hasattr(opt, "data") else common.HOME_DIR / f".{self.ver.__appid__}"\n'
        func_txt += f'    if "{title}":\n'
        func_txt += f'        opt_path = opt["data"] / ".cmds" / f"cmd-{title}.json"\n'
        func_txt += f'        opt.update(common.loadopt(opt_path))\n'
        func_txt += f'    scope = signin.get_request_scope()\n'
        func_txt += f'    if logger.level == logging.DEBUG:\n'
        func_txt +=  '        logger.debug(f"MCP Call scope={scope}")\n'
        func_txt += f'    opt["mode"] = "{mode}"\n'
        func_txt += f'    opt["cmd"] = "{cmd}"\n'
        func_txt += f'    opt["format"] = False\n'
        func_txt += f'    opt["output_json"] = None\n'
        func_txt += f'    opt["output_json_append"] = False\n'
        func_txt += f'    opt["debug"] = logger.level == logging.DEBUG\n'
        func_txt += f'    opt["signin_file"] = scope["web"].signin_file\n'
        func_txt += f'    args = argparse.Namespace(**opt)\n'
        func_txt += f'    signin_data = signin.Signin.load_signin_file(args.signin_file)\n'
        func_txt += f'    req = scope["req"] if scope["req"] is not None else scope["websocket"]\n'
        func_txt += f'    sign = signin.Signin._check_signin(req, scope["res"], signin_data, logger)\n'
        func_txt += f'    if sign is not None:\n'
        func_txt += f'        logger.warning("Unable to execute command because authentication information cannot be obtained")\n'
        func_txt += f'        return dict(warn="Unable to execute command because authentication information cannot be obtained")\n'
        func_txt += f'    groups = req.session["signin"]["groups"]\n'
        func_txt += f'    if not signin.Signin._check_cmd(signin_data, groups, "{mode}", "{cmd}", logger):\n'
        func_txt += f'        logger.warning("You do not have permission to execute this command.")\n'
        func_txt += f'        return dict(warn="You do not have permission to execute this command.")\n'
        func_txt += f'    feat = options.get_cmd_attr("{mode}", "{cmd}", "feature")\n'
        func_txt += f'    args.groups = groups\n'
        func_txt += f'    try:\n'
        func_txt += f'        if logger.level == logging.DEBUG:\n'
        func_txt +=  '            logger.debug(f"MCP Call {feat}#apprun, args={args}")\n'
        func_txt += f'        st, ret, _ = feat.apprun(logger, args, time.perf_counter(), [])\n'
        func_txt += f'        return ret\n'
        func_txt += f'    except Exception as e:\n'
        func_txt += f'        logger.error("Error occurs when tool is executed:", exc_info=True)\n'
        func_txt += f'        raise e\n'
        func_txt += f'func_ctx.append({func_name})\n'
        return func_txt

    def create_tools(self, logger:logging.Logger, args:argparse.Namespace, extract_callable:bool) -> Any:
        """
        ツールリストを作成します
        
        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            extract_callable (bool): コール可能な関数を抽出するかどうか

        Returns:
            ToolList: ToolListのリスト
        """
        tool_list = ToolList(self, logger)
        tool_list.extract_callable = extract_callable
        return tool_list

    def create_mw_logging(self, logger:logging.Logger, args:argparse.Namespace) -> Any:
        """
        ログ出力用のミドルウェアを作成します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数

        Returns:
            Any: ミドルウェア
        """
        from fastmcp.server.middleware import Middleware, MiddlewareContext
        class LoggingMiddleware(Middleware):
            async def on_message(self, context: MiddlewareContext, call_next):
                if logger.level == logging.DEBUG:
                    logger.debug(f"MCP Processing method=`{context.method}`, source=`{context.source}`, message=`{context.message}`")
                try:
                    result = await call_next(context)
                    if logger.level == logging.DEBUG:
                        logger.debug(f"MCP Complated method=`{context.method}`")
                    return result
                except Exception as e:
                    logger.error(f"MCP Error method=`{context.method}`, source=`{context.source}`, message=`{context.message}`: {e}", exc_info=True)
                    raise e
        return LoggingMiddleware()

    def create_mw_reqscope(self, logger:logging.Logger, args:argparse.Namespace) -> Any:
        """
        認証用のミドルウェアを作成します

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            web (Any): Web関連のオブジェクト

        Returns:
            Any: ミドルウェア
        """
        from cmdbox.app.web import Web
        from fastapi import Response
        from fastmcp.server.middleware import Middleware, MiddlewareContext
        class ReqScopeMiddleware(Middleware):
            async def on_message(self, context: MiddlewareContext, call_next):
                signin.request_scope.set(dict(req=context.fastmcp_context.request_context.request, res=Response(), websocket=None, web=Web.getInstance()))
                result = await call_next(context)
                return result
        return ReqScopeMiddleware()

    def init_agent_runner(self, logger:logging.Logger, args:argparse.Namespace, web:Any) -> Tuple[Any, Any]:
        """
        エージェントの初期化を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            web (Any): Web関連のオブジェクト

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
        from fastmcp import FastMCP
        from google.adk.sessions import BaseSessionService
        session_service:BaseSessionService = self.create_session_service(args)
        mcp:FastMCP = self.create_mcpserver(logger, args, self.create_tools(logger, args, False))
        root_agent = self.create_agent(logger, args, self.create_tools(logger, args, True))
        runner = self.create_runner(logger, args, session_service, root_agent)
        if logger.level == logging.DEBUG:
            logger.debug(f"init_agent_runner complate.")
        return runner, mcp

class ToolList(object):
    def __init__(self, mcp:Mcp, logger:logging.Logger, *args:List):
        """
        ツールリストを初期化します

        Args:
            mcp (Mcp): MCPインスタンス
            logger (logging.Logger): ロガー
            *args (List): 追加するツールのリスト
        """
        from fastmcp.tools import FunctionTool
        options = Options.getInstance()
        is_japan = common.is_japan()

        self.tools = []
        self.mcp = mcp
        self.logger = logger
        self.extract_callable = False
        for mode in options.get_mode_keys():
            for cmd in options.get_cmd_keys(mode):
                if not options.get_cmd_attr(mode, cmd, 'use_agent'):
                    continue
                # コマンドの説明と選択肢を取得
                description = options.get_cmd_attr(mode, cmd, 'description_ja' if is_japan else 'description_en')
                choices = options.get_cmd_choices(mode, cmd, False)
                func_name = f"{mode}_{cmd}"
                # 関数の定義を生成
                func_txt  = self.mcp._create_func_txt(func_name, mode, cmd, is_japan, options)
                if self.logger.level == logging.DEBUG:
                    self.logger.debug(f"generating agent tool: {func_name}")
                func_ctx = []
                # 関数を実行してコンテキストに追加
                exec(func_txt,
                    dict(time=time,List=List, Path=Path, argparse=argparse, common=common, options=options, logging=logging, signin=signin,),
                    dict(func_ctx=func_ctx))
                # 関数のスキーマを生成
                input_schema = dict(
                    type="object",
                    properties={o['opt']: self.mcp._to_schema(o, is_japan) for o in choices},
                    required=[o['opt'] for o in choices if o['required']],
                )
                output_schema = dict(type="object", properties=dict())
                func_tool = FunctionTool(fn=func_ctx[0], name=func_name, title=func_name.title(), description=description, 
                                        tags=[f"mode={mode}", f"cmd={cmd}"],
                                        parameters=input_schema, output_schema=output_schema,)
                # ツールリストに追加
                self.tools.append(func_tool)
        for tool in args:
            if isinstance(tool, FunctionTool):
                if self.logger.level == logging.DEBUG:
                    self.logger.debug(f"adding tool: {tool.name}")
            else:
                raise TypeError(f"Expected FunctionTool, got {type(tool)}")
            self.tools.append(tool)

    @property
    def extract_callable(self):
        """
        ツールリストから関数を抽出するかどうかを取得します

        Returns:
            bool: 関数を抽出する場合はTrue、しない場合はFalse
        """
        return self._extract_callable
    
    @extract_callable.setter
    def extract_callable(self, value:bool):
        """
        ツールリストから関数を抽出するかどうかを設定します

        Args:
            value (bool): 関数を抽出する場合はTrue、しない場合はFalse
        """
        if not isinstance(value, bool):
            raise TypeError(f"Expected bool, got {type(value)}")
        self._extract_callable = value

    def append(self, tool):
        """
        ツールを追加します

        Args:
            tool (FunctionTool): 追加するツール
        """
        from fastmcp.tools import FunctionTool
        if isinstance(tool, FunctionTool):
            self.tools.append(tool)
        else:
            raise TypeError(f"Expected FunctionTool, got {type(tool)}")

    def pop(self):
        """
        ツールを取り出します

        Returns:
            FunctionTool: 取り出したツール
        """
        if len(self.tools) == 0:
            raise IndexError("No tools available to pop.")
        return self.tools.pop()

    def __repr__(self):
        """
        ツールリストの文字列表現を返します

        Returns:
            str: ツールリストの文字列表現
        """
        return 'ToolList(' + repr(self.tools) + ')'

    def __str__(self):
        """
        ツールリストの文字列表現を返します

        Returns:
            str: ツールリストの文字列表現
        """
        return str(self.tools)

    def __getitem__(self, key:int):
        """
        ツールリストからツールを取得します

        Args:
            key (int): インデックス
        Returns:
            FunctionTool: 取得したツール
        """
        return self.tools[key]

    def __iter__(self):
        """
        ツールリストをイテレータとして返します

        Returns:
            Iterator[FunctionTool]: ツールリストのイテレータ
        """
        from cmdbox.app.web import Web
        from fastmcp.tools import FunctionTool
        options = Options.getInstance()
        is_japan = common.is_japan()
        ret_tools = self.tools.copy()
        web = Web.getInstance()
        if web.signin.signin_file_data is None:
            # サインインファイルが読み込まれていない場合は登録済みのリストを返す
            if self.extract_callable:
                # 関数を抽出する場合はツールリストから関数を抽出して返す
                return (tool.fn for tool in ret_tools if callable(tool.fn)).__iter__()
            return ret_tools.__iter__()
        try:
            # ユーザーコマンドの読み込み
            paths = glob.glob(str(Path(web.data) / ".cmds" / f"cmd-*.json"))
            cmd_list = [common.loadopt(path, True) for path in paths]
            cmd_list = sorted(cmd_list, key=lambda cmd: cmd["title"])
            # ユーザーコマンドリストの取得(すべてのコマンドを取得するためにgroupsをadminに設定)
            # 実行時にはユーザーのグループに応じて認可する
            cmd_list = [dict(title=r.get('title',''), mode=r['mode'], cmd=r['cmd'],
                        description=r.get('description','') + options.get_cmd_attr(r['mode'], r['cmd'], 'description_ja' if is_japan else 'description_en'),
                        tag=r.get('tag','')) for r in cmd_list \
                       if signin.Signin._check_cmd(web.signin.signin_file_data, ['admin'], r['mode'], r['cmd'], self.logger)]

        except Exception as e:
            # ユーザーコマンドの読み込みに失敗した場合は警告を出して登録済みのリストを返す
            self.logger.warning(f"Error loading user commands: {e}", exc_info=True)
            if self.extract_callable:
                # 関数を抽出する場合はツールリストから関数を抽出して返す
                return (tool.fn for tool in ret_tools if callable(tool.fn)).__iter__()
            return ret_tools.__iter__()
        _tools_fns = [tool.name for tool in ret_tools]
        # ユーザーコマンドの定義を関数として生成
        for opt in cmd_list:
            func_name = opt['title']
            mode, cmd, description = opt['mode'], opt['cmd'], opt['description'] if 'description' in opt and opt['description'] else ''
            choices = options.get_cmd_choices(mode, cmd, False)
            description += '\n' + options.get_cmd_attr(mode, cmd, 'description_ja' if is_japan else 'description_en')
            # 関数の定義を生成
            func_txt  = self.mcp._create_func_txt(func_name, mode, cmd, is_japan, options, title=opt['title'])
            if self.logger.level == logging.DEBUG:
                self.logger.debug(f"generating agent tool: {func_name}")
            func_ctx = []
            # 関数を実行してコンテキストに追加
            exec(func_txt,
                dict(time=time,List=List, Path=Path, argparse=argparse, common=common, options=options, logging=logging, signin=signin,),
                dict(func_ctx=func_ctx))
            # 関数のスキーマを生成
            input_schema = dict(
                type="object",
                properties={o['opt']: self.mcp._to_schema(o, is_japan) for o in choices},
                required=[],
            )
            output_schema = dict(type="object", properties=dict())
            func_tool = FunctionTool(fn=func_ctx[0], name=func_name, title=func_name.title(), description=description, 
                                     tags=[f"mode={mode}", f"cmd={cmd}"],
                                     parameters=input_schema, output_schema=output_schema,)
            if func_name in _tools_fns:
                # 既に同名の関数が存在する場合は差し替え
                self.logger.warning(f"Function {func_name} already exists, replacing.")
                ret_tools = [tool for tool in ret_tools if tool.name != func_name]
            ret_tools.append(func_tool)
        if self.extract_callable:
            # 関数を抽出する場合はツールリストから関数を抽出して返す
            return (tool.fn for tool in ret_tools if callable(tool.fn)).__iter__()
        return ret_tools.__iter__()
