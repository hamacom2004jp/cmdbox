.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( a2asv mode )
****************************************************

List of a2asv mode commands.

a2asv ( start ) : `cmdbox -m a2asv -c start <Option>`
========================================================================================

- Starts the A2A server.

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
    "--a2asv_listen_port <service port>","","If omitted, `8071` is used."
    "--ssl_a2asv_listen_port <service port>","","If omitted, `8423` is used."
    "--ssl_cert <SSL server certificate file>","","Specify the SSL server certificate file."
    "--ssl_key <SSL Server Private Key File>","","Specify the SSL server private key file."
    "--ssl_keypass <SSL Server Private Key Password>","","Specify the composite password for the SSL server private key file."
    "--ssl_ca_certs <SSL Server CA Certificate File>","","Specify the SSL server CA certificate file."
    "--signin_file <user list file>","","Specify a file containing users and passwords with which they can signin. If omitted, no authentication is required."
    "--gunicorn_workers <second>","","Specifies the number of gunicorn workers, valid only in Linux environment. If -1 or unspecified, the number of CPUs is used."
    "--gunicorn_timeout <second>","","Specify the timeout duration of the gunicorn worker in seconds."

a2asv ( stop ) : `cmdbox -m a2asv -c stop <Option>`
========================================================================================

- Stops the A2A server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data folder>","","When omitted, f`$HONE/.{version.__appid__}` is used."

