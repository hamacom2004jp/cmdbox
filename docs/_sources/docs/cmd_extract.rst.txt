.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( extract mode )
****************************************************

- List of extract mode commands.


Delete extraction configuration. : `cmdbox -m extract -c del <Option>`
==============================================================================

- Deletes extraction configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server."
    "--extract_name <name>","Yes","Specify the name of the extraction configuration to delete."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


List extraction configuration. : `cmdbox -m extract -c list <Option>`
==============================================================================

- Lists saved extraction configurations.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--kwd <keyword>","","Partial match filter for extraction configuration names."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Load extraction configuration. : `cmdbox -m extract -c load <Option>`
==============================================================================

- Loads extraction configuration from the specified file.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server."
    "--extract_name <name>","Yes","Specify the name of the extraction configuration to load."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Save extraction configuration. : `cmdbox -m extract -c save <Option>`
==============================================================================

- Saves settings for extracting text from the specified file.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server."
    "--extract_name <name>","Yes","Specify the name of the extraction configuration."
    "--extract_cmd <command name>","Yes","Specify the name of the extraction command setting."
    "--extract_type <type>","Yes","Specify the type of extraction. Available values: `file`."
    "--scope <scope>","","Specify the reference scope. Available scopes: `client`, `server`."
    "--client_data <path>","","Specify the path of the data folder when local is referenced."
    "--loadpath <path>","Yes","Specify the source path."
    "--loadregs <pattern>","Yes","Specifies a load regular expression pattern."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Extract text using pdfplumber. : `cmdbox -m extract -c pdfplumber <Option>`
==============================================================================

- Extracts text from the specified PDF document file using pdfplumber.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server."
    "--scope <scope>","","Specify the reference scope. Available scopes: `client`, `current`, `server`."
    "--loadpath <path>","Yes","Specify the source file path."
    "--client_data <path>","","Specify the path of the data folder when local is referenced."
    "--chunk_table <method>","","Specifies how to chunk tables in the PDF file. Available values: `none`, `table`, `row_with_header`. Default: `table`."
    "--chunk_table_header <name>","","Replaces existing header items by specifying the names of table header items (multiple values allowed)."
    "--chunk_exec <statement>","","Specify an exec statement for the contents of the chunk (multiple values allowed)."
    "--chunk_exclude <pattern>","","A regular expression specifying a string that should not be included in the chunk (multiple values allowed)."
    "--chunk_tag <tag>","","Specify tags to be registered in the chunk metadata (multiple values allowed)."
    "--chunk_size <size>","","Specifies the chunk size. Default: 1000."
    "--chunk_overlap <size>","","Specifies the overlap size of the chunk. Default: 50."
    "--chunk_separator <separator>","","Specifies the delimiter character for chunking (multiple values allowed)."
    "--chunk_in_metadata <metadata>","","Specifies metadata to be included in the contents of the chunk (multiple values allowed)."
    "--chunk_spage <page>","","Specifies the starting page of the embedding range. Default: 0."
    "--chunk_epage <page>","","Specifies the ending page of the embedding range. Default: 9999."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Extract text using chunklet. : `cmdbox -m extract -c chunklet <Option>`
==============================================================================

- Extracts text from the specified document file using chunklet.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server."
    "--scope <scope>","","Specify the reference scope. Available scopes: `client`, `current`, `server`."
    "--loadpath <path>","Yes","Specify the source file path."
    "--client_data <path>","","Specify the path of the data folder when local is referenced."
    "--chunk_lang <language>","","Specify the language of the text to be chunked. Available values: `auto`, `ja`, `en`. Default: `auto`."
    "--chunk_max_sentences <count>","","Specify the maximum number of sentences (not characters) for chunking text. Default: 4."
    "--chunk_overlap_percent <percent>","","Specifies the overlap percentage of the chunk. Default: 20."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."
