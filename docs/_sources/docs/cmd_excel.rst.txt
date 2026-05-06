.. -*- coding: utf-8 -*-

********************************
Command Reference ( excel mode )
********************************

List of excel mode commands.

excel ( cell_details ) : ``cmdbox -m excel -c cell_details <Option>``
=====================================================================

- Get the details of the specified cell in the Excel file under the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--svpath <svpath>","file","","required","/","","Specify the directory path to get the list of files."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","15","","Specify the maximum waiting time until the server responds."
    "--formula_data_only <formula_data_only>","bool","","required","False","True | False","Specify whether to get only formula data. This option is valid if cached data exists."
    "--sheet_name <sheet_name>","str","","","","","Specify the sheet name to get the cell value.If omitted, the first sheet will be used."
    "--cell_name <cell_name>","str","multi","","","","Specify the cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_top_left <cell_top_left>","str","","","","","Specify the top-left cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_bottom_right <cell_bottom_right>","str","","","","","Specify the bottom-right cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--output_detail_format <output_detail_format>","str","","","json","json | text","Specify the output format. For example, `json`, `text`."

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
            "sheet_name": "string",
            "cellinfos": {}
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
    "success.data","list[Row] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


excel ( cell_search ) : ``cmdbox -m excel -c cell_search <Option>``
===================================================================

- Searches for the value in the specified cell of an Excel file located in the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--svpath <svpath>","file","","required","/","","Specify the directory path to get the list of files."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","15","","Specify the maximum waiting time until the server responds."
    "--formula_data_only <formula_data_only>","bool","","required","False","True | False","Specify whether to get only formula data. This option is valid if cached data exists."
    "--sheet_name <sheet_name>","str","","","","","Specify the sheet name to get the cell value.If omitted, all sheets will be used."
    "--cell_name <cell_name>","str","multi","","","","Specify the cell name to search for the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_top_left <cell_top_left>","str","","","","","Specify the top-left cell name to search for the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_bottom_right <cell_bottom_right>","str","","","","","Specify the bottom-right cell name to search for the cell value. For example, `A1`, `B2`, `R5987`."
    "--match_type <match_type>","str","","required","partial","full | partial | regex","Specifies the matching method for the value in the search cell. `full`: Exact match, `partial`: Partial match, `regex`: Regular expression."
    "--search_value <search_value>","str","","required","","","Specify the value to search for in the cell. The method of specification depends on `match_type`."
    "--output_cell_format <output_cell_format>","str","","","json","json | csv | md | html","Specify the output format. For example, `json`, `csv`、 `md`、 `html`."

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
            "sheet_name": "string",
            "cellinfos": {}
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
    "success.data","list[Row] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


excel ( cell_values ) : ``cmdbox -m excel -c cell_values <Option>``
===================================================================

- Retrieves or sets the value of a specified cell in an Excel file located within the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--svpath <svpath>","file","","required","/","","Specify the directory path to get the list of files."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","15","","Specify the maximum waiting time until the server responds."
    "--formula_data_only <formula_data_only>","bool","","required","False","True | False","Specify whether to get only formula data. This option is valid if cached data exists."
    "--sheet_name <sheet_name>","str","","","","","Specify the sheet name to get the cell value.If omitted, the first sheet will be used."
    "--cell_name <cell_name>","str","multi","","","","Specify the cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_top_left <cell_top_left>","str","","","","","Specify the top-left cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_bottom_right <cell_bottom_right>","str","","","","","Specify the bottom-right cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_value <cell_value>","dict","multi","","","","Set a value in a cell. Specify the cell's name and value. Cell names can be, for example, `A1`, `B2`, or `R5987`."
    "--output_cell_format <output_cell_format>","str","","","json","json | csv | md | html","Specify the output format. For example, `json`, `csv`、 `md`、 `html`."

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
            "sheet_name": "string",
            "cellinfos": {}
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
    "success.data","list[Row] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


excel ( sheet_list ) : ``cmdbox -m excel -c sheet_list <Option>``
=================================================================

- Retrieves the list of sheets in an Excel file located within the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--svpath <svpath>","file","","required","/","","Specify the directory path to get the list of files."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","15","","Specify the maximum waiting time until the server responds."

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
            "sheet_name": "string",
            "sheetinfos": {}
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
    "success.data","list[Row] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

