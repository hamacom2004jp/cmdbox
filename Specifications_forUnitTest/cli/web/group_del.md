# web group_del

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | web |
| cmd | group_del |
| クラス | WebGroupDel |
| モジュール | cmdbox.app.features.cli.cmdbox_web_group_del |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_group_del.py |
| 詳細設計書 | Specifications/cli/web/group_del.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: Webモードのグループを削除します。
- 英語: Del a group in Web mode.

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

- 必須パラメータ group_id が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー success, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --group_id=enabled_value、--signin_file=.cmdbox/user_list.yml。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 戻り値以外の副作用がないことを確認する |
| TC-002 | 必須チェック | group_id 未指定 | --group_id を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --group_id の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | group_id 空文字 | --group_id に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-004 | 型境界 | group_id 1文字 | --group_id に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-005 | 型境界 | group_id 特殊文字 | --group_id に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-006 | 型境界 | group_id 長文 | --group_id に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-007 | ファイルI/O | signin_file 有効入力ファイル | --signin_file に存在する妥当なファイルを指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success, warn が含まれる | 入力ファイル内容が意図どおり読み込まれることを確認する |
| TC-008 | ファイルI/O | signin_file 存在しない入力ファイル | --signin_file に存在しないパスを指定する | RESP_WARN | ファイル未存在のエラーまたは警告が返る | 後続処理に進まず、副作用が発生しないことを確認する |
| TC-009 | ファイルI/O | signin_file 空ファイル | --signin_file に 0 byte の空ファイルを指定する | RESP_WARN | フォーマット不正または入力不足として扱われる | 異常終了時のログやエラー文言が十分であることを確認する |
| TC-010 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに success, warn が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_group_del.py
- 詳細設計書: Specifications/cli/web/group_del.md
- 生成日時: 2026-04-23T23:40:14