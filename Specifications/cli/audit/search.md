# audit search

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | audit |
| cmd | search |
| クラス | AuditSearch |
| モジュール | cmdbox.app.features.cli.cmdbox_audit_search |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_audit_search.py |
| 継承元 | AuditBase, ResultEdgeFeature, Feature |
| Redis | 任意 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: 監査ログを検索します。
- 英語: Search the audit log.

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
| --select | 辞書 | いいえ | はい | いいえ | None | - | 取得項目を指定します。指定しない場合は全ての項目を取得します。 |
| --select_date_format | 文字列 | いいえ | いいえ | いいえ | None | , %Y/%m/%d %H:%M, %Y/%m/%d %H, %Y/%m/%d, %Y/%m, %Y, %m, %u | 取得項目の日時のフォーマットを指定します。 |
| --filter_audit_type | 文字列 | いいえ | いいえ | いいえ | None | , user, admin, system, auth, event | フィルタ条件の監査の種類を指定します。 |
| --filter_clmsg_id | 文字列 | いいえ | いいえ | いいえ | None | - | フィルタ条件のクライアントのメッセージIDを指定します。 |
| --filter_clmsg_sdate | 日時 | いいえ | いいえ | いいえ | None | - | フィルタ条件のクライアントのメッセージ発生日時(開始)を指定します。 |
| --filter_clmsg_edate | 日時 | いいえ | いいえ | いいえ | None | - | フィルタ条件のクライアントのメッセージ発生日時(終了)を指定します。 |
| --filter_clmsg_src | 文字列 | いいえ | いいえ | いいえ | None | - | フィルタ条件のクライアントのメッセージの発生源を指定します。LIKE検索を行います。 |
| --filter_clmsg_title | 文字列 | いいえ | いいえ | いいえ | None | - | フィルタ条件のクライアントのメッセージタイトルを指定します。LIKE検索を行います。 |
| --filter_clmsg_user | 文字列 | いいえ | いいえ | いいえ | None | - | フィルタ条件のクライアントのメッセージの発生させたユーザーを指定します。LIKE検索を行います。 |
| --filter_clmsg_body | 辞書 | いいえ | はい | いいえ | None | - | フィルタ条件のクライアントのメッセージの本文を辞書形式で指定します。LIKE検索を行います。 |
| --filter_clmsg_tag | 文字列 | いいえ | はい | いいえ | None | - | フィルタ条件のクライアントのメッセージのタグを指定します。 |
| --filter_svmsg_id | 文字列 | いいえ | いいえ | いいえ | None | - | フィルタ条件のサーバーのメッセージIDを指定します。 |
| --filter_svmsg_sdate | 日時 | いいえ | いいえ | いいえ | None | - | フィルタ条件のサーバーのメッセージ発生日時(開始)を指定します。 |
| --filter_svmsg_edate | 日時 | いいえ | いいえ | いいえ | None | - | フィルタ条件のサーバーのメッセージ発生日時(終了)を指定します。 |
| --groupby | 文字列 | いいえ | はい | いいえ | None | , audit_type, clmsg_id, clmsg_date, clmsg_src, clmsg_title, clmsg_user, clmsg_body, clmsg_tag, svmsg_id, svmsg_date | グループ化項目を指定します。 |
| --groupby_date_format | 文字列 | いいえ | いいえ | いいえ | None | , %Y/%m/%d %H:%M, %Y/%m/%d %H, %Y/%m/%d, %Y/%m, %Y, %m, %u | グループ化項目の日時のフォーマットを指定します。 |
| --sort | 辞書 | いいえ | はい | いいえ | None | - | ソート項目を指定します。 |
| --offset | 整数 | いいえ | いいえ | いいえ | 0 | - | 取得する行の開始位置を指定します。 |
| --limit | 整数 | いいえ | いいえ | いいえ | 100 | - | 取得する行数を指定します。 |
| --csv | 真偽値 | いいえ | いいえ | いいえ | false | False, True | 検索結果をcsvで出力します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: AuditSearch
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - 条件 not hasattr(args, 'format') or not args.format に応じて分岐する。主な呼出: hasattr
  - 条件 not hasattr(args, 'output_json') or not args.output_json に応じて分岐する。主な呼出: hasattr
  - 条件 not hasattr(args, 'output_json_append') or not args.output_json_append に応じて分岐する。主な呼出: hasattr
  - 条件 args.svname is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - select_b64 に convert.str2b64str の結果を格納する
  - select_date_format_b64 に convert.str2b64str の結果を格納する
  - groupby_b64 に convert.str2b64str の結果を格納する
  - groupby_date_format_b64 に convert.str2b64str の結果を格納する
  - sort_str に json.dumps の結果を格納する
  - sort_b64 に convert.str2b64str の結果を格納する
  - offset に getattr の結果を格納する
  - limit に getattr の結果を格納する
  - filter_audit_type_b64 に convert.str2b64str の結果を格納する
  - filter_clmsg_id_b64 に convert.str2b64str の結果を格納する
  - filter_clmsg_sdate_b64 に convert.str2b64str の結果を格納する
  - filter_clmsg_edate_b64 に convert.str2b64str の結果を格納する
  - filter_clmsg_src_b64 に convert.str2b64str の結果を格納する
  - filter_clmsg_title_b64 に convert.str2b64str の結果を格納する
  - filter_clmsg_user_b64 に convert.str2b64str の結果を格納する
  - filter_clmsg_body_b64 に convert.str2b64str の結果を格納する
  - filter_clmsg_tag_b64 に convert.str2b64str の結果を格納する
  - filter_svmsg_id_b64 に convert.str2b64str の結果を格納する
  - filter_svmsg_sdate_b64 に convert.str2b64str の結果を格納する
  - filter_svmsg_edate_b64 に convert.str2b64str の結果を格納する
  - pg_host_b64 に convert.str2b64str の結果を格納する
  - pg_user_b64 に convert.str2b64str の結果を格納する
  - pg_password_b64 に convert.str2b64str の結果を格納する
  - pg_dbname_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 条件 'data' in ret['success'] に応じて分岐する。主な呼出: list, row.keys, sorted, hasattr, io.StringIO, csv.DictWriter
  - common.print_format を呼び出す
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: AuditSearch
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: INT_0, INT_1, INT_2
- 処理フロー:
  - select に json.loads の結果を格納する
  - select_date_format に convert.b64str2str の結果を格納する
  - groupby に json.loads の結果を格納する
  - groupby_date_format に convert.b64str2str の結果を格納する
  - sort に json.loads の結果を格納する
  - filter_audit_type に convert.b64str2str の結果を格納する
  - filter_clmsg_id に convert.b64str2str の結果を格納する
  - filter_clmsg_sdate に convert.b64str2str の結果を格納する
  - filter_clmsg_edate に convert.b64str2str の結果を格納する
  - filter_clmsg_src に convert.b64str2str の結果を格納する
  - filter_clmsg_title に convert.b64str2str の結果を格納する
  - filter_clmsg_user に convert.b64str2str の結果を格納する
  - body に json.loads の結果を格納する
  - tags に json.loads の結果を格納する
  - filter_svmsg_id に convert.b64str2str の結果を格納する
  - filter_svmsg_sdate に convert.b64str2str の結果を格納する
  - filter_svmsg_edate に convert.b64str2str の結果を格納する
  - pg_host に convert.b64str2str の結果を格納する
  - pg_user に convert.b64str2str の結果を格納する
  - pg_password に convert.b64str2str の結果を格納する
  - pg_dbname に convert.b64str2str の結果を格納する
  - st に self.search の結果を格納する
  - st を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_0, INT_1, INT_2
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### search

- 実装元: AuditSearch
- 役割: 監査ログを検索する  Args: reskey (str): レスポンスキー select (Dict[str, str]): 取得項目 select_date_format (str): 取得項目の日時フォーマット groupby (List[str]): グループ化項目 groupby_date_format (str): グループ化項目の日時フォーマット sort (Dict[str, str]): ソート条件 offset (int): 取得する行の開始位置 limit (int): 取得する行数 filter_audit_type (str): 監査の種類 filter_clmsg_id (str): クライアントメッセージID filter_clmsg_sdate (str): クライアントメッセージ発生日時(開始) filter_clmsg_edate (str): クライアントメッセージ発生日時(終了) filter_clmsg_src (str): クライアントメッセージの発生源 filter_clmsg_title (str): クライアントメッセージのタイトル filter_clmsg_user (str): クライアントメッセージの発生させたユーザー filter_clmsg_body (Dict[str, Any]): クライアントメッセージの本文 filter_clmsg_tags (List[str]): クライアントメッセージのタグ filter_svmsg_id (str): サーバーメッセージID filter_svmsg_sdate (str): サーバーメッセージ発生日時(開始) filter_svmsg_edate (str): サーバーメッセージ発生日時(終了) pg_enabled (bool): PostgreSQLを使用する場合はTrue pg_host (str): PostgreSQLホスト pg_port (int): PostgreSQLポート pg_user (str): PostgreSQLユーザー pg_password (str): PostgreSQLパスワード pg_dbname (str): PostgreSQLデータベース名 data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント  Returns: int: レスポンスコード
- 処理概要:
  - 例外処理を伴って処理する。主な呼出: self.initdb, conn.cursor, logger.warning, redis_cli.rpush, select.items, cursor.execute
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN）

## 単体テスト観点

- 選択肢を持つパラメータ pg_enabled, select_date_format, filter_audit_type, groupby, groupby_date_format, csv, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ select, filter_clmsg_body, filter_clmsg_tag, groupby, sort の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_0, INT_1, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_audit_search.py
- apprun 実装元: AuditSearch
- svrun 実装元: AuditSearch
- 生成日時: 2026-04-19T20:59:07
