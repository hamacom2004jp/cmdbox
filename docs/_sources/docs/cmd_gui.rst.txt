.. -*- coding: utf-8 -*-

******************************
Command Reference ( gui mode )
******************************

List of gui mode commands.

gui ( start ) : ``cmdbox -m gui -c start <Option>``
===================================================

- Start GUI mode.

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

gui ( stop ) : ``cmdbox -m gui -c stop <Option>``
=================================================

- Stop GUI mode.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data>","","When omitted, `$HONE/.cmdbox` is used."
