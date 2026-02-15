from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class RagSave(feature.OneshotResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'rag'

    def get_cmd(self) -> str:
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'save'

    def get_option(self) -> Dict[str, Any]:
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="RAG（検索拡張生成）の設定を保存します。",
            description_en="Saves the settings for RAG (Retrieval-Augmented Generation).",
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
                dict(opt="timeout", type=Options.T_INT, default=120, required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="rag_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="RAG設定の名前を指定します。",
                     description_en="Specify the name of the RAG configuration."),
                dict(opt="rag_type", type=Options.T_STR, default='vector', required=True, multi=False, hide=False,
                     choice=['', 'vector_pg', 'vector_sqlite', 'graph_n4j', 'graph_pg'],
                     choice_show=dict(
                            vector_pg=[
                                "vector_store_pghost",
                                "vector_store_pgport",
                                "vector_store_pguser",
                                "vector_store_pgpass",
                                "vector_store_pgdbname"
                            ],
                            vector_sqlite=[
                            ],
                            graph_n4j=[
                            ],
                            graph_pg=[
                                "graph_store_pghost",
                                "graph_store_pgport",
                                "graph_store_pguser",
                                "graph_store_pgpass",
                                "graph_store_pgdbname"
                            ],
                     ),
                     description_ja="RAGの種類を指定します。",
                     description_en="Specify the type of RAG."),
                dict(opt="extract", type=Options.T_STR, default=None, required=True, multi=True, hide=False, choice=[],
                     callcmd="async () => {await cmdbox.callcmd('extract','list',{},(res)=>{"
                             + "const val = $(\"[name='extract']\").val();"
                             + "$(\"[name='extract']\").empty().append('<option></option>');"
                             + "res['data'].map(elm=>{$(\"[name='extract']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                             + "$(\"[name='extract']\").val(val);"
                             + "},$(\"[name='title']\").val(),'extract');"
                             + "}",
                     description_ja="RAGで使用するExtract処理の登録名を指定します。候補がない場合はextractモードのコマンドの登録が必要です。",
                     description_en="Specify the registered name for the Extract process used in RAG. If no candidates exist, you must register a command in extract mode."),
                dict(opt="embed", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=[],
                     callcmd="async () => {await cmdbox.callcmd('embed','list',{},(res)=>{"
                             + "const val = $(\"[name='embed']\").val();"
                             + "$(\"[name='embed']\").empty().append('<option></option>');"
                             + "res['data'].map(elm=>{$(\"[name='embed']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                             + "$(\"[name='embed']\").val(val);"
                             + "},$(\"[name='title']\").val(),'embed');"
                             + "}",
                     description_ja="rag_typeがvectorの場合、エンベッドモデルの登録名を指定します。",
                     description_en="If rag_type is vector, specify the registration name of the embed model."),
                dict(opt="vector_store_pghost", type=Options.T_STR, default='localhost', required=False, multi=False, hide=False, choice=None,
                     description_ja="VecRAG保存先用PostgreSQLホストを指定します。",
                     description_en="Specify the postgresql host for VecRAG storage."),
                dict(opt="vector_store_pgport", type=Options.T_INT, default=5432, required=False, multi=False, hide=False, choice=None,
                     description_ja="VecRAG保存先用PostgreSQLポートを指定します。",
                     description_en="Specify the postgresql port for VecRAG storage."),
                dict(opt="vector_store_pguser", type=Options.T_STR, default='postgres', required=False, multi=False, hide=False, choice=None,
                     description_ja="VecRAG保存先用PostgreSQLユーザー名を指定します。",
                     description_en="Specify the postgresql user for VecRAG storage."),
                dict(opt="vector_store_pgpass", type=Options.T_PASSWD, default='', required=False, multi=False, hide=False, choice=None,
                     description_ja="VecRAG保存先用PostgreSQLパスワードを指定します。",
                     description_en="Specify the postgresql password for VecRAG storage."),
                dict(opt="vector_store_pgdbname", type=Options.T_STR, default='rag_db', required=False, multi=False, hide=False, choice=None,
                     description_ja="VecRAG保存先用PostgreSQLデータベース名を指定します。",
                     description_en="Specify the postgresql database name for VecRAG storage."),
                dict(opt="graph_store_pghost", type=Options.T_STR, default='localhost', required=False, multi=False, hide=False, choice=None,
                     description_ja="GraphRAG保存先用PostgreSQLホストを指定します。",
                     description_en="Specify the postgresql host for GraphRAG storage."),
                dict(opt="graph_store_pgport", type=Options.T_INT, default=5432, required=False, multi=False, hide=False, choice=None,
                     description_ja="GraphRAG保存先用PostgreSQLポートを指定します。",
                     description_en="Specify the postgresql port for GraphRAG storage."),
                dict(opt="graph_store_pguser", type=Options.T_STR, default='postgres', required=False, multi=False, hide=False, choice=None,
                     description_ja="GraphRAG保存先用PostgreSQLユーザー名を指定します。",
                     description_en="Specify the postgresql user for GraphRAG storage."),
                dict(opt="graph_store_pgpass", type=Options.T_PASSWD, default='', required=False, multi=False, hide=False, choice=None,
                     description_ja="GraphRAG保存先用PostgreSQLパスワードを指定します。",
                     description_en="Specify the postgresql password for GraphRAG storage."),
                dict(opt="graph_store_pgdbname", type=Options.T_STR, default='rag_db', required=False, multi=False, hide=False, choice=None,
                     description_ja="GraphRAG保存先用PostgreSQLデータベース名を指定します.",
                     description_en="Specify the postgresql database name for GraphRAG storage."),
                dict(opt="output_json", short="o", type=Options.T_FILE, default=None, required=False, multi=False, hide=True, choice=None, fileio="out",
                    description_ja="処理結果jsonの保存先ファイルを指定。",
                    description_en="Specify the destination file for saving the processing result json."),
                dict(opt="output_json_append", short="a", type=Options.T_BOOL, default=False, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="処理結果jsonファイルを追記保存します。",
                    description_en="Save the processing result json file by appending."),
                dict(opt="stdout_log", type=Options.T_BOOL, default=True, required=False, multi=False, hide=True, choice=[True, False],
                    description_ja="GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。",
                    description_en="Available only in GUI mode. Outputs standard output during command execution to Console log."),
            ]
        )

    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if not hasattr(args, 'rag_name') or args.rag_name is None:
            msg = dict(warn="Please specify --rag_name")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not re.match(r'^[\w\-]+$', args.rag_name):
            msg = dict(warn="RAG name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not hasattr(args, 'rag_type') or args.rag_type is None:
            msg = dict(warn="Please specify --rag_type")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        # Build payload
        payload = dict(
            rag_name=args.rag_name,
            rag_type=args.rag_type,
            extract=list(set(args.extract)) if hasattr(args, 'extract') and args.extract is not None else None,
            embed=args.embed if hasattr(args, 'embed') else None,
            vector_store_pghost=args.vector_store_pghost if hasattr(args, 'vector_store_pghost') else None,
            vector_store_pgport=args.vector_store_pgport if hasattr(args, 'vector_store_pgport') else None,
            vector_store_pguser=args.vector_store_pguser if hasattr(args, 'vector_store_pguser') else None,
            vector_store_pgpass=args.vector_store_pgpass if hasattr(args, 'vector_store_pgpass') else None,
            vector_store_pgdbname=args.vector_store_pgdbname if hasattr(args, 'vector_store_pgdbname') else None,
            graph_store_pghost=args.graph_store_pghost if hasattr(args, 'graph_store_pghost') else None,
            graph_store_pgport=args.graph_store_pgport if hasattr(args, 'graph_store_pgport') else None,
            graph_store_pguser=args.graph_store_pguser if hasattr(args, 'graph_store_pguser') else None,
            graph_store_pgpass=args.graph_store_pgpass if hasattr(args, 'graph_store_pgpass') else None,
            graph_store_pgdbname=args.graph_store_pgdbname if hasattr(args, 'graph_store_pgdbname') else None
        )

        payload_b64 = convert.str2b64str(common.to_str(payload))

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

            configure_path = data_dir / ".agent" / f"rag-{configure['rag_name']}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            with configure_path.open('w', encoding='utf-8') as f:
                json.dump(configure, f, indent=4)
            msg = dict(success=f"RAG configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN
