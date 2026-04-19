# audit search

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | audit |
| cmd | search |
| クラス | AuditSearch |
| モジュール | cmdbox.app.features.cli.cmdbox_audit_search |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_audit_search.py |
| 詳細設計書 | Specifications/cli/audit/search.md |
| 実装上の必須推定 | svname |

## 概要

- 日本語: 監査ログを検索します。
- 英語: Search the audit log.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。
- 出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_0, INT_1, INT_2
- 結果キー候補: warn

## 副作用確認観点

- output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する
- 生成物が空でなく、フォーマット不整合がないことを確認する

## 詳細設計からの観点

- 選択肢を持つパラメータ pg_enabled, select_date_format, filter_audit_type, groupby, groupby_date_format, csv, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ select, filter_clmsg_body, filter_clmsg_tag, groupby, sort の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_0, INT_1, INT_2 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | 全パラメータ省略またはデフォルト値で実行する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 生成物が空でなく、フォーマット不整合がないことを確認する |
| TC-002 | 型境界 | pg_enabled=False | --pg_enabled に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-003 | 型境界 | pg_enabled=True | --pg_enabled に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-004 | 型境界 | pg_host 空文字 | --pg_host に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-005 | 型境界 | pg_host 1文字 | --pg_host に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-006 | 型境界 | pg_host 特殊文字 | --pg_host に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-007 | 型境界 | pg_host 長文 | --pg_host に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-008 | 型境界 | pg_port=0 | --pg_port に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-009 | 型境界 | pg_port=1 | --pg_port に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-010 | 型境界 | pg_port=-1 | --pg_port に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-011 | 型境界 | pg_port=2147483647 | --pg_port に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-012 | 型境界 | pg_user 空文字 | --pg_user に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-013 | 型境界 | pg_user 1文字 | --pg_user に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-014 | 型境界 | pg_user 特殊文字 | --pg_user に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-015 | 型境界 | pg_user 長文 | --pg_user に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-016 | 型境界 | pg_password 空文字 | --pg_password に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-017 | 型境界 | pg_password 1文字 | --pg_password に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-018 | 型境界 | pg_password 特殊文字 | --pg_password に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-019 | 型境界 | pg_password 長文 | --pg_password に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-020 | 型境界 | pg_dbname 空文字 | --pg_dbname に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-021 | 型境界 | pg_dbname 1文字 | --pg_dbname に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-022 | 型境界 | pg_dbname 特殊文字 | --pg_dbname に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-023 | 型境界 | pg_dbname 長文 | --pg_dbname に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-024 | 複数値境界 | select 0件 | --select に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-025 | 複数値境界 | select 1件 | --select に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-026 | 複数値境界 | select 複数件 | --select に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-027 | 選択値境界 | select_date_format 先頭選択肢 | --select_date_format に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-028 | 選択値境界 | select_date_format 末尾選択肢 | --select_date_format に選択肢の末尾値 %u を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-029 | 選択値境界 | select_date_format 不正選択肢 | --select_date_format に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-030 | 型境界 | select_date_format 空文字 | --select_date_format に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-031 | 型境界 | select_date_format 1文字 | --select_date_format に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-032 | 型境界 | select_date_format 特殊文字 | --select_date_format に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-033 | 型境界 | select_date_format 長文 | --select_date_format に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-034 | 選択値境界 | filter_audit_type 先頭選択肢 | --filter_audit_type に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-035 | 選択値境界 | filter_audit_type 末尾選択肢 | --filter_audit_type に選択肢の末尾値 event を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-036 | 選択値境界 | filter_audit_type 不正選択肢 | --filter_audit_type に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-037 | 型境界 | filter_audit_type 空文字 | --filter_audit_type に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-038 | 型境界 | filter_audit_type 1文字 | --filter_audit_type に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-039 | 型境界 | filter_audit_type 特殊文字 | --filter_audit_type に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-040 | 型境界 | filter_audit_type 長文 | --filter_audit_type に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-041 | 型境界 | filter_clmsg_id 空文字 | --filter_clmsg_id に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-042 | 型境界 | filter_clmsg_id 1文字 | --filter_clmsg_id に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-043 | 型境界 | filter_clmsg_id 特殊文字 | --filter_clmsg_id に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-044 | 型境界 | filter_clmsg_id 長文 | --filter_clmsg_id に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-045 | 型境界 | filter_clmsg_src 空文字 | --filter_clmsg_src に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-046 | 型境界 | filter_clmsg_src 1文字 | --filter_clmsg_src に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-047 | 型境界 | filter_clmsg_src 特殊文字 | --filter_clmsg_src に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-048 | 型境界 | filter_clmsg_src 長文 | --filter_clmsg_src に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-049 | 型境界 | filter_clmsg_title 空文字 | --filter_clmsg_title に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-050 | 型境界 | filter_clmsg_title 1文字 | --filter_clmsg_title に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-051 | 型境界 | filter_clmsg_title 特殊文字 | --filter_clmsg_title に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-052 | 型境界 | filter_clmsg_title 長文 | --filter_clmsg_title に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-053 | 型境界 | filter_clmsg_user 空文字 | --filter_clmsg_user に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-054 | 型境界 | filter_clmsg_user 1文字 | --filter_clmsg_user に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-055 | 型境界 | filter_clmsg_user 特殊文字 | --filter_clmsg_user に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-056 | 型境界 | filter_clmsg_user 長文 | --filter_clmsg_user に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-057 | 複数値境界 | filter_clmsg_body 0件 | --filter_clmsg_body に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-058 | 複数値境界 | filter_clmsg_body 1件 | --filter_clmsg_body に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-059 | 複数値境界 | filter_clmsg_body 複数件 | --filter_clmsg_body に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-060 | 複数値境界 | filter_clmsg_tag 0件 | --filter_clmsg_tag に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-061 | 複数値境界 | filter_clmsg_tag 1件 | --filter_clmsg_tag に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-062 | 複数値境界 | filter_clmsg_tag 複数件 | --filter_clmsg_tag に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-063 | 型境界 | filter_clmsg_tag 空文字 | --filter_clmsg_tag に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-064 | 型境界 | filter_clmsg_tag 1文字 | --filter_clmsg_tag に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-065 | 型境界 | filter_clmsg_tag 特殊文字 | --filter_clmsg_tag に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-066 | 型境界 | filter_clmsg_tag 長文 | --filter_clmsg_tag に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-067 | 型境界 | filter_svmsg_id 空文字 | --filter_svmsg_id に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-068 | 型境界 | filter_svmsg_id 1文字 | --filter_svmsg_id に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-069 | 型境界 | filter_svmsg_id 特殊文字 | --filter_svmsg_id に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-070 | 型境界 | filter_svmsg_id 長文 | --filter_svmsg_id に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-071 | 選択値境界 | groupby 先頭選択肢 | --groupby に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-072 | 選択値境界 | groupby 末尾選択肢 | --groupby に選択肢の末尾値 svmsg_date を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-073 | 選択値境界 | groupby 不正選択肢 | --groupby に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-074 | 複数値境界 | groupby 0件 | --groupby に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-075 | 複数値境界 | groupby 1件 | --groupby に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-076 | 複数値境界 | groupby 複数件 | --groupby に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-077 | 型境界 | groupby 空文字 | --groupby に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-078 | 型境界 | groupby 1文字 | --groupby に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-079 | 型境界 | groupby 特殊文字 | --groupby に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-080 | 型境界 | groupby 長文 | --groupby に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-081 | 選択値境界 | groupby_date_format 先頭選択肢 | --groupby_date_format に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-082 | 選択値境界 | groupby_date_format 末尾選択肢 | --groupby_date_format に選択肢の末尾値 %u を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-083 | 選択値境界 | groupby_date_format 不正選択肢 | --groupby_date_format に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-084 | 型境界 | groupby_date_format 空文字 | --groupby_date_format に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-085 | 型境界 | groupby_date_format 1文字 | --groupby_date_format に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-086 | 型境界 | groupby_date_format 特殊文字 | --groupby_date_format に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-087 | 型境界 | groupby_date_format 長文 | --groupby_date_format に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-088 | 複数値境界 | sort 0件 | --sort に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-089 | 複数値境界 | sort 1件 | --sort に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-090 | 複数値境界 | sort 複数件 | --sort に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-091 | 型境界 | offset=0 | --offset に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-092 | 型境界 | offset=1 | --offset に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-093 | 型境界 | offset=-1 | --offset に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-094 | 型境界 | offset=2147483647 | --offset に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-095 | 型境界 | limit=0 | --limit に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-096 | 型境界 | limit=1 | --limit に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-097 | 型境界 | limit=-1 | --limit に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-098 | 型境界 | limit=2147483647 | --limit に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-099 | 型境界 | csv=False | --csv に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-100 | 型境界 | csv=True | --csv に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-101 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-102 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 生成物が空でなく、フォーマット不整合がないことを確認する |
| TC-103 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_audit_search.py
- 詳細設計書: Specifications/cli/audit/search.md
- 生成日時: 2026-04-19T21:16:02