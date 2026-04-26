# web gencert

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | web |
| cmd | gencert |
| クラス | WebGencert |
| モジュール | cmdbox.app.features.cli.cmdbox_web_gencert |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_web_gencert.py |
| 詳細設計書 | Specifications/cli/web/gencert.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: webモードでSSLを簡易的に実装するために自己署名証明書を生成します。
- 英語: Generate a self-signed certificate for simple implementation of SSL in web mode.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。
- 出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn, success, error

## 副作用確認観点

- output_cert で指定した出力ファイルが作成され、内容が空でないことを確認する
- output_pkey で指定した出力ファイルが作成され、内容が空でないことを確認する
- output_key で指定した出力ファイルが作成され、内容が空でないことを確認する
- 生成物が空でなく、フォーマット不整合がないことを確認する

## 詳細設計からの観点

- 選択肢を持つパラメータ output_cert_format, output_pkey_format, output_key_format, overwrite, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn, success, error が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --webhost=localhost。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | output_cert で指定した出力ファイルが作成され、内容が空でないことを確認する / output_pkey で指定した出力ファイルが作成され、内容が空でないことを確認する / output_key で指定した出力ファイルが作成され、内容が空でないことを確認する / 生成物が空でなく、フォーマット不整合がないことを確認する |
| TC-002 | 型境界 | webhost 1文字 | --webhost に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-003 | 型境界 | webhost 特殊文字 | --webhost に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-004 | 型境界 | webhost 長文 | --webhost に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-005 | ファイルI/O | output_cert 新規出力 | --output_cert に存在しない新規出力先を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | output_cert で指定した出力ファイルが作成され、内容が空でないことを確認する |
| TC-006 | ファイルI/O | output_cert 既存出力先 | --output_cert に既存ファイルを指定する | RESP_SUCCESS | 上書きまたは追記の仕様どおりに出力される | output_cert で指定した出力ファイルが作成され、内容が空でないことを確認する |
| TC-007 | ファイルI/O | output_cert 無効出力先 | --output_cert に親ディレクトリが存在しないパスを指定する | RESP_WARN | 保存失敗が検知され、エラーまたは警告になる | 不完全ファイルが残らないことを確認する |
| TC-008 | 選択値境界 | output_cert_format 先頭選択肢 | --output_cert_format に選択肢の先頭値 DER を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-009 | 選択値境界 | output_cert_format 末尾選択肢 | --output_cert_format に選択肢の末尾値 PEM を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-010 | 選択値境界 | output_cert_format 不正選択肢 | --output_cert_format に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-011 | ファイルI/O | output_pkey 新規出力 | --output_pkey に存在しない新規出力先を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | output_pkey で指定した出力ファイルが作成され、内容が空でないことを確認する |
| TC-012 | ファイルI/O | output_pkey 既存出力先 | --output_pkey に既存ファイルを指定する | RESP_SUCCESS | 上書きまたは追記の仕様どおりに出力される | output_pkey で指定した出力ファイルが作成され、内容が空でないことを確認する |
| TC-013 | ファイルI/O | output_pkey 無効出力先 | --output_pkey に親ディレクトリが存在しないパスを指定する | RESP_WARN | 保存失敗が検知され、エラーまたは警告になる | 不完全ファイルが残らないことを確認する |
| TC-014 | 選択値境界 | output_pkey_format 先頭選択肢 | --output_pkey_format に選択肢の先頭値 DER を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-015 | 選択値境界 | output_pkey_format 末尾選択肢 | --output_pkey_format に選択肢の末尾値 PEM を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-016 | 選択値境界 | output_pkey_format 不正選択肢 | --output_pkey_format に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-017 | ファイルI/O | output_key 新規出力 | --output_key に存在しない新規出力先を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | output_key で指定した出力ファイルが作成され、内容が空でないことを確認する |
| TC-018 | ファイルI/O | output_key 既存出力先 | --output_key に既存ファイルを指定する | RESP_SUCCESS | 上書きまたは追記の仕様どおりに出力される | output_key で指定した出力ファイルが作成され、内容が空でないことを確認する |
| TC-019 | ファイルI/O | output_key 無効出力先 | --output_key に親ディレクトリが存在しないパスを指定する | RESP_WARN | 保存失敗が検知され、エラーまたは警告になる | 不完全ファイルが残らないことを確認する |
| TC-020 | 選択値境界 | output_key_format 先頭選択肢 | --output_key_format に選択肢の先頭値 DER を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-021 | 選択値境界 | output_key_format 末尾選択肢 | --output_key_format に選択肢の末尾値 PEM を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, error が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-022 | 選択値境界 | output_key_format 不正選択肢 | --output_key_format に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-023 | 型境界 | overwrite=False | --overwrite に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-024 | 型境界 | overwrite=True | --overwrite に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-025 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_cert で指定した出力ファイルが作成され、内容が空でないことを確認する / output_pkey で指定した出力ファイルが作成され、内容が空でないことを確認する / output_key で指定した出力ファイルが作成され、内容が空でないことを確認する / 生成物が空でなく、フォーマット不整合がないことを確認する |
| TC-026 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn, success, error が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_web_gencert.py
- 詳細設計書: Specifications/cli/web/gencert.md
- 生成日時: 2026-04-26T00:53:18