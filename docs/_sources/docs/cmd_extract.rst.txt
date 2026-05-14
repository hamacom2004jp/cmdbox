.. -*- coding: utf-8 -*-

**********************************
Command Reference ( extract mode )
**********************************

List of extract mode commands.

extract ( chunklet ) : ``cmdbox -m extract -c chunklet <Option>``
=================================================================

- Extracts text from the specified document file.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--scope <scope>","str","","required","current"," | client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--fwpath <fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--rjpath <rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--loadpath <loadpath>","file","","required","","","Specify the source file path."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--chunk_lang <chunk_lang>","str","","","auto","auto | ja | en","Specify the language of the text to be chunked. If `auto` is specified, the language will be automatically detected."
    "--chunk_max_token_counter <chunk_max_token_counter>","str","","","gpt-4o","","Specify the maximum number of tokens for chunking text."
    "--chunk_max_tokens <chunk_max_tokens>","int","","","1024","","Specify the maximum number of tokens for chunking text."
    "--chunk_max_sentences <chunk_max_sentences>","int","","","4","","Specify the maximum number of sentences (not characters) for chunking text."
    "--chunk_overlap_percent <chunk_overlap_percent>","int","","","20","","Specifies the overlap percentage of the chunk."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."

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
        "file": "<class 'pathlib.Path'>",
        "data": [
          {
            "content": "string",
            "metadata": {}
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
    "success.file","Path | str | null","no","null","ファイルパス"
    "success.data","list[ContentRecord] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


extract ( del ) : ``cmdbox -m extract -c del <Option>``
=======================================================

- Delete the extraction configuration.

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
    "--extract_name <extract_name>","str","","required","","","Specify the name of the extraction configuration to delete."

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


extract ( list ) : ``cmdbox -m extract -c list <Option>``
=========================================================

- Display a list of saved extraction settings.

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


extract ( load ) : ``cmdbox -m extract -c load <Option>``
=========================================================

- Loads settings for extracting text from the specified file.

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
    "--extract_name <extract_name>","str","","required","","","Specify the name of the extraction configuration to load."

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
        "extract_name": "string",
        "extract_type": "string",
        "extract_cmd": "string",
        "scope": "string",
        "client_data": "string",
        "loadpath": "string",
        "loadregs": "string"
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
    "success.extract_name","str | null","no","null","エクストラクト名"
    "success.extract_type","str | null","no","null","エクストラクトタイプ"
    "success.extract_cmd","str | null","no","null","エクストラクトコマンド"
    "success.scope","str | null","no","null","スコープ"
    "success.client_data","str | null","no","null","クライアントデータ"
    "success.loadpath","str | null","no","null","読み込みパス"
    "success.loadregs","str | null","no","null","読み込み正規表現"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


extract ( pdfplumber ) : ``cmdbox -m extract -c pdfplumber <Option>``
=====================================================================

- Extracts text from the specified document file.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server."
    "--scope <scope>","str","","required","current"," | client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--loadpath <loadpath>","file","","required","","","Specify the source file path."
    "--fwpath <fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--rjpath <rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--chunk_table <chunk_table>","str","","","table","none | table | row_with_header","Specifies how to chunk tables in the PDF file. `none` :do not chunk by table, `table` :by table, `row_with_header` :by row (with header)"
    "--chunk_table_header <chunk_table_header>","str","multi","","","","Replaces existing header items by specifying the names of the table header items in the PDF file, from left to right."
    "--chunk_exclude <chunk_exclude>","str","multi","","","","A regular expression specifying a string that should not be included in the chunk. If this specification is matched, embedding will not be performed."
    "--chunk_size <chunk_size>","int","","","1000","","Specifies the chunk size."
    "--chunk_overlap <chunk_overlap>","int","","","50","","Specifies the overlap size of the chunk."
    "--chunk_separator <chunk_separator>","str","multi","","","","Specifies the delimiter character for chunking."
    "--chunk_spage <chunk_spage>","int","","","0","","Specifies the starting page of the embedding range."
    "--chunk_epage <chunk_epage>","int","","","9999","","Specifies the ending page of the embedding range."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","120","","Specify the maximum waiting time until the server responds."

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
        "file": "<class 'pathlib.Path'>",
        "data": [
          {
            "content": "string",
            "metadata": {}
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
    "success.file","Path | str | null","no","null","ファイルパス"
    "success.data","list[ContentRecord] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


extract ( save ) : ``cmdbox -m extract -c save <Option>``
=========================================================

- Saves settings for extracting text from the specified file.

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
    "--extract_name <extract_name>","str","","required","","","Specify the name of the extraction configuration."
    "--extract_cmd <extract_cmd>","str","","required","","","Specify the name of the extraction command setting."
    "--extract_type <extract_type>","str","","required","file"," | file","Specify the type of extraction."
    "--scope <scope>","str","","","client"," | client | server","Specify the reference scope. The available image types are `client` and `server`."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--loadpath <loadpath>","dir","","required","","","Specify the source path."
    "--loadregs <loadregs>","str","","required",".*","","Specifies a load regular expression pattern."

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

