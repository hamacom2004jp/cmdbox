.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( agent mode )
****************************************************

- List of agent mode commands.


Delete Agent configuration. : `cmdbox -m agent -c agent_del <Option>`
==============================================================================

- Deletes agent configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--agent_name <name>","Yes","Specify the name of the agent configuration to delete."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


List Agent configuration. : `cmdbox -m agent -c agent_list <Option>`
==============================================================================

- Lists listed agent configurations.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--kwd <keyword>","","Partial match filter for agent names."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Load Agent configuration. : `cmdbox -m agent -c agent_load <Option>`
==============================================================================

- Loads agent configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--agent_name <name>","Yes","Specify the name of the agent configuration to load."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Save Agent configuration. : `cmdbox -m agent -c agent_save <Option>`
==============================================================================

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--agent_name <name>","Yes","Specify the name of the agent configuration to save."
    "--agent_type <type>","Yes","Specify the agent type. Specify either `local` or `remote`."
    "--a2asv_baseurl <url>","","Specify the base URL for the A2A Server."
    "--llm <name>","","LLM configuration name or reference."
    "--mcpservers <name>","","Specify the MCP server name used by the Agent."
    "--subagents <name>","","Specify the subagent name used by the agent."
    "--agent_description <text>","","Specify a description of the agent's capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."
    "--agent_instruction <text>","","Specify instructions for the LLM model used by the agent. These will guide the agent's behavior."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


MCP client : `cmdbox -m agent -c mcp_client <Option>`
==============================================================================
- Starts an MCP client that makes requests to a remote MCP server.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--mcpserver_name <name>","Yes","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <url>","Yes","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8091/mcp`."
    "--mcpserver_apikey <apikey>","","Specify the API Key of the remote MCP server."
    "--mcpserver_transport <transport>","Yes","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."
    "--operation <op>","Yes","Specifies the operations to request from the remote MCP server. If omitted, `list_tools` is used."
    "--tool_name <name>","","Specify the name of the tool to run on the remote MCP server."
    "--tool_args <dict>","","Specify arguments for the tool to run on the remote MCP server."
    "--mcp_timeout <sec>","","Specifies the maximum time to wait for a response from the remote MCP server."
    "--resource_url <url>","","Specify the URL of the resource to retrieve from the remote MCP server."
    "--prompt_name <name>","","Specifies the name of the prompt to be retrieved from the remote MCP server."
    "--prompt_args <dict>","","Specifies prompt arguments to be retrieved from the remote MCP server."


Proxy to transport MCP : `cmdbox -m agent -c mcp_proxy <Option>`
==============================================================================

- Starts a Proxy server that accepts standard input and makes requests to a remote MCP server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--mcpserver_name <name>","","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <url>","","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8091/mcp`."
    "--mcpserver_apikey <apikey>","","Specify the API Key of the remote MCP server."
    "--mcpserver_transport <transport>","","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."

Delete MCP server configuration. : `cmdbox -m agent -c mcpsv_del <Option>`
===============================================================================

- Deletes MCP server configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--mcpserver_name <name>","Yes","Specify the name of the MCP server configuration to delete."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Lists MCP server configurations. : `cmdbox -m agent -c mcpsv_list <Option>`
==============================================================================

- Lists saved MCP server configurations.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--kwd <keyword>","","Specify the name you want to search for. Searches for partial matches."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Loads MCP server configuration. : `cmdbox -m agent -c mcpsv_load <Option>`
==============================================================================

- Loads MCP server configuration from the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--mcpserver_name <name>","Yes","Specify the name of the MCP server configuration to load."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Saves MCP server configuration. : `cmdbox -m agent -c mcpsv_save <Option>`
==============================================================================

- Saves MCP server configuration via the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--mcpserver_name <name>","Yes","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <url>","Yes","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8091/mcp`."
    "--mcpserver_delegated_auth","","Authenticate with the remote MCP server using the API key of the currently logged-in user."
    "--mcpserver_apikey <apikey>","","Specifies the API Key for the remote MCP server when starting the A2A Server. If `mcpserver_delegated_auth` is disabled, it is also used when running MCP."
    "--mcpserver_transport <transport>","Yes","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."
    "--mcp_tools <list>","","Specify the tools provided by the remote server."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Delete Memory configuration. : `cmdbox -m agent -c memory_del <Option>`
==============================================================================

- Delete the memory configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--memory_name <name>","Yes","Specify the registration name of the memory to delete."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


List Memory configuration. : `cmdbox -m agent -c memory_list <Option>`
==============================================================================

- Display a list of saved memory configurations.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--kwd <keyword>","","Partial match filter for memory names."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Load Memory configuration. : `cmdbox -m agent -c memory_load <Option>`
==============================================================================

- Loads the memory configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--memory_name <name>","Yes","Specify the registration name of the memory to load."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Save Memory configuration. : `cmdbox -m agent -c memory_save <Option>`
==============================================================================

- Saves memory configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--memory_name <name>","Yes","Specify the name of the Memory setting."
    "--memory_type <type>","Yes","Specify the type of memory service."
    "--llm <name>","","Specify the LLM configuration name to use for summarization processing."
    "--embed <name>","","Specify the Embedding setting name to use for embedding processing."
    "--memory_store_pghost <host>","","Specify the postgresql host for memory service."
    "--memory_store_pgport <port>","","Specify the postgresql port for memory service."
    "--memory_store_pguser <user>","","Specify the postgresql user name for memory service."
    "--memory_store_pgpass <pass>","","Specify the postgresql password for memory service."
    "--memory_store_pgdbname <name>","","Specify the postgresql database name for memory service."
    "--memory_description <desc>","","Specify a description of the agent's memory capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."
    "--memory_instruction <inst>","","Specify instructions for the LLM model used by the memory. These will guide the memory's behavior."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Status Memory configuration. : `cmdbox -m agent -c memory_save <Option>`
==============================================================================

- Get the memory status for the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--runner_name <name>","Yes","Specify the name of the Runner configuration."
    "--user_name <name>","Yes","Specify a user name."
    "--memory_query <query>","","Specify a query to search memory contents. Perform semantic search."
    "--memory_fetch_offset <offset>","","Specify the starting position when retrieving memory contents."
    "--memory_fetch_count <count>","","Specify the number of memory contents to retrieve."
    "--memory_fetch_summary","","Specify whether to summarize the retrieved memory contents."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Status Memory configuration. : `cmdbox -m agent -c memory_status <Option>`
==============================================================================

- Get the memory status for the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--runner_name <name>","Yes","Specify the name of the Runner configuration."
    "--user_name <name>","Yes","Specify a user name."
    "--memory_query <query>","","Specify a query to search memory contents. Perform semantic search."
    "--memory_fetch_offset <offset>","","Specify the starting position when retrieving memory contents."
    "--memory_fetch_count <count>","","Specify the number of memory contents to retrieve."
    "--memory_fetch_summary","","Specify whether to summarize the retrieved memory contents."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

Delete runner configuration. : `cmdbox -m agent -c runner_del <Option>`
==============================================================================

- Deletes runner configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--runner_name <name>","Yes","Specify the name of the runner configuration to delete."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


List runner configuration. : `cmdbox -m agent -c runner_list <Option>`
==============================================================================

- Lists listed runner configurations.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--kwd <keyword>","","Partial match filter for runner names."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Load runner configuration. : `cmdbox -m agent -c runner_load <Option>`
==============================================================================

- Loads runner configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--runner_name <name>","Yes","Specify the name of the runner configuration to load."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Save runner configuration. : `cmdbox -m agent -c runner_save <Option>`
==============================================================================

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--runner_name <name>","Yes","Specify the name of the runner configuration to save."
    "--agent <name>","Yes","Agent configuration name or reference."
    "--tts_engine <engine>","","Specify the TTS engine to use."
    "--memory <name>","","Specify the Memory configuration name referenced by the Runner."
    "--rag <name>","","Specify the RAG configuration name referenced by the Runner."
    "--voicevox_model <model>","","Specify the model of the TTS engine to use."
    "--session_store_type <type>","","Specify how the bot's session is stored."
    "--session_store_pghost <host>","","Specify the postgresql host for session store."
    "--session_store_pgport <port>","","Specify the postgresql port for session store."
    "--session_store_pguser <user>","","Specify the postgresql user name for session store."
    "--session_store_pgpass <pass>","","Specify the postgresql password for session store."
    "--session_store_pgdbname <name>","","Specify the postgresql database name for session store."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Chat with the agent. : `cmdbox -m agent -c chat <Option>`
==============================================================================

- Chat with the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--runner_name <name>","Yes","Specify the name of the Runner configuration."
    "--user_name <name>","Yes","Specify a user name."
    "--session_id <id>","","Specify the session ID to send to the Runner."
    "--a2asv_apikey <apikey>","","Specify the API Key of the A2A Server."
    "--mcpserver_apikey <apikey>","","Specify the API Key of the remote MCP server."
    "--message <text>","Yes","Specify the message to send to the Runner."
    "--call_tts","","Specify whether to execute the TTS (Text-to-Speech) feature."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


List sessions for the agent. : `cmdbox -m agent -c session_list <Option>`
==============================================================================

- List sessions for the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--runner_name <name>","Yes","Specify the name of the Runner configuration."
    "--user_name <name>","Yes","Specify a user name."
    "--session_id <id>","","Specify the session ID to send to the Runner."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Delete sessions for the agent. : `cmdbox -m agent -c session_del <Option>`
==============================================================================

- Delete sessions for the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--runner_name <name>","Yes","Specify the name of the Runner configuration."
    "--user_name <name>","Yes","Specify a user name."
    "--session_id <id>","Yes","Specify the session ID to send to the Runner."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

