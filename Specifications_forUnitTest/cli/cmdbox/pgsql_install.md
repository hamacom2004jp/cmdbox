# cmdbox pgsql_install

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | cmdbox |
| cmd | pgsql_install |
| クラス | CmdboxPgSQLInstall |
| モジュール | cmdbox.app.features.cli.cmdbox_cmdbox_pgsql_install |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_pgsql_install.py |
| 詳細設計書 | Specifications/cli/cmdbox/pgsql_install.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: PostgreSQLサーバーをインストールします。
- 英語: Installs the PostgreSQL server.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。
- 出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: 特になし

## 副作用確認観点

- output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する

## 詳細設計からの観点

- 選択肢を持つパラメータ output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --install_pgsqlver=18。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |
| TC-002 | 型境界 | install_pgsqlver 1文字 | --install_pgsqlver に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-003 | 型境界 | install_pgsqlver 特殊文字 | --install_pgsqlver に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-004 | 型境界 | install_pgsqlver 長文 | --install_pgsqlver に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-005 | 型境界 | install_from 1文字 | --install_from に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-006 | 型境界 | install_from 特殊文字 | --install_from に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-007 | 型境界 | install_from 長文 | --install_from に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-008 | 型境界 | install_tag 空文字 | --install_tag に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-009 | 型境界 | install_tag 1文字 | --install_tag に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-010 | 型境界 | install_tag 特殊文字 | --install_tag に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-011 | 型境界 | install_tag 長文 | --install_tag に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-012 | 型境界 | no_install_pgvector=False | --no_install_pgvector に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-013 | 型境界 | no_install_pgvector=True | --no_install_pgvector に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-014 | 型境界 | install_pgvector_tag 1文字 | --install_pgvector_tag に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-015 | 型境界 | install_pgvector_tag 特殊文字 | --install_pgvector_tag に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-016 | 型境界 | install_pgvector_tag 長文 | --install_pgvector_tag に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-017 | 型境界 | no_install_age=False | --no_install_age に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-018 | 型境界 | no_install_age=True | --no_install_age に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-019 | 型境界 | install_age_tag 1文字 | --install_age_tag に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-020 | 型境界 | install_age_tag 特殊文字 | --install_age_tag に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-021 | 型境界 | install_age_tag 長文 | --install_age_tag に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-022 | 型境界 | no_install_pgcron=False | --no_install_pgcron に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-023 | 型境界 | no_install_pgcron=True | --no_install_pgcron に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-024 | 型境界 | install_pgcron_tag 1文字 | --install_pgcron_tag に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-025 | 型境界 | install_pgcron_tag 特殊文字 | --install_pgcron_tag に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-026 | 型境界 | install_pgcron_tag 長文 | --install_pgcron_tag に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-027 | ファイルI/O | compose_path 有効入力ファイル | --compose_path に存在する妥当なファイルを指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 入力ファイル内容が意図どおり読み込まれることを確認する |
| TC-028 | ファイルI/O | compose_path 存在しない入力ファイル | --compose_path に存在しないパスを指定する | RESP_WARN | ファイル未存在のエラーまたは警告が返る | 後続処理に進まず、副作用が発生しないことを確認する |
| TC-029 | ファイルI/O | compose_path 空ファイル | --compose_path に 0 byte の空ファイルを指定する | RESP_WARN | フォーマット不正または入力不足として扱われる | 異常終了時のログやエラー文言が十分であることを確認する |
| TC-030 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-031 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_pgsql_install.py
- 詳細設計書: Specifications/cli/cmdbox/pgsql_install.md
- 生成日時: 2026-04-26T00:53:18