from cmdbox.app import common, client
from cmdbox.app.commons import convert, redis_client, validator
from cmdbox.app.features.cli import cmdbox_embed_start, cmdbox_llm_chat
from cmdbox.app.features.cli.agent import agant_base
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List
import argparse
import logging
import json
import re


class AgentMemoryStatus(agant_base.AgentBase, validator.Validator):

    def __init__(self, appcls, ver, language:str=None):
        super().__init__(appcls, ver, language=language)
        self.llm_chat = cmdbox_llm_chat.LLMChat(appcls, ver, language=language)

    def get_mode(self) -> str:
        return 'agent'

    def get_cmd(self) -> str:
        return 'memory_status'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=True,
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
                dict(opt="capture_stdout", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。",
                    description_en="Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."),
                dict(opt="capture_maxsize", type=Options.T_INT, default=self.DEFAULT_CAPTURE_MAXSIZE, required=False, multi=False, hide=True, choice=None,
                    description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。",
                    description_en="Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."),
            ]
        )

    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        st, msg, cl = self.valid(logger, args, tm, pf)
        if st != self.RESP_SUCCESS:
            return st, msg, cl

        if not re.match(r'^[\w\-]+$', args.runner_name):
            msg = dict(warn="Runner name can only contain alphanumeric characters, underscores, and hyphens.")
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
            _, _, llm_conf, memory_conf, memory_llm_conf, memory_embed_conf, _ = self.load_conf(runner_name, data_dir, logger)

            # memory_queryが指定されていない場合は新しいもの順で取得する
            memory_conf["memory_fetch_offset"] = memory_fetch_offset
            memory_conf["memory_fetch_count"] = memory_fetch_count
            memory_conf["memory_fetch_summary"] = memory_fetch_summary
            from google.adk.memory import BaseMemoryService
            memory_service:BaseMemoryService = self.create_memory_service(
                data_dir, logger, memory_conf, memory_llm_conf, memory_embed_conf, sessions)
            responce = await memory_service.search_memory(app_name=runner_name, user_id=user_name, query=memory_query)
            responce.memories.sort(key=lambda m: m.custom_metadata.get('distance', 0), reverse=True)
            # Build status information
            res = responce.model_dump()
            res = [dict(event_id=content.get('id', ''),
                        distance=content.get('custom_metadata', {}).get('distance', 0),
                        role=content.get('content', {}).get('role', ''),
                        my_cnt=1,
                        ts_start=content.get('timestamp', ''),
                        ts_end=content.get('timestamp', ''),
                        all_cnt=content.get('custom_metadata', {}).get('all_cnt', 1),
                        text="\n\n".join([part.get('text', '') for part in content.get('content', {}).get('parts', [])])
                        ) for content in res.get('memories', [])]
            if memory_fetch_summary and len(res) > 0:
                # 取得したメモリーを要約する
                all_text = memory_conf.get('memory_instruction', '') + "\n\n"
                all_text+= "---\n".join([f"{r['text']}" for r in res])
                st, all_text = self.chat(data_dir, logger, llm_conf.get("llmname"), msg_role="system", msg_text=all_text)
                if st != self.RESP_SUCCESS:
                    raise Exception(f"Failed to summarize memory contents: {all_text}")
                all_text = "\n\n".join([r['content'] for r in all_text])
                res = [dict(event_id=common.random_string(),
                            score=1,
                            role='system',
                            my_cnt=len(res),
                            ts_start=res[-1]['ts_start'],
                            ts_end=res[0]['ts_end'],
                            all_cnt=res[0]['all_cnt'],
                            text=all_text)]

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

    def create_memory_service(self, data_dir:Path, logger:logging.Logger,
                              memory_conf:Dict[str, Any], memory_llm_conf:Dict[str, Any], memory_embed_conf:Dict[str, Any],
                              sessions:Dict[str, Dict[str, Any]]) -> Any:
        """
        メモリーサービスを作成します

        Args:
            data_dir (Path): データディレクトリパス
            logger (logging.Logger): ロガー
            memory_conf (Dict[str, Any]): メモリー設定
            memory_llm_conf (Dict[str, Any]): メモリー用LLM設定
            memory_embed_conf (Dict[str, Any]): メモリー用埋め込みモデル設定
            sessions (Dict[str, Dict[str, Any]]): セッション情報辞書

        Returns:
            BaseMemoryService: メモリーサービス
        """
        from google.adk.memory import InMemoryMemoryService
        from cmdbox.app.features.cli.agent.sqlite_memory_service import SqliteMemoryService
        from cmdbox.app.features.cli.agent.postgresql_memory_service import PostgresqlMemoryService
        
        memory_type = memory_conf.get('memory_type', 'memory')
        device = memory_embed_conf.get('embed_device', None)
        embed_name = memory_embed_conf.get('embed_name', None)
        embed_model = memory_embed_conf.get('embed_model', None)

        if memory_type == 'memory':
            logger.info("Using InMemoryMemoryService")
            return InMemoryMemoryService()
        elif memory_type == 'sqlite':
            logger.info("Using SqliteMemoryService")
            memory_dbpath = str(data_dir / '.agent' / 'memory.db').replace('\\', '/')
            memory_dburl = f"sqlite+aiosqlite:///{memory_dbpath}"
            ebcls = cmdbox_embed_start.EmbedStart
            model = ebcls._start_embed_model(data_dir, sessions,
                                             device, embed_name, embed_model, logger)
            return SqliteMemoryService(db_url=memory_dburl, embed_name=embed_name, embed_model=model,
                                       memory_fetch_offset=memory_conf.get('memory_fetch_offset', 0),
                                       memory_fetch_count=memory_conf.get('memory_fetch_count', 10),
                                       memory_fetch_summary=memory_conf.get('memory_fetch_summary', False),
                                       logger=logger)
        elif memory_type == 'postgresql':
            logger.info("Using PostgresqlMemoryService")
            memory_dburl = memory_conf.get('memory_dburl', None)
            if memory_dburl is None:
                # Build PostgreSQL URL from individual configuration parameters
                pg_host = memory_conf.get('memory_store_pghost')
                pg_port = memory_conf.get('memory_store_pgport')
                pg_user = memory_conf.get('memory_store_pguser')
                pg_pass = memory_conf.get('memory_store_pgpass')
                pg_dbname = memory_conf.get('memory_store_pgdbname')

                if pg_host and pg_port and pg_user and pg_pass and pg_dbname:
                    memory_dburl = f"postgresql://{pg_user}:{pg_pass}@{pg_host}:{pg_port}/{pg_dbname}"
                else:
                    raise ValueError("memory_dburl or PostgreSQL connection parameters (memory_store_pghost, memory_store_pgport, memory_store_pguser, memory_store_pgpass, memory_store_pgdbname) are required for postgresql memory_type")
            ebcls = cmdbox_embed_start.EmbedStart
            model = ebcls._start_embed_model(data_dir, sessions,
                                             device, embed_name, embed_model, logger)
            return PostgresqlMemoryService(db_url=memory_dburl, embed_name=embed_name, embed_model=model,
                                           memory_fetch_offset=memory_conf.get('memory_fetch_offset', 0),
                                           memory_fetch_count=memory_conf.get('memory_fetch_count', 10),
                                           memory_fetch_summary=memory_conf.get('memory_fetch_summary', False),
                                           logger=logger)
        else:
            logger.info(f"Using InMemoryMemoryService (unknown memory_type: {memory_type})")
            return InMemoryMemoryService()

    async def summary(self, data_dir:Path, logger:logging.Logger, llmname:str, short_mem_msg:str, msg_text_system:str):
        st, res = self.llm_chat.chat(data_dir, logger, llmname,
                                     msg_role="system", msg_text=short_mem_msg, msg_text_system=msg_text_system)
        if st != self.RESP_SUCCESS:
            raise Exception(f"Failed to summarize memory contents: {res}")
        return res

    async def add_memory(self, memory_service, session, sammary_msg):
        from google.adk.events import Event
        from google.genai import types
        session.events.append(Event(
            id=common.random_string(32),
            author='system',
            content=types.Content(role='system', parts=[types.Part(text=sammary_msg)]),
        ))
        # メモリーにセッションを保存する
        await memory_service.add_session_to_memory(session)
