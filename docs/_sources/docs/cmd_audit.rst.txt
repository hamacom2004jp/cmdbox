.. -*- coding: utf-8 -*-

********************************
Command Reference ( audit mode )
********************************

List of audit mode commands.

audit ( createdb ) : ``cmdbox -m audit -c createdb <Option>``
=============================================================

- Create a database to record audits.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--pg_host <pg_host>","str","","required","pgsql","","Specify the postgresql host."
    "--pg_port <pg_port>","int","","required","5432","","Specify the postgresql port."
    "--pg_user <pg_user>","str","","required","pgsql","","Specify the postgresql user name."
    "--pg_password <pg_password>","passwd","","required","pgsql","","Specify the postgresql password."
    "--pg_dbname <pg_dbname>","str","","required","postgresql","","Specify the postgresql database name."
    "--new_pg_dbname <new_pg_dbname>","str","","required","audit","","Specify a new postgresql database name."
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","15","","Specify the maximum waiting time until the server responds."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": false,
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","bool | null","no","null","成功した場合の結果"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


audit ( delete ) : ``cmdbox -m audit -c delete <Option>``
=========================================================

- Delete the audit log.

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
    "--timeout <timeout>","int","","","15","","Specify the maximum waiting time until the server responds."
    "--pg_enabled <pg_enabled>","bool","","","False","True | False","Specify True if using the postgresql database server."
    "--pg_host <pg_host>","str","","","pgsql","","Specify the postgresql host."
    "--pg_port <pg_port>","int","","","5432","","Specify the postgresql port."
    "--pg_user <pg_user>","str","","","pgsql","","Specify the postgresql user name."
    "--pg_password <pg_password>","passwd","","","pgsql","","Specify the postgresql password."
    "--pg_dbname <pg_dbname>","str","","","audit","","Specify the postgresql database name."
    "--delete_audit_type <delete_audit_type>","str","","",""," | user | admin | system | auth | event","Specifies the type of audit for the delete condition."
    "--delete_clmsg_id <delete_clmsg_id>","str","","","","","Specify the message ID of the client for the delete condition."
    "--delete_clmsg_sdate <delete_clmsg_sdate>","datetime","","","","","Specify the date and time (start) when the message occurred for the client in the delete condition."
    "--delete_clmsg_edate <delete_clmsg_edate>","datetime","","","","","Specify the date and time (end) when the message occurred for the client in the delete condition."
    "--delete_clmsg_src <delete_clmsg_src>","str","","","","","Specifies the source of the message for the client in the delete condition; performs a LIKE search."
    "--delete_clmsg_title <delete_clmsg_title>","str","","","","","Specifies the message title of the client for the deletion condition; a LIKE search is performed."
    "--delete_clmsg_user <delete_clmsg_user>","str","","","","","Specifies the user who generated the message for the client in the delete condition; performs a LIKE search."
    "--delete_clmsg_body <delete_clmsg_body>","dict","multi","","","","Specifies the body of the client's message in the delete condition in dictionary format; performs a LIKE search."
    "--delete_clmsg_tag <delete_clmsg_tag>","str","multi","","","","Specifies the tag of the client's message in the delete condition."
    "--delete_svmsg_id <delete_svmsg_id>","str","","","","","Specify the message ID of the server for the delete condition."
    "--delete_svmsg_sdate <delete_svmsg_sdate>","datetime","","","","","Specify the date and time (start) when the message occurred for the server in the delete condition."
    "--delete_svmsg_edate <delete_svmsg_edate>","datetime","","","","","Specify the date and time (end) when the message occurred for the server in the delete condition."

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
        "msg": "string",
        "count": 0
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
    "success.msg","str | null","no","null","処理結果のメッセージ"
    "success.count","int | null","no","null","件数"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


audit ( search ) : ``cmdbox -m audit -c search <Option>``
=========================================================

- Search the audit log.

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
    "--timeout <timeout>","int","","","15","","Specify the maximum waiting time until the server responds."
    "--pg_enabled <pg_enabled>","bool","","","False","True | False","Specify True if using the postgresql database server."
    "--pg_host <pg_host>","str","","","pgsql","","Specify the postgresql host."
    "--pg_port <pg_port>","int","","","5432","","Specify the postgresql port."
    "--pg_user <pg_user>","str","","","pgsql","","Specify the postgresql user name."
    "--pg_password <pg_password>","passwd","","","pgsql","","Specify the postgresql password."
    "--pg_dbname <pg_dbname>","str","","","audit","","Specify the postgresql database name."
    "--select <select>","dict","multi","","","","Specify the items to be retrieved. If not specified, all items are acquired."
    "--select_date_format <select_date_format>","str","","",""," | %Y/%m/%d %H:%M | %Y/%m/%d %H | %Y/%m/%d | %Y/%m | %Y | %m | %u","Specifies the format of the date and time of the acquisition item."
    "--filter_audit_type <filter_audit_type>","str","","",""," | user | admin | system | auth | event","Specifies the type of audit for the filter condition."
    "--filter_clmsg_id <filter_clmsg_id>","str","","","","","Specify the message ID of the client for the filter condition."
    "--filter_clmsg_sdate <filter_clmsg_sdate>","datetime","","","","","Specify the date and time (start) when the message occurred for the client in the filter condition."
    "--filter_clmsg_edate <filter_clmsg_edate>","datetime","","","","","Specify the date and time (end) when the message occurred for the client in the filter condition."
    "--filter_clmsg_src <filter_clmsg_src>","str","","","","","Specifies the source of the message for the client in the filter condition; performs a LIKE search."
    "--filter_clmsg_title <filter_clmsg_title>","str","","","","","Specifies the message title of the client for the filter condition; a LIKE search is performed."
    "--filter_clmsg_user <filter_clmsg_user>","str","","","","","Specifies the user who generated the message for the client in the filter condition; performs a LIKE search."
    "--filter_clmsg_body <filter_clmsg_body>","dict","multi","","","","Specifies the body of the client's message in the filter condition in dictionary format; performs a LIKE search."
    "--filter_clmsg_tag <filter_clmsg_tag>","str","multi","","","","Specifies the tag of the client's message in the filter condition."
    "--filter_svmsg_id <filter_svmsg_id>","str","","","","","Specify the message ID of the server for the filter condition."
    "--filter_svmsg_sdate <filter_svmsg_sdate>","datetime","","","","","Specify the date and time (start) when the message occurred for the server in the filter condition."
    "--filter_svmsg_edate <filter_svmsg_edate>","datetime","","","","","Specify the date and time (end) when the message occurred for the server in the filter condition."
    "--groupby <groupby>","str","multi","",""," | audit_type | clmsg_id | clmsg_date | clmsg_src | clmsg_title | clmsg_user | clmsg_body | clmsg_tag | svmsg_id | svmsg_date","Specify grouping items."
    "--groupby_date_format <groupby_date_format>","str","","",""," | %Y/%m/%d %H:%M | %Y/%m/%d %H | %Y/%m/%d | %Y/%m | %Y | %m | %u","Specifies the format of the date and time of the grouping item."
    "--sort <sort>","dict","multi","","","","Specify the sort item."
    "--offset <offset>","int","","","0","","Specifies the starting position of the row to be retrieved."
    "--limit <limit>","int","","","100","","Specifies the number of rows to retrieve."
    "--csv <csv>","bool","","","False","False | True","Output search results in csv."

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
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[any] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


audit ( write ) : ``cmdbox -m audit -c write <Option>``
=======================================================

- Record the audit.

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
    "--timeout <timeout>","int","","","15","","Specify the maximum waiting time until the server responds."
    "--pg_enabled <pg_enabled>","bool","","","False","True | False","Specify True if using the postgresql database server."
    "--pg_host <pg_host>","str","","","pgsql","","Specify the postgresql host."
    "--pg_port <pg_port>","int","","","5432","","Specify the postgresql port."
    "--pg_user <pg_user>","str","","","pgsql","","Specify the postgresql user name."
    "--pg_password <pg_password>","passwd","","","pgsql","","Specify the postgresql password."
    "--pg_dbname <pg_dbname>","str","","","audit","","Specify the postgresql database name."
    "--client_only <client_only>","bool","","","False","True | False","Do not make connections to the server."
    "--audit_type <audit_type>","str","","required","","user | admin | system | auth | event","Specifies the audit type."
    "--clmsg_id <clmsg_id>","str","","","","","Specifies the message ID of the client. If omitted, uuid4 will be generated."
    "--clmsg_date <clmsg_date>","datetime","","","","","Specifies the date and time the client message occurred. If omitted, the server's current date/time is used."
    "--clmsg_src <clmsg_src>","str","","","","","Specifies the source of client messages. Usually specifies the name of a class that extends `cmdbox.app.feature.Feature` ."
    "--clmsg_title <clmsg_title>","str","","","","","Specifies the client message title. Usually specifies the command title."
    "--clmsg_user <clmsg_user>","str","","","","","SpecSpecifies the user who generated the client message."
    "--clmsg_body <clmsg_body>","dict","multi","","","","Specifies the body of the client's message in dictionary format."
    "--clmsg_tag <clmsg_tag>","str","multi","","","","Specifies the tag for the client's message. Specify to make it easier to search later."
    "--retention_period_days <retention_period_days>","int","","","365","","Specify the number of days to keep the audit. If the number is less than or equal to 0, the audit will be kept indefinitely."
    "--buffered_interval <buffered_interval>","int","","","30","","Specify the interval, in seconds, for buffering audit log writes."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": false,
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","bool | null","no","null","成功した場合の結果"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

