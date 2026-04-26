.. -*- coding: utf-8 -*-

********************************
Command Reference ( mcpsv mode )
********************************

List of mcpsv mode commands.

mcpsv ( start ) : ``cmdbox -m mcpsv -c start <Option>``
=======================================================

- Start MCP server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data>","","When omitted, `$HONE/.cmdbox` is used."
    "--allow_host <allow_host>","","If omitted, `0.0.0.0` is used."
    "--mcpsv_listen_port <mcpsv_listen_port>","","If omitted, `8091` is used."
    "--ssl_mcpsv_listen_port <ssl_mcpsv_listen_port>","","If omitted, `8453` is used."
    "--ssl_cert <ssl_cert>","","Specify the SSL server certificate file."
    "--ssl_key <ssl_key>","","Specify the SSL server private key file."
    "--ssl_keypass <ssl_keypass>","","Specify the composite password for the SSL server private key file."
    "--ssl_ca_certs <ssl_ca_certs>","","Specify the SSL server CA certificate file."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--gunicorn_workers <gunicorn_workers>","","Specifies the number of gunicorn workers, valid only in Linux environment. If -1 or unspecified, the number of CPUs is used."
    "--gunicorn_timeout <gunicorn_timeout>","","Specify the timeout duration of the gunicorn worker in seconds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

mcpsv ( stop ) : ``cmdbox -m mcpsv -c stop <Option>``
=====================================================

- Stop MCP server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data>","","When omitted, `$HONE/.cmdbox` is used."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
