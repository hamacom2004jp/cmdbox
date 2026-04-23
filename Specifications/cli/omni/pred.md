# omni pred

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | omni |
| cmd | pred |
| クラス | OmniPred |
| モジュール | cmdbox.app.features.cli.cmdbox_omni_pred |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_omni_pred.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: Omniモデルを使用して、マルチモーダル推論を行います。(実験用)
- 英語: Performs multimodal inference using the Omni model.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 3600 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: OmniPred
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

- 実装元: OmniPred
- 役割: サーバー側で受け取ったlistコマンドを処理します。
- 終了コード候補: INT_1, RESP_SUCCESS, RESP_WARN, INT_0, INT_2
- 結果キー候補: success, warn
- 処理フロー:
  - 例外処理を伴って処理する。主な呼出: json.loads, self.pred, dict, redis_cli.rpush, convert.b64str2str, argparse.Namespace
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_0, INT_2
- 結果キー候補: success, warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### pred

- 実装元: OmniPred
- 処理概要:
  - offload_folder に tempfile.gettempdir の結果を格納する
  - model に Qwen3OmniMoeForConditionalGeneration.from_pretrained(MODEL_PATH, dtype='auto', device_map=None, o... の結果を格納する
  - processor に Qwen3OmniMoeProcessor.from_pretrained の結果を格納する
  - text に processor.apply_chat_template の結果を格納する
  - (audios, images, videos) に process_mm_info の結果を格納する
  - inputs に processor の結果を格納する
  - inputs に inputs.to(model.device).to の結果を格納する
  - (text_ids, audio) に model.generate の結果を格納する
  - text に processor.batch_decode の結果を格納する
  - print を呼び出す
  - 条件 audio is not None に応じて分岐する。主な呼出: sf.write, audio.reshape(-1).detach().cpu().numpy, audio.reshape(-1).detach().cpu, audio.reshape(-1).detach, audio.reshape
  - 終了コード RESP_SUCCESS, INT_0 / 結果キー outputs を返却する

## 単体テスト観点

- 選択肢を持つパラメータ output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 結果オブジェクトのキー success, warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_0, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_omni_pred.py
- apprun 実装元: OmniPred
- svrun 実装元: OmniPred
- 生成日時: 2026-04-23T23:40:03
