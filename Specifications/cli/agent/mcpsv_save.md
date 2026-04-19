# agent mcpsv_save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | mcpsv_save |
| クラス | AgentMcpSave |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_mcpsv_save |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_mcpsv_save.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: MCP サーバ設定を保存します。
- 英語: Saves MCP server configuration.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 60 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| --mcpserver_name | 文字列 | はい | いいえ | いいえ | mcpserver | - | リモートMCPサーバーの名前を指定します。省略した場合は`mcpserver`となります。 |
| --mcpserver_url | 文字列 | はい | いいえ | いいえ | http://localhost:8091/mcp | - | リモートMCPサーバーのURLを指定します。省略した場合は`http://localhost:8091/mcp`となります。 |
| --mcpserver_delegated_auth | 真偽値 | いいえ | いいえ | いいえ | false | True, False | リモートMCPサーバーの認証を現在のログインユーザーのAPI Keyを使用して行います。 |
| --mcpserver_apikey | パスワード | いいえ | いいえ | いいえ | None | - | A2A Server起動時のリモートMCPサーバーのAPI Keyを指定します。 `mcpserver_delegated_auth` が無効な場合は、MCP実行時に使用も使用されます。 |
| --mcpserver_transport | 文字列 | はい | いいえ | いいえ | streamable-http | , streamable-http, sse | リモートMCPサーバーのトランスポートを指定します。省略した場合は`streamable-http`となります。 |
| --mcp_tools | 複数選択リスト | いいえ | いいえ | いいえ | None | - | リモートサーバーが提供しているツールを指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: AgentMcpSave
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - 条件 not hasattr(args, 'mcpserver_name') or args.mcpserver_name is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not hasattr(args, 'mcpserver_url') or args.mcpserver_url is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not re.match('^[\\w\\-]+$', args.mcpserver_name) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not args.mcpserver_delegated_auth and (not hasattr(args, 'mcpserver_apikey') or args.mcpserver_ap... を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - configure に dict の結果を格納する
  - payload_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: AgentMcpSave
- 終了コード候補: INT_1, RESP_SUCCESS, RESP_WARN, INT_2
- 結果キー候補: success, warn
- 処理フロー:
  - 例外処理を伴って処理する。主な呼出: json.loads, configure.get, configure_path.parent.mkdir, dict, redis_cli.rpush, convert.b64str2str
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_2
- 結果キー候補: warn, success
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 選択肢を持つパラメータ mcpserver_delegated_auth, mcpserver_transport, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_mcpsv_save.py
- apprun 実装元: AgentMcpSave
- svrun 実装元: AgentMcpSave
- 生成日時: 2026-04-19T20:59:05
