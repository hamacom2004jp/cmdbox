.. -*- coding: utf-8 -*-

**************
Features
**************

- cmdbox has a `features.yml` mechanism for implementing new commands.
- This section describes how to use `features.yml`.

Reading order of `features.yml`
===================================

- The `features.yml` will try to read in the following order and use the first one found.

1. Try reading the `features.yml` that exists in the runtime directory.
2. Try reading the `extensions/features.yml` under the `version` module of the newly created `cmdbox` application.

Configuration items in `features.yml`
========================================

.. list-table::

    * - level
      - Setting items
      - type
      - e.g.
      - Description
    * - 1
      - features
      - dict
      - 
      - 
    * - 2
      - cli
      - list
      - 
      - Specify a list of package names in which the module implementing the command is located.
    * - 3
      - 
      - dict
      - 
      - 
    * - 4
      - package
      - str
      - sample.app.features.cli
      - Package Name. Classes inheriting from `cmdbox.app.feature.Feature` .
    * - 4
      - prefix
      - str
      - `sample_`
      - Module name prefix. Modules that begin with this letter are eligible.
    * - 2
      - web
      - list
      - 
      - Specify a list of package names with modules that implement web screens and RESTAPIs.
    * - 3
      - 
      - dict
      - 
      - 
    * - 4
      - package
      - str
      - sample.app.features.cli
      - Package Name. Classes inheriting from `cmdbox.app.feature.WebFeature` .
    * - 4
      - prefix
      - str
      - `sample_web_`
      - Module name prefix. Modules that begin with this letter are eligible.
    * - 1
      - args
      - dict
      - 
      - Specifies default or forced arguments for the specified command.
    * - 2
      - cli
      - list
      - 
      - Specify rules to apply default values or force arguments.
    * - 3
      - 
      - dict
      - 
      - 
    * - 4
      - rule
      - dict
      - mode: web
      - Specify the rules for applying default values and forced arguments for each command line option.
    * - 4
      - default
      - dict
      - doc_root: f"{Path(self.ver.__file__).parent / 'web'}"
      - Specify a default value for each item to be set when a rule is matched.
    * - 4
      - coercion
      - dict
      - doc_root: f"{Path(self.ver.__file__).parent / 'web'}"
      - Specify a coercion value for each item to be set when a rule is matched.

- See also the contents of `.sample/sample_project/sample/extensions/features.yml`.


Implement a class that extends `cmdbox.app.feature.Feature`
============================================================

- The new command implements a class that extends `cmdbox.app.feature`.
- Implementing methods of this class defines the behavior of the command.
- Below is a description of the methods of `cmdbox.app.feature`.


.. code-block:: python

    class Feature:

        def __init__(self, appcls, ver):
            """
            constructor

            Args:
                appcls (Type[cmdbox.app.CmdBoxApp]): Application class inheriting from cmdbox.app.CmdBoxApp
                ver (Type[cmdbox.app.Version]): New application version class
            """
            self.ver = ver
            self.appcls = appcls

        def get_mode(self) -> Union[str, List[str]]:
            """
            Returns the mode name of this function
            Returns a string corresponding to the mode option on the command line.

            Returns:
                Union[str, List[str]]: mode name
            """
            raise NotImplementedError

        def get_cmd(self) -> str:
            """
            Returns the command name of this function
            Returns a string corresponding to the cmd option on the command line.

            Returns:
                str: command name
            """
            raise NotImplementedError

        def get_option(self) -> Dict[str, Any]:
            """
            Returns the options for this function.
            The options returned here correspond to the command line options.
            I can't explain it well, so please refer to the classes in the cmdbox.app.features.cli package.

            Returns:
                Dict[str, Any]: option
            """
            raise NotImplementedError

        def get_svcmd(self):
            """
            Returns the name of the server-side command for this function.
            If the command is not executed on the server side, return None.
            I can't explain it well, so please refer to the classes in the cmdbox.app.features.cli package.

            Returns:
                str: Server-side command name
            """
            return None

        def apprun(self, logger:logging.Logger, args:argparse.Namespace, tm:float, pf:List[Dict[str, float]]) -> Tuple[int, Dict[str, Any], Any]:
            """
            Performs client-side processing.
            I can't explain it well, so please refer to the classes in the cmdbox.app.features.cli package.

            Args:
                logger (logging.Logger): logger
                args (argparse.Namespace): argument
                tm (float): execution start time
                pf (List[Dict[str, float]]): Caller Performance Information

            Returns:
                Tuple[int, Dict[str, Any], Any]: Exit Code, Result, Object
            """
            raise NotImplementedError

        def is_cluster_redirect(self):
            """
            If the message is addressed to a cluster, returns whether the message should be forwarded or not.
            This function returns True when the function should be performed on all servers with the same name if more than one server is started.

            Returns:
                bool: True if you want to forward the message.
            """
            raise NotImplementedError

        def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
                sessions:Dict[str, Dict[str, Any]]) -> int:
            """
            Performs server-side processing.
            I can't explain it well, so please refer to the classes in the cmdbox.app.features.cli package.

            Args:
                data_dir (Path): Server-side data directory
                logger (logging.Logger): logger
                redis_cli (redis_client.RedisClient): Redis Client
                msg (List[str]): incoming message
                sessions (Dict[str, Dict[str, Any]]): Session Information
            
            Returns:
                int: exit code
            """
            raise NotImplementedError
