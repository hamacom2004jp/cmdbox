.. -*- coding: utf-8 -*-

*******************************
Command Reference ( test mode )
*******************************

List of test mode commands.

test ( gen_cli_docs ) : ``cmdbox -m test -c gen_cli_docs <Option>``
===================================================================

- Generates command reference RST files from detailed design documents.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--specs_dir <specs_dir>","","Specify the Specifications directory containing cli-command-specifications.json. Defaults to ./Specifications when omitted."
    "--docs_dir <docs_dir>","","Specify the output directory for cmd_*.rst files. Defaults to ./docs_src/docs when omitted."
    "--mode_filter <mode_filter>","","Filter generation targets by mode name. All modes are targeted when omitted. (e.g. server, client)"
    "--cmd_filter <cmd_filter>","","Filter generation targets by command name. All commands are targeted when omitted. (e.g. list, start)"
    "--dry_run <dry_run>","","If True, does not actually write files but only shows what would be generated."

test ( gen_cli_spec ) : ``cmdbox -m test -c gen_cli_spec <Option>``
===================================================================

- Analyzes a feature package and generates CLI command detailed design documents.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--feature_package <feature_package>","required","Specify the Python package name containing features.(e.g. cmdbox.app.features.cli, myapp.app.features.cli)"
    "--output_dir <output_dir>","","Specify the output directory for specifications.Defaults to ./Specifications when omitted."
    "--root_dir <root_dir>","","Specify the project root directory used for computing relative source paths.Defaults to the current directory when omitted."
    "--prefix <prefix>","","Specify the filename prefix of feature modules."
    "--clear_output_dir <clear_output_dir>","","If True, clears (deletes and recreates) the output directory before generating specifications when it already exists. If False, returns a warning when the output directory already exists."
    "--app_class <app_class>","","Specify the module path of the application class.(e.g. myapp.app.MyApp) Defaults to cmdbox.app.app.CmdBoxApp when omitted."
    "--ver_module <ver_module>","","Specify the path of the version module.(e.g. myapp.version) Defaults to cmdbox.version when omitted."

test ( gen_test_spec ) : ``cmdbox -m test -c gen_test_spec <Option>``
=====================================================================

- Reads CLI command specification JSON and generates unit test specification documents.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--input_json <input_json>","required","Specify the path to the input cli-command-specifications.json."
    "--output_dir <output_dir>","","Specify the output directory for test specifications. Defaults to ./Specifications_forUnitTest when omitted."
    "--root_dir <root_dir>","","Specify the project root directory used for referencing design document markdowns. Defaults to the current directory when omitted."
    "--clear_output_dir <clear_output_dir>","","If True, clears (deletes and recreates) the output directory before generating specifications when it already exists. If False, returns a warning when the output directory already exists."

test ( run_spec ) : ``cmdbox -m test -c run_spec <Option>``
===========================================================

- Runs tests based on the unit test specification JSON and reports results.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--mode_filter <mode_filter>","","Filter test targets by mode name. Runs all modes when omitted. (e.g. server, test)"
    "--cmd_filter <cmd_filter>","","Filter test targets by command name. Runs all commands when omitted. (e.g. list, start)"
    "--input_json <input_json>","required","Specify the path to the input cli-unit-test-specifications.json."
    "--use_tempdir <use_tempdir>","","Replace output parameters with temporary directories during test execution. When True, avoids overwriting existing files."
    "--output_dir <output_dir>","","Specify the output directory for test run results (JSON and MD). Defaults to ./Specifications_forUnitTest_results when omitted."
    "--clear_output_dir <clear_output_dir>","","If True, clears (deletes and recreates) the output directory before writing results when it already exists. If False (default), merges the current test case results into the existing result files, overwriting only the executed test cases."
    "--app_class <app_class>","","Specify the module path of the application class to test. (e.g. myapp.app.MyApp) Defaults to cmdbox.app.app.CmdBoxApp when omitted."
    "--ver_module <ver_module>","","Specify the path of the version module. (e.g. myapp.version) Defaults to cmdbox.version when omitted."
