.. -*- coding: utf-8 -*-

******************************
Command Reference ( gui mode )
******************************

List of gui mode commands.

gui ( start ) : ``cmdbox -m gui -c start <Option>``
===================================================

- Start GUI mode.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--host <host>","str","","required","localhost","","Specify the service host of the Redis server."
    "--port <port>","int","","required","6379","","Specify the service port of the Redis server."
    "--password <password>","passwd","","required","password","","Specify the access password of the Redis server (optional). If omitted, `password` is used."
    "--svname <svname>","str","","required","cmdbox","","Specify the service name of the inference server. If omitted, `server` is used."
    "--data <data>","dir","","","C:\Users\hama\.cmdbox","","When omitted, `$HONE/.cmdbox` is used."
    "--allow_host <allow_host>","str","","","0.0.0.0","","If omitted, `0.0.0.0` is used."
    "--listen_port <listen_port>","int","","","8081","","If omitted, `8081` is used."
    "--ssl_listen_port <ssl_listen_port>","int","","","8443","","If omitted, `8443` is used."
    "--ssl_cert <ssl_cert>","file","","","","","Specify the SSL server certificate file."
    "--ssl_key <ssl_key>","file","","","","","Specify the SSL server private key file."
    "--ssl_keypass <ssl_keypass>","str","","","","","Specify the composite password for the SSL server private key file."
    "--ssl_ca_certs <ssl_ca_certs>","file","","","","","Specify the SSL server CA certificate file."
    "--signin_file <signin_file>","file","","required",".cmdbox/user_list.yml","","Specify a file containing users and passwords with which they can signin.Typically, specify '.cmdbox/user_list.yml'."
    "--session_domain <session_domain>","str","","","","","Specify the domain for which the signed-in user's session is valid."
    "--session_path <session_path>","str","","","/","","Specify the session timeout in seconds for signed-in users."
    "--session_secure <session_secure>","bool","","","False","True | False","Set the Secure flag for the signed-in user's session."
    "--session_timeout <session_timeout>","int","","","900","","Specify the session timeout in seconds for signed-in users."
    "--gunicorn_workers <gunicorn_workers>","int","","","6","","Specifies the number of gunicorn workers, valid only in Linux environment. If -1 or unspecified, the number of CPUs is used."
    "--gunicorn_timeout <gunicorn_timeout>","int","","","900","","Specify the timeout duration of the gunicorn worker in seconds."
    "--client_only <client_only>","bool","","","False","True | False","Do not make connections to the server."
    "--outputs_key <outputs_key>","str","multi","","","","Specify items to be displayed on the showimg and webcap screens. If omitted, all items are displayed."
    "--doc_root <doc_root>","dir","","","","","Document root for custom files. URL mapping from the path of a folder-specified custom file with the path of doc_root removed."
    "--gui_html <gui_html>","file","","","","","Specify `gui.html`. If omitted, the cmdbox built-in HTML file is used."
    "--filer_html <filer_html>","file","","","","","Specify `filer.html`. If omitted, the cmdbox built-in HTML file is used."
    "--result_html <result_html>","file","","","","","Specify `result.html`. If omitted, the cmdbox built-in HTML file is used."
    "--users_html <users_html>","file","","","","","Specify `users.html`. If omitted, the cmdbox built-in HTML file is used."
    "--agent_html <agent_html>","file","","","","","Specify `agent.html`. If omitted, the cmdbox built-in HTML file is used."
    "--assets <assets>","file","multi","","","","Specify the asset file required when using html files."
    "--signin_html <signin_html>","file","","","","","Specify `signin.html`. If omitted, the cmdbox built-in HTML file is used."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


gui ( stop ) : ``cmdbox -m gui -c stop <Option>``
=================================================

- Stop GUI mode.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--data <data>","dir","","","C:\Users\hama\.cmdbox","","When omitted, `$HONE/.cmdbox` is used."

**Output Schema**

This command implements ``output_schema()`` returning ``Result`` model.

.. code-block:: json

    {
      "success": {
        "performance": [
          {
            "key": "string",
            "value": null
          }
        ],
        "data": "string"
      },
      "warn": {},
      "error": {},
      "output_schema": {},
      "end": false
    }

.. csv-table::
    :widths: 25, 10, 10, 15, 40
    :header-rows: 1

    "Field","Type","Required","Default","Description"
    "success","Data | null","no","null","成功した場合の結果"
    "success.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "success.data","str | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"

