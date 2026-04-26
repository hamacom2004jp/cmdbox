# cmdbox pgsql_install

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | cmdbox |
| cmd | pgsql_install |
| クラス | CmdboxPgSQLInstall |
| モジュール | cmdbox.app.features.cli.cmdbox_cmdbox_pgsql_install |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_pgsql_install.py |
| 継承元 | CmdboxBase, OneshotEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: PostgreSQLサーバーをインストールします。
- 英語: Installs the PostgreSQL server.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --install_pgsqlver | 文字列 | はい | いいえ | いいえ | 18 | - | PostgreSQLバージョンを指定します。 |
| --install_from | 文字列 | いいえ | いいえ | いいえ | postgres:18.2 | - | インストール元のPostgreSQLイメージを指定します。 |
| --install_tag | 文字列 | いいえ | いいえ | いいえ | None | - | 指定すると作成するdockerイメージのタグ名に追記出来ます。 |
| --no_install_pgvector | 真偽値 | いいえ | いいえ | いいえ | false | - | pgvector拡張機能をインストールしないかどうかを指定します。 |
| --install_pgvector_tag | 文字列 | いいえ | いいえ | いいえ | v0.8.2 | - | pgvector拡張機能のリポジトリ `https://github.com/pgvector/pgvector.git` のtag名を指定します。 |
| --no_install_age | 真偽値 | いいえ | いいえ | いいえ | false | - | Apache AGE拡張機能をインストールしないかどうかを指定します。 |
| --install_age_tag | 文字列 | いいえ | いいえ | いいえ | release/PG18/1.7.0 | - | Apache AGE拡張機能のリポジトリ `https://github.com/apache/age.git` のtag名を指定します。 |
| --no_install_pgcron | 真偽値 | いいえ | いいえ | いいえ | false | - | pg_cron拡張機能をインストールしないかどうかを指定します。 |
| --install_pgcron_tag | 文字列 | いいえ | いいえ | いいえ | v1.6.7 | - | pg_cron拡張機能のリポジトリ `https://github.com/citusdata/pg_cron.git` のtag名を指定します。 |
| --compose_path | ファイル | いいえ | いいえ | はい | None | - | `docker-compose.yml` ファイルを指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: CmdboxPgSQLInstall
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 処理フロー:
  - common.set_debug を呼び出す
  - 例外処理を伴って処理する。主な呼出: self.valid, self.pgsql_install, common.print_format, common.set_debug

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

### audited_by

- 実装元: CmdboxPgSQLInstall
- 役割: この機能が監査ログを記録する対象かどうかを返します  Returns: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 bool: 監査ログを記録する場合はTrue
- 処理概要:
  - False を返却する

### pgsql_install

- 実装元: CmdboxPgSQLInstall
- 役割: PostgreSQLサーバーをインストールします  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 Returns: Dict[str, str]: 結果
- 処理概要:
  - 条件 platform.system() == 'Windows' を満たす場合は早期終了し、戻り値あり。結果キー: warn
  - dockerfile に Path の結果を格納する
  - コンテキスト open(dockerfile, 'w', encoding='utf-8') を利用して処理する。主な呼出: open, self._load_dockerfile, start_sh_hst.parent.mkdir, shutil.copytree, self.get_imgname, text.replace
  - (returncode, _, _cmd) に common.cmd の結果を格納する
  - dockerfile.unlink を呼び出す
  - (comp, docker_compose_path) に self.make_compose_pgsql の結果を格納する
  - コンテキスト open(docker_compose_path, 'w', encoding='utf-8') を利用して処理する。主な呼出: open, yaml.dump
  - 条件 returncode != 0 を満たす場合は早期終了し、INT_0。結果キー: error
  - 結果キー success を返却する

## 単体テスト観点

- 選択肢を持つパラメータ output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_pgsql_install.py
- apprun 実装元: CmdboxPgSQLInstall
- svrun 実装元: Feature
- 生成日時: 2026-04-26T00:53:06
