.. -*- coding: utf-8 -*-

**********************************
Command Reference ( limiter mode )
**********************************

List of limiter mode commands.

limiter ( counter ) : ``cmdbox -m limiter -c counter <Option>``
===============================================================

- Gets the counter for a limiter configuration.

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
    "--limiter_name <limiter_name>","str","","required","","","Specify the identifier name of the limiter configuration to get the counter for."
    "--scope <scope>","str","","required","server","client | current | server","Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory."
    "--load_history <load_history>","bool","","","False","True | False","Specify whether to retrieve the counter history as well. If you set this to True, the counter history will also be retrieved."

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
        "data": {
          "limiter_name": "string",
          "total_count": 0,
          "total_time": 0.0,
          "total_input": 0,
          "total_process": 0,
          "total_output": 0,
          "total_credits": 0,
          "total_registrations": 0,
          "last_refresh": "string",
          "last_update": "string"
        }
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
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","Counter | list[Counter] | null","no","null","処理結果のデータ"
    "success.data.limiter_name","str | null","no","null","制限設定の識別名"
    "success.data.total_count","int | null","no","null","実行回数"
    "success.data.total_time","float | null","no","null","実行総時間（秒）"
    "success.data.total_input","int | null","no","null","入力総バイト数"
    "success.data.total_process","int | null","no","null","処理総バイト数"
    "success.data.total_output","int | null","no","null","出力総バイト数"
    "success.data.total_credits","int | null","no","null","コマンドの最大クレジット数"
    "success.data.total_registrations","int | null","no","null","登録総数"
    "success.data.last_refresh","str | null","no","null","最終リセット日時"
    "success.data.last_update","str | null","no","null","最終更新日時"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


limiter ( del ) : ``cmdbox -m limiter -c del <Option>``
=======================================================

- Deletes a limiter configuration.

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
    "--limiter_name <limiter_name>","str","","required","","","Specify the identifier name of the limiter configuration to delete."
    "--scope <scope>","str","","required","server","client | current | server","Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory."

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
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


limiter ( list ) : ``cmdbox -m limiter -c list <Option>``
=========================================================

- Lists registered limiter configurations.

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
    "--kwd <kwd>","str","","","","","Specify the identifier name to search for. Searches for partial matches."
    "--scope <scope>","str","","required","server","client | current | server","Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory."

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
            "target_mode": "string",
            "target_cmd": "string",
            "target_option": [
              {}
            ]
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
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[LimiterRecord]","no","(必須)","処理結果のデータ"
    "success.data.name","str","yes","(必須)","制限設定の識別名"
    "success.data.target_mode","str | null","no","null","対象コマンドのモード名"
    "success.data.target_cmd","str | null","no","null","対象コマンドのコマンド名"
    "success.data.target_option","list[dict[str, any]] | dict[str, any] | null","no","null","対象コマンドの条件"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


limiter ( load ) : ``cmdbox -m limiter -c load <Option>``
=========================================================

- Loads a limiter configuration.

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
    "--limiter_name <limiter_name>","str","","required","","","Specify the identifier name of the limiter configuration to load."
    "--scope <scope>","str","","required","server","client | current | server","Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory."

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
        "data": {
          "scope": "string",
          "limiter_name": "string",
          "target_mode": "string",
          "target_cmd": "string",
          "target_option": [
            {}
          ],
          "max_registrations": 0,
          "max_total_count": 0,
          "max_total_time": 0.0,
          "max_total_input": 0,
          "max_total_process": 0,
          "max_total_output": 0,
          "max_total_credits": 0,
          "service_credits": 0,
          "exec_period_start": "string",
          "exec_period_end": "string",
          "refresh_datetime": "string",
          "refresh_interval": 0.0,
          "max_history_interval": 0.0
        }
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
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","Configure | null","no","null","処理結果のデータ"
    "success.data.scope","str | null","no","null","スコープ"
    "success.data.limiter_name","str | null","no","null","制限設定の識別名"
    "success.data.target_mode","str | null","no","null","対象コマンドのモード名"
    "success.data.target_cmd","str | null","no","null","対象コマンドのコマンド名"
    "success.data.target_option","list[dict[str, any]] | dict[str, any] | null","no","null","対象コマンドの条件"
    "success.data.max_registrations","int | null","no","null","登録最大数（又は登録最大サイズ）"
    "success.data.max_total_count","int | null","no","null","実行最大回数"
    "success.data.max_total_time","float | null","no","null","実行可能総時間（秒）"
    "success.data.max_total_input","int | null","no","null","入力総バイト数の上限"
    "success.data.max_total_process","int | null","no","null","処理総バイト数の上限"
    "success.data.max_total_output","int | null","no","null","出力総バイト数の上限"
    "success.data.max_total_credits","int | null","no","null","コマンドの最大クレジット数"
    "success.data.service_credits","int | null","no","null","サービスクレジット数"
    "success.data.exec_period_start","str | null","no","null","実行可能期間の開始日時"
    "success.data.exec_period_end","str | null","no","null","実行可能期間の終了日時"
    "success.data.refresh_datetime","str | null","no","null","カウンタリセット日時"
    "success.data.refresh_interval","float | null","no","null","カウンタリセット間隔（秒）"
    "success.data.max_history_interval","float | null","no","null","履歴保存期間の最大間隔（秒）"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


limiter ( save ) : ``cmdbox -m limiter -c save <Option>``
=========================================================

- Adds or saves quantitative restriction settings for command execution.

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
    "--limiter_name <limiter_name>","str","","required","","","Specify the identifier name of the limiter configuration."
    "--scope <scope>","str","","required","server","client | current | server","Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory."
    "--target_mode <target_mode>","str","","required","","","Specify the mode name of the target command to apply the restriction. If omitted, all modes are targeted."
    "--target_cmd <target_cmd>","str","","required","","","Specify the command name of the target command to apply the restriction. If omitted, all commands are targeted."
    "--target_option <target_option>","dict","multi","","","","Specify the conditions for the commands to which the restrictions apply in dictionary format. Specify the command option name as the key and the option value as the value."
    "--max_registrations <max_registrations>","int","","","","","Specify the maximum number of registrations (or maximum registration size). If omitted, no limit is applied."
    "--max_total_count <max_total_count>","int","","","","","Specify the maximum number of command executions. If omitted, no limit is applied."
    "--max_total_time <max_total_time>","int","","","","","Specify the total executable time in seconds for the command. If omitted, no limit is applied."
    "--max_total_input <max_total_input>","int","","","","","Specify the maximum total number of input bytes. If omitted, no limit is applied."
    "--max_total_process <max_total_process>","int","","","","","Specify the maximum total number of process bytes. If omitted, no limit is applied."
    "--max_total_output <max_total_output>","int","","","","","Specify the maximum total number of output bytes. If omitted, no limit is applied."
    "--max_total_credits <max_total_credits>","int","","","","","Specify the maximum number of credits. If omitted, no limit is applied."
    "--service_credits <service_credits>","int","","","","","Specify the number of service credits."
    "--exec_period_start <exec_period_start>","datetime","","","","","Specify the start datetime of the executable period for the command (e.g. 2024-01-01T00:00:00). If omitted, no limit is applied."
    "--exec_period_end <exec_period_end>","datetime","","","","","Specify the end datetime of the executable period for the command (e.g. 2024-12-31T23:59:59). If omitted, no limit is applied."
    "--refresh_datetime <refresh_datetime>","datetime","","","","","Specify the datetime to reset this restriction (e.g. 2024-06-01T00:00:00). The restriction counters are reset at the specified datetime. If omitted, no reset is performed."
    "--refresh_interval <refresh_interval>","int","","","","","Specify the interval in seconds after which this restriction is reset. The restriction counters are reset when the specified number of seconds has elapsed. If omitted, no reset is performed."
    "--max_history_interval <max_history_interval>","int","","required","2678400","","Specify the maximum duration (in seconds) for which counter history will be retained. History older than the specified number of seconds will be deleted."

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
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


limiter ( targets ) : ``cmdbox -m limiter -c targets <Option>``
===============================================================

- Gets the list of Features that inherit from LimitedFeature.

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
    "--scope <scope>","str","","required","server","client | current | server","Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory."
    "--filter_target_mode <filter_target_mode>","str","","","","","Filter by target mode. If specified, returns results for that mode only."
    "--filter_target_cmd <filter_target_cmd>","str","","","","","Filter by target command. If specified, returns results for that command only."

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
            "mode": "string",
            "cmd": "string",
            "limiters": [
              {}
            ]
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
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[TargetRecord]","no","(必須)","処理結果のデータ"
    "success.data.mode","str | list[str]","yes","(必須)","フィーチャーのモード"
    "success.data.cmd","str","yes","(必須)","フィーチャーのコマンド"
    "success.data.limiters","list[dict[str, any]]","no","(必須)","適合する制限設定の詳細内容リスト"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

