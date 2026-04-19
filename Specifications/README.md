# CLI Specifications

フィーチャーパッケージのコマンド実装から生成した詳細設計書です。

- 生成対象コマンド数: 115
- 生成日時: 2026-04-19T20:59:12
- JSON メタデータ: cli-command-specifications.json

## 共通仕様

- すべての CLI コマンドは mode と cmd の組で識別されます。
- get_option() の choice 配列が、受け付けるパラメータ定義の原本です。
- apprun() はクライアント側処理、svrun() はサーバー側処理を表します。
- 終了コードは Feature.RESP_SUCCESS, Feature.RESP_WARN, Feature.RESP_ERROR を中心に返します。

## 一覧

### a2asv (2)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| start | A2A サーバーを起動します。 | [start](cli/a2asv/start.md) |
| stop | A2A サーバーを停止します。 | [stop](cli/a2asv/stop.md) |

### agent (22)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| agent_del | Agent 設定を削除します。 | [agent_del](cli/agent/agent_del.md) |
| agent_list | 保存されているAgent設定を一覧表示します。 | [agent_list](cli/agent/agent_list.md) |
| agent_load | Agent 設定を読み込みます。 | [agent_load](cli/agent/agent_load.md) |
| agent_save | Agent 設定を保存します。 | [agent_save](cli/agent/agent_save.md) |
| chat | Agentとチャットを行います。 | [chat](cli/agent/chat.md) |
| mcp_client | リモートMCPサーバーにリクエストを行うMCPクライアントを起動します。 | [mcp_client](cli/agent/mcp_client.md) |
| mcp_proxy | 標準入力を受け付け、リモートMCPサーバーにリクエストを行うProxyサーバーを起動します。 | [mcp_proxy](cli/agent/mcp_proxy.md) |
| mcpsv_del | MCP サーバ設定を削除します。 | [mcpsv_del](cli/agent/mcpsv_del.md) |
| mcpsv_list | 保存されているMCPサーバ設定を一覧表示します。 | [mcpsv_list](cli/agent/mcpsv_list.md) |
| mcpsv_load | MCP サーバ設定を読み込みます。 | [mcpsv_load](cli/agent/mcpsv_load.md) |
| mcpsv_save | MCP サーバ設定を保存します。 | [mcpsv_save](cli/agent/mcpsv_save.md) |
| memory_del | Memory設定を削除します。 | [memory_del](cli/agent/memory_del.md) |
| memory_list | 保存されているMemory設定を一覧表示します。 | [memory_list](cli/agent/memory_list.md) |
| memory_load | Memory設定を読み込みます。 | [memory_load](cli/agent/memory_load.md) |
| memory_save | Memory 設定を保存します。 | [memory_save](cli/agent/memory_save.md) |
| memory_status | Agentのメモリステータスを取得します。 | [memory_status](cli/agent/memory_status.md) |
| runner_del | Runner 設定を削除します。 | [runner_del](cli/agent/runner_del.md) |
| runner_list | 保存されているRunner設定を一覧表示します。 | [runner_list](cli/agent/runner_list.md) |
| runner_load | Runner 設定を読み込みます。 | [runner_load](cli/agent/runner_load.md) |
| runner_save | Runner 設定を保存します。 | [runner_save](cli/agent/runner_save.md) |
| session_del | Agentのセッションを削除します。 | [session_del](cli/agent/session_del.md) |
| session_list | Agentのセッション一覧を取得します。 | [session_list](cli/agent/session_list.md) |

### audit (4)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| createdb | 監査を記録するデータベースを作成します。 | [createdb](cli/audit/createdb.md) |
| delete | 監査ログを削除します。 | [delete](cli/audit/delete.md) |
| search | 監査ログを検索します。 | [search](cli/audit/search.md) |
| write | 監査を記録します。 | [write](cli/audit/write.md) |

### client (11)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| file_copy | サーバー側のデータフォルダ配下のファイルをコピーします。 | [file_copy](cli/client/file_copy.md) |
| file_download | サーバー側のデータフォルダ配下のファイルをダウンロードします。 | [file_download](cli/client/file_download.md) |
| file_list | データフォルダ配下のファイルリストを取得します。 | [file_list](cli/client/file_list.md) |
| file_mkdir | データフォルダ配下に新しいフォルダを作成します。 | [file_mkdir](cli/client/file_mkdir.md) |
| file_move | データフォルダ配下のファイルを移動します。 | [file_move](cli/client/file_move.md) |
| file_remove | データフォルダ配下のファイルを削除します。 | [file_remove](cli/client/file_remove.md) |
| file_rmdir | データフォルダ配下のフォルダを削除します。 | [file_rmdir](cli/client/file_rmdir.md) |
| file_upload | データフォルダ配下にファイルをアップロードします。 | [file_upload](cli/client/file_upload.md) |
| http | HTTPサーバーに対してリクエストを送信し、レスポンスを取得します。 | [http](cli/client/http.md) |
| server_info | サーバーの情報を取得します。 | [server_info](cli/client/server_info.md) |
| time | クライアント側の現在時刻を表示します。 | [time](cli/client/time.md) |

### cmd (2)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| list | データフォルダ配下のコマンドリストを取得します。 | [list](cli/cmd/list.md) |
| load | データフォルダ配下のコマンドの内容を取得します。 | [load](cli/cmd/load.md) |

### cmdbox (14)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| down | コンテナを停止します。 | [down](cli/cmdbox/down.md) |
| exec | コンテナ内で任意のコマンドを実行します。 | [exec](cli/cmdbox/exec.md) |
| load | コンテナイメージを読み込みます。 | [load](cli/cmdbox/load.md) |
| logs | コンテナのログを表示します。 | [logs](cli/cmdbox/logs.md) |
| pgsql_install | PostgreSQLサーバーをインストールします。 | [pgsql_install](cli/cmdbox/pgsql_install.md) |
| pgsql_load | cmdboxのPostgreSQLをロードします。 | [pgsql_load](cli/cmdbox/pgsql_load.md) |
| reboot | コンテナを再起動します。 | [reboot](cli/cmdbox/reboot.md) |
| redis_install | cmdboxのRedisをインストールします。 | [redis_install](cli/cmdbox/redis_install.md) |
| redis_load | cmdboxのRedisをロードします。 | [redis_load](cli/cmdbox/redis_load.md) |
| save | コンテナイメージを保存します。 | [save](cli/cmdbox/save.md) |
| server_install | cmdboxのコンテナをインストールします。 | [server_install](cli/cmdbox/server_install.md) |
| server_load | cmdboxのコンテナイメージをロードします。 | [server_load](cli/cmdbox/server_load.md) |
| uninstall | コンテナをアンインストールします。 | [uninstall](cli/cmdbox/uninstall.md) |
| up | コンテナを起動します。 | [up](cli/cmdbox/up.md) |

### edge (2)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| config | 端末モードの設定を行います。 | [config](cli/edge/config.md) |
| start | 端末モードを起動します。 | [start](cli/edge/start.md) |

### embed (7)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| del | 入力情報の特徴量データを生成するエンベッドモデルの設定を削除します。 | [del](cli/embed/del.md) |
| embedding | 入力情報の特徴量データを生成します。 | [embedding](cli/embed/embedding.md) |
| list | 保存されているエンベッドモデル設定を一覧表示します。 | [list](cli/embed/list.md) |
| load | 入力情報の特徴量データを生成するエンベッドモデルの設定を読み込みます。 | [load](cli/embed/load.md) |
| save | 入力情報の特徴量データを生成するエンベッドモデルの設定を保存します。 | [save](cli/embed/save.md) |
| start | 入力情報の特徴量データを生成するエンベッドモデルを開始します。 | [start](cli/embed/start.md) |
| stop | 入力情報の特徴量データを生成するエンベッドモデルを停止します。 | [stop](cli/embed/stop.md) |

### excel (4)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| cell_details | データフォルダ配下のExcelファイルの指定したセルの詳細情報を取得します。 | [cell_details](cli/excel/cell_details.md) |
| cell_search | データフォルダ配下のExcelファイルの指定したセルの値を検索します。 | [cell_search](cli/excel/cell_search.md) |
| cell_values | データフォルダ配下のExcelファイルの指定したセルの値を取得又は設定します。 | [cell_values](cli/excel/cell_values.md) |
| sheet_list | データフォルダ配下のExcelファイルのシート一覧を取得します。 | [sheet_list](cli/excel/sheet_list.md) |

### extract (6)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| chunklet | 指定されたドキュメントファイルからテキストを抽出します。 | [chunklet](cli/extract/chunklet.md) |
| del | 抽出設定を削除します。 | [del](cli/extract/del.md) |
| list | 保存されている抽出設定を一覧表示します。 | [list](cli/extract/list.md) |
| load | 指定されたファイルからテキストを抽出する設定を読み込みます。 | [load](cli/extract/load.md) |
| pdfplumber | 指定されたドキュメントファイルからテキストを抽出します。 | [pdfplumber](cli/extract/pdfplumber.md) |
| save | 指定されたファイルからテキストを抽出する設定を保存します。 | [save](cli/extract/save.md) |

### gui (2)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| start | GUIモードを起動します。 | [start](cli/gui/start.md) |
| stop | GUIモードを停止します。 | [stop](cli/gui/stop.md) |

### llm (5)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| chat | LLMに対しチャットメッセージを送信します。 | [chat](cli/llm/chat.md) |
| del | LLM 設定を削除します。 | [del](cli/llm/del.md) |
| list | 保存されているLLM設定を一覧表示します。 | [list](cli/llm/list.md) |
| load | LLM 設定を読み込みます。 | [load](cli/llm/load.md) |
| save | LLM 設定を保存します。 | [save](cli/llm/save.md) |

### mcpsv (2)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| start | MCP サーバーを起動します。 | [start](cli/mcpsv/start.md) |
| stop | MCP サーバーを停止します。 | [stop](cli/mcpsv/stop.md) |

### omni (1)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| pred | Omniモデルを使用して、マルチモーダル推論を行います。(実験用) | [pred](cli/omni/pred.md) |

### rag (7)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| build | RAG（検索拡張生成）の設定を元にデータベースを構築します。 | [build](cli/rag/build.md) |
| del | RAG（検索拡張生成）の設定を削除します。 | [del](cli/rag/del.md) |
| list | 保存されているRAG設定を一覧表示します。 | [list](cli/rag/list.md) |
| load | RAG（検索拡張生成）の設定を読み込みます。 | [load](cli/rag/load.md) |
| regist | RAG（検索拡張生成）の登録処理を実行します。 | [regist](cli/rag/regist.md) |
| save | RAG（検索拡張生成）の設定を保存します。 | [save](cli/rag/save.md) |
| search | RAG（検索拡張生成）の検索処理を実行します。 | [search](cli/rag/search.md) |

### server (3)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| list | 起動中のサーバーの一覧を表示します。クライアント環境からの利用も可能です。 | [list](cli/server/list.md) |
| start | サーバーを起動します。installモードで `cmdbox -m install -c server` を実行している場合は、 `docker-compose up -d` を使用してください。 | [start](cli/server/start.md) |
| stop | サーバーを停止します。installモードで `cmdbox -m install -c server` を実行している場合は、 `docker-compose down` を使用してください。 | [stop](cli/server/stop.md) |

### test (3)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| gen_cli_spec | フィーチャーパッケージを解析してCLIコマンド詳細設計書を生成します。 | [gen_cli_spec](cli/test/gen_cli_spec.md) |
| gen_test_spec | CLIコマンド仕様JSONを読み込みユニットテスト仕様書を生成します。 | [gen_test_spec](cli/test/gen_test_spec.md) |
| run_spec | テスト仕様JSONに基づいてテストを実行し、結果を報告します。 | [run_spec](cli/test/run_spec.md) |

### tts (4)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| install | Text-to-Speech(TTS)エンジンをインストールします。 | [install](cli/tts/install.md) |
| list | Text-to-Speech(TTS)エンジンのリストを取得します。 | [list](cli/tts/list.md) |
| say | Text-to-Speech(TTS)エンジンを使ってテキストを音声に変換します。 | [say](cli/tts/say.md) |
| uninstall | Text-to-Speech(TTS)エンジンをアンインストールします。 | [uninstall](cli/tts/uninstall.md) |

### web (14)

| cmd | 概要 | ファイル |
| --- | --- | --- |
| apikey_add | WebモードのユーザーのApiKeyを追加します。 | [apikey_add](cli/web/apikey_add.md) |
| apikey_del | WebモードのユーザーのApiKeyを削除します。 | [apikey_del](cli/web/apikey_del.md) |
| gencert | webモードでSSLを簡易的に実装するために自己署名証明書を生成します。 | [gencert](cli/web/gencert.md) |
| genpass | webモードで使用できるパスワード文字列を生成します。 | [genpass](cli/web/genpass.md) |
| group_add | Webモードのグループを追加します。 | [group_add](cli/web/group_add.md) |
| group_del | Webモードのグループを削除します。 | [group_del](cli/web/group_del.md) |
| group_edit | Webモードのグループを編集します。 | [group_edit](cli/web/group_edit.md) |
| group_list | Webモードのグループー一覧を取得します。 | [group_list](cli/web/group_list.md) |
| start | Webモードを起動します。 | [start](cli/web/start.md) |
| stop | Webモードを停止します。 | [stop](cli/web/stop.md) |
| user_add | Webモードのユーザーを追加します。 | [user_add](cli/web/user_add.md) |
| user_del | Webモードのユーザーを削除します。 | [user_del](cli/web/user_del.md) |
| user_edit | Webモードのユーザーを編集します。 | [user_edit](cli/web/user_edit.md) |
| user_list | Webモードのユーザー一覧を取得します。 | [user_list](cli/web/user_list.md) |
