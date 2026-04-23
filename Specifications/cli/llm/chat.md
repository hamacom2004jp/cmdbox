# llm chat

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | llm |
| cmd | chat |
| クラス | LLMChat |
| モジュール | cmdbox.app.features.cli.cmdbox_llm_chat |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_llm_chat.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: LLMに対しチャットメッセージを送信します。
- 英語: Send a chat message to the LLM.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 600 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| --llmname | 文字列 | はい | いいえ | いいえ | None | - | 読み込むLLM設定の名前を指定します。 |
| --msg_role | 文字列 | はい | いいえ | いいえ | user | user, assistant, system, function, tool | メッセージ送信者の役割を指定します。 |
| --msg_name | 文字列 | いいえ | いいえ | いいえ | None | - | メッセージ送信者の名前を指定します。msg_roleが `function` または `tool` の場合は必須です。 |
| --msg_text | 複数行文字列 | いいえ | いいえ | いいえ | None | - | 送信するテキストの内容を指定します。 |
| --msg_text_system | 複数行文字列 | いいえ | いいえ | いいえ | 次のユーザーの依頼にこたえてください。\n\n{{msg_text}} | - | 送信するシステムプロンプトを指定します。 `{{AAA}}` と表記すると `AAA` のパラメータを設定できます。なお `{{msg_text}}` と指定すると `msg_text` オプションの値が設定されます。 |
| --msg_text_param | 辞書 | いいえ | はい | いいえ | None | - | 送信するテキストのパラメータを指定します。 |
| --msg_image_url | 文字列 | いいえ | いいえ | いいえ | None | - | 送信する画像のURLを指定します。 |
| --msg_audio | ファイル | いいえ | いいえ | いいえ | None | - | 送信する音声の内容を指定します。 |
| --msg_audio_format | 文字列 | いいえ | いいえ | いいえ | wav | wav, mp3, ogg, flac | 送信する音声のフォーマットを指定します。 |
| --msg_video_url | 文字列 | いいえ | いいえ | いいえ | None | - | 送信する動画のURLを指定します。 |
| --msg_file_url | 文字列 | いいえ | いいえ | いいえ | None | - | 送信するファイルのURLを指定します。 |
| --msg_doc | ファイル | いいえ | いいえ | いいえ | None | - | 送信するドキュメントの内容を指定します。 |
| --msg_doc_mime | 文字列 | いいえ | いいえ | いいえ | application/pdf | - | 送信するドキュメントのMIMEタイプを指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: LLMChat
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - (st, msg, cl) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 条件 not re.match('^[\\w\\-]+$', args.llmname) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.msg_audio を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.msg_doc を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - payload に dict の結果を格納する
  - payload_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: LLMChat
- 役割: サーバー側で受け取ったloadコマンドを処理します。
- 終了コード候補: INT_1, RESP_WARN, INT_2
- 結果キー候補: warn
- 処理フロー:
  - 例外処理を伴って処理する。主な呼出: json.loads, payload.get, self.chat, redis_cli.rpush, convert.b64str2str, dict
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_2
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### chat

- 実装元: LLMChat
- 役割: LLMにチャットメッセージを送信します。  Args: data_dir (Path): データディレクトリのパス logger (logging.Logger): ロガー llmname (str): LLM設定の名前 msg_role (str, optional): メッセージ送信者の役割。 msg_name (str, optional): メッセージ送信者の名前。 msg_text (str, optional): 送信するテキストの内容。 msg_text_system (str, optional): 送信するシステムプロンプト。 `{{AAA}}` と表記すると `AAA` のパラメータを設定できます。なお `{{msg_text}}` と指定すると `msg_text` オプションの値が設定されます。 msg_text_param (Dict[str, Any], optional): 送信するテキストのパラメータ。 msg_image_url (str, optional): 送信する画像のURL。 msg_audio (str, optional): 送信する音声の内容。Base64エンコードされた文字列で指定します。 msg_audio_format (str, optional): 送信する音声のフォーマット。 `wav`, `mp3`, `ogg`, `flac` のいずれかを指定します。 msg_video_url (str, optional): 送信する動画のURL。 msg_file_url (str, optional): 送信するファイルのURL。 msg_doc (str, optional): 送信するドキュメントの内容。Base64エンコードされた文字列で指定します。 msg_doc_mime (str, optional): 送信するドキュメントのMIMEタイプ。 Returns: Tuple[int, List[Dict[str, Any]]]: (ステータスコード, LLMからの応答メッセージのリスト)
- 処理概要:
  - 条件 not configure_path.exists() を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - コンテキスト configure_path.open('r', encoding='utf-8') を利用して処理する。主な呼出: configure_path.open, json.load
  - 条件 msg_text_system に応じて分岐する。主な呼出: msg_text_param.items, msg_text_system.replace, str
  - message に dict の結果を格納する
  - 条件 msg_text に応じて分岐する。主な呼出: message['content'].append, dict
  - 条件 msg_image_url に応じて分岐する。主な呼出: message['content'].append, dict
  - 条件 msg_audio に応じて分岐する。主な呼出: message['content'].append, dict
  - 条件 msg_video_url に応じて分岐する。主な呼出: message['content'].append, dict
  - 条件 msg_file_url に応じて分岐する。主な呼出: message['content'].append, dict
  - 条件 msg_doc に応じて分岐する。主な呼出: message['content'].append, dict
  - llmprov に configure.get の結果を格納する
  - 条件 llmprov == 'openai' に応じて分岐する。主な呼出: configure.get, litellm.completion, response.get, ValueError, choice.get, res.append
  - 終了コード RESP_SUCCESS を返却する

## 単体テスト観点

- 必須パラメータ llmname が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ msg_role, msg_audio_format, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ msg_text_param の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_llm_chat.py
- apprun 実装元: LLMChat
- svrun 実装元: LLMChat
- 生成日時: 2026-04-23T23:40:02
