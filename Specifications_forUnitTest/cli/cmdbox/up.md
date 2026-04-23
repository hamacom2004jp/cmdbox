# cmdbox up

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | cmdbox |
| cmd | up |
| クラス | CmdboxUp |
| モジュール | cmdbox.app.features.cli.cmdbox_cmdbox_up |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_up.py |
| 詳細設計書 | Specifications/cli/cmdbox/up.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: コンテナを起動します。
- 英語: Starts the container.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: 特になし

## 副作用確認観点

- 戻り値とログのみを確認対象とする

## 詳細設計からの観点

- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | 全パラメータ省略またはデフォルト値で実行する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 戻り値以外の副作用がないことを確認する |
| TC-002 | 型境界 | container 空文字 | --container(-C) に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-003 | 型境界 | container 1文字 | --container(-C) に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-004 | 型境界 | container 特殊文字 | --container(-C) に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-005 | 型境界 | container 長文 | --container(-C) に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-006 | ファイルI/O | compose_path 有効入力ファイル | --compose_path に存在する妥当なファイルを指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 入力ファイル内容が意図どおり読み込まれることを確認する |
| TC-007 | ファイルI/O | compose_path 存在しない入力ファイル | --compose_path に存在しないパスを指定する | RESP_WARN | ファイル未存在のエラーまたは警告が返る | 後続処理に進まず、副作用が発生しないことを確認する |
| TC-008 | ファイルI/O | compose_path 空ファイル | --compose_path に 0 byte の空ファイルを指定する | RESP_WARN | フォーマット不正または入力不足として扱われる | 異常終了時のログやエラー文言が十分であることを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_up.py
- 詳細設計書: Specifications/cli/cmdbox/up.md
- 生成日時: 2026-04-23T23:40:14