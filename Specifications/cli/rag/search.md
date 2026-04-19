# rag search

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | rag |
| cmd | search |
| クラス | RagSearch |
| モジュール | cmdbox.app.features.cli.cmdbox_rag_search |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_rag_search.py |
| 継承元 | RAGBase, ResultEdgeFeature, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | 不明 |

## 概要

- 日本語: RAG（検索拡張生成）の検索処理を実行します。
- 英語: Execute the RAG (Retrieval-Augmented Generation) search process.

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
| --rag_name | 文字列 | はい | いいえ | いいえ | None | - | 登録に使用するRAG設定の名前を指定します。 |
| --query | 文字列 | いいえ | いいえ | いいえ | None | - | 検索クエリーを指定します。 |
| --kcount | 整数 | はい | いいえ | いいえ | 5 | - | 検索結果件数を指定します。フィルタ条件を指定するとここで指定した件数の中からフィルタします。 |
| --select | 文字列 | いいえ | はい | いいえ | None | - | 取得する項目を指定します。未指定の場合はすべての項目を返します。 |
| --filter_origin_name | 文字列 | いいえ | いいえ | いいえ | None | - | フィルタ条件のorigin_nameを指定します。 |
| --filter_dict | 辞書 | いいえ | はい | いいえ | None | - | 任意のフィルタ条件を指定します。cmetaの項目名と項目値を複数指定できます。項目値は `％` を使用することであいまい検索できます。 {args.query}という表記を含めるとqueryパラメータの値を使用できます。 |
| --sort_dict | 辞書 | いいえ | はい | いいえ | None | , ASC, DESC | queryを指定しないときのソート条件を指定します。cmetaの項目名とソート順（ `ASC` (昇順) 又は `DESC` (降順)）を複数指定できます。 |
| --data | ディレクトリ | はい | いいえ | いいえ | C:\Users\hama\.cmdbox | - | 省略した時は `$HONE/.cmdbox` を使用します。 |
| --signin_file | ファイル | はい | いいえ | いいえ | None | - | サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.cmdbox/user_list.yml' を指定します。 |
| --groups | 文字列 | はい | はい | はい | None | - | `signin_file` を指定した場合に、このユーザーグループに許可されているコマンドリストを返すように指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |

## 処理内容

### apprun

- 実装元: RagSearch
- 終了コード候補: RESP_WARN, RESP_SUCCESS, INT_0
- 結果キー候補: warn, success, res
- 処理フロー:
  - 条件 not hasattr(args, 'rag_name') or args.rag_name is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not re.match('^[\\w\\-]+$', args.rag_name) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not hasattr(args, 'data') or args.data is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not hasattr(args, 'groups') or args.groups is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not hasattr(args, 'signin_file') or args.signin_file is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not hasattr(args, 'kcount') or args.kcount is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - options に Options.getInstance の結果を格納する
  - cl に client.Client の結果を格納する
  - 例外処理を伴って処理する。主な呼出: self.load_rag_config, self.check_signin, self.embedstart, rag_store.RagStore.create, store.connect, store.select_doc
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_WARN, RESP_SUCCESS, INT_0
- 結果キー候補: warn, success, res
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 必須パラメータ rag_name, signin_file, groups が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ sort_dict, output_json_append, stdout_log の境界値と不正値を確認する
- 複数値パラメータ select, filter_dict, sort_dict, groups の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn, success, res が期待どおり構成されることを確認する
- 終了コード RESP_WARN, RESP_SUCCESS, INT_0 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_rag_search.py
- apprun 実装元: RagSearch
- svrun 実装元: Feature
- 生成日時: 2026-04-19T20:59:11
