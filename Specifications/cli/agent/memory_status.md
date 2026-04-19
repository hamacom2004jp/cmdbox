# agent memory_status

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | memory_status |
| クラス | AgentMemoryStatus |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_memory_status |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_memory_status.py |
| 継承元 | AgentBase, ResultEdgeFeature, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: Agentのメモリステータスを取得します。
- 英語: Get the memory status for the agent.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 120 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| --runner_name | 文字列 | はい | いいえ | いいえ | None | - | Runner設定の名前を指定します。 |
| --user_name | 文字列 | はい | いいえ | いいえ | None | - | ユーザー名を指定します。 |
| --memory_query | 複数行文字列 | いいえ | いいえ | いいえ | None | - | メモリ内容を検索するクエリを指定します。意味検索を行います。 |
| --memory_fetch_offset | 整数 | いいえ | いいえ | いいえ | 0 | - | メモリ内容を取得する時の開始位置を指定します。 |
| --memory_fetch_count | 整数 | いいえ | いいえ | いいえ | 10 | - | メモリ内容を取得する件数を指定します。 |
| --memory_fetch_summary | 真偽値 | いいえ | いいえ | いいえ | false | False, True | 取得したメモリ内容を要約するかどうかを指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: AgentMemoryStatus
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - 条件 not getattr(args, 'runner_name', None) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not re.match('^[\\w\\-]+$', args.runner_name) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not getattr(args, 'user_name', None) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - payload に dict の結果を格納する
  - payload_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: AgentMemoryStatus
- 終了コード候補: INT_1, RESP_SUCCESS, INT_0, RESP_WARN, INT_2
- 処理フロー:
  - 例外処理を伴って処理する。主な呼出: json.loads, payload.get, self.load_conf, self.create_memory_service, responce.memories.sort, responce.model_dump
  - FileNotFoundError を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN）
  - json.JSONDecodeError を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN）
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN）

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_0, INT_2
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### add_memory

- 実装元: AgentMemoryStatus
- 処理概要:
  - session.events.append を呼び出す

### create_memory_service

- 実装元: AgentMemoryStatus
- 役割: メモリーサービスを作成します  Args: data_dir (Path): データディレクトリパス logger (logging.Logger): ロガー memory_conf (Dict[str, Any]): メモリー設定 memory_llm_conf (Dict[str, Any]): メモリー用LLM設定 memory_embed_conf (Dict[str, Any]): メモリー用埋め込みモデル設定 sessions (Dict[str, Dict[str, Any]]): セッション情報辞書  Returns: BaseMemoryService: メモリーサービス
- 処理概要:
  - memory_type に memory_conf.get の結果を格納する
  - device に memory_embed_conf.get の結果を格納する
  - embed_name に memory_embed_conf.get の結果を格納する
  - embed_model に memory_embed_conf.get の結果を格納する
  - 条件 memory_type == 'memory' を満たす場合は早期終了し、INT_0

### summary

- 実装元: AgentMemoryStatus
- 処理概要:
  - (st, res) に self.llm_chat.chat の結果を格納する
  - 条件 st != self.RESP_SUCCESS に応じて分岐する。主な呼出: Exception
  - res を返却する

## 単体テスト観点

- 必須パラメータ runner_name, user_name が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ memory_fetch_summary, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_0, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_memory_status.py
- apprun 実装元: AgentMemoryStatus
- svrun 実装元: AgentMemoryStatus
- 生成日時: 2026-04-19T20:59:06
