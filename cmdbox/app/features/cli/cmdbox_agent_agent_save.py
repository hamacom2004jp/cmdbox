from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, limiter, redis_client, resdata, validator
from cmdbox.app.options import Options
from cmdbox.app.features.cli import cmdbox_agent_agent_list
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic
import re


class AgentAgentSave(feature.OneshotResultEdgeFeature, validator.Validator, limiter.LimitedFeature):
    def __init__(self, appcls, ver, language = None):
        super().__init__(appcls, ver, language)
        self.agent_list = cmdbox_agent_agent_list.AgentAgentList(appcls, ver, language)

    def get_mode(self) -> Union[str, List[str]]:
        return 'agent'

    def get_cmd(self) -> str:
        return 'agent_save'

    def get_option(self) -> Dict[str, Any]:
        is_japan = common.is_japan(language=self.language)
        description = f"{self.ver.__appid__}に登録されているコマンド提供"
        description = description if is_japan else f"Provides commands registered in {self.ver.__appid__}"
        system_instruction = f"""<system_context>
役割：あなたは {self.ver.__appid__} Agent であり、{self.ver.__appid__} フレームワークに基づいて構築された高度な自律運用エンジニアです。あなたの主な目的は、{self.ver.__appid__}のカスタムコマンドを動的に調整・実行することで、自由度が高く、あらかじめ定義されていないユーザーのリクエストを解決することです。
プラットフォームの機能：{self.ver.__appid__}システムは、複数の環境（CLI、REST API、Webインターフェース、およびRedisを介したリモートワーカーサーバー）で動作します。社内ツールでは、これらのコマンド機能をModel Context Protocol（MCP）サーバーまたは生の実行可能インターフェースとして公開しています。
コグニティブゾーン：あらゆる問題に対して、プロのソフトウェアエンジニアとしての姿勢で取り組む必要があります。ローカルファイルシステムの検索、プロセスツール、データベース、LLMユーティリティを利用できます。パラメータを推測しようとせず、常に分析、検索、検証、実行を行ってください。
</system_context>

<execution_protocol>
すべての受信リクエストは、以下の順序に従って処理しなければなりません。

1. 分類とルーティング:
   - ユーザー入力を分析し、そのクエリが直接的な会話形式の質問（例：挨拶、一般的な概念の説明など）なのか、それともコマンド操作を必要とする機能的なタスクなのかを判断する。
   - 会話形式の場合は、質の高い専門的な文章で即座に返信する。ツールを起動してはならない。
   - 機能的なタスクの場合は、動的計画段階に入る。

2. 探検と発見:
   - メタデータコンテキストで利用可能なコマンドの一覧を確認し、該当する機能を探してください。
   - 候補となるツールが見つかったものの、詳細な使用方法がわからない場合は、MCPサーバーからツールの詳細情報を取得してください。ユーザーが指定していないパラメータを勝手に作成しようとしないでください。

3. 行動する前に考え、確認する:
   - いかなる機能ツール（特に破壊的またはシステムを変更するコマンド）を呼び出す前に、現在の状態を分析するために、必ず `<thinking>` XML ブロックを出力する必要があります。
   - 内なる独白の中で、明確な計画を立て、パラメータの型（整数か文字列か）を確認し、終了条件や成功条件を確立しなければなりません。

4. ステップバイステップのリアクトループ:
   - コマンドは1つずつ実行してください。複数の書き込みコマンドを無闇に連鎖させてはいけません。
   - 各 {self.ver.__appid__} コマンドの実行によって返される stdout/stderr または JSON ペイロードを必ず確認してください。
   - コマンドの実行結果は JSON 文字列で出力するようにしてください。この時 JSON 文字列は「```json」と「```」で囲んだ文字列にしてください。
   - もし出力内容に Markdown の構文が含まれている場合は、出力する前に JSON 文字列 に変換してください。この時、JSON 文字列は「```json」と「```」で囲んだ文字列にしてください。
   - コマンドが失敗した場合、自己修正ロジックを使用してください。思考ブロック内でエラーメッセージを分析し、オプションを変更して再試行してください。あるステップが 3 回連続で失敗した場合は、一旦停止し、オペレーターに指示を求めてください。

5. 応答の合成:
   - すべての出力を、ユーザーの入力言語（例：クエリが日本語の場合は日本語）に翻訳する。
   - ユーザーが求めている結果にコマンドのJSON文字列の実行結果が含まれる場合、前項の「```json」で「```」で囲んだ文字列は変更しないでください。
   - 最終結果は事実に基づく要約として提示し、曖昧なプレースホルダーや架空のログは避ける。
</execution_protocol>

<thinking_scratchpad_protocol>
`<thinking>` 出力を生成する場合は、以下の点に留意する必要があります:
- 現状チェックリスト：これまでに何が達成されたか？
- 検討中の制約事項：どのようなセキュリティパラメータやローカライズされたルールが指定されているか？
- コマンド生成チェック：生成された CLI コマンドの構造は、{self.ver.__appid__} の構文ガイドラインに準拠していますか？
- リスク軽減策：この操作は元に戻せますか？元に戻せない場合、ユーザーに確認しましたか、あるいはドライランを実施しましたか？
</thinking_scratchpad_protocol>

<formatting_and_style>
- 極めて専門的で、客観的かつ中立的な口調を保つこと。感情的な表現、謝罪、無駄な装飾は避けること。
- 構成の明瞭さを最優先すること。データの直接比較やパラメータのスキーマについては、Markdownの表を活用すること。
- 最終的な回答は、読みやすい文章で記述すること。厳密に順序立てられた技術的な手順を説明する場合を除き、箇条書きが密集した段落は避けること。
- 語彙は、標準的なシステム管理および情報技術の用語に合わせる。
</formatting_and_style>
"""
        system_instruction = system_instruction if is_japan else f"""<system_context>
Role: You are {self.ver.__appid__} Agent, an advanced autonomous operations engineer built on the {self.ver.__appid__}  framework. Your primary objective is to solve open-ended, non-predefined user requests by dynamically coordinating and executing {self.ver.__appid__} custom commands.
Platform Capabilities: The {self.ver.__appid__} system operates across multiple environments (CLI, RESTAPI, Web interface, and Redis-mediated remote worker servers). Your internal tools expose these command capabilities as Model Context Protocol (MCP) servers or raw executable interfaces.
Cognitive Zone: You must approach every problem as a professional software engineer. You have access to local filesystem search, process tools, databases, and LLM utilities. Do not attempt to guess parameters; always analyze, search, verify, and execute.
</system_context>

<execution_protocol>
You must process all incoming requests according to the following sequential protocol:

1. CLASSIFY & ROUTE:
   - Analyze the user input to determine if the query is a direct conversational question (e.g., greetings, general conceptual explanations) or a functional task requiring command operations.
   - If conversational, reply immediately with high-quality, professional prose. Do not invoke tools.
   - If functional, enter the dynamic planning phase.

2. EXPLORE & DISCOVER:
   - Review the list of available commands in your metadata context to find matching functionality.
   - If you have found a potential tool but are unsure how to use it in detail, please obtain detailed information about the tool from the MCP server. Do not attempt to create parameters on your own that the user has not specified.

3. THINK & VERIFY BEFORE ACTION:
   - Before calling any functional tools (especially commands that are destructive or modify the system), you must always output a `<thinking>` XML block to analyze the current state.
   - In your inner monologue, you must formulate a clear plan, verify the data types of the parameters (whether they are integers or strings), and establish the termination and success conditions.

4. STEP-BY-STEP REACT LOOP:
   - Execute commands one at a time. Never chain multiple write commands blindly.
   - Inspect the stdout/stderr or JSON payload returned by each {self.ver.__appid__} command execution.
   - Please output the results of the command as a JSON string. When doing so, enclose the JSON string in “```json” and “```”.
   - If the output contains Markdown syntax, please convert it to a JSON string before outputting it. When doing so, enclose the JSON string in “```json” and “```”.
   - If a command fails, use your self-correction logic: analyze the error message in your thinking block, modify the options, and retry. If a step fails 3 times consecutively, pause and ask the operator for guidance.

5. RESPONSE SYNTHESIS:
   - Translate all outputs back into the user's input language (e.g., Japanese, if the query is in Japanese).
   - If the content includes Markdown syntax, convert it to HTML before outputting it.
   - Present final results with factual summaries, avoiding vague placeholders or hallucinated logs.
</execution_protocol>

<thinking_scratchpad_protocol>
When generating `<thinking>` output, you must consider the following points:
- Current State Checklist: What has been accomplished so far?
- Constraints Under Review: What security parameters and localized rules have been specified?
- Command Generation Check: Does the generated CLI command structure align with {self.ver.__appid__} syntax guidelines?
- Risk Mitigations: Is this action reversible? If irreversible, have you confirmed with the user or performed dry-runs?
</thinking_scratchpad_protocol>

<formatting_and_style>
- Maintain a highly professional, objective, and neutral tone. No excitement, no apologies, no fluff.
- Prioritize structural clarity. Utilize Markdown tables for direct data comparisons or parameter schemas.
- Write smoothly flowing prose for final answers. Avoid dense, bulleted paragraphs unless expressing strictly sequential technical steps.
- Match your vocabulary to standard systems administration and information technology terminology.
</formatting_and_style>
"""
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="Agent 設定を保存します。",
            description_en="Saves agent configuration.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                    description_ja="Redisサーバーのサービスホストを指定します。",
                    description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                    description_ja="Redisサーバーのサービスポートを指定します。",
                    description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                    description_ja=f"Redisサーバーのアクセスパスワード(任意)を指定します。省略時は `{self.default_pass}` を使用します。",
                    description_en=f"Specify the access password of the Redis server (optional). If omitted, `{self.default_pass}` is used."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                    description_ja="サーバーのサービス名を指定します。省略時は `server` を使用します。",
                    description_en="Specify the service name of the inference server. If omitted, `server` is used."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                    description_ja="Redisサーバーへの再接続回数を指定します。0以下を指定すると永遠に再接続を行います。",
                    description_en="Specifies the number of reconnections to the Redis server.If less than 0 is specified, reconnection is forever."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                    description_ja="Redisサーバーに再接続までの秒数を指定します。",
                    description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default="60", required=False, multi=False, hide=True, choice=None,
                    description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                    description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="agent_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                    description_ja="保存するAgentの名前を指定します。",
                    description_en="Specify the name of the agent configuration to save."),
                dict(opt="agent_type", type=Options.T_STR, default='local', required=True, multi=False, hide=False,
                    choice=['local', 'remote'],
                    choice_show=dict(local=["llm", "mcpservers", "subagents", "agent_description", "agent_instruction", "prompt_param"],
                                     remote=["a2asv_baseurl", "a2asv_delegated_auth", "a2asv_apikey", "agent_description"]),
                    description_ja="Agentの種類を指定します。`local` または `remote` を指定します。",
                    description_en="Specify the agent type. Specify either `local` or `remote`."),
                dict(opt="use_planner", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[False, True],
                    description_ja="エージェントの計画機能を使用するかどうかを指定します。",
                    description_en="Specify whether to use the planning feature of the agent."),
                dict(opt="a2asv_baseurl", type=Options.T_STR, default="http://localhost:8071/a2a/<agent_name>", required=False, multi=False, hide=False, choice=None,
                    description_ja="A2A Serverの基本URLを指定します。",
                    description_en="Specify the base URL for the A2A Server."),
                dict(opt="a2asv_delegated_auth", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                    description_ja="A2A Serverの認証を現在のログインユーザーのAPI Keyを使用して行います。",
                    description_en="Authenticate the A2A Server using the API Key of the currently logged-in user.",),
                dict(opt="a2asv_apikey", type=Options.T_PASSWD, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="A2A Server起動時のAPI Keyを指定します。 また`a2asv_delegated_auth` が無効な場合は、Agent実行時に使用も使用されます。",
                    description_en="Specify the API Key when starting the A2A Server. Additionally, if `a2asv_delegated_auth` is disabled, it will also be used when running the Agent.",),
                dict(opt="llm", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('llm','list',{},(res)=>{"
                            + "const val = $(\"[name='llm']\").val();"
                            + "$(\"[name='llm']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='llm']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='llm']\").val(val);"
                            + "},$(\"[name='title']\").val(),'llm');"
                            + "}",
                    description_ja="Agentが参照するLLM設定名を指定します。",
                    description_en="Specify the LLM configuration name referenced by the Agent."),
                dict(opt="mcpservers", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('agent','mcpsv_list',{},(res)=>{"
                            + "const val = $(\"[name='mcpservers']\").val();"
                            + "$(\"[name='mcpservers']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{$(\"[name='mcpservers']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');});"
                            + "$(\"[name='mcpservers']\").val(val);"
                            + "},$(\"[name='title']\").val(),'mcpservers');"
                            + "}",
                    description_ja="Agentが利用するMCPサーバー名を指定します。",
                    description_en="Specify the MCP server name used by the Agent."),
                dict(opt="subagents", type=Options.T_STR, default=None, required=False, multi=True, hide=False, choice=[],
                    callcmd="async () => {await cmdbox.callcmd('agent','agent_list',{},(res)=>{"
                            + "const val = $(\"[name='subagents']\").val();"
                            + "$(\"[name='subagents']\").empty().append('<option></option>');"
                            + "res['data'].map(elm=>{"
                            + "  if (elm[\"name\"] === $(\"[name='agent_name']\").val()) return;"
                            + "  $(\"[name='subagents']\").append('<option value=\"'+elm[\"name\"]+'\">'+elm[\"name\"]+'</option>');"
                            + "});"
                            + "$(\"[name='subagents']\").val(val);"
                            + "},$(\"[name='title']\").val(),'subagents');"
                            + "}",
                    description_ja="Agentが利用するサブエージェント名を指定します。",
                    description_en="Specify the subagent name used by the agent."),
                dict(opt="agent_description", type=Options.T_TEXT, default=description, required=False, multi=False, hide=False, choice=None,
                    description_ja="Agentの能力に関する説明を指定します。モデルはこれを使用して、制御をエージェントに委譲するかどうかを決定します。一行の説明で十分であり、推奨されます。",
                    description_en="Specify a description of the agent's capabilities. The model uses this to determine whether to delegate control to the agent. A single line description is sufficient and recommended."),
                dict(opt="agent_instruction", type=Options.T_TEXT, default=None, required=False, multi=False, hide=False, choice=None,
                    description_ja="Agentが使用するLLMモデル向けの指示を指定します。これはエージェントの挙動を促すものになります。",
                    description_en="Specify instructions for the LLM model used by the agent. These will guide the agent's behavior."),
                dict(opt="agent_system_instruction", type=Options.T_TEXT, default=system_instruction, required=False, multi=False, hide=True, choice=None,
                    description_ja="サービス提供側がエンドユーザーに公開せずに内部的に設定するシステムプロンプトを指定します。`agent_instruction` と同様にAgentに渡されますが、こちらは非公開の設定です。",
                    description_en="Specify a system prompt set internally by the service provider without exposing it to end users. Like `agent_instruction`, it is passed to the Agent, but this one is private."),
                dict(opt="prompt_param", type=Options.T_DICT, default=None, required=False, multi=True, hide=False, choice=None,
                    description_ja="`agent_instruction` や `agent_system_instruction` に埋め込まれたプレースホルダーに対応するパラメータを指定します。例: `{\"key\": \"value\"}`",
                    description_en="Specify parameters corresponding to placeholders embedded in `agent_instruction` or `agent_system_instruction`. Example: `{\"key\": \"value\"}`"),
            ]
        )

    def list_mcvpservers(self, data_dir: str) -> List[str]:
        agent_dir = Path(data_dir) / ".agent"
        if not agent_dir.exists() or not agent_dir.is_dir():
            return []
        paths = agent_dir.glob("mcpsv-*.json")
        ret: List[str] = []
        for p in sorted(paths):
            name = p.name
            if not name.startswith('mcpsv-') or not name.endswith('.json'):
                continue
            svname = name[6:-5]
            ret.append(svname)
        return ret

    def list_llms(self, data_dir: str) -> List[str]:
        agent_dir = Path(data_dir) / ".agent"
        if not agent_dir.exists() or not agent_dir.is_dir():
            return []
        paths = agent_dir.glob("llm-*.json")
        ret: List[str] = []
        for p in sorted(paths):
            name = p.name
            if not name.startswith('llm-') or not name.endswith('.json'):
                continue
            llmname = name[4:-5]
            ret.append(llmname)
        return ret

    def list_agents(self, data_dir: str) -> List[str]:
        agent_dir = Path(data_dir) / ".agent"
        if not agent_dir.exists() or not agent_dir.is_dir():
            return []
        paths = agent_dir.glob("agent-*.json")
        ret: List[str] = []
        for p in sorted(paths):
            name = p.name
            if not name.startswith('agent-') or not name.endswith('.json'):
                continue
            svname = name[6:-5]
            ret.append(svname)
        return ret

    @limiter.apprun_check_limit
    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float, pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        if args.agent_type == 'local':
            if not hasattr(args, 'llm') or args.llm is None:
                msg = dict(warn="Please specify --llm for local agent")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
        elif args.agent_type == 'remote':
            if not hasattr(args, 'a2asv_baseurl') or args.a2asv_baseurl is None:
                msg = dict(warn="Please specify --a2asv_baseurl for remote agent")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None
        if not args.a2asv_delegated_auth and args.agent_type == 'remote' and (not getattr(args, 'a2asv_apikey', None) or args.a2asv_apikey is None):
            msg = dict(warn="Please specify --a2asv_apikey or enable --a2asv_delegated_auth")
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

        configure = dict(
            agent_name=args.agent_name,
            agent_type=args.agent_type,
            use_planner=args.use_planner if hasattr(args, 'use_planner') else False,
            a2asv_baseurl=args.a2asv_baseurl if hasattr(args, 'a2asv_baseurl') else None,
            a2asv_delegated_auth=args.a2asv_delegated_auth if hasattr(args, 'a2asv_delegated_auth') else False,
            a2asv_apikey=args.a2asv_apikey if hasattr(args, 'a2asv_apikey') else None,
            llm=args.llm if hasattr(args, 'llm') else None,
            mcpservers=list(set(args.mcpservers)) if hasattr(args, 'mcpservers') and args.mcpservers is not None else None,
            subagents=list(set(args.subagents)) if hasattr(args, 'subagents') and args.subagents is not None else None,
            agent_description=args.agent_description if hasattr(args, 'agent_description') else None,
            agent_instruction=args.agent_instruction if hasattr(args, 'agent_instruction') else None,
            agent_system_instruction=args.agent_system_instruction if hasattr(args, 'agent_system_instruction') else None,
            prompt_param=args.prompt_param if hasattr(args, 'prompt_param') else None,
        )

        payload_b64 = convert.str2b64str(common.to_str(configure))

        cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
        ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                    retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
        common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
        if 'success' not in ret:
            return self.RESP_WARN, ret, cl
        return self.RESP_SUCCESS, ret, cl

    def output_schema(self) -> type:
        class Data(resdata.Data):
            data: Union[str, None] = pydantic.Field(default=None, description="処理結果のデータ")
        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")
        return Result

    def is_cluster_redirect(self):
        return False

    @limiter.svrun_check_limit
    def svrun(self, data_dir:Path, logger:logging.Logger, redis_cli:redis_client.RedisClient, msg:List[str],
              sessions:Dict[str, Dict[str, Any]]) -> int:
        reskey = msg[1]
        try:
            configure = json.loads(convert.b64str2str(msg[2]))

            if configure['agent_type'] == 'local':
                if configure['llm'] is not None and configure['llm'] not in self.list_llms(data_dir):
                    msg = dict(warn=f"Specified LLM configuration '{configure['llm']}' not found.")
                    redis_cli.rpush(reskey, msg)
                    return self.RESP_WARN
                if configure['mcpservers'] is not None:
                    entries = self.list_mcvpservers(data_dir)
                    configure['mcpservers'] = list(set(configure['mcpservers']))
                    for m in configure['mcpservers']:
                        if m not in entries:
                            msg = dict(warn=f"Specified MCP server configuration '{m}' not found.")
                            redis_cli.rpush(reskey, msg)
                            return self.RESP_WARN
                if configure['subagents'] is not None:
                    configure['subagents'] = list(set(configure['subagents']))
                    entries = self.list_agents(data_dir)
                    for a in configure['subagents']:
                        if a not in entries:
                            msg = dict(warn=f"Specified subagent configuration '{a}' not found.")
                            redis_cli.rpush(reskey, msg)
                            return self.RESP_WARN
                        if a == configure['agent_name']:
                            msg = dict(warn=f"An agent cannot include itself as a subagent.")
                            redis_cli.rpush(reskey, msg)
                            return self.RESP_WARN

            name = configure.get('agent_name')
            configure_path = data_dir / ".agent" / f"agent-{name}.json"
            configure_path.parent.mkdir(parents=True, exist_ok=True)
            with configure_path.open('w', encoding='utf-8') as f:
                json.dump(configure, f, indent=4)
            msg = dict(success=f"Agent configuration saved to '{str(configure_path)}'.")
            redis_cli.rpush(reskey, msg)
            return self.RESP_SUCCESS

        except Exception as e:
            msg = dict(warn=f"{self.get_mode()}_{self.get_cmd()}: {e}")
            logger.warning(f"{self.get_mode()}_{self.get_cmd()}: {e}", exc_info=True)
            redis_cli.rpush(reskey, msg)
            return self.RESP_WARN

    def apprun_registrations(self, data_dir, logger, args, msg):
        raise NotImplementedError("In the Limiter settings, please use `scope=server`.")

    def svrun_registrations(self, data_dir, logger, opt, msg):
        agent_dir = data_dir / '.agent'
        count = 0
        if agent_dir.exists() and agent_dir.is_dir():
            paths = agent_dir.glob(f"agent-*.json")
            for p in sorted(paths):
                name = p.name
                if not name.startswith('agent-') or not name.endswith('.json'):
                    continue
                count += 1
        return count

    def init_test(self) -> None:
        """
        テスト用の初期化処理を行います
        """
        app_obj = self.appcls.getInstance(appcls=self.appcls, ver=self.ver)
        app_obj.main(args_list=[
            "-m", "llm", "-c", "save",
            "--llmname", "default_value",
            "--llmprov", "azureopenai",
        ])
        app_obj.main(args_list=[
            "-m", "llm", "-c", "save",
            "--llmname", "enabled_value",
            "--llmprov", "azureopenai",
        ])

    def cleaning_test(self) -> None:
        """
        テスト用のクリーンアップ処理を行います
        """
        app_obj = self.appcls.getInstance(appcls=self.appcls, ver=self.ver)
        app_obj.main(args_list=[
            "-m", "llm", "-c", "del",
            "--llmname", "default_value",
        ])
        app_obj.main(args_list=[
            "-m", "llm", "-c", "del",
            "--llmname", "enabled_value",
        ])
