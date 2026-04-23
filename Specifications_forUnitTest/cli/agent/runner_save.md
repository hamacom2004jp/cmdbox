# agent runner_save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | runner_save |
| クラス | AgentRunnerSave |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_runner_save |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_runner_save.py |
| 詳細設計書 | Specifications/cli/agent/runner_save.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: Runner 設定を保存します。
- 英語: Saves runner configuration.

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

- 必須パラメータ runner_name, agent が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ session_store_type, tts_engine, voicevox_model, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ rag の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --runner_name=enabled_value、--agent=enabled_value、--tts_engine=。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 必要なディレクトリが生成され、再実行時も競合しないことを確認する |
| TC-002 | 必須チェック | runner_name 未指定 | --runner_name を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --runner_name の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | runner_name 空文字 | --runner_name に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-004 | 型境界 | runner_name 1文字 | --runner_name に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-005 | 型境界 | runner_name 特殊文字 | --runner_name に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-006 | 型境界 | runner_name 長文 | --runner_name に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-007 | 必須チェック | agent 未指定 | --agent を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --agent の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-008 | 型境界 | agent 空文字 | --agent に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-009 | 型境界 | agent 1文字 | --agent に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-010 | 型境界 | agent 特殊文字 | --agent に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-011 | 型境界 | agent 長文 | --agent に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-012 | 選択値境界 | session_store_type 先頭選択肢 | --session_store_type に選択肢の先頭値 memory を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-013 | 選択値境界 | session_store_type 末尾選択肢 | --session_store_type に選択肢の末尾値 postgresql を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-014 | 選択値境界 | session_store_type 不正選択肢 | --session_store_type に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-015 | 型境界 | session_store_type 空文字 | --session_store_type に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-016 | 型境界 | session_store_type 1文字 | --session_store_type に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-017 | 型境界 | session_store_type 特殊文字 | --session_store_type に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-018 | 型境界 | session_store_type 長文 | --session_store_type に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-019 | 選択値境界 | tts_engine 先頭選択肢 | --tts_engine に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-020 | 選択値境界 | tts_engine 末尾選択肢 | --tts_engine に選択肢の末尾値 voicevox を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-021 | 選択値境界 | tts_engine 不正選択肢 | --tts_engine に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-022 | 型境界 | tts_engine 空文字 | --tts_engine に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-023 | 型境界 | tts_engine 1文字 | --tts_engine に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-024 | 型境界 | tts_engine 特殊文字 | --tts_engine に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-025 | 型境界 | tts_engine 長文 | --tts_engine に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-026 | 型境界 | memory 空文字 | --memory に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-027 | 型境界 | memory 1文字 | --memory に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-028 | 型境界 | memory 特殊文字 | --memory に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-029 | 型境界 | memory 長文 | --memory に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-030 | 複数値境界 | rag 0件 | --rag に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-031 | 複数値境界 | rag 1件 | --rag に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-032 | 複数値境界 | rag 複数件 | --rag に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-033 | 型境界 | rag 空文字 | --rag に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-034 | 型境界 | rag 1文字 | --rag に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-035 | 型境界 | rag 特殊文字 | --rag に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-036 | 型境界 | rag 長文 | --rag に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-037 | 選択値境界 | voicevox_model 先頭選択肢 | --voicevox_model に選択肢の先頭値 No.7アナウンス を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-038 | 選択値境界 | voicevox_model 末尾選択肢 | --voicevox_model に選択肢の末尾値 黒沢冴白ノーマル を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-039 | 選択値境界 | voicevox_model 不正選択肢 | --voicevox_model に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-040 | 型境界 | voicevox_model 空文字 | --voicevox_model に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-041 | 型境界 | voicevox_model 1文字 | --voicevox_model に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-042 | 型境界 | voicevox_model 特殊文字 | --voicevox_model に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-043 | 型境界 | voicevox_model 長文 | --voicevox_model に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-044 | 型境界 | session_store_pghost 空文字 | --session_store_pghost に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-045 | 型境界 | session_store_pghost 1文字 | --session_store_pghost に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-046 | 型境界 | session_store_pghost 特殊文字 | --session_store_pghost に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-047 | 型境界 | session_store_pghost 長文 | --session_store_pghost に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-048 | 型境界 | session_store_pgport=0 | --session_store_pgport に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-049 | 型境界 | session_store_pgport=1 | --session_store_pgport に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-050 | 型境界 | session_store_pgport=-1 | --session_store_pgport に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-051 | 型境界 | session_store_pgport=2147483647 | --session_store_pgport に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-052 | 型境界 | session_store_pguser 空文字 | --session_store_pguser に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-053 | 型境界 | session_store_pguser 1文字 | --session_store_pguser に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-054 | 型境界 | session_store_pguser 特殊文字 | --session_store_pguser に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-055 | 型境界 | session_store_pguser 長文 | --session_store_pguser に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-056 | 型境界 | session_store_pgpass 空文字 | --session_store_pgpass に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-057 | 型境界 | session_store_pgpass 1文字 | --session_store_pgpass に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-058 | 型境界 | session_store_pgpass 特殊文字 | --session_store_pgpass に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-059 | 型境界 | session_store_pgpass 長文 | --session_store_pgpass に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-060 | 型境界 | session_store_pgdbname 空文字 | --session_store_pgdbname に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-061 | 型境界 | session_store_pgdbname 1文字 | --session_store_pgdbname に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-062 | 型境界 | session_store_pgdbname 特殊文字 | --session_store_pgdbname に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-063 | 型境界 | session_store_pgdbname 長文 | --session_store_pgdbname に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-064 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-065 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 必要なディレクトリが生成され、再実行時も競合しないことを確認する |
| TC-066 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn, success が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_runner_save.py
- 詳細設計書: Specifications/cli/agent/runner_save.md
- 生成日時: 2026-04-23T23:40:13