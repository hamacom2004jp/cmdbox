from cmdbox.app import common, feature
from cmdbox.app.features.cli import cmdbox_web_start
from cmdbox.app.options import Options
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging


class McpProxy(feature.UnsupportEdgeFeature):
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
        return 'proxy'

    def get_option(self):
        """
        この機能のオプションを返します

        Returns:
            Dict[str, Any]: オプション
        """
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=False,
            description_ja="標準入力を受け付け、リモートMCPサーバーにリクエストを行うProxyサーバーを起動します。",
            description_en="Starts a Proxy server that accepts standard input and makes requests to a remote MCP server.",
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
            ])

    def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]=[]) -> Tuple[int, Dict[str, Any], Any]:
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
        if not hasattr(args, 'mcpserver_name'):
            args.mcpserver_name = 'mcpserver'
        if not hasattr(args, 'mcpserver_url'):
            args.mcpserver_url = 'http://localhost:8081/mcpsv/mcp'
        if not hasattr(args, 'mcpserver_transport'):
            args.mcpserver_transport = 'streamable-http'
        if not hasattr(args, 'mcpserver_apikey'):
            args.mcpserver_apikey = None

        from fastmcp import FastMCP
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
            proxy = FastMCP.as_proxy(config, name="Config-Based Proxy")
            proxy.run()
        except Exception as e:
            logger.setLevel(logging.ERROR)
            for h in logger.handlers:
                h.setLevel(logging.ERROR)
            logger.error(f"Failed to start MCP proxy: {e}", exc_info=True)
            return self.RESP_ERROR, dict(warn=f"Failed to start MCP proxy: {e}"), None
        return self.RESP_SCCESS, dict(info="MCP proxy successfully."), None
