.. -*- coding: utf-8 -*-

*********************************
Command Reference ( client mode )
*********************************

List of client mode commands.

client ( file_copy ) : ``cmdbox -m client -c file_copy <Option>``
=================================================================

- Copy the files under the data folder on the server side.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--from_path <from_path>","required","Specify the copy source path under the data folder of the inference server."
    "--to_path <to_path>","required","Specify the path to copy under the data folder of the inference server."
    "--from_fwpath <from_fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--to_fwpath <to_fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--orverwrite <orverwrite>","","Overwrites the copy even if it exists at the destination."
    "--scope <scope>","required","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."

client ( file_download ) : ``cmdbox -m client -c file_download <Option>``
=========================================================================

- Download a file under the data folder on the server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","required","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--etag <etag>","","Specify the ETag. If the ETag matches the file's ETag on the server, the file content will not be downloaded and an empty response will be returned."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--rpath <rpath>","","Specifies the request path. This value is returned in the response without any modification."
    "--download_file <download_file>","","Specify the destination path of the client."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--img_thumbnail <img_thumbnail>","","Specifies the size in pixels of the thumbnail if the subject is an image."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."

client ( file_list ) : ``cmdbox -m client -c file_list <Option>``
=================================================================

- Get a list of files under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","required","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","required","Specify a path to determine whether the specified path is out of bounds. If it is not under this path, it is interpreted as having specified this path."
    "--listregs <listregs>","","Specify the regular expression conditions to list."
    "--recursive <recursive>","","Get a list of files recursively for a folder contained in the specified path."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."

client ( file_mkdir ) : ``cmdbox -m client -c file_mkdir <Option>``
===================================================================

- Create a new folder under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","required","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."

client ( file_move ) : ``cmdbox -m client -c file_move <Option>``
=================================================================

- Move the files under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--from_path <from_path>","required","Specify the source path under the data folder."
    "--to_path <to_path>","required","Specify the destination path under the data folder."
    "--from_fwpath <from_fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--to_fwpath <to_fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."

client ( file_remove ) : ``cmdbox -m client -c file_remove <Option>``
=====================================================================

- Delete a file under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","required","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."

client ( file_rmdir ) : ``cmdbox -m client -c file_rmdir <Option>``
===================================================================

- Delete a folder under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","required","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."

client ( file_upload ) : ``cmdbox -m client -c file_upload <Option>``
=====================================================================

- Upload a file under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <svpath>","required","Specify the directory path to get the list of files."
    "--fwpath <fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--upload_file <upload_file>","","Specify the source path of the client."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--mkdir <mkdir>","","If there is no in between folder, create one."
    "--orverwrite <orverwrite>","","Overwrites the file even if it exists at the upload destination."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."

client ( http ) : ``cmdbox -m client -c http <Option>``
=======================================================

- Sends a request to the HTTP server and gets a response.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--url <url>","required","Specify the URL to request."
    "--proxy <proxy>","","Specifies whether or not to send the received request parameters to the destination URL when invoked in web mode."
    "--send_method <send_method>","required","Specifies the request method."
    "--send_content_type <send_content_type>","","Specifies the Content-Type of the data to be sent."
    "--send_apikey <send_apikey>","","Specify the API key to be used for authentication of the request destination."
    "--send_header <send_header>","","Specifies the request header."
    "--send_param <send_param>","","Specifies parameters to be sent."
    "--send_data <send_data>","","Specifies the data to be sent."
    "--send_verify <send_verify>","","Specifies the timeout before a response is received."
    "--send_timeout <send_timeout>","","Specifies the timeout before a response is received."

client ( server_info ) : ``cmdbox -m client -c server_info <Option>``
=====================================================================

- Retrieve server information.

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

client ( time ) : ``cmdbox -m client -c time <Option>``
=======================================================

- Displays the current time at the client side.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--timedelta <timedelta>","","Specify the number of hours of time difference."
