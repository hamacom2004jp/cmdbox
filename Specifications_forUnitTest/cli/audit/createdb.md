# audit createdb

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | audit |
| cmd | createdb |
| クラス | AuditCreatedb |
| モジュール | cmdbox.app.features.cli.cmdbox_audit_createdb |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_audit_createdb.py |
| 詳細設計書 | Specifications/cli/audit/createdb.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: 監査を記録するデータベースを作成します。
- 英語: Create a database to record audits.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_2, INT_1
- 結果キー候補: 特になし

## 副作用確認観点

- 戻り値とログのみを確認対象とする

## 詳細設計からの観点

- 終了コード RESP_SUCCESS, RESP_WARN, INT_2, INT_1 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --pg_host=pgsql、--pg_port=5432、--pg_user=pgsql、--pg_password=pgsql、--pg_dbname=postgresql、--new_pg_dbname=audit。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 戻り値以外の副作用がないことを確認する |
| TC-002 | 型境界 | pg_host 1文字 | --pg_host に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-003 | 型境界 | pg_host 特殊文字 | --pg_host に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-004 | 型境界 | pg_host 長文 | --pg_host に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-005 | 型境界 | pg_port=0 | --pg_port に 0 を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-006 | 型境界 | pg_port=1 | --pg_port に 1 を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-007 | 型境界 | pg_port=-1 | --pg_port に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-008 | 型境界 | pg_port=2147483647 | --pg_port に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-009 | 型境界 | pg_user 1文字 | --pg_user に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-010 | 型境界 | pg_user 特殊文字 | --pg_user に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-011 | 型境界 | pg_user 長文 | --pg_user に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-012 | 型境界 | pg_password 1文字 | --pg_password に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-013 | 型境界 | pg_password 特殊文字 | --pg_password に a_日本語 space-_.#"'&<> を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-014 | 型境界 | pg_dbname 1文字 | --pg_dbname に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-015 | 型境界 | pg_dbname 特殊文字 | --pg_dbname に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-016 | 型境界 | pg_dbname 長文 | --pg_dbname に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-017 | 型境界 | new_pg_dbname 1文字 | --new_pg_dbname に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-018 | 型境界 | new_pg_dbname 特殊文字 | --new_pg_dbname に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-019 | 型境界 | new_pg_dbname 長文 | --new_pg_dbname に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_audit_createdb.py
- 詳細設計書: Specifications/cli/audit/createdb.md
- 生成日時: 2026-04-26T00:53:18