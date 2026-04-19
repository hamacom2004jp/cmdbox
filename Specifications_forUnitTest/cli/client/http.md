# client http

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | client |
| cmd | http |
| クラス | ClientHttp |
| モジュール | cmdbox.app.features.cli.cmdbox_client_http |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_client_http.py |
| 詳細設計書 | Specifications/cli/client/http.md |
| 実装上の必須推定 | url |

## 概要

- 日本語: HTTPサーバーに対してリクエストを送信し、レスポンスを取得します。
- 英語: Sends a request to the HTTP server and gets a response.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn, error

## 副作用確認観点

- 戻り値とログのみを確認対象とする

## 詳細設計からの観点

- 必須パラメータ url が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ proxy, send_method, send_content_type, send_verify, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ send_header, send_param の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn, error が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --url=enabled_value、--send_method=GET。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 戻り値以外の副作用がないことを確認する |
| TC-002 | 必須チェック | url 未指定 | --url を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --url の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | url 空文字 | --url に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-004 | 型境界 | url 1文字 | --url に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-005 | 型境界 | url 特殊文字 | --url に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-006 | 型境界 | url 長文 | --url に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-007 | 選択値境界 | proxy 先頭選択肢 | --proxy に選択肢の先頭値 no を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-008 | 選択値境界 | proxy 末尾選択肢 | --proxy に選択肢の末尾値 yes を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-009 | 選択値境界 | proxy 不正選択肢 | --proxy に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-010 | 型境界 | proxy 空文字 | --proxy に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-011 | 型境界 | proxy 1文字 | --proxy に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-012 | 型境界 | proxy 特殊文字 | --proxy に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-013 | 型境界 | proxy 長文 | --proxy に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-014 | 選択値境界 | send_method 先頭選択肢 | --send_method に選択肢の先頭値 GET を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-015 | 選択値境界 | send_method 末尾選択肢 | --send_method に選択肢の末尾値 OPTIONS を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-016 | 選択値境界 | send_method 不正選択肢 | --send_method に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-017 | 型境界 | send_method 空文字 | --send_method に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-018 | 型境界 | send_method 1文字 | --send_method に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-019 | 型境界 | send_method 特殊文字 | --send_method に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-020 | 型境界 | send_method 長文 | --send_method に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-021 | 選択値境界 | send_content_type 先頭選択肢 | --send_content_type に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-022 | 選択値境界 | send_content_type 末尾選択肢 | --send_content_type に選択肢の末尾値 multipart/form-data を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-023 | 選択値境界 | send_content_type 不正選択肢 | --send_content_type に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-024 | 型境界 | send_content_type 空文字 | --send_content_type に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-025 | 型境界 | send_content_type 1文字 | --send_content_type に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-026 | 型境界 | send_content_type 特殊文字 | --send_content_type に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-027 | 型境界 | send_content_type 長文 | --send_content_type に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-028 | 型境界 | send_apikey 空文字 | --send_apikey に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-029 | 型境界 | send_apikey 1文字 | --send_apikey に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-030 | 型境界 | send_apikey 特殊文字 | --send_apikey に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-031 | 型境界 | send_apikey 長文 | --send_apikey に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-032 | 複数値境界 | send_header 0件 | --send_header に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-033 | 複数値境界 | send_header 1件 | --send_header に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-034 | 複数値境界 | send_header 複数件 | --send_header に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-035 | 複数値境界 | send_param 0件 | --send_param に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-036 | 複数値境界 | send_param 1件 | --send_param に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-037 | 複数値境界 | send_param 複数件 | --send_param に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-038 | 型境界 | send_data 空文字 | --send_data に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-039 | 型境界 | send_data 1文字 | --send_data に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-040 | 型境界 | send_data 特殊文字 | --send_data に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-041 | 型境界 | send_data 長文 | --send_data に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-042 | 型境界 | send_verify=False | --send_verify に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-043 | 型境界 | send_verify=True | --send_verify に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-044 | 型境界 | send_timeout=0 | --send_timeout に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-045 | 型境界 | send_timeout=1 | --send_timeout に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-046 | 型境界 | send_timeout=-1 | --send_timeout に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-047 | 型境界 | send_timeout=2147483647 | --send_timeout に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, error が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-048 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn, error が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_client_http.py
- 詳細設計書: Specifications/cli/client/http.md
- 生成日時: 2026-04-19T21:16:02