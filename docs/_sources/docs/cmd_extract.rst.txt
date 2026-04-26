.. -*- coding: utf-8 -*-

**********************************
Command Reference ( extract mode )
**********************************

List of extract mode commands.

extract ( chunklet ) : ``cmdbox -m extract -c chunklet <Option>``
=================================================================

- Extracts text from the specified document file.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--fwpath <fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--loadpath <loadpath>","required","Specify the source file path."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--chunk_lang <chunk_lang>","","Specify the language of the text to be chunked. If `auto` is specified, the language will be automatically detected."
    "--chunk_max_token_counter <chunk_max_token_counter>","","Specify the maximum number of tokens for chunking text."
    "--chunk_max_tokens <chunk_max_tokens>","","Specify the maximum number of tokens for chunking text."
    "--chunk_max_sentences <chunk_max_sentences>","","Specify the maximum number of sentences (not characters) for chunking text."
    "--chunk_overlap_percent <chunk_overlap_percent>","","Specifies the overlap percentage of the chunk."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."

extract ( del ) : ``cmdbox -m extract -c del <Option>``
=======================================================

- Delete the extraction configuration.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--extract_name <extract_name>","required","Specify the name of the extraction configuration to delete."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."

extract ( list ) : ``cmdbox -m extract -c list <Option>``
=========================================================

- Display a list of saved extraction settings.

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
    "--kwd <kwd>","","Specify the name you want to search for. Searches for partial matches."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
    "--capture_stdout <capture_stdout>","","Available only in GUI mode. Captures standard output during command execution and displays it on the execution result screen."
    "--capture_maxsize <capture_maxsize>","","Available only in GUI mode. Specifies the maximum capture size of standard output when executing commands."

extract ( load ) : ``cmdbox -m extract -c load <Option>``
=========================================================

- Loads settings for extracting text from the specified file.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--extract_name <extract_name>","required","Specify the name of the extraction configuration to load."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."

extract ( pdfplumber ) : ``cmdbox -m extract -c pdfplumber <Option>``
=====================================================================

- Extracts text from the specified document file.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--scope <scope>","required","Specifies the scope to be referenced. When omitted, 'client' is used."
    "--loadpath <loadpath>","required","Specify the source file path."
    "--fwpath <fwpath>","required","Specify the path to determine whether the specified path is out of bounds. If it is not under this path, it will result in an error."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--chunk_table <chunk_table>","","Specifies how to chunk tables in the PDF file. `none` :do not chunk by table, `table` :by table, `row_with_header` :by row (with header)"
    "--chunk_table_header <chunk_table_header>","","Replaces existing header items by specifying the names of the table header items in the PDF file, from left to right."
    "--chunk_exclude <chunk_exclude>","","A regular expression specifying a string that should not be included in the chunk. If this specification is matched, embedding will not be performed."
    "--chunk_size <chunk_size>","","Specifies the chunk size."
    "--chunk_overlap <chunk_overlap>","","Specifies the overlap size of the chunk."
    "--chunk_separator <chunk_separator>","","Specifies the delimiter character for chunking."
    "--chunk_spage <chunk_spage>","","Specifies the starting page of the embedding range."
    "--chunk_epage <chunk_epage>","","Specifies the ending page of the embedding range."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."

extract ( save ) : ``cmdbox -m extract -c save <Option>``
=========================================================

- Saves settings for extracting text from the specified file.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--extract_name <extract_name>","required","Specify the name of the extraction configuration."
    "--extract_cmd <extract_cmd>","required","Specify the name of the extraction command setting."
    "--extract_type <extract_type>","required","Specify the type of extraction."
    "--scope <scope>","","Specify the reference scope. The available image types are `client` and `server`."
    "--client_data <client_data>","","Specify the path of the data folder when local is referenced."
    "--loadpath <loadpath>","required","Specify the source path."
    "--loadregs <loadregs>","required","Specifies a load regular expression pattern."
    "-o, --output_json <output_json>","","Specify the destination file for saving the processing result json."
    "-a, --output_json_append <output_json_append>","","Save the processing result json file by appending."
    "--stdout_log <stdout_log>","","Available only in GUI mode. Outputs standard output during command execution to Console log."
