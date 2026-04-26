# test gen_cli_spec

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | test |
| cmd | gen_cli_spec |
| クラス | TestGenCliSpec |
| モジュール | cmdbox.app.features.cli.cmdbox_test_gen_cli_spec |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_test_gen_cli_spec.py |
| 詳細設計書 | Specifications/cli/test/gen_cli_spec.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: フィーチャーパッケージを解析してCLIコマンド詳細設計書を生成します。
- 英語: Analyzes a feature package and generates CLI command detailed design documents.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。
- 出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success, output_dir, json_file, count, warn

## 副作用確認観点

- output_dir で指定した出力ファイルが作成され、内容が空でないことを確認する
- output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する

## 詳細設計からの観点

- 選択肢を持つパラメータ clear_output_dir, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー success, output_dir, json_file, count, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --feature_package=cmdbox.app.features.cli。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, output_dir, json_file, count, warn が含まれる | output_dir で指定した出力ファイルが作成され、内容が空でないことを確認する / output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |
| TC-002 | 型境界 | feature_package 1文字 | --feature_package に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに success, output_dir, json_file, count, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-003 | 型境界 | feature_package 特殊文字 | --feature_package に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-004 | 型境界 | feature_package 長文 | --feature_package に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-005 | 型境界 | output_dir 既存空ディレクトリ | --output_dir に既存の空ディレクトリを指定する | RESP_SUCCESS | 空ディレクトリ前提の初期状態が正常に処理される | 必要な初期化ファイルやサブディレクトリが作成される場合は生成を確認する |
| TC-006 | 型境界 | output_dir 既存データありディレクトリ | --output_dir に既存データを含むディレクトリを指定する | RESP_SUCCESS | 既存データを読み込む経路が正常に処理される | 既存ファイルを意図せず破壊しないことを確認する |
| TC-007 | 型境界 | output_dir 非存在ディレクトリ | --output_dir に存在しないディレクトリを指定する | RESP_WARN | 存在チェックエラーまたは初期化失敗が返る | 自動作成される仕様でない限り、ディレクトリが勝手に作成されないことを確認する |
| TC-008 | 型境界 | root_dir 既存空ディレクトリ | --root_dir に既存の空ディレクトリを指定する | RESP_SUCCESS | 空ディレクトリ前提の初期状態が正常に処理される | 必要な初期化ファイルやサブディレクトリが作成される場合は生成を確認する |
| TC-009 | 型境界 | root_dir 既存データありディレクトリ | --root_dir に既存データを含むディレクトリを指定する | RESP_SUCCESS | 既存データを読み込む経路が正常に処理される | 既存ファイルを意図せず破壊しないことを確認する |
| TC-010 | 型境界 | root_dir 非存在ディレクトリ | --root_dir に存在しないディレクトリを指定する | RESP_WARN | 存在チェックエラーまたは初期化失敗が返る | 自動作成される仕様でない限り、ディレクトリが勝手に作成されないことを確認する |
| TC-011 | 型境界 | prefix 1文字 | --prefix に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに success, output_dir, json_file, count, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-012 | 型境界 | prefix 特殊文字 | --prefix に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-013 | 型境界 | prefix 長文 | --prefix に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-014 | 型境界 | clear_output_dir=False | --clear_output_dir に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-015 | 型境界 | clear_output_dir=True | --clear_output_dir に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-016 | 型境界 | app_class 1文字 | --app_class に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに success, output_dir, json_file, count, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-017 | 型境界 | app_class 特殊文字 | --app_class に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-018 | 型境界 | app_class 長文 | --app_class に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-019 | 型境界 | ver_module 1文字 | --ver_module に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに success, output_dir, json_file, count, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-020 | 型境界 | ver_module 特殊文字 | --ver_module に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-021 | 型境界 | ver_module 長文 | --ver_module に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-022 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-023 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_dir で指定した出力ファイルが作成され、内容が空でないことを確認する / output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |
| TC-024 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに success, output_dir, json_file, count, warn が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_test_gen_cli_spec.py
- 詳細設計書: Specifications/cli/test/gen_cli_spec.md
- 生成日時: 2026-04-26T00:53:18