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
    "--llmname <llmname>","str","","required","","","Specify the name of the LLM configuration to load."
    "--msg_role <msg_role>","str","","required","user","user | assistant | system | function | tool","Specify the role of the message sender."
    "--msg_name <msg_name>","str","","","","","Specify the name of the message sender. Required if msg_role is `function` or `tool`."
    "--msg_text <msg_text>","text","","","","","Specify the content of the text to be sent."
    "--msg_text_system <msg_text_system>","text","","","次のユーザーの依頼にこたえてください。\n\n{{msg_text}}","","Specify the system prompt to send. Using `{{AAA}}` allows you to set the `AAA` parameter. Note that specifying `{{msg_text}}` sets the value of the `msg_text` option."
    "--msg_text_param <msg_text_param>","dict","multi","","","","Specify the parameters for the text."
    "--msg_image_url <msg_image_url>","str","","","","","Specify the URL of the image to be sent."
    "--scope <scope>","str","","","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--fwpath <fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--msg_audio <msg_audio>","file","","","","","Specify the content of the audio to be sent."
    "--msg_audio_format <msg_audio_format>","str","","","wav","wav | mp3 | ogg | flac","Specify the format of the audio to be sent."
    "--msg_video_url <msg_video_url>","str","","","","","Specify the URL of the video to be sent."
    "--msg_file_url <msg_file_url>","str","","","","","Specify the URL of the file to be sent."
    "--msg_file <msg_file>","file","","","","","Specify the content of the file to be sent."
    "--msg_file_mime <msg_file_mime>","str","","","application/pdf","","Specify the MIME type of the file to be sent."

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
        "data": null
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
    "success","Data | str | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","any | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
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
            "path": "string",
            "priority": 0
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
    "success.data","list[NamedRecoard]","no","(必須)","処理結果のデータ"
    "success.data.name","str","yes","(必須)","名前"
    "success.data.path","str","yes","(必須)","パス"
    "success.data.priority","int","yes","(必須)","優先度"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
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
        "llmname": "string",
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
        "llmpriority": 0
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
    "success.llmname","str | null","no","null","LLM名"
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
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
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
    "--llmprov <llmprov>","str","","required",""," | azureopenai | openai | vertexai | ollama","Specify llm provider."
    "--llmprojectid <llmprojectid>","str","","","","","Specify the project ID for llm's provider connection."
    "--llmsvaccountfile <llmsvaccountfile>","file","","","","","Specifies the service account file for llm's provider connection."
    "--llmlocation <llmlocation>","str","","","","","Specifies the location for llm provider connections."
    "--llmapikey <llmapikey>","passwd","","","","","Specify API key for llm provider connection."
    "--llmapiversion <llmapiversion>","str","","","","","Specifies the API version for llm provider connections."
    "--llmendpoint <llmendpoint>","str","","","","","Specifies the endpoint for llm provider connections."
    "--llmmodel <llmmodel>","str","","","text-multilingual-embedding-002","","Specifies the llm model."
    "--llmseed <llmseed>","int","","","13","","Specifies the seed value when using llm model."
    "--llmtemperature <llmtemperature>","float","","","0.1","","Specifies the temperature when using llm model."
    "--llmpriority <llmpriority>","int","","required","1","","Specifies the priority when using llm model. Lower values indicate higher priority."

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
    "--clear_cache <clear_cache>","bool","","","False","True | False","Specify if the translation cache should be cleared."

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
        "data": {}
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
    "success","Data | str | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","dict[str, str] | null","no","null","翻訳結果。{元の単語: 翻訳後の文字列} の辞書形式。"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

