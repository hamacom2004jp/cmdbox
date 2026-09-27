.. -*- coding: utf-8 -*-

******************************
Command Reference ( llm mode )
******************************

List of llm mode commands.

llm ( chat ) : ``cmdbox -m llm -c chat <Option>``
=================================================

- Send a chat message to the LLM.

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
    "--timeout <timeout>","int","","","600","","Specify the maximum waiting time until the server responds."
    "--llmname <llmname>","str","","","","","Specify the name of the LLM configuration to use. If omitted, the LLM configuration with the highest priority is automatically selected."
    "--msg_role <msg_role>","str","","required","user","user | assistant | system | function | tool","Specify the role of the message sender."
    "--msg_name <msg_name>","str","","","","","Specify the name of the message sender. Required if msg_role is `function` or `tool`."
    "--msg_text <msg_text>","text","","","","","Specify the content of the text to be sent."
    "--msg_text_system <msg_text_system>","text","","","次のユーザーの依頼にこたえてください。\n\n{{msg_text}}","","Specify the system prompt to send. Using `{{AAA}}` allows you to set the `AAA` parameter. Note that specifying `{{msg_text}}` sets the value of the `msg_text` option."
    "--msg_text_param <msg_text_param>","dict","multi","","","","Specify the parameters for the text."
    "--msg_image_url <msg_image_url>","str","","","","","Specify the URL of the image to be sent."
    "--scope <scope>","str","","","client","client | current | server","Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory."
    "--fwpath <fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--msg_audio <msg_audio>","file","","","","","Specify the content of the audio to be sent."
    "--msg_audio_format <msg_audio_format>","str","","","wav","wav | mp3 | ogg | flac","Specify the format of the audio to be sent."
    "--msg_video_url <msg_video_url>","str","","","","","Specify the URL of the video to be sent."
    "--msg_file_url <msg_file_url>","str","","","","","Specify the URL of the file to be sent."
    "--msg_file <msg_file>","file","","","","","Specify the content of the file to be sent."
    "--msg_file_mime <msg_file_mime>","str","","","application/pdf","","Specify the MIME type of the file to be sent."
    "--groups <groups>","str","multi","","","","Specify user groups used to authorize chat operations."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": null,
        "token_usage": {}
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | str | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","any | null","no","null","処理結果のデータ"
    "success.token_usage","dict[str, any] | null","no","null","トークン使用量"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


llm ( del ) : ``cmdbox -m llm -c del <Option>``
===============================================

- Deletes LLM configuration.

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
    "--llmname <llmname>","str","","required","","","Specify the name of the LLM configuration to delete."
    "--groups <groups>","str","multi","","","","Specify user groups used to authorize LLM configuration deletion."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
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
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


llm ( embed ) : ``cmdbox -m llm -c embed <Option>``
===================================================

- Request text embedding from the LLM.

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
    "--timeout <timeout>","int","","","600","","Specify the maximum waiting time until the server responds."
    "--llmname <llmname>","str","","","","","Specify the name of the LLM configuration to use. If omitted, the LLM configuration with the highest priority is automatically selected."
    "--input_text <input_text>","text","multi","required","","","Specify the text to embed. Multiple values can be specified."
    "--groups <groups>","str","multi","","","","Specify user groups used to authorize chat operations."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": null
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | str | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","any | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


llm ( list ) : ``cmdbox -m llm -c list <Option>``
=================================================

- Lists saved LLM configurations.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--kwd <kwd>","str","","","","","Specify the name you want to search for. Searches for partial matches."
    "--groups <groups>","str","multi","","","","Specify to return only LLM configurations available to this user group."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": [
          {
            "name": "string",
            "path": "string",
            "priority": 0,
            "type": "string"
          }
        ]
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[NamedRecoard]","no","(必須)","処理結果のデータ"
    "success.data.name","str","yes","(必須)","名前"
    "success.data.path","str","yes","(必須)","パス"
    "success.data.priority","int","yes","(必須)","優先度"
    "success.data.type","str","yes","(必須)","タイプ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


llm ( load ) : ``cmdbox -m llm -c load <Option>``
=================================================

- Loads LLM configuration.

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
    "--llmname <llmname>","str","","required","","","Specify the name of the LLM configuration to load."
    "--groups <groups>","str","multi","","","","Specify user groups used to authorize access to the LLM configuration."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "llmname": "string",
        "llmtype": "string",
        "llmprov": "string",
        "llmprojectid": "string",
        "llmsvaccountfile": "string",
        "llmlocation": "string",
        "llmapikey": "string",
        "llmapiversion": "string",
        "llmendpoint": "string",
        "llmmodel": "string",
        "llmseed": 0,
        "llmtemperature": 0.0,
        "llmsvaccountfile_data": {},
        "llmpriority": 0,
        "groups": [
          "string"
        ],
        "owner_groups": [
          "string"
        ],
        "user_groups": [
          "string"
        ]
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.llmname","str | null","no","null","LLM名"
    "success.llmtype","str | null","no","null","LLMタイプ"
    "success.llmprov","str | null","no","null","LLMプロバイダ"
    "success.llmprojectid","str | null","no","null","LLMプロジェクトID"
    "success.llmsvaccountfile","str | null","no","null","LLMサービスアカウントファイル"
    "success.llmlocation","str | null","no","null","LLMロケーション"
    "success.llmapikey","str | null","no","null","LLM APIキー"
    "success.llmapiversion","str | null","no","null","LLM APIバージョン"
    "success.llmendpoint","str | null","no","null","LLMエンドポイント"
    "success.llmmodel","str | null","no","null","LLMモデル名"
    "success.llmseed","int | null","no","null","LLMシード値"
    "success.llmtemperature","float | null","no","null","LLM温度パラメータ"
    "success.llmsvaccountfile_data","dict[str, any] | null","no","null","LLMサービスアカウントファイルデータ"
    "success.llmpriority","int | null","no","null","LLM優先度"
    "success.groups","list[str] | null","no","null","LLMに関連付けられたグループ"
    "success.owner_groups","list[str] | null","no","null","保存(edit/del)を許可するグループ"
    "success.user_groups","list[str] | null","no","null","使用(list/load)を許可するグループ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


llm ( metrics ) : ``cmdbox -m llm -c metrics <Option>``
=======================================================

- Retrieves metrics information for the specified LLM.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--llmname <llmname>","str","","required","","","Specify the name of the LLM configuration to get metrics for."
    "--groups <groups>","str","multi","","","","Specify user groups used to authorize access to the LLM configuration."
    "--format_raw <format_raw>","bool","","","False","","Return the metrics in raw Prometheus text format."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "llmname": "string",
        "endpoint": "string",
        "metrics_raw": "string",
        "metrics": [
          {
            "name": "string",
            "value": 0.0,
            "help_text": "string"
          }
        ],
        "gpu_load": 0.0,
        "requests_running": 0,
        "requests_waiting": 0,
        "tokens_generated_total": 0,
        "cache_usage_perc": 0.0
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.llmname","str | null","no","null","LLM名"
    "success.endpoint","str | null","no","null","メトリクスエンドポイント"
    "success.metrics_raw","str | null","no","null","生のPrometheusフォーマットメトリクス"
    "success.metrics","list[MetricValue] | null","no","null","パースされたメトリクス"
    "success.gpu_load","float | null","no","null","GPU負荷率（%）"
    "success.requests_running","int | null","no","null","実行中のリクエスト数"
    "success.requests_waiting","int | null","no","null","待機中のリクエスト数"
    "success.tokens_generated_total","int | null","no","null","生成されたトークンの合計数"
    "success.cache_usage_perc","float | null","no","null","キャッシュ使用率（%）"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


llm ( proxy_start ) : ``cmdbox -m llm -c proxy_start <Option>``
===============================================================

- Start LiteLLM Proxy service.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--data <data>","dir","","","C:\Users\hama\.cmdbox","","When omitted, `$HOME/.cmdbox` is used."
    "--proxy_allow_host <proxy_allow_host>","str","","","0.0.0.0","","Specify the bind host name. Default is `0.0.0.0`."
    "--proxy_listen_port <proxy_listen_port>","int","","","4000","","Specify the listening port of LiteLLM Proxy. Default is `4000`."
    "--proxy_workers <proxy_workers>","int","","","3","","Specify the number of workers for LiteLLM Proxy. Default is `3`."
    "--proxy_apikey <proxy_apikey>","str","","required","","","Specify the API key for LiteLLM Proxy. It must start with 'sk-'."
    "--llm_config <llm_config>","file","","","","","Directly specify the LiteLLM Proxy config file (config.yml). When specified, --llm options are ignored."
    "--llm <llm>","str","multi","","","","Specify multiple LLM configuration names to register to the proxy. The specified order is used as failover priority."
    "--num_retries <num_retries>","int","","","2","","Specify retry count for LiteLLM Router."
    "--request_timeout <request_timeout>","int","","","90","","Specify request timeout seconds for LiteLLM Proxy. 90 seconds recommended for production."
    "--allowed_fails <allowed_fails>","int","","","3","","Specify failure threshold for cooldown."
    "--cooldown_time <cooldown_time>","int","","","60","","Specify cooldown duration in seconds. 60 seconds recommended for production."
    "--connection_timeout <connection_timeout>","int","","","10","","Specify connection timeout seconds to LLM. Improves stability under high load."
    "--cache_responses <cache_responses>","bool","","","False","","Enable response caching. Improves performance and reduces load."
    "--max_retries_per_call <max_retries_per_call>","int","","","3","","Specify max retries per LLM call."
    "--enable_polling_logs <enable_polling_logs>","bool","","","False","","Enable polling logs."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "pid": 0,
        "config_path": "string",
        "proxy_allow_host": "string",
        "proxy_listen_port": 0,
        "proxy_workers": 0,
        "llm": [
          "string"
        ],
        "message": "string"
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.pid","int | null","no","null","起動したプロセスID"
    "success.config_path","str | null","no","null","生成したLiteLLM設定ファイルパス"
    "success.proxy_allow_host","str | null","no","null","待ち受けホスト"
    "success.proxy_listen_port","int | null","no","null","待ち受けポート"
    "success.proxy_workers","int | null","no","null","LiteLLM Proxy ワーカー数"
    "success.llm","list[str]","no","(必須)","登録したLLM設定名"
    "success.message","str | null","no","null","実行結果メッセージ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


llm ( proxy_stop ) : ``cmdbox -m llm -c proxy_stop <Option>``
=============================================================

- Stop LiteLLM Proxy service.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--data <data>","dir","","","C:\Users\hama\.cmdbox","","When omitted, `$HOME/.cmdbox` is used."
    "--proxy_listen_port <proxy_listen_port>","int","","","4000","","Specify the listening port of LiteLLM Proxy to stop. Default is `4000`."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "pid": 0,
        "proxy_listen_port": 0,
        "pid_path": "string",
        "message": "string"
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.pid","int | null","no","null","停止したプロセスID"
    "success.proxy_listen_port","int | null","no","null","停止対象ポート"
    "success.pid_path","str | null","no","null","PIDファイルパス"
    "success.message","str | null","no","null","実行結果メッセージ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


llm ( save ) : ``cmdbox -m llm -c save <Option>``
=================================================

- Saves LLM configuration.

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
    "--llmname <llmname>","str","","required","","","Specify the name of the LLM configuration to save."
    "--llmprov <llmprov>","str","","required",""," | azureopenai | openai | vertexai | ollama | proxy | custom","Specify llm provider."
    "--llmtype <llmtype>","str","","","chat","chat | embedding","Specify the type of the LLM configuration to save."
    "--llmprojectid <llmprojectid>","str","","","","","Specify the project ID for llm's provider connection."
    "--llmsvaccountfile <llmsvaccountfile>","file","","","","","Specifies the service account file for llm's provider connection."
    "--llmlocation <llmlocation>","str","","","","","Specifies the location for llm provider connections."
    "--llmapikey <llmapikey>","passwd","","","","","Specify API key for llm provider connection."
    "--llmapiversion <llmapiversion>","str","","","","","Specifies the API version for llm provider connections."
    "--llmendpoint <llmendpoint>","str","","","","","Specifies the endpoint for llm provider connections."
    "--llmmodel <llmmodel>","str","","required","","","Specifies the llm model."
    "--llmseed <llmseed>","int","","","13","","Specifies the seed value when using llm model."
    "--llmtemperature <llmtemperature>","float","","","0.1","","Specifies the temperature when using llm model."
    "--llmpriority <llmpriority>","int","","required","1","","Specifies the priority when using llm model. Lower values indicate higher priority."
    "--groups <groups>","str","multi","","","","Specify user groups used to authorize LLM configuration edit/save operations."
    "--owner_groups <owner_groups>","mlist","","","","","Specify the groups that are allowed to save (save/del) this LLM configuration. If omitted, all groups are allowed."
    "--user_groups <user_groups>","mlist","","","","","Specify the groups that are allowed to use this LLM configuration (list/load). If omitted, all groups are allowed."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
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
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


llm ( translation ) : ``cmdbox -m llm -c translation <Option>``
===============================================================

- Translates a list of words using LLM and returns the result in JSON format.
- Already-translated words are reused from cache.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","600","","Specify the maximum waiting time until the server responds."
    "--llmname <llmname>","str","","","","","Specify the name of the LLM configuration to use. If omitted, the LLM configuration with the highest priority is automatically selected."
    "--words <words>","str","multi","required","","","Specify the list of words to translate. Multiple values can be specified."
    "--target_lang <target_lang>","str","","required","en_US","","Specify the target language."
    "--nosave <nosave>","bool","","","False","True | False","Specify if the translation result should not be saved."
    "--groups <groups>","str","multi","","","","Specify user groups used to authorize translation operations."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "save_mode": "string",
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": {},
        "token_usage": {}
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | str | null","no","null","成功した場合の結果"
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","dict[str, str] | null","no","null","翻訳結果。{元の単語: 翻訳後の文字列} の辞書形式。"
    "success.token_usage","dict[str, any] | null","no","null","トークン使用量"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

