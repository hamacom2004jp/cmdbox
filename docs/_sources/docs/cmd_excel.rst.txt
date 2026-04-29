.. -*- coding: utf-8 -*-

********************************
Command Reference ( excel mode )
********************************

List of excel mode commands.

excel ( cell_details ) : ``cmdbox -m excel -c cell_details <Option>``
=====================================================================

- Get the details of the specified cell in the Excel file under the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--svpath <svpath>","required","Specify the directory path to get the list of files."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--formula_data_only <formula_data_only>","required","Specify whether to get only formula data. This option is valid if cached data exists."
    "--sheet_name <sheet_name>","","Specify the sheet name to get the cell value.If omitted, the first sheet will be used."
    "--cell_name <cell_name>","","Specify the cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_top_left <cell_top_left>","","Specify the top-left cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_bottom_right <cell_bottom_right>","","Specify the bottom-right cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--output_detail_format <output_detail_format>","","Specify the output format. For example, `json`, `text`."

excel ( cell_search ) : ``cmdbox -m excel -c cell_search <Option>``
===================================================================

- Searches for the value in the specified cell of an Excel file located in the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--svpath <svpath>","required","Specify the directory path to get the list of files."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--formula_data_only <formula_data_only>","required","Specify whether to get only formula data. This option is valid if cached data exists."
    "--sheet_name <sheet_name>","","Specify the sheet name to get the cell value.If omitted, all sheets will be used."
    "--cell_name <cell_name>","","Specify the cell name to search for the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_top_left <cell_top_left>","","Specify the top-left cell name to search for the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_bottom_right <cell_bottom_right>","","Specify the bottom-right cell name to search for the cell value. For example, `A1`, `B2`, `R5987`."
    "--match_type <match_type>","required","Specifies the matching method for the value in the search cell. `full`: Exact match, `partial`: Partial match, `regex`: Regular expression."
    "--search_value <search_value>","required","Specify the value to search for in the cell. The method of specification depends on `match_type`."
    "--output_cell_format <output_cell_format>","","Specify the output format. For example, `json`, `csv`、 `md`、 `html`."

excel ( cell_values ) : ``cmdbox -m excel -c cell_values <Option>``
===================================================================

- Retrieves or sets the value of a specified cell in an Excel file located within the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--svpath <svpath>","required","Specify the directory path to get the list of files."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--formula_data_only <formula_data_only>","required","Specify whether to get only formula data. This option is valid if cached data exists."
    "--sheet_name <sheet_name>","","Specify the sheet name to get the cell value.If omitted, the first sheet will be used."
    "--cell_name <cell_name>","","Specify the cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_top_left <cell_top_left>","","Specify the top-left cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_bottom_right <cell_bottom_right>","","Specify the bottom-right cell name to get the cell value. For example, `A1`, `B2`, `R5987`."
    "--cell_value <cell_value>","","Set a value in a cell. Specify the cell's name and value. Cell names can be, for example, `A1`, `B2`, or `R5987`."
    "--output_cell_format <output_cell_format>","","Specify the output format. For example, `json`, `csv`、 `md`、 `html`."

excel ( sheet_list ) : ``cmdbox -m excel -c sheet_list <Option>``
=================================================================

- Retrieves the list of sheets in an Excel file located within the data folder.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--svpath <svpath>","required","Specify the directory path to get the list of files."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
