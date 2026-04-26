# web user_add

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | web |
| cmd | user_add |
| クラス | WebUserAdd |
| モジュール | cmdbox.app.features.cli.cmdbox_web_user_add |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_web_user_add.py |
| 継承元 | UnsupportEdgeFeature, Validator, Feature |
| Redis | 任意 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: Webモードのユーザーを追加します。
- 英語: Add a user in Web mode.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --user_id | 整数 | はい | いいえ | いいえ | None | - | ユーザーIDを指定します。他のユーザーと重複しないようにしてください。 |
| --user_name | 文字列 | はい | いいえ | いいえ | None | - | ユーザー名を指定します。他のユーザーと重複しないようにしてください。 |
| --user_pass | 文字列 | いいえ | いいえ | いいえ | None | - | ユーザーパスワードを指定します。 |
| --user_pass_hash | 文字列 | いいえ | いいえ | いいえ | sha1 | oauth2, saml, plain, md5, sha1, sha256 | ユーザーパスワードのハッシュアルゴリズムを指定します。 |
| --user_email | 文字列 | いいえ | いいえ | いいえ | None | - | ユーザーメールアドレスを指定します。 `user_pass_hash` が `oauth2` 又は `saml` の時は必須です。 |
| --user_group | 文字列 | はい | はい | いいえ | None | - | ユーザーが所属するグループを指定します。 |
| --signin_file | ファイル | はい | いいえ | いいえ | .cmdbox/user_list.yml | - | サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.cmdbox/user_list.yml' を指定します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: WebUserAdd
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success, warn
- 処理フロー:
  - (st, msg, obj) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 例外処理を伴って処理する。主な呼出: web.Web, dict, w.user_add, common.print_format
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success, warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 必須パラメータ user_id, user_name, user_group が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ user_pass_hash, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ user_group の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー success, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_web_user_add.py
- apprun 実装元: WebUserAdd
- svrun 実装元: Feature
- 生成日時: 2026-04-26T00:53:09
