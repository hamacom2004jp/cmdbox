.. -*- coding: utf-8 -*-

*******************************
Command Reference ( edge mode )
*******************************

List of edge mode commands.

edge ( config ) : ``cmdbox -m edge -c config <Option>``
=======================================================

- Set the edge mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--endpoint <endpoint>","","Specify the URL of the endpoint."
    "--icon_path <icon_path>","","Specify the path to the icon image."
    "--auth_type <auth_type>","","Specifies the authentication method for endpoint connections."
    "--user <user>","","Specifies the user connecting to the endpoint."
    "--password <password>","","Specify the password for connecting to the endpoint."
    "--apikey <apikey>","","Specify the APIKEY to connect to the endpoint."
    "--oauth2 <oauth2>","","Connect to the endpoint using OAuth2 authentication."
    "--oauth2_port <oauth2_port>","","Specifies the callback port when OAuth2 authentication is used. If omitted, `8091` is used."
    "--oauth2_tenant_id <oauth2_tenant_id>","","Specifies the tenant ID when OAuth2 authentication is used."
    "--oauth2_client_id <oauth2_client_id>","","Specifies the client ID when OAuth2 authentication is used."
    "--oauth2_client_secret <oauth2_client_secret>","","Specifies the client secret when OAuth2 authentication is used."
    "--oauth2_timeout <oauth2_timeout>","","Specify the timeout period before OAuth2 authentication completes."
    "--saml <saml>","","Connect to the endpoint using SAML authentication."
    "--saml_port <saml_port>","","Specifies the callback port when SAML authentication is used. If omitted, `8091` is used."
    "--saml_tenant_id <saml_tenant_id>","","Specifies the tenant ID when SAML authentication is used."
    "--saml_timeout <saml_timeout>","","Specify the timeout period before SAML authentication completes."
    "--data <data>","","When omitted, f`$HONE/.cmdbox` is used."
    "--svcert_no_verify <svcert_no_verify>","","Do not verify server certificates during HTTPS requests."
    "--timeout <timeout>","","Specifies the timeout period before the request completes."

edge ( start ) : ``cmdbox -m edge -c start <Option>``
=====================================================

- Start Edge mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data>","required","When omitted, f`$HONE/.cmdbox` is used."
