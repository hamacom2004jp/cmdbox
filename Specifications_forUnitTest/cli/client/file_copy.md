# client file_copy

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | client |
| cmd | file_copy |
| クラス | ClientFileCopy |
| モジュール | cmdbox.app.features.cli.cmdbox_client_file_copy |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_client_file_copy.py |
| 詳細設計書 | Specifications/cli/client/file_copy.md |
| 実装上の必須推定 | svname |

## 概要

- 日本語: サーバー側のデータフォルダ配下のファイルをコピーします。
- 英語: Copy the files under the data folder on the server side.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。
- 出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_2
- 結果キー候補: warn

## 副作用確認観点

- output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する
- 生成物が空でなく、フォーマット不整合がないことを確認する

## 詳細設計からの観点

- 必須パラメータ from_path, to_path, from_fwpath, to_fwpath が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ orverwrite, scope, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ from_fwpath, to_fwpath の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --from_path=enabled_value、--to_path=enabled_value、--from_fwpath=enabled_value、--to_fwpath=enabled_value、--scope=client。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 生成物が空でなく、フォーマット不整合がないことを確認する |
| TC-002 | 必須チェック | from_path 未指定 | --from_path を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --from_path の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 必須チェック | to_path 未指定 | --to_path を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --to_path の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-004 | 必須チェック | from_fwpath 未指定 | --from_fwpath を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --from_fwpath の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-005 | 複数値境界 | from_fwpath 0件 | --from_fwpath に空配列または未指定を与える | RESP_WARN | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-006 | 複数値境界 | from_fwpath 1件 | --from_fwpath に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-007 | 複数値境界 | from_fwpath 複数件 | --from_fwpath に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-008 | 必須チェック | to_fwpath 未指定 | --to_fwpath を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --to_fwpath の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-009 | 複数値境界 | to_fwpath 0件 | --to_fwpath に空配列または未指定を与える | RESP_WARN | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-010 | 複数値境界 | to_fwpath 1件 | --to_fwpath に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-011 | 複数値境界 | to_fwpath 複数件 | --to_fwpath に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-012 | 型境界 | orverwrite=False | --orverwrite に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-013 | 型境界 | orverwrite=True | --orverwrite に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-014 | 選択値境界 | scope 先頭選択肢 | --scope に選択肢の先頭値 client を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-015 | 選択値境界 | scope 末尾選択肢 | --scope に選択肢の末尾値 server を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-016 | 選択値境界 | scope 不正選択肢 | --scope に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-017 | 型境界 | scope 空文字 | --scope に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-018 | 型境界 | scope 1文字 | --scope に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-019 | 型境界 | scope 特殊文字 | --scope に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-020 | 型境界 | scope 長文 | --scope に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-021 | 型境界 | client_data 空文字 | --client_data に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-022 | 型境界 | client_data 1文字 | --client_data に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-023 | 型境界 | client_data 特殊文字 | --client_data に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-024 | 型境界 | client_data 長文 | --client_data に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-025 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-026 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 生成物が空でなく、フォーマット不整合がないことを確認する |
| TC-027 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_client_file_copy.py
- 詳細設計書: Specifications/cli/client/file_copy.md
- 生成日時: 2026-04-19T21:16:02