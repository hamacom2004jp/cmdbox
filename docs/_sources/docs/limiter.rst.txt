.. -*- coding: utf-8 -*-

****************************************************
Limiter
****************************************************

`Limiter` provides quantitative restrictions on command execution.
By saving restriction configurations and verifying them before each command runs, you can prevent excessive usage.

Overview
========

The Limiter functionality is implemented using the following modules:

- `cmdbox.app.commons.limiter`: Core logic for restriction checks and counter updates.
- `cmdbox.app.features.cli.cmdbox_limiter_save`: Add or save a restriction configuration.
- `cmdbox.app.features.cli.cmdbox_limiter_load`: Load a restriction configuration.
- `cmdbox.app.features.cli.cmdbox_limiter_list`: List registered restriction configurations.
- `cmdbox.app.features.cli.cmdbox_limiter_del`: Delete a restriction configuration.
- `cmdbox.app.features.cli.cmdbox_limiter_counter`: Retrieve restriction counters.
- `cmdbox.app.features.cli.cmdbox_limiter_targets`: List Features that inherit from `LimitedFeature`.

Restriction configurations are stored at `data_dir/.limiter/limiter-{name}.json` and
counters are stored at `data_dir/.limiter/counter-{name}.json`.

Scope
=====

Limiter supports two scopes:

- `server`: Stores restriction configurations in the server-side data directory (recommended).
- `client`: Stores restriction configurations in the client-side data directory specified by `--client_data`.

Saving a Restriction Configuration
===================================

Use the `save` command to register a restriction configuration.

Example (limit command executions to 100 times on the server side):

.. code-block:: bash

    cmdbox -m limiter -c save \
        --host localhost --port 6379 --password password --svname cmdbox \
        --limiter_name my_limit \
        --scope server \
        --target_mode mymode \
        --target_cmd mycommand \
        --max_total_count 100

Example (set an execution period and periodic reset on the client side):

.. code-block:: bash

    cmdbox -m limiter -c save \
        --host localhost --port 6379 --password password --svname cmdbox \
        --limiter_name my_limit2 \
        --scope client \
        --target_mode mymode \
        --exec_period_start 2024-01-01T00:00:00 \
        --exec_period_end 2024-12-31T23:59:59 \
        --refresh_interval 86400 \
        --max_history_interval 2678400

Main options:

.. list-table::
    :widths: 25 75
    :header-rows: 1

    * - Option
      - Description
    * - ``--limiter_name``
      - Identifier name for the restriction configuration (required).
    * - ``--scope``
      - Scope: `client` or `server` (required).
    * - ``--target_mode``
      - Mode name of the target command to restrict. If omitted, all modes are targeted.
    * - ``--target_cmd``
      - Command name of the target command to restrict. If omitted, all commands are targeted.
    * - ``--target_option``
      - Conditions for the target command in dictionary format (can be specified multiple times).
    * - ``--max_registrations``
      - Maximum number of registrations (or maximum registration size). If omitted, no limit is applied.
    * - ``--max_total_count``
      - Maximum number of command executions. If omitted, no limit is applied.
    * - ``--max_total_time``
      - Total executable time in seconds for the command. If omitted, no limit is applied.
    * - ``--max_total_input``
      - Maximum total number of input bytes. If omitted, no limit is applied.
    * - ``--max_total_process``
      - Maximum total number of process bytes. If omitted, no limit is applied.
    * - ``--max_total_output``
      - Maximum total number of output bytes. If omitted, no limit is applied.
    * - ``--max_total_credits``
      - Maximum number of credits for the command. If omitted, no limit is applied.
    * - ``--service_credits``
      - Number of service credits.
    * - ``--exec_period_start``
      - Start datetime of the executable period (e.g. `2024-01-01T00:00:00`). If omitted, no limit is applied.
    * - ``--exec_period_end``
      - End datetime of the executable period (e.g. `2024-12-31T23:59:59`). If omitted, no limit is applied.
    * - ``--refresh_datetime``
      - Datetime at which the restriction counters are reset. If omitted, no reset is performed.
    * - ``--refresh_interval``
      - Interval in seconds after which the restriction counters are reset. If omitted, no reset is performed.
    * - ``--max_history_interval``
      - Maximum duration in seconds for which counter history is retained. Default is 31 days (2678400 seconds).

Loading a Restriction Configuration
=====================================

Use the `load` command to inspect a registered restriction configuration.

.. code-block:: bash

    cmdbox -m limiter -c load \
        --host localhost --port 6379 --password password --svname cmdbox \
        --limiter_name my_limit \
        --scope server

Listing Restriction Configurations
====================================

Use the `list` command to display all registered restriction configurations.

.. code-block:: bash

    cmdbox -m limiter -c list \
        --host localhost --port 6379 --password password --svname cmdbox \
        --scope server

Example with keyword search (partial match):

.. code-block:: bash

    cmdbox -m limiter -c list \
        --host localhost --port 6379 --password password --svname cmdbox \
        --scope server \
        --kwd my_

Deleting a Restriction Configuration
======================================

Use the `del` command to delete a registered restriction configuration.

.. code-block:: bash

    cmdbox -m limiter -c del \
        --host localhost --port 6379 --password password --svname cmdbox \
        --limiter_name my_limit \
        --scope server

Retrieving Counters
====================

Use the `counter` command to retrieve the counter for a restriction configuration.

.. code-block:: bash

    cmdbox -m limiter -c counter \
        --host localhost --port 6379 --password password --svname cmdbox \
        --limiter_name my_limit \
        --scope server

To also retrieve counter history:

.. code-block:: bash

    cmdbox -m limiter -c counter \
        --host localhost --port 6379 --password password --svname cmdbox \
        --limiter_name my_limit \
        --scope server \
        --load_history

Available counter fields:

.. list-table::
    :widths: 30 70
    :header-rows: 1

    * - Field
      - Description
    * - ``limiter_name``
      - Identifier name of the restriction configuration.
    * - ``total_count``
      - Number of executions.
    * - ``total_time``
      - Total execution time in seconds.
    * - ``total_input``
      - Total input bytes.
    * - ``total_process``
      - Total process bytes.
    * - ``total_output``
      - Total output bytes.
    * - ``total_credits``
      - Total credits consumed.
    * - ``total_registrations``
      - Total number of registrations.
    * - ``last_refresh``
      - Datetime of the last counter reset.
    * - ``last_update``
      - Datetime of the last counter update.

Listing Restriction Targets
=============================

Use the `targets` command to list all Features that inherit from `LimitedFeature` (i.e. commands that support restriction).

.. code-block:: bash

    cmdbox -m limiter -c targets \
        --host localhost --port 6379 --password password --svname cmdbox \
        --scope server

To filter by mode or command:

.. code-block:: bash

    cmdbox -m limiter -c targets \
        --host localhost --port 6379 --password password --svname cmdbox \
        --scope server \
        --filter_target_mode mymode \
        --filter_target_cmd mycommand

Developer Guide: Implementing a Limiter-Enabled Command
========================================================

To apply the Limiter to a custom command, inherit from `LimitedFeature` and apply the appropriate decorator to `apprun` or `svrun`.

**Applying to a client-side command**

.. code-block:: python

    from cmdbox.app.commons.limiter import LimitedFeature, apprun_check_limit

    class MyFeature(LimitedFeature):
        def get_mode(self):
            return 'mymode'

        def get_cmd(self):
            return 'mycommand'

        @apprun_check_limit
        def apprun(self, logger, args, tm, pf=[]):
            # The restriction check runs automatically before execution.
            # The counter is updated automatically after execution.
            result = dict(success="done")
            return self.RESP_SUCCESS, result, None

**Applying to a server-side command**

.. code-block:: python

    from cmdbox.app.commons.limiter import LimitedFeature, svrun_check_limit

    class MyFeature(LimitedFeature):
        @svrun_check_limit
        def svrun(self, data_dir, logger, redis_cli, msg, sessions):
            # The restriction check runs automatically before execution.
            # The counter is updated automatically after execution.
            ...
            return self.RESP_SUCCESS

**Applying to async commands**

Use `async_apprun_check_limit` / `async_svrun_check_limit` for async `apprun` / `svrun`.

.. code-block:: python

    from cmdbox.app.commons.limiter import LimitedFeature, async_apprun_check_limit

    class MyAsyncFeature(LimitedFeature):
        @async_apprun_check_limit
        async def apprun(self, logger, args, tm, pf=[]):
            result = dict(success="done")
            return self.RESP_SUCCESS, result, None

**Customizing counter calculation methods**

`LimitedFeature` provides the following methods that can be overridden to customize how counter values are calculated:

.. list-table::
    :widths: 35 65
    :header-rows: 1

    * - Method
      - Description
    * - ``apprun_input_bytes()``
      - Returns the input byte count for a client-side command. Default is the byte length of the argument string.
    * - ``apprun_output_bytes()``
      - Returns the output byte count for a client-side command. Default is the byte length of the result string.
    * - ``apprun_credit()``
      - Returns the credits consumed by a client-side command. Default is 0.
    * - ``apprun_count()``
      - Returns the execution count for a client-side command. Default is 1.
    * - ``apprun_process_bytes()``
      - Returns the process byte count for a client-side command. Default is 0.
    * - ``apprun_registrations()``
      - Returns the registration count for a client-side command. Default is 0.
    * - ``svrun_input_bytes()``
      - Returns the input byte count for a server-side command.
    * - ``svrun_output_bytes()``
      - Returns the output byte count for a server-side command.
    * - ``svrun_credit()``
      - Returns the credits consumed by a server-side command. Default is 0.
    * - ``svrun_count()``
      - Returns the execution count for a server-side command. Default is 1.
    * - ``svrun_process_bytes()``
      - Returns the process byte count for a server-side command. Default is 0.
    * - ``svrun_registrations()``
      - Returns the registration count for a server-side command. Default is 0.

Command Reference
=================

For the full list of options for each command, see :doc:`cmd_limiter`.
