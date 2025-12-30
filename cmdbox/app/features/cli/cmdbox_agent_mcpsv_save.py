from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client
from cmdbox.app.options import Options
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import re


class AgentMcpSave(feature.OneshotResultEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'mcpsv_save'

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="MCP サーバ設定を保存します。",
            description_en="Saves MCP server configuration.",
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
                dict(opt="mcpserver_name", type=Options.T_STR, default='mcpserver', required=True, multi=False, hide=False, choice=None,
                    description_ja="リモートMCPサーバーの名前を指定します。省略した場合は`mcpserver`となります。",
                    description_en="Specify the name of the MCP server. If omitted, it will be `mcpserver`.",),
                dict(opt="mcpserver_url", type=Options.T_STR, default='http://localhost:8091/mcp', required=True, multi=False, hide=False, choice=None,
                    description_ja="リモートMCPサーバーのURLを指定します。省略した場合は`http://localhost:8091/mcp`となります。",
                    description_en="Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8091/mcp`.",),
                dict(opt="mcpserver_delegated_auth", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                    description_ja="リモートMCPサーバーの認証を現在のログインユーザーのAPI Keyを使用して行います。",
                    description_en="Authenticate with the remote MCP server using the API key of the currently logged-in user.",),
                dict(opt="mcpserver_apikey", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="A2A Server起動時のリモートMCPサーバーのAPI Keyを指定します。 `mcpserver_delegated_auth` が無効な場合は、MCP実行時に使用も使用されます。",
                    description_en="Specifies the API Key for the remote MCP server when starting the A2A Server. If `mcpserver_delegated_auth` is disabled, it is also used when running MCP.",),
                dict(opt="mcpserver_transport", type=Options.T_STR, default='streamable-http', required=True, multi=False, hide=False, choice=['', 'streamable-http', 'sse'],
                    description_ja="リモートMCPサーバーのトランスポートを指定します。省略した場合は`streamable-http`となります。",
                    description_en="Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`.",),
                dict(opt="mcp_tools", type=Options.T_MLIST, default=None, required=False, multi=False, hide=False, choice=[],
                    callcmd="async () => {const user = await cmdbox.user_info();"
                            + "let apikey = $(\"[name='mcpserver_apikey']\").val();"
                            + "if (!apikey && user && user['apikeys']) {"
                            + "  const keys = Object.keys(user['apikeys']);"
                            + "  if (keys.length > 0) apikey = user['apikeys'][keys[0]][0];"
                            + "}"
                            + "await cmdbox.callcmd('agent','mcp_client',{"
                            + "'mcpserver_url':$(\"[name='mcpserver_url']\").val(),"
                            + "'mcpserver_apikey':apikey,"
                            + "'mcpserver_transport':$(\"[name='mcpserver_transport']\").val(),"
                            + "'operation':'list_tools',"
                            + "},(res)=>{"
                            + "const val = $(\"[name='mcp_tools']\").val();"
                            + "$(\"[name='mcp_tools']\").empty();"
                            + "res.map(elm=>{$(\"[name='mcp_tools']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='mcp_tools']\").val(val);"
                            + "},$(\"[name='title']\").val(),'mcp_tools');"
                            + "}",
                    description_ja="リモートサーバーが提供しているツールを指定します。",
                    description_en="Specify the tools provided by the remote server.",),
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
        if not getattr(args, 'mcpserver_name', None) or args.mcpserver_name is None:
            msg = dict(warn="Please specify --mcpserver_name")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not getattr(args, 'mcpserver_url', None) or args.mcpserver_url is None:
            msg = dict(warn="Please specify --mcpserver_url")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None
        if not re.match(r'^[\w\-]+$', args.mcpserver_name):
            msg = dict(warn="MCP server name can only contain alphanumeric characters, underscores, and hyphens.")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        configure = dict(
            mcpserver_name=args.mcpserver_name,
            mcpserver_url=args.mcpserver_url,
            mcpserver_apikey=args.mcpserver_apikey,
            mcpserver_delegated_auth=args.mcpserver_delegated_auth,
            mcpserver_transport=args.mcpserver_transport,
            mcpserver_mcp_tools=args.mcp_tools,
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

            name = configure.get('mcpserver_name')
            configure_path = data_dir / ".agent" / f"mcpsv-{name}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            with configure_path.open('w', encoding='utf-8') as f:
                json.dump(configure, f, indent=4)
            msg = dict(success=f"MCP server configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN
