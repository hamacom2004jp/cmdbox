# agent session_list

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | session_list |
| クラス | AgentSessionList |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_session_list |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_session_list.py |
| 詳細設計書 | Specifications/cli/agent/session_list.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: Agentのセッション一覧を取得します。
- 英語: List sessions for the agent.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。
- 出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_2
- 結果キー候補: warn, runner_name, session_id, user_name, last_update_time

## 副作用確認観点

- output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する

## 詳細設計からの観点

- 必須パラメータ runner_name, user_name が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn, runner_name, session_id, user_name, last_update_time が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --runner_name=enabled_value、--user_name=enabled_value。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, runner_name, session_id, user_name, last_update_time が含まれる | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |
| TC-002 | 必須チェック | runner_name 未指定 | --runner_name を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --runner_name の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | runner_name 空文字 | --runner_name に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-004 | 型境界 | runner_name 1文字 | --runner_name に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, runner_name, session_id, user_name, last_update_time が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-005 | 型境界 | runner_name 特殊文字 | --runner_name に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-006 | 型境界 | runner_name 長文 | --runner_name に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-007 | 必須チェック | user_name 未指定 | --user_name を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --user_name の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-008 | 型境界 | user_name 空文字 | --user_name に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-009 | 型境界 | user_name 1文字 | --user_name に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, runner_name, session_id, user_name, last_update_time が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-010 | 型境界 | user_name 特殊文字 | --user_name に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-011 | 型境界 | user_name 長文 | --user_name に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-012 | 型境界 | session_id 空文字 | --session_id に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-013 | 型境界 | session_id 1文字 | --session_id に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, runner_name, session_id, user_name, last_update_time が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-014 | 型境界 | session_id 特殊文字 | --session_id に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-015 | 型境界 | session_id 長文 | --session_id に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-016 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-017 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |
| TC-018 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn, runner_name, session_id, user_name, last_update_time が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_session_list.py
- 詳細設計書: Specifications/cli/agent/session_list.md
- 生成日時: 2026-04-19T21:16:02