# client server_info

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | client |
| cmd | server_info |
| クラス | ClientServerInfo |
| モジュール | cmdbox.app.features.cli.cmdbox_client_server_info |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_client_server_info.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: サーバーの情報を取得します。
- 英語: Retrieve server information.

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

- 実装元: ClientServerInfo
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - 条件 args.svname is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - cl に client.Client の結果を格納する
  - ret に cl.server_info の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: ClientServerInfo
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: INT_1
- 処理フロー:
  - st に self.server_info の結果を格納する
  - st を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### get_svcmd

- 実装元: ClientServerInfo
- 役割: この機能のサーバー側のコマンドを返します  Returns: str: サーバー側のコマンド
- 処理概要:
  - 'server_info' を返却する

### server_info

- 実装元: ClientServerInfo
- 役割: サーバー情報を取得する  Args: reskey (str): レスポンスキー data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: レスポンスコード
- 処理概要:
  - 例外処理を伴って処理する。主な呼出: dict, redis_cli.rpush, logger.warning
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN）

## 単体テスト観点

- 選択肢を持つパラメータ output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_client_server_info.py
- apprun 実装元: ClientServerInfo
- svrun 実装元: ClientServerInfo
- 生成日時: 2026-04-19T20:59:07
