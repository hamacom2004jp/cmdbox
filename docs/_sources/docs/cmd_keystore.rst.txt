.. -*- coding: utf-8 -*-

***********************************
Command Reference ( keystore mode )
***********************************

List of keystore mode commands.

keystore ( add ) : ``cmdbox -m keystore -c add <Option>``
=========================================================

- Add a key information to keystore.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data>","dir","","","C:\Users\hama\.cmdbox","","When omitted, `$HOME/.cmdbox` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","60","","Specify the maximum waiting time until the server responds."
    "--key_id <key_id>","str","","","","","Unique key identifier across all keys. If omitted, it will be auto-generated."
    "--key_name <key_name>","str","","required","","","Readable key name."
    "--key_provider <key_provider>","str","","","","","Key provider, usually a domain name. If omitted, `cmdbox` is used."
    "--key_type <key_type>","str","","required","apikey","apikey | signkey | enckey | cacert","Specify the type of key information to register."
    "--key_usage <key_usage>","str","multi","","","","Target commands (get_svcmd values) that can use this key. Multiple values allowed."
    "--key_value <key_value>","text","","","","","Actual key value. If omitted, a JWT token will be auto-generated for the current user."
    "--sign_key <sign_key>","file","","","","","Private key file for the public key certificate."
    "--sign_cert <sign_cert>","file","","","","","Public key certificate file."
    "--key_pass <key_pass>","passwd","","","","","Password for the private key."
    "--enc_key <enc_key>","str","","","","","Base64-encoded encryption key content."
    "--ca_cert <ca_cert>","file","","","","","CA certificate file."
    "--key_period_start <key_period_start>","datetime","","","","","Datetime when the key becomes valid. If omitted, effective immediately."
    "--key_period_end <key_period_end>","datetime","","","","","Datetime when the key expires. If omitted, no expiration."
    "--groups <groups>","str","multi","","","","Groups that can use this key. Multiple values allowed."
    "--owner <owner>","str","multi","","","","Owner user names of this key. Multiple values allowed."
    "--claims <claims>","dict","multi","","","","Claim requirements for this key."
    "--signin_file <signin_file>","file","","required",".cmdbox/user_list.yml","","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."

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
        "key_id": "string",
        "key_name": "string",
        "path": "string",
        "msg": "string"
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
    "success.key_id","str | null","no","null","キーID"
    "success.key_name","str | null","no","null","キー名"
    "success.path","str | null","no","null","保存先パス"
    "success.msg","str | null","no","null","処理結果メッセージ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


keystore ( del ) : ``cmdbox -m keystore -c del <Option>``
=========================================================

- Delete API key information from keystore.

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
    "--key_id <key_id>","str","","required","","","Specify the key ID to delete."
    "--key_name <key_name>","str","","required","","","If key name is specified, delete only the matching key."

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


keystore ( list ) : ``cmdbox -m keystore -c list <Option>``
===========================================================

- List API keys in keystore.

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
    "--kwd <kwd>","str","","","","","Specify key name to search. Partial match is used."

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
            "key_id": "string",
            "key_name": "string",
            "key_provider": "string",
            "key_type": "string",
            "key_usage": [
              "string"
            ],
            "key_period_start": "string",
            "key_period_end": "string",
            "path": "string"
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
    "success.data","list[KeyRecord]","no","(必須)","処理結果のデータ"
    "success.data.key_id","str","yes","(必須)","キーID"
    "success.data.key_name","str","yes","(必須)","キー名"
    "success.data.key_provider","str | null","no","null","キー発行者"
    "success.data.key_type","str | null","no","null","キー種別"
    "success.data.key_usage","list[str]","no","(必須)","利用対象コマンド"
    "success.data.key_period_start","str | null","no","null","使用開始日時"
    "success.data.key_period_end","str | null","no","null","使用終了日時"
    "success.data.path","str","yes","(必須)","保存先パス"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


keystore ( load ) : ``cmdbox -m keystore -c load <Option>``
===========================================================

- Load API key information from keystore.

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
    "--key_id <key_id>","str","","required","","","Specify the key ID to load."

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
        "key_id": "string",
        "key_name": "string",
        "key_provider": "string",
        "key_type": "string",
        "key_usage": [
          "string"
        ],
        "key_value": "string",
        "sign_key": "string",
        "sign_cert": "string",
        "key_pass": "string",
        "enc_key": "string",
        "ca_cert": "string",
        "key_period_start": "string",
        "key_period_end": "string",
        "groups": [
          "string"
        ],
        "owner": [
          "string"
        ],
        "claims": {}
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
    "success.key_id","str | null","no","null","キーID"
    "success.key_name","str | null","no","null","キー名"
    "success.key_provider","str | null","no","null","キー発行者"
    "success.key_type","str | null","no","null","キー種別"
    "success.key_usage","list[str] | null","no","null","利用対象コマンド"
    "success.key_value","str | null","no","null","キー実体"
    "success.sign_key","str | null","no","null","秘密鍵ファイル"
    "success.sign_cert","str | null","no","null","証明書ファイル"
    "success.key_pass","str | null","no","null","秘密鍵パスワード"
    "success.enc_key","str | null","no","null","暗号鍵"
    "success.ca_cert","str | null","no","null","CA証明書ファイル"
    "success.key_period_start","str | null","no","null","使用開始日時"
    "success.key_period_end","str | null","no","null","使用終了日時"
    "success.groups","list[str] | null","no","null","利用可能グループ"
    "success.owner","list[str] | null","no","null","所有者"
    "success.claims","dict[str, any] | null","no","null","要求クレーム"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

