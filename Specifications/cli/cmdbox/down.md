# cmdbox down

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | cmdbox |
| cmd | down |
| クラス | CmdboxDown |
| モジュール | cmdbox.app.features.cli.cmdbox_cmdbox_down |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_down.py |
| 継承元 | CmdboxBase, OneshotEdgeFeature, Feature |
| Redis | 不要 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: コンテナを停止します。
- 英語: Stops the container.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| -C, --container | 文字列 | いいえ | いいえ | いいえ | None | - | コンテナ名を指定します。 |

## 処理内容

### apprun

- 実装元: CmdboxDown
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 処理フロー:
  - ret に self.down の結果を格納する
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
- 結果キー候補: 抽出なし
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_down.py
- apprun 実装元: CmdboxDown
- svrun 実装元: Feature
- 生成日時: 2026-04-19T20:59:07
