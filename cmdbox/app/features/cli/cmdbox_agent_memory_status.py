from cmdbox.app import common, client, feature, options
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.features.cli import cmdbox_agent_chat
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List
import argparse
import logging
import json
import re


class AgentMemoryStatus(cmdbox_agent_chat.AgentChat):

    def get_mode(self) -> str:
        return 'agent'

    def get_cmd(self) -> str:
        return 'memory_status'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE,
            nouse_webmode=False,
            use_agent=True,
            description_ja="Agentのメモリステータスを取得します。",
            description_en="Get the memory status for the agent.",
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
                dict(opt="memory_query", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="メモリ内容を検索するクエリを指定します。意味検索を行います。",
                     description_en="Specify a query to search memory contents. Perform semantic search."),
                dict(opt="memory_fetch_offset", type=Options.T_INT, default=0, required=False, multi=False, hide=False, choice=None,
                     description_ja="メモリ内容を取得する時の開始位置を指定します。",
                     description_en="Specify the starting position when retrieving memory contents."),
                dict(opt="memory_fetch_count", type=Options.T_INT, default=10, required=False, multi=False, hide=False, choice=None,
                     description_ja="メモリ内容を取得する件数を指定します。",
                     description_en="Specify the number of memory contents to retrieve."),
                dict(opt="memory_fetch_summary", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[False, True],
                     description_ja="取得したメモリ内容を要約するかどうかを指定します。",
                     description_en="Specify whether to summarize the retrieved memory contents."),
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
        if not getattr(args, 'user_name', None):
            msg = dict(warn="Please specify --user_name")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        payload = dict(runner_name=args.runner_name, user_name=args.user_name, memory_query=args.memory_query,
                       memory_fetch_offset=args.memory_fetch_offset, memory_fetch_count=args.memory_fetch_count,
                       memory_fetch_summary=args.memory_fetch_summary)
        payload_b64 = convert.str2b64str(common.to_str(payload))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, False, tm, None, False, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def is_cluster_redirect(self):
        return False

    async def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
                    sessions:Dict[str, Dict[str, Any]]):
        reskey = msg[1]
        try:
            if 'agents' not in sessions:
                sessions['agents'] = {}

            payload = json.loads(convert.b64str2str(msg[2]))
            runner_name = payload.get('runner_name')
            user_name = payload.get('user_name')
            memory_query = payload.get('memory_query')
            memory_fetch_offset = payload.get('memory_fetch_offset', 0)
            memory_fetch_count = payload.get('memory_fetch_count', 10)
            memory_fetch_summary = payload.get('memory_fetch_summary', False)
            runner_conf, agent_conf, llm_conf, memory_conf, memory_llm_conf, memory_embed_conf, mcpsv_confs = self.load_conf(runner_name, data_dir, logger)
            memory_conf["memory_fetch_offset"] = memory_fetch_offset
            memory_conf["memory_fetch_count"] = memory_fetch_count
            memory_conf["memory_fetch_summary"] = memory_fetch_summary

            from google.adk.memory import BaseMemoryService
            memory_service:BaseMemoryService = self.create_memory_service(
                data_dir, logger, memory_conf, memory_llm_conf, memory_embed_conf, sessions)
            memory_agent_name = f"{memory_conf.get('memory_name', 'memory_agent')}_runner"
            responce = await memory_service.search_memory(app_name=memory_agent_name, user_id=user_name, query=memory_query)
            responce.memories.sort(key=lambda m: m.custom_metadata.get('score', 0), reverse=True)
            # Build status information
            res = responce.model_dump()
            res = [dict(event_id=content.get('id', ''),
                        score=content.get('custom_metadata', {}).get('score', 0),
                        role=content.get('content', {}).get('role', ''),
                        text="\n\n".join([part.get('text', '') for part in content.get('content', {}).get('parts', [])])
                        ) for content in res.get('memories', [])]

            out = dict(success=res, end=True)
            redis_cli.rpush(reskey, out)
            return self.RESP_SUCCESS
        except FileNotFoundError as e:
            logger.warning(f"Memory configuration file not found: {e}", exc_info=True)
            out = dict(warn=f"Memory configuration file not found: {e}", end=True)
            redis_cli.rpush(reskey, out)
            return self.RESP_WARN
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse memory configuration: {e}", exc_info=True)
            out = dict(warn=f"Failed to parse memory configuration: {e}", end=True)
            redis_cli.rpush(reskey, out)
            return self.RESP_WARN
        except Exception as e:
            # その他のエラーが発生した時はログに出力してエラーを返す
            logger.warning(f"get_memory_status warning: {e}", exc_info=True)
            out = dict(warn=str(e), end=True)
            redis_cli.rpush(reskey, out)
            return self.RESP_WARN
