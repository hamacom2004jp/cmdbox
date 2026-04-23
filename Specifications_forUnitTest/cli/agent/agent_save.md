# agent agent_save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | agent_save |
| クラス | AgentAgentSave |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_agent_save |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_agent_save.py |
| 詳細設計書 | Specifications/cli/agent/agent_save.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: Agent 設定を保存します。
- 英語: Saves agent configuration.

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

- 必須パラメータ agent_name, llm が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ agent_type, use_planner, a2asv_delegated_auth, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ mcpservers, subagents の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --agent_name=enabled_value、--agent_type=、--llm=enabled_value。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 必要なディレクトリが生成され、再実行時も競合しないことを確認する |
| TC-002 | 必須チェック | agent_name 未指定 | --agent_name を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --agent_name の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | agent_name 空文字 | --agent_name に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-004 | 型境界 | agent_name 1文字 | --agent_name に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-005 | 型境界 | agent_name 特殊文字 | --agent_name に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-006 | 型境界 | agent_name 長文 | --agent_name に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-007 | 選択値境界 | agent_type 先頭選択肢 | --agent_type に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-008 | 選択値境界 | agent_type 末尾選択肢 | --agent_type に選択肢の末尾値 remote を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-009 | 選択値境界 | agent_type 不正選択肢 | --agent_type に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-010 | 型境界 | agent_type 空文字 | --agent_type に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-011 | 型境界 | agent_type 1文字 | --agent_type に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-012 | 型境界 | agent_type 特殊文字 | --agent_type に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-013 | 型境界 | agent_type 長文 | --agent_type に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-014 | 型境界 | use_planner=False | --use_planner に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-015 | 型境界 | use_planner=True | --use_planner に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-016 | 型境界 | a2asv_baseurl 空文字 | --a2asv_baseurl に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-017 | 型境界 | a2asv_baseurl 1文字 | --a2asv_baseurl に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-018 | 型境界 | a2asv_baseurl 特殊文字 | --a2asv_baseurl に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-019 | 型境界 | a2asv_baseurl 長文 | --a2asv_baseurl に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-020 | 型境界 | a2asv_delegated_auth=False | --a2asv_delegated_auth に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-021 | 型境界 | a2asv_delegated_auth=True | --a2asv_delegated_auth に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-022 | 型境界 | a2asv_apikey 空文字 | --a2asv_apikey に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-023 | 型境界 | a2asv_apikey 1文字 | --a2asv_apikey に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-024 | 型境界 | a2asv_apikey 特殊文字 | --a2asv_apikey に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-025 | 型境界 | a2asv_apikey 長文 | --a2asv_apikey に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-026 | 必須チェック | llm 未指定 | --llm を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --llm の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-027 | 型境界 | llm 空文字 | --llm に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-028 | 型境界 | llm 1文字 | --llm に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-029 | 型境界 | llm 特殊文字 | --llm に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-030 | 型境界 | llm 長文 | --llm に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-031 | 複数値境界 | mcpservers 0件 | --mcpservers に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-032 | 複数値境界 | mcpservers 1件 | --mcpservers に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-033 | 複数値境界 | mcpservers 複数件 | --mcpservers に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-034 | 型境界 | mcpservers 空文字 | --mcpservers に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-035 | 型境界 | mcpservers 1文字 | --mcpservers に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-036 | 型境界 | mcpservers 特殊文字 | --mcpservers に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-037 | 型境界 | mcpservers 長文 | --mcpservers に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-038 | 複数値境界 | subagents 0件 | --subagents に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-039 | 複数値境界 | subagents 1件 | --subagents に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-040 | 複数値境界 | subagents 複数件 | --subagents に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-041 | 型境界 | subagents 空文字 | --subagents に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-042 | 型境界 | subagents 1文字 | --subagents に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-043 | 型境界 | subagents 特殊文字 | --subagents に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-044 | 型境界 | subagents 長文 | --subagents に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-045 | 型境界 | agent_description 空文字 | --agent_description に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-046 | 型境界 | agent_description 1文字 | --agent_description に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-047 | 型境界 | agent_description 特殊文字 | --agent_description に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-048 | 型境界 | agent_description 長文 | --agent_description に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-049 | 型境界 | agent_instruction 空文字 | --agent_instruction に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-050 | 型境界 | agent_instruction 1文字 | --agent_instruction に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-051 | 型境界 | agent_instruction 特殊文字 | --agent_instruction に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-052 | 型境界 | agent_instruction 長文 | --agent_instruction に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-053 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-054 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 必要なディレクトリが生成され、再実行時も競合しないことを確認する |
| TC-055 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn, success が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_agent_save.py
- 詳細設計書: Specifications/cli/agent/agent_save.md
- 生成日時: 2026-04-23T23:40:13