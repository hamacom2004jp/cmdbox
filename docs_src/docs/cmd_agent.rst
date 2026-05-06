.. -*- coding: utf-8 -*-

********************************
Command Reference ( agent mode )
********************************

List of agent mode commands.

agent ( agent_del ) : ``cmdbox -m agent -c agent_del <Option>``
===============================================================

- Deletes agent configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--agent_name <agent_name>","str","","required","","","Specify the name of the agent configuration to delete."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( agent_list ) : ``cmdbox -m agent -c agent_list <Option>``
=================================================================

- Lists saved agent configurations.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--kwd <kwd>","str","","","","","Specify the name you want to search for. Searches for partial matches."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          {
            "name": "string",
            "path": "<class 'pathlib.Path'>"
          }
        ]
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data","yes","(必須)","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[NamePath]","no","(必須)","処理結果のデータ"
    "success.data.name","str","yes","(必須)","名前"
    "success.data.path","Path | str | null","no","null","パス"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( agent_load ) : ``cmdbox -m agent -c agent_load <Option>``
=================================================================

- Loads agent configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--agent_name <agent_name>","str","","required","","","Specify the name of the agent configuration to load."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "agent_name": "string",
        "agent_type": "string",
        "use_planner": false,
        "a2asv_baseurl": "string",
        "a2asv_delegated_auth": false,
        "a2asv_apikey": "string",
        "llm": "string",
        "mcpservers": [
          "string"
        ],
        "subagents": [
          "string"
        ],
        "agent_description": "string",
        "agent_instruction": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data","yes","(必須)","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.agent_name","str","no","null","エージェント名"
    "success.agent_type","str","no","null","エージェントタイプ"
    "success.use_planner","bool | null","no","null","プランナー使用フラグ"
    "success.a2asv_baseurl","str | null","no","null","A2AサーバーのベースURL"
    "success.a2asv_delegated_auth","bool | null","no","null","A2Aサーバーの委任認証フラグ"
    "success.a2asv_apikey","str | null","no","null","A2AサーバーのAPIキー"
    "success.llm","str | null","no","null","LLM名"
    "success.mcpservers","list[str] | null","no","null","MCPサーバーリスト"
    "success.subagents","list[str] | null","no","null","サブエージェントリスト"
    "success.agent_description","str | null","no","null","エージェントの説明"
    "success.agent_instruction","str | null","no","null","エージェントへの指示"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( agent_save ) : ``cmdbox -m agent -c agent_save <Option>``
=================================================================

- Saves agent configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--agent_name <agent_name>","str","","required","","","Specify the name of the agent configuration to save."
    "--agent_type <agent_type>","str","","required","local","local | remote","Specify the agent type. Specify either `local` or `remote`."
    "--use_planner <use_planner>","bool","","","False","False | True","Specify whether to use the planning feature of the agent."
    "--a2asv_baseurl <a2asv_baseurl>","str","","","http://localhost:8071/a2a/<agent_name>","","Specify the base URL for the A2A Server."
    "--a2asv_delegated_auth <a2asv_delegated_auth>","bool","","","False","True | False","Authenticate the A2A Server using the API Key of the currently logged-in user."
    "--a2asv_apikey <a2asv_apikey>","passwd","","","","","Specify the API Key when starting the A2A Server. Additionally, if `a2asv_delegated_auth` is disabled, it will also be used when running the Agent."
    "--llm <llm>","str","","required","","","Specify the LLM configuration name referenced by the Agent."
    "--mcpservers <mcpservers>","str","multi","","","","Specify the MCP server name used by the Agent."
    "--subagents <subagents>","str","multi","","","","Specify the subagent name used by the agent."
    "--agent_description <agent_description>","text","","","cmdboxに登録されているコマンド提供","","Specify a description of the agent's capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."
    "--agent_instruction <agent_instruction>","text","","","あなたはコマンドの意味を熟知しているエキスパートです。ユーザーがコマンドを実行したいとき、あなたは以下の手順に従ってコマンドを確実に実行してください。<br>1. ユーザーのクエリからが実行したいコマンドを特定します。<br>2. コマンド実行に必要なパラメータのなかで、ユーザーのクエリから取得できないものは、特にパラメータを指定せず実行してください。<br>3. もしエラーが発生した場合は、ユーザーにコマンド名とパラメータとエラー内容を提示してください。<br>4. コマンドの実行結果は、json文字列で出力するようにしてください。この時json文字列は「```json」と「```」で囲んだ文字列にしてください。<br>","","Specify instructions for the LLM model used by the agent. These will guide the agent's behavior."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( chat ) : ``cmdbox -m agent -c chat <Option>``
=====================================================

- Chat with the agent.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","600","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","str","","required","","","Specify the name of the Runner configuration."
    "--user_name <user_name>","str","","required","","","Specify a user name."
    "--session_id <session_id>","str","","","","","Specify the session ID to send to the Runner."
    "--a2asv_apikey <a2asv_apikey>","passwd","","","","","Specify the API Key of the A2A Server."
    "--mcpserver_apikey <mcpserver_apikey>","passwd","","","","","Specify the API Key of the remote MCP server."
    "--message <message>","text","","required","","","Specify the message to send to the Runner."
    "--call_tts <call_tts>","bool","","","False","True | False","Specify whether to execute the TTS (Text-to-Speech) feature."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "ids": {
          "agent_session_id": "string",
          "event_id": "string",
          "invocation_id": "string"
        },
        "flags": {
          "final_response": false,
          "function_call": false,
          "function_response": false
        },
        "message": "string",
        "wav_b64": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.ids","Ids | null","no","null","セッション・イベントID情報"
    "success.ids.agent_session_id","str","no","null","エージェントセッションID"
    "success.ids.event_id","str","no","null","イベントID"
    "success.ids.invocation_id","str","no","null","呼び出しID"
    "success.flags","Flags | null","no","null","フラグ情報"
    "success.flags.final_response","bool","no","False","最終レスポンスフラグ"
    "success.flags.function_call","bool","no","False","関数呼び出しフラグ"
    "success.flags.function_response","bool","no","False","関数レスポンスフラグ"
    "success.message","str | null","no","null","メッセージ"
    "success.wav_b64","str | null","no","null","Base64エンコードされたWAVデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( mcp_client ) : ``cmdbox -m agent -c mcp_client <Option>``
=================================================================

- Starts an MCP client that makes requests to a remote MCP server.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--mcpserver_name <mcpserver_name>","str","","required","mcpserver","","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <mcpserver_url>","str","","required","http://localhost:8091/mcp","","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8091/mcp`."
    "--mcpserver_apikey <mcpserver_apikey>","passwd","","","","","Specify the API Key of the remote MCP server."
    "--mcpserver_transport <mcpserver_transport>","str","","required","streamable-http"," | streamable-http | sse | http","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."
    "--operation <operation>","str","","required","list_tools","list_tools | call_tool | list_resources | read_resource | list_prompts | get_prompt","Specifies the operations to request from the remote MCP server. If omitted, `list_tools` is used."
    "--tool_name <tool_name>","str","","","","","Specify the name of the tool to run on the remote MCP server."
    "--tool_args <tool_args>","dict","multi","","","","Specify arguments for the tool to run on the remote MCP server."
    "--mcp_timeout <mcp_timeout>","int","","","60","","Specifies the maximum time to wait for a response from the remote MCP server."
    "--resource_url <resource_url>","str","","","","","Specify the URL of the resource to retrieve from the remote MCP server."
    "--prompt_name <prompt_name>","str","","","","","Specifies the name of the prompt to be retrieved from the remote MCP server."
    "--prompt_args <prompt_args>","dict","multi","","","","Specifies prompt arguments to be retrieved from the remote MCP server."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          null
        ]
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[any] | any","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( mcp_proxy ) : ``cmdbox -m agent -c mcp_proxy <Option>``
===============================================================

- Starts a Proxy server that accepts standard input and makes requests to a remote MCP server.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--mcpserver_name <mcpserver_name>","str","","required","mcpserver","","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <mcpserver_url>","str","","required","http://localhost:8091/mcp","","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8091/mcp`."
    "--mcpserver_apikey <mcpserver_apikey>","passwd","","","","","Specify the API Key of the remote MCP server."
    "--mcpserver_transport <mcpserver_transport>","str","","required","streamable-http"," | streamable-http | sse | http","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( mcpsv_del ) : ``cmdbox -m agent -c mcpsv_del <Option>``
===============================================================

- Deletes MCP server configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--mcpserver_name <mcpserver_name>","str","","required","","","Specify the name of the MCP server configuration to delete."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( mcpsv_list ) : ``cmdbox -m agent -c mcpsv_list <Option>``
=================================================================

- Lists saved MCP server configurations.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--kwd <kwd>","str","","","","","Specify the name you want to search for. Searches for partial matches."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          {
            "name": "string",
            "path": "<class 'pathlib.Path'>"
          }
        ]
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[NamePath]","no","(必須)","処理結果のデータ"
    "success.data.name","str","yes","(必須)","名前"
    "success.data.path","Path | str | null","no","null","パス"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( mcpsv_load ) : ``cmdbox -m agent -c mcpsv_load <Option>``
=================================================================

- Loads MCP server configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--mcpserver_name <mcpserver_name>","str","","required","","","Specify the name of the MCP server configuration to load."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "mcpserver_name": "string",
        "mcpserver_url": "string",
        "mcpserver_apikey": "string",
        "mcpserver_delegated_auth": false,
        "mcpserver_transport": "string",
        "mcpserver_mcp_tools": [
          "string"
        ]
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.mcpserver_name","str | null","no","null","MCPサーバー名"
    "success.mcpserver_url","str | null","no","null","MCPサーバーURL"
    "success.mcpserver_apikey","str | null","no","null","MCPサーバーAPIキー"
    "success.mcpserver_delegated_auth","bool | null","no","null","MCPサーバー委任認証フラグ"
    "success.mcpserver_transport","str | null","no","null","MCPサーバートランスポート"
    "success.mcpserver_mcp_tools","list[str] | null","no","null","MCPツールリスト"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( mcpsv_save ) : ``cmdbox -m agent -c mcpsv_save <Option>``
=================================================================

- Saves MCP server configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--mcpserver_name <mcpserver_name>","str","","required","mcpserver","","Specify the name of the MCP server. If omitted, it will be `mcpserver`."
    "--mcpserver_url <mcpserver_url>","str","","required","http://localhost:8091/mcp","","Specifies the URL of the remote MCP server. If omitted, it will be `http://localhost:8091/mcp`."
    "--mcpserver_delegated_auth <mcpserver_delegated_auth>","bool","","","False","True | False","Authenticate with the remote MCP server using the API key of the currently logged-in user."
    "--mcpserver_apikey <mcpserver_apikey>","passwd","","","","","Specifies the API Key for the remote MCP server when starting the A2A Server. If `mcpserver_delegated_auth` is disabled, it is also used when running MCP."
    "--mcpserver_transport <mcpserver_transport>","str","","required","streamable-http"," | streamable-http | sse","Specifies the transport of the remote MCP server. If omitted, it is `streamable-http`."
    "--mcp_tools <mcp_tools>","mlist","","","","","Specify the tools provided by the remote server."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( memory_del ) : ``cmdbox -m agent -c memory_del <Option>``
=================================================================

- Delete the memory configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."
    "--memory_name <memory_name>","str","","required","","","Specify the registration name of the memory to delete."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( memory_list ) : ``cmdbox -m agent -c memory_list <Option>``
===================================================================

- Display a list of saved memory configurations.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--kwd <kwd>","str","","","","","Specify the name you want to search for. Searches for partial matches."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          {
            "name": "string",
            "path": "<class 'pathlib.Path'>"
          }
        ]
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[NamePath]","no","(必須)","処理結果のデータ"
    "success.data.name","str","yes","(必須)","名前"
    "success.data.path","Path | str | null","no","null","パス"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( memory_load ) : ``cmdbox -m agent -c memory_load <Option>``
===================================================================

- Loads the memory configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."
    "--memory_name <memory_name>","str","","required","","","Specify the registration name of the memory to load."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "memory_name": "string",
        "memory_type": "string",
        "llm": "string",
        "embed": "string",
        "memory_store_pghost": "string",
        "memory_store_pgport": 0,
        "memory_store_pguser": "string",
        "memory_store_pgpass": "string",
        "memory_store_pgdbname": "string",
        "memory_description": "string",
        "memory_instruction": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.memory_name","str | null","no","null","メモリ名"
    "success.memory_type","str | null","no","null","メモリタイプ"
    "success.llm","str | null","no","null","LLM名"
    "success.embed","str | null","no","null","エンベッディング名"
    "success.memory_store_pghost","str | null","no","null","メモリストアPostgreSQLホスト"
    "success.memory_store_pgport","int | null","no","null","メモリストアPostgreSQLポート"
    "success.memory_store_pguser","str | null","no","null","メモリストアPostgreSQLユーザー"
    "success.memory_store_pgpass","str | null","no","null","メモリストアPostgreSQLパスワード"
    "success.memory_store_pgdbname","str | null","no","null","メモリストアPostgreSQLデータベース名"
    "success.memory_description","str | null","no","null","メモリの説明"
    "success.memory_instruction","str | null","no","null","メモリへの指示"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( memory_save ) : ``cmdbox -m agent -c memory_save <Option>``
===================================================================

- Saves memory configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--memory_name <memory_name>","str","","required","","","Specify the name of the Memory setting."
    "--memory_type <memory_type>","str","","required","memory"," | memory | sqlite | postgresql","Specify the type of memory service."
    "--llm <llm>","str","","","","","Specify the LLM configuration name to use for summarization processing."
    "--embed <embed>","str","","","","","Specify the Embedding setting name to use for embedding processing."
    "--memory_store_pghost <memory_store_pghost>","str","","","pgsql","","Specify the postgresql host for memory service."
    "--memory_store_pgport <memory_store_pgport>","int","","","5432","","Specify the postgresql port for memory service."
    "--memory_store_pguser <memory_store_pguser>","str","","","pgsql","","Specify the postgresql user name for memory service."
    "--memory_store_pgpass <memory_store_pgpass>","passwd","","","pgsql","","Specify the postgresql password for memory service."
    "--memory_store_pgdbname <memory_store_pgdbname>","str","","","pgsql","","Specify the postgresql database name for memory service."
    "--memory_description <memory_description>","text","","","cmdboxのメモリ設定","","Specify a description of the agent's memory capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."
    "--memory_instruction <memory_instruction>","text","","","あなたはユーザーの期待値を推測することが出来るメモリ管理のエキスパートです。ユーザーとエージェントとの会話の内容のみを根拠に、発言傾向と行動パターンから確認できる事実だけを500文字程度で要約してください。<br>ただし、不明な時は『確認できない』と答えてください。<br>さらに、得た内容を根拠に以下の点を提示してください。<br>１．一貫した思考傾向<br>２．強みの思考パターン<br>３．内面ギャップの可能性<br>","","Specify instructions for the LLM model used by the memory. These will guide the memory's behavior."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( memory_status ) : ``cmdbox -m agent -c memory_status <Option>``
=======================================================================

- Get the memory status for the agent.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","str","","required","","","Specify the name of the Runner configuration."
    "--user_name <user_name>","str","","required","","","Specify a user name."
    "--memory_query <memory_query>","text","","","","","Specify a query to search memory contents. Perform semantic search."
    "--memory_fetch_offset <memory_fetch_offset>","int","","","0","","Specify the starting position when retrieving memory contents."
    "--memory_fetch_count <memory_fetch_count>","int","","","10","","Specify the number of memory contents to retrieve."
    "--memory_fetch_summary <memory_fetch_summary>","bool","","","False","False | True","Specify whether to summarize the retrieved memory contents."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          {
            "event_id": "string",
            "distance": 0.0,
            "role": "string",
            "my_cnt": 0,
            "ts_start": "string",
            "ts_end": "string",
            "all_cnt": 0,
            "text": "string"
          }
        ]
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[MemoryRecord] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( runner_del ) : ``cmdbox -m agent -c runner_del <Option>``
=================================================================

- Deletes runner configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","str","","required","","","Specify the name of the runner configuration to delete."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( runner_list ) : ``cmdbox -m agent -c runner_list <Option>``
===================================================================

- Lists saved runner configurations.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--kwd <kwd>","str","","","","","Specify the name you want to search for. Searches for partial matches."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          {
            "name": "string",
            "path": "<class 'pathlib.Path'>"
          }
        ]
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[NamePath]","no","(必須)","処理結果のデータ"
    "success.data.name","str","yes","(必須)","名前"
    "success.data.path","Path | str | null","no","null","パス"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( runner_load ) : ``cmdbox -m agent -c runner_load <Option>``
===================================================================

- Loads runner configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","str","","required","","","Specify the name of the runner configuration to load."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "runner_name": "string",
        "agent": "string",
        "session_store_type": "string",
        "tts_engine": "string",
        "memory": "string",
        "rag": [
          "string"
        ],
        "voicevox_model": "string",
        "session_store_pghost": "string",
        "session_store_pgport": 0,
        "session_store_pguser": "string",
        "session_store_pgpass": "string",
        "session_store_pgdbname": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.runner_name","str | null","no","null","ランナー名"
    "success.agent","str | null","no","null","エージェント名"
    "success.session_store_type","str | null","no","null","セッションストアタイプ"
    "success.tts_engine","str | null","no","null","TTSエンジン名"
    "success.memory","str | null","no","null","メモリ名"
    "success.rag","list[str] | null","no","null","RAG設定リスト"
    "success.voicevox_model","str | null","no","null","VOICEVOXモデル"
    "success.session_store_pghost","str | null","no","null","セッションストアPostgreSQLホスト"
    "success.session_store_pgport","int | null","no","null","セッションストアPostgreSQLポート"
    "success.session_store_pguser","str | null","no","null","セッションストアPostgreSQLユーザー"
    "success.session_store_pgpass","str | null","no","null","セッションストアPostgreSQLパスワード"
    "success.session_store_pgdbname","str | null","no","null","セッションストアPostgreSQLデータベース名"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( runner_save ) : ``cmdbox -m agent -c runner_save <Option>``
===================================================================

- Saves runner configuration.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","str","","required","","","Specify the name of the runner configuration to save."
    "--agent <agent>","str","","required","","","Specify the Agent configuration name referenced by the Runner."
    "--session_store_type <session_store_type>","str","","","memory","memory | sqlite | postgresql","Specify how the bot's session is stored."
    "--tts_engine <tts_engine>","str","","required","voicevox"," | voicevox","Specify the TTS engine to use."
    "--memory <memory>","str","","","","","Specify the Memory configuration name referenced by the Runner."
    "--rag <rag>","str","multi","","","","Specify the RAG configuration name referenced by the Runner."
    "--voicevox_model <voicevox_model>","str","","","","No.7アナウンス | No.7ノーマル | No.7読み聞かせ | Voidollノーマル | WhiteCULかなしい | WhiteCULたのしい | WhiteCULびえーん | WhiteCULノーマル | †聖騎士 紅桜†ノーマル | あいえるたんノーマル | ずんだもんあまあま | ずんだもんささやき | ずんだもんなみだめ | ずんだもんセクシー | ずんだもんツンツン | ずんだもんノーマル | ずんだもんヒソヒソ | ずんだもんヘロヘロ | ぞん子ノーマル | ぞん子低血圧 | ぞん子実況風 | ぞん子覚醒 | ちび式じいノーマル | もち子さんのんびり | もち子さんセクシー／あん子 | もち子さんノーマル | もち子さん喜び | もち子さん怒り | もち子さん泣き | ナースロボ＿タイプＴノーマル | ナースロボ＿タイプＴ内緒話 | ナースロボ＿タイプＴ恐怖 | ナースロボ＿タイプＴ楽々 | ユーレイちゃんささやき | ユーレイちゃんツクモちゃん | ユーレイちゃんノーマル | ユーレイちゃん哀しみ | ユーレイちゃん甘々 | 中国うさぎおどろき | 中国うさぎこわがり | 中国うさぎへろへろ | 中国うさぎノーマル | 中部つるぎおどおど | 中部つるぎノーマル | 中部つるぎヒソヒソ | 中部つるぎ怒り | 中部つるぎ絶望と敗北 | 九州そらあまあま | 九州そらささやき | 九州そらセクシー | 九州そらツンツン | 九州そらノーマル | 冥鳴ひまりノーマル | 剣崎雌雄ノーマル | 四国めたんあまあま | 四国めたんささやき | 四国めたんセクシー | 四国めたんツンツン | 四国めたんノーマル | 四国めたんヒソヒソ | 小夜/SAYOノーマル | 後鬼ぬいぐるみver. | 後鬼人間ver. | 後鬼人間（怒り）ver. | 後鬼鬼ver. | 春日部つむぎノーマル | 春歌ナナノーマル | 東北きりたんノーマル | 東北ずん子ノーマル | 東北イタコノーマル | 栗田まろんノーマル | 櫻歌ミコノーマル | 櫻歌ミコロリ | 櫻歌ミコ第二形態 | 波音リツクイーン | 波音リツノーマル | 満別花丸ささやき | 満別花丸ぶりっ子 | 満別花丸ノーマル | 満別花丸ボーイ | 満別花丸元気 | 猫使アルうきうき | 猫使アルおちつき | 猫使アルつよつよ | 猫使アルへろへろ | 猫使アルノーマル | 猫使ビィおちつき | 猫使ビィつよつよ | 猫使ビィノーマル | 猫使ビィ人見知り | 玄野武宏ツンギレ | 玄野武宏ノーマル | 玄野武宏喜び | 玄野武宏悲しみ | 琴詠ニアノーマル | 白上虎太郎おこ | 白上虎太郎びえーん | 白上虎太郎びくびく | 白上虎太郎ふつう | 白上虎太郎わーい | 雀松朱司ノーマル | 離途シリアス | 離途ノーマル | 雨晴はうノーマル | 青山龍星かなしみ | 青山龍星しっとり | 青山龍星ノーマル | 青山龍星不機嫌 | 青山龍星喜び | 青山龍星囁き | 青山龍星熱血 | 麒ヶ島宗麟ノーマル | 黒沢冴白ノーマル","Specify the model of the TTS engine to use."
    "--session_store_pghost <session_store_pghost>","str","","","pgsql","","Specify the postgresql host for session store."
    "--session_store_pgport <session_store_pgport>","int","","","5432","","Specify the postgresql port for session store."
    "--session_store_pguser <session_store_pguser>","str","","","pgsql","","Specify the postgresql user name for session store."
    "--session_store_pgpass <session_store_pgpass>","passwd","","","pgsql","","Specify the postgresql password for session store."
    "--session_store_pgdbname <session_store_pgdbname>","str","","","pgsql","","Specify the postgresql database name for session store."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( session_del ) : ``cmdbox -m agent -c session_del <Option>``
===================================================================

- Delete sessions for the agent.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","str","","required","","","Specify the name of the Runner configuration."
    "--user_name <user_name>","str","","required","","","Specify a user name."
    "--session_id <session_id>","str","","required","","","Specify the session ID to send to the Runner."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          "string"
        ]
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[str] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


agent ( session_list ) : ``cmdbox -m agent -c session_list <Option>``
=====================================================================

- List sessions for the agent.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."
    "--runner_name <runner_name>","str","","required","","","Specify the name of the Runner configuration."
    "--user_name <user_name>","str","","required","","","Specify a user name."
    "--session_id <session_id>","str","","","","","Specify the session ID to send to the Runner."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          {
            "runner_name": "string",
            "session_id": "string",
            "user_name": "string",
            "last_update_time": null,
            "events": [
              {
                "author": "string",
                "text": "string",
                "final_response": false,
                "function_call": false,
                "function_response": false
              }
            ]
          }
        ]
      },
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[SessionRecord] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

