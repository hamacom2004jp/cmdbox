.. -*- coding: utf-8 -*-

******************************
Command Reference ( llm mode )
******************************

List of llm mode commands.

llm ( chat ) : ``cmdbox -m llm -c chat <Option>``
=================================================

- Send a chat message to the LLM.

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
    "--llmname <llmname>","required","Specify the name of the LLM configuration to load."
    "--msg_role <msg_role>","required","Specify the role of the message sender."
    "--msg_name <msg_name>","","Specify the name of the message sender. Required if msg_role is `function` or `tool`."
    "--msg_text <msg_text>","","Specify the content of the text to be sent."
    "--msg_text_system <msg_text_system>","","Specify the system prompt to send. Using `{{AAA}}` allows you to set the `AAA` parameter. Note that specifying `{{msg_text}}` sets the value of the `msg_text` option."
    "--msg_text_param <msg_text_param>","","Specify the parameters for the text."
    "--msg_image_url <msg_image_url>","","Specify the URL of the image to be sent."
    "--msg_audio <msg_audio>","","Specify the content of the audio to be sent."
    "--msg_audio_format <msg_audio_format>","","Specify the format of the audio to be sent."
    "--msg_video_url <msg_video_url>","","Specify the URL of the video to be sent."
    "--msg_file_url <msg_file_url>","","Specify the URL of the file to be sent."
    "--msg_doc <msg_doc>","","Specify the content of the document to be sent."
    "--msg_doc_mime <msg_doc_mime>","","Specify the MIME type of the document to be sent."

llm ( del ) : ``cmdbox -m llm -c del <Option>``
===============================================

- Deletes LLM configuration.

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
    "--llmname <llmname>","required","Specify the name of the LLM configuration to delete."

llm ( list ) : ``cmdbox -m llm -c list <Option>``
=================================================

- Lists saved LLM configurations.

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

llm ( load ) : ``cmdbox -m llm -c load <Option>``
=================================================

- Loads LLM configuration.

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
    "--llmname <llmname>","required","Specify the name of the LLM configuration to load."

llm ( save ) : ``cmdbox -m llm -c save <Option>``
=================================================

- Saves LLM configuration.

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
    "--llmname <llmname>","required","Specify the name of the LLM configuration to save."
    "--llmprov <llmprov>","required","Specify llm provider."
    "--llmprojectid <llmprojectid>","","Specify the project ID for llm's provider connection."
    "--llmsvaccountfile <llmsvaccountfile>","","Specifies the service account file for llm's provider connection."
    "--llmlocation <llmlocation>","","Specifies the location for llm provider connections."
    "--llmapikey <llmapikey>","","Specify API key for llm provider connection."
    "--llmapiversion <llmapiversion>","","Specifies the API version for llm provider connections."
    "--llmendpoint <llmendpoint>","","Specifies the endpoint for llm provider connections."
    "--llmmodel <llmmodel>","","Specifies the llm model."
    "--llmseed <llmseed>","","Specifies the seed value when using llm model."
    "--llmtemperature <llmtemperature>","","Specifies the temperature when using llm model."
