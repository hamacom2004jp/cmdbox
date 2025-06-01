.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( web mode )
****************************************************

- List of web mode commands.

Self-signed server certificate generation : `cmdbox -m web -c gencert <Option>`
=================================================================================

- Generate a self-signed certificate for simple implementation of SSL in web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--webhost <Server Name>","","Specify the host name to be specified as the CN (Common Name) of the self-signed certificate."
    "--output_cert <destination file>","","Specify the self-signed certificate file to be output.If omitted, the hostname specified in the `webhost option` .crt will be output."
    "--output_cert_format <format>","","Specifies the file format of the self-signed certificate to be output.'PEM' and 'DER' can be specified."
    "--output_key <destination file>","","Specifies the private key file of the self-signed certificate to be output.If omitted, the hostname specified in the `webhost option` .key will be output."
    "--output_key_format <format>","","Specifies the private key file format of the output self-signed certificate.'PEM' and 'DER' can be specified."
    "--overwrite","","Overwrites the self-signed certificate file to be output if it exists."

Password generation : `cmdbox -m web -c genpass <Option>`
=================================================================================

- Generates a password string that can be used in web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--pass_length <length>","","Specifies the length of the password."
    "--pass_count <count>","","Specify the number of passwords to be generated."
    "--use_alphabet <type>","","Specifies the type of alphabet used for the password. `notuse` , `upper` , `lower` , `both` can be specified."
    "--use_number <type>","","Specify the type of number to be used for the password. `notuse` , `use` can be specified."
    "--use_symbol <type>","","Specifies the type of symbol used in the password. `notuse` , `use` can be specified."
    "--similar <type>","","Specifies whether certain similar characters should be used. `exclude` , `include` can be specified."

Add Group : `cmdbox -m web -c group_add <Option>`
==============================================================================

- Add a group in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."
    "--group_id <Group ID>","required","Specify the group ID. Do not duplicate other groups."
    "--group_name <Group Name>","required","Specify a group name. Do not duplicate other groups."
    "--group_parent <parent group name>","","Specifies the parent group name."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."

Delete Group : `cmdbox -m web -c group_del <Option>`
==============================================================================

- Del a group in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."
    "--group_id <Group ID>","required","Specify the group ID. Do not duplicate other groups."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."

Edit Group : `cmdbox -m web -c group_edit <Option>`
==============================================================================

- Edit a group in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."
    "--group_id <Group ID>","required","Specify the group ID. Do not duplicate other groups."
    "--group_name <Group Name>","required","Specify a group name. Do not duplicate other groups."
    "--group_parent <parent group name>","","Specifies the parent group name."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."

List Group : `cmdbox -m web -c group_list <Option>`
==============================================================================

- Get a list of users in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."
    "--group_name <Group Name>","","Retrieved by specifying a group name. If omitted, all groups are retrieved."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."

Web Service Launch : `cmdbox -m web -c start <Option>`
==============================================================================

- Start Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."
    "--allow_host <IP to allow connection>","","If omitted, `0.0.0.0` is used."
    "--listen_port <service port>","","If omitted, `8081` is used."
    "--ssl_listen_port <service port>","","If omitted, `8443` is used."
    "--ssl_cert <SSL server certificate file>","","Specify the SSL server certificate file."
    "--ssl_key <SSL Server Private Key File>","","Specify the SSL server private key file."
    "--ssl_keypass <SSL Server Private Key Password>","","Specify the composite password for the SSL server private key file."
    "--ssl_ca_certs <SSL Server CA Certificate File>","","Specify the SSL server CA certificate file."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin. If omitted, no authentication is required."
    "--session_domain <domain>","","Specify the domain for which the signed-in user's session is valid."
    "--session_path <path>","","Specify the session timeout in seconds for signed-in users."
    "--session_secure","","Set the Secure flag for the signed-in user's session."
    "--session_timeout <second>","","Specify the session timeout in seconds for signed-in users."
    "--guvicorn_workers <second>","","Specifies the number of guvicorn workers, valid only in Linux environment. If -1 or unspecified, twice the number of CPUs is used."
    "--guvicorn_timeout <second>","","Specify the timeout duration of the guvicorn worker in seconds."
    "--client_only","","Do not make connections to the server."
    "--outputs_key <output key>","","Specify items to be displayed on the showimg and webcap screens. If omitted, all items are displayed."
    "--doc_root <document root path>","","Document root for custom files. URL mapping from the path of a folder-specified custom file with the path of doc_root removed."
    "--gui_html <gui.html file path>","","Specify `gui.html`. If omitted, the cmdbox built-in HTML file is used."
    "--filer_html <filer.html file path>","","Specify `filer.html`. If omitted, the cmdbox built-in HTML file is used."
    "--result_html <result.html file path>","","Specify `result.html`. If omitted, the cmdbox built-in HTML file is used."
    "--users_html <users.html file path>","","Specify `users.html`. If omitted, the cmdbox built-in HTML file is used."
    "--assets <Path to js and css files>","","Specify the asset file required when using html files."
    "--signin_html <signin.html file path>","","Specify `signin.html`. If omitted, the cmdbox built-in HTML file is used."
    "--agent <use>","","Specifies whether the agent is used. `no` or `use` can be specified."
    "--agent_name <name>","","Specifies the agent name."
    "--agent_description <description>","","Specify agent description."
    "--agent_instruction <instruction>","","Specifies the agent's system instructions."
    "--agent_session_store <session_store>","","Specify how the agent's session is to be saved."
    "--mcp_listen_port <service port>","","If omitted, `9081` is used."
    "--mcp_ssl_listen_port <service port>","","If omitted, `9443` is used."
    "--agent_pg_host <host>","","Specify the postgresql host."
    "--agent_pg_port <posrt>","","Specify the postgresql port."
    "--agent_pg_user <user>","","Specify the postgresql user name."
    "--agent_pg_password <passwd>","","Specify the postgresql password."
    "--agent_pg_dbname <dbname>","","Specify the postgresql database name."
    "--llmprov <provider>","","Specify llm provider."
    "--llmprojectid <projectid>","","Specify the project ID for llm's provider connection."
    "--llmsvaccountfile <file>","","Specifies the service account file for llm's provider connection."
    "--llmlocation <location>","","Specifies the location for llm provider connections."
    "--llmapikey <apikey>","","Specify API key for llm provider connection."
    "--llmapiversion <apiver>","","Specifies the API version for llm provider connections."
    "--llmendpoint <endpoint>","","Specifies the endpoint for llm provider connections."
    "--llmmodel <model>","","Specifies the llm model."
    "--llmseed <seed>","","Specifies the seed value when using llm model."
    "--llmtemperature <temperature>","","Specifies the temperature when using llm model."


Web Service Stops : `cmdbox -m web -c stop <Option>`
==============================================================================

- Stop Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."

Add User : `cmdbox -m web -c user_add <Option>`
==============================================================================

- Add a user in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."
    "--user_id <user ID>","required","Specify the user ID. Do not duplicate other users."
    "--user_name <username>","required","Specify a user name. Do not duplicate other users."
    "--user_pass <user password>","","Specify the user password."
    "--user_pass_hash <hash algorithm>","","Specifies the hash algorithm for user passwords.'oauth2', 'saml', 'plain', 'md5', 'sha1', and 'sha256' can be specified."
    "--user_email <user email>","","Specify the user email. Required when `user_pass_hash` is `oauth2` or `saml`."
    "--user_group <user group>","required","Specifies the groups to which the user belongs."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."

Delete User : `cmdbox -m web -c user_del <Option>`
==============================================================================

- Delete a user in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."
    "--user_id <user ID>","required","Specify the user ID. Do not duplicate other users."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."

Edit User : `cmdbox -m web -c user_edit <Option>`
==============================================================================

- Edit users in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."
    "--user_id <user ID>","required","Specify the user ID. Do not duplicate other users."
    "--user_name <username>","required","Specify a user name. Do not duplicate other users."
    "--user_pass <user password>","","Specify the user password."
    "--user_pass_hash <hash algorithm>","","Specifies the hash algorithm for user passwords.'oauth2', 'saml', 'plain', 'md5', 'sha1', and 'sha256' can be specified."
    "--user_email <user email>","","Specify the user email. Required when `user_pass_hash` is `oauth2` or `saml`."
    "--user_group <user group>","required","Specifies the groups to which the user belongs."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."

List User : `cmdbox -m web -c user_list <Option>`
==============================================================================

- Get a list of users in Web mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."
    "--user_name <username>","","Retrieved by specifying a user name. If omitted, all users are retrieved."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin."
