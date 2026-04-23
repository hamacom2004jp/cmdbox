# edge start

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | edge |
| cmd | start |
| クラス | EdgeStart |
| モジュール | cmdbox.app.features.cli.cmdbox_edge_start |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_edge_start.py |
| 継承元 | UnsupportEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: 端末モードを起動します。
- 英語: Start Edge mode.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --data | ディレクトリ | はい | いいえ | はい | C:\Users\hama\.cmdbox | - | 省略した時は f`$HONE/.cmdbox` を使用します。 |

## 処理内容

### apprun

- 実装元: EdgeStart
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS
- 結果キー候補: success
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - app に edge.Edge の結果を格納する
  - msg に app.start の結果を格納する
  - msg に dict の結果を格納する
  - common.print_format を呼び出す
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS
- 結果キー候補: success
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### load_cmds

- 実装元: EdgeStart
- 役割: コマンドファイルのタイトル一覧を取得する  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数  Returns: status_code (int): ステータスコード List[Dict[str, Any]]: コマンドファイルのタイトル一覧
- 処理概要:
  - res に self.session.post の結果を格納する
  - 条件 res.status_code != 200 を満たす場合は早期終了し、戻り値あり。結果キー: warn
  - cmds に res.json の結果を格納する
  - 終了コード RESP_SUCCESS を返却する

### load_pipes

- 実装元: EdgeStart
- 役割: パイプファイルのタイトル一覧を取得する  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数  Returns: status_code (int): ステータスコード List[Dict[str, Any]]: コマンドファイルのタイトル一覧
- 処理概要:
  - res に self.session.post の結果を格納する
  - 条件 res.status_code != 200 を満たす場合は早期終了し、戻り値あり。結果キー: warn
  - pipes に res.json の結果を格納する
  - 終了コード RESP_SUCCESS を返却する

## 単体テスト観点

- 結果オブジェクトのキー success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_edge_start.py
- apprun 実装元: EdgeStart
- svrun 実装元: Feature
- 生成日時: 2026-04-23T23:40:00
