.. -*- coding: utf-8 -*-

****************************************************
コマンドリファレンス（serverモード）
****************************************************

- serverモードのコマンド一覧です。

サーバー起動 : `cmdbox -m server -c start <Option>`
==============================================================================

- installモードで `cmdbox -m install -c server` を実行している場合は、 `docker-compose up -d` を使用してください。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します。"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します。"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。"
    "--svname <推論サービス名>","","サーバーのサービス名を指定します。省略時は `server` を使用します"
    "--data <データフォルダ>","","省略した時は `$HONE/.cmdbox` を使用します。"
    "--retry_count <再接続回数>","","Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。"
    "--retry_interval <秒数>","","Redisサーバーに再接続までの秒数を指定します。"

サーバー停止 : `cmdbox -m server -c stop <Option>`
==============================================================================

- installモードで `cmdbox -m install -c server` を実行している場合は、 `docker-compose down` を使用してください。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します。"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します。"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。"
    "--svname <推論サービス名>","","サーバーのサービス名を指定します。省略時は `server` を使用します"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間を指定します。"

サーバー一覧 : `cmdbox -m server -c list <Option>`
==============================================================================

- 起動中のサーバーの一覧を表示します。
- クライアント環境からの利用も可能です。

.. csv-table::
    :widths: 20, 10, 70
    :header-rows: 1

    "Option","Required","Description"
    "--host <IPアドレス又はホスト名>","","Redisサーバーのサービスホストを指定します。"
    "--port <ポート番号>","","Redisサーバーのサービスポートを指定します。"
    "--password <パスワード>","","Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。"
    "--timeout <タイムアウト>","","サーバーの応答が返ってくるまでの最大待ち時間を指定します。"
