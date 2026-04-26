# audit createdb

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | audit |
| cmd | createdb |
| クラス | AuditCreatedb |
| モジュール | cmdbox.app.features.cli.cmdbox_audit_createdb |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_audit_createdb.py |
| 継承元 | UnsupportEdgeFeature, Validator, Feature |
| Redis | 任意 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: 監査を記録するデータベースを作成します。
- 英語: Create a database to record audits.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --pg_host | 文字列 | はい | いいえ | いいえ | pgsql | - | postgresqlホストを指定する。 |
| --pg_port | 整数 | はい | いいえ | いいえ | 5432 | - | postgresqlのポートを指定する。 |
| --pg_user | 文字列 | はい | いいえ | いいえ | pgsql | - | postgresqlのユーザー名を指定する。 |
| --pg_password | パスワード | はい | いいえ | いいえ | pgsql | - | postgresqlのパスワードを指定する。 |
| --pg_dbname | 文字列 | はい | いいえ | いいえ | postgresql | - | postgresqlデータベース名を指定します。 |
| --new_pg_dbname | 文字列 | はい | いいえ | いいえ | audit | - | 新しいpostgresqlデータベース名を指定します。 |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 15 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |

## 処理内容

### apprun

- 実装元: AuditCreatedb
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - pg_host_b64 に convert.str2b64str の結果を格納する
  - pg_user_b64 に convert.str2b64str の結果を格納する
  - pg_password_b64 に convert.str2b64str の結果を格納する
  - pg_dbname_b64 に convert.str2b64str の結果を格納する
  - new_pg_dbname_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: AuditCreatedb
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: INT_2, INT_1
- 処理フロー:
  - pg_host に convert.b64str2str の結果を格納する
  - pg_user に convert.b64str2str の結果を格納する
  - pg_password に convert.b64str2str の結果を格納する
  - pg_dbname に convert.b64str2str の結果を格納する
  - new_pg_dbname に convert.b64str2str の結果を格納する
  - st に self.createdb の結果を格納する
  - st を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_2, INT_1
- 結果キー候補: 抽出なし
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### createdb

- 実装元: AuditCreatedb
- 役割: 監査ログデータベースを作成する  Args: reskey (str): レスポンスキー pg_host (str): PostgreSQLホスト pg_port (int): PostgreSQLポート pg_user (str): PostgreSQLユーザー pg_password (str): PostgreSQLパスワード pg_dbname (str): PostgreSQLデータベース名 new_pg_dbname (str): 新しいPostgreSQLデータベース名 data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント  Returns: int: レスポンスコード
- 処理概要:
  - 例外処理を伴って処理する。主な呼出: psycopg.connect, conn.cursor, logger.warning, redis_cli.rpush, cursor.execute, cursor.close
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN）

## 単体テスト観点

- 終了コード RESP_SUCCESS, RESP_WARN, INT_2, INT_1 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_audit_createdb.py
- apprun 実装元: AuditCreatedb
- svrun 実装元: AuditCreatedb
- 生成日時: 2026-04-26T00:53:05
