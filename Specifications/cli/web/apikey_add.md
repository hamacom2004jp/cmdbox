# web apikey_add

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | web |
| cmd | apikey_add |
| クラス | WebApikeyAdd |
| モジュール | cmdbox.app.features.cli.cmdbox_web_apikey_add |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_apikey_add.py |
| 継承元 | UnsupportEdgeFeature, Feature |
| Redis | 任意 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: WebモードのユーザーのApiKeyを追加します。
- 英語: Add an ApiKey for a user in Web mode.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --user_name | 文字列 | はい | いいえ | いいえ | None | - | 対象のユーザー名を指定します。 |
| --apikey_name | 文字列 | はい | いいえ | いいえ | None | - | このユーザーのApiKey名を指定します。 |
| --signin_file | ファイル | はい | いいえ | いいえ | None | - | サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.cmdbox/user_list.yml' を指定します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: WebApikeyAdd
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_WARN, RESP_SUCCESS
- 結果キー候補: warn, success
- 処理フロー:
  - 条件 args.data is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 例外処理を伴って処理する。主な呼出: web.Web, dict, w.apikey_add, common.print_format
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_WARN, RESP_SUCCESS
- 結果キー候補: warn, success
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 必須パラメータ user_name, apikey_name, signin_file が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_WARN, RESP_SUCCESS の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_apikey_add.py
- apprun 実装元: WebApikeyAdd
- svrun 実装元: Feature
- 生成日時: 2026-04-19T20:59:12
