from cmdbox.app import common, client, feature, options
from cmdbox.app.features.cli import cmdbox_llm_chat, cmdbox_datasource_load
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import logging
import json
import sys
import re


class AgentBase(feature.ResultEdgeFeature):
    def __init__(self, appcls, ver, language:str=None):
        super().__init__(appcls, ver, language=language)
        self.llm_chat = cmdbox_llm_chat.LLMChat(appcls, ver, language=language)
        self.ds_load = cmdbox_datasource_load.DatasourceLoad(appcls, ver, language=language)
        is_japan = common.is_japan(language=self.language)
        self.agent_description = f"{self.ver.__appid__}に登録されているコマンド提供"
        self.agent_description = self.agent_description if is_japan else f"Provides commands registered in {self.ver.__appid__}"
        self.agent_system_instruction = f"""<system_context>
役割：
  - あなたは {self.ver.__appid__} Agent であり、{self.ver.__appid__} フレームワークに基づいて構築された高度な自律運用エンジニアです。
  - あなたの主な目的は、{self.ver.__appid__}のカスタムコマンドを動的に調整・実行することで、自由度が高く、あらかじめ定義されていないユーザーのリクエストを解決することです。
プラットフォームの機能：
  - {self.ver.__appid__}システムは、複数の環境（CLI、REST API、Webインターフェース、およびRedisを介したリモートワーカーサーバー）で動作します。
  - 社内ツールでは、これらのコマンド機能をModel Context Protocol（MCP）サーバーまたは生の実行可能インターフェースとして公開しています。
コグニティブゾーン：
  - あらゆる問題に対して、プロのソフトウェアエンジニアとしての姿勢で取り組む必要があります。
  - ローカルファイルシステムの検索、プロセスツール、データベース、LLMユーティリティを利用できます。
  - パラメータを推測しようとせず、常に分析、検索、検証、実行を行ってください。
</system_context>

<execution_protocol>
すべての受信リクエストは、以下の順序に従って処理しなければなりません。
1. 分類とルーティング:
  - ユーザー入力を分析し、そのクエリが直接的な会話形式の質問（例：挨拶、一般的な概念の説明など）なのか、それともコマンド操作を必要とする機能的なタスクなのかを判断する。
  - 会話形式の場合は、質の高い専門的な文章で即座に返信する。ツールを起動してはならない。
  - 機能的なタスクの場合は、動的計画段階に入る。
2. 探検と発見:
  - メタデータコンテキストで利用可能なコマンドの一覧を確認し、該当する機能を探してください。
  - 候補となるツールが見つかったものの、詳細な使用方法がわからない場合は、MCPサーバーからツールの詳細情報を取得してください。
  - ユーザーが指定していないパラメータを勝手に作成しようとしないでください。
3. 行動する前に考え、確認する:
  - いかなる機能ツール（特に破壊的またはシステムを変更するコマンド）を呼び出す前に、現在の状態を分析するために、必ず `<thinking>` XML ブロックを出力する必要があります。
  - 内なる独白の中で、明確な計画を立て、パラメータの型（整数か文字列か）を確認し、終了条件や成功条件を確立しなければなりません。
4. ステップバイステップのリアクトループ:
  - コマンドは1つずつ実行してください。複数の書き込みコマンドを無闇に連鎖させてはいけません。
  - 各 {self.ver.__appid__} コマンドの実行によって返される stdout/stderr または JSON ペイロードを必ず確認してください。
  - コマンドが失敗した場合、自己修正ロジックを使用してください。思考ブロック内でエラーメッセージを分析し、オプションを変更して再試行してください。
  - あるステップが 3 回連続で失敗した場合は、一旦停止し、オペレーターに指示を求めてください。
5. 応答の合成:
  - すべての出力を、ユーザーの入力言語（例：クエリが日本語の場合は日本語）に翻訳する。
  - ユーザーが求めている結果にコマンドのJSON文字列の実行結果が含まれる場合、文字列は変更しないでください。
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
        self.agent_system_instruction = self.agent_system_instruction if is_japan else f"""<system_context>
Role: 
  - You are a {self.ver.__appid__} Agent, an advanced autonomous operations engineer built on the {self.ver.__appid__} framework. 
  - Your primary objective is to resolve highly flexible, non-predefined user requests by dynamically adapting and executing {self.ver.__appid__} custom commands.
Platform Features:
  - The {self.ver.__appid__} system operates across multiple environments (CLI, REST API, web interface, and remote worker servers via Redis).
  - Internal tools expose these command capabilities as a Model Context Protocol (MCP) server or a raw executable interface.
Cognitive Zone:
  - You must approach every problem with the mindset of a professional software engineer.
  - You can utilize local filesystem search, process tools, databases, and LLM utilities.
  - Do not attempt to guess parameters; always analyze, search, verify, and execute.
</system_context>

<execution_protocol>
All incoming requests must be processed in the following order:
1. Classification and Routing:
  - Analyze user input to determine whether the query is a direct conversational question (e.g., a greeting, an explanation of a general concept, etc.) or a functional task requiring a command-based operation.
  - If it is a conversational query, respond immediately with high-quality, professional text. Do not launch any tools.
  - If it is a functional task, proceed to the dynamic planning phase.
2. Exploration and Discovery:
  - Check the list of available commands in the metadata context and search for the relevant feature.
  - If a candidate tool is found but you do not know how to use it in detail, retrieve detailed information about the tool from the MCP server.
  - Do not attempt to create parameters on your own that the user has not specified.
3. Think and Verify Before Acting:
  - Before invoking any functional tool (especially destructive or system-altering commands), you must always output a `<thinking>` XML block to analyze the current state.
  - In your inner monologue, you must formulate a clear plan, verify the parameter types (integer or string), and establish termination and success conditions.
4. Step-by-Step Reactor Loop:
  - Execute commands one at a time. Do not chain multiple write commands indiscriminately.
  - Be sure to check the stdout/stderr or JSON payload returned by the execution of each {self.ver.__appid__} command.
  - If a command fails, use self-correcting logic. Analyze the error message within the thought block, adjust the options, and retry.
  - If a step fails three times in a row, pause and ask the operator for instructions.
5. Response Synthesis:
  - Translate all output into the user’s input language (e.g., Japanese if the query is in Japanese).
  - If the command’s JSON output contains the result the user is seeking, do not modify the string.
  - Present the final result as a fact-based summary, avoiding ambiguous placeholders or fictional logs.
</execution_protocol>

<thinking_scratchpad_protocol>
`<thinking>` When generating output, keep the following points in mind:
  - Current Status Checklist: What has been accomplished so far?
  - Constraints Under Consideration: What security parameters and localized rules have been specified?
  - Command Generation Check: Does the structure of the generated CLI command comply with the syntax guidelines for {self.ver.__appid__}?
  - Risk mitigation measures: Is this operation reversible? If not, have you confirmed this with the user or performed a dry run?
</thinking_scratchpad_protocol>

<formatting_and_style>
  - Maintain an extremely professional, objective, and neutral tone. Avoid emotional language, apologies, and unnecessary embellishments.
  - Prioritize clarity of structure. Use Markdown tables for direct comparisons of data and parameter schemas.
  - Write the final answer in easy-to-read prose. Avoid paragraphs densely packed with bullet points, except when explaining strictly ordered technical procedures.
  - Use vocabulary consistent with standard system administration and information technology terminology.
</formatting_and_style>
"""

    def load_conf(self, runner_name:str, data_dir:Path, logger:logging.Logger):
        runner_conf_path = data_dir / ".agent" / f"runner-{runner_name}.json"
        if not runner_conf_path.exists():
            raise FileNotFoundError(f"Specified runner configuration '{runner_name}' not found on server at '{str(runner_conf_path)}'.")
        with runner_conf_path.open('r', encoding='utf-8') as f:
            runner_conf = json.load(f)

        agent_conf = self._load_agent_config(data_dir, runner_conf['agent'])
        if agent_conf.get('llm', None) is not None:
            llm_conf = self._load_llm_config(data_dir, agent_conf['llm'])
        else:
            llm_conf = {}

        if agent_conf.get('mcpservers', None) is not None:
            mcpsv_confs = self._load_mcpsv_config(data_dir, agent_conf['mcpservers'])
        else:
            mcpsv_confs = []
        
        if runner_conf.get('session_datasource', None) is not None:
            ds_conf = self._load_ds_config(data_dir, runner_conf['session_datasource'])
        else:
            ds_conf = {}
        if 'db_fullpath' not in ds_conf or not ds_conf['db_fullpath']:
            if 'db_path' in ds_conf and ds_conf['db_path']:
                db_path = str(ds_conf['db_path'])
                db_path = db_path.replace("\\","/").replace("//","/") if db_path else None
                db_path = db_path[1:] if db_path and db_path.startswith('/') else db_path
                ds_conf['db_fullpath'] = str((data_dir / db_path).resolve()) if db_path else None

        return runner_conf, agent_conf, llm_conf, mcpsv_confs, ds_conf

    def _load_agent_config(self, data_dir:Path, agent_name:str) -> Dict[str, Any]:
        agent_conf_path = data_dir / ".agent" / f"agent-{agent_name}.json"
        if not agent_conf_path.exists():
            raise FileNotFoundError(f"Specified agent configuration '{agent_name}' not found on server at '{str(agent_conf_path)}'.")
        with agent_conf_path.open('r', encoding='utf-8') as f:
            agent_conf = json.load(f)
        return agent_conf

    def _load_llm_config(self, data_dir:Path, llm_name:str) -> Dict[str, Any]:
        llm_conf_path = data_dir / ".agent" / f"llm-{llm_name}.json"
        if not llm_conf_path.exists():
            raise FileNotFoundError(f"Specified llm configuration '{llm_name}' not found on server at '{str(llm_conf_path)}'.")
        with llm_conf_path.open('r', encoding='utf-8') as f:
            llm_conf = json.load(f)
        return llm_conf

    def _load_mcpsv_config(self, data_dir:Path, mcpservers:List[str]) -> List[Dict[str, Any]]:
        mcpsv_confs = []
        if isinstance(mcpservers, list):
            for mcpsv_name in mcpservers:
                mcpsv_conf_path = data_dir / ".agent" / f"mcpsv-{mcpsv_name}.json"
                if not mcpsv_conf_path.exists():
                    raise FileNotFoundError(f"Specified MCP server configuration '{mcpsv_name}' not found on server at '{str(mcpsv_conf_path)}'.")
                with mcpsv_conf_path.open('r', encoding='utf-8') as f:
                    mcpsv_conf = json.load(f)
                    mcpsv_confs.append(mcpsv_conf)
        return mcpsv_confs

    def _load_ds_config(self, data_dir:Path, dsname:str) -> Dict[str, Any]:
        ds_conf = self.ds_load.load_datasource(data_dir, dsname)
        return ds_conf

    def create_session_service(self, *, logger:logging.Logger, data_dir:Path, ds_conf:Dict[str, Any]) -> Any:
        """
        セッションサービスを作成します

        Args:
            logger (logging.Logger): ロガー
            data_dir (Path): データディレクトリ
            ds_conf (Dict[str, Any]): データソースの設定

        Returns:
            BaseSessionService: セッションサービス
        """
        if ds_conf.get('dbtype') == 'sqlite':
            if sys.platform == 'win32':
                uri = Path(ds_conf['db_fullpath']).as_uri()
                agent_session_dburl = f"sqlite+aiosqlite:{uri.replace('file:///', '///')}"
            else:
                db_path = Path(ds_conf['db_fullpath']).resolve().as_posix()
                agent_session_dburl = f"sqlite+aiosqlite:////{db_path.lstrip('/')}"
        elif ds_conf.get('dbtype') == 'postgresql':
            agent_session_dburl = f"postgresql+psycopg://{ds_conf['pguser']}:{ds_conf['pgpass']}@{ds_conf['pghost']}:{ds_conf['pgport']}/{ds_conf['pgdbname']}"
        else:
            agent_session_dburl = None
        from google.adk.sessions import InMemorySessionService
        from google.adk.sessions.database_session_service import DatabaseSessionService
        if agent_session_dburl is not None:
            logger.info(f"Using DatabaseSessionService: {agent_session_dburl}")
            dss = DatabaseSessionService(db_url=agent_session_dburl)
            return dss
        else:
            logger.info(f"Using InMemorySessionService")
            return InMemorySessionService()

    async def create_agent_session(self, *, session_service:Any, runner_name:str, user_name:str, session_id:str=None) -> Any:
        """
        セッションを作成します

        Args:
            session_service (BaseSessionService): セッションサービス
            runner_name (str): ランナー名
            user_name (str): ユーザー名
            session_id (str): セッションID

        Returns:
            Any: セッション
        """
        if session_id is None:
            session_id = common.random_string(32)
        try:
            session = await session_service.get_session(app_name=runner_name, user_id=user_name, session_id=session_id)
            if session is None:
                session = await session_service.create_session(app_name=runner_name, user_id=user_name, session_id=session_id)
            return session
        except NotImplementedError:
            # セッションが１件もない場合はNotImplementedErrorが発生することがある
            session = await session_service.create_session(app_name=runner_name, user_id=user_name, session_id=session_id)
            return session

    @classmethod
    def apply_prompt_param(cls, text: str, prompt_param: Dict[str, Any]) -> str:
        """
        テキスト中のプレースホルダーを prompt_param の値で置換します

        Args:
            text (str): 置換対象のテキスト
            prompt_param (Dict[str, Any]): プレースホルダーに対応するパラメータ

        Returns:
            str: 置換後のテキスト
        """
        if text is None or not prompt_param:
            return text
        try:
            return text.format_map(prompt_param)
        except (KeyError, ValueError):
            return text

    @classmethod
    def gen_msg(cls, event:Any) -> Tuple[str, bool, bool, bool, int]:
        msg = None
        is_func_call = False
        is_func_response = False
        is_final_response = False
        st = cls.RESP_SUCCESS
        calls = event.get_function_calls()
        responses = event.get_function_responses()
        is_func_call = bool(calls)
        is_func_response = bool(responses)
        is_final_response = event.is_final_response()
        if event.content and event.content.parts:
            msg = "\n".join([p.text for p in event.content.parts
                             if p and p.text and not getattr(p, 'thought', False)])
        elif event.actions and event.actions.escalate:
            msg = f"Agent escalated: {event.error_message or 'No specific message.'}"
        if event.error_message:
            msg = msg if msg else ""
            msg = f"{event.error_code if event.error_code else ''}"
            msg = f"{msg} {event.error_message if event.error_message else ''}".strip()
            st = cls.RESP_WARN
        return msg, is_func_call, is_func_response, is_final_response, st
