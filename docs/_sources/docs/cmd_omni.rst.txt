.. -*- coding: utf-8 -*-

*******************************
Command Reference ( omni mode )
*******************************

List of omni mode commands.

omni ( pred ) : ``cmdbox -m omni -c pred <Option>``
===================================================

- Performs multimodal inference using the Omni model.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
