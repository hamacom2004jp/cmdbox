# agent mcp_client

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | mcp_client |
| クラス | AgentMcpClient |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_mcp_client |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_mcp_client.py |
| 継承元 | UnsupportEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: リモートMCPサーバーにリクエストを行うMCPクライアントを起動します。
- 英語: Starts an MCP client that makes requests to a remote MCP server.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --mcpserver_name | 文字列 | はい | いいえ | いいえ | mcpserver | - | リモートMCPサーバーの名前を指定します。省略した場合は`mcpserver`となります。 |
| --mcpserver_url | 文字列 | はい | いいえ | いいえ | http://localhost:8091/mcp | - | リモートMCPサーバーのURLを指定します。省略した場合は`http://localhost:8091/mcp`となります。 |
| --mcpserver_apikey | パスワード | いいえ | いいえ | いいえ | None | - | リモートMCPサーバーのAPI Keyを指定します。 |
| --mcpserver_transport | 文字列 | はい | いいえ | いいえ | streamable-http | , streamable-http, sse, http | リモートMCPサーバーのトランスポートを指定します。省略した場合は`streamable-http`となります。 |
| --operation | 文字列 | はい | いいえ | いいえ | list_tools | list_tools, call_tool, list_resources, read_resource, list_prompts, get_prompt | リモートMCPサーバーに要求する操作を指定します。省略した場合は`list_tools`となります。 |
| --tool_name | 文字列 | いいえ | いいえ | いいえ | None | - | リモートMCPサーバーで実行するツールの名前を指定します。 |
| --tool_args | 辞書 | いいえ | はい | いいえ | None | - | リモートMCPサーバーで実行するツールの引数を指定します。 |
| --mcp_timeout | 整数 | いいえ | いいえ | いいえ | 60 | - | リモートMCPサーバーの応答が返ってくるまでの最大待ち時間を指定します。 |
| --resource_url | 文字列 | いいえ | いいえ | いいえ | None | - | リモートMCPサーバーから取得するリソースのURLを指定します。 |
| --prompt_name | 文字列 | いいえ | いいえ | いいえ | None | - | リモートMCPサーバーから取得するプロンプトの名前を指定します。 |
| --prompt_args | 辞書 | いいえ | はい | いいえ | None | - | リモートMCPサーバーから取得するプロンプトの引数を指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: AgentMcpClient
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_ERROR
- 結果キー候補: warn, success
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - config に dict の結果を格納する
  - 例外処理を伴って処理する。主な呼出: common.reset_logger, Client, common.print_format, logger.debug, logger.setLevel, logger.error
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_ERROR / 結果キー: warn）

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_ERROR
- 結果キー候補: warn, success
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 選択肢を持つパラメータ mcpserver_transport, operation, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ tool_args, prompt_args の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_ERROR の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_mcp_client.py
- apprun 実装元: AgentMcpClient
- svrun 実装元: Feature
- 生成日時: 2026-04-23T23:39:57
