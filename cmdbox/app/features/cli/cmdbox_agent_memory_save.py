from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class AgentMemorySave(feature.OneshotResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'memory_save'

    def get_option(self) -> Dict[str, Any]:
        is_japan = common.is_japan()
        description = f"Memory configuration for {self.ver.__appid__}"
        description = description if not is_japan else f"{self.ver.__appid__}のメモリ設定"
        instruction = f"あなたはユーザーの期待値を推測することが出来るメモリ管理のエキスパートです。" + \
                      f"ユーザーとエージェントとの会話の内容を以下の項目にそれぞれ２００文字以内にまとめてください。\n" + \
                      f"1. ユーザーが知りたかった内容の要約。\n" + \
                      f"2. ユーザーが期待している回答の要約。\n" + \
                      f"3. ユーザーの期待にエージェントが答えたかどうか。また答えられた場合の回答の要約。\n" + \
                      f"4. ユーザーが何故そのような期待を持ったのかの要約。\n"
        instruction = instruction if is_japan else \
                      f"You are a memory management expert capable of anticipating user expectations." + \
                      f"Please summarize the conversation between the user and the agent into the following items, each within 200 characters.\n" + \
                      f"1. A summary of the information the user wanted to know.\n" + \
                      f"2. A summary of the response the user expects.\n" + \
                      f"3. Whether the agent met the user's expectations. And if so, a summary of the response.\n" + \
                      f"4. Summary of why the user had such expectations.\n"
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="Memory 設定を保存します。",
            description_en="Saves memory configuration.",
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
                dict(opt="memory_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="Memory設定の名前を指定します。",
                    description_en="Specify the name of the Memory setting."),
                dict(opt="memory_type", type=Options.T_STR, default='memory', required=True, multi=False, hide=False,
                    choice=['', 'memory', 'sqlite', 'postgresql'],
                    choice_show=dict(
                        memory=[],
                        sqlite=[],
                        postgresql=[
                            "memory_store_pghost",
                            "memory_store_pgport",
                            "memory_store_pguser",
                            "memory_store_pgpass",
                            "memory_store_pgdbname"]),
                    description_ja="メモリサービスの種類を指定します。",
                    description_en="Specify the type of memory service."),
                dict(opt="llm", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('agent','llm_list',{},(res)=>{"
                            + "const val = $(\"[name='llm']\").val();"
                            + "$(\"[name='llm']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='llm']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='llm']\").val(val);"
                            + "},$(\"[name='title']\").val(),'llm');"
                            + "}",
                    description_ja="要約処理で使用するLLM設定名を指定します。",
                    description_en="Specify the LLM configuration name to use for summarization processing."),
                dict(opt="embed", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('agent','embed_list',{},(res)=>{"
                            + "const val = $(\"[name='embed']\").val();"
                            + "$(\"[name='embed']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='embed']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='embed']\").val(val);"
                            + "},$(\"[name='title']\").val(),'embedding');"
                            + "}",
                    description_ja="埋込処理で使用するEmbedding設定名を指定します。",
                    description_en="Specify the Embedding setting name to use for embedding processing."),
                dict(opt="memory_store_pghost", type=Options.T_STR, default='localhost', required=False, multi=False, hide=False, choice=None,
                    description_ja="メモリサービス用PostgreSQLホストを指定します。",
                    description_en="Specify the postgresql host for memory service."),
                dict(opt="memory_store_pgport", type=Options.T_INT, default=5432, required=False, multi=False, hide=False, choice=None,
                    description_ja="メモリサービス用PostgreSQLポートを指定します。",
                    description_en="Specify the postgresql port for memory service."),
                dict(opt="memory_store_pguser", type=Options.T_STR, default='postgres', required=False, multi=False, hide=False, choice=None,
                    description_ja="メモリサービス用PostgreSQLのユーザー名を指定します。",
                    description_en="Specify the postgresql user name for memory service."),
                dict(opt="memory_store_pgpass", type=Options.T_PASSWD, default='postgres', required=False, multi=False, hide=False, choice=None,
                    description_ja="メモリサービス用PostgreSQLのパスワードを指定します。",
                    description_en="Specify the postgresql password for memory service."),
                dict(opt="memory_store_pgdbname", type=Options.T_STR, default='memory', required=False, multi=False, hide=False, choice=None,
                    description_ja="メモリサービス用PostgreSQLのデータベース名を指定します。",
                    description_en="Specify the postgresql database name for memory service."),
                dict(opt="memory_description", type=Options.T_TEXT, default=description, required=False, multi=False, hide=False, choice=None,
                    description_ja="メモリの能力に関する説明を指定します。モデルはこれを使用して、制御をエージェントに委譲するかどうかを決定します。一行の説明で十分であり、推奨されます。",
                    description_en="Specify a description of the agent's memory capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."),
                dict(opt="memory_instruction", type=Options.T_TEXT, default=instruction, required=False, multi=False, hide=False, choice=None,
                    description_ja="メモリが使用するLLMモデル向けの指示を指定します。これはメモリの挙動を促すものになります。",
                    description_en="Specify instructions for the LLM model used by the memory. These will guide the memory's behavior."),
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
        if not hasattr(args, 'memory_name') or args.memory_name is None:
            msg = dict(warn="Please specify --memory_name")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not re.match(r'^[\w\-]+$', args.memory_name):
            msg = dict(warn="Memory name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not hasattr(args, 'memory_type') or args.memory_type is None:
            msg = dict(warn="Please specify --memory_type")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        elif args.memory_type == 'postgresql':
            if not hasattr(args, 'memory_store_pghost') or args.memory_store_pghost is None:
                msg = dict(warn="Please specify --memory_store_pghost for postgresql memory_type")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if not hasattr(args, 'memory_store_pguser') or args.memory_store_pguser is None:
                msg = dict(warn="Please specify --memory_store_pguser for postgresql memory_type")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if not hasattr(args, 'memory_store_pgpass') or args.memory_store_pgpass is None:
                msg = dict(warn="Please specify --memory_store_pgpass for postgresql memory_type")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
            if not hasattr(args, 'memory_store_pgdbname') or args.memory_store_pgdbname is None:
                msg = dict(warn="Please specify --memory_store_pgdbname for postgresql memory_type")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

        configure = dict(
            memory_name=args.memory_name,
            memory_type=args.memory_type,
            llm=args.llm if hasattr(args, 'llm') else None,
            embed=args.embed if hasattr(args, 'embed') else None,
            memory_store_pghost=args.memory_store_pghost if hasattr(args, 'memory_store_pghost') else None,
            memory_store_pgport=args.memory_store_pgport if hasattr(args, 'memory_store_pgport') else None,
            memory_store_pguser=args.memory_store_pguser if hasattr(args, 'memory_store_pguser') else None,
            memory_store_pgpass=args.memory_store_pgpass if hasattr(args, 'memory_store_pgpass') else None,
            memory_store_pgdbname=args.memory_store_pgdbname if hasattr(args, 'memory_store_pgdbname') else None,
            memory_description=args.memory_description if hasattr(args, 'memory_description') else None,
            memory_instruction=args.memory_instruction if hasattr(args, 'memory_instruction') else None,
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
            configure = json.loads(convert.b64str2str(msg[2]))

            name = configure.get('memory_name')
            configure_path = data_dir / ".agent" / f"memory-{name}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            with configure_path.open('w', encoding='utf-8') as f:
                json.dump(configure, f, indent=4)
            msg = dict(success=f"Memory configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN
