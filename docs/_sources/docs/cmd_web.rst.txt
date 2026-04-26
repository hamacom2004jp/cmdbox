.. -*- coding: utf-8 -*-

******************************
Command Reference ( web mode )
******************************

List of web mode commands.

web ( apikey_add ) : ``cmdbox -m web -c apikey_add <Option>``
=============================================================

- Add an ApiKey for a user in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--user_name <user_name>","required","Specify the target user name."
    "--apikey_name <apikey_name>","required","Specify the ApiKey name for this user."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( apikey_del ) : ``cmdbox -m web -c apikey_del <Option>``
=============================================================

- Del an ApiKey for a user in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--user_name <user_name>","required","Specify the target user name."
    "--apikey_name <apikey_name>","required","Specify the ApiKey name for this user."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( gencert ) : ``cmdbox -m web -c gencert <Option>``
=======================================================

- Generate a self-signed certificate for simple implementation of SSL in web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--webhost <webhost>","required","Specify the host name to be specified as the CN (Common Name) of the self-signed certificate."
    "--output_cert <output_cert>","","Specify the self-signed certificate file to be output.If omitted, the hostname specified in the `webhost option` .crt will be output."
    "--output_cert_format <output_cert_format>","","Specifies the file format of the self-signed certificate to be output."
    "--output_pkey <output_pkey>","","Specifies the public key file of the self-signed certificate to output. If omitted, the output will be in the `hostname specified in the `webhost option` .pkey."
    "--output_pkey_format <output_pkey_format>","","Specifies the file format of the public key of the self-signed certificate to be output."
    "--output_key <output_key>","","Specifies the private key file of the self-signed certificate to be output.If omitted, the hostname specified in the `webhost option` .key will be output."
    "--output_key_format <output_key_format>","","Specifies the private key file format of the output self-signed certificate."
    "--overwrite <overwrite>","","Overwrites the self-signed certificate file to be output if it exists."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( genpass ) : ``cmdbox -m web -c genpass <Option>``
=======================================================

- Generates a password string that can be used in web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--pass_length <pass_length>","","Specifies the length of the password."
    "--pass_count <pass_count>","","Specify the number of passwords to be generated."
    "--use_alphabet <use_alphabet>","","Specifies the type of alphabet used for the password. `notuse` , `upper` , `lower` , `both` can be specified."
    "--use_number <use_number>","","Specify the type of number to be used for the password. `notuse` , `use` can be specified."
    "--use_symbol <use_symbol>","","Specifies the type of symbol used in the password. `notuse` , `use` can be specified."
    "--similar <similar>","","Specifies whether certain similar characters should be used. `exclude` , `include` can be specified."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( group_add ) : ``cmdbox -m web -c group_add <Option>``
===========================================================

- Add a group in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--group_id <group_id>","required","Specify the group ID. Do not duplicate other groups."
    "--group_name <group_name>","required","Specify a group name. Do not duplicate other groups."
    "--group_parent <group_parent>","","Specifies the parent group name."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( group_del ) : ``cmdbox -m web -c group_del <Option>``
===========================================================

- Del a group in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--group_id <group_id>","required","Specify the group ID. Do not duplicate other groups."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( group_edit ) : ``cmdbox -m web -c group_edit <Option>``
=============================================================

- Edit a group in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--group_id <group_id>","required","Specify the group ID. Do not duplicate other groups."
    "--group_name <group_name>","required","Specify a group name. Do not duplicate other groups."
    "--group_parent <group_parent>","","Specifies the parent group name."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( group_list ) : ``cmdbox -m web -c group_list <Option>``
=============================================================

- Get a list of users in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--group_name <group_name>","","Retrieved by specifying a group name. If omitted, all groups are retrieved."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( start ) : ``cmdbox -m web -c start <Option>``
===================================================

- Start Web mode.

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
    "--listen_port <listen_port>","","If omitted, `8081` is used."
    "--ssl_listen_port <ssl_listen_port>","","If omitted, `8443` is used."
    "--ssl_cert <ssl_cert>","","Specify the SSL server certificate file."
    "--ssl_key <ssl_key>","","Specify the SSL server private key file."
    "--ssl_keypass <ssl_keypass>","","Specify the composite password for the SSL server private key file."
    "--ssl_ca_certs <ssl_ca_certs>","","Specify the SSL server CA certificate file."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--session_domain <session_domain>","","Specify the domain for which the signed-in user's session is valid."
    "--session_path <session_path>","","Specify the session timeout in seconds for signed-in users."
    "--session_secure <session_secure>","","Set the Secure flag for the signed-in user's session."
    "--session_timeout <session_timeout>","","Specify the session timeout in seconds for signed-in users."
    "--gunicorn_workers <gunicorn_workers>","","Specifies the number of gunicorn workers, valid only in Linux environment. If -1 or unspecified, the number of CPUs is used."
    "--gunicorn_timeout <gunicorn_timeout>","","Specify the timeout duration of the gunicorn worker in seconds."
    "--client_only <client_only>","","Do not make connections to the server."
    "--outputs_key <outputs_key>","","Specify items to be displayed on the showimg and webcap screens. If omitted, all items are displayed."
    "--doc_root <doc_root>","","Document root for custom files. URL mapping from the path of a folder-specified custom file with the path of doc_root removed."
    "--gui_html <gui_html>","","Specify `gui.html`. If omitted, the cmdbox built-in HTML file is used."
    "--filer_html <filer_html>","","Specify `filer.html`. If omitted, the cmdbox built-in HTML file is used."
    "--result_html <result_html>","","Specify `result.html`. If omitted, the cmdbox built-in HTML file is used."
    "--users_html <users_html>","","Specify `users.html`. If omitted, the cmdbox built-in HTML file is used."
    "--agent_html <agent_html>","","Specify `agent.html`. If omitted, the cmdbox built-in HTML file is used."
    "--assets <assets>","","Specify the asset file required when using html files."
    "--signin_html <signin_html>","","Specify `signin.html`. If omitted, the cmdbox built-in HTML file is used."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( stop ) : ``cmdbox -m web -c stop <Option>``
=================================================

- Stop Web mode.

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

web ( user_add ) : ``cmdbox -m web -c user_add <Option>``
=========================================================

- Add a user in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--user_id <user_id>","required","Specify the user ID. Do not duplicate other users."
    "--user_name <user_name>","required","Specify a user name. Do not duplicate other users."
    "--user_pass <user_pass>","","Specify the user password."
    "--user_pass_hash <user_pass_hash>","","Specifies the hash algorithm for user passwords."
    "--user_email <user_email>","","Specify the user email. Required when `user_pass_hash` is `oauth2` or `saml`."
    "--user_group <user_group>","required","Specifies the groups to which the user belongs."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( user_del ) : ``cmdbox -m web -c user_del <Option>``
=========================================================

- Delete a user in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--user_id <user_id>","required","Specify the user ID."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( user_edit ) : ``cmdbox -m web -c user_edit <Option>``
===========================================================

- Edit users in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--user_id <user_id>","required","Specify the user ID."
    "--user_name <user_name>","required","Specify a user name. Do not duplicate other users."
    "--user_pass <user_pass>","","Specify the user password."
    "--user_pass_hash <user_pass_hash>","","Specifies the hash algorithm for user passwords."
    "--user_email <user_email>","","Specify the user email. Required when `user_pass_hash` is `oauth2` or `saml`."
    "--user_group <user_group>","required","Specifies the groups to which the user belongs."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

web ( user_list ) : ``cmdbox -m web -c user_list <Option>``
===========================================================

- Get a list of users in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--user_name <user_name>","","Retrieved by specifying a user name. If omitted, all users are retrieved."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."
