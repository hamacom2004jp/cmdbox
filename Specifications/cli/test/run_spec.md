# test run_spec

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | test |
| cmd | run_spec |
| クラス | TestRunSpec |
| モジュール | cmdbox.app.features.cli.cmdbox_test_run_spec |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_test_run_spec.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: テスト仕様JSONに基づいてテストを実行し、結果を報告します。
- 英語: Runs tests based on the unit test specification JSON and reports results.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --mode_filter | 文字列 | いいえ | いいえ | いいえ | None | - | 実行対象をモード名でフィルタします。省略時は全モードを実行します。(例: server, test) |
| --cmd_filter | 複数選択リスト | いいえ | いいえ | いいえ | None | - | 実行対象をコマンド名でフィルタします。省略時は全コマンドを実行します。(例: list, start) |
| --input_json | ファイル | はい | いいえ | いいえ | ./Specifications_forUnitTest/cli-unit-test-specifications.json | - | 入力となる cli-unit-test-specifications.json のパスを指定します。 |
| --use_tempdir | 真偽値 | いいえ | いいえ | いいえ | false | True, False | 出力系パラメータを一時ディレクトリに置換してテストを実行します。Trueにすると既存ファイルを上書きしません。 |
| --output_dir | ディレクトリ | いいえ | いいえ | いいえ | ./Specifications_forUnitTest_results/ | - | テスト実行結果（JSONおよびMD）の出力先ディレクトリを指定します。省略時は ./Specifications_forUnitTest_results を使用します。 |
| --clear_output_dir | 真偽値 | いいえ | いいえ | いいえ | false | True, False | Trueを指定すると、出力先ディレクトリが既に存在する場合にクリア（削除して再作成）してから結果を出力します。Falseの場合（デフォルト）、既存の結果ファイルに今回のテストケース結果をマージして上書きします。 |
| --app_class | 文字列 | いいえ | いいえ | いいえ | cmdbox.app.app.CmdBoxApp | - | テスト対象のアプリケーションクラスのモジュールパスを指定します。(例: myapp.app.MyApp) 省略時は cmdbox.app.app.CmdBoxApp を使用します。 |
| --ver_module | 文字列 | いいえ | いいえ | いいえ | cmdbox.version | - | バージョンモジュールのパスを指定します。(例: myapp.version) 省略時は cmdbox.version を使用します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: TestRunSpec
- 役割: テスト仕様JSONに基づいてテストを実行し、結果を報告します。  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, INT_0, RESP_WARN
- 結果キー候補: success, warn
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - input_json に Path の結果を格納する
  - 条件 not input_json.exists() を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - clear_output_dir に bool の結果を格納する
  - 条件 output_dir is not None and output_dir.exists() に応じて分岐する。主な呼出: output_dir.exists, shutil.rmtree
  - 条件 args.app_class を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.ver_module を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 例外処理を伴って処理する。主な呼出: run_spec.run, logger.warning, dict, common.print_format, str
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）
  - success_data に dict の結果を格納する
  - 条件 output_dir is not None に応じて分岐する。主な呼出: str
  - msg に dict の結果を格納する
  - 条件 failed_count > 0 に応じて分岐する
  - common.print_format を呼び出す
  - 終了コード RESP_SUCCESS, RESP_WARN, INT_0 を返却する

### svrun

- 実装元: TestRunSpec
- 終了コード候補: RESP_SUCCESS
- 処理フロー:
  - 終了コード RESP_SUCCESS を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, INT_0, RESP_WARN
- 結果キー候補: success, warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 選択肢を持つパラメータ use_tempdir, clear_output_dir, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー success, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, INT_0, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_test_run_spec.py
- apprun 実装元: TestRunSpec
- svrun 実装元: TestRunSpec
- 生成日時: 2026-04-26T00:53:09
