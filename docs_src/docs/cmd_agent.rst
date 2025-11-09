.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( agent mode )
****************************************************

- List of agent mode commands.


Deletes LLM configuration. : `cmdbox -m agent -c llm_del <Option>`
==============================================================================

- Deletes LLM configuration. This command sends a delete request to the agent via Redis.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--llmname <name>","Yes","Specify the name of the LLM configuration to delete."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


Lists saved LLM configurations. : `cmdbox -m agent -c llm_list <Option>`
==============================================================================

- Lists saved LLM configurations. Sends a list request to the agent and receives matching LLM names.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--kwd <keyword>","No","Specify a partial match keyword to filter saved LLMs."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


Loads LLM configuration. : `cmdbox -m agent -c llm_load <Option>`
==============================================================================

- Loads LLM configuration from the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--llmname <name>","Yes","Specify the name of the LLM configuration to load."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


Saves LLM configuration. : `cmdbox -m agent -c llm_save <Option>`
===============================================================================

- Saves LLM configuration via the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--llmname <name>","Yes","Specify the name of the LLM configuration to save."
    "--llmprov <provider>","Yes","Specify llm provider."
    "--llmprojectid <id>","No","Project ID for provider connection."
    "--llmsvaccountfile <file>","No","Service account file for provider connection."
    "--llmlocation <location>","No","Provider location."
    "--llmapikey <key>","No","API key for provider connection."
    "--llmendpoint <endpoint>","No","Provider endpoint."
    "--llmmodel <model>","No","LLM model name."
    "--llmseed <int>","No","Seed for model sampling."
    "--llmtemperature <float>","No","Temperature for model sampling."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


Agent client start : `cmdbox -m agent -c client <Option>`
==============================================================================
- Starts an MCP client that makes requests to a remote MCP server.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--mcpserver_name <name>","Yes","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <url>","Yes","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8081/mcpsv/mcp`."
    "--mcpserver_apikey <apikey>","No","Specify the API Key of the remote MCP server."
    "--mcpserver_transport <transport>","Yes","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."
    "--operation <op>","Yes","Specifies the operations to request from the remote MCP server. If omitted, `list_tools` is used."
    "--tool_name <name>","No","Specify the name of the tool to run on the remote MCP server."
    "--tool_args <dict>","No","Specify arguments for the tool to run on the remote MCP server."
    "--mcp_timeout <sec>","No","Specifies the maximum time to wait for a response from the remote MCP server."
    "--resource_url <url>","No","Specify the URL of the resource to retrieve from the remote MCP server."
    "--prompt_name <name>","No","Specifies the name of the prompt to be retrieved from the remote MCP server."
    "--prompt_args <dict>","No","Specifies prompt arguments to be retrieved from the remote MCP server."


Agent stdio to transport proxy start : `cmdbox -m agent -c proxy <Option>`
==============================================================================

- This command invokes a proxy to forward MCP standard input/output via TCP/IP.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--mcpserver_name <name>","","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <url>","","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8081/mcpsv/mcp`."
    "--mcpserver_apikey <apikey>","","Specify the API Key of the remote MCP server."
    "--mcpserver_transport <transport>","","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."

Delete MCP server configuration. : `cmdbox -m agent -c mcpsv_del <Option>`
===============================================================================

- Deletes MCP server configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--mcpserver_name <name>","Yes","Specify the name of the MCP server configuration to delete."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


Lists MCP server configurations. : `cmdbox -m agent -c mcpsv_list <Option>`
==============================================================================

- Lists saved MCP server configurations.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--kwd <keyword>","No","Specify the name you want to search for. Searches for partial matches."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


Loads MCP server configuration. : `cmdbox -m agent -c mcpsv_load <Option>`
==============================================================================

- Loads MCP server configuration from the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--mcpserver_name <name>","Yes","Specify the name of the MCP server configuration to load."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


Saves MCP server configuration. : `cmdbox -m agent -c mcpsv_save <Option>`
==============================================================================

- Saves MCP server configuration via the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--mcpserver_name <name>","Yes","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <url>","Yes","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8081/mcpsv/mcp`."
    "--mcpserver_apikey <apikey>","No","Specify the API Key of the remote MCP server."
    "--mcpserver_transport <transport>","Yes","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


Delete runner configuration. : `cmdbox -m agent -c runner_del <Option>`
==============================================================================

- Deletes runner configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--runner_name <name>","Yes","Specify the name of the runner configuration to delete."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


List runner configuration. : `cmdbox -m agent -c runner_list <Option>`
==============================================================================

- Lists saved runner configurations.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--kwd <keyword>","No","Partial match filter for runner names."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


Load runner configuration. : `cmdbox -m agent -c runner_load <Option>`
==============================================================================

- Loads runner configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--runner_name <name>","Yes","Specify the name of the runner configuration to load."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."


Save runner configuration. : `cmdbox -m agent -c runner_save <Option>`
==============================================================================

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","Yes","Redis server host (hidden in UI)."
    "--port <port>","Yes","Redis server port (hidden in UI)."
    "--password <pass>","No","Redis server password (hidden in UI)."
    "--svname <name>","No","Service name for the agent (hidden)."
    "--retry_count <n>","No","Redis send retry count."
    "--retry_interval <sec>","No","Retry interval in seconds."
    "--timeout <sec>","No","Max wait seconds for server response."
    "--runner_name <name>","Yes","Specify the name of the runner configuration to save."
    "--runner_instruction <text>","No","Specify instructions for the LLM model used by the runner. These will guide the agent's behavior."
    "--llm_description <text>","No","Specify a description of the runner's capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."
    "--llm <name>","No","LLM configuration name or reference."
    "--mcpservers <name>","No","List or mapping of MCP servers used by the runner."
    "--session_store_type <type>","No","Specify how the bot's session is stored."
    "--session_store_pghost <host>","No","Specify the postgresql host for session store."
    "--session_store_pgport <port>","No","Specify the postgresql port for session store."
    "--session_store_pguser <user>","No","Specify the postgresql user name for session store."
    "--session_store_pgpass <pass>","No","Specify the postgresql password for session store."
    "--session_store_pgdbname <name>","No","Specify the postgresql database name for session store."
    "--output_json <file>","No","Save result json to file."
    "--output_json_append","No","Append result json to file."

