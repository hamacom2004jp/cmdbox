# gui start

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | gui |
| cmd | start |
| クラス | GuiStart |
| モジュール | cmdbox.app.features.cli.cmdbox_gui_start |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_gui_start.py |
| 継承元 | WebStart, UnsupportEdgeFeature, Feature |
| Redis | 任意 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: GUIモードを起動します。
- 英語: Start GUI mode.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --data | ディレクトリ | いいえ | いいえ | いいえ | C:\Users\hama\.cmdbox | - | 省略した時は `$HONE/.cmdbox` を使用します。 |
| --allow_host | 文字列 | いいえ | いいえ | いいえ | 0.0.0.0 | - | 省略した時は `0.0.0.0` を使用します。 |
| --listen_port | 整数 | いいえ | いいえ | いいえ | 8081 | - | 省略した時は `8081` を使用します。 |
| --ssl_listen_port | 整数 | いいえ | いいえ | いいえ | 8443 | - | 省略した時は `8443` を使用します。 |
| --ssl_cert | ファイル | いいえ | いいえ | はい | None | - | SSLサーバー証明書ファイルを指定します。 |
| --ssl_key | ファイル | いいえ | いいえ | はい | None | - | SSLサーバー秘密鍵ファイルを指定します。 |
| --ssl_keypass | 文字列 | いいえ | いいえ | はい | None | - | SSLサーバー秘密鍵ファイルの複合化パスワードを指定します。 |
| --ssl_ca_certs | ファイル | いいえ | いいえ | はい | None | - | SSLサーバーCA証明書ファイルを指定します。 |
| --signin_file | ファイル | いいえ | いいえ | いいえ | .cmdbox/user_list.yml | - | サインイン可能なユーザーとパスワードを記載したファイルを指定します。通常 '.cmdbox/user_list.yml' を指定します。 |
| --session_domain | 文字列 | いいえ | いいえ | はい | None | - | サインインしたユーザーのセッションが有効なドメインを指定します。 |
| --session_path | 文字列 | いいえ | いいえ | はい | / | - | サインインしたユーザーのセッションが有効なパスを指定します。 |
| --session_secure | 真偽値 | いいえ | いいえ | はい | false | True, False | サインインしたユーザーのセッションにSecureフラグを設定します。 |
| --session_timeout | 整数 | いいえ | いいえ | はい | 900 | - | サインインしたユーザーのセッションタイムアウトの時間を秒で指定します。 |
| --gunicorn_workers | 整数 | いいえ | いいえ | はい | 6 | - | gunicornワーカー数を指定します。Linux環境でのみ有効です。-1又は未指定の場合はCPU数を使用します。 |
| --gunicorn_timeout | 整数 | いいえ | いいえ | はい | 900 | - | gunicornワーカーのタイムアウトの時間を秒で指定します。 |
| --client_only | 真偽値 | いいえ | いいえ | はい | false | True, False | サーバーへの接続を行わないようにします. |
| --outputs_key | 文字列 | いいえ | はい | いいえ | None | - | showimg及びwebcap画面で表示する項目を指定します。省略した場合は全ての項目を表示します。 |
| --doc_root | ディレクトリ | いいえ | いいえ | いいえ | None | - | カスタムファイルのドキュメントルート. フォルダ指定のカスタムファイルのパスから、doc_rootのパスを除去したパスでURLマッピングします。 |
| --gui_html | ファイル | いいえ | いいえ | いいえ | None | - | `gui.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。 |
| --filer_html | ファイル | いいえ | いいえ | いいえ | None | - | `filer.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。 |
| --result_html | ファイル | いいえ | いいえ | いいえ | None | - | `result.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。 |
| --users_html | ファイル | いいえ | いいえ | いいえ | None | - | `users.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。 |
| --agent_html | ファイル | いいえ | いいえ | いいえ | None | - | `agent.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。 |
| --assets | ファイル | いいえ | はい | いいえ | None | - | htmlファイルを使用する場合に必要なアセットファイルを指定します。 |
| --signin_html | ファイル | いいえ | いいえ | いいえ | None | - | `signin.html` を指定します。省略時はcmdbox内蔵のHTMLファイルを使用します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: GuiStart
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 処理フロー:
  - super().apprun(logger, args, tm, pf) を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: 抽出なし
- 結果キー候補: 抽出なし
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 選択肢を持つパラメータ session_secure, client_only, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ outputs_key, assets の 0 件・1 件・複数件入力を確認する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_gui_start.py
- apprun 実装元: GuiStart
- svrun 実装元: Feature
- 生成日時: 2026-04-19T20:59:10
