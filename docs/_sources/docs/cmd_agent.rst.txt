.. -*- coding: utf-8 -*-

********************************
Command Reference ( agent mode )
********************************

List of agent mode commands.

agent ( agent_del ) : ``cmdbox -m agent -c agent_del <Option>``
===============================================================

- Deletes agent configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--agent_name <agent_name>","required","Specify the name of the agent configuration to delete."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( agent_list ) : ``cmdbox -m agent -c agent_list <Option>``
=================================================================

- Lists saved agent configurations.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--kwd <kwd>","","Specify the name you want to search for. Searches for partial matches."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( agent_load ) : ``cmdbox -m agent -c agent_load <Option>``
=================================================================

- Loads agent configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--agent_name <agent_name>","required","Specify the name of the agent configuration to load."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( agent_save ) : ``cmdbox -m agent -c agent_save <Option>``
=================================================================

- Saves agent configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--agent_name <agent_name>","required","Specify the name of the agent configuration to save."
    "--agent_type <agent_type>","required","Specify the agent type. Specify either `local` or `remote`."
    "--use_planner <use_planner>","","Specify whether to use the planning feature of the agent."
    "--a2asv_baseurl <a2asv_baseurl>","","Specify the base URL for the A2A Server."
    "--a2asv_delegated_auth <a2asv_delegated_auth>","","Authenticate the A2A Server using the API Key of the currently logged-in user."
    "--a2asv_apikey <a2asv_apikey>","","Specify the API Key when starting the A2A Server. Additionally, if `a2asv_delegated_auth` is disabled, it will also be used when running the Agent."
    "--llm <llm>","required","Specify the LLM configuration name referenced by the Agent."
    "--mcpservers <mcpservers>","","Specify the MCP server name used by the Agent."
    "--subagents <subagents>","","Specify the subagent name used by the agent."
    "--agent_description <agent_description>","","Specify a description of the agent's capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."
    "--agent_instruction <agent_instruction>","","Specify instructions for the LLM model used by the agent. These will guide the agent's behavior."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( chat ) : ``cmdbox -m agent -c chat <Option>``
=====================================================

- Chat with the agent.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","required","Specify the name of the Runner configuration."
    "--user_name <user_name>","required","Specify a user name."
    "--session_id <session_id>","","Specify the session ID to send to the Runner."
    "--a2asv_apikey <a2asv_apikey>","","Specify the API Key of the A2A Server."
    "--mcpserver_apikey <mcpserver_apikey>","","Specify the API Key of the remote MCP server."
    "--message <message>","required","Specify the message to send to the Runner."
    "--call_tts <call_tts>","","Specify whether to execute the TTS (Text-to-Speech) feature."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( mcp_client ) : ``cmdbox -m agent -c mcp_client <Option>``
=================================================================

- Starts an MCP client that makes requests to a remote MCP server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--mcpserver_name <mcpserver_name>","required","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <mcpserver_url>","required","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8091/mcp`."
    "--mcpserver_apikey <mcpserver_apikey>","","Specify the API Key of the remote MCP server."
    "--mcpserver_transport <mcpserver_transport>","required","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."
    "--operation <operation>","required","Specifies the operations to request from the remote MCP server. If omitted, `list_tools` is used."
    "--tool_name <tool_name>","","Specify the name of the tool to run on the remote MCP server."
    "--tool_args <tool_args>","","Specify arguments for the tool to run on the remote MCP server."
    "--mcp_timeout <mcp_timeout>","","Specifies the maximum time to wait for a response from the remote MCP server."
    "--resource_url <resource_url>","","Specify the URL of the resource to retrieve from the remote MCP server."
    "--prompt_name <prompt_name>","","Specifies the name of the prompt to be retrieved from the remote MCP server."
    "--prompt_args <prompt_args>","","Specifies prompt arguments to be retrieved from the remote MCP server."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( mcp_proxy ) : ``cmdbox -m agent -c mcp_proxy <Option>``
===============================================================

- Starts a Proxy server that accepts standard input and makes requests to a remote MCP server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--mcpserver_name <mcpserver_name>","required","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <mcpserver_url>","required","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8091/mcp`."
    "--mcpserver_apikey <mcpserver_apikey>","","Specify the API Key of the remote MCP server."
    "--mcpserver_transport <mcpserver_transport>","required","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."

agent ( mcpsv_del ) : ``cmdbox -m agent -c mcpsv_del <Option>``
===============================================================

- Deletes MCP server configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--mcpserver_name <mcpserver_name>","required","Specify the name of the MCP server configuration to delete."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( mcpsv_list ) : ``cmdbox -m agent -c mcpsv_list <Option>``
=================================================================

- Lists saved MCP server configurations.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--kwd <kwd>","","Specify the name you want to search for. Searches for partial matches."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( mcpsv_load ) : ``cmdbox -m agent -c mcpsv_load <Option>``
=================================================================

- Loads MCP server configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--mcpserver_name <mcpserver_name>","required","Specify the name of the MCP server configuration to load."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( mcpsv_save ) : ``cmdbox -m agent -c mcpsv_save <Option>``
=================================================================

- Saves MCP server configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--mcpserver_name <mcpserver_name>","required","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <mcpserver_url>","required","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8091/mcp`."
    "--mcpserver_delegated_auth <mcpserver_delegated_auth>","","Authenticate with the remote MCP server using the API key of the currently logged-in user."
    "--mcpserver_apikey <mcpserver_apikey>","","Specifies the API Key for the remote MCP server when starting the A2A Server. If `mcpserver_delegated_auth` is disabled, it is also used when running MCP."
    "--mcpserver_transport <mcpserver_transport>","required","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."
    "--mcp_tools <mcp_tools>","","Specify the tools provided by the remote server."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( memory_del ) : ``cmdbox -m agent -c memory_del <Option>``
=================================================================

- Delete the memory configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--memory_name <memory_name>","required","Specify the registration name of the memory to delete."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."

agent ( memory_list ) : ``cmdbox -m agent -c memory_list <Option>``
===================================================================

- Display a list of saved memory configurations.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--kwd <kwd>","","Specify the name you want to search for. Searches for partial matches."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( memory_load ) : ``cmdbox -m agent -c memory_load <Option>``
===================================================================

- Loads the memory configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--memory_name <memory_name>","required","Specify the registration name of the memory to load."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."

agent ( memory_save ) : ``cmdbox -m agent -c memory_save <Option>``
===================================================================

- Saves memory configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--memory_name <memory_name>","required","Specify the name of the Memory setting."
    "--memory_type <memory_type>","required","Specify the type of memory service."
    "--llm <llm>","","Specify the LLM configuration name to use for summarization processing."
    "--embed <embed>","","Specify the Embedding setting name to use for embedding processing."
    "--memory_store_pghost <memory_store_pghost>","","Specify the postgresql host for memory service."
    "--memory_store_pgport <memory_store_pgport>","","Specify the postgresql port for memory service."
    "--memory_store_pguser <memory_store_pguser>","","Specify the postgresql user name for memory service."
    "--memory_store_pgpass <memory_store_pgpass>","","Specify the postgresql password for memory service."
    "--memory_store_pgdbname <memory_store_pgdbname>","","Specify the postgresql database name for memory service."
    "--memory_description <memory_description>","","Specify a description of the agent's memory capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."
    "--memory_instruction <memory_instruction>","","Specify instructions for the LLM model used by the memory. These will guide the memory's behavior."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( memory_status ) : ``cmdbox -m agent -c memory_status <Option>``
=======================================================================

- Get the memory status for the agent.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","required","Specify the name of the Runner configuration."
    "--user_name <user_name>","required","Specify a user name."
    "--memory_query <memory_query>","","Specify a query to search memory contents. Perform semantic search."
    "--memory_fetch_offset <memory_fetch_offset>","","Specify the starting position when retrieving memory contents."
    "--memory_fetch_count <memory_fetch_count>","","Specify the number of memory contents to retrieve."
    "--memory_fetch_summary <memory_fetch_summary>","","Specify whether to summarize the retrieved memory contents."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( runner_del ) : ``cmdbox -m agent -c runner_del <Option>``
=================================================================

- Deletes runner configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","required","Specify the name of the runner configuration to delete."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( runner_list ) : ``cmdbox -m agent -c runner_list <Option>``
===================================================================

- Lists saved runner configurations.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--kwd <kwd>","","Specify the name you want to search for. Searches for partial matches."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( runner_load ) : ``cmdbox -m agent -c runner_load <Option>``
===================================================================

- Loads runner configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","required","Specify the name of the runner configuration to load."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( runner_save ) : ``cmdbox -m agent -c runner_save <Option>``
===================================================================

- Saves runner configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","required","Specify the name of the runner configuration to save."
    "--agent <agent>","required","Specify the Agent configuration name referenced by the Runner."
    "--session_store_type <session_store_type>","","Specify how the bot's session is stored."
    "--tts_engine <tts_engine>","required","Specify the TTS engine to use."
    "--memory <memory>","","Specify the Memory configuration name referenced by the Runner."
    "--rag <rag>","","Specify the RAG configuration name referenced by the Runner."
    "--voicevox_model <voicevox_model>","","Specify the model of the TTS engine to use."
    "--session_store_pghost <session_store_pghost>","","Specify the postgresql host for session store."
    "--session_store_pgport <session_store_pgport>","","Specify the postgresql port for session store."
    "--session_store_pguser <session_store_pguser>","","Specify the postgresql user name for session store."
    "--session_store_pgpass <session_store_pgpass>","","Specify the postgresql password for session store."
    "--session_store_pgdbname <session_store_pgdbname>","","Specify the postgresql database name for session store."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( session_del ) : ``cmdbox -m agent -c session_del <Option>``
===================================================================

- Delete sessions for the agent.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","required","Specify the name of the Runner configuration."
    "--user_name <user_name>","required","Specify a user name."
    "--session_id <session_id>","required","Specify the session ID to send to the Runner."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

agent ( session_list ) : ``cmdbox -m agent -c session_list <Option>``
=====================================================================

- List sessions for the agent.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","required","Specify the name of the Runner configuration."
    "--user_name <user_name>","required","Specify a user name."
    "--session_id <session_id>","","Specify the session ID to send to the Runner."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
