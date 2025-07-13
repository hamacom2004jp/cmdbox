from cmdbox.app import common, feature
from cmdbox.app.features.cli import cmdbox_web_start
from cmdbox.app.options import Options
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class McpClient(feature.UnsupportEdgeFeature):
    def get_mode(self) -> Union[str, List[str]]:
        """
        この機能のモードを返します

        Returns:
            Union[str, List[str]]: モード
        """
        return 'mcp'

    def get_cmd(self) -> str:
        """
        この機能のコマンドを返します

        Returns:
            str: コマンド
        """
        return 'client'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=True, use_agent=False,
            description_ja="リモートMCPサーバーにリクエストを行うMCPクライアントを起動します。",
            description_en="Starts an MCP client that makes requests to a remote MCP server.",
            choice=[
                dict(opt="mcpserver_name", type=Options.T_STR, default='mcpserver', required=True, multi=False, hide=False, choice=None,
                     description_ja="リモートMCPサーバーの名前を指定します。省略した場合は`mcpserver`となります。",
                     description_en="Specify the name of the MCP server. If omitted, it will be `mcpserver`.",),
                dict(opt="mcpserver_url", type=Options.T_STR, default='http://localhost:8081/mcpsv/mcp', required=True, multi=False, hide=False, choice=None,
                     description_ja="リモートMCPサーバーのURLを指定します。省略した場合は`http://localhost:8081/mcpsv/mcp`となります。",
                     description_en="Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8081/mcpsv/mcp`.",),
                dict(opt="mcpserver_apikey", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="リモートMCPサーバーのAPI Keyを指定します。",
                     description_en="Specify the API Key of the remote MCP server.",),
                dict(opt="mcpserver_transport", type=Options.T_STR, default='streamable-http', required=True, multi=False, hide=False, choice=['', 'streamable-http', 'sse', 'http'],
                     description_ja="リモートMCPサーバーのトランスポートを指定します。省略した場合は`streamable-http`となります。",
                     description_en="Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`.",),
                dict(opt="operation", type=Options.T_STR, default='list_tools', required=True, multi=False, hide=False,
                     choice=['list_tools', 'call_tool', 'list_resources', 'read_resource', 'list_prompts', 'get_prompt'],
                     choice_show=dict(call_tool=['tool_name', 'tool_args', 'mcp_timeout',],
                                      read_resource=['resource_url',],
                                      get_prompt=['prompt_name', 'prompt_args']),
                     description_ja="リモートMCPサーバーに要求する操作を指定します。省略した場合は`list_tools`となります。",
                     description_en="Specifies the operations to request from the remote MCP server. If omitted, `list_tools` is used.",),
                dict(opt="tool_name", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="リモートMCPサーバーで実行するツールの名前を指定します。",
                     description_en="Specify the name of the tool to run on the remote MCP server."),
                dict(opt="tool_args", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="リモートMCPサーバーで実行するツールの引数を指定します。",
                     description_en="Specify arguments for the tool to run on the remote MCP server."),
                dict(opt="mcp_timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=False, choice=None,
                     description_ja="リモートMCPサーバーの応答が返ってくるまでの最大待ち時間を指定します。",
                     description_en="Specifies the maximum time to wait for a response from the remote MCP server."),
                dict(opt="resource_url", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="リモートMCPサーバーから取得するリソースのURLを指定します。",
                     description_en="Specify the URL of the resource to retrieve from the remote MCP server."),
                dict(opt="prompt_name", type=Options.T_STR, default=None, required=False, multi=False, hide=False, choice=None,
                     description_ja="リモートMCPサーバーから取得するプロンプトの名前を指定します。",
                     description_en="Specifies the name of the prompt to be retrieved from the remote MCP server."),
                dict(opt="prompt_args", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                     description_ja="リモートMCPサーバーから取得するプロンプトの引数を指定します。",
                     description_en="Specifies prompt arguments to be retrieved from the remote MCP server."),
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
            ])

    async def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
        """
        この機能の実行を行います

        Args:
            logger (logging.Logger): ロガー
            args (argparse.Namespace): 引数
            tm (float): 実行開始時間
            pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報

        Returns:
            Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
        """
        logger.info("apprun function has started.")
        if not hasattr(args, 'mcpserver_name'):
            args.mcpserver_name = 'mcpserver'
        if not hasattr(args, 'mcpserver_url'):
            args.mcpserver_url = 'http://localhost:8081/mcpsv/mcp'
        if not hasattr(args, 'mcpserver_transport'):
            args.mcpserver_transport = 'streamable-http'
        if not hasattr(args, 'mcpserver_apikey'):
            args.mcpserver_apikey = None

        from fastmcp import Client
        config = dict(
            mcpServers=dict(
                default=dict(
                    url=args.mcpserver_url,
                    transport=args.mcpserver_transport,
                    auth=args.mcpserver_apikey
                )
            )
        )
        try:
            common.reset_logger('FastMCP.fastmcp.server.server')
            client = Client(config)
            if logger.level == logging.DEBUG:
                logger.debug(f"Starting MCP client: {config}")
            async with client:
                if args.operation == 'list_tools':
                    result = await client.list_tools()
                    ret = dict(success=[r.__dict__ for r in result])
                elif args.operation == 'call_tool':
                    if not args.tool_name:
                        raise ValueError("Tool name must be specified for 'call_tool' operation.")
                    if not args.tool_args:
                        args.tool_args = dict()
                    if not hasattr(args, 'mcp_timeout'):
                        args.mcp_timeout = 60
                    result = await client.call_tool(args.tool_name, arguments=args.tool_args, timeout=args.mcp_timeout)
                    ret = dict(success=result.__dict__)
                elif args.operation == 'list_resources':
                    result = await client.list_resources()
                    ret = dict(success=[r.__dict__ for r in result])
                elif args.operation == 'read_resource':
                    if not args.resource_url:
                        raise ValueError("Resource URL must be specified for 'read_resource' operation.")
                    result = await client.read_resource(args.resource_url)
                    ret = dict(success=result.__dict__)
                elif args.operation == 'list_prompts':
                    result = await client.list_prompts()
                    ret = dict(success=[r.__dict__ for r in result])
                elif args.operation == 'get_prompt':
                    if not args.prompt_name:
                        raise ValueError("Prompt name must be specified for 'get_prompt' operation.")
                    if not args.prompt_args:
                        args.prompt_args = dict()
                    result = await client.get_prompt(args.prompt_name, arguments=args.prompt_args)
                    ret = dict(success=result.__dict__)
                else:
                    raise ValueError(f"Unknown operation: {args.operation}")
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_SCCESS, ret, None
        except Exception as e:
            logger.setLevel(logging.ERROR)
            for h in logger.handlers:
                h.setLevel(logging.ERROR)
            logger.error(f"Failed to start MCP proxy: {e}", exc_info=True)
            msg = dict(warn=f"Failed to start MCP proxy: {e}")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_ERROR, msg, None
