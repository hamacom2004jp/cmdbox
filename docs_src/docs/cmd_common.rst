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
    "-h","","help display"
    "-u,--useopt <Option File to save>","Required if `-s` is specified.","Use the file that stores the options."
    "-s,--saveopt","","Save the specified options to the file specified by `-u`."
    "-d,--debug","","Starts in debug mode."
    "-f,--format","","Output the processing result in an easy-to-read format. If not specified, output in json format."
    "-o, --output_json <Destination file for processing result json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append","","Save the processing result json file by appending."
    "--stdout_log","","Available only in GUI mode. Outputs standard output to Console log when executing commands."
    "--capture_stdout","","Available in GUI mode only. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <size>","","Available in GUI mode only. Specifies the maximum capture size of standard output when executing commands."
    "-v, --version","","Display version"
    "-t,--tag <tag>","","Specify the tag for this command."
    "--clmsg_id <id>","","Specifies the message ID of the client. If omitted, uuid4 will be generated."
    "--description <description>","","Specifies a description of this command registration, used to help the Agent understand the use of this command."
    "--logsv","","Enables logsv. Logsv is a feature that synchronizes log file writing among multiple processes. If there is already an active process with logsv enabled, it will be ignored."
