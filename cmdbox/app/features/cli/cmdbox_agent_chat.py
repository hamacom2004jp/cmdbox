from cmdbox.app import common, client, feature, options
from cmdbox.app.auth import signin
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import asyncio
import argparse
import logging
import json
import re
import time


class CmdAgentChat(feature.ResultEdgeFeature):

    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'chat'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE,
            nouse_webmode=False,
            use_agent=True,
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
                dict(opt="timeout", type=Options.T_INT, default="120", required=False, multi=False, hide=True, choice=None,
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
                dict(opt="mcpserver_apikey", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="リモートMCPサーバーのAPI Keyを指定します。",
                    description_en="Specify the API Key of the remote MCP server.",),
                dict(opt="message", type=Options.T_TEXT, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="Runnerに送信するメッセージを指定します。",
                    description_en="Specify the message to send to the Runner."),
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
        if not getattr(args, 'user_name', None):
            msg = dict(warn="Please specify --user_name")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not getattr(args, 'runner_name', None):
            msg = dict(warn="Please specify --runner_name")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not re.match(r'^[\w\-]+$', args.runner_name):
            msg = dict(warn="Runner name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        payload = dict(runner_name=args.runner_name, user_name=args.user_name, session_id=args.session_id,
                       mcpserver_apikey=args.mcpserver_apikey, message=args.message)
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        msg = dict(success=[], warn=[])
        for res in cl.redis_cli.send_cmd_sse(self.get_svcmd(), [payload_b64],
                                             retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False):
            common.print_format(res, False, tm, None, False, pf=pf)
            if 'success' in res:
                msg['success'].append(res['success'])
            elif 'warn' in res:
                msg['warn'].append(res['warn'])
            else:
                msg['warn'].append(res)
        if len(msg['success']) <= 0:
            del msg['success']
        if len(msg['warn']) > 0:
            return self.RESP_WARN, msg, cl
        return self.RESP_SUCCESS, msg, cl

    def is_cluster_redirect(self):
        return False

    async def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
                    sessions:Dict[str, Dict[str, Any]]):
        reskey = msg[1]
        try:
            if logger.level == logging.DEBUG:
                logger.debug(f"{self.get_mode()}_{self.get_cmd()} msg: {msg}")
            if 'agents' not in sessions:
                sessions['agents'] = {}

            # イベントループポリシー設定
            try:
                asyncio.set_event_loop_policy(asyncio.DefaultEventLoopPolicy())
            except Exception as e:
                if logger.level == logging.DEBUG:
                    logger.debug(f"Failed to set event loop policy: {e}")
            import platform
            if platform.system() != "Windows":
                # LiteLLMのロギングワーカーがイベントループをリセットするのを防ぐため、
                # 既存のイベントループを再利用する
                try:
                    loop = asyncio.get_running_loop()
                except:
                    loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)

            payload = json.loads(convert.b64str2str(msg[2]))
            name = payload.get('runner_name')
            user_name = payload.get('user_name')
            session_id = payload.get('session_id')
            mcpserver_apikey = payload.get('mcpserver_apikey')
            message = payload.get('message')
            if name not in sessions['agents']:
                msg = dict(warn=f"Runner '{name}' is not running.", end=True)
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN

            from google.adk.agents.run_config import RunConfig, StreamingMode
            from google.adk.events import Event
            from google.adk.runners import Runner
            from google.adk.sessions import BaseSessionService, Session
            from google.genai import types

            async def create_agent_session(session_service:BaseSessionService, runner_name:str, 
                                           user_name:str, session_id:str=None) -> Session:
                """
                セッションを作成します

                Args:
                    session_service (BaseSessionService): セッションサービス
                    app_name (str): アプリケーション名
                    user_name (str): ユーザー名
                    session_id (str): セッションID

                Returns:
                    Any: セッション
                """
                if session_id is None:
                    session_id = common.random_string(32)
                try:
                    session = await session_service.get_session(app_name=runner_name, user_id=user_name, session_id=session_id)
                    if session is None:
                        session = await session_service.create_session(app_name=runner_name, user_id=user_name, session_id=session_id)
                    return session
                except NotImplementedError:
                    # セッションが１件もない場合はNotImplementedErrorが発生することがある
                    session = await session_service.create_session(app_name=runner_name, user_id=user_name, session_id=session_id)
                    return session

            json_pattern = re.compile(r'\{.*?\}')

            runner:Runner = sessions['agents'][name]['runner']
            content = types.Content(role='user', parts=[types.Part(text=message)])
            # セッションを作成する
            agent_session = await create_agent_session(runner.session_service, name, user_name, session_id=session_id)
            # チャットを実行する
            signin.set_request_scope(dict(mcpserver_apikey=mcpserver_apikey))
            run_config = RunConfig(streaming_mode=StreamingMode.NONE)
            run_iter = runner.run_async(user_id=user_name, session_id=agent_session.id, new_message=content, run_config=run_config)
            async for event in run_iter:
                outputs = dict(success=dict(agent_session_id=agent_session.id))
                if event.turn_complete:
                    outputs['success']['turn_complete'] = True
                if event.interrupted:
                    outputs['success']['interrupted'] = True
                msg = self.__class__.gen_msg(event)
                if msg:
                    outputs['success']['message'] = msg
                    options.Options.getInstance().audit_exec(body=dict(agent_session=agent_session.id, result=msg),
                                                                audit_type=options.Options.AT_USER, user=user_name)
                    redis_cli.rpush(reskey, outputs)
                    if event.is_final_response():
                        break
            msg = dict(success=f"Chat '{name}' successfully.", end=True)
            redis_cli.rpush(reskey, msg)
            await run_iter.aclose()
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}", end=True)
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN

    @classmethod
    def _replace_match(cls, match_obj):
        json_str = match_obj.group(0)
        try:
            data = json.loads(json_str) # ユニコード文字列をエンコード
            return json.dumps(data, ensure_ascii=False, default=common.default_json_enc)
        except json.JSONDecodeError:
            return json_str

    @classmethod
    def gen_msg(cls, event:Any) -> str:
        json_pattern = re.compile(r'\{.*?\}')
        msg = None
        if event.content and event.content.parts:
            msg = "\n".join([p.text for p in event.content.parts if p and p.text])
            calls = event.get_function_calls()
            if calls:
                msg += '\n```json{"function_calls":'+common.to_str([dict(fn=c.name,args=c.args) for c in calls])+'}```'
            responses = event.get_function_responses()
            if responses:
                msg += '\n```json{"function_responses":'+common.to_str([dict(fn=r.name, res=r.response) for r in responses])+'}```'
        elif event.actions and event.actions.escalate:
            msg = f"Agent escalated: {event.error_message or 'No specific message.'}"
        if msg:
            msg = json_pattern.sub(cls._replace_match, msg)
        return msg
