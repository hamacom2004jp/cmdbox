# web user_edit

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | web |
| cmd | user_edit |
| クラス | WebUserEdit |
| モジュール | cmdbox.app.features.cli.cmdbox_web_user_edit |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_user_edit.py |
| 詳細設計書 | Specifications/cli/web/user_edit.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: Webモードのユーザーを編集します。
- 英語: Edit users in Web mode.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success, warn

## 副作用確認観点

- 戻り値とログのみを確認対象とする

## 詳細設計からの観点

- 必須パラメータ user_id, user_name, user_group が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ user_pass_hash, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ user_group の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー success, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --user_id=1、--user_name=enabled_value、--user_group=enabled_value、--signin_file=.cmdbox/user_list.yml。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 戻り値以外の副作用がないことを確認する |
| TC-002 | 必須チェック | user_id 未指定 | --user_id を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --user_id の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | user_id=0 | --user_id に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-004 | 型境界 | user_id=1 | --user_id に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-005 | 型境界 | user_id=-1 | --user_id に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-006 | 型境界 | user_id=2147483647 | --user_id に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-007 | 必須チェック | user_name 未指定 | --user_name を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --user_name の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-008 | 型境界 | user_name 空文字 | --user_name に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-009 | 型境界 | user_name 1文字 | --user_name に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-010 | 型境界 | user_name 特殊文字 | --user_name に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-011 | 型境界 | user_name 長文 | --user_name に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-012 | 型境界 | user_pass 空文字 | --user_pass に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-013 | 型境界 | user_pass 1文字 | --user_pass に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-014 | 型境界 | user_pass 特殊文字 | --user_pass に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-015 | 型境界 | user_pass 長文 | --user_pass に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-016 | 選択値境界 | user_pass_hash 先頭選択肢 | --user_pass_hash に選択肢の先頭値 oauth2 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-017 | 選択値境界 | user_pass_hash 末尾選択肢 | --user_pass_hash に選択肢の末尾値 sha256 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-018 | 選択値境界 | user_pass_hash 不正選択肢 | --user_pass_hash に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-019 | 型境界 | user_pass_hash 空文字 | --user_pass_hash に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-020 | 型境界 | user_pass_hash 1文字 | --user_pass_hash に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-021 | 型境界 | user_pass_hash 特殊文字 | --user_pass_hash に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-022 | 型境界 | user_pass_hash 長文 | --user_pass_hash に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-023 | 型境界 | user_email 空文字 | --user_email に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-024 | 型境界 | user_email 1文字 | --user_email に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-025 | 型境界 | user_email 特殊文字 | --user_email に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-026 | 型境界 | user_email 長文 | --user_email に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-027 | 必須チェック | user_group 未指定 | --user_group を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --user_group の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-028 | 複数値境界 | user_group 0件 | --user_group に空配列または未指定を与える | RESP_WARN | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-029 | 複数値境界 | user_group 1件 | --user_group に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-030 | 複数値境界 | user_group 複数件 | --user_group に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-031 | 型境界 | user_group 空文字 | --user_group に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-032 | 型境界 | user_group 1文字 | --user_group に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-033 | 型境界 | user_group 特殊文字 | --user_group に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-034 | 型境界 | user_group 長文 | --user_group に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-035 | ファイルI/O | signin_file 有効入力ファイル | --signin_file に存在する妥当なファイルを指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 入力ファイル内容が意図どおり読み込まれることを確認する |
| TC-036 | ファイルI/O | signin_file 存在しない入力ファイル | --signin_file に存在しないパスを指定する | RESP_WARN | ファイル未存在のエラーまたは警告が返る | 後続処理に進まず、副作用が発生しないことを確認する |
| TC-037 | ファイルI/O | signin_file 空ファイル | --signin_file に 0 byte の空ファイルを指定する | RESP_WARN | フォーマット不正または入力不足として扱われる | 異常終了時のログやエラー文言が十分であることを確認する |
| TC-038 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに success, warn が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_user_edit.py
- 詳細設計書: Specifications/cli/web/user_edit.md
- 生成日時: 2026-04-23T23:40:14