# web genpass

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | web |
| cmd | genpass |
| クラス | WebGenpass |
| モジュール | cmdbox.app.features.cli.cmdbox_web_genpass |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_genpass.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | 不明 |

## 概要

- 日本語: webモードで使用できるパスワード文字列を生成します。
- 英語: Generates a password string that can be used in web mode.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --pass_length | 整数 | いいえ | いいえ | いいえ | 16 | - | パスワードの長さを指定します。 |
| --pass_count | 整数 | いいえ | いいえ | いいえ | 5 | - | 生成するパスワードの件数を指定します。 |
| --use_alphabet | 文字列 | いいえ | いいえ | いいえ | both | notuse, upper, lower, both | パスワードに使用するアルファベットの種類を指定します。 `notuse` , `upper` , `lower` , `both` が指定できます。 |
| --use_number | 文字列 | いいえ | いいえ | いいえ | use | notuse, use | パスワードに使用する数字の種類を指定します。 `notuse` , `use` が指定できます。 |
| --use_symbol | 文字列 | いいえ | いいえ | いいえ | use | notuse, use | パスワードに使用する記号の種類を指定します。 `notuse` , `use` が指定できます。 |
| --similar | 文字列 | いいえ | いいえ | はい | exclude | exclude, include | 特定の似た文字を使用するかどうかを指定します。 `exclude` , `include` が指定できます。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: WebGenpass
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, INT_1, RESP_WARN
- 結果キー候補: warn, success, error
- 処理フロー:
  - (st, msg, obj) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 条件 args.pass_length < 1 を満たす場合は早期終了し、INT_1, RESP_WARN。結果キー: warn
  - 条件 args.pass_count < 1 を満たす場合は早期終了し、INT_1, RESP_WARN。結果キー: warn
  - 条件 args.pass_count >= 40 を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 例外処理を伴って処理する。主な呼出: range, dict, common.print_format, re.sub, passwords.append, common.random_string
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: error）
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, INT_1, RESP_WARN
- 結果キー候補: warn, success, error
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### gen_cert

- 実装元: WebGenpass
- 処理概要:
  - private_key に rsa.generate_private_key の結果を格納する
  - コンテキスト open(output_key, 'wb') を利用して処理する。主な呼出: open, f.write, logger.info, private_key.private_bytes, serialization.NoEncryption
  - subject, issuer に x509.Name の結果を格納する
  - self_cert に x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(private_key.public... の結果を格納する
  - コンテキスト open(output_cert, 'wb') を利用して処理する。主な呼出: open, f.write, logger.info, self_cert.public_bytes

## 単体テスト観点

- 選択肢を持つパラメータ use_alphabet, use_number, use_symbol, similar, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn, success, error が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, INT_1, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_genpass.py
- apprun 実装元: WebGenpass
- svrun 実装元: Feature
- 生成日時: 2026-04-23T23:40:04
