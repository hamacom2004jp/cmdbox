# web genpass

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | web |
| cmd | genpass |
| クラス | WebGenpass |
| モジュール | cmdbox.app.features.cli.cmdbox_web_genpass |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_web_genpass.py |
| 詳細設計書 | Specifications/cli/web/genpass.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: webモードで使用できるパスワード文字列を生成します。
- 英語: Generates a password string that can be used in web mode.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, INT_1, RESP_WARN
- 結果キー候補: warn, success, error

## 副作用確認観点

- 戻り値とログのみを確認対象とする

## 詳細設計からの観点

- 選択肢を持つパラメータ use_alphabet, use_number, use_symbol, similar, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn, success, error が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, INT_1, RESP_WARN の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | 全パラメータ省略またはデフォルト値で実行する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 戻り値以外の副作用がないことを確認する |
| TC-002 | 型境界 | pass_length=0 | --pass_length に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-003 | 型境界 | pass_length=1 | --pass_length に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-004 | 型境界 | pass_length=-1 | --pass_length に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-005 | 型境界 | pass_length=2147483647 | --pass_length に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-006 | 型境界 | pass_count=0 | --pass_count に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-007 | 型境界 | pass_count=1 | --pass_count に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-008 | 型境界 | pass_count=-1 | --pass_count に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-009 | 型境界 | pass_count=2147483647 | --pass_count に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-010 | 選択値境界 | use_alphabet 先頭選択肢 | --use_alphabet に選択肢の先頭値 notuse を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-011 | 選択値境界 | use_alphabet 末尾選択肢 | --use_alphabet に選択肢の末尾値 both を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-012 | 選択値境界 | use_alphabet 不正選択肢 | --use_alphabet に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-013 | 選択値境界 | use_number 先頭選択肢 | --use_number に選択肢の先頭値 notuse を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-014 | 選択値境界 | use_number 末尾選択肢 | --use_number に選択肢の末尾値 use を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-015 | 選択値境界 | use_number 不正選択肢 | --use_number に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-016 | 選択値境界 | use_symbol 先頭選択肢 | --use_symbol に選択肢の先頭値 notuse を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-017 | 選択値境界 | use_symbol 末尾選択肢 | --use_symbol に選択肢の末尾値 use を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-018 | 選択値境界 | use_symbol 不正選択肢 | --use_symbol に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-019 | 選択値境界 | similar 先頭選択肢 | --similar に選択肢の先頭値 exclude を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-020 | 選択値境界 | similar 末尾選択肢 | --similar に選択肢の末尾値 include を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-021 | 選択値境界 | similar 不正選択肢 | --similar に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-022 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn, success, error が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_web_genpass.py
- 詳細設計書: Specifications/cli/web/genpass.md
- 生成日時: 2026-04-26T00:53:18