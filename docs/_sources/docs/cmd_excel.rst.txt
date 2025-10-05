.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( excel mode )
****************************************************

List of excel mode commands.

excel ( Cell Details ) : `cmdbox -m excel -c cell_details <Option>`
========================================================================================

- Get the details of the specified cell in the Excel file under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--svpath <server-side path>","","Specify the directory path to get the list of files."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."
    "--formula_data_only","","Specify whether to get only formula data. This option is valid if cached data exists."
    "--sheet_name <Sheet Name>","","Specify the sheet name to get the cell value.If omitted, the first sheet will be used."
    "--cell_name <Cell Name>","","Specify the cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_top_left <Cell Name>","","Specify the top-left cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_bottom_right <Cell Name>","","Specify the bottom-right cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--output_detail_format <format>","","Specify the output format. For example, `json`, `text`."


excel ( Cell Search ) : `cmdbox -m excel -c cell_search <Option>`
========================================================================================

- Searches for the value in the specified cell of an Excel file located in the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--svpath <server-side path>","","Specify the directory path to get the list of files."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."
    "--formula_data_only","","Specify whether to get only formula data. This option is valid if cached data exists."
    "--sheet_name <Sheet Name>","","Specify the sheet name to get the cell value.If omitted, the first sheet will be used."
    "--cell_name <Cell Name>","","Specify the cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_top_left <Cell Name>","","Specify the top-left cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_bottom_right <Cell Name>","","Specify the bottom-right cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--match_type <type>","","Specifies the matching method for the value in the search cell. `full`: Exact match, `partial`: Partial match, `regex`: Regular expression."
    "--search_value <value>","","Specify the value to search for in the cell. The method of specification depends on `match_type`."
    "--output_cell_format <format>","","Specify the output format. For example, `json`, `csv`、 `md`、 `html`."


excel ( Cell Values ) : `cmdbox -m excel -c cell_values <Option>`
========================================================================================

- Retrieves or sets the value of a specified cell in an Excel file located within the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <reference scope>","","Specifies the scope to be referenced. Possible image types are `client` , `current`, and `server`."
    "--svpath <server-side path>","","Specify the directory path to get the list of files."
    "--client_data <data folder>","","Specify the path of the data folder when local is referenced."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."
    "--formula_data_only","","Specify whether to get only formula data. This option is valid if cached data exists."
    "--sheet_name <Sheet Name>","","Specify the sheet name to get the cell value.If omitted, the first sheet will be used."
    "--cell_name <Cell Name>","","Specify the cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_top_left <Cell Name>","","Specify the top-left cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_bottom_right <Cell Name>","","Specify the bottom-right cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_value <value>","","Set a value in a cell. Specify the cell's name and value. Cell names can be, for example, `A1`, `B2`, or `R5987`."
    "--output_cell_format <format>","","Specify the output format. For example, `json`, `csv`、 `md`、 `html`."
