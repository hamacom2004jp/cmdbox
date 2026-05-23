.. -*- coding: utf-8 -*-

*******************************
Command Reference ( test mode )
*******************************

List of test mode commands.

test ( gen_cli_docs ) : ``cmdbox -m test -c gen_cli_docs <Option>``
===================================================================

- Generates command reference RST files from detailed design documents.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--specs_dir <specs_dir>","dir","","","./Specifications/","","Specify the Specifications directory containing cli-command-specifications.json. Defaults to ./Specifications when omitted."
    "--docs_dir <docs_dir>","dir","","","./docs_src/docs/","","Specify the output directory for cmd_*.rst files. Defaults to ./docs_src/docs when omitted."
    "--mode_filter <mode_filter>","str","","","","","Filter generation targets by mode name. All modes are targeted when omitted. (e.g. server, client)"
    "--cmd_filter <cmd_filter>","mlist","","","","","Filter generation targets by command name. All commands are targeted when omitted. (e.g. list, start)"
    "--dry_run <dry_run>","bool","","","False","True | False","If True, does not actually write files but only shows what would be generated."

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
        "message": "string",
        "generated": [
          "string"
        ],
        "skipped": [
          "string"
        ],
        "dry_run": false
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
    "success.message","str | null","no","null","メッセージ"
    "success.generated","list[str] | null","no","null","生成されたファイルのリスト"
    "success.skipped","list[str] | null","no","null","スキップされたファイルまたはスキップ件数"
    "success.dry_run","bool | null","no","null","ドライランフラグ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


test ( gen_cli_spec ) : ``cmdbox -m test -c gen_cli_spec <Option>``
===================================================================

- Analyzes a feature package and generates CLI command detailed design documents.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--feature_package <feature_package>","str","","required","cmdbox.app.features.cli","","Specify the Python package name containing features.(e.g. cmdbox.app.features.cli, myapp.app.features.cli)"
    "--output_dir <output_dir>","dir","","","./Specifications/","","Specify the output directory for specifications.Defaults to ./Specifications when omitted."
    "--root_dir <root_dir>","dir","","","./","","Specify the project root directory used for computing relative source paths.Defaults to the current directory when omitted."
    "--prefix <prefix>","str","","","cmdbox_","","Specify the filename prefix of feature modules."
    "--clear_output_dir <clear_output_dir>","bool","","","False","True | False","If True, clears (deletes and recreates) the output directory before generating specifications when it already exists. If False, returns a warning when the output directory already exists."
    "--app_class <app_class>","str","","","cmdbox.app.app.CmdBoxApp","","Specify the module path of the application class.(e.g. myapp.app.MyApp) Defaults to cmdbox.app.app.CmdBoxApp when omitted."
    "--ver_module <ver_module>","str","","","cmdbox.version","","Specify the path of the version module.(e.g. myapp.version) Defaults to cmdbox.version when omitted."

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
        "message": "string",
        "output_dir": "string",
        "json_file": "string",
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
    "success.message","str | null","no","null","メッセージ"
    "success.output_dir","str | null","no","null","出力先ディレクトリ"
    "success.json_file","str | null","no","null","JSONファイルパス"
    "success.count","int | null","no","null","件数"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


test ( gen_test_spec ) : ``cmdbox -m test -c gen_test_spec <Option>``
=====================================================================

- Reads CLI command specification JSON and generates unit test specification documents.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--input_json <input_json>","file","","required","./Specifications/cli-command-specifications.json","","Specify the path to the input cli-command-specifications.json."
    "--output_dir <output_dir>","dir","","","./Specifications_forUnitTest/","","Specify the output directory for test specifications. Defaults to ./Specifications_forUnitTest when omitted."
    "--root_dir <root_dir>","dir","","","./","","Specify the project root directory used for referencing design document markdowns. Defaults to the current directory when omitted."
    "--clear_output_dir <clear_output_dir>","bool","","","False","True | False","If True, clears (deletes and recreates) the output directory before generating specifications when it already exists. If False, returns a warning when the output directory already exists."

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
        "message": "string",
        "output_dir": "string",
        "json_file": "string",
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
    "success.message","str | null","no","null","メッセージ"
    "success.output_dir","str | null","no","null","出力先ディレクトリ"
    "success.json_file","str | null","no","null","JSONファイルパス"
    "success.count","int | null","no","null","件数"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


test ( run_spec ) : ``cmdbox -m test -c run_spec <Option>``
===========================================================

- Runs tests based on the unit test specification JSON and reports results.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--mode_filter <mode_filter>","str","","","","","Filter test targets by mode name. Runs all modes when omitted. (e.g. server, test)"
    "--cmd_filter <cmd_filter>","mlist","","","","","Filter test targets by command name. Runs all commands when omitted. (e.g. list, start)"
    "--input_json <input_json>","file","","required","./Specifications_forUnitTest/cli-unit-test-specifications.json","","Specify the path to the input cli-unit-test-specifications.json."
    "--use_tempdir <use_tempdir>","bool","","","False","True | False","Replace output parameters with temporary directories during test execution. When True, avoids overwriting existing files."
    "--output_dir <output_dir>","dir","","","./Specifications_forUnitTest_results/","","Specify the output directory for test run results (JSON and MD). Defaults to ./Specifications_forUnitTest_results when omitted."
    "--clear_output_dir <clear_output_dir>","bool","","","False","True | False","If True, clears (deletes and recreates) the output directory before writing results when it already exists. If False (default), merges the current test case results into the existing result files, overwriting only the executed test cases."
    "--app_class <app_class>","str","","","cmdbox.app.app.CmdBoxApp","","Specify the module path of the application class to test. (e.g. myapp.app.MyApp) Defaults to cmdbox.app.app.CmdBoxApp when omitted."
    "--ver_module <ver_module>","str","","","cmdbox.version","","Specify the path of the version module. (e.g. myapp.version) Defaults to cmdbox.version when omitted."

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
          "message": "string",
          "commands": 0,
          "total": 0,
          "passed": 0,
          "failed": 0,
          "skipped": 0,
          "results": [
            {
              "mode": "string",
              "cmd": "string",
              "total": 0,
              "passed": 0,
              "failed": 0,
              "skipped": 0,
              "test_cases": [
                {
                  "id": "string",
                  "category": "string",
                  "focus": "string",
                  "input_pattern": "string",
                  "expected_status": "string",
                  "executed_at": "string",
                  "status": "string",
                  "input_values": {},
                  "ret_msg": [
                    null
                  ],
                  "actual_code": 0,
                  "actual_status": "string",
                  "actual_result": null,
                  "reason": null,
                  "expected_status_detail": null
                }
              ]
            }
          ],
          "output_dir": "<class 'pathlib.Path'>",
          "json_file": "<class 'pathlib.Path'>",
          "index_md_file": "<class 'pathlib.Path'>",
          "error_json_file": "<class 'pathlib.Path'>",
          "error_md_file": "<class 'pathlib.Path'>"
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
    "success.data","Summary | null","no","null","処理結果のデータ"
    "success.data.message","str | null","no","null","メッセージ"
    "success.data.commands","int | null","no","null","コマンド数"
    "success.data.total","int | null","no","null","合計件数"
    "success.data.passed","int | null","no","null","成功件数"
    "success.data.failed","int | null","no","null","失敗件数"
    "success.data.skipped","int | null","no","null","スキップされたファイルまたはスキップ件数"
    "success.data.results","list[ResultData] | null","no","null","結果のリスト"
    "success.data.output_dir","Path | str | null","no","null","出力先ディレクトリ"
    "success.data.json_file","Path | str | null","no","null","JSONファイルパス"
    "success.data.index_md_file","Path | str | null","no","null","インデックスMarkdownファイルパス"
    "success.data.error_json_file","Path | str | null","no","null","エラーJSONファイルパス"
    "success.data.error_md_file","Path | str | null","no","null","エラーMarkdownファイルパス"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

