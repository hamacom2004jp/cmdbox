.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( rag mode )
****************************************************

- List of rag mode commands.


Delete RAG configuration. : `cmdbox -m rag -c del <Option>`
==============================================================================

- Deletes RAG (Retrieval-Augmented Generation) configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server."
    "--rag_name <name>","Yes","Specify the name of the RAG configuration to delete."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


List RAG configuration. : `cmdbox -m rag -c list <Option>`
==============================================================================

- Displays a list of saved RAG configurations.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--kwd <keyword>","","Partial match filter for RAG configuration names."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server. If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Load RAG configuration. : `cmdbox -m rag -c load <Option>`
==============================================================================

- Loads the settings for RAG (Retrieval-Augmented Generation).

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server."
    "--rag_name <name>","Yes","Specify the name of the RAG configuration to load."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Save RAG configuration. : `cmdbox -m rag -c save <Option>`
==============================================================================

- Saves the settings for RAG (Retrieval-Augmented Generation).

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server."
    "--rag_name <name>","Yes","Specify the name of the RAG configuration."
    "--rag_type <type>","Yes","Specify the type of RAG. Available values: `vector_pg`, `vector_sqlite`, `graph_n4j`, `graph_pg`."
    "--extract <name>","Yes","Specify the registered name for the Extract process used in RAG (multiple values allowed)."
    "--embed <name>","","If rag_type is vector, specify the registration name of the embed model."
    "--embed_vector_dim <dimension>","","Specify the vector dimension for embedding. Default: 256."
    "--savetype <pattern>","","Specify the storage pattern. `per_doc` :per document, `per_service` :per service, `add_only` :add only"
    "--vector_store_pghost <host>","","Specify the postgresql host for VecRAG storage. Default: localhost."
    "--vector_store_pgport <port>","","Specify the postgresql port for VecRAG storage. Default: 5432."
    "--vector_store_pguser <user>","","Specify the postgresql user for VecRAG storage. Default: postgres."
    "--vector_store_pgpass <password>","","Specify the postgresql password for VecRAG storage."
    "--vector_store_pgdbname <database>","","Specify the postgresql database name for VecRAG storage. Default: rag_db."
    "--graph_store_pghost <host>","","Specify the postgresql host for GraphRAG storage. Default: localhost."
    "--graph_store_pgport <port>","","Specify the postgresql port for GraphRAG storage. Default: 5432."
    "--graph_store_pguser <user>","","Specify the postgresql user for GraphRAG storage. Default: postgres."
    "--graph_store_pgpass <password>","","Specify the postgresql password for GraphRAG storage."
    "--graph_store_pgdbname <database>","","Specify the postgresql database name for GraphRAG storage. Default: rag_db."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Build RAG database. : `cmdbox -m rag -c build <Option>`
==============================================================================

- Builds the database based on the RAG (Retrieval-Augmented Generation) configuration.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server."
    "--rag_name <name>","Yes","Specify the name of the RAG configuration to build."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Register RAG data. : `cmdbox -m rag -c regist <Option>`
==============================================================================

- Executes the RAG (Retrieval-Augmented Generation) registration process.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server."
    "--rag_name <name>","Yes","Specify the name of the RAG configuration to use for registration."
    "--data <path>","Yes","Specify the data directory path. When omitted, `$HOME/.cmdbox` is used."
    "--signin_file <file>","Yes","Specify a file containing users and passwords for signin. Typically, specify `.cmdbox/user_list.yml`."
    "--groups <group>","Yes","Specify user groups allowed to execute commands (multiple values allowed)."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."
