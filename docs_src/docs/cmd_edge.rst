.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( edge mode )
****************************************************

- List of edge mode commands.

Set the edge mode. : `cmdbox -m edge -c config <Option>`
=================================================================================

- Create the configuration necessary to run edge start.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--endpoint <url>","","Specify the URL of the endpoint."
    "--icon_path <path>","","Specify the path to the icon image."
    "--auth_type <type>","","Specifies the authentication method for endpoint connections."
    "--user <user_name>","","Specifies the user connecting to the endpoint."
    "--password <password>","","Specify the password for connecting to the endpoint."
    "--apikey <apikey>","","Specify the APIKEY to connect to the endpoint."
    "--oauth2 <provider>","","Connect to the endpoint using OAuth2 authentication."
    "--oauth2_port <port>","","Specifies the callback port when OAuth2 authentication is used. If omitted, `8091` is used."
    "--oauth2_client_id <client_id>","","Specifies the client ID when OAuth2 authentication is used."
    "--oauth2_client_secret <client_secret>","","Specifies the client secret when OAuth2 authentication is used."
    "--oauth2_timeout <sec>","","Specify the timeout period before OAuth2 authentication completes."
    "--data <path>","","When omitted, `$HONE/.{self.ver.__appid__}` is used."
    "--svcert_no_verify","","Do not verify server certificates during HTTPS requests."
    "--timeout <sec>","","Specifies the timeout period before the request completes."

Start Edge mode. : `cmdbox -m edge -c start <Option>`
=================================================================================

- Start Edge mode.
- In the case of windows, it will reside in the task tray.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <path>","","When omitted, `$HONE/.{self.ver.__appid__}` is used."

