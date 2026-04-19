# cmd load

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | cmd |
| cmd | load |
| クラス | CmdLoad |
| モジュール | cmdbox.app.features.cli.cmdbox_cmd_load |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_cmd_load.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Feature |
| Redis | 不要 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | 不明 |

## 概要

- 日本語: データフォルダ配下のコマンドの内容を取得します。
- 英語: Obtains the contents of commands under the data folder.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --data | ディレクトリ | はい | いいえ | いいえ | C:\Users\hama\.cmdbox | - | 省略した時は `$HONE/.cmdbox` を使用します。 |
| --signin_file | ファイル | いいえ | いいえ | いいえ | None | - | サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.cmdbox/user_list.yml' を指定します。 |
| --groups | 文字列 | いいえ | はい | はい | None | - | `signin_file` を指定した場合に、このユーザーグループに許可されているコマンドリストを返すように指定します。 |
| --cmd_title | 文字列 | はい | いいえ | いいえ | None | - | 読込みたいコマンド名を指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: CmdLoad
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: success, warn
- 処理フロー:
  - 条件 args.data is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.cmd_title is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not hasattr(self, 'signin_file_data') or self.signin_file_data is None に応じて分岐する。主な呼出: signin.Signin.load_signin_file, hasattr
  - opt に common.loadopt の結果を格納する
  - 条件 not signin.Signin._check_cmd(self.signin_file_data, args.groups, opt['mode'], opt['cmd'], args.__... を満たす場合は早期終了し、RESP_WARN。結果キー: warn
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
- 結果キー候補: success, warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 必須パラメータ cmd_title が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ groups の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー success, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_cmd_load.py
- apprun 実装元: CmdLoad
- svrun 実装元: Feature
- 生成日時: 2026-04-19T20:59:07
