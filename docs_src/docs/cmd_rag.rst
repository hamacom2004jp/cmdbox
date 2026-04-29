.. -*- coding: utf-8 -*-

******************************
Command Reference ( rag mode )
******************************

List of rag mode commands.

rag ( build ) : ``cmdbox -m rag -c build <Option>``
===================================================

- We build the database based on the RAG (Retrieval-Augmented Generation) configuration.

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
    "--rag_name <rag_name>","required","Specify the name of the RAG configuration to build."

rag ( del ) : ``cmdbox -m rag -c del <Option>``
===============================================

- Delete the RAG (Retrieval-Augmented Generation) configuration.

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
    "--rag_name <rag_name>","required","Specify the name of the RAG configuration to delete."

rag ( list ) : ``cmdbox -m rag -c list <Option>``
=================================================

- Display a list of saved RAG settings.

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

rag ( load ) : ``cmdbox -m rag -c load <Option>``
=================================================

- Loads the settings for RAG (Retrieval-Augmented Generation).

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
    "--rag_name <rag_name>","required","Specify the name of the RAG configuration to load."

rag ( regist ) : ``cmdbox -m rag -c regist <Option>``
=====================================================

- Execute the RAG (Retrieval-Augmented Generation) registration process.

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
    "--rag_name <rag_name>","required","Specify the name of the RAG configuration to use for registration."
    "--data <data>","required","When omitted, `$HONE/.cmdbox` is used."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--groups <groups>","required","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."

rag ( save ) : ``cmdbox -m rag -c save <Option>``
=================================================

- Saves the settings for RAG (Retrieval-Augmented Generation).

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
    "--rag_name <rag_name>","required","Specify the name of the RAG configuration."
    "--rag_type <rag_type>","required","Specify the type of RAG."
    "--extract <extract>","required","Specify the registered name for the Extract process used in RAG. If no candidates exist, you must register a command in extract mode."
    "--embed <embed>","","If rag_type is vector, specify the registration name of the embed model."
    "--embed_vector_dim <embed_vector_dim>","","Specify the vector dimension for embedding."
    "--savetype <savetype>","","Specify the storage pattern. `per_doc` :per document, `per_service` :per service, `add_only` :add only"
    "--vector_store_pghost <vector_store_pghost>","","Specify the postgresql host for VecRAG storage."
    "--vector_store_pgport <vector_store_pgport>","","Specify the postgresql port for VecRAG storage."
    "--vector_store_pguser <vector_store_pguser>","","Specify the postgresql user for VecRAG storage."
    "--vector_store_pgpass <vector_store_pgpass>","","Specify the postgresql password for VecRAG storage."
    "--vector_store_pgdbname <vector_store_pgdbname>","","Specify the postgresql database name for VecRAG storage."
    "--graph_store_pghost <graph_store_pghost>","","Specify the postgresql host for GraphRAG storage."
    "--graph_store_pgport <graph_store_pgport>","","Specify the postgresql port for GraphRAG storage."
    "--graph_store_pguser <graph_store_pguser>","","Specify the postgresql user for GraphRAG storage."
    "--graph_store_pgpass <graph_store_pgpass>","","Specify the postgresql password for GraphRAG storage."
    "--graph_store_pgdbname <graph_store_pgdbname>","","Specify the postgresql database name for GraphRAG storage."

rag ( search ) : ``cmdbox -m rag -c search <Option>``
=====================================================

- Execute the RAG (Retrieval-Augmented Generation) search process.

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
    "--rag_name <rag_name>","required","Specify the name of the RAG configuration to use for registration."
    "--query <query>","","Specifies a search query."
    "--kcount <kcount>","required","Specify the number of search results. If filter conditions are specified, the results will be filtered from the number of results specified here."
    "--select <select>","","Specifies the items to be retrieved. If not specified, all items are returned."
    "--filter_origin_name <filter_origin_name>","","Specifies the origin_name of the filter condition."
    "--filter_dict <filter_dict>","","Specify arbitrary filter conditions, allowing multiple cmeta item names and values. Item values can be ambiguously searched by using `％`.  You can use the value of the query parameter by including the notation {args.query}."
    "--sort_dict <sort_dict>","","Specifies the sort conditions when no query is specified. Multiple cmeta field names and sort orders (`ASC` (ascending) or `DESC` (descending)) can be specified."
    "--data <data>","required","When omitted, `$HONE/.cmdbox` is used."
    "--signin_file <signin_file>","required","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--groups <groups>","required","Specifies that `signin_file`, if specified, should return the list of commands allowed for this user group."
