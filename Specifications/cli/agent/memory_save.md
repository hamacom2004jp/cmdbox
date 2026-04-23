# agent memory_save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | memory_save |
| クラス | AgentMemorySave |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_memory_save |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_memory_save.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: Memory 設定を保存します。
- 英語: Saves memory configuration.

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
| --memory_name | 文字列 | はい | いいえ | いいえ | None | - | Memory設定の名前を指定します。 |
| --memory_type | 文字列 | はい | いいえ | いいえ | memory | , memory, sqlite, postgresql | メモリサービスの種類を指定します。 |
| --llm | 文字列 | いいえ | いいえ | いいえ | None | - | 要約処理で使用するLLM設定名を指定します。 |
| --embed | 文字列 | いいえ | いいえ | いいえ | None | - | 埋込処理で使用するEmbedding設定名を指定します。 |
| --memory_store_pghost | 文字列 | いいえ | いいえ | いいえ | pgsql | - | メモリサービス用PostgreSQLホストを指定します。 |
| --memory_store_pgport | 整数 | いいえ | いいえ | いいえ | 5432 | - | メモリサービス用PostgreSQLポートを指定します。 |
| --memory_store_pguser | 文字列 | いいえ | いいえ | いいえ | pgsql | - | メモリサービス用PostgreSQLのユーザー名を指定します。 |
| --memory_store_pgpass | パスワード | いいえ | いいえ | いいえ | pgsql | - | メモリサービス用PostgreSQLのパスワードを指定します。 |
| --memory_store_pgdbname | 文字列 | いいえ | いいえ | いいえ | pgsql | - | メモリサービス用PostgreSQLのデータベース名を指定します。 |
| --memory_description | 複数行文字列 | いいえ | いいえ | いいえ | cmdboxのメモリ設定 | - | メモリの能力に関する説明を指定します。モデルはこれを使用して、制御をエージェントに委譲するかどうかを決定します。一行の説明で十分であり、推奨されます。 |
| --memory_instruction | 複数行文字列 | いいえ | いいえ | いいえ | あなたはユーザーの期待値を推測することが出来るメモリ管理のエキスパートです。ユーザーとエージェントとの会話の内容のみを根拠に、発言傾向と行動パターンから確認できる事実だけを500文字程度で要約してください。<br>ただし、不明な時は『確認できない』と答えてください。<br>さらに、得た内容を根拠に以下の点を提示してください。<br>１．一貫した思考傾向<br>２．強みの思考パターン<br>３．内面ギャップの可能性<br> | - | メモリが使用するLLMモデル向けの指示を指定します。これはメモリの挙動を促すものになります。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: AgentMemorySave
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 条件 not re.match('^[\\w\\-]+$', args.memory_name) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.memory_type == 'postgresql' を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - configure に dict の結果を格納する
  - payload_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: AgentMemorySave
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

- 必須パラメータ memory_name が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ memory_type, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_memory_save.py
- apprun 実装元: AgentMemorySave
- svrun 実装元: AgentMemorySave
- 生成日時: 2026-04-23T23:39:58
