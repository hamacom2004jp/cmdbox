.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( audit mode )
****************************************************

- List of audit mode commands.

Audit createdb : `cmdbox -m audit -c createdb <Option>`
==============================================================================

- Create a database to record audits.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--pg_host <host>","","Specify the postgresql host."
    "--pg_port <posrt>","","Specify the postgresql port."
    "--pg_user <user>","","Specify the postgresql user name."
    "--pg_password <passwd>","","Specify the postgresql password."
    "--pg_dbname <dbname>","","Specify the postgresql database name."
    "--new_pg_dbname <dbname>","","Specify a new postgresql database name."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

Audit delete : `cmdbox -m audit -c delete <Option>`
==============================================================================

- Delete the audit log.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."

    "--delete_audit_type <audit_type>","","Specifies the type of audit for the delete condition."
    "--delete_clmsg_id <clmsg_id>","","Specify the message ID of the client for the delete condition."
    "--delete_clmsg_sdate <clmsg_date>","","Specify the date and time (start) when the message occurred for the client in the delete condition."
    "--delete_clmsg_edate <clmsg_date>","","Specify the date and time (end) when the message occurred for the client in the delete condition."
    "--delete_clmsg_src <clmsg_src>","","Specifies the source of the message for the client in the delete condition; performs a LIKE search."
    "--delete_clmsg_user <clmsg_user>","","Specifies the user who generated the message for the client in the delete condition; performs a LIKE search."
    "--delete_clmsg_body <clmsg_body>","","Specifies the body of the client's message in the delete condition in dictionary format; performs a LIKE search."
    "--delete_clmsg_tag <clmsg_tag>","","Specifies the tag of the client's message in the delete condition."
    "--delete_svmsg_id <svmsg_id>","","Specify the message ID of the server for the delete condition."
    "--delete_svmsg_sdate <svmsg_date>","","Specify the date and time (start) when the message occurred for the server in the delete condition."
    "--delete_svmsg_edate <svmsg_date>","","Specify the date and time (end) when the message occurred for the server in the delete condition."

    "--pg_enabled","","Specify True if using the postgresql database server."
    "--pg_host <host>","","Specify the postgresql host."
    "--pg_port <posrt>","","Specify the postgresql port."
    "--pg_user <user>","","Specify the postgresql user name."
    "--pg_password <passwd>","","Specify the postgresql password."
    "--pg_dbname <dbname>","","Specify the postgresql database name."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

Audit search : `cmdbox -m audit -c search <Option>`
==============================================================================

- Search the audit log.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."

    "--select","","Specify the items to be retrieved. If not specified, all items are acquired."
    "--filter_audit_type <audit_type>","","Specifies the type of audit for the filter condition."
    "--filter_clmsg_id <clmsg_id>","","Specify the message ID of the client for the filter condition."
    "--filter_clmsg_sdate <clmsg_date>","","Specify the date and time (start) when the message occurred for the client in the filter condition."
    "--filter_clmsg_edate <clmsg_date>","","Specify the date and time (end) when the message occurred for the client in the filter condition."
    "--filter_clmsg_src <clmsg_src>","","Specifies the source of the message for the client in the filter condition; performs a LIKE search."
    "--filter_clmsg_user <clmsg_user>","","Specifies the user who generated the message for the client in the filter condition; performs a LIKE search."
    "--filter_clmsg_body <clmsg_body>","","Specifies the body of the client's message in the filter condition in dictionary format; performs a LIKE search."
    "--filter_clmsg_tag <clmsg_tag>","","Specifies the tag of the client's message in the filter condition."
    "--filter_svmsg_id <svmsg_id>","","Specify the message ID of the server for the filter condition."
    "--filter_svmsg_sdate <svmsg_date>","","Specify the date and time (start) when the message occurred for the server in the filter condition."
    "--filter_svmsg_edate <svmsg_date>","","Specify the date and time (end) when the message occurred for the server in the filter condition."
    "--sort <sort>","","Specify the sort item."
    "--offset <offset>","","Specifies the starting position of the row to be retrieved."
    "--limit <limit>","","Specifies the number of rows to retrieve."

    "--pg_enabled","","Specify True if using the postgresql database server."
    "--pg_host <host>","","Specify the postgresql host."
    "--pg_port <posrt>","","Specify the postgresql port."
    "--pg_user <user>","","Specify the postgresql user name."
    "--pg_password <passwd>","","Specify the postgresql password."
    "--pg_dbname <dbname>","","Specify the postgresql database name."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

Audit write : `cmdbox -m audit -c write <Option>`
==============================================================================

- Record the audit.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."

    "--audit_type <audit_type>","","Specifies the audit type."
    "--clmsg_id <clmsg_id>","","Specifies the message ID of the client. If omitted, uuid4 will be generated."
    "--clmsg_date <clmsg_date>","","Specifies the date and time the client message occurred. If omitted, the server's current date/time is used."
    "--clmsg_src <clmsg_src>","","Specifies the source of client messages. Usually specifies the name of a class that extends `cmdbox.app.feature.Feature` ."
    "--clmsg_user <clmsg_user>","","Specifies the user who generated the client message."
    "--clmsg_body <clmsg_body>","","Specifies the body of the client's message in dictionary format."
    "--clmsg_tag <clmsg_tag>","","Specifies the tag for the client's message. Specify to make it easier to search later."
    "--filter_svmsg_id <svmsg_id>","","Specify the message ID of the server for the filter condition."
    "--retention_period_days <days>","","Specify the number of days to keep the audit. If the number is less than or equal to 0, the audit will be kept indefinitely."

    "--pg_enabled","","Specify True if using the postgresql database server."
    "--pg_host <host>","","Specify the postgresql host."
    "--pg_port <posrt>","","Specify the postgresql port."
    "--pg_user <user>","","Specify the postgresql user name."
    "--pg_password <passwd>","","Specify the postgresql password."
    "--pg_dbname <dbname>","","Specify the postgresql database name."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."
