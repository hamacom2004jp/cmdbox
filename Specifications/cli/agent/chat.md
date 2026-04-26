# agent chat

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | chat |
| クラス | AgentChat |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_chat |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_agent_chat.py |
| 継承元 | AgentBase, ResultEdgeFeature, Validator, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: Agentとチャットを行います。
- 英語: Chat with the agent.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 600 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| --runner_name | 文字列 | はい | いいえ | いいえ | None | - | Runner設定の名前を指定します。 |
| --user_name | 文字列 | はい | いいえ | いいえ | None | - | ユーザー名を指定します。 |
| --session_id | 文字列 | いいえ | いいえ | いいえ | None | - | Runnerに送信するセッションIDを指定します。 |
| --a2asv_apikey | パスワード | いいえ | いいえ | いいえ | None | - | A2A ServerのAPI Keyを指定します。 |
| --mcpserver_apikey | パスワード | いいえ | いいえ | いいえ | None | - | リモートMCPサーバーのAPI Keyを指定します。 |
| --message | 複数行文字列 | はい | いいえ | いいえ | None | - | Runnerに送信するメッセージを指定します。 |
| --call_tts | 真偽値 | いいえ | いいえ | はい | false | True, False | TTS(Text-to-Speech)機能を実行するかどうかを指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: AgentChat
- 終了コード候補: RESP_SUCCESS, INT_0, RESP_WARN
- 結果キー候補: success, warn
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 条件 not re.match('^[\\w\\-]+$', args.runner_name) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - payload に dict の結果を格納する
  - payload_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - msg に dict の結果を格納する
  - self.apprun_generate(logger, host=args.host, port=args.port, password=args.password, svname=args.... を走査し、(st, res) ごとに処理する。主な呼出: self.apprun_generate, msg['success'].append, msg['warn'].append
  - 条件 len(msg['success']) <= 0 に応じて分岐する。主な呼出: len
  - 条件 len(msg['warn']) > 0 を満たす場合は早期終了し、INT_0, RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: AgentChat
- 終了コード候補: INT_1, RESP_SUCCESS, RESP_WARN, INT_2, INT_0
- 結果キー候補: success, end, warn
- 処理フロー:
  - 例外処理を伴って処理する。主な呼出: json.loads, payload.get, re.compile, self.load_conf, self.create_agent, self.memory.create_memory_service
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn, end）

## 処理結果

- 終了コード候補: RESP_SUCCESS, INT_0, RESP_WARN, INT_1, INT_2
- 結果キー候補: success, warn, end
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### apprun_generate

- 実装元: AgentChat
- 役割: Agentチャットを実行します  Args: logger (logging.Logger): ロガー host (str): Redisホスト port (int): Redisポート password (str): Redisパスワード svname (str): サービス名 retry_interval (int): 再接続インターバル秒数 retry_count (int): 再接続回数 timeout (int): タイムアウト秒数 runner_name (str): Runner設定名 user_name (str): ユーザー名 session_id (str): セッションID a2asv_apikey (str): A2A Server API Key mcpserver_apikey (str): MCPサーバーAPI Key message (str): メッセージ call_tts (bool): TTS機能を呼び出すかどうか Yields: Tuple[int, Any]: 処理結果ステータスと内容
- 処理概要:
  - payload に dict の結果を格納する
  - payload_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - msg に dict の結果を格納する
  - cl.redis_cli.send_cmd_sse(self.get_svcmd(), [payload_b64], retry_count=retry_count, retry_interva... を走査し、res ごとに処理する。主な呼出: cl.redis_cli.send_cmd_sse, self.get_svcmd

### create_agent

- 実装元: AgentChat
- 役割: エージェントを作成します  Args: logger (logging.Logger): ロガー data_dir (Path): データディレクトリパス disable_remote_agent (bool): リモートエージェントを無効化するかどうか agent_conf (Dict[str, Any]): エージェント設定 llm_conf (Dict[str, Any]): LLM設定 mcpsv_confs (List[Dict[str, Any]]): MCPサーバー設定リスト  Returns: Agent: エージェント
- 処理概要:
  - 条件 logger.level == logging.DEBUG に応じて分岐する。主な呼出: logger.debug
  - description に agent_conf.get の結果を格納する
  - instruction に agent_conf.get の結果を格納する
  - 条件 logger.level == logging.DEBUG に応じて分岐する。主な呼出: logger.debug
  - 条件 logger.level == logging.DEBUG に応じて分岐する。主な呼出: logger.debug
  - common.reset_logger を呼び出す
  - common.reset_logger を呼び出す
  - common.reset_logger を呼び出す
  - common.reset_logger を呼び出す
  - common.reset_logger を呼び出す
  - common.reset_logger を呼び出す
  - common.reset_logger を呼び出す
  - agent_name に agent_conf.get の結果を格納する
  - agent_type に agent_conf.get の結果を格納する
  - use_planner に agent_conf.get の結果を格納する
  - a2asv_baseurl に agent_conf.get の結果を格納する
  - a2asv_delegated_auth に agent_conf.get の結果を格納する
  - a2asv_apikey に agent_conf.get の結果を格納する
  - agent_subagents に agent_conf.get の結果を格納する
  - 条件 'subagents' in agent_conf and isinstance(agent_subagents, list) に応じて分岐する。主な呼出: isinstance, create_subagent, subagents.append
  - llmprov に llm_conf.get の結果を格納する
  - 条件 agent_type == 'remote' and (not disable_remote_agent) を満たす場合は早期終了し、INT_0
  - 条件 logger.level == logging.DEBUG に応じて分岐する。主な呼出: logger.debug
  - agent を返却する

### create_tool_mcpsv

- 実装元: AgentChat
- 役割: MCPサーバーツールを作成します Args: logger (logging.Logger): ロガー mcpsv_confs (List[Dict[str, Any]]): MCPサーバー設定リスト Returns: List[MCPToolset]: MCPToolsetのリスト
- 処理概要:
  - auth_scheme に HTTPBearer の結果を格納する
  - mcpsv_confs を走査し、mcpsv_conf ごとに処理する。主な呼出: mcpsv_conf.get, AuthCredential, MCPToolset, tools.append, SseConnectionParams, StreamableHTTPConnectionParams
  - tools を返却する

## 単体テスト観点

- 必須パラメータ runner_name, user_name, message が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ call_tts, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー success, warn, end が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, INT_0, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_agent_chat.py
- apprun 実装元: AgentChat
- svrun 実装元: AgentChat
- 生成日時: 2026-04-26T00:53:04
