# agent agent_save

## 基本情報

| 項目 | 内容 |
| --- | --- |
| mode | agent |
| cmd | agent_save |
| クラス | AgentAgentSave |
| モジュール | cmdbox.app.features.cli.cmdbox_agent_agent_save |
| 実装ファイル | F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_agent_save.py |
| 継承元 | OneshotResultEdgeFeature, ResultEdgeFeature, Validator, Feature |
| Redis | 必須 |
| Web モード禁止 | いいえ |
| Agent 利用 | いいえ |
| クラスタ転送 | False |

## 概要

- 日本語: Agent 設定を保存します。
- 英語: Saves agent configuration.

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
| --agent_name | 文字列 | はい | いいえ | いいえ | None | - | 保存するAgentの名前を指定します。 |
| --agent_type | 文字列 | はい | いいえ | いいえ | local | , local, remote | Agentの種類を指定します。`local` または `remote` を指定します。 |
| --use_planner | 真偽値 | いいえ | いいえ | いいえ | false | False, True | エージェントの計画機能を使用するかどうかを指定します。 |
| --a2asv_baseurl | 文字列 | いいえ | いいえ | いいえ | http://localhost:8071/a2a/<agent_name> | - | A2A Serverの基本URLを指定します。 |
| --a2asv_delegated_auth | 真偽値 | いいえ | いいえ | いいえ | false | True, False | A2A Serverの認証を現在のログインユーザーのAPI Keyを使用して行います。 |
| --a2asv_apikey | パスワード | いいえ | いいえ | いいえ | None | - | A2A Server起動時のAPI Keyを指定します。 また`a2asv_delegated_auth` が無効な場合は、Agent実行時に使用も使用されます。 |
| --llm | 文字列 | はい | いいえ | いいえ | None | - | Agentが参照するLLM設定名を指定します。 |
| --mcpservers | 文字列 | いいえ | はい | いいえ | None | - | Agentが利用するMCPサーバー名を指定します。 |
| --subagents | 文字列 | いいえ | はい | いいえ | None | - | Agentが利用するサブエージェント名を指定します。 |
| --agent_description | 複数行文字列 | いいえ | いいえ | いいえ | cmdboxに登録されているコマンド提供 | - | Agentの能力に関する説明を指定します。モデルはこれを使用して、制御をエージェントに委譲するかどうかを決定します。一行の説明で十分であり、推奨されます。 |
| --agent_instruction | 複数行文字列 | いいえ | いいえ | いいえ | あなたはコマンドの意味を熟知しているエキスパートです。ユーザーがコマンドを実行したいとき、あなたは以下の手順に従ってコマンドを確実に実行してください。<br>1. ユーザーのクエリからが実行したいコマンドを特定します。<br>2. コマンド実行に必要なパラメータのなかで、ユーザーのクエリから取得できないものは、特にパラメータを指定せず実行してください。<br>3. もしエラーが発生した場合は、ユーザーにコマンド名とパラメータとエラー内容を提示してください。<br>4. コマンドの実行結果は、json文字列で出力するようにしてください。この時json文字列は「```json」と「```」で囲んだ文字列にしてください。<br> | - | Agentが使用するLLMモデル向けの指示を指定します。これはエージェントの挙動を促すものになります。 |
| -o, --output_json | ファイル | いいえ | いいえ | はい | None | - | 処理結果jsonの保存先ファイルを指定。 |
| -a, --output_json_append | 真偽値 | いいえ | いいえ | はい | false | True, False | 処理結果jsonファイルを追記保存します。 |
| --stdout_log | 真偽値 | いいえ | いいえ | はい | true | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をConsole logに出力します。 |
| --capture_stdout | 真偽値 | いいえ | いいえ | はい | false | True, False | GUIモードでのみ使用可能です。コマンド実行時の標準出力をキャプチャーし、実行結果画面に表示します。 |
| --capture_maxsize | 整数 | いいえ | いいえ | はい | 10485760 | - | GUIモードでのみ使用可能です。コマンド実行時の標準出力の最大キャプチャーサイズを指定します。 |

## 処理内容

### apprun

- 実装元: AgentAgentSave
- 終了コード候補: RESP_SUCCESS, RESP_WARN
- 結果キー候補: warn
- 処理フロー:
  - (st, msg, obj) に self.valid の結果を格納する
  - 条件 st != self.RESP_SUCCESS を満たす場合は早期終了し、RESP_SUCCESS
  - 条件 not re.match('^[\\w\\-]+$', args.agent_name) を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 args.agent_type == 'local' を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - 条件 not args.a2asv_delegated_auth and args.agent_type == 'remote' and (not getattr(args, 'a2asv_apike... を満たす場合は早期終了し、RESP_WARN。結果キー: warn
  - configure に dict の結果を格納する
  - payload_b64 に convert.str2b64str の結果を格納する
  - cl に client.Client の結果を格納する
  - ret に cl.redis_cli.send_cmd の結果を格納する
  - common.print_format を呼び出す
  - 条件 'success' not in ret を満たす場合は早期終了し、RESP_WARN
  - 終了コード RESP_SUCCESS を返却する

### svrun

- 実装元: AgentAgentSave
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

### cleaning_test

- 実装元: AgentAgentSave
- 役割: テスト用のクリーンアップ処理を行います
- 処理概要:
  - app_obj に self.appcls.getInstance の結果を格納する
  - app_obj.main を呼び出す
  - app_obj.main を呼び出す

### init_test

- 実装元: AgentAgentSave
- 役割: テスト用の初期化処理を行います
- 処理概要:
  - app_obj に self.appcls.getInstance の結果を格納する
  - app_obj.main を呼び出す
  - app_obj.main を呼び出す

### list_agents

- 実装元: AgentAgentSave
- 処理概要:
  - 条件 not agent_dir.exists() or not agent_dir.is_dir() を満たす場合は早期終了し、戻り値あり
  - paths に agent_dir.glob の結果を格納する
  - sorted(paths) を走査し、p ごとに処理する。主な呼出: sorted, ret.append, name.startswith, name.endswith
  - ret を返却する

### list_llms

- 実装元: AgentAgentSave
- 処理概要:
  - 条件 not agent_dir.exists() or not agent_dir.is_dir() を満たす場合は早期終了し、戻り値あり
  - paths に agent_dir.glob の結果を格納する
  - sorted(paths) を走査し、p ごとに処理する。主な呼出: sorted, ret.append, name.startswith, name.endswith
  - ret を返却する

### list_mcvpservers

- 実装元: AgentAgentSave
- 処理概要:
  - 条件 not agent_dir.exists() or not agent_dir.is_dir() を満たす場合は早期終了し、戻り値あり
  - paths に agent_dir.glob の結果を格納する
  - sorted(paths) を走査し、p ごとに処理する。主な呼出: sorted, ret.append, name.startswith, name.endswith
  - ret を返却する

## 単体テスト観点

- 必須パラメータ agent_name, llm が不足した場合の警告応答を確認する
- 選択肢を持つパラメータ agent_type, use_planner, a2asv_delegated_auth, output_json_append, stdout_log, capture_stdout の境界値と不正値を確認する
- 複数値パラメータ mcpservers, subagents の 0 件・1 件・複数件入力を確認する
- 結果オブジェクトのキー warn, success が期待どおり構成されることを確認する
- 終了コード RESP_SUCCESS, RESP_WARN, INT_1, INT_2 の到達条件をそれぞれ検証する

## ソース参照

- 実装ファイル: F:/devenv/cmdbox/cmdbox/app/features/cli/cmdbox_agent_agent_save.py
- apprun 実装元: AgentAgentSave
- svrun 実装元: AgentAgentSave
- 生成日時: 2026-04-19T20:59:05
