.. -*- coding: utf-8 -*-

****************************************************
Command Reference ( cmdbox mode )
****************************************************

List of cmdbox mode commands.


cmdbox ( down ) : `cmdbox -m cmdbox -c down <Option>`
========================================================================================

- Stops the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--container <container>","","Specify the container name."


cmdbox ( exec ) : `cmdbox -m cmdbox -c exec <Option>`
========================================================================================

- Execute any command inside the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--container <container>","","Specify the container name."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."
    "--command <command>","","Specify the command to execute."


cmdbox ( logs ) : `cmdbox -m cmdbox -c logs <Option>`
========================================================================================

- Displays the logs of the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--container <container>","","Specify the container name."
    "--follow","","Follow log output."
    "--number <num>","","Outputs the specified number of lines from the end of the log."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( reboot ) : `cmdbox -m cmdbox -c reboot <Option>`
========================================================================================

- Reboots the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--container <container>","","Specify the container name."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( up ) : `cmdbox -m cmdbox -c up <Option>`
========================================================================================

- Starts the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--container <container>","","Specify the container name."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( pgsql_install ) : `cmdbox -m cmdbox -c pgsql_install <Option>`
========================================================================================

- Installs the PostgreSQL server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_pgsqlver <version>","","Specify the PostgreSQL version."
    "--install_from <base>","","Specify the source PostgreSQL image to install."
    "--install_tag <tag>","","If specified, you can add to the tag name of the docker image to create."
    "--no_install_pgvector","","Specify whether not to install the pgvector extension."
    "--install_pgvector_tag <tag>","","Specify the tag name in the pgvector extension repository `https://github.com/pgvector/pgvector.git`."
    "--no_install_age","","Specify whether not to install the Apache AGE extension."
    "--install_age_tag <tag>","","Specify the tag name in the Apache AGE extension repository `https://github.com/apache/age.git`."
    "--no_install_pgcron","","Specify whether not to install the pg_cron extension."
    "--install_pgcron_tag <tag>","","Specify the tag name in the pg_cron extension repository `https://github.com/citusdata/pg_cron.git`."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( pgsql_uninstall ) : `cmdbox -m cmdbox -c pgsql_uninstall <Option>`
========================================================================================

- Uninstalls the PostgreSQL server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_pgsqlver <version>","","Specify the PostgreSQL version."
    "--install_tag <tag>","","If specified, you can add to the tag name of the docker image to create."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( redis_install ) : `cmdbox -m cmdbox -c redis_install <Option>`
========================================================================================

- Installs the Redis server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_from <base>","","Specify the source Redis image to install."
    "--install_tag <tag>","","If specified, you can add to the tag name of the docker image to create."
    "--compose_path <path>","","Specify the `docker-compose.yml` file."


cmdbox ( redis_uninstall ) : `cmdbox -m cmdbox -c redis_uninstall <Option>`
========================================================================================

- Uninstalls the cmdbox Redis.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
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
    "--run_extra_pre <command>","","Specify additional commands to run before install_extra execution."
    "--run_extra_post <command>","","Specify additional commands to run after install_extra execution."
    "--install_extra <module>","","Specify additional packages to install."
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

