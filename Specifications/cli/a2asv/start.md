# a2asv start

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | a2asv |
| cmd | start |
| クラス | A2aSvStart |
| モジュール | cmdbox.app.features.cli.cmdbox_a2asv_start |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_a2asv_start.py |
| 継承元 | UnsupportEdgeFeature, Validator, Feature |
| Redis | 必須 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: A2A サーバーを起動します。
- 英語: Start A2A server.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --data | ディレクトリ | いいえ | いいえ | いいえ | /home/ubuntu/.cmdbox | - | 省略した時は `$HONE/.cmdbox` を使用します。 |
| --allow_host | 文字列 | いいえ | いいえ | いいえ | 0.0.0.0 | - | 省略した時は `0.0.0.0` を使用します。 |
| --a2asv_listen_port | 整数 | いいえ | いいえ | いいえ | 8071 | - | 省略した時は `8071` を使用します。 |
| --ssl_a2asv_listen_port | 整数 | いいえ | いいえ | いいえ | 8433 | - | 省略した時は `8433` を使用します。 |
| --ssl_cert | ファイル | いいえ | いいえ | はい | None | - | SSLサーバー証明書ファイルを指定します。 |
| --ssl_key | ファイル | いいえ | いいえ | はい | None | - | SSLサーバー秘密鍵ファイルを指定します。 |
| --ssl_keypass | 文字列 | いいえ | いいえ | はい | None | - | SSLサーバー秘密鍵ファイルの複合化パスワードを指定します。 |
| --ssl_ca_certs | ファイル | いいえ | いいえ | はい | None | - | SSLサーバーCA証明書ファイルを指定します。 |
| --signin_file | ファイル | はい | いいえ | いいえ | .cmdbox/user_list.yml | - | サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.cmdbox/user_list.yml' を指定します。 |
| --gunicorn_workers | 整数 | いいえ | いいえ | はい | 6 | - | gunicornワーカー数を指定します。Linux環境でのみ有効です。-1又は未指定の場合はCPU数を使用します。 |
| --gunicorn_timeout | 整数 | いいえ | いいえ | はい | 900 | - | gunicornワーカーのタイムアウトの時間を秒で指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: A2aSvStart
- 役割: この機能の実行を行います
- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1
- 結果キー候補: success, warn
- 処理フロー:
  - (st, msg, obj) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 例外処理を伴って処理する。主な呼出: web.Web.getInstance, signin.Signin, a2a_mod.A2a, dict, common.print_format, Path
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1
- 結果キー候補: success, warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 選択肢を持つパラメータ output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー success, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_a2asv_start.py
- apprun 実装元: A2aSvStart
- svrun 実装元: Feature
- 生成日時: 2026-04-26T00:53:03
