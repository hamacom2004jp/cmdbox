# cmdbox server_install

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | cmdbox |
| cmd | server_install |
| クラス | CmdboxServerInstall |
| モジュール | cmdbox.app.features.cli.cmdbox_cmdbox_server_install |
| 実装ファイル | /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_server_install.py |
| 継承元 | CmdboxBase, OneshotEdgeFeature, Validator, Feature |
| Redis | 不要 |
| Web モード禁止 | はい |
| Agent 利用 | いいえ |
| クラスタ転送 | 不明 |

## 概要

- 日本語: cmdboxのコンテナをインストールします。
- 英語: Install the cmdbox container.

## パラメータ

| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| --data | ディレクトリ | いいえ | いいえ | いいえ | /home/ubuntu/.cmdbox | - | 省略した時は `$HONE/.cmdbox` を使用します。 |
| --install_cmdbox | 文字列 | いいえ | いいえ | はい | cmdbox==0.7.9 | - | 省略した時は `cmdbox==0.7.9` を使用します。 |
| --install_from | 文字列 | いいえ | いいえ | いいえ | None | - | 作成するdockerイメージの元となるFROMイメージを指定します。 |
| --install_no_python | 真偽値 | いいえ | いいえ | いいえ | false | True, False | pythonのインストールを行わないようにします。 |
| --install_compile_python | 真偽値 | いいえ | いいえ | いいえ | false | True, False | python3をコンパイルしてインストールします。install_no_pythonが指定されるとそちらを優先します。 |
| --install_tag | 文字列 | いいえ | いいえ | いいえ | None | - | 指定すると作成するdockerイメージのタグ名に追記出来ます。 |
| --install_use_gpu | 真偽値 | いいえ | いいえ | いいえ | false | True, False | GPUを使用するモジュール構成でインストールします。 |
| --tts_engine | 文字列 | はい | いいえ | いいえ | voicevox | , voicevox | 使用するTTSエンジンを指定します。 |
| --voicevox_ver | 文字列 | いいえ | いいえ | いいえ | 0.16.3 | , 0.16.3 | 使用するVOICEVOXのバージョンを指定します。 |
| --voicevox_whl | 文字列 | いいえ | いいえ | いいえ | voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl | , voicevox_core-0.16.3-cp310-abi3-win32.whl, voicevox_core-0.16.3-cp310-abi3-win_amd64.whl, voicevox_core-0.16.3-cp310-abi3-macosx_10_12_x86_64.whl, voicevox_core-0.16.3-cp310-abi3-macosx_11_0_arm64.whl, voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_aarch64.whl, voicevox_core-0.16.3-cp310-abi3-manylinux_2_34_x86_64.whl | 使用するVOICEVOXのホイールファイルを指定します。 |
| --init_extra | 文字列 | いいえ | はい | いいえ | None | - | from直後に実行するコマンドを指定します。 |
| --run_extra_pre | 文字列 | いいえ | はい | いいえ | None | - | install_extraの実行前に実行するコマンドを指定します。 |
| --run_extra_post | 文字列 | いいえ | はい | いいえ | None | - | install_extraの実行後に実行するコマンドを指定します。 |
| --install_extra | 文字列 | いいえ | はい | いいえ | None | - | 追加でインストールするパッケージを指定します。 |
| --compose_path | ファイル | いいえ | いいえ | はい | None | - | `docker-compose.yml` ファイルを指定します。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: CmdboxServerInstall
- 役割: この機能の実行を行います  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 tm (float): 実行開始時間 pf (List[Dict[str, float]]): 呼出元のパフォーマンス情報  Returns: Tuple[int, Dict[str, Any], Any]: 終了コード, 結果, オブジェクト
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 処理フロー:
  - (st, msg, obj) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - ret に self.server_install の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: Feature
- 役割: この機能のサーバー側の実行を行います  Args: data_dir (Path): データディレクトリ logger (logging.Logger): ロガー redis_cli (redis_client.RedisClient): Redisクライアント msg (List[str]): 受信メッセージ sessions (Dict[str, Dict[str, Any]]): セッション情報  Returns: int: 終了コード
- 処理フロー:
  - 実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。

## 処理結果

- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: 抽出なし
- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]

## 主な補助メソッド

### server_install

- 実装元: CmdboxServerInstall
- 役割: cmdboxが含まれるdockerイメージをインストールします。  Args: logger (logging.Logger): ロガー args (argparse.Namespace): 引数 data (Path): cmdbox-serverのデータディレクトリ install_cmdbox_tgt (str): cmdboxのインストール元 install_from (str): インストール元dockerイメージ install_no_python (bool): pythonをインストールしない install_compile_python (bool): pythonをコンパイルしてインストール install_tag (str): インストールタグ install_use_gpu (bool): GPUを使用するモジュール構成でインストールします。 tts_engine (str): TTSエンジンの指定 voicevox_ver (str): VoiceVoxのバージョン voicevox_whl (str): VoiceVoxのwhlファイルの名前 init_extra (List[str]): from直後に実行するコマンド run_extra_pre (List[str]): install_extraの実行前に実行するコマンド run_extra_post (List[str]): install_extraの実行後に実行するコマンド install_extra (List[str]): 追加でインストールするパッケージ compose_path (str): docker-compose.ymlファイルパス language (str): 言語コード  Returns: dict: 処理結果
- 処理概要:
  - common.set_debug を呼び出す
  - 例外処理を伴って処理する。主な呼出: getpass.getuser, re.match, self.get_imgname, Path, common.cmd, dockerfile.unlink

## 単体テスト観点

- 選択肢を持つパラメータ install_no_python, install_compile_python, install_use_gpu, tts_engine, voicevox_ver, voicevox_whl, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ init_extra, run_extra_pre, run_extra_post, install_extra の 0 件・1 件・複数件入力を確認する
- 終了コード RESP_SUCCESS, RESP_WARN の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: /home/ubuntu/cmdbox/cmdbox/app/features/cli/cmdbox_cmdbox_server_install.py
- apprun 実装元: CmdboxServerInstall
- svrun 実装元: Feature
- 生成日時: 2026-04-26T00:53:06
