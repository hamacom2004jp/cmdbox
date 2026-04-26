.. -*- coding: utf-8 -*-

*******************************
Command Reference ( test mode )
*******************************

List of test mode commands.

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
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

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
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

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
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
