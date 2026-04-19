# excel cell_search

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | excel |
| cmd | cell_search |
| クラス | ExcelCellSearch |
| モジュール | cmdbox.app.features.cli.cmdbox_excel_cell_search |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_excel_cell_search.py |
| 継承元 | ExcelBase, ResultEdgeFeature, Feature |
| Redis | 任意 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: データフォルダ配下のExcelファイルの指定したセルの値を検索します。
- 英語: Searches for the value in the specified cell of an Excel file located in the data folder.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --scope | 文字列 | はい | いいえ | いいえ | client | client, current, server | 参照先スコープを指定します。指定可能な画像タイプは `client` , `current` , `server` です。 |
| --svpath | ファイル | はい | いいえ | いいえ | / | - | サーバーのデータフォルダ以下のパスを指定します。省略時は `/` を使用します。 |
| --client_data | 文字列 | いいえ | いいえ | いいえ | None | - | ローカルを参照させる場合のデータフォルダのパスを指定します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 15 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |
| --formula_data_only | 真偽値 | はい | いいえ | いいえ | false | True, False | 数式データのみを参照するかどうかを指定します。このオプションはキャッシュされたデータが存在する場合に有効です。 |
| --sheet_name | 文字列 | いいえ | いいえ | いいえ | None | - | セルの値を取得するシートの名前を指定します。省略した場合、すべてのシートが使用されます。 |
| --cell_name | 文字列 | いいえ | はい | いいえ | None | - | セルの値を検索するセルの名前を指定します。例えば、`A1`、`B2`、`R5987`。 |
| --cell_top_left | 文字列 | いいえ | いいえ | いいえ | None | - | セルの値を検索する左上セルの名前を指定します。例えば、`A1`、`B2`、`R5987`。 |
| --cell_bottom_right | 文字列 | いいえ | いいえ | いいえ | None | - | セルの値を検索する右下セルの名前を指定します。例えば、`A1`、`B2`、`R5987`。 |
| --match_type | 文字列 | はい | いいえ | いいえ | partial | full, partial, regex | 検索するセルの値に対するマッチ方法を指定します。`full`: 完全一致、`partial`: 部分一致、`regex`: 正規表現。 |
| --search_value | 文字列 | はい | いいえ | いいえ | None | - | 検索するセルの値を指定します。指定方法は `match_type` によって異なります。 |
| --output_cell_format | 文字列 | いいえ | いいえ | いいえ | json | json, csv, md, html | 出力フォーマットを指定します。例えば、`json`、`csv`、 `md`、 `html`。 |

## 処理内容

### apprun

- 実装元: ExcelBase
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - (chk, msg, _) に self.chk_args の結果を格納する
  - 条件 chk != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS, RESP_WARN
  - 例外処理を伴って処理する。主な呼出: Path, logger.warning, args.client_data.replace, filer.Filer, f._file_exists, self.excel_proc
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

### svrun

- 実装元: ExcelCellSearch
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: RESP_SUCCESS, INT_2, RESP_WARN, INT_1
- 処理フロー:
  - svpath に convert.b64str2str の結果を格納する
  - sheet_name に convert.b64str2str の結果を格納する
  - cell_name に json.loads の結果を格納する
  - cell_top_left に convert.b64str2str の結果を格納する
  - cell_bottom_right に convert.b64str2str の結果を格納する
  - match_type に convert.b64str2str の結果を格納する
  - search_value に convert.b64str2str の結果を格納する
  - output_cell_format に convert.b64str2str の結果を格納する
  - 例外処理を伴って処理する。主な呼出: filer.Filer, f._file_exists, self.cell_search, redis_cli.rpush, logger.warning, dict
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN, INT_1）
  - 終了コード RESP_SUCCESS を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_2, INT_1
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### cell_search

- 実装元: ExcelCellSearch
- 役割: 指定したワークブックのセルの値を検索します。  Args: filepath (str): ワークブックのパス formula_data_only (bool): 数式データのみを参照するかどうか。このオプションはキャッシュされたデータが存在する場合に有効です。 sheet_name (str): 詳細情報を取得するシートの名前 cell_name (List[str]): 詳細情報を取得するセルの名前のリスト。例えば、`A1`、`B2`、`R5987`。 cell_top_left (str): 詳細情報を取得する左上セルの名前。例えば、`A1`、`B2`、`R5987`。 cell_bottom_right (str): 詳細情報を取得する右下セルの名前。 例えば、`A1`、`B2`、`R5987`。 match_type (str): 検索するセルの値に対するマッチ方法。`full`: 完全一致、`partial`: 部分一致、`regex`: 正規表現。 search_value (str): 検索するセルの値。 output_cell_format (str): 出力フォーマット。例えば、`json`、`csv`、 `md`、 `html`。 logger (logging.Logger): ロガー Returns: dict: セルの詳細情報
- 処理概要:
  - 例外処理を伴って処理する。主な呼出: openpyxl.load_workbook, dict, logger.warning, _proc, wb.close, ':'.join
  - Exception を捕捉した場合の代替経路を持つ（結果キー: warn）

### chk_args

- 実装元: ExcelCellSearch
- 役割: 引数のチェックを行います  Args: args (argparse.Namespace): 引数  Returns: Tuple[bool, str]: チェック結果, メッセージ
- 処理概要:
  - 条件 args.svname is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.scope is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.svpath is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.match_type is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.search_value is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 終了コード RESP_SUCCESS を返却する

### excel_proc

- 実装元: ExcelCellSearch
- 役割: Excel処理のベース  Args: abspath (Path): Excelファイルの絶対パス args (argparse.Namespace): 引数 logger (logging.Logger): ロガー tm (float): 処理時間 pf (List[Dict[str, float]]): パフォーマンス情報  Returns: Dict[str, Any]: 結果
- 処理概要:
  - res_json に self.cell_search の結果を格納する
  - res_json を返却する

### get_svparam

- 実装元: ExcelCellSearch
- 役割: サーバーに送信するパラメーターを返します  Args: args (argparse.Namespace): 引数  Returns: List[str]: サーバーに送信するパラメーター
- 処理概要:
  - ret を返却する

## 単体テスト観点

- 必須パラメータ formula_data_only, search_value が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ scope, output_json_append, stdout_log, capture_stdout, formula_data_only, match_type, output_cell_format の境界値と不正値を確認する
- 複数値パラメータ cell_name の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_2, INT_1 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_excel_cell_search.py
- apprun 実装元: ExcelBase
- svrun 実装元: ExcelCellSearch
- 生成日時: 2026-04-19T20:59:09
