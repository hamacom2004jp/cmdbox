# cmdbox load

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | cmdbox |
| cmd | load |
| クラス | CmdboxLoad |
| モジュール | cmdbox.app.features.cli.cmdbox_cmdbox_load |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_load.py |
| 継承元 | CmdboxBase, OneshotEdgeFeature, Feature |
| Redis | 不要 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: コンテナイメージを読み込みます。
- 英語: Loads the container image.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --image_file | ファイル | いいえ | いいえ | いいえ | None | - | 読込元イメージファイルを指定します。 |
| -C, --container | 文字列 | いいえ | いいえ | いいえ | None | - | コンテナ名を指定します。 |
| --install_tag | 文字列 | いいえ | いいえ | いいえ | None | - | 指定すると作成するdockerイメージのタグ名に追記出来ます。 |
| --compose_path | ファイル | いいえ | いいえ | はい | None | - | `docker-compose.yml` ファイルを指定します。 |

## 処理内容

### apprun

- 実装元: CmdboxLoad
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - common.set_debug を呼び出す
  - 例外処理を伴って処理する。主な呼出: self.get_imgname, self.get_scripts_path, start_sh_hst.parent.mkdir, self.make_compose, self.load, common.print_format

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### get_scripts_path

- 実装元: CmdboxLoad
- 役割: コンテナ内にマウントするスクリプトの保存先を返します Args: container (str): コンテナ名 Returns: Path: スクリプトの保存先パス
- 処理概要:
  - start_sh_hst を返却する

### make_compose

- 実装元: CmdboxLoad
- 役割: docker-compose.ymlの内容を作成します  Args: logger (logging.Logger): ロガー compose_path (Union[str, Path]): docker-compose.ymlのパス container (str): コンテナ名 imgname (str): イメージ名  Returns: Tuple[Dict[str, Any], Path]: docker-compose.ymlの内容, docker-compose.ymlのパス
- 処理概要:
  - (comp, compose_path) に self.make_compose_default の結果を格納する
  - (comp, compose_path) を返却する

## 単体テスト観点

- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_load.py
- apprun 実装元: CmdboxLoad
- svrun 実装元: Feature
- 生成日時: 2026-04-19T20:59:07
