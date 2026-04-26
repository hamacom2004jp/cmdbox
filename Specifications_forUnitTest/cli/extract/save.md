# extract save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | extract |
| cmd | save |
| クラス | ExtractSave |
| モジュール | cmdbox.app.features.cli.cmdbox_extract_save |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_extract_save.py |
| 詳細設計書 | Specifications/cli/extract/save.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: 指定されたファイルからテキストを抽出する設定を保存します。
- 英語: Saves settings for extracting text from the specified file.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。
- 出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_2
- 結果キー候補: success, warn

## 副作用確認観点

- output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する
- 必要なディレクトリが生成され、再実行時も競合しないことを確認する

## 詳細設計からの観点

- 必須パラメータ extract_name, extract_cmd, loadpath が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ extract_type, scope, output_json_append, stdout_log の境界値と不正値を確認する
- 結果オブジェクトのキー success, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --extract_name=enabled_value、--extract_cmd=enabled_value、--extract_type=、--loadpath=既存の作業ディレクトリ、--loadregs=.*。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 必要なディレクトリが生成され、再実行時も競合しないことを確認する |
| TC-002 | 必須チェック | extract_name 未指定 | --extract_name を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --extract_name の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | extract_name 空文字 | --extract_name に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-004 | 型境界 | extract_name 1文字 | --extract_name に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに success, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-005 | 型境界 | extract_name 特殊文字 | --extract_name に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-006 | 型境界 | extract_name 長文 | --extract_name に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-007 | 必須チェック | extract_cmd 未指定 | --extract_cmd を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --extract_cmd の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-008 | 型境界 | extract_cmd 空文字 | --extract_cmd に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-009 | 型境界 | extract_cmd 1文字 | --extract_cmd に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに success, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-010 | 型境界 | extract_cmd 特殊文字 | --extract_cmd に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-011 | 型境界 | extract_cmd 長文 | --extract_cmd に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-012 | 選択値境界 | extract_type 先頭選択肢 | --extract_type に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-013 | 選択値境界 | extract_type 末尾選択肢 | --extract_type に選択肢の末尾値 file を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-014 | 選択値境界 | extract_type 不正選択肢 | --extract_type に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-015 | 選択値境界 | scope 先頭選択肢 | --scope に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-016 | 選択値境界 | scope 末尾選択肢 | --scope に選択肢の末尾値 server を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-017 | 選択値境界 | scope 不正選択肢 | --scope に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-018 | 型境界 | client_data 空文字 | --client_data に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-019 | 型境界 | client_data 1文字 | --client_data に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに success, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-020 | 型境界 | client_data 特殊文字 | --client_data に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-021 | 型境界 | client_data 長文 | --client_data に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-022 | 必須チェック | loadpath 未指定 | --loadpath を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --loadpath の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-023 | 型境界 | loadpath 既存空ディレクトリ | --loadpath に既存の空ディレクトリを指定する | RESP_SUCCESS | 空ディレクトリ前提の初期状態が正常に処理される | 必要な初期化ファイルやサブディレクトリが作成される場合は生成を確認する |
| TC-024 | 型境界 | loadpath 既存データありディレクトリ | --loadpath に既存データを含むディレクトリを指定する | RESP_SUCCESS | 既存データを読み込む経路が正常に処理される | 既存ファイルを意図せず破壊しないことを確認する |
| TC-025 | 型境界 | loadpath 非存在ディレクトリ | --loadpath に存在しないディレクトリを指定する | RESP_WARN | 存在チェックエラーまたは初期化失敗が返る | 自動作成される仕様でない限り、ディレクトリが勝手に作成されないことを確認する |
| TC-026 | 型境界 | loadregs 1文字 | --loadregs に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに success, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-027 | 型境界 | loadregs 特殊文字 | --loadregs に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-028 | 型境界 | loadregs 長文 | --loadregs に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-029 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-030 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 必要なディレクトリが生成され、再実行時も競合しないことを確認する |
| TC-031 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに success, warn が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_extract_save.py
- 詳細設計書: Specifications/cli/extract/save.md
- 生成日時: 2026-04-26T00:53:18