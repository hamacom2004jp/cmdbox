# client file_download

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | client |
| cmd | file_download |
| クラス | ClientFileDownload |
| モジュール | cmdbox.app.features.cli.cmdbox_client_file_download |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_client_file_download.py |
| 詳細設計書 | Specifications/cli/client/file_download.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: サーバー側のデータフォルダ配下のファイルをダウンロードします。
- 英語: Download a file under the data folder on the server.

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

- download_file で指定した出力ファイルが作成され、内容が空でないことを確認する
- output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する

## 詳細設計からの観点

- 必須パラメータ fwpath が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ scope, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ fwpath の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --svpath=/、--fwpath=enabled_value、--scope=client。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | download_file で指定した出力ファイルが作成され、内容が空でないことを確認する / output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |
| TC-002 | 必須チェック | fwpath 未指定 | --fwpath を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --fwpath の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 複数値境界 | fwpath 0件 | --fwpath に空配列または未指定を与える | RESP_WARN | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-004 | 複数値境界 | fwpath 1件 | --fwpath に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-005 | 複数値境界 | fwpath 複数件 | --fwpath に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-006 | 型境界 | etag 空文字 | --etag に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-007 | 型境界 | etag 1文字 | --etag に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-008 | 型境界 | etag 特殊文字 | --etag に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-009 | 型境界 | etag 長文 | --etag に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-010 | 選択値境界 | scope 先頭選択肢 | --scope に選択肢の先頭値 client を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-011 | 選択値境界 | scope 末尾選択肢 | --scope に選択肢の末尾値 server を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-012 | 選択値境界 | scope 不正選択肢 | --scope に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-013 | 型境界 | scope 空文字 | --scope に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-014 | 型境界 | scope 1文字 | --scope に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-015 | 型境界 | scope 特殊文字 | --scope に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-016 | 型境界 | scope 長文 | --scope に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-017 | 型境界 | rpath 空文字 | --rpath に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-018 | 型境界 | rpath 1文字 | --rpath に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-019 | 型境界 | rpath 特殊文字 | --rpath に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-020 | 型境界 | rpath 長文 | --rpath に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-021 | ファイルI/O | download_file 新規出力 | --download_file に存在しない新規出力先を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | download_file で指定した出力ファイルが作成され、内容が空でないことを確認する |
| TC-022 | ファイルI/O | download_file 既存出力先 | --download_file に既存ファイルを指定する | RESP_SUCCESS | 上書きまたは追記の仕様どおりに出力される | download_file で指定した出力ファイルが作成され、内容が空でないことを確認する |
| TC-023 | ファイルI/O | download_file 無効出力先 | --download_file に親ディレクトリが存在しないパスを指定する | RESP_WARN | 保存失敗が検知され、エラーまたは警告になる | 不完全ファイルが残らないことを確認する |
| TC-024 | 型境界 | client_data 空文字 | --client_data に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-025 | 型境界 | client_data 1文字 | --client_data に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-026 | 型境界 | client_data 特殊文字 | --client_data に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-027 | 型境界 | client_data 長文 | --client_data に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-028 | 型境界 | img_thumbnail=0.0 | --img_thumbnail に 0.0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 浮動小数の比較誤差やオーバーフローが起きないことを確認する |
| TC-029 | 型境界 | img_thumbnail=1.0 | --img_thumbnail に 1.0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 浮動小数の比較誤差やオーバーフローが起きないことを確認する |
| TC-030 | 型境界 | img_thumbnail=-1.0 | --img_thumbnail に -1.0 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 浮動小数の比較誤差やオーバーフローが起きないことを確認する |
| TC-031 | 型境界 | img_thumbnail=1e+308 | --img_thumbnail に 1e+308 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 浮動小数の比較誤差やオーバーフローが起きないことを確認する |
| TC-032 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-033 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | download_file で指定した出力ファイルが作成され、内容が空でないことを確認する / output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |
| TC-034 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_client_file_download.py
- 詳細設計書: Specifications/cli/client/file_download.md
- 生成日時: 2026-04-23T23:40:13