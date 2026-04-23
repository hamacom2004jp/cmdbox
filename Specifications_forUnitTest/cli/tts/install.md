# tts install

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | tts |
| cmd | install |
| クラス | TtsInstall |
| モジュール | cmdbox.app.features.cli.cmdbox_tts_install |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_tts_install.py |
| 詳細設計書 | Specifications/cli/tts/install.md |
| 実装上の必須推定 | data |

## 概要

- 日本語: Text-to-Speech(TTS)エンジンをインストールします。
- 英語: Installs the Text-to-Speech (TTS) engine.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_2, INT_1
- 結果キー候補: warn

## 副作用確認観点

- 戻り値とログのみを確認対象とする

## 詳細設計からの観点

- 選択肢を持つパラメータ client_only, force_install, tts_engine, voicevox_ver, voicevox_whl, openjtalk_ver, openjtalk_dic, onnxruntime_ver, onnxruntime_lib の境界値と不正値を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_2, INT_1 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --data=C:\Users\hama\.cmdbox、--tts_engine=。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 戻り値以外の副作用がないことを確認する |
| TC-002 | 型境界 | data 既存空ディレクトリ | --data に既存の空ディレクトリを指定する | RESP_SUCCESS | 空ディレクトリ前提の初期状態が正常に処理される | 必要な初期化ファイルやサブディレクトリが作成される場合は生成を確認する |
| TC-003 | 型境界 | data 既存データありディレクトリ | --data に既存データを含むディレクトリを指定する | RESP_SUCCESS | 既存データを読み込む経路が正常に処理される | 既存ファイルを意図せず破壊しないことを確認する |
| TC-004 | 型境界 | data 非存在ディレクトリ | --data に存在しないディレクトリを指定する | RESP_WARN | 存在チェックエラーまたは初期化失敗が返る | 自動作成される仕様でない限り、ディレクトリが勝手に作成されないことを確認する |
| TC-005 | 型境界 | client_only=False | --client_only に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-006 | 型境界 | client_only=True | --client_only に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-007 | 型境界 | force_install=False | --force_install に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-008 | 型境界 | force_install=True | --force_install に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-009 | 選択値境界 | tts_engine 先頭選択肢 | --tts_engine に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-010 | 選択値境界 | tts_engine 末尾選択肢 | --tts_engine に選択肢の末尾値 voicevox を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-011 | 選択値境界 | tts_engine 不正選択肢 | --tts_engine に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-012 | 型境界 | tts_engine 空文字 | --tts_engine に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-013 | 型境界 | tts_engine 1文字 | --tts_engine に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-014 | 型境界 | tts_engine 特殊文字 | --tts_engine に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-015 | 型境界 | tts_engine 長文 | --tts_engine に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-016 | 選択値境界 | voicevox_ver 先頭選択肢 | --voicevox_ver に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-017 | 選択値境界 | voicevox_ver 末尾選択肢 | --voicevox_ver に選択肢の末尾値 0.16.3 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-018 | 選択値境界 | voicevox_ver 不正選択肢 | --voicevox_ver に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-019 | 型境界 | voicevox_ver 空文字 | --voicevox_ver に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-020 | 型境界 | voicevox_ver 1文字 | --voicevox_ver に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-021 | 型境界 | voicevox_ver 特殊文字 | --voicevox_ver に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-022 | 型境界 | voicevox_ver 長文 | --voicevox_ver に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-023 | 選択値境界 | voicevox_whl 先頭選択肢 | --voicevox_whl に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-024 | 選択値境界 | voicevox_whl 末尾選択肢 | --voicevox_whl に選択肢の末尾値 voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-025 | 選択値境界 | voicevox_whl 不正選択肢 | --voicevox_whl に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-026 | 型境界 | voicevox_whl 空文字 | --voicevox_whl に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-027 | 型境界 | voicevox_whl 1文字 | --voicevox_whl に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-028 | 型境界 | voicevox_whl 特殊文字 | --voicevox_whl に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-029 | 型境界 | voicevox_whl 長文 | --voicevox_whl に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-030 | 選択値境界 | openjtalk_ver 先頭選択肢 | --openjtalk_ver に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-031 | 選択値境界 | openjtalk_ver 末尾選択肢 | --openjtalk_ver に選択肢の末尾値 v1.11.1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-032 | 選択値境界 | openjtalk_ver 不正選択肢 | --openjtalk_ver に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-033 | 型境界 | openjtalk_ver 空文字 | --openjtalk_ver に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-034 | 型境界 | openjtalk_ver 1文字 | --openjtalk_ver に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-035 | 型境界 | openjtalk_ver 特殊文字 | --openjtalk_ver に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-036 | 型境界 | openjtalk_ver 長文 | --openjtalk_ver に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-037 | 選択値境界 | openjtalk_dic 先頭選択肢 | --openjtalk_dic に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-038 | 選択値境界 | openjtalk_dic 末尾選択肢 | --openjtalk_dic に選択肢の末尾値 open_jtalk_dic_utf_8-1.11.tar.gz を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-039 | 選択値境界 | openjtalk_dic 不正選択肢 | --openjtalk_dic に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-040 | 型境界 | openjtalk_dic 空文字 | --openjtalk_dic に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-041 | 型境界 | openjtalk_dic 1文字 | --openjtalk_dic に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-042 | 型境界 | openjtalk_dic 特殊文字 | --openjtalk_dic に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-043 | 型境界 | openjtalk_dic 長文 | --openjtalk_dic に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-044 | 選択値境界 | onnxruntime_ver 先頭選択肢 | --onnxruntime_ver に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-045 | 選択値境界 | onnxruntime_ver 末尾選択肢 | --onnxruntime_ver に選択肢の末尾値 voicevox_onnxruntime-1.17.3 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-046 | 選択値境界 | onnxruntime_ver 不正選択肢 | --onnxruntime_ver に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-047 | 型境界 | onnxruntime_ver 空文字 | --onnxruntime_ver に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-048 | 型境界 | onnxruntime_ver 1文字 | --onnxruntime_ver に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-049 | 型境界 | onnxruntime_ver 特殊文字 | --onnxruntime_ver に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-050 | 型境界 | onnxruntime_ver 長文 | --onnxruntime_ver に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-051 | 選択値境界 | onnxruntime_lib 先頭選択肢 | --onnxruntime_lib に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-052 | 選択値境界 | onnxruntime_lib 末尾選択肢 | --onnxruntime_lib に選択肢の末尾値 voicevox_onnxruntime-win-x86-1.17.3.tgz を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-053 | 選択値境界 | onnxruntime_lib 不正選択肢 | --onnxruntime_lib に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-054 | 型境界 | onnxruntime_lib 空文字 | --onnxruntime_lib に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-055 | 型境界 | onnxruntime_lib 1文字 | --onnxruntime_lib に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-056 | 型境界 | onnxruntime_lib 特殊文字 | --onnxruntime_lib に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-057 | 型境界 | onnxruntime_lib 長文 | --onnxruntime_lib に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-058 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_tts_install.py
- 詳細設計書: Specifications/cli/tts/install.md
- 生成日時: 2026-04-23T23:40:14