# extract save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | extract |
| cmd | save |
| クラス | ExtractSave |
| モジュール | cmdbox.app.features.cli.cmdbox_extract_save |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_extract_save.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: 指定されたファイルからテキストを抽出する設定を保存します。
- 英語: Saves settings for extracting text from the specified file.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 120 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| --extract_name | 文字列 | はい | いいえ | いいえ | None | - | 抽出設定の名前を指定します。 |
| --extract_cmd | 文字列 | はい | いいえ | いいえ | None | - | 抽出コマンドの設定名を指定します。 |
| --extract_type | 文字列 | はい | いいえ | いいえ | file | , file | 抽出の種類を指定します。 |
| --scope | 文字列 | いいえ | いいえ | いいえ | client | , client, server | 参照先スコープを指定します。指定可能な画像タイプは `client` , `server` です。 |
| --client_data | 文字列 | いいえ | いいえ | いいえ | None | - | ローカルを参照させる場合のデータフォルダのパスを指定します。 |
| --loadpath | ディレクトリ | はい | いいえ | いいえ | None | - | 読み込み元パスを指定します。 |
| --loadregs | 文字列 | はい | いいえ | いいえ | .* | - | 読込み正規表現パターンを指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |

## 処理内容

### apprun

- 実装元: ExtractSave
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - payload に dict の結果を格納する
  - payload_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: ExtractSave
- 終了コード候補: INT_1, RESP_SUCCESS, RESP_WARN, INT_2
- 結果キー候補: success, warn
- 処理フロー:
  - 例外処理を伴って処理する。主な呼出: json.loads, configure_path.parent.mkdir, dict, redis_cli.rpush, convert.b64str2str, configure_path.open
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_2
- 結果キー候補: success, warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 必須パラメータ extract_name, extract_cmd, loadpath が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ extract_type, scope, output_json_append, stdout_log の境界値と不正値を確認する
- 結果オブジェクトのキー success, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_extract_save.py
- apprun 実装元: ExtractSave
- svrun 実装元: ExtractSave
- 生成日時: 2026-04-23T23:40:02
