# cmdbox redis_load

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | cmdbox |
| cmd | redis_load |
| クラス | CmdboxRedisLoad |
| モジュール | cmdbox.app.features.cli.cmdbox_cmdbox_redis_load |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_redis_load.py |
| 継承元 | CmdboxBase, OneshotEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: cmdboxのRedisをロードします。
- 英語: Loads the cmdbox Redis.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --image_file | ファイル | いいえ | いいえ | いいえ | None | - | 読込元イメージファイルを指定します。 |
| --install_tag | 文字列 | いいえ | いいえ | いいえ | None | - | 指定すると作成するdockerイメージのタグ名に追記出来ます。 |
| --compose_path | ファイル | いいえ | いいえ | はい | None | - | `docker-compose.yml` ファイルを指定します。 |

## 処理内容

### apprun

- 実装元: CmdboxRedisLoad
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - common.set_debug を呼び出す
  - 例外処理を伴って処理する。主な呼出: self.valid, self.get_imgname, start_sh_hst.parent.mkdir, shutil.copytree, self.make_compose_redis, self.load

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_redis_load.py
- apprun 実装元: CmdboxRedisLoad
- svrun 実装元: Feature
- 生成日時: 2026-04-23T23:40:00
