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

.. code-block:: yaml

    features:
      cli:                                  # Specify a list of package names in which the module implementing the command is located.
        - package: cmdbox.app.features.cli  # Package Name. Classes inheriting from cmdbox.app.feature.Feature.
          prefix: cmdbox_                   # Module name prefix. Modules that begin with this letter are eligible.
          exclude_modules: []               # Specify the module name to exclude from the list of modules to be loaded.
      web:                                  # Specify a list of package names with modules that implement web screens and RESTAPIs.
        - package: cmdbox.app.features.web  # Package Name. Classes inheriting from cmdbox.app.feature.WebFeature .
          prefix: cmdbox_web_               # Module name prefix. Modules that begin with this letter are eligible.
    args:                                   # Specifies default or forced arguments for the specified command.
      cli:                                  # Specify rules to apply default values or force arguments.
        - rule:                             # Specify the rules for applying default values and forced arguments for each command line option.
                                            #   e.g. mode: web
          default:                          # Specify a default value for each item to be set when a rule is matched.
                                            #   e.g. doc_root: f"{Path(self.ver.__file__).parent / 'web'}"
          coercion:                         # Specify a coercion value for each item to be set when a rule is matched.
                                            #   e.g. doc_root: f"{Path(self.ver.__file__).parent / 'web'}"
    aliases:                                # Specify the alias for the specified command.
      cli:                                  # Specify the alias for the command line.
        - source:                           # Specifies the command from which the alias originates.
            mode:                           # Specify the mode of the source command. The exact match "mode" is selected.
                                            #   e.g. client
            cmd:                            # Specify the source command to be aliased. The regex match "cmd" is selected.
                                            #   e.g. (.+)_(.+)
          target:                           # Specifies the command to be aliased to.
            mode:                           # Specify the mode of the target command. Create an alias for this “mode”.
                                            #   e.g. CLIENT
            cmd:                            # Specify the target command to be aliased. Create an alias for this “cmd”, referring to the regular expression group of source by "{n}".
                                            #   e.g. {2}_{1}
            move:                           # Specify whether to move the regular expression group of the source to the target.
                                            #   e.g. true
      web:                                  # Specify the alias for the RESTAPI.
        - source:                           # Specifies the RESTAPI from which the alias originates.
            path:                           # Specify the path of the source RESTAPI. The regex match "path" is selected.
                                            #   e.g. /exec_(.+)
          target:                           # Specifies the RESTAPI to be aliased to.
            path:                           # Specify the path of the target RESTAPI. Create an alias for this “path”, referring to the regular expression group of source by "{n}".
                                            #   e.g. /{1}_exec
            move:                           # Specify whether to move the regular expression group of the source to the target.
                                            #   e.g. true
    agentrule:                              # Specifies a list of rules that determine which commands the agent can execute.
      policy: deny                          # Specify the default policy for the rule. The value can be allow or deny.
      rules:                                # Specify the rules for the commands that the agent can execute according to the group to which the user belongs.
      - mode: cmd                           # Specify the "mode" as the condition for applying the rule.
        cmds: [list, load]                  # Specify the "cmd" to which the rule applies. Multiple items can be specified in a list.
        rule: allow                         # Specifies whether the specified command is allowed or not. Values are allow or deny.
      - mode: client
        cmds: [file_download, file_list, http, server_info]
        rule: allow
      - mode: excel
        cmds: [cell_details, cell_search, cell_values, sheet_list]
        rule: allow
      - mode: server
        cmds: [list]
        rule: allow
      - mode: tts
        cmds: [say]
        rule: allow
    audit:
      enabled: true                         # Specify whether to enable the audit function.
      write:
        mode: audit                         # Specify the mode of the feature to be writed.
        cmd: write                          # Specify the command to be writed.
      search:
        mode: audit                         # Specify the mode of the feature to be searched.
        cmd: search                         # Specify the command to be searched.
      options:                              # Specify the options for the audit function.
        host: localhost                     # Specify the service host of the audit Redis server.However, if it is specified as a command line argument, it is ignored.
        port: 6379                          # Specify the service port of the audit Redis server.However, if it is specified as a command line argument, it is ignored.
        password: password                  # Specify the access password of the audit Redis server.However, if it is specified as a command line argument, it is ignored.
        svname: cmdbox                      # Specify the audit service name of the inference server.However, if it is specified as a command line argument, it is ignored.
        retry_count: 3                      # Specifies the number of reconnections to the audit Redis server.If less than 0 is specified, reconnection is forever.
        retry_interval: 1                   # Specifies the number of seconds before reconnecting to the audit Redis server.
        timeout: 15                         # Specify the maximum waiting time until the server responds.
        pg_enabled: False                   # Specify True if using the postgresql database server.
        pg_host: localhost                  # Specify the postgresql host.
        pg_port: 5432                       # Specify the postgresql port.
        pg_user: postgres                   # Specify the postgresql user name.
        pg_password: password               # Specify the postgresql password.
        pg_dbname: audit                    # Specify the postgresql database name.
        retention_period_days: 365          # Specify the number of days to retain audit logs.

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

        def edgerun(self, opt:Dict[str, Any], tool:edge.Tool, logger:logging.Logger, timeout:int, prevres:Any=None):
            """
            Performs edge-side execution of this function

            Args:
                opt (Dict[str, Any]): option
                tool (edge.Tool): Classes for edge-side UI operations such as notification functions
                logger (logging.Logger): logger
                timeout (int): Timeout time
                prevres (Any): Result of the previous command, used when referencing the results of a pipeline run.

            Yields:
                Tuple[int, Dict[str, Any]]: 終了コード, 結果
            """
            status, res = tool.exec_cmd(opt, logger, timeout, prevres)
            yield status, res


- To simplify implementation on the edge, we provide several classes that inherit from `cmdbox.app.feature`.
- For details, refer to the `cmdbox.app.feature` module.


.. code-block:: python

    class OneshotEdgeFeature(Feature):
        """
        Base class for edge functions that execute only once.
        """

    class OneshotNotifyEdgeFeature(OneshotEdgeFeature):
        """
        Base class for edge functionality that provides notification of execution results.
        """

    class ResultEdgeFeature(Feature):
        """
        Base class for edge functionality that displays execution results in a web browser.
        """

    class OneshotResultEdgeFeature(ResultEdgeFeature):
        """
        Base class for edge functionality that displays the result of a one-time execution in a web browser.
        """

    class UnsupportEdgeFeature(Feature):
        """
        Base class for unsupported edge features.
        """


Implementation of the `get_option(self) -> Dict[str, Any]` method
-------------------------------------------------------------------------

- The `get_option(self) -> Dict[str, Any]` method returns the command line options for the command.
- Below is an example of how to implement this method.


.. code-block:: python

    def get_option(self) -> Dict[str, Any]:
        return dict(
            use_redis=self.USE_REDIS_FALSE, nouse_webmode=False, use_agent=True,
            description_ja="MCP サーバ設定を保存します。",
            description_en="Saves MCP server configuration.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                    description_ja="Redisサーバーのサービスホストを指定します。",
                    description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                    description_ja="Redisサーバーのサービスポートを指定します。",
                    description_en="Specify the service port of the Redis server."),
            ]
        )


- The options returned here correspond to the command line options.
- Details for each option item are as follows.

    - use_redis: Specifies whether to use Redis. Specify one of the following constants defined in `cmdbox.app.feature.Feature`: `USE_REDIS_TRUE`, `USE_REDIS_FALSE`, `USE_REDIS_MEIGHT`.
    - nouse_webmode: Specifies whether the command is not executable in Web mode. The default is False.
    - use_agent: Specifies whether the command is available to agents. The default is False.
    - description_ja: Description in Japanese
    - description_en: Description in English
    - choice: Specifies the list of command line options. Each option is specified as a dictionary with the following items.
        - opt: Option name
        - type: Option type. Specify one of the following constants defined in `cmdbox.app.options.Options`:
            - T_INT = 'int'
            - T_FLOAT = 'float'
            - T_BOOL = 'bool'
            - T_STR = 'str'
            - T_DATE = 'date'
            - T_DATETIME = 'datetime'
            - T_DICT = 'dict'
            - T_TEXT = 'text'
            - T_FILE = 'file'
            - T_DIR = 'dir'
            - T_MLIST = 'mlist'
        - default: Default value
        - required: Whether this option is required
        - multi: Whether multiple values can be specified
        - hide: Whether to hide this option by default in Web mode
        - web: Specifies how to display options that cannot be edited in web mode. Specifying “mask” masks the option. Specifying “readonly” makes it read-only.
        - fileio: When the type is file, specify whether it is a read file or a write file. Specify `in` or `out`.
        - choice: Specifies the choices for this option. If dynamic generation is required, implement the `choice_fn` method in the feature class.
            Choices can be specified in either of the following two ways.

            - Options when type is a list or mlist.

            .. code-block:: python

                choice=[False, True]

            - Options when type is a dictionary.

            .. code-block:: python

                choice=dict(key=["dictkey1","dictkey2","dictkey3"], val=["dictval1","dictval2","dictval3"])

        - choice_edit: Specifies whether values other than the options can be entered. If true, values other than the options can be entered.

            .. code-block:: python

                choice_edit=True,

        - choice_fn: A function that generates the choices dynamically.

            .. code-block:: python

                def choice_fn(self, o:Dict[str, Any], webmode:bool, opt:Dict[str, Any]) -> Any:
                    """
                    オプションのchoiceを動的に生成する関数

                    Args:
                        o (Dict[str, Any]): choice_fn関数が呼ばれたコマンドオプションのchoice定義
                        webmode (bool): Webモードかどうか
                        opt (Dict[str, Any]): このコマンドのすべてのコマンドオプションのchoice定義

                    Returns:
                        Any: choice情報
                    """
                    choices = []
                    return choices

        - choice_show: Specify the other options to display when this option is selected.

            .. code-block:: python

                choice_show=dict(choice1=["opt1", "opt2"], choice2=["opt3"], choice3=["opt4", "opt5"]),


        - callcmd: コマンドボタンを追加し、そのコマンドボタンが押されたときに呼ばれるjavascript関数を指定します。

            .. code-block:: python

                callcmd="()=>{cmdbox.callcmd('cmd','list',{'kwd':'*'},(res)=>{console.log(res);},$(\"[name='title']\").val(),'tag');}",
