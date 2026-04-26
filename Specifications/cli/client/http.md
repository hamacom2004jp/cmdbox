# client http

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | client |
| cmd | http |
| クラス | ClientHttp |
| モジュール | cmdbox.app.features.cli.cmdbox_client_http |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_client_http.py |
| 継承元 | ResultEdgeFeature, Validator, Feature |
| Redis | 任意 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: HTTPサーバーに対してリクエストを送信し、レスポンスを取得します。
- 英語: Sends a request to the HTTP server and gets a response.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --url | 文字列 | はい | いいえ | いいえ | None | - | リクエスト先URLを指定します。 |
| --proxy | 文字列 | いいえ | いいえ | いいえ | no | no, yes | webモードで呼び出された場合、受信したリクエストパラメータをリクエスト先URLに送信するかどうかを指定します。 |
| --send_method | 文字列 | はい | いいえ | いいえ | GET | GET, POST, PUT, DELETE, PATCH, HEAD, OPTIONS | リクエストメソッドを指定します。 |
| --send_content_type | 文字列 | いいえ | いいえ | いいえ | None | , application/octet-stream, application/json, multipart/form-data | 送信するデータのContent-Typeを指定します。 |
| --send_apikey | パスワード | いいえ | いいえ | いいえ | None | - | リクエスト先の認証で使用するAPIキーを指定します。 |
| --send_header | 辞書 | いいえ | はい | いいえ | None | - | リクエストヘッダーを指定します。 |
| --send_param | 辞書 | いいえ | はい | いいえ | None | - | 送信するパラメータを指定します。 |
| --send_data | 複数行文字列 | いいえ | いいえ | いいえ | None | - | 送信するデータを指定します。 |
| --send_verify | 真偽値 | いいえ | いいえ | はい | false | False, True | レスポンスを受け取るまでのタイムアウトを指定します。 |
| --send_timeout | 整数 | いいえ | いいえ | はい | 30 | - | レスポンスを受け取るまでのタイムアウトを指定します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: ClientHttp
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: error, warn
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 条件 args.proxy == 'yes' を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - url に urllib.parse.urlparse の結果を格納する
  - query に urllib.parse.parse_qs の結果を格納する
  - args.url に urllib.parse.urlunparse の結果を格納する
  - res に requests.request の結果を格納する
  - 条件 res.status_code != 200 を満たす場合は早期終了し、RESP_WARN。結果キー: error
  - content_type に res.headers.get の結果を格納する
  - 条件 content_type.startswith('application/json') を満たす場合は早期終了し、RESP_SUCCESS
  - common.print_format を呼び出す
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: error, warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 必須パラメータ url が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ proxy, send_method, send_content_type, send_verify, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ send_header, send_param の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー error, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_client_http.py
- apprun 実装元: ClientHttp
- svrun 実装元: Feature
- 生成日時: 2026-04-26T00:53:06
