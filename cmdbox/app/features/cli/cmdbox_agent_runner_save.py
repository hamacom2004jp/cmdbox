from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.features.cli import cmdbox_tts_start
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class CmdAgentRunnerSave(feature.OneshotResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'runner_save'

    def get_option(self) -> Dict[str, Any]:
        is_japan = common.is_japan()
        description = f"{self.ver.__appid__}に登録されているコマンド提供"
        description = description if is_japan else f"Provides commands registered in {self.ver.__appid__}"
        instruction = f"あなたはコマンドの意味を熟知しているエキスパートです。" + \
                      f"ユーザーがコマンドを実行したいとき、あなたは以下の手順に従ってコマンドを確実に実行してください。\n" + \
                      f"1. ユーザーのクエリからが実行したいコマンドを特定します。\n" + \
                      f"2. コマンド実行に必要なパラメータのなかで、ユーザーのクエリから取得できないものは、コマンド定義にあるデフォルト値を指定して実行してください。\n" + \
                      f"3. もしエラーが発生した場合は、ユーザーにコマンド名とパラメータとエラー内容を提示してください。\n" \
                      f"4. コマンドの実行結果は、json文字列で出力するようにしてください。この時json文字列は「```json」と「```」で囲んだ文字列にしてください。\n"
        instruction = instruction if is_japan else \
                      f"You are the expert who knows what the commands mean." + \
                      f"When a user wants to execute a command, you follow these steps to ensure that the command is executed.\n" + \
                      f"1. Identify the command you want to execute from the user's query.\n" + \
                      f"2. Any parameters required to execute the command that cannot be obtained from the user's query should be executed with the default values provided in the command definition.\n" + \
                      f"3. If an error occurs, provide the user with the command name, parameters, and error description.\n" \
                      f"4. The result of the command execution should be output as a json string. The json string should be a string enclosed in '```json' and '```'."
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="Runner 設定を保存します。",
            description_en="Saves runner configuration.",
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
                    description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                    description_ja="Redisサーバーに再接続までの秒数を指定します。",
                    description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                    description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                    description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="runner_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="保存するRunnerの名前を指定します。",
                    description_en="Specify the name of the runner configuration to save."),
                dict(opt="llm", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                    #choice_fn=self.choice_fn,
                    callcmd="async () => {await cmdbox.callcmd('agent','llm_list',{},(res)=>{"
                            + "const val = $(\"[name='llm']\").val();"
                            + "$(\"[name='llm']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='llm']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='llm']\").val(val);"
                            + "},$(\"[name='title']\").val(),'llm');"
                            + "}",
                    description_ja="Runnerが参照するLLM設定名を指定します。",
                    description_en="LLM configuration name or reference."),
                dict(opt="mcpservers", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=[],
                    #choice_fn=self.choice_fn,
                    callcmd="async () => {await cmdbox.callcmd('agent','mcpsv_list',{},(res)=>{"
                            + "const val = $(\"[name='mcpservers']\").val();"
                            + "$(\"[name='mcpservers']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='mcpservers']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='mcpservers']\").val(val);"
                            + "},$(\"[name='title']\").val(),'mcpservers');"
                            + "}",
                    description_ja="Runnerが利用するMCPサーバー名を指定します。",
                    description_en="List or mapping of MCP servers used by the runner."),
                dict(opt="session_store_type", type=Options.T_STR, default='memory', required=False, multi=False, hide=False, choice=['memory', 'sqlite', 'postgresql'],
                    description_ja="セッションの保存方法を指定します。",
                    description_en="Specify how the bot's session is stored.",
                    choice_show=dict(postgresql=["session_store_pghost", "session_store_pgport", "session_store_pguser", "session_store_pgpass", "session_store_pgdbname"]),),
                dict(opt="llm_description", type=Options.T_TEXT, default=description, required=False, multi=False, hide=False, choice=None,
                    description_ja="Runnerの能力に関する説明を指定します。モデルはこれを使用して、制御をエージェントに委譲するかどうかを決定します。一行の説明で十分であり、推奨されます。",
                    description_en="Specify a description of the runner's capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."),
                dict(opt="runner_instruction", type=Options.T_TEXT, default=instruction, required=False, multi=False, hide=False, choice=None,
                    description_ja="Runnerが使用するLLMモデル向けの指示を指定します。これはエージェントの挙動を促すものになります。",
                    description_en="Specify instructions for the LLM model used by the runner. These will guide the agent's behavior."),
                dict(opt="tts_engine", type=Options.T_STR, default="voicevox", required=True, multi=False, hide=False,
                     choice=["", "voicevox"],
                     choice_show=dict(voicevox=["voicevox_ver", "voicevox_os", "voicevox_arc", "voicevox_device", "voicevox_whl"]),
                     description_ja="使用するTTSエンジンを指定します。",
                     description_en="Specify the TTS engine to use."),
                dict(opt="voicevox_model", type=Options.T_STR, default=None, required=False, multi=False, hide=False,
                     choice=sorted([v['select'] for v in cmdbox_tts_start.TtsStart.VOICEVOX_STYLE.values()]),
                     choice_edit=True,
                     description_ja="使用するTTSエンジンのモデルを指定します。",
                     description_en="Specify the model of the TTS engine to use."),
                dict(opt="session_store_pghost", type=Options.T_STR, default='localhost', required=False, multi=False, hide=False, choice=None,
                    description_ja="セッション保存用PostgreSQLホストを指定します。",
                    description_en="Specify the postgresql host for session store."),
                dict(opt="session_store_pgport", type=Options.T_INT, default=5432, required=False, multi=False, hide=False, choice=None,
                    description_ja="セッション保存用PostgreSQLポートを指定します。",
                    description_en="Specify the postgresql port for session store."),
                dict(opt="session_store_pguser", type=Options.T_STR, default='postgres', required=False, multi=False, hide=False, choice=None,
                    description_ja="セッション保存用PostgreSQLのユーザー名を指定します。",
                    description_en="Specify the postgresql user name for session store."),
                dict(opt="session_store_pgpass", type=Options.T_PASSWD, default='postgres', required=False, multi=False, hide=False, choice=None,
                    description_ja="セッション保存用PostgreSQLのパスワードを指定します。",
                    description_en="Specify the postgresql password for session store."),
                dict(opt="session_store_pgdbname", type=Options.T_STR, default='runner', required=False, multi=False, hide=False, choice=None,
                    description_ja="セッション保存用PostgreSQLのデータベース名を指定します。",
                    description_en="Specify the postgresql database name for session store."),
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

    def choice_fn(self, o:Dict[str, Any], webmode:bool, opt:Dict[str, Any]) -> Any:
        """
        オプションのchoiceを動的に生成する関数

        Args:
            o (Dict[str, Any]): オプション情報
            webmode (bool): Webモードかどうか
            opt (Dict[str, Any]): オプション値

        Returns:
            Any: choice情報
        """
        # MCP Servers
        if o.get('opt') == 'mcpservers':
            return self.list_mcvpservers(o.get('data', self.default_data))
        # LLMs
        if o.get('opt') == 'llm':
            return self.list_llms(o.get('data', self.default_data))
        return []
    
    def list_mcvpservers(self, data_dir: str) -> List[str]:
        agent_dir = Path(data_dir) / ".agent"
        if not agent_dir.exists() or not agent_dir.is_dir():
            return []
        paths = agent_dir.glob("mcpsv-*.json")
        ret: List[str] = []
        for p in sorted(paths):
            name = p.name
            if not name.startswith('mcpsv-') or not name.endswith('.json'):
                continue
            svname = name[6:-5]
            ret.append(svname)
        return ret

    def list_llms(self, data_dir: str) -> List[str]:
        agent_dir = Path(data_dir) / ".agent"
        if not agent_dir.exists() or not agent_dir.is_dir():
            return []
        paths = agent_dir.glob("llm-*.json")
        ret: List[str] = []
        for p in sorted(paths):
            name = p.name
            if not name.startswith('llm-') or not name.endswith('.json'):
                continue
            llmname = name[4:-5]
            ret.append(llmname)
        return ret

    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if not hasattr(args, 'runner_name') or args.runner_name is None:
            msg = dict(warn="Please specify --runner_name")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not re.match(r'^[\w\-]+$', args.runner_name):
            msg = dict(warn="Runner name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not hasattr(args, 'llm') or args.llm is None:
            msg = dict(warn="Please specify --llm")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        configure = dict(
            runner_name=args.runner_name,
            llm_description=args.llm_description if hasattr(args, 'llm_description') else None,
            runner_instruction=args.runner_instruction if hasattr(args, 'runner_instruction') else None,
            mcpservers=list(set(args.mcpservers)) if hasattr(args, 'mcpservers') else None,
            llm=args.llm if hasattr(args, 'llm') else None,
            tts_engine=args.tts_engine if hasattr(args, 'tts_engine') else None,
            voicevox_model=args.voicevox_model if hasattr(args, 'voicevox_model') else None,
            session_store_type=args.session_store_type if hasattr(args, 'session_store_type') else None,
            session_store_pghost=args.session_store_pghost if hasattr(args, 'session_store_pghost') else None,
            session_store_pgport=args.session_store_pgport if hasattr(args, 'session_store_pgport') else None,
            session_store_pguser=args.session_store_pguser if hasattr(args, 'session_store_pguser') else None,
            session_store_pgpass=args.session_store_pgpass if hasattr(args, 'session_store_pgpass') else None,
            session_store_pgdbname=args.session_store_pgdbname if hasattr(args, 'session_store_pgdbname') else None,
        )

        payload_b64 = convert.str2b64str(common.to_str(configure))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def is_cluster_redirect(self):
        return False

    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            if logger.level == logging.DEBUG:
                logger.debug(f"{self.get_mode()}_{self.get_cmd()} msg: {msg}")
            configure = json.loads(convert.b64str2str(msg[2]))

            if configure['llm'] not in self.list_llms(data_dir):
                msg = dict(warn=f"Specified LLM configuration '{configure['llm']}' not found.")
                redis_cli.rpush(reskey, msg)
                return self.RESP_WARN
            for m in self.list_mcvpservers(data_dir):
                if m not in configure['mcpservers']:
                    msg = dict(warn=f"Specified MCP server configuration '{m}' not found.")
                    redis_cli.rpush(reskey, msg)
                    return self.RESP_WARN

            name = configure.get('runner_name')
            configure_path = data_dir / ".agent" / f"runner-{name}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            with configure_path.open('w', encoding='utf-8') as f:
                json.dump(configure, f, indent=4)
            msg = dict(success=f"Runner configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN
