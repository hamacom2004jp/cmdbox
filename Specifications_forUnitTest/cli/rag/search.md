# rag search

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | rag |
| cmd | search |
| クラス | RagSearch |
| モジュール | cmdbox.app.features.cli.cmdbox_rag_search |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_rag_search.py |
| 詳細設計書 | Specifications/cli/rag/search.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: RAG（検索拡張生成）の検索処理を実行します。
- 英語: Execute the RAG (Retrieval-Augmented Generation) search process.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。
- 出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_0
- 結果キー候補: warn, success, res

## 副作用確認観点

- output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する

## 詳細設計からの観点

- 必須パラメータ rag_name, groups が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ sort_dict, output_json_append, stdout_log の境界値と不正値を確認する
- 複数値パラメータ select, filter_dict, sort_dict, groups の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn, success, res が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_0 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --rag_name=enabled_value、--kcount=5、--data=/home/ubuntu/.cmdbox、--signin_file=.cmdbox/user_list.yml、--groups=enabled_value。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |
| TC-002 | 必須チェック | rag_name 未指定 | --rag_name を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --rag_name の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | rag_name 空文字 | --rag_name に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-004 | 型境界 | rag_name 1文字 | --rag_name に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-005 | 型境界 | rag_name 特殊文字 | --rag_name に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-006 | 型境界 | rag_name 長文 | --rag_name に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-007 | 型境界 | query 空文字 | --query に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-008 | 型境界 | query 1文字 | --query に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-009 | 型境界 | query 特殊文字 | --query に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-010 | 型境界 | query 長文 | --query に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-011 | 型境界 | kcount=0 | --kcount に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-012 | 型境界 | kcount=1 | --kcount に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-013 | 型境界 | kcount=-1 | --kcount に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-014 | 型境界 | kcount=2147483647 | --kcount に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-015 | 複数値境界 | select 0件 | --select に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-016 | 複数値境界 | select 1件 | --select に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-017 | 複数値境界 | select 複数件 | --select に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-018 | 型境界 | select 空文字 | --select に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-019 | 型境界 | select 1文字 | --select に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-020 | 型境界 | select 特殊文字 | --select に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-021 | 型境界 | select 長文 | --select に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-022 | 型境界 | filter_origin_name 空文字 | --filter_origin_name に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-023 | 型境界 | filter_origin_name 1文字 | --filter_origin_name に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-024 | 型境界 | filter_origin_name 特殊文字 | --filter_origin_name に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-025 | 型境界 | filter_origin_name 長文 | --filter_origin_name に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-026 | 複数値境界 | filter_dict 0件 | --filter_dict に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-027 | 複数値境界 | filter_dict 1件 | --filter_dict に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-028 | 複数値境界 | filter_dict 複数件 | --filter_dict に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-029 | 選択値境界 | sort_dict 先頭選択肢 | --sort_dict に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-030 | 選択値境界 | sort_dict 末尾選択肢 | --sort_dict に選択肢の末尾値 DESC を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-031 | 選択値境界 | sort_dict 不正選択肢 | --sort_dict に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-032 | 複数値境界 | sort_dict 0件 | --sort_dict に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-033 | 複数値境界 | sort_dict 1件 | --sort_dict に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-034 | 複数値境界 | sort_dict 複数件 | --sort_dict に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-035 | 型境界 | data 既存空ディレクトリ | --data に既存の空ディレクトリを指定する | RESP_SUCCESS | 空ディレクトリ前提の初期状態が正常に処理される | 必要な初期化ファイルやサブディレクトリが作成される場合は生成を確認する |
| TC-036 | 型境界 | data 既存データありディレクトリ | --data に既存データを含むディレクトリを指定する | RESP_SUCCESS | 既存データを読み込む経路が正常に処理される | 既存ファイルを意図せず破壊しないことを確認する |
| TC-037 | 型境界 | data 非存在ディレクトリ | --data に存在しないディレクトリを指定する | RESP_WARN | 存在チェックエラーまたは初期化失敗が返る | 自動作成される仕様でない限り、ディレクトリが勝手に作成されないことを確認する |
| TC-038 | ファイルI/O | signin_file 有効入力ファイル | --signin_file に存在する妥当なファイルを指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 入力ファイル内容が意図どおり読み込まれることを確認する |
| TC-039 | ファイルI/O | signin_file 存在しない入力ファイル | --signin_file に存在しないパスを指定する | RESP_WARN | ファイル未存在のエラーまたは警告が返る | 後続処理に進まず、副作用が発生しないことを確認する |
| TC-040 | ファイルI/O | signin_file 空ファイル | --signin_file に 0 byte の空ファイルを指定する | RESP_WARN | フォーマット不正または入力不足として扱われる | 異常終了時のログやエラー文言が十分であることを確認する |
| TC-041 | 必須チェック | groups 未指定 | --groups を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --groups の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-042 | 複数値境界 | groups 0件 | --groups に空配列または未指定を与える | RESP_WARN | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-043 | 複数値境界 | groups 1件 | --groups に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-044 | 複数値境界 | groups 複数件 | --groups に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-045 | 型境界 | groups 空文字 | --groups に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-046 | 型境界 | groups 1文字 | --groups に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success, res が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-047 | 型境界 | groups 特殊文字 | --groups に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-048 | 型境界 | groups 長文 | --groups に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-049 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-050 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |
| TC-051 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn, success, res が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_rag_search.py
- 詳細設計書: Specifications/cli/rag/search.md
- 生成日時: 2026-04-26T00:53:18