# agent mcp_proxy

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | mcp_proxy |
| クラス | AgentMcpProxy |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_mcp_proxy |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_mcp_proxy.py |
| 詳細設計書 | Specifications/cli/agent/mcp_proxy.md |
| 実装上の必須推定 | - |

## 概要

- 日本語: 標準入力を受け付け、リモートMCPサーバーにリクエストを行うProxyサーバーを起動します。
- 英語: Starts a Proxy server that accepts standard input and makes requests to a remote MCP server.

## 境界値ポリシー

- 数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。
- 文字列型は空文字、1文字、特殊文字列、512文字相当の長文を境界として扱う。
- ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。
- 複数値パラメータは 0 件、1 件、複数件を境界として扱う。
- 選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。

## 共通期待結果

- 終了コード候補: RESP_SUCCESS, RESP_ERROR
- 結果キー候補: info, warn

## 副作用確認観点

- 戻り値とログのみを確認対象とする

## 詳細設計からの観点

- 選択肢を持つパラメータ mcpserver_transport の境界値と不正値を確認する
- 結果オブジェクトのキー info, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_ERROR の到達条件をそれぞれ検証する

## テストパターン

| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
| --- | --- | --- | --- | --- | --- | --- |
| TC-001 | 正常系 | 最小有効入力 | --mcpserver_name=mcpserver、--mcpserver_url=http://localhost:8091/mcp、--mcpserver_transport=。任意パラメータは省略する | RESP_SUCCESS | 正常終了し、結果オブジェクトに info, warn が含まれる | 戻り値以外の副作用がないことを確認する |
| TC-002 | 型境界 | mcpserver_name 空文字 | --mcpserver_name に空文字を指定する | RESP_ERROR | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-003 | 型境界 | mcpserver_name 1文字 | --mcpserver_name に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに info, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-004 | 型境界 | mcpserver_name 特殊文字 | --mcpserver_name に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-005 | 型境界 | mcpserver_name 長文 | --mcpserver_name に 512 文字相当の文字列を指定する | RESP_ERROR | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-006 | 型境界 | mcpserver_url 空文字 | --mcpserver_url に空文字を指定する | RESP_ERROR | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-007 | 型境界 | mcpserver_url 1文字 | --mcpserver_url に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに info, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-008 | 型境界 | mcpserver_url 特殊文字 | --mcpserver_url に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-009 | 型境界 | mcpserver_url 長文 | --mcpserver_url に 512 文字相当の文字列を指定する | RESP_ERROR | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-010 | 型境界 | mcpserver_apikey 空文字 | --mcpserver_apikey に空文字を指定する | RESP_SUCCESS | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-011 | 型境界 | mcpserver_apikey 1文字 | --mcpserver_apikey に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに info, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-012 | 型境界 | mcpserver_apikey 特殊文字 | --mcpserver_apikey に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-013 | 型境界 | mcpserver_apikey 長文 | --mcpserver_apikey に 512 文字相当の文字列を指定する | RESP_ERROR | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-014 | 選択値境界 | mcpserver_transport 先頭選択肢 | --mcpserver_transport に選択肢の先頭値  を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに info, warn が含まれる | 先頭選択肢でも分岐が正しく処理されることを確認する |
| TC-015 | 選択値境界 | mcpserver_transport 末尾選択肢 | --mcpserver_transport に選択肢の末尾値 http を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに info, warn が含まれる | 末尾選択肢でも分岐が正しく処理されることを確認する |
| TC-016 | 選択値境界 | mcpserver_transport 不正選択肢 | --mcpserver_transport に選択肢外の値 INVALID_CHOICE を指定する | RESP_ERROR | パラメータ検証エラーまたは実行時警告になる | 不正値で副作用が発生しないことを確認する |
| TC-017 | 型境界 | mcpserver_transport 空文字 | --mcpserver_transport に空文字を指定する | RESP_ERROR | 空文字の扱いが省略と区別され、検証結果が仕様どおりになる | エラー時は副作用が発生しないことを確認する |
| TC-018 | 型境界 | mcpserver_transport 1文字 | --mcpserver_transport に 1 文字値 X を指定する | RESP_SUCCESS | 正常終了し、結果オブジェクトに info, warn が含まれる | 最短相当の入力でも分岐や検索条件が崩れないことを確認する |
| TC-019 | 型境界 | mcpserver_transport 特殊文字 | --mcpserver_transport に a_日本語 space-_.# を指定する | RESP_SUCCESS | 日本語・空白・記号を含む入力が正しく受理される | 文字化けやエスケープ漏れがないことを確認する |
| TC-020 | 型境界 | mcpserver_transport 長文 | --mcpserver_transport に 512 文字相当の文字列を指定する | RESP_ERROR | 512 文字を超える入力は検証エラーまたは警告になる | エラー時は副作用が発生しないことを確認する |
| TC-021 | 結果検証 | 結果キー整合性 | 正常系の代表入力で実行する | RESP_SUCCESS | 結果オブジェクトに info, warn が含まれる | 不要なキー欠落や型崩れがないことを確認する |

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_mcp_proxy.py
- 詳細設計書: Specifications/cli/agent/mcp_proxy.md
- 生成日時: 2026-04-23T23:40:13