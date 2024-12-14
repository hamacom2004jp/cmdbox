.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( client mode )
****************************************************

List of client mode commands.

client ( Copy File ) : `cmdbox -m client -c file_copy <Option>`
========================================================================================

- Copy the files under the data folder on the server side.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--from_path <source path>","","Specify the copy source path under the data folder of the inference server."
    "--to_path <destination path>","","Specify the path to copy under the data folder of the inference server."
    "--orverwrite","","Overwrites the file even if it exists at the copy destination."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

client ( Download File ) : `cmdbox -m client -c file_download <Option>`
==========================================================================================

- サーバー側のデータフォルダ配下のファイルをダウンロードします。
- `--svpath` で指定したファイルを `--download_file` で指定した場所に保存します。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <server-side path>","","Specify the directory path to get the list of files."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--rpath <client-request path>","","Specifies the request path. This value is returned in the response without any modification."
    "--download_file <client-side path>","","Specify the destination path of the client."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--img_thumbnail <Thumbnail size>","","Specifies the size in pixels of the thumbnail if the subject is an image."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

client ( List File ) : `cmdbox -m client -c file_list <Option>`
========================================================================================

- Get a list of files under the data folder.
- Returns the folder specified by `--svpath` and a list of the folders and files under it.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <server-side path>","","Specify the directory path to get the list of files."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--recursive","","Get a list of files recursively for a folder contained in the specified path."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

client ( Create Folder ) : `cmdbox -m client -c file_mkdir <Option>`
========================================================================================

- Create a new folder under the data folder.
- Creates the folder specified by `--svpath`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <server-side path>","","Specify the directory path to get the list of files."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

client ( Move File ) : `cmdbox -m client -c file_move <Option>`
========================================================================================

- Move the files under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--from_path <source path>","","Specify the source path under the data folder."
    "--to_path <destination path>","","Specify the destination path under the data folder."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

client ( Delete File ) : `cmdbox -m client -c file_remove <Option>`
========================================================================================

- Delete a file under the data folder.
- Deletes the file specified by `--svpath`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <server-side path>","","Specify the directory path to get the list of files."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

client ( Delete Folder ) : `cmdbox -m client -c file_rmdir <Option>`
========================================================================================

- Delete a folder under the data folder.
- Deletes the folder specified by `--svpath`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <server-side path>","","Specify the directory path to get the list of files."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

client ( Upload File ) : `cmdbox -m client -c file_upload <Option>`
========================================================================================

- Upload a file under the data folder.
- Upload the file specified by `--upload_file` to the location specified by `--svpath`.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--svpath <server-side path>","","Specify the directory path to get the list of files."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--upload_file <client-side path>","","Specify the source path of the client."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--mkdir","","If there is no in between folder, create one."
    "--orverwrite","","Overwrites the file even if it exists at the upload destination."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

client ( Server Info ) : `cmdbox -m client -c server_info <Option>`
========================================================================================

- Retrieve server information.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."
