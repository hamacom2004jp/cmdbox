# client time

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | client |
| cmd | time |
| クラス | ClientTime |
| モジュール | cmdbox.app.features.cli.cmdbox_client_time |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_client_time.py |
| 詳細設計書 | Specifications/cli/client/time.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: クライアント側の現在時刻を表示します。
- 英語: Displays the current time at the client side.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success

## 副作用確認観点

- 戻り値とログのみを確認対象とする

## 詳細設計からの観点

- 結果オブジェクトのキー success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | 全パラメータ省略またはデフォルト値で実行する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success が含まれる | 戻り値以外の副作用がないことを確認する |
| TC-002 | 型境界 | timedelta=0 | --timedelta に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-003 | 型境界 | timedelta=1 | --timedelta に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-004 | 型境界 | timedelta=-1 | --timedelta に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-005 | 型境界 | timedelta=2147483647 | --timedelta に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-006 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに success が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_client_time.py
- 詳細設計書: Specifications/cli/client/time.md
- 生成日時: 2026-04-19T21:16:02