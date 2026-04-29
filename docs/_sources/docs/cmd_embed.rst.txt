.. -*- coding: utf-8 -*-

********************************
Command Reference ( embed mode )
********************************

List of embed mode commands.

embed ( del ) : ``cmdbox -m embed -c del <Option>``
===================================================

- Delete the embed model configuration that generates feature data from input information.

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
    "--embed_name <embed_name>","required","Specify the registration name of the embed model to delete."

embed ( embedding ) : ``cmdbox -m embed -c embedding <Option>``
===============================================================

- Generates feature data from input information.

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
    "--embed_name <embed_name>","required","Specify the registration name of the embed model."
    "--original_data <original_data>","required","Specify the original data to generate feature vectors."

embed ( list ) : ``cmdbox -m embed -c list <Option>``
=====================================================

- Display a list of saved embedding model settings.

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

embed ( load ) : ``cmdbox -m embed -c load <Option>``
=====================================================

- Loads the settings for the embedding model that generates feature data from input information.

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
    "--embed_name <embed_name>","required","Specify the registration name of the embed model to load."

embed ( save ) : ``cmdbox -m embed -c save <Option>``
=====================================================

- Saves the settings for the embedding model that generates feature data from input information.

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
    "--embed_name <embed_name>","required","Specify the registration name of the embed model."
    "--embed_device <embed_device>","","Specify the execution device of the embed model."
    "--embed_model <embed_model>","required","Specify the name of the huggingface embed model."

embed ( start ) : ``cmdbox -m embed -c start <Option>``
=======================================================

- Start the embedding model that generates feature data from the input information.

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
    "--embed_name <embed_name>","required","Specify the registration name of the embed model."

embed ( stop ) : ``cmdbox -m embed -c stop <Option>``
=====================================================

- Stop the embedding model that generates feature data from input information.

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
    "--embed_name <embed_name>","required","Specify the registration name of the embed model."
