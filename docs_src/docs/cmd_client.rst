.. -*- coding: utf-8 -*-

*********************************
Command Reference ( client mode )
*********************************

List of client mode commands.

client ( file_copy ) : ``cmdbox -m client -c file_copy <Option>``
=================================================================

- Copy the files under the data folder on the server side.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--from_path <from_path>","file","","required","","","Specify the copy source path under the data folder of the inference server."
    "--to_path <to_path>","file","","required","","","Specify the path to copy under the data folder of the inference server."
    "--from_fwpath <from_fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--to_fwpath <to_fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--from_rjpath <from_rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--to_rjpath <to_rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--orverwrite <orverwrite>","bool","","","False","True | False","Overwrites the copy even if it exists at the destination."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
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
        "path": "string",
        "to_path": "string",
        "from_path": "string",
        "ret_path": "string",
        "msg": "string"
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
    "success.path","str | null","no","null","パス"
    "success.to_path","str | null","no","null","コピー先・移動先のパス"
    "success.from_path","str | null","no","null","コピー元・移動元のパス"
    "success.ret_path","str | null","no","null","戻りのパス"
    "success.msg","str | null","no","null","処理結果のメッセージ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


client ( file_download ) : ``cmdbox -m client -c file_download <Option>``
=========================================================================

- Download a file under the data folder on the server.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","file","","required","/","","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--etag <etag>","str","","","","","Specify the ETag. If the ETag matches the file's ETag on the server, the file content will not be downloaded and an empty response will be returned."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--rpath <rpath>","str","","","","","Specifies the request path. This value is returned in the response without any modification."
    "--download_file <download_file>","file","","","","","Specify the destination path of the client."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--img_thumbnail <img_thumbnail>","float","","","0.0","","Specifies the size in pixels of the thumbnail if the subject is an image."
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
        "name": "string",
        "data": "string",
        "mime_type": "string",
        "etag": "string",
        "not_modified": false,
        "rpath": "string",
        "svpath": "string"
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
    "success.name","str | null","no","null","名前"
    "success.data","str | null","no","null","処理結果のデータ"
    "success.mime_type","str | null","no","null","MIMEタイプ"
    "success.etag","str | null","no","null","ETag"
    "success.not_modified","bool | null","no","null","未更新フラグ"
    "success.rpath","str | null","no","null","リクエストパス"
    "success.svpath","str | null","no","null","サーバーパス"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


client ( file_list ) : ``cmdbox -m client -c file_list <Option>``
=================================================================

- Get a list of files under the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","dir","","required","/","","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","file","multi","required","","","Specify a path to determine whether the specified path is out of bounds. If it is not under this path, it is interpreted as having specified this path."
    "--rjpath <rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--listregs <listregs>","str","","",".*","","Specify the regular expression conditions to list."
    "--recursive <recursive>","bool","","","False","True | False","Get a list of files recursively for a folder contained in the specified path."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","15","","Specify the maximum waiting time until the server responds."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {},
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","dict[str, any] | null","no","null","成功した場合の結果"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


client ( file_mkdir ) : ``cmdbox -m client -c file_mkdir <Option>``
===================================================================

- Create a new folder under the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","file","","required","/","","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--rjpath <rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
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
        "path": "string",
        "msg": "string"
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
    "success.path","str | null","no","null","パス"
    "success.msg","str | null","no","null","処理結果のメッセージ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


client ( file_move ) : ``cmdbox -m client -c file_move <Option>``
=================================================================

- Move the files under the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--from_path <from_path>","file","","required","","","Specify the source path under the data folder."
    "--to_path <to_path>","file","","required","","","Specify the destination path under the data folder."
    "--from_fwpath <from_fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--to_fwpath <to_fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--from_rjpath <from_rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--to_rjpath <to_rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
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
        "path": "string",
        "to_path": "string",
        "from_path": "string",
        "ret_path": "string",
        "msg": "string"
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
    "success.path","str | null","no","null","パス"
    "success.to_path","str | null","no","null","移動先・移動先のパス"
    "success.from_path","str | null","no","null","移動元・移動元のパス"
    "success.ret_path","str | null","no","null","戻りのパス"
    "success.msg","str | null","no","null","処理結果のメッセージ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


client ( file_remove ) : ``cmdbox -m client -c file_remove <Option>``
=====================================================================

- Delete a file under the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","file","","required","/","","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--rjpath <rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
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
        "path": "string",
        "msg": "string"
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
    "success.path","str | null","no","null","パス"
    "success.msg","str | null","no","null","処理結果のメッセージ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


client ( file_rmdir ) : ``cmdbox -m client -c file_rmdir <Option>``
===================================================================

- Delete a folder under the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","file","","required","/","","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--rjpath <rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
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
        "path": "string",
        "msg": "string"
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
    "success.path","str | null","no","null","パス"
    "success.msg","str | null","no","null","処理結果のメッセージ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


client ( file_upload ) : ``cmdbox -m client -c file_upload <Option>``
=====================================================================

- Upload a file under the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","file","","required","/","","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","file","multi","required","","","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--rjpath <rjpath>","file","multi","","","","If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."
    "--scope <scope>","str","","required","client","client | current | server","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--upload_file <upload_file>","file","","","","","Specify the source path of the client."
    "--client_data <client_data>","str","","","","","Specify the path of the data folder when local is referenced."
    "--mkdir <mkdir>","bool","","","False","True | False","If there is no in between folder, create one."
    "--orverwrite <orverwrite>","bool","","","False","True | False","Overwrites the file even if it exists at the upload destination."
    "--retry_count <retry_count>","int","","","3","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","int","","","5","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","int","","","15","","Specify the maximum waiting time until the server responds."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": "string",
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","str | null","no","null","成功した場合の結果"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


client ( http ) : ``cmdbox -m client -c http <Option>``
=======================================================

- Sends a request to the HTTP server and gets a response.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--url <url>","str","","required","","","Specify the URL to request."
    "--proxy <proxy>","str","","","no","no | yes","Specifies whether or not to send the received request parameters to the destination URL when invoked in web mode."
    "--send_method <send_method>","str","","required","GET","GET | POST | PUT | DELETE | PATCH | HEAD | OPTIONS","Specifies the request method."
    "--send_content_type <send_content_type>","str","","",""," | application/octet-stream | application/json | multipart/form-data","Specifies the Content-Type of the data to be sent."
    "--send_apikey <send_apikey>","passwd","","","","","Specify the API key to be used for authentication of the request destination."
    "--send_header <send_header>","dict","multi","","","","Specifies the request header."
    "--send_param <send_param>","dict","multi","","","","Specifies parameters to be sent."
    "--send_data <send_data>","text","","","","","Specifies the data to be sent."
    "--send_verify <send_verify>","bool","","","False","False | True","Specifies the timeout before a response is received."
    "--send_timeout <send_timeout>","int","","","30","","Specifies the timeout before a response is received."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": null,
      "warn": {},
      "error": {},
      "schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","any | null","no","null","成功した場合の結果"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


client ( server_info ) : ``cmdbox -m client -c server_info <Option>``
=====================================================================

- Retrieve server information.

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
        "svname": "string",
        "redis_host": "string",
        "redis_port": 0,
        "redis_password": "string",
        "data_dir": "string"
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
    "success.svname","str | null","no","null","サーバー名"
    "success.redis_host","str | null","no","null","Redisサーバーホスト"
    "success.redis_port","int | null","no","null","Redisサーバーポート"
    "success.redis_password","str | null","no","null","Redisサーバーパスワード"
    "success.data_dir","str | null","no","null","データディレクトリ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


client ( time ) : ``cmdbox -m client -c time <Option>``
=======================================================

- Displays the current time at the client side.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--timedelta <timedelta>","int","","","9","","Specify the number of hours of time difference."

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
        "data": "string",
        "timezone": "string",
        "timestamp": 0.0
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
    "success.data","str | null","no","null","処理結果のデータ"
    "success.timezone","str | null","no","null","タイムゾーン"
    "success.timestamp","float | null","no","null","タイムスタンプ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

