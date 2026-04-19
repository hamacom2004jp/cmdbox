# tts say

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | tts |
| cmd | say |
| クラス | TtsSay |
| モジュール | cmdbox.app.features.cli.cmdbox_tts_say |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_tts_say.py |
| 詳細設計書 | Specifications/cli/tts/say.md |
| 実装上の必須推定 | tts_engine, tts_text |

## 概要

- 日本語: Text-to-Speech(TTS)エンジンを使ってテキストを音声に変換します。
- 英語: Converts text to speech using the Text-to-Speech (TTS) engine.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。
- 出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_2, INT_1
- 結果キー候補: warn

## 副作用確認観点

- tts_output で指定した出力ファイルが作成され、内容が空でないことを確認する
- 生成物が空でなく、フォーマット不整合がないことを確認する

## 詳細設計からの観点

- 必須パラメータ tts_text が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ tts_engine, voicevox_model の境界値と不正値を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_2, INT_1 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --tts_engine=、--tts_text=enabled_value。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | tts_output で指定した出力ファイルが作成され、内容が空でないことを確認する / 生成物が空でなく、フォーマット不整合がないことを確認する |
| TC-002 | 選択値境界 | tts_engine 先頭選択肢 | --tts_engine に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-003 | 選択値境界 | tts_engine 末尾選択肢 | --tts_engine に選択肢の末尾値 voicevox を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-004 | 選択値境界 | tts_engine 不正選択肢 | --tts_engine に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-005 | 型境界 | tts_engine 空文字 | --tts_engine に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-006 | 型境界 | tts_engine 1文字 | --tts_engine に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-007 | 型境界 | tts_engine 特殊文字 | --tts_engine に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-008 | 型境界 | tts_engine 長文 | --tts_engine に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-009 | 選択値境界 | voicevox_model 先頭選択肢 | --voicevox_model に選択肢の先頭値 No.7アナウンス を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-010 | 選択値境界 | voicevox_model 末尾選択肢 | --voicevox_model に選択肢の末尾値 黒沢冴白ノーマル を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-011 | 選択値境界 | voicevox_model 不正選択肢 | --voicevox_model に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-012 | 型境界 | voicevox_model 空文字 | --voicevox_model に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-013 | 型境界 | voicevox_model 1文字 | --voicevox_model に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-014 | 型境界 | voicevox_model 特殊文字 | --voicevox_model に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-015 | 型境界 | voicevox_model 長文 | --voicevox_model に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-016 | 必須チェック | tts_text 未指定 | --tts_text を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --tts_text の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-017 | 型境界 | tts_text 空文字 | --tts_text に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-018 | 型境界 | tts_text 1文字 | --tts_text に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-019 | 型境界 | tts_text 特殊文字 | --tts_text に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-020 | 型境界 | tts_text 長文 | --tts_text に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-021 | ファイルI/O | tts_output 新規出力 | --tts_output に存在しない新規出力先を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn が含まれる | tts_output で指定した出力ファイルが作成され、内容が空でないことを確認する |
| TC-022 | ファイルI/O | tts_output 既存出力先 | --tts_output に既存ファイルを指定する | RESP_SUCCESS | 上書きまたは追記の仕様どおりに出力される | tts_output で指定した出力ファイルが作成され、内容が空でないことを確認する |
| TC-023 | ファイルI/O | tts_output 無効出力先 | --tts_output に親ディレクトリが存在しないパスを指定する | RESP_WARN | 保存失敗が検知され、エラーまたは警告になる | 不完全ファイルが残らないことを確認する |
| TC-024 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | tts_output で指定した出力ファイルが作成され、内容が空でないことを確認する / 生成物が空でなく、フォーマット不整合がないことを確認する |
| TC-025 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_tts_say.py
- 詳細設計書: Specifications/cli/tts/say.md
- 生成日時: 2026-04-19T21:16:02