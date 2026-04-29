.. -*- coding: utf-8 -*-

********************************
Command Reference ( a2asv mode )
********************************

List of a2asv mode commands.

a2asv ( start ) : ``cmdbox -m a2asv -c start <Option>``
=======================================================

- Start A2A server.

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
    "--a2asv_listen_port <a2asv_listen_port>","","If omitted, `8071` is used."
    "--ssl_a2asv_listen_port <ssl_a2asv_listen_port>","","If omitted, `8433` is used."
    "--ssl_cert <ssl_cert>","","Specify the SSL server certificate file."
    "--ssl_key <ssl_key>","","Specify the SSL server private key file."
    "--ssl_keypass <ssl_keypass>","","Specify the composite password for the SSL server private key file."
    "--ssl_ca_certs <ssl_ca_certs>","","Specify the SSL server CA certificate file."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--gunicorn_workers <gunicorn_workers>","","Specifies the number of gunicorn workers, valid only in Linux environment. If -1 or unspecified, the number of CPUs is used."
    "--gunicorn_timeout <gunicorn_timeout>","","Specify the timeout duration of the gunicorn worker in seconds."

a2asv ( stop ) : ``cmdbox -m a2asv -c stop <Option>``
=====================================================

- Stop A2A server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data>","","When omitted, `$HONE/.cmdbox` is used."
