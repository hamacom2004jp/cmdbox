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


Deletes LLM configuration. : `cmdbox -m agent -c llm_del <Option>`
==============================================================================

- Deletes LLM configuration. This command sends a delete request to the agent via Redis.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--llmname <name>","Yes","Specify the name of the LLM configuration to delete."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Lists saved LLM configurations. : `cmdbox -m agent -c llm_list <Option>`
==============================================================================

- Lists saved LLM configurations. Sends a list request to the agent and receives matching LLM names.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--kwd <keyword>","","Specify a partial match keyword to filter saved LLMs."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Loads LLM configuration. : `cmdbox -m agent -c llm_load <Option>`
==============================================================================

- Loads LLM configuration from the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--llmname <name>","Yes","Specify the name of the LLM configuration to load."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Saves LLM configuration. : `cmdbox -m agent -c llm_save <Option>`
===============================================================================

- Saves LLM configuration via the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--llmname <name>","Yes","Specify the name of the LLM configuration to save."
    "--llmprov <provider>","Yes","Specify llm provider."
    "--llmprojectid <id>","","Project ID for provider connection."
    "--llmsvaccountfile <file>","","Service account file for provider connection."
    "--llmlocation <location>","","Provider location."
    "--llmapikey <key>","","API key for provider connection."
    "--llmapiversion <version>","","Specifies the API version for llm provider connections."
    "--llmendpoint <endpoint>","","Provider endpoint."
    "--llmmodel <model>","","LLM model name."
    "--llmseed <int>","","Seed for model sampling."
    "--llmtemperature <float>","","Temperature for model sampling."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Agent client start : `cmdbox -m agent -c mcp_client <Option>`
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


Agent stdio to transport proxy start : `cmdbox -m agent -c mcp_proxy <Option>`
==============================================================================

- This command invokes a proxy to forward MCP standard input/output via TCP/IP.

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


Starts a runner. : `cmdbox -m agent -c start <Option>`
==============================================================================

- Starts a runner.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--runner_name <name>","Yes","Specify the name of the Runner configuration."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Stops a runner. : `cmdbox -m agent -c stop <Option>`
==============================================================================

- Stops a runner.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--runner_name <name>","Yes","Specify the name of the Runner configuration."
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

