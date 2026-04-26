# rag save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | rag |
| cmd | save |
| クラス | RagSave |
| モジュール | cmdbox.app.features.cli.cmdbox_rag_save |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_rag_save.py |
| 詳細設計書 | Specifications/cli/rag/save.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: RAG（検索拡張生成）の設定を保存します。
- 英語: Saves the settings for RAG (Retrieval-Augmented Generation).

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

- 必須パラメータ rag_name, extract が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ rag_type, savetype, output_json_append, stdout_log の境界値と不正値を確認する
- 複数値パラメータ extract の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --rag_name=enabled_value、--rag_type=、--extract=enabled_value。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 必要なディレクトリが生成され、再実行時も競合しないことを確認する |
| TC-002 | 必須チェック | rag_name 未指定 | --rag_name を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --rag_name の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-003 | 型境界 | rag_name 空文字 | --rag_name に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-004 | 型境界 | rag_name 1文字 | --rag_name に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-005 | 型境界 | rag_name 特殊文字 | --rag_name に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-006 | 型境界 | rag_name 長文 | --rag_name に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-007 | 選択値境界 | rag_type 先頭選択肢 | --rag_type に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-008 | 選択値境界 | rag_type 末尾選択肢 | --rag_type に選択肢の末尾値 graph_pg を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-009 | 選択値境界 | rag_type 不正選択肢 | --rag_type に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-010 | 必須チェック | extract 未指定 | --extract を省略し、他の必須パラメータは有効値を指定する | RESP_WARN | --extract の不足を示すエラーまたは警告が返る | 処理を継続せず、副作用が発生しないことを確認する |
| TC-011 | 複数値境界 | extract 0件 | --extract に空配列または未指定を与える | RESP_WARN | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-012 | 複数値境界 | extract 1件 | --extract に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-013 | 複数値境界 | extract 複数件 | --extract に 2 件以上指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-014 | 型境界 | extract 空文字 | --extract に空文字を指定する | RESP_WARN | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-015 | 型境界 | extract 1文字 | --extract に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-016 | 型境界 | extract 特殊文字 | --extract に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-017 | 型境界 | extract 長文 | --extract に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-018 | 型境界 | embed 空文字 | --embed に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-019 | 型境界 | embed 1文字 | --embed に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-020 | 型境界 | embed 特殊文字 | --embed に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-021 | 型境界 | embed 長文 | --embed に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-022 | 型境界 | embed_vector_dim=0 | --embed_vector_dim に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-023 | 型境界 | embed_vector_dim=1 | --embed_vector_dim に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-024 | 型境界 | embed_vector_dim=-1 | --embed_vector_dim に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-025 | 型境界 | embed_vector_dim=2147483647 | --embed_vector_dim に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-026 | 選択値境界 | savetype 先頭選択肢 | --savetype に選択肢の先頭値 per_doc を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-027 | 選択値境界 | savetype 末尾選択肢 | --savetype に選択肢の末尾値 add_only を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-028 | 選択値境界 | savetype 不正選択肢 | --savetype に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-029 | 型境界 | vector_store_pghost 1文字 | --vector_store_pghost に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-030 | 型境界 | vector_store_pghost 特殊文字 | --vector_store_pghost に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-031 | 型境界 | vector_store_pghost 長文 | --vector_store_pghost に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-032 | 型境界 | vector_store_pgport=0 | --vector_store_pgport に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-033 | 型境界 | vector_store_pgport=1 | --vector_store_pgport に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-034 | 型境界 | vector_store_pgport=-1 | --vector_store_pgport に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-035 | 型境界 | vector_store_pgport=2147483647 | --vector_store_pgport に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-036 | 型境界 | vector_store_pguser 1文字 | --vector_store_pguser に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-037 | 型境界 | vector_store_pguser 特殊文字 | --vector_store_pguser に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-038 | 型境界 | vector_store_pguser 長文 | --vector_store_pguser に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-039 | 型境界 | vector_store_pgpass 1文字 | --vector_store_pgpass に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-040 | 型境界 | vector_store_pgpass 特殊文字 | --vector_store_pgpass に a_日本語 space-_.#"'&<> を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-041 | 型境界 | vector_store_pgdbname 1文字 | --vector_store_pgdbname に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-042 | 型境界 | vector_store_pgdbname 特殊文字 | --vector_store_pgdbname に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-043 | 型境界 | vector_store_pgdbname 長文 | --vector_store_pgdbname に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-044 | 型境界 | graph_store_pghost 1文字 | --graph_store_pghost に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-045 | 型境界 | graph_store_pghost 特殊文字 | --graph_store_pghost に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-046 | 型境界 | graph_store_pghost 長文 | --graph_store_pghost に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-047 | 型境界 | graph_store_pgport=0 | --graph_store_pgport に 0 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-048 | 型境界 | graph_store_pgport=1 | --graph_store_pgport に 1 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-049 | 型境界 | graph_store_pgport=-1 | --graph_store_pgport に -1 を指定する | RESP_WARN | 負値を許容しない場合はエラーまたは警告になる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-050 | 型境界 | graph_store_pgport=2147483647 | --graph_store_pgport に 2147483647 を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 数値が内部で丸められず、そのまま評価されることを確認する |
| TC-051 | 型境界 | graph_store_pguser 1文字 | --graph_store_pguser に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-052 | 型境界 | graph_store_pguser 特殊文字 | --graph_store_pguser に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-053 | 型境界 | graph_store_pguser 長文 | --graph_store_pguser に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-054 | 型境界 | graph_store_pgpass 1文字 | --graph_store_pgpass に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-055 | 型境界 | graph_store_pgpass 特殊文字 | --graph_store_pgpass に a_日本語 space-_.#"'&<> を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-056 | 型境界 | graph_store_pgdbname 1文字 | --graph_store_pgdbname に 1 文字値 X を指定する | RESP_WARN | 正常終了し、結果オブジェクトに warn, success が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-057 | 型境界 | graph_store_pgdbname 特殊文字 | --graph_store_pgdbname に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-058 | 型境界 | graph_store_pgdbname 長文 | --graph_store_pgdbname に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-059 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-060 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する / 必要なディレクトリが生成され、再実行時も競合しないことを確認する |
| TC-061 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに warn, success が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_rag_save.py
- 詳細設計書: Specifications/cli/rag/save.md
- 生成日時: 2026-04-26T00:53:18