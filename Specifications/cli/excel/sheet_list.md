# excel sheet_list

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | excel |
| cmd | sheet_list |
| クラス | ExcelSheetList |
| モジュール | cmdbox.app.features.cli.cmdbox_excel_sheet_list |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_excel_sheet_list.py |
| 継承元 | ExcelBase, ResultEdgeFeature, Validator, Feature |
| Redis | 任意 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: データフォルダ配下のExcelファイルのシート一覧を取得します。
- 英語: Retrieves the list of sheets in an Excel file located within the data folder.

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

- 実装元: ExcelSheetList
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: RESP_SUCCESS, INT_2, RESP_WARN, INT_1
- 処理フロー:
  - svpath に convert.b64str2str の結果を格納する
  - 例外処理を伴って処理する。主な呼出: filer.Filer, f._file_exists, self.sheet_list, redis_cli.rpush, logger.warning, dict
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN, INT_1）
  - 終了コード RESP_SUCCESS を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_2, INT_1
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### chk_args

- 実装元: ExcelSheetList
- 役割: 引数のチェックを行います  Args: args (argparse.Namespace): 引数  Returns: Tuple[bool, str]: チェック結果, メッセージ
- 処理概要:
  - (st, msg, cl) に super().chk_args の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 終了コード RESP_SUCCESS を返却する

### excel_proc

- 実装元: ExcelSheetList
- 役割: Excel処理のベース  Args: abspath (Path): Excelファイルの絶対パス args (argparse.Namespace): 引数 logger (logging.Logger): ロガー tm (float): 処理時間 pf (List[Dict[str, float]]): パフォーマンス情報  Returns: Dict[str, Any]: 結果
- 処理概要:
  - res_json に self.sheet_list の結果を格納する
  - res_json を返却する

### get_svparam

- 実装元: ExcelSheetList
- 役割: サーバーに送信するパラメーターを返します  Args: args (argparse.Namespace): 引数  Returns: List[str]: サーバーに送信するパラメーター
- 処理概要:
  - ret を返却する

### sheet_list

- 実装元: ExcelSheetList
- 役割: 指定したワークブックのシート一覧を取得します。  Args: filepath (str): ワークブックのパス logger (logging.Logger): ロガー Returns: dict: シートの情報
- 処理概要:
  - 例外処理を伴って処理する。主な呼出: openpyxl.load_workbook, dict, logger.warning, wb.close
  - Exception を捕捉した場合の代替経路を持つ（結果キー: warn）

## 単体テスト観点

- 選択肢を持つパラメータ scope, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_2, INT_1 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_excel_sheet_list.py
- apprun 実装元: ExcelBase
- svrun 実装元: ExcelSheetList
- 生成日時: 2026-04-23T23:40:02
