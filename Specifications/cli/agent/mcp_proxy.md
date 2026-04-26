# agent mcp_proxy

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | mcp_proxy |
| クラス | AgentMcpProxy |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_mcp_proxy |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_agent_mcp_proxy.py |
| 継承元 | UnsupportEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: 標準入力を受け付け、リモートMCPサーバーにリクエストを行うProxyサーバーを起動します。
- 英語: Starts a Proxy server that accepts standard input and makes requests to a remote MCP server.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --mcpserver_name | 文字列 | はい | いいえ | いいえ | mcpserver | - | リモートMCPサーバーの名前を指定します。省略した場合は`mcpserver`となります。 |
| --mcpserver_url | 文字列 | はい | いいえ | いいえ | http://localhost:8091/mcp | - | リモートMCPサーバーのURLを指定します。省略した場合は`http://localhost:8091/mcp`となります。 |
| --mcpserver_apikey | パスワード | いいえ | いいえ | いいえ | None | - | リモートMCPサーバーのAPI Keyを指定します。 |
| --mcpserver_transport | 文字列 | はい | いいえ | いいえ | streamable-http | , streamable-http, sse, http | リモートMCPサーバーのトランスポートを指定します。省略した場合は`streamable-http`となります。 |

## 処理内容

### apprun

- 実装元: AgentMcpProxy
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_ERROR
- 結果キー候補: info, warn
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - config に dict の結果を格納する
  - 例外処理を伴って処理する。主な呼出: common.reset_logger, FastMCP.as_proxy, proxy.run, logger.setLevel, logger.error, h.setLevel
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_ERROR / 結果キー: warn）
  - 終了コード RESP_SUCCESS / 結果キー info を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_ERROR
- 結果キー候補: info, warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 選択肢を持つパラメータ mcpserver_transport の境界値と不正値を確認する
- 結果オブジェクトのキー info, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_ERROR の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_agent_mcp_proxy.py
- apprun 実装元: AgentMcpProxy
- svrun 実装元: Feature
- 生成日時: 2026-04-26T00:53:04
