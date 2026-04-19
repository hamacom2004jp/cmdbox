# test gen_cli_spec

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | test |
| cmd | gen_cli_spec |
| クラス | TestGenCliSpec |
| モジュール | cmdbox.app.features.cli.cmdbox_test_gen_cli_spec |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_test_gen_cli_spec.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Feature |
| Redis | 不要 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: フィーチャーパッケージを解析してCLIコマンド詳細設計書を生成します。
- 英語: Analyzes a feature package and generates CLI command detailed design documents.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --feature_package | 文字列 | はい | いいえ | いいえ | cmdbox.app.features.cli | - | フィーチャーを含むPythonパッケージ名を指定します。(例: cmdbox.app.features.cli, myapp.app.features.cli) |
| --output_dir | ディレクトリ | いいえ | いいえ | いいえ | ./Specifications/ | - | 仕様書の出力先ディレクトリを指定します。省略時はカレントディレクトリ配下の Specifications ディレクトリを使用します。 |
| --root_dir | ディレクトリ | いいえ | いいえ | いいえ | ./ | - | プロジェクトルートディレクトリを指定します。ソースファイルの相対パス計算に使用します。省略時はカレントディレクトリを使用します。 |
| --prefix | 文字列 | いいえ | いいえ | いいえ | cmdbox_ | - | フィーチャーモジュールのファイル名プレフィックスを指定します。 |
| --app_class | 文字列 | いいえ | いいえ | いいえ | cmdbox.app.app.CmdBoxApp | - | アプリケーションクラスのモジュールパスを指定します。(例: myapp.app.MyApp) 省略時は cmdbox.app.app.CmdBoxApp を使用します。 |
| --ver_module | 文字列 | いいえ | いいえ | いいえ | cmdbox.version | - | バージョンモジュールのパスを指定します。(例: myapp.version) 省略時は cmdbox.version を使用します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: TestGenCliSpec
- 役割: フィーチャーパッケージを解析してCLIコマンド詳細設計書を生成します。  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success, output_dir, json_file, count, warn
- 処理フロー:
  - 条件 not feature_package を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.app_class を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.ver_module を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 例外処理を伴って処理する。主な呼出: gen_cli_spec.generate, logger.warning, dict, common.print_format, str
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）
  - msg に dict の結果を格納する
  - common.print_format を呼び出す
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: TestGenCliSpec
- 終了コード候補: RESP_SUCCESS
- 処理フロー:
  - 終了コード RESP_SUCCESS を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success, output_dir, json_file, count, warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 選択肢を持つパラメータ output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー success, output_dir, json_file, count, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_test_gen_cli_spec.py
- apprun 実装元: TestGenCliSpec
- svrun 実装元: TestGenCliSpec
- 生成日時: 2026-04-19T20:59:11
