# audit write

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | audit |
| cmd | write |
| クラス | AuditWrite |
| モジュール | cmdbox.app.features.cli.cmdbox_audit_write |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_audit_write.py |
| 継承元 | AuditBase, ResultEdgeFeature, Validator, Feature |
| Redis | 任意 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: 監査を記録します。
- 英語: Record the audit.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 15 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| --pg_enabled | 真偽値 | いいえ | いいえ | はい | false | True, False | postgresqlデータベース・サーバを使用する場合はTrueを指定します。 |
| --pg_host | 文字列 | いいえ | いいえ | はい | pgsql | - | postgresqlホストを指定する。 |
| --pg_port | 整数 | いいえ | いいえ | はい | 5432 | - | postgresqlのポートを指定する。 |
| --pg_user | 文字列 | いいえ | いいえ | はい | pgsql | - | postgresqlのユーザー名を指定する。 |
| --pg_password | パスワード | いいえ | いいえ | はい | pgsql | - | postgresqlのパスワードを指定する。 |
| --pg_dbname | 文字列 | いいえ | いいえ | はい | audit | - | postgresqlデータベース名を指定します。 |
| --client_only | 真偽値 | いいえ | いいえ | はい | false | True, False | サーバーへの接続を行わないようにします。 |
| --audit_type | 文字列 | はい | いいえ | いいえ | None | user, admin, system, auth, event | 監査の種類を指定します。 |
| --clmsg_id | 文字列 | いいえ | いいえ | いいえ | None | - | クライアントのメッセージIDを指定します。省略した場合はuuid4で生成されます。 |
| --clmsg_date | 日時 | いいえ | いいえ | いいえ | None | - | クライアントのメッセージ発生日時を指定します。省略した場合はサーバーの現在日時が使用されます。 |
| --clmsg_src | 文字列 | いいえ | いいえ | いいえ | None | - | クライアントのメッセージの発生源を指定します。通常 `cmdbox.app.feature.Feature` を継承したクラス名を指定します。 |
| --clmsg_title | 文字列 | いいえ | いいえ | いいえ | None | - | クライアントのメッセージタイトルを指定します。通常コマンドタイトルを指定します。 |
| --clmsg_user | 文字列 | いいえ | いいえ | いいえ | None | - | クライアントのメッセージを発生させたユーザーを指定します。 |
| --clmsg_body | 辞書 | いいえ | はい | いいえ | None | - | クライアントのメッセージの本文を辞書形式で指定します。 |
| --clmsg_tag | 文字列 | いいえ | はい | いいえ | None | - | クライアントのメッセージのタグを指定します。後で検索しやすくするために指定します。 |
| --retention_period_days | 整数 | いいえ | いいえ | はい | 365 | - | 監査を保存する日数を指定します。この日数より古い監査は削除します。0以下を指定すると無期限で保存されます。 |

## 処理内容

### apprun

- 実装元: AuditWrite
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS
- 結果キー候補: success
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 条件 args.clmsg_id is None に応じて分岐する。主な呼出: str, uuid.uuid4
  - 条件 args.clmsg_date is None に応じて分岐する。主な呼出: datetime.now().strftime, common.get_tzoffset_str, datetime.now
  - 条件 hasattr(args, 'client_only') and args.client_only == True を満たす場合は早期終了し、RESP_SUCCESS。結果キー: success
  - audit_type_b64 に convert.str2b64str の結果を格納する
  - clmsg_id_b64 に convert.str2b64str の結果を格納する
  - clmsg_date_b64 に convert.str2b64str の結果を格納する
  - clmsg_body_b64 に convert.str2b64str の結果を格納する
  - clmsg_tag_b64 に convert.str2b64str の結果を格納する
  - pg_host_b64 に convert.str2b64str の結果を格納する
  - pg_user_b64 に convert.str2b64str の結果を格納する
  - pg_password_b64 に convert.str2b64str の結果を格納する
  - pg_dbname_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - cl.redis_cli.send_cmd を呼び出す
  - ret に dict の結果を格納する
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: AuditWrite
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: INT_2, INT_1
- 処理フロー:
  - audit_type に convert.b64str2str の結果を格納する
  - clmsg_id に convert.b64str2str の結果を格納する
  - clmsg_date に convert.b64str2str の結果を格納する
  - clmsg_src に convert.b64str2str の結果を格納する
  - clmsg_title に convert.b64str2str の結果を格納する
  - clmsg_user に convert.b64str2str の結果を格納する
  - clmsg_body に convert.b64str2str の結果を格納する
  - clmsg_tags に convert.b64str2str の結果を格納する
  - pg_host に convert.b64str2str の結果を格納する
  - pg_user に convert.b64str2str の結果を格納する
  - pg_password に convert.b64str2str の結果を格納する
  - pg_dbname に convert.b64str2str の結果を格納する
  - svmsg_id に str の結果を格納する
  - st に self.write の結果を格納する
  - st を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, INT_2, INT_1
- 結果キー候補: success
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### write

- 実装元: AuditWrite
- 役割: 監査ログを書き込む  Args: reskey (str): レスポンスキー audit_type (str): 監査の種類 clmsg_id (str): クライアントメッセージID clmsg_date (str): クライアントメッセージ発生日時 clmsg_src (str): クライアントメッセージの発生源 clmsg_title (str): クライアントメッセージのタイトル clmsg_user (str): クライアントメッセージの発生させたユーザー clmsg_body (str): クライアントメッセージの本文 clmsg_tags (str): クライアントメッセージのタグ svmsg_id (str): サーバーメッセージID pg_enabled (bool): PostgreSQLを使用する場合はTrue pg_host (str): PostgreSQLホスト pg_port (int): PostgreSQLポート pg_user (str): PostgreSQLユーザー pg_password (str): PostgreSQLパスワード pg_dbname (str): PostgreSQLデータベース名 retention_period_days (int): 監査を保存する日数 data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント  Returns: int: レスポンスコード
- 処理概要:
  - 例外処理を伴って処理する。主な呼出: self.initdb, conn.cursor, logger.warning, redis_cli.rpush, conn.commit, cursor.close
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN）

## 単体テスト観点

- 必須パラメータ audit_type が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ pg_enabled, client_only, audit_type の境界値と不正値を確認する
- 複数値パラメータ clmsg_body, clmsg_tag の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, INT_2, INT_1 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_audit_write.py
- apprun 実装元: AuditWrite
- svrun 実装元: AuditWrite
- 生成日時: 2026-04-26T00:53:05
