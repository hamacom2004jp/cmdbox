# agent runner_save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | runner_save |
| クラス | AgentRunnerSave |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_runner_save |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_runner_save.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: Runner 設定を保存します。
- 英語: Saves runner configuration.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 60 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| --runner_name | 文字列 | はい | いいえ | いいえ | None | - | 保存するRunnerの名前を指定します。 |
| --agent | 文字列 | はい | いいえ | いいえ | None | - | Runnerが参照するAgent設定名を指定します。 |
| --session_store_type | 文字列 | いいえ | いいえ | いいえ | memory | memory, sqlite, postgresql | セッションの保存方法を指定します。 |
| --tts_engine | 文字列 | はい | いいえ | いいえ | voicevox | , voicevox | 使用するTTSエンジンを指定します。 |
| --memory | 文字列 | いいえ | いいえ | いいえ | None | - | Runnerが参照するメモリー設定名を指定します。 |
| --rag | 文字列 | いいえ | はい | いいえ | None | - | Runnerが参照するRAG設定名を指定します。 |
| --voicevox_model | 文字列 | いいえ | いいえ | いいえ | None | No.7アナウンス, No.7ノーマル, No.7読み聞かせ, Voidollノーマル, WhiteCULかなしい, WhiteCULたのしい, WhiteCULびえーん, WhiteCULノーマル, †聖騎士 紅桜†ノーマル, あいえるたんノーマル, ずんだもんあまあま, ずんだもんささやき, ずんだもんなみだめ, ずんだもんセクシー, ずんだもんツンツン, ずんだもんノーマル, ずんだもんヒソヒソ, ずんだもんヘロヘロ, ぞん子ノーマル, ぞん子低血圧, ぞん子実況風, ぞん子覚醒, ちび式じいノーマル, もち子さんのんびり, もち子さんセクシー／あん子, もち子さんノーマル, もち子さん喜び, もち子さん怒り, もち子さん泣き, ナースロボ＿タイプＴノーマル, ナースロボ＿タイプＴ内緒話, ナースロボ＿タイプＴ恐怖, ナースロボ＿タイプＴ楽々, ユーレイちゃんささやき, ユーレイちゃんツクモちゃん, ユーレイちゃんノーマル, ユーレイちゃん哀しみ, ユーレイちゃん甘々, 中国うさぎおどろき, 中国うさぎこわがり, 中国うさぎへろへろ, 中国うさぎノーマル, 中部つるぎおどおど, 中部つるぎノーマル, 中部つるぎヒソヒソ, 中部つるぎ怒り, 中部つるぎ絶望と敗北, 九州そらあまあま, 九州そらささやき, 九州そらセクシー, 九州そらツンツン, 九州そらノーマル, 冥鳴ひまりノーマル, 剣崎雌雄ノーマル, 四国めたんあまあま, 四国めたんささやき, 四国めたんセクシー, 四国めたんツンツン, 四国めたんノーマル, 四国めたんヒソヒソ, 小夜/SAYOノーマル, 後鬼ぬいぐるみver., 後鬼人間ver., 後鬼人間（怒り）ver., 後鬼鬼ver., 春日部つむぎノーマル, 春歌ナナノーマル, 東北きりたんノーマル, 東北ずん子ノーマル, 東北イタコノーマル, 栗田まろんノーマル, 櫻歌ミコノーマル, 櫻歌ミコロリ, 櫻歌ミコ第二形態, 波音リツクイーン, 波音リツノーマル, 満別花丸ささやき, 満別花丸ぶりっ子, 満別花丸ノーマル, 満別花丸ボーイ, 満別花丸元気, 猫使アルうきうき, 猫使アルおちつき, 猫使アルつよつよ, 猫使アルへろへろ, 猫使アルノーマル, 猫使ビィおちつき, 猫使ビィつよつよ, 猫使ビィノーマル, 猫使ビィ人見知り, 玄野武宏ツンギレ, 玄野武宏ノーマル, 玄野武宏喜び, 玄野武宏悲しみ, 琴詠ニアノーマル, 白上虎太郎おこ, 白上虎太郎びえーん, 白上虎太郎びくびく, 白上虎太郎ふつう, 白上虎太郎わーい, 雀松朱司ノーマル, 離途シリアス, 離途ノーマル, 雨晴はうノーマル, 青山龍星かなしみ, 青山龍星しっとり, 青山龍星ノーマル, 青山龍星不機嫌, 青山龍星喜び, 青山龍星囁き, 青山龍星熱血, 麒ヶ島宗麟ノーマル, 黒沢冴白ノーマル | 使用するTTSエンジンのモデルを指定します。 |
| --session_store_pghost | 文字列 | いいえ | いいえ | いいえ | pgsql | - | セッション保存用PostgreSQLホストを指定します。 |
| --session_store_pgport | 整数 | いいえ | いいえ | いいえ | 5432 | - | セッション保存用PostgreSQLポートを指定します。 |
| --session_store_pguser | 文字列 | いいえ | いいえ | いいえ | pgsql | - | セッション保存用PostgreSQLのユーザー名を指定します。 |
| --session_store_pgpass | パスワード | いいえ | いいえ | いいえ | pgsql | - | セッション保存用PostgreSQLのパスワードを指定します。 |
| --session_store_pgdbname | 文字列 | いいえ | いいえ | いいえ | pgsql | - | セッション保存用PostgreSQLのデータベース名を指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: AgentRunnerSave
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - 条件 not hasattr(args, 'runner_name') or args.runner_name is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not re.match('^[\\w\\-]+$', args.runner_name) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not hasattr(args, 'agent') or args.agent is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - configure に dict の結果を格納する
  - payload_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: AgentRunnerSave
- 終了コード候補: INT_1, RESP_SUCCESS, RESP_WARN, INT_2
- 結果キー候補: success, warn
- 処理フロー:
  - 例外処理を伴って処理する。主な呼出: json.loads, configure.get, configure_path.parent.mkdir, dict, redis_cli.rpush, convert.b64str2str
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN / 結果キー: warn）

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_1, INT_2
- 結果キー候補: warn, success
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### list_agents

- 実装元: AgentRunnerSave
- 処理概要:
  - 条件 not agent_dir.exists() or not agent_dir.is_dir() を満たす場合は早期終了し、戻り値あり
  - paths に agent_dir.glob の結果を格納する
  - sorted(paths) を走査し、p ごとに処理する。主な呼出: sorted, ret.append, name.startswith, name.endswith
  - ret を返却する

## 単体テスト観点

- 必須パラメータ runner_name, agent が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ session_store_type, tts_engine, voicevox_model, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ rag の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_runner_save.py
- apprun 実装元: AgentRunnerSave
- svrun 実装元: AgentRunnerSave
- 生成日時: 2026-04-19T20:59:06
