# web user_del

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | web |
| cmd | user_del |
| クラス | WebUserDel |
| モジュール | cmdbox.app.features.cli.cmdbox_web_user_del |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_user_del.py |
| 詳細設計書 | Specifications/cli/web/user_del.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: Webモードのユーザーを削除します。
- 英語: Delete a user in Web mode.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。

## 共通期待結果

- 終了コード候補: RESP_WARN, RESP_SUCCESS
- 結果キー候補: warn, success

## 副作用確認観点

- 戻り値とログのみを確認対象とする

## 詳細設計からの観点

- 必須パラメータ user_id, signin_file が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_WARN, RESP_SUCCESS の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --user_id=1、--signin_file=既存の妥当な入力ファイル。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 戻り値以外の副作用がないことを確認する |
| TC-002 | 必須チェック | user_id 未指定 | --user_id を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --user_id の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | user_id=0 | --user_id に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-004 | 型境界 | user_id=1 | --user_id に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-005 | 型境界 | user_id=-1 | --user_id に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-006 | 型境界 | user_id=2147483647 | --user_id に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-007 | 必須チェック | signin_file 未指定 | --signin_file を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --signin_file の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-008 | ファイルI/O | signin_file 有効入力ファイル | --signin_file に存在する妥当なファイルを指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 入力ファイル内容が意図どおり読み込まれることを確認する |
| TC-009 | ファイルI/O | signin_file 存在しない入力ファイル | --signin_file に存在しないパスを指定する | RESP_WARN | ファイル未存在のエラーまたは警告が返る | 後続処理に進まず、副作用が発生しないことを確認する |
| TC-010 | ファイルI/O | signin_file 空ファイル | --signin_file に 0 byte の空ファイルを指定する | RESP_WARN | フォーマット不正または入力不足として扱われる | 異常終了時のログやエラー文言が十分であることを確認する |
| TC-011 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn, success が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_user_del.py
- 詳細設計書: Specifications/cli/web/user_del.md
- 生成日時: 2026-04-19T21:16:02