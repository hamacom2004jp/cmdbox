.. -*- coding: utf-8 -*-

*********************************
Command Reference ( cmdbox mode )
*********************************

List of cmdbox mode commands.

cmdbox ( down ) : ``cmdbox -m cmdbox -c down <Option>``
=======================================================

- Stops the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-C, --container <container>","","Specify the container name."

cmdbox ( exec ) : ``cmdbox -m cmdbox -c exec <Option>``
=======================================================

- Execute any command inside the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-C, --container <container>","","Specify the container name."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."
    "--command <command>","required","Specify the command to execute."

cmdbox ( load ) : ``cmdbox -m cmdbox -c load <Option>``
=======================================================

- Loads the container image.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--image_file <image_file>","","Specify the source image file."
    "-C, --container <container>","","Specify the container name."
    "--install_tag <install_tag>","","If specified, you can add to the tag name of the docker image to create."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( logs ) : ``cmdbox -m cmdbox -c logs <Option>``
=======================================================

- Displays the logs of the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-C, --container <container>","","Specify the container name."
    "-F, --follow <follow>","","Follow log output."
    "--number <number>","","Outputs the specified number of lines from the end of the log."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( pgsql_install ) : ``cmdbox -m cmdbox -c pgsql_install <Option>``
=========================================================================

- Installs the PostgreSQL server.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_pgsqlver <install_pgsqlver>","required","Specify the PostgreSQL version."
    "--install_from <install_from>","","Specify the source PostgreSQL image to install."
    "--install_tag <install_tag>","","If specified, you can add to the tag name of the docker image to create."
    "--no_install_pgvector <no_install_pgvector>","","Specify whether not to install the pgvector extension."
    "--install_pgvector_tag <install_pgvector_tag>","","Specify the tag name in the pgvector extension repository `https://github.com/pgvector/pgvector.git`."
    "--no_install_age <no_install_age>","","Specify whether not to install the Apache AGE extension."
    "--install_age_tag <install_age_tag>","","Specify the tag name in the Apache AGE extension repository `https://github.com/apache/age.git`."
    "--no_install_pgcron <no_install_pgcron>","","Specify whether not to install the pg_cron extension."
    "--install_pgcron_tag <install_pgcron_tag>","","Specify the tag name in the pg_cron extension repository `https://github.com/citusdata/pg_cron.git`."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( pgsql_load ) : ``cmdbox -m cmdbox -c pgsql_load <Option>``
===================================================================

- Loads the cmdbox PostgreSQL.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--image_file <image_file>","","Specify the source image file."
    "--install_pgsqlver <install_pgsqlver>","required","Specify the PostgreSQL version."
    "--install_tag <install_tag>","","If specified, you can add to the tag name of the docker image to create."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( reboot ) : ``cmdbox -m cmdbox -c reboot <Option>``
===========================================================

- Reboots the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-C, --container <container>","","Specify the container name."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( redis_install ) : ``cmdbox -m cmdbox -c redis_install <Option>``
=========================================================================

- Installs the cmdbox Redis.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--install_from <install_from>","","Specify the source Redis image to install."
    "--install_tag <install_tag>","","If specified, you can add to the tag name of the docker image to create."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( redis_load ) : ``cmdbox -m cmdbox -c redis_load <Option>``
===================================================================

- Loads the cmdbox Redis.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--image_file <image_file>","","Specify the source image file."
    "--install_tag <install_tag>","","If specified, you can add to the tag name of the docker image to create."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( save ) : ``cmdbox -m cmdbox -c save <Option>``
=======================================================

- Saves the container image.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-C, --container <container>","","Specify the container name."
    "--image_file <image_file>","","Specify the destination image file."
    "--install_tag <install_tag>","","If specified, you can add to the tag name of the docker image to create."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( server_install ) : ``cmdbox -m cmdbox -c server_install <Option>``
===========================================================================

- Install the cmdbox container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data>","","When omitted, `$HONE/.cmdbox` is used."
    "--install_cmdbox <install_cmdbox>","","When omitted, `cmdbox==0.7.9` is used."
    "--install_from <install_from>","","Specify the FROM image that will be the source of the docker image to be created."
    "--install_no_python <install_no_python>","","Do not install python."
    "--install_compile_python <install_compile_python>","","Compile and install python3; if install_no_python is specified, it is preferred."
    "--install_tag <install_tag>","","If specified, you can add to the tag name of the docker image to create."
    "--install_use_gpu <install_use_gpu>","","Install with a module configuration that uses the GPU."
    "--tts_engine <tts_engine>","required","Specify the TTS engine to use."
    "--voicevox_ver <voicevox_ver>","","Specify the version of VOICEVOX to use."
    "--voicevox_whl <voicevox_whl>","","Specify the VOICEVOX wheel file to use."
    "--init_extra <init_extra>","","Specify the command to be executed immediately after “from”."
    "--run_extra_pre <run_extra_pre>","","Specify additional commands to run before install_extra execution."
    "--run_extra_post <run_extra_post>","","Specify additional commands to run after install_extra execution."
    "--install_extra <install_extra>","","Specify additional packages to install."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( server_load ) : ``cmdbox -m cmdbox -c server_load <Option>``
=====================================================================

- Load the cmdbox container image.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--data <data>","","When omitted, `$HONE/.cmdbox` is used."
    "--image_file <image_file>","","Specify the source image file."
    "--install_tag <install_tag>","","If specified, you can add to the tag name of the docker image to create."
    "--install_use_gpu <install_use_gpu>","","Install with a module configuration that uses the GPU."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( uninstall ) : ``cmdbox -m cmdbox -c uninstall <Option>``
=================================================================

- Uninstalls the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-C, --container <container>","","Specify the container name."
    "--install_tag <install_tag>","","If specified, you can add to the tag name of the docker image to create."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."

cmdbox ( up ) : ``cmdbox -m cmdbox -c up <Option>``
===================================================

- Starts the container.

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "-C, --container <container>","","Specify the container name."
    "--compose_path <compose_path>","","Specify the `docker-compose.yml` file."
