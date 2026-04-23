# server start

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | server |
| cmd | start |
| クラス | ServerStart |
| モジュール | cmdbox.app.features.cli.cmdbox_server_start |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_server_start.py |
| 継承元 | UnsupportEdgeFeature, Validator, Feature |
| Redis | 必須 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: サーバーを起動します。installモードで `cmdbox -m install -c server` を実行している場合は、 `docker-compose up -d` を使用してください。
- 英語: Start the inference server. If you are running `cmdbox -m install -c server` in install mode, use `docker-compose up -d`.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --data | ディレクトリ | いいえ | いいえ | いいえ | C:\Users\hama\.cmdbox | - | 省略した時は `$HONE/.cmdbox` を使用します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 20 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: ServerStart
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS
- 結果キー候補: success
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - sv に server.Server の結果を格納する
  - sv.start_server を呼び出す
  - 終了コード RESP_SUCCESS / 結果キー success を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS
- 結果キー候補: success
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 選択肢を持つパラメータ output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_server_start.py
- apprun 実装元: ServerStart
- svrun 実装元: Feature
- 生成日時: 2026-04-23T23:40:03
