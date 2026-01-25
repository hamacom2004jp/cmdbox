.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( cmdbox mode )
****************************************************

List of cmdbox mode commands.

cmdbox ( redis_install ) : `cmdbox -m cmdbox -c redis_install <Option>`
========================================================================================

- Installs the redis server.

cmdbox ( server_down ) : `cmdbox -m cmdbox -c server_down <Option>`
========================================================================================

- Stops the cmdbox server.

cmdbox ( server_exec ) : `cmdbox -m cmdbox -c server_exec <Option>`
========================================================================================

- Execute any command within the cmdbox server container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--command <command>","","Specify the command to execute."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( server_install ) : `cmdbox -m cmdbox -c server_install <Option>`
========================================================================================

- Install the cmdbox container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data folder>","","When omitted, `$HONE/.{self.ver.__appid__}` is used."
    "--install_cmdbox <module>","","When omitted, `cmdbox=={version.__version__}` is used."
    "--install_from <base>","","Specify the FROM image that will be the source of the docker image to be created."
    "--install_no_python","","Do not install python."
    "--install_compile_python","","Compile and install python3; if install_no_python is specified, it is preferred."
    "--install_tag <tag>","","If specified, you can add to the tag name of the docker image to create."
    "--install_use_gpu","","Install with a module configuration that uses the GPU."
    "--tts_engine <TTS Engine>","","Specify the TTS engine to use."
    "--voicevox_ver <version>","","Specify the version of the TTS engine to use."
    "--voicevox_whl <whl>","","Specify the wheel file for the TTS engine."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( server_logs ) : `cmdbox -m cmdbox -c server_logs <Option>`
========================================================================================

- Displays the logs of the cmdbox server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--follow","","Follow log output."
    "--number <num>","","Outputs the specified number of lines from the end of the log."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( server_reboot ) : `cmdbox -m cmdbox -c server_reboot <Option>`
========================================================================================

- Reboots the cmdbox server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( server_uninstall ) : `cmdbox -m cmdbox -c server_uninstall <Option>`
========================================================================================

- Uninstalls the cmdbox server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_tag <tag>","","If specified, you can add to the tag name of the docker image to create."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( server_up ) : `cmdbox -m cmdbox -c server_up <Option>`
========================================================================================

- Starts the cmdbox server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--compose_path <path>","","Specify the `docker-compose.yml` file."
