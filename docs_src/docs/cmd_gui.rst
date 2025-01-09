.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( gui mode )
****************************************************

- List of gui mode commands.

Management screen startup : `cmdbox -m gui -c start <Option>`
==============================================================================

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
    "--session_timeout <second>","","Specify the session timeout in seconds for signed-in users."
    "--client_only","","Do not make connections to the server."
    "--outputs_key <output key>","","Specify items to be displayed on the showimg and webcap screens. If omitted, all items are displayed."
    "--doc_root <document root path>","","Document root for custom files. URL mapping from the path of a folder-specified custom file with the path of doc_root removed."
    "--gui_html <gui.html file path>","","Specify `gui.html`. If omitted, the cmdbox built-in HTML file is used."
    "--filer_html <filer.html file path>","","Specify `filer.html`. If omitted, the cmdbox built-in HTML file is used."
    "--assets <Path to js and css files>","","Specify the asset file required when using html files."
    "--signin_html <signin.html file path>","","Specify `signin.html`. If omitted, the cmdbox built-in HTML file is used."

