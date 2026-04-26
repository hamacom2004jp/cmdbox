.. -*- coding: utf-8 -*-

******************************
Command Reference ( tts mode )
******************************

List of tts mode commands.

tts ( install ) : ``cmdbox -m tts -c install <Option>``
=======================================================

- Installs the Text-to-Speech (TTS) engine.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data>","","When omitted, `$HONE/.cmdbox` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--client_only <client_only>","","Do not make connections to the server."
    "--force_install <force_install>","","Overwrite the installation even if it is already installed."
    "--tts_engine <tts_engine>","required","Specify the TTS engine to use."
    "--voicevox_ver <voicevox_ver>","","Specify the version of VOICEVOX to use."
    "--voicevox_whl <voicevox_whl>","","Specify the VOICEVOX wheel file to use."
    "--openjtalk_ver <openjtalk_ver>","","Specify the version of openjtalk to use."
    "--openjtalk_dic <openjtalk_dic>","","Specify the openjtalk dictionary file to use."
    "--onnxruntime_ver <onnxruntime_ver>","","Specify the version of ONNX Runtime to use."
    "--onnxruntime_lib <onnxruntime_lib>","","Specify the ONNX Runtime library file to use."

tts ( list ) : ``cmdbox -m tts -c list <Option>``
=================================================

- Lists the Text-to-Speech (TTS) engines.

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
    "--tts_engine <tts_engine>","required","Specify the TTS engine to use."

tts ( say ) : ``cmdbox -m tts -c say <Option>``
===============================================

- Converts text to speech using the Text-to-Speech (TTS) engine.

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
    "--tts_engine <tts_engine>","required","Specify the TTS engine to use."
    "--voicevox_model <voicevox_model>","","Specify the model of the TTS engine to use."
    "--tts_text <tts_text>","required","Specifies the text to convert."
    "--tts_output <tts_output>","","Specifies the output file for the converted audio."

tts ( uninstall ) : ``cmdbox -m tts -c uninstall <Option>``
===========================================================

- Uninstalls the Text-to-Speech (TTS) engine.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <host>","required","Specify the service host of the Redis server."
    "--port <port>","required","Specify the service port of the Redis server."
    "--password <password>","required","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","required","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data>","","When omitted, `$HONE/.cmdbox` is used."
    "--retry_count <retry_count>","","Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."
    "--retry_interval <retry_interval>","","Specifies the number of seconds before reconnecting to the Redis server."
    "--timeout <timeout>","","Specify the maximum waiting time until the server responds."
    "--client_only <client_only>","","Do not make connections to the server."
    "--tts_engine <tts_engine>","required","Specify the TTS engine to use."
