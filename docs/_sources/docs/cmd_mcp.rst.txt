.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( mcp mode )
****************************************************

- List of mcp mode commands.

MCP stdio to transport proxy start : `cmdbox -m mcp -c proxy <Option>`
==============================================================================

- This command invokes a proxy to forward MCP standard input/output via TCP/IP.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--mcpserver_name <name>","","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <url>","","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8081/mcpsv/mcp`."
    "--mcpserver_transport <transport>","","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."
