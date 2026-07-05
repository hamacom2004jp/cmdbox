.. -*- coding: utf-8 -*-

**********************************
Command Reference ( limiter mode )
**********************************

List of limiter mode commands.

limiter ( billing_calc ) : ``cmdbox -m limiter -c billing_calc <Option>``
=========================================================================

- Retrieves the list of plan configurations, calculates billing data based on evidences for each plan, and saves the results.
- Existing billing data files will not be overwritten.

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
    "--plan_name <plan_name>","str","","","","","Specify the plan identifier name to process. If omitted, all plans are targeted."

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
            "billing_file": "string",
            "plan_name": "string",
            "billing_limiter": "string",
            "last_reset": "string",
            "billing_amount": 0.0,
            "billing_currency": "string",
            "skipped": false
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
    "success.data","list[BillingResult] | null","no","null","請求データ処理結果一覧"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


limiter ( billing_load ) : ``cmdbox -m limiter -c billing_load <Option>``
=========================================================================

- Loads billing data by specifying a plan name.
- If last_reset is specified, returns billing data for that timing.
- If not specified, returns the latest billing data.

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
    "--plan_name <plan_name>","str","","required","","","Specify the plan name to load."
    "--last_reset <last_reset>","datetime","","","","","Specify the reset datetime (e.g. 2024-01-01T00:00:00 or 20240101_000000). If omitted, returns the latest billing data."

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
          "plan_name": "string",
          "plan_title": "string",
          "billing_limiter": "string",
          "billing_limiter_item": "string",
          "billing_type": "string",
          "billing_currency": "string",
          "billing_unit_price": 0.0,
          "billing_min_amount": 0.0,
          "billing_max_amount": 0.0,
          "billing_amount": 0.0,
          "last_reset": "string",
          "calc_datetime": "string",
          "evidence_filename": "string",
          "last_counter": {}
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
    "success.data","BillingData | list[BillingData] | null","no","null","請求データ（last_reset指定時は単一、未指定時は配列）"
    "success.data.plan_name","str | null","no","null","プランの識別名"
    "success.data.plan_title","str | null","no","null","プランのタイトル"
    "success.data.billing_limiter","str | null","no","null","請求対象のリミッター名"
    "success.data.billing_limiter_item","str | null","no","credits","請求計算に使用するリミッター項目"
    "success.data.billing_type","str | null","no","null","請求タイプ（period or metered）"
    "success.data.billing_currency","str | null","no","JPY","請求通貨"
    "success.data.billing_unit_price","float | null","no","null","請求単価"
    "success.data.billing_min_amount","float | null","no","null","請求の最小金額"
    "success.data.billing_max_amount","float | null","no","null","請求の最大金額"
    "success.data.billing_amount","float | null","no","null","計算された請求金額"
    "success.data.last_reset","str | null","no","null","リセット日時"
    "success.data.calc_datetime","str | null","no","null","請求計算日時"
    "success.data.evidence_filename","str | null","no","null","エビデンスファイル名"
    "success.data.last_counter","dict[str, any] | null","no","null","リセット時点のカウンター"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


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
    "--load_history <load_history>","bool","","","False","True | False","Specify whether to retrieve the history as well. If you set this to True, the history will also be retrieved."

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
          "last_reset": "string",
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
    "success.data.last_reset","str | null","no","null","最終リセット日時"
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


limiter ( evidences ) : ``cmdbox -m limiter -c evidences <Option>``
===================================================================

- Gets the list of evidence files for a limiter configuration.
- Evidence files are saved when the reset timing comes and contain information such as counter history.

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
    "--limiter_name <limiter_name>","str","","required","","","Specify the identifier name of the limiter configuration to get the evidence files for."
    "--scope <scope>","str","","required","server","client | current | server","Specify the scope. `client` refers to the client side, and `server` refers to the server side. `current` refers to the current directory."
    "--include_history <include_history>","bool","","","False","True | False","Specifies whether to include history information in the evidence file. If set to `True`, the history information is included in the output."

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
            "filename": "string",
            "filepath": "string",
            "limiter_name": "string",
            "last_counter": null,
            "last_reset": "string",
            "config": {},
            "history": [
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
    "success.data","list[Evidence] | null","no","null","処理結果のデータ"
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
            "limiter_title": "string",
            "target_mode": "string",
            "target_cmd": "string",
            "target_option": [
              {}
            ],
            "history_end": "string"
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
    "success.data.limiter_title","str | null","no","null","制限設定の表示名"
    "success.data.target_mode","str | null","no","null","対象コマンドのモード名"
    "success.data.target_cmd","str | null","no","null","対象コマンドのコマンド名"
    "success.data.target_option","list[dict[str, any]] | dict[str, any] | null","no","null","対象コマンドの条件"
    "success.data.history_end","str | null","no","null","カウンター記録の最終日時"
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
          "limiter_title": "string",
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
          "reset_datetime": "string",
          "reset_period_unit": "string",
          "reset_period_qty": 0,
          "max_history_interval": 0.0,
          "history_end": "string"
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
    "success.data.limiter_title","str | null","no","null","制限設定の表示名"
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
    "success.data.reset_datetime","str | null","no","null","カウンタリセット日時"
    "success.data.reset_period_unit","str | null","no","null","リセット単位（hour/day/month/year）"
    "success.data.reset_period_qty","int | null","no","null","リセット間隔の数量"
    "success.data.max_history_interval","float | null","no","null","履歴保存期間の最大間隔（秒）"
    "success.data.history_end","str | null","no","null","カウンター記録の最終日時"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


limiter ( plan_del ) : ``cmdbox -m limiter -c plan_del <Option>``
=================================================================

- Deletes a plan configuration.

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
    "--plan_name <plan_name>","str","","required","","","Specify the identifier name of the plan to delete."

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


limiter ( plan_list ) : ``cmdbox -m limiter -c plan_list <Option>``
===================================================================

- Lists registered plan configurations.

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
    "--kwd <kwd>","str","","","","","Specify the plan identifier name to search for. Searches for partial matches."

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
            "plan_title": "string",
            "plan_desc": "string",
            "billing_type": "string",
            "billing_limiter": "string",
            "billing_limiter_item": "string",
            "billing_currency": "string",
            "limiters": [
              "string"
            ],
            "plan_start": "string",
            "plan_end": "string"
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
    "success.data","list[PlanInfo] | null","no","null","プラン設定一覧"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


limiter ( plan_load ) : ``cmdbox -m limiter -c plan_load <Option>``
===================================================================

- Loads a plan configuration.

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
    "--plan_name <plan_name>","str","","required","","","Specify the identifier name of the plan to load."
    "--include_history <include_history>","bool","","","False","True | False","Specifies whether to include history information in the evidence file. If set to `True`, the history information is included in the output."

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
          "plan_name": "string",
          "plan_title": "string",
          "plan_desc": "string",
          "limiters": [
            {
              "limiter_name": "string",
              "limiter_title": "string",
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
              "reset_datetime": "string",
              "reset_period_unit": "string",
              "reset_period_qty": 0,
              "max_history_interval": 0.0,
              "counter": {}
            }
          ],
          "plan_start": "string",
          "plan_end": "string",
          "open_date": "string",
          "suspend_date": "string",
          "notice_date": "string",
          "billing_type": "string",
          "billing_period_unit": "string",
          "billing_period_qty": 0,
          "billing_limiter": "string",
          "billing_limiter_item": "string",
          "billing_min_amount": 0.0,
          "billing_max_amount": 0.0,
          "billing_unit_price": 0.0,
          "billing_currency": "string",
          "current_billing_qty": 0.0,
          "current_billing_amount": 0.0,
          "billing_data": [
            {
              "plan_name": "string",
              "plan_title": "string",
              "billing_limiter": "string",
              "billing_limiter_item": "string",
              "billing_type": "string",
              "billing_currency": "string",
              "billing_unit_price": 0.0,
              "billing_min_amount": 0.0,
              "billing_max_amount": 0.0,
              "billing_amount": 0.0,
              "last_reset": "string",
              "last_counter": {},
              "calc_datetime": "string",
              "evidence_filename": "string"
            }
          ]
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
    "success.data","Configure | null","no","null","プラン設定データ"
    "success.data.plan_name","str | null","no","null","プランの識別名"
    "success.data.plan_title","str | null","no","null","プランのタイトル"
    "success.data.plan_desc","str | null","no","null","プランの説明"
    "success.data.limiters","list[LimiterDetail] | null","no","null","このプランに含まれるリミッター設定の詳細情報"
    "success.data.plan_start","str | null","no","null","プラン適用開始日時"
    "success.data.plan_end","str | null","no","null","プラン適用終了日時"
    "success.data.open_date","str | null","no","null","ユーザー利用開始日時"
    "success.data.suspend_date","str | null","no","null","ユーザー利用停止日時"
    "success.data.notice_date","str | null","no","null","利用停止日の通知日時"
    "success.data.billing_type","str | null","no","null","請求タイプ（period or metered）"
    "success.data.billing_period_unit","str | null","no","null","請求期間単位"
    "success.data.billing_period_qty","int | null","no","null","請求期間数量"
    "success.data.billing_limiter","str | null","no","null","請求対象のリミッター名"
    "success.data.billing_limiter_item","str | null","no","credits","請求計算に使用するリミッター項目（registrations/count/time/input/process/output/credits）"
    "success.data.billing_min_amount","float | null","no","null","請求の最小金額"
    "success.data.billing_max_amount","float | null","no","null","請求の最大金額"
    "success.data.billing_unit_price","float | null","no","null","請求単価"
    "success.data.billing_currency","str | null","no","JPY","請求に使用する通貨（JPY, USD, EUR等）"
    "success.data.current_billing_qty","float | null","no","null","現在の請求対象量"
    "success.data.current_billing_amount","float | null","no","null","現在の請求金額"
    "success.data.billing_data","list[BillingData] | null","no","null","請求データリスト"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


limiter ( plan_save ) : ``cmdbox -m limiter -c plan_save <Option>``
===================================================================

- Adds or saves plan settings that bundle multiple limiter configurations.

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
    "--plan_name <plan_name>","str","","required","","","Specify the identifier name of the plan."
    "--plan_title <plan_title>","str","","","","","Specify the title of the plan."
    "--plan_desc <plan_desc>","text","","","","","Specify the description of the plan."
    "--limiters <limiters>","str","multi","required","","","Specify the limiter configuration names included in this plan."
    "--plan_start <plan_start>","datetime","","required","","","Specify the start datetime of the plan application (e.g. 2024-01-01T00:00:00)."
    "--plan_end <plan_end>","datetime","","","","","Specify the end datetime of the plan application (e.g. 2024-12-31T23:59:59). If omitted, no limit is applied."
    "--open_date <open_date>","datetime","","","","","Specify the start datetime for user access (e.g. 2024-01-01T00:00:00). If omitted, no limit is applied."
    "--suspend_date <suspend_date>","datetime","","","","","Specify the end datetime for user access (e.g. 2024-12-31T23:59:59). If omitted, no limit is applied."
    "--notice_date <notice_date>","datetime","","","","","Specify the datetime to notify about the suspension date before the suspend_date (e.g. 2024-12-20T00:00:00). If omitted, no notification is sent."
    "--billing_type <billing_type>","str","","required","period","period | metered","Specify the billing type. `period` for period-based billing, `metered` for metered billing."
    "--billing_period_unit <billing_period_unit>","str","","","","hour | day | month | year","Specify the billing period unit (for period-based billing). Choose from hour, day, month, year."
    "--billing_period_qty <billing_period_qty>","int","","","","","Specify the billing period quantity (for period-based billing)."
    "--billing_limiter <billing_limiter>","str","","","","","Specify the limiter name to be billed (for metered billing). Billing is based on the specified item of this limiter."
    "--billing_limiter_item <billing_limiter_item>","str","","","credits","registrations | count | time | input | process | output | credits","Specify the limiter item to be used for billing calculation (for metered billing). Choose from registrations, count, time, input, process, output, credits. Default is credits."
    "--billing_min_amount <billing_min_amount>","float","","","","","Specify the minimum billing amount (for metered billing)."
    "--billing_max_amount <billing_max_amount>","float","","","","","Specify the maximum billing amount (for metered billing)."
    "--billing_currency <billing_currency>","str","","","JPY","","Specify the currency used for billing. Default is JPY (Japanese Yen)."
    "--billing_unit_price <billing_unit_price>","float","","","","","Specify the billing unit price. For period-based billing, the price per period. For metered billing, the price per credit."

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
    "--limiter_title <limiter_title>","str","","","","","Specify the display name of the limiter configuration."
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
    "--reset_datetime <reset_datetime>","datetime","","required","","","Specify the date and time from which this restriction takes effect (e.g., 2024-06-01T00:00:00). The restriction counter will be reset based on the specified date and time."
    "--reset_period_unit <reset_period_unit>","str","","","","hour | day | month | year","Specify the reset unit based on reset_datetime. Select from hour, day, month, or year."
    "--reset_period_qty <reset_period_qty>","int","","","","","Specify the reset interval quantity. The counter is reset at intervals of this quantity in reset_period_unit units, starting from reset_datetime."
    "--max_history_interval <max_history_interval>","int","","required","2678400","3600 | 86400 | 2678400 | 31622400","Specify the maximum duration (in seconds) for which counter history will be retained. History older than the specified number of seconds will be deleted."
    "--history_end <history_end>","datetime","","","","","Specify the final datetime to record the counter (e.g. 2024-12-31T23:59:59). After this datetime, the counter will not be updated. If omitted, no limit is applied."

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
    "--filter_limiter_name <filter_limiter_name>","str","","","","","Filter by limiter name. If specified, returns results for that limiter only."
    "--include_history <include_history>","bool","","","False","True | False","Specifies whether to include history information in the evidence file. If set to `True`, the history information is included in the output."

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

