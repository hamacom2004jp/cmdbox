# extract chunklet

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | extract |
| cmd | chunklet |
| クラス | ExtractChunklet |
| モジュール | cmdbox.app.features.cli.cmdbox_extract_chunklet |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_extract_chunklet.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: 指定されたドキュメントファイルからテキストを抽出します。
- 英語: Extracts text from the specified document file.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。 |
| --scope | 文字列 | はい | いいえ | いいえ | current | , client, current, server | 参照先スコープを指定します。指定可能な画像タイプは `client` , `current` , `server` です。 |
| --fwpath | ファイル | はい | はい | いいえ | None | - | 指定したパスが範囲外であるかどうかを判定するパスを指定します。このパスの配下でない場合エラーにします。 |
| --loadpath | ファイル | はい | いいえ | いいえ | None | - | 読み込みファイルパスを指定します。 |
| --client_data | 文字列 | いいえ | いいえ | いいえ | None | - | ローカルを参照させる場合のデータフォルダのパスを指定します。 |
| --chunk_lang | 文字列 | いいえ | いいえ | いいえ | auto | auto, ja, en | チャンキングするテキストの言語を指定します。`auto` を指定した場合は自動で言語を判定します。 |
| --chunk_max_token_counter | 文字列 | いいえ | いいえ | いいえ | gpt-4o | - | チャンキングするテキストの最大トークン数を指定します。 |
| --chunk_max_tokens | 整数 | いいえ | いいえ | いいえ | 1024 | - | チャンキングするテキストの最大トークン数を指定します。 |
| --chunk_max_sentences | 整数 | いいえ | いいえ | いいえ | 4 | - | チャンキングするテキストの最大文数(文字数ではない)を指定します。 |
| --chunk_overlap_percent | 整数 | いいえ | いいえ | いいえ | 20 | - | チャンクのオーバーラップ割合を指定します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 120 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |

## 処理内容

### apprun

- 実装元: ExtractChunklet
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 例外処理を伴って処理する。主な呼出: Path, logger.warning, args.client_data.replace, filer.Filer, f._file_exists, f.check_fwpath
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

### svrun

- 実装元: ExtractChunklet
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: RESP_SUCCESS, INT_1, RESP_WARN, INT_0, INT_2
- 処理フロー:
  - 例外処理を伴って処理する。主な呼出: json.loads, filer.Filer, f._file_exists, f.check_fwpath, argparse.Namespace, self.extract
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN）
  - 終了コード RESP_SUCCESS を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_0, INT_2
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### choice_chunk_max_token_counter

- 実装元: ExtractChunklet
- 役割: オプションのchoiceを動的に生成する関数  Args: o (Dict[str, Any]): choice_fn関数が呼ばれたコマンドオプションのchoice定義 webmode (bool): Webモードかどうか opt (Dict[str, Any]): このコマンドのすべてのコマンドオプションのchoice定義  Returns: Any: choice情報
- 処理概要:
  - [''] + sorted([k for k in model.MODEL_TO_ENCODING.keys()]) を返却する

### extract

- 実装元: ExtractChunklet
- 役割: 指定されたファイルからテキストを抽出します  Args: abspath (Path): 抽出対象ファイルの絶対パス args (argparse.Namespace): 引数 logger (logging.Logger): ロガー tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報 Returns: Dict[str, Any]: 抽出結果
- 処理概要:
  - 例外処理を伴って処理する。主な呼出: DocumentChunker, enumerate, dict, logger.info, IOError, tiktoken.encoding_for_model
  - Exception を捕捉した場合の代替経路を持つ（結果キー: error）

## 単体テスト観点

- 必須パラメータ fwpath, loadpath が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ scope, chunk_lang, output_json_append, stdout_log の境界値と不正値を確認する
- 複数値パラメータ fwpath の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_0, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_extract_chunklet.py
- apprun 実装元: ExtractChunklet
- svrun 実装元: ExtractChunklet
- 生成日時: 2026-04-26T00:53:07
