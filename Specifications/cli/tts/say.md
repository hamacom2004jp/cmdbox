# tts say

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | tts |
| cmd | say |
| クラス | TtsSay |
| モジュール | cmdbox.app.features.cli.cmdbox_tts_say |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_tts_say.py |
| 継承元 | ResultEdgeFeature, Feature |
| Redis | 任意 |
| Web モード禁止 | いいえ |
| Agent 利用 | はい |
| クラスタ転送 | False |

## 概要

- 日本語: Text-to-Speech(TTS)エンジンを使ってテキストを音声に変換します。
- 英語: Converts text to speech using the Text-to-Speech (TTS) engine.

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
| --tts_engine | 文字列 | はい | いいえ | いいえ | voicevox | , voicevox | 使用するTTSエンジンを指定します。 |
| --voicevox_model | 文字列 | いいえ | いいえ | いいえ | None | No.7アナウンス, No.7ノーマル, No.7読み聞かせ, Voidollノーマル, WhiteCULかなしい, WhiteCULたのしい, WhiteCULびえーん, WhiteCULノーマル, †聖騎士 紅桜†ノーマル, あいえるたんノーマル, ずんだもんあまあま, ずんだもんささやき, ずんだもんなみだめ, ずんだもんセクシー, ずんだもんツンツン, ずんだもんノーマル, ずんだもんヒソヒソ, ずんだもんヘロヘロ, ぞん子ノーマル, ぞん子低血圧, ぞん子実況風, ぞん子覚醒, ちび式じいノーマル, もち子さんのんびり, もち子さんセクシー／あん子, もち子さんノーマル, もち子さん喜び, もち子さん怒り, もち子さん泣き, ナースロボ＿タイプＴノーマル, ナースロボ＿タイプＴ内緒話, ナースロボ＿タイプＴ恐怖, ナースロボ＿タイプＴ楽々, ユーレイちゃんささやき, ユーレイちゃんツクモちゃん, ユーレイちゃんノーマル, ユーレイちゃん哀しみ, ユーレイちゃん甘々, 中国うさぎおどろき, 中国うさぎこわがり, 中国うさぎへろへろ, 中国うさぎノーマル, 中部つるぎおどおど, 中部つるぎノーマル, 中部つるぎヒソヒソ, 中部つるぎ怒り, 中部つるぎ絶望と敗北, 九州そらあまあま, 九州そらささやき, 九州そらセクシー, 九州そらツンツン, 九州そらノーマル, 冥鳴ひまりノーマル, 剣崎雌雄ノーマル, 四国めたんあまあま, 四国めたんささやき, 四国めたんセクシー, 四国めたんツンツン, 四国めたんノーマル, 四国めたんヒソヒソ, 小夜/SAYOノーマル, 後鬼ぬいぐるみver., 後鬼人間ver., 後鬼人間（怒り）ver., 後鬼鬼ver., 春日部つむぎノーマル, 春歌ナナノーマル, 東北きりたんノーマル, 東北ずん子ノーマル, 東北イタコノーマル, 栗田まろんノーマル, 櫻歌ミコノーマル, 櫻歌ミコロリ, 櫻歌ミコ第二形態, 波音リツクイーン, 波音リツノーマル, 満別花丸ささやき, 満別花丸ぶりっ子, 満別花丸ノーマル, 満別花丸ボーイ, 満別花丸元気, 猫使アルうきうき, 猫使アルおちつき, 猫使アルつよつよ, 猫使アルへろへろ, 猫使アルノーマル, 猫使ビィおちつき, 猫使ビィつよつよ, 猫使ビィノーマル, 猫使ビィ人見知り, 玄野武宏ツンギレ, 玄野武宏ノーマル, 玄野武宏喜び, 玄野武宏悲しみ, 琴詠ニアノーマル, 白上虎太郎おこ, 白上虎太郎びえーん, 白上虎太郎びくびく, 白上虎太郎ふつう, 白上虎太郎わーい, 雀松朱司ノーマル, 離途シリアス, 離途ノーマル, 雨晴はうノーマル, 青山龍星かなしみ, 青山龍星しっとり, 青山龍星ノーマル, 青山龍星不機嫌, 青山龍星喜び, 青山龍星囁き, 青山龍星熱血, 麒ヶ島宗麟ノーマル, 黒沢冴白ノーマル | 使用するTTSエンジンのモデルを指定します。 |
| --tts_text | 複数行文字列 | はい | いいえ | いいえ | None | - | 変換するテキストを指定します。 |
| --tts_output | ファイル | いいえ | いいえ | いいえ | None | - | 変換後の音声ファイルの出力先を指定します。 |

## 処理内容

### apprun

- 実装元: TtsSay
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - 条件 args.tts_engine is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.tts_engine == 'voicevox' を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.tts_text is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - tts_engine_b64 に convert.str2b64str の結果を格納する
  - tts_text_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - 条件 args.tts_output に応じて分岐する。主な呼出: convert.b64str2bytes, common.save_file, f.write
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: TtsSay
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: INT_2, INT_1
- 処理フロー:
  - tts_engine に convert.b64str2str の結果を格納する
  - voicevox_model に convert.b64str2str の結果を格納する
  - tts_text に convert.b64str2str の結果を格納する
  - st に self.say の結果を格納する
  - st を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_2, INT_1
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### say

- 実装元: TtsSay
- 役割: TTSエンジンを使ってテキストを音声に変換します  Args: reskey (str): レスポンスキー data_dir (Path): データディレクトリ tts_engine (str): TTSエンジン voicevox_model (str): VoiceVoxモデル tts_text (str): TTSテキスト logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: レスポンスコード
- 処理概要:
  - 例外処理を伴って処理する。主な呼出: TtsSay.tts_start, TtsSay.tts_say, redis_cli.rpush, logger.warning, dict, TtsSay.tts_stop
  - Exception を捕捉した場合の代替経路を持つ（終了コード候補: RESP_WARN）

## 単体テスト観点

- 必須パラメータ tts_text が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ tts_engine, voicevox_model の境界値と不正値を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_2, INT_1 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_tts_say.py
- apprun 実装元: TtsSay
- svrun 実装元: TtsSay
- 生成日時: 2026-04-19T20:59:11
