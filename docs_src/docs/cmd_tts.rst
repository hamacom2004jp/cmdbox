.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( tts mode )
****************************************************

- List of tts mode commands.

Installs the Text-to-Speech (TTS) engine : `cmdbox -m tts -c install <Option>`
==============================================================================

- Installs the Text-to-Speech (TTS) engine.

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
    "--force_install","","Overwrite the installation even if it is already installed."
    "--tts_engine <TTS Engine>","","Specify the TTS engine to use."
    "--voicevox_ver <version>","","Specify the version of the TTS engine to use."
    "--voicevox_whl <whl>","","Specify the wheel file for the TTS engine."
    "--openjtalk_ver <ver>","","Specify the version of openjtalk to use."
    "--openjtalk_dic <file>","","Specify the openjtalk dictionary file to use."
    "--onnxruntime_ver <ver>","","Specify the version of ONNX Runtime to use."
    "--onnxruntime_lib <file>","","Specify the ONNX Runtime library file to use."


Lists the Text-to-Speech (TTS) engine : `cmdbox -m tts -c list <Option>`
==============================================================================

- Lists the Text-to-Speech (TTS) engines.

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
    "--tts_engine <TTS Engine>","","Specify the TTS engine to use."

Exec the Text-to-Speech (TTS) engine : `cmdbox -m tts -c say <Option>`
==============================================================================

- Converts text to speech using the Text-to-Speech (TTS) engine.

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
    "--tts_engine <TTS Engine>","","Specify the TTS engine to use."
    "--voicevox_model <model>","","Specify the model of the TTS engine to use."
    "--tts_text <text>","","Specifies the text to convert"
    "--tts_output <file>","","Specifies the output file for the converted audio."


Uninstalls the Text-to-Speech (TTS) engine : `cmdbox -m tts -c uninstall <Option>`
========================================================================================

- Uninstalls the Text-to-Speech (TTS) engine.

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
    "--tts_engine <TTS Engine>","","Specify the TTS engine to use."
