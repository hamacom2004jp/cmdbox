# client file_list

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | client |
| cmd | file_list |
| クラス | ClientFileList |
| モジュール | cmdbox.app.features.cli.cmdbox_client_file_list |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_client_file_list.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 任意 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: データフォルダ配下のファイルリストを取得します。
- 英語: Get a list of files under the data folder.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --svpath | ファイル | はい | いいえ | いいえ | / | - | サーバーのデータフォルダ以下のパスを指定します。省略時は `/` を使用します。 |
| --fwpath | ファイル | はい | はい | いいえ | None | - | 指定したパスが範囲外であるかどうかを判定するパスを指定します。このパスの配下でない場合、このパスを指定したと解釈します。 |
| --listregs | 文字列 | いいえ | いいえ | いいえ | .* | - | リストアップする条件を正規表現で指定します。 |
| --recursive | 真偽値 | いいえ | いいえ | はい | false | True, False | 指定したパスに含まれるフォルダについて、再帰的にファイルリストを取得します。 |
| --scope | 文字列 | はい | いいえ | いいえ | client | client, current, server | 参照先スコープを指定します。指定可能な画像タイプは `client` , `current` , `server` です。 |
| --client_data | 文字列 | いいえ | いいえ | いいえ | None | - | ローカルを参照させる場合のデータフォルダのパスを指定します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 15 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: ClientFileList
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 処理フロー:
  - 条件 not hasattr(args, 'fwpath') or args.fwpath is None に応じて分岐する。主な呼出: hasattr
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - cl に client.Client の結果を格納する
  - ret に cl.file_list の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: ClientFileList
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: INT_1, INT_2
- 処理フロー:
  - payload に json.loads の結果を格納する
  - svpath に payload.get の結果を格納する
  - recursive に payload.get の結果を格納する
  - fwpaths に payload.get の結果を格納する
  - listregs に payload.get の結果を格納する
  - st に self.file_list の結果を格納する
  - st を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_2
- 結果キー候補: 抽出なし
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### file_list

- 実装元: ClientFileList
- 役割: ファイルリストを取得する  Args: reskey (str): レスポンスキー current_path (str): ファイルパス recursive (bool): 再帰的に取得するかどうか fwpaths (List[str]): 範囲内かどうかを示すパスのリスト listregs (str): リストアップする正規表現条件 data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: レスポンスコード
- 処理概要:
  - 例外処理を伴って処理する。主な呼出: filer.Filer, f.file_list, redis_cli.rpush, logger.warning, dict
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN）

### get_svcmd

- 実装元: ClientFileList
- 役割: この機能のサーバー側のコマンドを返します  Returns: str: サーバー側のコマンド
- 処理概要:
  - 'file_list' を返却する

## 単体テスト観点

- 必須パラメータ fwpath が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ recursive, scope, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ fwpath の 0 件・1 件・複数件入力を確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_client_file_list.py
- apprun 実装元: ClientFileList
- svrun 実装元: ClientFileList
- 生成日時: 2026-04-26T00:53:05
