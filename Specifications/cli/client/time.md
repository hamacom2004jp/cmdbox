# client time

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | client |
| cmd | time |
| クラス | ClientTime |
| モジュール | cmdbox.app.features.cli.cmdbox_client_time |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_client_time.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: クライアント側の現在時刻を表示します。
- 英語: Displays the current time at the client side.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --timedelta | 整数 | いいえ | いいえ | いいえ | 9 | - | 時差の時間数を指定します。 |

## 処理内容

### apprun

- 実装元: ClientTime
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - tz に datetime.timezone の結果を格納する
  - dt に datetime.datetime.now の結果を格納する
  - ret に dict の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### edgerun

- 実装元: ClientTime
- 役割: この機能のエッジ側の実行を行います  Args: opt (Dict[str, Any]): オプション tool (edge.Tool): 通知関数などedge側のUI操作を行うためのクラス logger (logging.Logger): ロガー timeout (int): タイムアウト時間 prevres (Any): 前コマンドの結果。pipeline実行の実行結果を参照する時に使用します。  Yields: Tuple[int, Dict[str, Any]]: 終了コード, 結果
- 処理概要:
  - (status, res) に tool.exec_cmd の結果を格納する
  - tool.notify を呼び出す

## 単体テスト観点

- 結果オブジェクトのキー success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_client_time.py
- apprun 実装元: ClientTime
- svrun 実装元: Feature
- 生成日時: 2026-04-26T00:53:06
