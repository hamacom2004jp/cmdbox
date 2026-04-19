# edge config

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | edge |
| cmd | config |
| クラス | EdgeConfig |
| モジュール | cmdbox.app.features.cli.cmdbox_edge_config |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_edge_config.py |
| 継承元 | UnsupportEdgeFeature, Feature |
| Redis | 不要 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: 端末モードの設定を行います。
- 英語: Set the edge mode.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --endpoint | 文字列 | いいえ | いいえ | いいえ | http://localhost:8081 | - | エンドポイントのURLを指定します。 |
| --icon_path | ファイル | いいえ | いいえ | いいえ | F:\devenv\cmdbox\cmdbox\web\assets\cmdbox\favicon.ico | - | アイコン画像のパスを指定します。 |
| --auth_type | 文字列 | いいえ | いいえ | いいえ | idpw | noauth, idpw, apikey, oauth2, saml | エンドポイント接続じの認証方式を指定します。 |
| --user | 文字列 | いいえ | いいえ | いいえ | user | - | エンドポイントへの接続ユーザーを指定します。 |
| --password | パスワード | いいえ | いいえ | いいえ | password | - | エンドポイントへの接続パスワードを指定します。 |
| --apikey | パスワード | いいえ | いいえ | いいえ | None | - | エンドポイントへの接続するためのAPIKEYを指定します。 |
| --oauth2 | 文字列 | いいえ | いいえ | いいえ | None | , google, github, azure | OAuth2認証を使用してエンドポイントに接続します。 |
| --oauth2_port | 整数 | いいえ | いいえ | いいえ | 8091 | - | OAuth2認証を使用する場合のコールバックポートを指定します。省略した時は `8091` を使用します。 |
| --oauth2_tenant_id | 文字列 | いいえ | いいえ | いいえ | None | - | OAuth2認証を使用するときのテナントIDを指定します。 |
| --oauth2_client_id | 文字列 | いいえ | いいえ | いいえ | None | - | OAuth2認証を使用するときのクライアントIDを指定します。 |
| --oauth2_client_secret | 文字列 | いいえ | いいえ | いいえ | None | - | OAuth2認証を使用するときのクライアントシークレットを指定します。 |
| --oauth2_timeout | 整数 | いいえ | いいえ | いいえ | 60 | - | OAuth2認証が完了するまでのタイムアウト時間を指定します。 |
| --saml | 文字列 | いいえ | いいえ | いいえ | None | , azure | SAML認証を使用してエンドポイントに接続します。 |
| --saml_port | 整数 | いいえ | いいえ | いいえ | 8091 | - | SAML認証を使用する場合のコールバックポートを指定します。省略した時は `8091` を使用します。 |
| --saml_tenant_id | 文字列 | いいえ | いいえ | いいえ | None | - | SAML認証を使用するときのテナントIDを指定します。 |
| --saml_timeout | 整数 | いいえ | いいえ | いいえ | 60 | - | SAML認証が完了するまでのタイムアウト時間を指定します。 |
| --data | ディレクトリ | いいえ | いいえ | はい | C:\Users\hama\.cmdbox | - | 省略した時は f`$HONE/.cmdbox` を使用します。 |
| --svcert_no_verify | 真偽値 | いいえ | いいえ | はい | false | False, True | HTTPSリクエストの時にサーバー証明書の検証を行いません。 |
| --timeout | 整数 | いいえ | いいえ | はい | 30 | - | リクエストが完了するまでのタイムアウト時間を指定します。 |

## 処理内容

### apprun

- 実装元: EdgeConfig
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS
- 処理フロー:
  - 条件 args.data is None に応じて分岐する
  - app に edge.Edge の結果を格納する
  - msg に app.configure の結果を格納する
  - common.print_format を呼び出す
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS
- 結果キー候補: 抽出なし
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 単体テスト観点

- 選択肢を持つパラメータ auth_type, oauth2, saml, svcert_no_verify の境界値と不正値を確認する
- 終了コード RESP_SUCCESS の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_edge_config.py
- apprun 実装元: EdgeConfig
- svrun 実装元: Feature
- 生成日時: 2026-04-19T20:59:08
