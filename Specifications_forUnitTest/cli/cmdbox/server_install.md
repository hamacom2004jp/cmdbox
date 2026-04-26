# cmdbox server_install

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | cmdbox |
| cmd | server_install |
| クラス | CmdboxServerInstall |
| モジュール | cmdbox.app.features.cli.cmdbox_cmdbox_server_install |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_server_install.py |
| 詳細設計書 | Specifications/cli/cmdbox/server_install.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: cmdboxのコンテナをインストールします。
- 英語: Install the cmdbox container.

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

- 選択肢を持つパラメータ install_no_python, install_compile_python, install_use_gpu, tts_engine, voicevox_ver, voicevox_whl, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ init_extra, run_extra_pre, run_extra_post, install_extra の 0 件・1 件・複数件入力を確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --tts_engine=。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |
| TC-002 | 型境界 | data 既存空ディレクトリ | --data に既存の空ディレクトリを指定する | RESP_SUCCESS | 空ディレクトリ前提の初期状態が正常に処理される | 必要な初期化ファイルやサブディレクトリが作成される場合は生成を確認する |
| TC-003 | 型境界 | data 既存データありディレクトリ | --data に既存データを含むディレクトリを指定する | RESP_SUCCESS | 既存データを読み込む経路が正常に処理される | 既存ファイルを意図せず破壊しないことを確認する |
| TC-004 | 型境界 | data 非存在ディレクトリ | --data に存在しないディレクトリを指定する | RESP_WARN | 存在チェックエラーまたは初期化失敗が返る | 自動作成される仕様でない限り、ディレクトリが勝手に作成されないことを確認する |
| TC-005 | 型境界 | install_cmdbox 1文字 | --install_cmdbox に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-006 | 型境界 | install_cmdbox 特殊文字 | --install_cmdbox に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-007 | 型境界 | install_cmdbox 長文 | --install_cmdbox に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-008 | 型境界 | install_from 空文字 | --install_from に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-009 | 型境界 | install_from 1文字 | --install_from に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-010 | 型境界 | install_from 特殊文字 | --install_from に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-011 | 型境界 | install_from 長文 | --install_from に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-012 | 型境界 | install_no_python=False | --install_no_python に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-013 | 型境界 | install_no_python=True | --install_no_python に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-014 | 型境界 | install_compile_python=False | --install_compile_python に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-015 | 型境界 | install_compile_python=True | --install_compile_python に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-016 | 型境界 | install_tag 空文字 | --install_tag に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-017 | 型境界 | install_tag 1文字 | --install_tag に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-018 | 型境界 | install_tag 特殊文字 | --install_tag に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-019 | 型境界 | install_tag 長文 | --install_tag に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-020 | 型境界 | install_use_gpu=False | --install_use_gpu に False を指定する | RESP_SUCCESS | False 分岐が正常に処理される | 既定値との差分がある場合は挙動の変化を確認する |
| TC-021 | 型境界 | install_use_gpu=True | --install_use_gpu に True を指定する | RESP_SUCCESS | True 分岐が正常に処理される | 副作用がある場合は有効化に伴う成果物の差分を確認する |
| TC-022 | 選択値境界 | tts_engine 先頭選択肢 | --tts_engine に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-023 | 選択値境界 | tts_engine 末尾選択肢 | --tts_engine に選択肢の末尾値 voicevox を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-024 | 選択値境界 | tts_engine 不正選択肢 | --tts_engine に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-025 | 選択値境界 | voicevox_ver 先頭選択肢 | --voicevox_ver に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-026 | 選択値境界 | voicevox_ver 末尾選択肢 | --voicevox_ver に選択肢の末尾値 0.16.3 を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-027 | 選択値境界 | voicevox_ver 不正選択肢 | --voicevox_ver に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-028 | 選択値境界 | voicevox_whl 先頭選択肢 | --voicevox_whl に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-029 | 選択値境界 | voicevox_whl 末尾選択肢 | --voicevox_whl に選択肢の末尾値 voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl を指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-030 | 選択値境界 | voicevox_whl 不正選択肢 | --voicevox_whl に選択肢外の値 INVALID_CHOICE を指定する | RESP_WARN | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-031 | 複数値境界 | init_extra 0件 | --init_extra に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-032 | 複数値境界 | init_extra 1件 | --init_extra に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-033 | 複数値境界 | init_extra 複数件 | --init_extra に 2 件以上指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-034 | 型境界 | init_extra 空文字 | --init_extra に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-035 | 型境界 | init_extra 1文字 | --init_extra に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-036 | 型境界 | init_extra 特殊文字 | --init_extra に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-037 | 型境界 | init_extra 長文 | --init_extra に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-038 | 複数値境界 | run_extra_pre 0件 | --run_extra_pre に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-039 | 複数値境界 | run_extra_pre 1件 | --run_extra_pre に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-040 | 複数値境界 | run_extra_pre 複数件 | --run_extra_pre に 2 件以上指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-041 | 型境界 | run_extra_pre 空文字 | --run_extra_pre に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-042 | 型境界 | run_extra_pre 1文字 | --run_extra_pre に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-043 | 型境界 | run_extra_pre 特殊文字 | --run_extra_pre に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-044 | 型境界 | run_extra_pre 長文 | --run_extra_pre に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-045 | 複数値境界 | run_extra_post 0件 | --run_extra_post に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-046 | 複数値境界 | run_extra_post 1件 | --run_extra_post に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-047 | 複数値境界 | run_extra_post 複数件 | --run_extra_post に 2 件以上指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-048 | 型境界 | run_extra_post 空文字 | --run_extra_post に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-049 | 型境界 | run_extra_post 1文字 | --run_extra_post に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-050 | 型境界 | run_extra_post 特殊文字 | --run_extra_post に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-051 | 型境界 | run_extra_post 長文 | --run_extra_post に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-052 | 複数値境界 | install_extra 0件 | --install_extra に空配列または未指定を与える | RESP_SUCCESS | 0 件入力時の既定動作が仕様どおりである | 一覧条件や絞り込み結果が崩れないことを確認する |
| TC-053 | 複数値境界 | install_extra 1件 | --install_extra に 1 件だけ指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 単一値で期待したフィルタリングまたは処理が行われることを確認する |
| TC-054 | 複数値境界 | install_extra 複数件 | --install_extra に 2 件以上指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 順序・重複・集約結果が仕様どおりであることを確認する |
| TC-055 | 型境界 | install_extra 空文字 | --install_extra に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-056 | 型境界 | install_extra 1文字 | --install_extra に 1 文字値 X を指定する | RESP_WARN | 正常終了し、戻り値とログが期待どおりである | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-057 | 型境界 | install_extra 特殊文字 | --install_extra に a_日本語 space-_.#"'&<> を指定する | RESP_WARN | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-058 | 型境界 | install_extra 長文 | --install_extra に 512 文字相当の文字列を指定する | RESP_WARN | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-059 | ファイルI/O | compose_path 有効入力ファイル | --compose_path に存在する妥当なファイルを指定する | RESP_SUCCESS | 正常終了し、戻り値とログが期待どおりである | 入力ファイル内容が意図どおり読み込まれることを確認する |
| TC-060 | ファイルI/O | compose_path 存在しない入力ファイル | --compose_path に存在しないパスを指定する | RESP_WARN | ファイル未存在のエラーまたは警告が返る | 後続処理に進まず、副作用が発生しないことを確認する |
| TC-061 | ファイルI/O | compose_path 空ファイル | --compose_path に 0 byte の空ファイルを指定する | RESP_WARN | フォーマット不正または入力不足として扱われる | 異常終了時のログやエラー文言が十分であることを確認する |
| TC-062 | ファイルI/O | output_json 追記保存 | 既存の output_json を用意し、output_json_append=True で 2 回連続実行する | RESP_SUCCESS | 各回の結果が保存され、追記モードで既存内容が失われない | 1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する |
| TC-063 | 副作用確認 | 成果物検証 | 副作用を発生させる有効入力で実行する | RESP_SUCCESS | 戻り値が正常であり、関連する成果物が期待どおり更新される | output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する |

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_server_install.py
- 詳細設計書: Specifications/cli/cmdbox/server_install.md
- 生成日時: 2026-04-26T00:53:18