.. -*- coding: utf-8 -*-

*******************************
Command Reference ( edge mode )
*******************************

List of edge mode commands.

edge ( config ) : ``cmdbox -m edge -c config <Option>``
=======================================================

- Set the edge mode.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--endpoint <endpoint>","str","","","http://localhost:8081","","Specify the URL of the endpoint."
    "--icon_path <icon_path>","file","","","F:\devenv\cmdbox\cmdbox\web\assets\cmdbox\favicon.ico","","Specify the path to the icon image."
    "--auth_type <auth_type>","str","","","idpw","noauth | idpw | apikey | oauth2 | saml","Specifies the authentication method for endpoint connections."
    "--user <user>","str","","","user","","Specifies the user connecting to the endpoint."
    "--password <password>","passwd","","","password","","Specify the password for connecting to the endpoint."
    "--apikey <apikey>","passwd","","","","","Specify the APIKEY to connect to the endpoint."
    "--oauth2 <oauth2>","str","","",""," | google | github | azure","Connect to the endpoint using OAuth2 authentication."
    "--oauth2_port <oauth2_port>","int","","","8091","","Specifies the callback port when OAuth2 authentication is used. If omitted, `8091` is used."
    "--oauth2_tenant_id <oauth2_tenant_id>","str","","","","","Specifies the tenant ID when OAuth2 authentication is used."
    "--oauth2_client_id <oauth2_client_id>","str","","","","","Specifies the client ID when OAuth2 authentication is used."
    "--oauth2_client_secret <oauth2_client_secret>","str","","","","","Specifies the client secret when OAuth2 authentication is used."
    "--oauth2_timeout <oauth2_timeout>","int","","","60","","Specify the timeout period before OAuth2 authentication completes."
    "--saml <saml>","str","","",""," | azure","Connect to the endpoint using SAML authentication."
    "--saml_port <saml_port>","int","","","8091","","Specifies the callback port when SAML authentication is used. If omitted, `8091` is used."
    "--saml_tenant_id <saml_tenant_id>","str","","","","","Specifies the tenant ID when SAML authentication is used."
    "--saml_timeout <saml_timeout>","int","","","60","","Specify the timeout period before SAML authentication completes."
    "--data <data>","dir","","","C:\Users\hama\.cmdbox","","When omitted, f`$HONE/.cmdbox` is used."
    "--svcert_no_verify <svcert_no_verify>","bool","","","False","False | True","Do not verify server certificates during HTTPS requests."
    "--timeout <timeout>","int","","","30","","Specifies the timeout period before the request completes."

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
        "data": {}
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
    "success.data","dict[str, any] | null","no","null","処理結果のデータ"
    "warn","dict[str, any] | list[any] | Data | str | bool | null","no","null","警告がある場合の結果"
    "warn.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "error","dict[str, any] | list[any] | Data | str | bool | null","no","null","エラーがある場合の結果"
    "error.performance","list[KeyVal] | null","no","null","パフォーマンス情報のリスト"
    "output_schema","dict[str, any] | null","no","null","スキーマ情報"
    "end","bool | null","no","null","終了フラグ"


edge ( start ) : ``cmdbox -m edge -c start <Option>``
=====================================================

- Start Edge mode.

.. csv-table::
    :widths: 20, 8, 8, 8, 12, 18, 26
    :header-rows: 1

    "Option","Type","Multi","Required","Default","Choices","Description"
    "--data <data>","dir","","required","C:\Users\hama\.cmdbox","","When omitted, f`$HONE/.cmdbox` is used."

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

