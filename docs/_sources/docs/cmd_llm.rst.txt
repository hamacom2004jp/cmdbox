.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( llm mode )
****************************************************

- List of llm mode commands.


Deletes LLM configuration. : `cmdbox -m llm -c del <Option>`
==============================================================================

- Deletes LLM configuration. This command sends a delete request to the agent via Redis.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--llmname <name>","Yes","Specify the name of the LLM configuration to delete."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Lists LLM configurations. : `cmdbox -m llm -c list <Option>`
==============================================================================

- Lists LLM configurations. Sends a list request to the agent and receives matching LLM names.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--kwd <keyword>","","Specify a partial match keyword to filter saved LLMs."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Loads LLM configuration. : `cmdbox -m llm -c load <Option>`
==============================================================================

- Loads LLM configuration from the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--llmname <name>","Yes","Specify the name of the LLM configuration to load."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."


Saves LLM configuration. : `cmdbox -m llm -c save <Option>`
===============================================================================

- Saves LLM configuration via the agent.

.. csv-table::
    :widths: 30, 10, 60
    :header-rows: 1

    "Option","Required","Description"
    "--host <IP address or host name>","","Specify the service host of the Redis server."
    "--port <port number>","","Specify the service port of the Redis server."
    "--password <password>","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <Service Name>","","Specify the service name of the inference server. If omitted, `server` is used."
    "--llmname <name>","Yes","Specify the name of the LLM configuration to save."
    "--llmprov <provider>","Yes","Specify llm provider."
    "--llmprojectid <id>","","Project ID for provider connection."
    "--llmsvaccountfile <file>","","Service account file for provider connection."
    "--llmlocation <location>","","Provider location."
    "--llmapikey <key>","","API key for provider connection."
    "--llmapiversion <version>","","Specifies the API version for llm provider connections."
    "--llmendpoint <endpoint>","","Provider endpoint."
    "--llmmodel <model>","","LLM model name."
    "--llmseed <int>","","Seed for model sampling."
    "--llmtemperature <float>","","Temperature for model sampling."
    "--retry_count <Number of retries>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <Retry Interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <time-out>","","Specify the maximum waiting time until the server responds."

