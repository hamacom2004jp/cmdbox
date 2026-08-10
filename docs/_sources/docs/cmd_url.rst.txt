.. -*- coding: utf-8 -*-

******************************
Command Reference ( url mode )
******************************

List of url mode commands.

url ( add ) : ``cmdbox -m url -c add <Option>``
===============================================

- Add a short URL.
- When target_url and period are specified, a url_id is generated and a url_id.json file is created in the .urls folder.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--base_url <base_url>","str","","required","","","Specify the base URL for the short URL."
    "--target_url <target_url>","str","","required","","","Specify the URL that the short URL will redirect to."
    "--period <period>","int","","","2592000","","Specify the validity period in seconds. Default is 1 month (2592000 seconds)."

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
        "data": {
          "url_id": "string",
          "short_url": "string",
          "target_url": "string",
          "base_url": "string",
          "period": 0,
          "saved_at": "string",
          "period_dt": "string",
          "file_path": "string",
          "msg": "string"
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
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","UrlData | null","no","null","URL情報"
    "success.data.url_id","str | null","no","null","生成されたURL ID"
    "success.data.short_url","str | null","no","null","生成された短縮URL"
    "success.data.target_url","str | null","no","null","リダイレクト先URL"
    "success.data.base_url","str | null","no","null","短縮URLのベースURL"
    "success.data.period","int | null","no","null","有効期限の秒数"
    "success.data.saved_at","str | null","no","null","保存日時"
    "success.data.period_dt","str | null","no","null","期限切れ日時"
    "success.data.file_path","str | null","no","null","作成されたJSONファイルのパス"
    "success.data.msg","str | null","no","null","処理結果のメッセージ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


url ( del ) : ``cmdbox -m url -c del <Option>``
===============================================

- Delete a short URL.
- Removes the JSON file for the specified url_id.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--url_id <url_id>","str","","required","","","Specify the url_id of the short URL to delete."

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
        "url_id": "string",
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
    "success.url_id","str | null","no","null","削除されたURL ID"
    "success.msg","str | null","no","null","処理結果のメッセージ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


url ( list ) : ``cmdbox -m url -c list <Option>``
=================================================

- Lists registered short URLs.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--kwd <kwd>","str","","","","","Specify the url_id to search for. Searches for partial matches."

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
            "url_id": "string",
            "short_url": "string",
            "target_url": "string",
            "base_url": "string",
            "period": 0,
            "saved_at": "string",
            "period_dt": "string"
          }
        ],
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
    "success.data","list[UrlInfo] | null","no","null","URL情報のリスト"
    "success.msg","str | null","no","null","処理結果のメッセージ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


url ( load ) : ``cmdbox -m url -c load <Option>``
=================================================

- Load a short URL.
- Retrieves information for the specified url_id.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--url_id <url_id>","str","","required","","","Specify the url_id of the short URL to load."

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
        "data": {
          "url_id": "string",
          "short_url": "string",
          "target_url": "string",
          "base_url": "string",
          "period": 0,
          "saved_at": "string",
          "period_dt": "string"
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
    "success.save_mode","str | null","no","null","保存モード"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","UrlData | null","no","null","URL情報"
    "success.data.url_id","str | null","no","null","URL ID"
    "success.data.short_url","str | null","no","null","生成された短縮URL"
    "success.data.target_url","str | null","no","null","リダイレクト先URL"
    "success.data.base_url","str | null","no","null","短縮URLのベースURL"
    "success.data.period","int | null","no","null","有効期限の秒数"
    "success.data.saved_at","str | null","no","null","保存日時"
    "success.data.period_dt","str | null","no","null","期限切れ日時"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.save_mode","str | null","no","null","保存モード"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.save_mode","str | null","no","null","保存モード"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

