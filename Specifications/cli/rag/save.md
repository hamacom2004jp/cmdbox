# rag save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | rag |
| cmd | save |
| クラス | RagSave |
| モジュール | cmdbox.app.features.cli.cmdbox_rag_save |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_rag_save.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: RAG（検索拡張生成）の設定を保存します。
- 英語: Saves the settings for RAG (Retrieval-Augmented Generation).

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
| --rag_name | 文字列 | はい | いいえ | いいえ | None | - | RAG設定の名前を指定します。 |
| --rag_type | 文字列 | はい | いいえ | いいえ | vector | , vector_pg, vector_sqlite, graph_n4j, graph_pg | RAGの種類を指定します。 |
| --extract | 文字列 | はい | はい | いいえ | None | - | RAGで使用するExtract処理の登録名を指定します。候補がない場合はextractモードのコマンドの登録が必要です。 |
| --embed | 文字列 | いいえ | いいえ | いいえ | None | - | rag_typeがvectorの場合、エンベッドモデルの登録名を指定します。 |
| --embed_vector_dim | 整数 | いいえ | いいえ | いいえ | 256 | - | Embed時のベクトル次元数を指定します。 |
| --savetype | 文字列 | いいえ | いいえ | いいえ | per_doc | per_doc, per_service, add_only | 保存パターンを指定します。 `per_doc` :ドキュメント単位、 `per_service` :サービス単位、 `add_only` :追加のみ |
| --vector_store_pghost | 文字列 | いいえ | いいえ | いいえ | pgsql | - | VecRAG保存先用PostgreSQLホストを指定します。 |
| --vector_store_pgport | 整数 | いいえ | いいえ | いいえ | 5432 | - | VecRAG保存先用PostgreSQLポートを指定します。 |
| --vector_store_pguser | 文字列 | いいえ | いいえ | いいえ | pgsql | - | VecRAG保存先用PostgreSQLユーザー名を指定します。 |
| --vector_store_pgpass | パスワード | いいえ | いいえ | いいえ | pgsql | - | VecRAG保存先用PostgreSQLパスワードを指定します。 |
| --vector_store_pgdbname | 文字列 | いいえ | いいえ | いいえ | pgsql | - | VecRAG保存先用PostgreSQLデータベース名を指定します。 |
| --graph_store_pghost | 文字列 | いいえ | いいえ | いいえ | pgsql | - | GraphRAG保存先用PostgreSQLホストを指定します。 |
| --graph_store_pgport | 整数 | いいえ | いいえ | いいえ | 5432 | - | GraphRAG保存先用PostgreSQLポートを指定します。 |
| --graph_store_pguser | 文字列 | いいえ | いいえ | いいえ | pgsql | - | GraphRAG保存先用PostgreSQLユーザー名を指定します。 |
| --graph_store_pgpass | パスワード | いいえ | いいえ | いいえ | pgsql | - | GraphRAG保存先用PostgreSQLパスワードを指定します。 |
| --graph_store_pgdbname | 文字列 | いいえ | いいえ | いいえ | pgsql | - | GraphRAG保存先用PostgreSQLデータベース名を指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |

## 処理内容

### apprun

- 実装元: RagSave
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - 条件 not hasattr(args, 'rag_name') or args.rag_name is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not re.match('^[\\w\\-]+$', args.rag_name) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not hasattr(args, 'rag_type') or args.rag_type is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not hasattr(args, 'savetype') or args.savetype not in ['per_doc', 'per_page', 'per_service', 'add... を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - payload に dict の結果を格納する
  - payload_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: RagSave
- 終了コード候補: INT_1, RESP_SUCCESS, RESP_WARN, INT_2
- 結果キー候補: success, warn
- 処理フロー:
  - 例外処理を伴って処理する。主な呼出: json.loads, configure_path.parent.mkdir, dict, redis_cli.rpush, convert.b64str2str, configure_path.open
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_2
- 結果キー候補: warn, success
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 必須パラメータ rag_name, extract が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ rag_type, savetype, output_json_append, stdout_log の境界値と不正値を確認する
- 複数値パラメータ extract の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_rag_save.py
- apprun 実装元: RagSave
- svrun 実装元: RagSave
- 生成日時: 2026-04-19T20:59:11
