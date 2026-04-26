.. -*- coding: utf-8 -*-

********************************
Command Reference ( audit mode )
********************************

List of audit mode commands.

audit ( createdb ) : ``cmdbox -m audit -c createdb <Option>``
=============================================================

- Create a database to record audits.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--pg_host <pg_host>","required","Specify the postgresql host."
    "--pg_port <pg_port>","required","Specify the postgresql port."
    "--pg_user <pg_user>","required","Specify the postgresql user name."
    "--pg_password <pg_password>","required","Specify the postgresql password."
    "--pg_dbname <pg_dbname>","required","Specify the postgresql database name."
    "--new_pg_dbname <new_pg_dbname>","required","Specify a new postgresql database name."
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."

audit ( delete ) : ``cmdbox -m audit -c delete <Option>``
=========================================================

- Delete the audit log.

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
    "--pg_enabled <pg_enabled>","","Specify True if using the postgresql database server."
    "--pg_host <pg_host>","","Specify the postgresql host."
    "--pg_port <pg_port>","","Specify the postgresql port."
    "--pg_user <pg_user>","","Specify the postgresql user name."
    "--pg_password <pg_password>","","Specify the postgresql password."
    "--pg_dbname <pg_dbname>","","Specify the postgresql database name."
    "--delete_audit_type <delete_audit_type>","","Specifies the type of audit for the delete condition."
    "--delete_clmsg_id <delete_clmsg_id>","","Specify the message ID of the client for the delete condition."
    "--delete_clmsg_sdate <delete_clmsg_sdate>","","Specify the date and time (start) when the message occurred for the client in the delete condition."
    "--delete_clmsg_edate <delete_clmsg_edate>","","Specify the date and time (end) when the message occurred for the client in the delete condition."
    "--delete_clmsg_src <delete_clmsg_src>","","Specifies the source of the message for the client in the delete condition; performs a LIKE search."
    "--delete_clmsg_title <delete_clmsg_title>","","Specifies the message title of the client for the deletion condition; a LIKE search is performed."
    "--delete_clmsg_user <delete_clmsg_user>","","Specifies the user who generated the message for the client in the delete condition; performs a LIKE search."
    "--delete_clmsg_body <delete_clmsg_body>","","Specifies the body of the client's message in the delete condition in dictionary format; performs a LIKE search."
    "--delete_clmsg_tag <delete_clmsg_tag>","","Specifies the tag of the client's message in the delete condition."
    "--delete_svmsg_id <delete_svmsg_id>","","Specify the message ID of the server for the delete condition."
    "--delete_svmsg_sdate <delete_svmsg_sdate>","","Specify the date and time (start) when the message occurred for the server in the delete condition."
    "--delete_svmsg_edate <delete_svmsg_edate>","","Specify the date and time (end) when the message occurred for the server in the delete condition."

audit ( search ) : ``cmdbox -m audit -c search <Option>``
=========================================================

- Search the audit log.

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
    "--pg_enabled <pg_enabled>","","Specify True if using the postgresql database server."
    "--pg_host <pg_host>","","Specify the postgresql host."
    "--pg_port <pg_port>","","Specify the postgresql port."
    "--pg_user <pg_user>","","Specify the postgresql user name."
    "--pg_password <pg_password>","","Specify the postgresql password."
    "--pg_dbname <pg_dbname>","","Specify the postgresql database name."
    "--select <select>","","Specify the items to be retrieved. If not specified, all items are acquired."
    "--select_date_format <select_date_format>","","Specifies the format of the date and time of the acquisition item."
    "--filter_audit_type <filter_audit_type>","","Specifies the type of audit for the filter condition."
    "--filter_clmsg_id <filter_clmsg_id>","","Specify the message ID of the client for the filter condition."
    "--filter_clmsg_sdate <filter_clmsg_sdate>","","Specify the date and time (start) when the message occurred for the client in the filter condition."
    "--filter_clmsg_edate <filter_clmsg_edate>","","Specify the date and time (end) when the message occurred for the client in the filter condition."
    "--filter_clmsg_src <filter_clmsg_src>","","Specifies the source of the message for the client in the filter condition; performs a LIKE search."
    "--filter_clmsg_title <filter_clmsg_title>","","Specifies the message title of the client for the filter condition; a LIKE search is performed."
    "--filter_clmsg_user <filter_clmsg_user>","","Specifies the user who generated the message for the client in the filter condition; performs a LIKE search."
    "--filter_clmsg_body <filter_clmsg_body>","","Specifies the body of the client's message in the filter condition in dictionary format; performs a LIKE search."
    "--filter_clmsg_tag <filter_clmsg_tag>","","Specifies the tag of the client's message in the filter condition."
    "--filter_svmsg_id <filter_svmsg_id>","","Specify the message ID of the server for the filter condition."
    "--filter_svmsg_sdate <filter_svmsg_sdate>","","Specify the date and time (start) when the message occurred for the server in the filter condition."
    "--filter_svmsg_edate <filter_svmsg_edate>","","Specify the date and time (end) when the message occurred for the server in the filter condition."
    "--groupby <groupby>","","Specify grouping items."
    "--groupby_date_format <groupby_date_format>","","Specifies the format of the date and time of the grouping item."
    "--sort <sort>","","Specify the sort item."
    "--offset <offset>","","Specifies the starting position of the row to be retrieved."
    "--limit <limit>","","Specifies the number of rows to retrieve."
    "--csv <csv>","","Output search results in csv."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

audit ( write ) : ``cmdbox -m audit -c write <Option>``
=======================================================

- Record the audit.

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
    "--pg_enabled <pg_enabled>","","Specify True if using the postgresql database server."
    "--pg_host <pg_host>","","Specify the postgresql host."
    "--pg_port <pg_port>","","Specify the postgresql port."
    "--pg_user <pg_user>","","Specify the postgresql user name."
    "--pg_password <pg_password>","","Specify the postgresql password."
    "--pg_dbname <pg_dbname>","","Specify the postgresql database name."
    "--client_only <client_only>","","Do not make connections to the server."
    "--audit_type <audit_type>","required","Specifies the audit type."
    "--clmsg_id <clmsg_id>","","Specifies the message ID of the client. If omitted, uuid4 will be generated."
    "--clmsg_date <clmsg_date>","","Specifies the date and time the client message occurred. If omitted, the server's current date/time is used."
    "--clmsg_src <clmsg_src>","","Specifies the source of client messages. Usually specifies the name of a class that extends `cmdbox.app.feature.Feature` ."
    "--clmsg_title <clmsg_title>","","Specifies the client message title. Usually specifies the command title."
    "--clmsg_user <clmsg_user>","","SpecSpecifies the user who generated the client message."
    "--clmsg_body <clmsg_body>","","Specifies the body of the client's message in dictionary format."
    "--clmsg_tag <clmsg_tag>","","Specifies the tag for the client's message. Specify to make it easier to search later."
    "--retention_period_days <retention_period_days>","","Specify the number of days to keep the audit. If the number is less than or equal to 0, the audit will be kept indefinitely."
