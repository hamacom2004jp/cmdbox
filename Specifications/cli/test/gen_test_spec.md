# test gen_test_spec

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | test |
| cmd | gen_test_spec |
| クラス | TestGenTestSpec |
| モジュール | cmdbox.app.features.cli.cmdbox_test_gen_test_spec |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_test_gen_test_spec.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: CLIコマンド仕様JSONを読み込みユニットテスト仕様書を生成します。
- 英語: Reads CLI command specification JSON and generates unit test specification documents.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --input_json | ファイル | はい | いいえ | いいえ | ./Specifications/cli-command-specifications.json | - | 入力となる cli-command-specifications.json のパスを指定します。 |
| --output_dir | ディレクトリ | いいえ | いいえ | いいえ | ./Specifications_forUnitTest/ | - | テスト仕様書の出力先ディレクトリを指定します。省略時はカレントディレクトリ配下の Specifications_forUnitTest ディレクトリを使用します。 |
| --root_dir | ディレクトリ | いいえ | いいえ | いいえ | ./ | - | プロジェクトルートディレクトリを指定します。詳細設計書マークダウンの参照に使用します。省略時はカレントディレクトリを使用します。 |
| --clear_output_dir | 真偽値 | いいえ | いいえ | いいえ | false | True, False | Trueを指定すると、出力先ディレクトリが既に存在する場合にクリア（削除して再作成）してから仕様書を生成します。Falseの場合、出力先ディレクトリが既に存在するとワーニングを返します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: TestGenTestSpec
- 役割: CLIコマンド仕様JSONを読み込みユニットテスト仕様書を生成します。  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success, output_dir, json_file, count, warn
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - input_json に Path の結果を格納する
  - 条件 not input_json.exists() を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - clear_output_dir に bool の結果を格納する
  - 条件 output_dir.exists() を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 例外処理を伴って処理する。主な呼出: gen_test_spec.generate, logger.warning, dict, common.print_format, str
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）
  - msg に dict の結果を格納する
  - common.print_format を呼び出す
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success, output_dir, json_file, count, warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 選択肢を持つパラメータ clear_output_dir, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー success, output_dir, json_file, count, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_test_gen_test_spec.py
- apprun 実装元: TestGenTestSpec
- svrun 実装元: Feature
- 生成日時: 2026-04-26T00:53:09
