# llm save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | llm |
| cmd | save |
| クラス | LLMSave |
| モジュール | cmdbox.app.features.cli.cmdbox_llm_save |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_llm_save.py |
| 詳細設計書 | Specifications/cli/llm/save.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: LLM 設定を保存します。
- 英語: Saves LLM configuration.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。
- 出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_2
- 結果キー候補: warn, success

## 副作用確認観点

- output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する
- 必要なディレクトリが生成され、再実行時も競合しないことを確認する

## 詳細設計からの観点

- 必須パラメータ llmname, llmprov が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ llmprov, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --llmname=enabled_value、--llmprov=。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 必要なディレクトリが生成され、再実行時も競合しないことを確認する |
| TC-002 | 必須チェック | llmname 未指定 | --llmname を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --llmname の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | llmname 空文字 | --llmname に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-004 | 型境界 | llmname 1文字 | --llmname に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-005 | 型境界 | llmname 特殊文字 | --llmname に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-006 | 型境界 | llmname 長文 | --llmname に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-007 | 必須チェック | llmprov 未指定 | --llmprov を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --llmprov の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-008 | 選択値境界 | llmprov 先頭選択肢 | --llmprov に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-009 | 選択値境界 | llmprov 末尾選択肢 | --llmprov に選択肢の末尾値 ollama を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-010 | 選択値境界 | llmprov 不正選択肢 | --llmprov に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-011 | 型境界 | llmprov 空文字 | --llmprov に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-012 | 型境界 | llmprojectid 空文字 | --llmprojectid に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-013 | 型境界 | llmprojectid 1文字 | --llmprojectid に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-014 | 型境界 | llmprojectid 特殊文字 | --llmprojectid に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-015 | 型境界 | llmprojectid 長文 | --llmprojectid に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-016 | ファイルI/O | llmsvaccountfile 有効入力ファイル | --llmsvaccountfile に存在する妥当なファイルを指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 入力ファイル内容が意図どおり読み込まれることを確認する |
| TC-017 | ファイルI/O | llmsvaccountfile 存在しない入力ファイル | --llmsvaccountfile に存在しないパスを指定する | RESP_WARN | ファイル未存在のエラーまたは警告が返る | 後続処理に進まず、副作用が発生しないことを確認する |
| TC-018 | ファイルI/O | llmsvaccountfile 空ファイル | --llmsvaccountfile に 0 byte の空ファイルを指定する | RESP_WARN | フォーマット不正または入力不足として扱われる | 異常終了時のログやエラー文言が十分であることを確認する |
| TC-019 | 型境界 | llmlocation 空文字 | --llmlocation に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-020 | 型境界 | llmlocation 1文字 | --llmlocation に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-021 | 型境界 | llmlocation 特殊文字 | --llmlocation に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-022 | 型境界 | llmlocation 長文 | --llmlocation に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-023 | 型境界 | llmapikey 空文字 | --llmapikey に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-024 | 型境界 | llmapikey 1文字 | --llmapikey に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-025 | 型境界 | llmapikey 特殊文字 | --llmapikey に a_日本語 space-_.#"'&<> を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-026 | 型境界 | llmapiversion 空文字 | --llmapiversion に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-027 | 型境界 | llmapiversion 1文字 | --llmapiversion に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-028 | 型境界 | llmapiversion 特殊文字 | --llmapiversion に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-029 | 型境界 | llmapiversion 長文 | --llmapiversion に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-030 | 型境界 | llmendpoint 空文字 | --llmendpoint に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-031 | 型境界 | llmendpoint 1文字 | --llmendpoint に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-032 | 型境界 | llmendpoint 特殊文字 | --llmendpoint に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-033 | 型境界 | llmendpoint 長文 | --llmendpoint に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-034 | 型境界 | llmmodel 1文字 | --llmmodel に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-035 | 型境界 | llmmodel 特殊文字 | --llmmodel に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-036 | 型境界 | llmmodel 長文 | --llmmodel に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-037 | 型境界 | llmseed=0 | --llmseed に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-038 | 型境界 | llmseed=1 | --llmseed に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-039 | 型境界 | llmseed=-1 | --llmseed に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-040 | 型境界 | llmseed=2147483647 | --llmseed に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-041 | 型境界 | llmtemperature=0.0 | --llmtemperature に 0.0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 浮動小数の比較誤差やオーバーフローが起きないことを確認する |
| TC-042 | 型境界 | llmtemperature=1.0 | --llmtemperature に 1.0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 浮動小数の比較誤差やオーバーフローが起きないことを確認する |
| TC-043 | 型境界 | llmtemperature=-1.0 | --llmtemperature に -1.0 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 浮動小数の比較誤差やオーバーフローが起きないことを確認する |
| TC-044 | 型境界 | llmtemperature=1e+308 | --llmtemperature に 1e+308 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 浮動小数の比較誤差やオーバーフローが起きないことを確認する |
| TC-045 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-046 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 必要なディレクトリが生成され、再実行時も競合しないことを確認する |
| TC-047 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn, success が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_llm_save.py
- 詳細設計書: Specifications/cli/llm/save.md
- 生成日時: 2026-04-26T00:53:18