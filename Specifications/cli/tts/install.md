# tts install

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | tts |
| cmd | install |
| クラス | TtsInstall |
| モジュール | cmdbox.app.features.cli.cmdbox_tts_install |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_tts_install.py |
| 継承元 | UnsupportEdgeFeature, Feature |
| Redis | 任意 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: Text-to-Speech(TTS)エンジンをインストールします。
- 英語: Installs the Text-to-Speech (TTS) engine.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --host | 文字列 | はい | いいえ | はい | localhost | - | Redisサーバーのサービスホストを指定します。 |
| --port | 整数 | はい | いいえ | はい | 6379 | - | Redisサーバーのサービスポートを指定します。 |
| --password | パスワード | はい | いいえ | はい | password | - | Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `password` を使用します。 |
| --svname | 文字列 | はい | いいえ | はい | cmdbox | - | サーバーのサービス名を指定します。省略時は `server` を使用します。 |
| --data | ディレクトリ | いいえ | いいえ | いいえ | C:\Users\hama\.cmdbox | - | 省略した時は `$HONE/.cmdbox` を使用します。 |
| --retry_count | 整数 | いいえ | いいえ | はい | 3 | - | Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。 |
| --retry_interval | 整数 | いいえ | いいえ | はい | 5 | - | Redisサーバーに再接続までの秒数を指定します。 |
| --timeout | 整数 | いいえ | いいえ | はい | 300 | - | サーバーの応答が返ってくるまでの最大待ち時間を指定。 |
| --client_only | 真偽値 | いいえ | いいえ | はい | false | True, False | サーバーへの接続を行わないようにします。 |
| --force_install | 真偽値 | いいえ | いいえ | いいえ | false | True, False | 既にインストール済みであっても上書きインストールを行います。 |
| --tts_engine | 文字列 | はい | いいえ | いいえ | voicevox | , voicevox | 使用するTTSエンジンを指定します。 |
| --voicevox_ver | 文字列 | いいえ | いいえ | いいえ | 0.16.3 | , 0.16.3 | 使用するVOICEVOXのバージョンを指定します。 |
| --voicevox_whl | 文字列 | いいえ | いいえ | いいえ | voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl | , voicevox_core-0.16.3-cp310-abi3-win32.whl, voicevox_core-0.16.3-cp310-abi3-win_amd64.whl, voicevox_core-0.16.3-cp310-abi3-macosx_10_12_x86_64.whl, voicevox_core-0.16.3-cp310-abi3-macosx_11_0_arm64.whl, voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_aarch64.whl, voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl | 使用するVOICEVOXのホイールファイルを指定します。 |
| --openjtalk_ver | 文字列 | いいえ | いいえ | いいえ | v1.11.1 | , v1.11.1 | 使用するopenjtalkのバージョンを指定します。 |
| --openjtalk_dic | 文字列 | いいえ | いいえ | いいえ | open_jtalk_dic_utf_8-1.11.tar.gz | , open_jtalk_dic_utf_8-1.11.tar.gz | 使用するopenjtalkの辞書ファイルを指定します。 |
| --onnxruntime_ver | 文字列 | いいえ | いいえ | いいえ | voicevox_onnxruntime-1.17.3 | , voicevox_onnxruntime-1.17.3 | 使用するONNX Runtimeのバージョンを指定します。 |
| --onnxruntime_lib | 文字列 | いいえ | いいえ | いいえ | voicevox_onnxruntime-linux-x64-1.17.3.tgz | , voicevox_onnxruntime-linux-arm64-1.17.3.tgz, voicevox_onnxruntime-linux-armhf-1.17.3.tgz, voicevox_onnxruntime-linux-x64-1.17.3.tgz, voicevox_onnxruntime-linux-x64-cuda-1.17.3.tgz, voicevox_onnxruntime-osx-arm64-1.17.3.tgz, voicevox_onnxruntime-osx-x86_64-1.17.3.tgz, voicevox_onnxruntime-win-x64-1.17.3.tgz, voicevox_onnxruntime-win-x64-cuda-1.17.3.tgz, voicevox_onnxruntime-win-x64-dml-1.17.3.tgz, voicevox_onnxruntime-win-x86-1.17.3.tgz | 使用するONNX Runtimeのライブラリファイルを指定します。 |

## 処理内容

### apprun

- 実装元: TtsInstall
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - 条件 args.data is None and (not args.client_only) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.tts_engine is None を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.tts_engine == 'voicevox' を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.client_only に応じて分岐する。主な呼出: self.install, convert.str2b64str, client.Client, cl.redis_cli.send_cmd, common.random_string, str
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: TtsInstall
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_2, INT_1
- 処理フロー:
  - tts_engine に convert.b64str2str の結果を格納する
  - voicevox_ver に convert.b64str2str の結果を格納する
  - voicevox_whl に convert.b64str2str の結果を格納する
  - openjtalk_ver に convert.b64str2str の結果を格納する
  - openjtalk_dic に convert.b64str2str の結果を格納する
  - onnxruntime_ver に convert.b64str2str の結果を格納する
  - onnxruntime_lib に convert.b64str2str の結果を格納する
  - ret に self.install の結果を格納する
  - redis_cli.rpush を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN, INT_2, INT_1
- 結果キー候補: warn
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### install

- 実装元: TtsInstall
- 役割: TTSエンジンをインストールします  Args: reskey (str): レスポンスキー data_dir (Path): データディレクトリ tts_engine (str): TTSエンジン voicevox_ver (str): VoiceVoxバージョン voicevox_whl (str): VoiceVox ホイールファイル openjtalk_ver (str): Open JTalk バージョン openjtalk_dic (str): Open JTalk 辞書 onnxruntime_ver (str): ONNX Runtime バージョン onnxruntime_lib (str): ONNX Runtime ライブラリ force_install (bool): 強制インストールフラグ logger (logging.Logger): ロガー  Returns: Dict[str, Any]: 結果
- 処理概要:
  - 例外処理を伴って処理する。主な呼出: voicevox_dir.mkdir, pip.main, logger.info, dict, logger.warning, voicevox_dir.exists
  - Exception を捕捉した場合の代替経路を持つ（結果キー: warn）

## 単体テスト観点

- 選択肢を持つパラメータ client_only, force_install, tts_engine, voicevox_ver, voicevox_whl, openjtalk_ver, openjtalk_dic, onnxruntime_ver, onnxruntime_lib の境界値と不正値を確認する
- 結果オブジェクトのキー warn が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_2, INT_1 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_tts_install.py
- apprun 実装元: TtsInstall
- svrun 実装元: TtsInstall
- 生成日時: 2026-04-19T20:59:11
