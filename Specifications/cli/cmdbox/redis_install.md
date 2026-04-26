# cmdbox redis_install

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | cmdbox |
| cmd | redis_install |
| クラス | CmdboxRedisInstall |
| モジュール | cmdbox.app.features.cli.cmdbox_cmdbox_redis_install |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_redis_install.py |
| 継承元 | CmdboxBase, OneshotEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: cmdboxのRedisをインストールします。
- 英語: Installs the cmdbox Redis.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --install_from | 文字列 | いいえ | いいえ | いいえ | ubuntu/redis:latest | - | インストール元のRedisイメージを指定します。 |
| --install_tag | 文字列 | いいえ | いいえ | いいえ | None | - | 指定すると作成するdockerイメージのタグ名に追記出来ます。 |
| --compose_path | ファイル | いいえ | いいえ | はい | None | - | `docker-compose.yml` ファイルを指定します。 |

## 処理内容

### apprun

- 実装元: CmdboxRedisInstall
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 処理フロー:
  - common.set_debug を呼び出す
  - 例外処理を伴って処理する。主な呼出: self.valid, self.redis_install, common.print_format, common.set_debug

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: 抽出なし
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### redis_install

- 実装元: CmdboxRedisInstall
- 役割: redisサーバーをインストールします  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数  Returns: Dict[str, str]: 結果
- 処理概要:
  - 条件 platform.system() == 'Windows' を満たす場合は早期終了し、戻り値あり。結果キー: warn
  - dockerfile に Path の結果を格納する
  - コンテキスト open(dockerfile, 'w', encoding='utf-8') を利用して処理する。主な呼出: open, self._load_dockerfile, start_sh_hst.parent.mkdir, shutil.copytree, self.get_imgname, text.replace
  - (returncode, _, _cmd) に common.cmd の結果を格納する
  - dockerfile.unlink を呼び出す
  - (comp, docker_compose_path) に self.make_compose_redis の結果を格納する
  - コンテキスト open(docker_compose_path, 'w', encoding='utf-8') を利用して処理する。主な呼出: open, yaml.dump
  - 条件 returncode != 0 を満たす場合は早期終了し、INT_0。結果キー: error
  - 結果キー success を返却する

## 単体テスト観点

- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_redis_install.py
- apprun 実装元: CmdboxRedisInstall
- svrun 実装元: Feature
- 生成日時: 2026-04-26T00:53:06
