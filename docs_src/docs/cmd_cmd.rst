.. -*- coding: utf-8 -*-

******************************
Command Reference ( cmd mode )
******************************

List of cmd mode commands.

cmd ( list ) : ``cmdbox -m cmd -c list <Option>``
=================================================

- Obtains a list of commands under the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--data <data>","dir","","required","C:\Users\hama\.cmdbox","","When omitted, `$HONE/.cmdbox` is used."
    "--kwd <kwd>","str","","","","","Specify the name you want to search for. Searches for partial matches."
    "--match_mode <match_mode>","str","","","","","Specify the mode condition of the command you want to search in. Searches for partial matches."
    "--match_cmd <match_cmd>","str","","","","","Specify the cmd condition of the command you want to search in. Searches for partial matches."
    "--match_opt <match_opt>","str","multi","","","","Specify the opt name of the command you want to search in."
    "--signin_file <signin_file>","file","","required",".cmdbox/user_list.yml","","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--groups <groups>","str","multi","","","","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."

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
            "title": "string",
            "mode": "string",
            "cmd": "string",
            "description": "string",
            "tag": [
              "string"
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
    "success","Data | list[CmdRecord] | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","list[CmdRecord] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


cmd ( load ) : ``cmdbox -m cmd -c load <Option>``
=================================================

- Obtains the contents of commands under the data folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--data <data>","dir","","required","C:\Users\hama\.cmdbox","","When omitted, `$HONE/.cmdbox` is used."
    "--signin_file <signin_file>","file","","required",".cmdbox/user_list.yml","","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--groups <groups>","str","multi","","","","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."
    "--cmd_title <cmd_title>","str","","required","","","Specify the name of the command to be read."

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
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","dict[str, any] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

