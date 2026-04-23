# web gencert

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | web |
| cmd | gencert |
| クラス | WebGencert |
| モジュール | cmdbox.app.features.cli.cmdbox_web_gencert |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_gencert.py |
| 継承元 | UnsupportEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: webモードでSSLを簡易的に実装するために自己署名証明書を生成します。
- 英語: Generate a self-signed certificate for simple implementation of SSL in web mode.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --webhost | 文字列 | はい | いいえ | いいえ | localhost | - | 自己署名証明書のCN(Common Name)に指定するホスト名を指定します。 |
| --output_cert | ファイル | いいえ | いいえ | いいえ | None | - | 出力する自己署名証明書のファイルを指定します。省略した場合は `webhostオプションに指定したホスト名` .crt に出力されます。 |
| --output_cert_format | 文字列 | いいえ | いいえ | いいえ | PEM | DER, PEM | 出力する自己署名証明書のファイルフォーマットを指定します。 |
| --output_pkey | ファイル | いいえ | いいえ | いいえ | None | - | 出力する自己署名証明書の公開鍵のファイルを指定します。省略した場合は `webhostオプションに指定したホスト名` .pkey に出力されます。 |
| --output_pkey_format | 文字列 | いいえ | いいえ | いいえ | PEM | DER, PEM | 出力する自己署名証明書の公開鍵のファイルフォーマットを指定します。 |
| --output_key | ファイル | いいえ | いいえ | いいえ | None | - | 出力する自己署名証明書の秘密鍵ファイルを指定します。省略した場合は `webhostオプションに指定したホスト名` .key に出力されます。 |
| --output_key_format | 文字列 | いいえ | いいえ | いいえ | PEM | DER, PEM | 出力する自己署名証明書の秘密鍵ファイルフォーマットを指定します。 |
| --overwrite | 真偽値 | いいえ | いいえ | はい | false | True, False | 出力する自己署名証明書のファイルが存在する場合に上書きします。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: WebGencert
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn, success, error
- 処理フロー:
  - (st, msg, obj) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 条件 args.output_cert is None に応じて分岐する
  - 条件 args.output_pkey is None に応じて分岐する
  - 条件 args.output_key is None に応じて分岐する
  - output_cert に Path の結果を格納する
  - output_pkey に Path の結果を格納する
  - output_key に Path の結果を格納する
  - 条件 not args.overwrite and output_cert.exists() を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not args.overwrite and output_pkey.exists() を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not args.overwrite and output_key.exists() を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 例外処理を伴って処理する。主な呼出: self.gen_cert, dict, common.print_format
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: error）
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn, success, error
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### gen_cert

- 実装元: WebGencert
- 処理概要:
  - private_key に rsa.generate_private_key の結果を格納する
  - コンテキスト open(output_key, 'wb') を利用して処理する。主な呼出: open, f.write, logger.info, private_key.private_bytes, serialization.NoEncryption
  - subject, issuer に x509.Name の結果を格納する
  - self_cert に x509.CertificateBuilder().subject_name(subject).issuer_name(issuer).public_key(private_key.public... の結果を格納する
  - コンテキスト open(output_pkey, 'wb') を利用して処理する。主な呼出: open, f.write, logger.info, self_cert.public_key().public_bytes, self_cert.public_key
  - コンテキスト open(output_cert, 'wb') を利用して処理する。主な呼出: open, f.write, logger.info, self_cert.public_bytes

## 単体テスト観点

- 選択肢を持つパラメータ output_cert_format, output_pkey_format, output_key_format, overwrite, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー warn, success, error が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_web_gencert.py
- apprun 実装元: WebGencert
- svrun 実装元: Feature
- 生成日時: 2026-04-23T23:40:04
