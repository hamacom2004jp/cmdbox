# server stop

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | server |
| cmd | stop |
| クラス | ServerStop |
| モジュール | cmdbox.app.features.cli.cmdbox_server_stop |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_server_stop.py |
| 継承元 | UnsupportEdgeFeature, Validator, Feature |
| Redis | 必須 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | True |

## 概要

- 日本語: サーバーを停止します。installモードで `cmdbox -m install -c server` を実行している場合は、 `docker-compose down` を使用してください。
- 英語: Stop the inference server. If you are running `cmdbox -m install -c server` in install mode, use `docker-compose down`.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 15 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: ServerStop
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - cl に client.Client の結果を格納する
  - ret に cl.stop_server の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: ServerStop
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: RESP_SUCCESS, INT_1
- 処理フロー:
  - redis_cli.rpush を呼び出す
  - 終了コード RESP_SUCCESS を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1
- 結果キー候補: 抽出なし
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### get_svcmd

- 実装元: ServerStop
- 役割: この機能のサーバー側のコマンドを返します  Returns: str: サーバー側のコマンド
- 処理概要:
  - 'stop_server' を返却する

## 単体テスト観点

- 選択肢を持つパラメータ output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_server_stop.py
- apprun 実装元: ServerStop
- svrun 実装元: ServerStop
- 生成日時: 2026-04-23T23:40:03
