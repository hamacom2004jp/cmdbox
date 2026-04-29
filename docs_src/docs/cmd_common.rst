.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( Common )
****************************************************

This is a common option that can be specified for all commands.


Common Options
===============

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-m, --mode","","Specify the startup mode."
    "-c, --cmd","","Specify the command."
    "-h","","help display"
    "-v, --version","","Display version"
    "-u,--useopt <Option File to save>","Required if `-s` is specified.","Specify the file where the options are saved."
    "-s,--saveopt","","Save the specified options to the file specified by `-u`."
    "-d,--debug","","Starts in debug mode."
    "--debug_attach","","Specify whether to enable attaching to the debug process."
    "--debug_attach_port","","Specify the port number to attach to the debug process."
    "-f,--format","","Output the processing result in an easy-to-read format. If not specified, output in json format."
    "-t,--tag <tag>","","Specify the tag for this command."
    "--clmsg_id <id>","","Specifies the message ID of the client. If omitted, uuid4 will be generated."
    "--language <language>","","Specify the language at the time of command execution."
    "--description <description>","","Specifies a description of this command registration, used to help the Agent understand the use of this command."
    "--logsv","","Enables logsv. Logsv is a feature that synchronizes log file writing among multiple processes. If there is already an active process with logsv enabled, it will be ignored."
    "--output_raw","","If the operation is successful, the result is output to standard output in base64-decoded form. If multiple results are returned, only the first one is output."
    "-o, --output_json <Destination file for processing result json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append","","Save the processing result json file by appending."
    "--stdout_log","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <size>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
