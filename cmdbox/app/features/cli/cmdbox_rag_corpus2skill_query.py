from pathlib import Path
from typing import Dict, Any, Tuple, List, Union
import argparse
import logging
import json
import pydantic
import sys
import time
import re

# Initialize sys.path for corpus2skill imports before importing from Corpus2Skill
_corpus2skill_root = Path(__file__).parent / "Corpus2Skill"
if str(_corpus2skill_root) not in sys.path:
    sys.path.insert(0, str(_corpus2skill_root))

from cmdbox.app import common, client, feature
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.features.cli import cmdbox_llm_chat
from cmdbox.app.options import Options


class RagCorpus2skillQuery(feature.OneshotResultEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language):
        super().__init__(appcls, ver, language)
        self.llm_chat = cmdbox_llm_chat.LLMChat(self.appcls, self.ver, self.language)
        self._prompt_cache = {}

    """
    Corpus2Skillのクエリコマンド：スキル階層をナビゲートして質問に回答します。

    Redis経由でサーバー側で実行します。
    """

    def get_mode(self) -> Union[str, List[str]]:
        """
        実行モードを取得します。

        Returns:
            str: 'rag'モード
        """
        return 'rag'

    def get_cmd(self) -> str:
        """
        コマンド名を取得します。

        Returns:
            str: 'corpus2skill_query'コマンド
        """
        return 'corpus2skill_query'

    def get_option(self) -> Dict[str, Any]:
        """
        コマンドの実行オプションを取得します。

        Corpus2Skillクエリ処理に必要な各種オプション（ホスト、ポート、RAGコーパス名、
        質問テキスト、LLMモデル名など）を定義して返します。

        Returns:
            Dict[str, Any]: オプション定義を含む辞書
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="Corpus2Skillのコンパイル済みスキル階層に対して質問を実行し、回答を生成します。",
            description_en="Execute a query against the compiled Corpus2Skill hierarchy and generate an answer.",
            choice=[
                dict(opt="host", type=Options.T_STR, default=self.default_host, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスホストを指定します。",
                     description_en="Specify the service host of the Redis server."),
                dict(opt="port", type=Options.T_INT, default=self.default_port, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja="Redisサーバーのサービスポートを指定します。",
                     description_en="Specify the service port of the Redis server."),
                dict(opt="password", type=Options.T_PASSWD, default=self.default_pass, required=True, multi=False, hide=True, choice=None, web="mask",
                     description_ja=f"Redisサーバーのアクセスパスワードを指定します。",
                     description_en=f"Specify the access password of the Redis server."),
                dict(opt="svname", type=Options.T_STR, default=self.default_svname, required=True, multi=False, hide=True, choice=None, web="readonly",
                     description_ja="サーバーのサービス名を指定します。",
                     description_en="Specify the service name of the inference server."),
                dict(opt="retry_count", type=Options.T_INT, default=3, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーへの再接続回数を指定します。",
                     description_en="Specifies the number of reconnections to the Redis server."),
                dict(opt="retry_interval", type=Options.T_INT, default=5, required=False, multi=False, hide=True, choice=None,
                     description_ja="Redisサーバーに再接続までの秒数を指定します。",
                     description_en="Specifies the number of seconds before reconnecting to the Redis server."),
                dict(opt="timeout", type=Options.T_INT, default=600, required=False, multi=False, hide=True, choice=None,
                     description_ja="サーバーの応答が返ってくるまでの最大待ち時間を指定。",
                     description_en="Specify the maximum waiting time until the server responds."),
                dict(opt="ragcorpus_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="クエリ対象のRAGコーパス名を指定します。スキル階層はdata_dir/.ragcorpus/<ragcorpus_name>から読み込まれます。",
                     description_en="Specify the RAG corpus name to query. The skill hierarchy will be loaded from data_dir/.ragcorpus/<ragcorpus_name>."),
                dict(opt="query", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="実行するクエリ（質問）を指定します。",
                     description_en="Specify the query (question) to execute."),
                dict(opt="llmname", type=Options.T_STR, default="claude-3-5-sonnet-20241022", required=False, multi=False, hide=False, choice=None,
                     description_ja="回答生成に使用するLLMモデル名を指定します。",
                     description_en="Specify the LLM model name for answer generation."),
                dict(opt="max_turns", type=Options.T_INT, default=10, required=False, multi=False, hide=False, choice=None,
                     description_ja="エージェントの最大ターン数を指定します。",
                     description_en="Specify the maximum number of agent turns."),
            ]
        )

    def is_cluster_redirect(self):
        """
        クラスタリダイレクト機能が有効かどうかを判定します。

        Returns:
            bool: False（このコマンドではクラスタリダイレクト無効）
        """
        return False

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float,
               pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        """
        クライアント側の実行処理：Redis経由でサーバーにペイロードを送信します。

        引数の検証を行い、Corpus2Skillクエリ処理をサーバー側で実行するための
        ペイロードをRedis経由で送信します。

        Args:
            logger: ログ出力用のロガーオブジェクト
            args: コマンドライン引数を含むArgumentsオブジェクト
            tm: 処理開始時刻（タイムスタンプ）
            pf: パフォーマンスプロファイル情報（デフォルト：空リスト）

        Returns:
            Tuple[int, Dict[str, Any], Any]: （ステータスコード、結果辞書、Clientオブジェクト）
        """
        try:
            payload = dict(
                ragcorpus_name=str(args.ragcorpus_name),
                query=str(args.query),
                llmname=str(args.llmname) if args.llmname else "claude-3-5-sonnet-20241022",
                max_turns=int(args.max_turns) if args.max_turns else 10,
            )
            payload_b64 = convert.str2b64str(common.to_str(payload))

            cl = client.Client(logger, redis_host=args.host, redis_port=args.port, redis_password=args.password, svname=args.svname)
            ret = cl.redis_cli.send_cmd(self.get_svcmd(), [payload_b64],
                                        retry_count=args.retry_count, retry_interval=args.retry_interval, timeout=args.timeout, nowait=False)
            common.print_format(ret, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            if 'success' not in ret:
                return self.RESP_WARN, ret, cl
            return self.RESP_SUCCESS, ret, cl

        except Exception as e:
            logger.warning(f"corpus2skill_query apprun failed: {e}", exc_info=True)
            msg = dict(warn=dict(message=str(e)))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        """
        サーバー側の実行処理：実際のクエリ処理を実行します。

        ドキュメントコーパスとエンティティインデックスを読み込み、マルチターンエージェントで
        クエリを処理してスキル階層を探索し、質問に対する回答を生成します。

        Args:
            data_dir: サーバーのデータディレクトリパス
            logger: ログ出力用のロガーオブジェクト
            redis_cli: Redisクライアント
            msg: Redisメッセージ（ペイロード情報を含む）
            sessions: セッション情報辞書

        Returns:
            int: 処理ステータスコード
        """
        reskey = msg[1]
        try:
            payload = json.loads(convert.b64str2str(msg[2]))

            ragcorpus_name = payload.get('ragcorpus_name')
            ragcorpus_dir = data_dir / '.ragcorpus' / ragcorpus_name
            query_text = payload.get('query', '')
            llmname = payload.get('llmname', 'claude-3-5-sonnet-20241022')
            max_turns = payload.get('max_turns', 10)

            logger.info(f"Executing query: {query_text}")
            logger.info(f"Using output directory: {ragcorpus_dir}")

            # コンパイル出力ディレクトリの検証
            skills_dir = ragcorpus_dir / ".claude" / "skills"
            documents_json = ragcorpus_dir / "documents.json"

            if not skills_dir.exists():
                msg_result = dict(warn=f"Skills directory not found: {skills_dir}")
                redis_cli.rpush(reskey, msg_result)
                return self.RESP_WARN

            if not documents_json.exists():
                msg_result = dict(warn=f"Documents file not found: {documents_json}")
                redis_cli.rpush(reskey, msg_result)
                return self.RESP_WARN

            # ドキュメントコーパスを読み込み
            doc_store = self._load_doc_store(ragcorpus_dir)
            logger.info(f"Loaded {len(doc_store)} documents")

            # ドキュメントメタデータを読み込み（元ファイルのパス情報を含む）
            doc_metadata = self._load_doc_metadata(ragcorpus_dir)
            logger.info(f"Loaded metadata for {len(doc_metadata)} documents")

            # エンティティインデックスを読み込み
            entity_index = self._load_entity_index(ragcorpus_dir)
            logger.info(f"Loaded {len(entity_index)} entities")

            # クエリ実行（マルチターンエージェント）
            answer, usage_info = self._execute_query(data_dir,
                query_text, skills_dir, ragcorpus_dir, doc_store, doc_metadata, entity_index,
                llmname, max_turns, logger
            )

            turns=usage_info.get('turns', [])
            del usage_info['turns']
            msg_result = dict(
                success=dict(
                    message="Query executed successfully",
                    answer=answer,
                    query=query_text,
                    usage=usage_info,
                    turns=turns,
                )
            )
            redis_cli.rpush(reskey, msg_result)
            return self.RESP_SUCCESS

        except Exception as e:
            logger.warning(f"corpus2skill_query svrun failed: {e}", exc_info=True)
            msg_result = dict(warn=f"corpus2skill_query: {e}")
            redis_cli.rpush(reskey, msg_result)
            return self.RESP_WARN

    # === ヘルパーメソッド ===

    def _load_doc_store(self, ragcorpus_dir: Path) -> Dict[str, str]:
        """
        documents.jsonファイルからドキュメントコーパスを読み込みます。

        RAGコーパスディレクトリに含まれるdocuments.jsonファイルを読み込み、
        ドキュメントID -> テキスト内容の辞書として返します。

        Args:
            ragcorpus_dir: RAGコーパスのディレクトリパス

        Returns:
            Dict[str, str]: {doc_id: doc_text, ...}形式のドキュメント辞書
        """
        doc_store = {}
        documents_json = ragcorpus_dir / "documents.json"

        try:
            if documents_json.exists():
                with open(documents_json, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        doc_store = data
        except Exception as e:
            pass

        return doc_store

    def _load_doc_metadata(self, ragcorpus_dir: Path) -> Dict[str, Dict[str, Any]]:
        """
        doc_metadata.jsonファイルからドキュメントメタデータを読み込みます。

        RAGコーパスディレクトリに含まれるdoc_metadata.jsonファイルから、
        ドキュメントID -> メタデータ（元ファイルのパスなど）の辞書として返します。

        Args:
            ragcorpus_dir: RAGコーパスのディレクトリパス

        Returns:
            Dict[str, Dict[str, Any]]: {doc_id: {"source_file": ..., "format": ...}, ...}形式のメタデータ辞書
        """
        doc_metadata = {}
        metadata_file = ragcorpus_dir / "doc_metadata.json"

        try:
            if metadata_file.exists():
                with open(metadata_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if isinstance(data, dict):
                        doc_metadata = data
        except Exception as e:
            pass

        return doc_metadata

    def _load_entity_index(self, ragcorpus_dir: Path) -> Dict[str, List[str]]:
        """
        entity_index.jsonファイルを読み込みます。

        RAGコーパスディレクトリに含まれるentity_index.jsonファイルから、
        エンティティ -> スキルIDのマッピングを読み込みます。

        Args:
            ragcorpus_dir: RAGコーパスのディレクトリパス

        Returns:
            Dict[str, List[str]]: エンティティインデックス辞書
        """
        entity_index = {}
        entity_file = ragcorpus_dir / "entity_index.json"

        try:
            if entity_file.exists():
                with open(entity_file, 'r', encoding='utf-8') as f:
                    entity_index = json.load(f)
        except Exception as e:
            pass

        return entity_index

    def _execute_query(self, data_dir: Path, query_text: str, skills_dir: Path, ragcorpus_dir: Path,
                      doc_store: Dict[str, str], doc_metadata: Dict[str, Dict[str, Any]], entity_index: Dict[str, List[str]],
                      llmname: str, max_turns: int, logger: logging.Logger) -> Tuple[str, Dict[str, Any]]:
        """
        クエリを実行してエージェントで回答を生成します。

        マルチターンのナビゲーション処理を実装し、スキル階層を探索して質問に回答します。
        プロンプトキャッシング、トークン計算精度改善、エンティティインデックス活用を含みます。

        Args:
            data_dir: データディレクトリパス
            query_text: 実行するクエリ（質問）テキスト
            skills_dir: スキルディレクトリパス
            ragcorpus_dir: RAGコーパスディレクトリパス
            doc_store: ドキュメントコーパス辞書
            doc_metadata: ドキュメントメタデータ辞書（元ファイルのパス情報を含む）
            entity_index: エンティティインデックス辞書
            llmname: 使用するLLMモデル名
            max_turns: エージェントの最大ターン数
            logger: ログ出力用のロガーオブジェクト

        Returns:
            Tuple[str, Dict[str, Any]]: （生成された回答テキスト、使用情報辞書）
        """
        system_prompt = self._build_system_prompt(skills_dir, entity_index)

        messages = []
        total_input_tokens = 0
        total_output_tokens = 0
        docs_retrieved = []
        per_turn_usage = []

        # 最初のターン：クエリ送信とスキル探索
        messages.append({
            "role": "user",
            "content": f"Answer this question by navigating the skill hierarchy:\n\n{query_text}"
        })

        for turn in range(max_turns):
            logger.info(f"Agent turn {turn + 1}/{max_turns}")

            # LLMに問い合わせ
            response_text = None
            for attempt in range(6):
                try:
                    # LLMChat.chat() の呼び出し：msg_text_system と msg_text を指定
                    st, response_messages = self.llm_chat.chat(
                        data_dir=data_dir, logger=logger, llmname=llmname,
                        msg_text_system=system_prompt,
                        msg_text="\n".join([
                            f"{'User' if m['role'] == 'user' else 'Assistant'}: {m['content']}"
                            for m in messages
                       ]),
                    )

                    if st != self.RESP_SUCCESS:
                        raise Exception(f"LLM returned non-success status: {st}")
                    data = response_messages.get('success', {}).get('data', []) if isinstance(response_messages, dict) else []
                    # 最後のメッセージから content を抽出
                    last_message = data[-1] if data else {}
                    response_text = last_message.get('content', '')

                    if not response_text:
                        raise Exception(f"No content in response")

                    # トークン情報を記録（使用可能な場合）
                    # LLMChat では usage 情報が返されないため、概算で計算
                    token_usage = response_messages.get('success', {}).get('token_usage', {}) if isinstance(response_messages, dict) else {}
                    turn_usage = {
                        "turn": turn,
                        "input_tokens": token_usage.get('prompt_tokens', 0),
                        "output_tokens": token_usage.get('completion_tokens', 0),
                    }
                    per_turn_usage.append(turn_usage)
                    total_output_tokens += turn_usage["output_tokens"]

                    break  # リトライ成功

                except Exception as e:
                    logger.debug(f"LLM error in turn {turn + 1}, attempt {attempt + 1}: {e}")
                    if attempt < 5:
                        wait_time = min(60, 2 ** attempt)  # 指数バックオフ: 1, 2, 4, 8, 16, 32秒
                        logger.info(f"Retrying after {wait_time}s...")
                        time.sleep(wait_time)
                        continue
                    else:
                        logger.warning(f"Max retries exceeded for turn {turn + 1}")
                        break

            if response_text is None:
                logger.warning(f"Failed to get response after retries")
                break

            messages.append({
                "role": "assistant",
                "content": response_text
            })

            # マルチターン制御を改善（JSON形式での判定）
            should_continue, action_results, turn_docs = self._evaluate_navigation_response(
                data_dir, response_text, skills_dir, doc_store, entity_index, llmname, logger
            )

            # 取得したドキュメント ID を累積
            docs_retrieved.extend(turn_docs)

            if should_continue:
                # ナビゲーション続行（action_results が診断メッセージまたは実行結果）
                messages.append({
                    "role": "user",
                    "content": f"Navigation results:\n{action_results}"
                })
                total_input_tokens += len(action_results.split()) * 1.3
            else:
                # 最終回答を返す
                logger.info(f"Generated answer after {turn + 1} turn(s)")
                # 取得したドキュメントのメタデータを結果に含める
                retrieved_docs_info = self._get_retrieved_docs_info(docs_retrieved, doc_metadata)
                return response_text.strip(), {
                    "total_input_tokens": int(total_input_tokens),
                    "total_output_tokens": int(total_output_tokens),
                    "turns_completed": turn + 1,
                    "documents_retrieved": docs_retrieved,
                    "retrieved_docs_info": retrieved_docs_info,
                    "per_turn_usage": per_turn_usage,
                    "turns": messages,
                }

        # 最後のメッセージから回答を抽出
        if messages and messages[-1]["role"] == "assistant":
            # 取得したドキュメントのメタデータを結果に含める
            retrieved_docs_info = self._get_retrieved_docs_info(docs_retrieved, doc_metadata)
            return messages[-1]["content"].strip(), {
                "total_input_tokens": int(total_input_tokens),
                "total_output_tokens": int(total_output_tokens),
                "turns_completed": len(messages) // 2,
                "documents_retrieved": docs_retrieved,
                "retrieved_docs_info": retrieved_docs_info,
                "per_turn_usage": per_turn_usage,
                "turns": messages,
            }

        # 取得したドキュメントのメタデータを結果に含める
        retrieved_docs_info = self._get_retrieved_docs_info(docs_retrieved, doc_metadata)
        return "Unable to generate an answer.", {
            "total_input_tokens": int(total_input_tokens),
            "total_output_tokens": int(total_output_tokens),
            "turns_completed": max_turns,
            "documents_retrieved": docs_retrieved,
            "retrieved_docs_info": retrieved_docs_info,
            "per_turn_usage": per_turn_usage,
            "turns": messages,
        }

    def _should_continue_navigation(self, response_text: str, data_dir: Path, llmname: str,
                                   logger: logging.Logger) -> bool:
        """
        応答がさらにナビゲーション処理を必要とするか判定します。

        LLMに問い合わせて、応答が最終回答であるか、さらなるナビゲーション処理が必要かを判定します。
        失敗時はキーワード検出にフォールバックします。

        Args:
            response_text: 評価対象の応答テキスト
            data_dir: データディレクトリパス
            llmname: 判定に使用するLLMモデル名
            logger: ログ出力用のロガーオブジェクト

        Returns:
            bool: True=ナビゲーション続行必要、False=最終回答
        """
        # LLMに判定を依頼
        judgment_prompt = f"""Analyze the following responses and determine whether they require further processing,
        require a follow-up question from the user,
        contain navigation commands, or are final responses.

Response:
{response_text}

Navigation commands include: cat, grep, ls, find, get_document.

Please limit your replies to a single word. If your response requires further processing,
if you need to ask the user a follow-up question,
or if your reply contains a navigation command,
please reply with “CONTINUE.” If your response is final, please reply with “ANSWER.”"""

        try:
            st, response_messages = self.llm_chat.chat(
                data_dir=data_dir,
                logger=logger,
                llmname=llmname,
                msg_text_system="You are a classifier. Analyze if text contains file navigation commands or is a final answer.",
                msg_text=judgment_prompt,
            )

            if st == self.RESP_SUCCESS and response_messages:
                # 最後のメッセージから content を抽出
                data = response_messages.get('success',{}).get('data',[]) if isinstance(response_messages, dict) else {}
                last_message = data[-1] if isinstance(data, list) and data else {}
                result_text = last_message.get('content', '') if isinstance(last_message, dict) else str(last_message)
                should_continue = 'CONTINUE' in result_text.upper()
                logger.debug(f"LLM judgment result: {result_text.strip()[:100]} -> {'CONTINUE' if should_continue else 'ANSWER'}")
                return should_continue
        except Exception as e:
            logger.debug(f"LLM judgment failed: {e}, falling back to keyword detection")

        # フォールバック：キーワード検索（LLM判定失敗時）
        navigation_keywords = ['cat ', 'grep ', 'get_document', 'ls ', 'find ']
        return any(keyword in response_text.lower() for keyword in navigation_keywords)

    def _get_retrieved_docs_info(self, doc_ids: List[str], doc_metadata: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        取得したドキュメントIDから、元ファイルの情報を取得します。

        docs_retrieved（ドキュメントIDのリスト）から、doc_metadataを参照して
        元ファイルのパス情報などを取得し、リンク情報として返します。

        Args:
            doc_ids: 取得したドキュメントIDのリスト
            doc_metadata: ドキュメントメタデータ辞書

        Returns:
            List[Dict[str, Any]]: 元ファイルの情報を含むリスト
                例: [{"doc_id": "...", "source_file": "...", "format": "..."}, ...]
        """
        docs_info = []
        seen_docs = set()

        for doc_id in doc_ids:
            if doc_id in seen_docs:
                continue
            seen_docs.add(doc_id)

            metadata = doc_metadata.get(doc_id, {})
            if metadata:
                docs_info.append({
                    "doc_id": doc_id,
                    "source_file": metadata.get("source_file", "unknown"),
                    "format": metadata.get("format", "unknown"),
                })
            else:
                docs_info.append({
                    "doc_id": doc_id,
                    "source_file": "unknown",
                    "format": "unknown",
                })

        return docs_info

    def _evaluate_navigation_response(self, data_dir: Path, response_text: str, skills_dir: Path,
                                     doc_store: Dict[str, str], entity_index: Dict[str, Any],
                                     llmname: str, logger: logging.Logger) -> Tuple[bool, str, List[str]]:
        """
        LLM応答を評価して、ナビゲーション続行か最終回答かを判定します。

        応答のテキストを解析し、さらなるナビゲーション処理が必要かどうかを判定します。
        必要に応じてナビゲーションアクション（cat、grep、get_document）を実行します。

        Args:
            data_dir: データディレクトリパス
            response_text: 評価対象のLLM応答テキスト
            skills_dir: スキルディレクトリパス
            doc_store: ドキュメントコーパス辞書
            entity_index: エンティティインデックス辞書
            llmname: 使用するLLMモデル名
            logger: ログ出力用のロガーオブジェクト

        Returns:
            Tuple[bool, str, List[str]]: （ナビゲーション続行フラグ、アクション実行結果、取得ドキュメント）
        """
        # ナビゲーション続行判定（LLMベース）
        should_continue = self._should_continue_navigation(response_text, data_dir, llmname, logger)

        if should_continue:
            # ナビゲーションアクションを実行
            action_results, extraction_status, docs_retrieved = self._execute_navigation_actions(
                response_text, skills_dir, doc_store, logger
            )

            # コマンド抽出に失敗した場合、LLMに診断メッセージを返して続行
            if not action_results and not extraction_status['found_any_command']:
                # コマンドが認識できないケース：形式ガイドを返す
                diagnostic_msg = (
                    f"Command extraction failed. Response contained 'CONTINUE' indicator but no valid commands found.\n"
                    f"Expected command formats:\n"
                    f"- cat <file_path>\n"
                    f"- cat <file_path> | grep <term>\n"
                    f"- get_document(doc_id)\n"
                    f"Please reformat your navigation command using one of the above formats.\n\n"
                    f"Your response:\n{response_text[:500]}"
                )
                return True, diagnostic_msg, docs_retrieved

            # コマンドが抽出できたか、部分的に実行できた場合は続行
            return bool(action_results) or extraction_status['found_any_command'], action_results, docs_retrieved
        else:
            # 最終回答（ナビゲーション必要なし）
            return False, "", []

    def _execute_navigation_actions(self, response_text: str, skills_dir: Path,
                                    doc_store: Dict[str, str], logger: logging.Logger) -> Tuple[str, Dict[str, Any], List[str]]:
        """
        応答に含まれるナビゲーション命令を実行します。

        応答テキストからナビゲーション命令（cat、grep、get_document）を抽出して実行し、
        その結果をテキスト形式で返します。複数のコマンド組み合わせに対応します。

        Args:
            response_text: ナビゲーション命令を含む応答テキスト
            skills_dir: スキルディレクトリパス
            doc_store: ドキュメントコーパス辞書
            logger: ログ出力用のロガーオブジェクト

        Returns:
            Tuple[str, Dict[str, Any], List[str]]: （ナビゲーション実行結果、抽出ステータス、取得ドキュメント）
                - results_text: 実行結果のテキスト
                - status: {'found_any_command': bool, 'attempted_commands': int, 'successful_commands': int}
                - docs_retrieved: 取得されたドキュメント ID のリスト
        """
        results = []
        docs_retrieved = []
        extraction_status = {
            'found_any_command': False,
            'attempted_commands': 0,
            'successful_commands': 0,
        }

        # cat ... | grep ... パターンを先に抽出（grep が含まれる場合）
        # より柔軟な grep パターン処理
        cat_grep_pattern = r'cat\s+([^\|]+?)\s*\|\s*grep\s+(?:-i\s+)?([^\s\n]+)'
        cat_grep_matches = re.findall(cat_grep_pattern, response_text, re.IGNORECASE)

        if cat_grep_matches:
            extraction_status['found_any_command'] = True

        for file_path_str, grep_term in cat_grep_matches:
            extraction_status['attempted_commands'] += 1
            file_path_str = file_path_str.strip()
            try:
                # skills_dir相対パスとして解釈（ワイルドカート対応）
                pattern_path = skills_dir / file_path_str.lstrip('/')

                # ワイルドカートを含む場合は glob で拡張
                if '*' in str(pattern_path) or '?' in str(pattern_path):
                    matching_files = list(skills_dir.glob(file_path_str.lstrip('/')))
                else:
                    matching_files = [pattern_path] if pattern_path.exists() and pattern_path.is_file() else []

                if not matching_files:
                    results.append(f"File not found: {file_path_str}")
                    continue

                for file_path in matching_files:
                    if not file_path.is_file():
                        continue

                    content = file_path.read_text(encoding='utf-8', errors='replace')

                    # grep_term をクリーンアップ
                    grep_term_clean = grep_term.replace('"', '').replace("'", '').replace(')', '').strip()

                    rel_path = file_path.relative_to(skills_dir)

                    # entity_index.json ファイルの特別処理
                    if file_path.name == 'entity_index.json':
                        try:
                            entity_index_data = json.loads(content)
                            if isinstance(entity_index_data, dict):
                                # JSON キーをフィルタリング
                                filtered_entities = {
                                    k: v for k, v in entity_index_data.items()
                                    if grep_term_clean.lower() in k.lower()
                                }
                                if filtered_entities:
                                    # エンティティ情報を見やすい形式で返す
                                    entity_lines = []
                                    for entity, info in sorted(filtered_entities.items())[:10]:  # 最大10個
                                        if isinstance(info, dict):
                                            count = info.get('count', 0)
                                            entity_lines.append(f"- {entity}: {count} mention(s)")
                                        else:
                                            entity_lines.append(f"- {entity}")
                                    filtered_content = '\n'.join(entity_lines)
                                    results.append(f"--- {rel_path} | grep {grep_term_clean} ---\nMatching entities:\n{filtered_content}")
                                    extraction_status['successful_commands'] += 1
                                    logger.debug(f"entity_index grep: {len(filtered_entities)} entities matched")
                                else:
                                    results.append(f"--- {rel_path} | grep {grep_term_clean} ---\nNo matching entities for '{grep_term_clean}'")
                                    extraction_status['successful_commands'] += 1
                                    logger.debug(f"entity_index grep found no matches")
                                continue
                        except json.JSONDecodeError:
                            pass  # JSON パースに失敗した場合は、テキスト処理にフォールバック

                    # 通常のテキスト grep フィルタリング
                    lines = content.split('\n')
                    filtered = [l for l in lines if grep_term_clean.lower() in l.lower()]

                    if filtered:
                        filtered_content = '\n'.join(filtered)
                        results.append(f"--- {rel_path} | grep {grep_term_clean} ---\n{filtered_content[:3000]}")
                        extraction_status['successful_commands'] += 1
                        logger.debug(f"grep executed: {rel_path} | grep {grep_term_clean} -> {len(filtered)} matches")
                    else:
                        results.append(f"--- {rel_path} | grep {grep_term_clean} ---\nNo matches for '{grep_term_clean}'")
                        extraction_status['successful_commands'] += 1
                        logger.debug(f"grep found no matches: {rel_path} | grep {grep_term_clean}")

            except Exception as e:
                logger.debug(f"Error executing grep on {file_path_str}: {e}")
                results.append(f"Error executing grep on {file_path_str}: {str(e)}")

        # cat のみのパターンを抽出（grep なし）
        cat_only_pattern = r'cat\s+([^\s|\n]+)'
        cat_only_matches = re.findall(cat_only_pattern, response_text)

        if cat_only_matches:
            extraction_status['found_any_command'] = True

        # grep で処理済みのファイルを除外
        grep_files = {f.strip() for f, _ in cat_grep_matches}

        for file_path_str in cat_only_matches:
            extraction_status['attempted_commands'] += 1
            if file_path_str not in grep_files:
                try:
                    # skills_dir相対パスとして解釈（ワイルドカート対応）
                    pattern_path = skills_dir / file_path_str.lstrip('/')

                    # ワイルドカートを含む場合は glob で拡張
                    if '*' in str(pattern_path) or '?' in str(pattern_path):
                        matching_files = list(skills_dir.glob(file_path_str.lstrip('/')))
                    else:
                        matching_files = [pattern_path] if pattern_path.exists() and pattern_path.is_file() else []

                    if not matching_files:
                        results.append(f"File not found: {file_path_str}")
                        continue

                    for file_path in matching_files:
                        if not file_path.is_file():
                            continue

                        content = file_path.read_text(encoding='utf-8', errors='replace')
                        rel_path = file_path.relative_to(skills_dir)

                        # entity_index.json ファイルの特別処理
                        if file_path.name == 'entity_index.json':
                            try:
                                entity_index_data = json.loads(content)
                                if isinstance(entity_index_data, dict):
                                    # すべてのエンティティ情報を見やすい形式で返す
                                    entity_lines = []
                                    for entity, info in sorted(entity_index_data.items())[:20]:  # 最大20個
                                        if isinstance(info, dict):
                                            count = info.get('count', 0)
                                            entity_lines.append(f"- {entity}: {count} mention(s)")
                                        else:
                                            entity_lines.append(f"- {entity}")
                                    entity_content = '\n'.join(entity_lines) if entity_lines else "No entities found"
                                    results.append(f"--- {rel_path} ---\nEntities in this skill:\n{entity_content}")
                                    extraction_status['successful_commands'] += 1
                                    continue
                            except json.JSONDecodeError:
                                pass  # JSON パースに失敗した場合は、テキスト処理にフォールバック

                        # 通常のファイル内容
                        results.append(f"--- {rel_path} ---\n{content[:3000]}")
                        extraction_status['successful_commands'] += 1

                except Exception as e:
                    logger.debug(f"Error reading file {file_path_str}: {e}")
                    results.append(f"Error reading {file_path_str}: {str(e)}")

        # get_document コマンド: get_document(doc_id) または get_document('doc_id')
        doc_pattern = r'get_document\([\s]*[\'"]?([a-f0-9]+)[\'"]?[\s]*\)'
        doc_matches = re.findall(doc_pattern, response_text)

        if doc_matches:
            extraction_status['found_any_command'] = True

        for doc_id in doc_matches:
            extraction_status['attempted_commands'] += 1
            try:
                # Fuzzy prefix matching でドキュメント取得
                doc_text = self._get_document_fuzzy(doc_id, doc_store, logger)
                if doc_text and "not found" not in doc_text.lower():
                    results.append(f"--- Document: {doc_id} ---\n{doc_text[:3000]}")
                    docs_retrieved.append(doc_id)  # ドキュメント取得を記録
                    extraction_status['successful_commands'] += 1
                else:
                    results.append(f"Document not found: {doc_id}")
            except Exception as e:
                logger.debug(f"Error retrieving document {doc_id}: {e}")
                results.append(f"Error retrieving {doc_id}: {str(e)}")

        results_text = "\n\n".join(results) if results else ""
        logger.debug(f"Navigation actions summary: found={extraction_status['found_any_command']}, "
                    f"attempted={extraction_status['attempted_commands']}, "
                    f"successful={extraction_status['successful_commands']}, "
                    f"docs_retrieved={len(docs_retrieved)}")

        return results_text, extraction_status, docs_retrieved

    def _get_document_fuzzy(self, doc_id: str, doc_store: Dict[str, str],
                           logger: logging.Logger) -> str:
        """
        ドキュメントをファジーマッチングで取得します。

        提供されたdoc_idで完全一致、またはプリフィックスマッチングを行い、
        ドキュメントテキストを返します。serve.pyの_get_document互換実装です。

        Args:
            doc_id: ドキュメントID（完全または部分的）
            doc_store: ドキュメントコーパス辞書
            logger: ログ出力用のロガーオブジェクト

        Returns:
            str: 取得されたドキュメントテキスト、見つからない場合はエラーメッセージ
        """
        # 完全一致
        if doc_id in doc_store:
            return doc_store[doc_id]

        # Prefix matching: 提供されたdoc_idで始まるもの、または完全IDのプリフィックス
        for full_id, text in doc_store.items():
            if full_id.startswith(doc_id) or doc_id.startswith(full_id):
                logger.debug(f"Fuzzy match: {doc_id} -> {full_id}")
                return text

        return f"Document not found: {doc_id}. Check the doc_id from the SKILL.md listing."

    def _build_system_prompt(self, skills_dir: Path, entity_index: Dict[str, Any]) -> str:
        """
        エージェント用のシステムプロンプトを構築します。

        スキル階層の構造説明、ナビゲーション戦略、利用可能なツール、回答形式などを含む
        包括的なシステムプロンプトを生成します。生成されたプロンプトはキャッシュされます。

        Args:
            skills_dir: スキルディレクトリパス
            entity_index: エンティティインデックス辞書

        Returns:
            str: エージェント用のシステムプロンプトテキスト
        """
        # キャッシュキーを生成
        cache_key = f"{skills_dir}_{len(entity_index)}"
        if cache_key in self._prompt_cache:
            return self._prompt_cache[cache_key]

        # スキル一覧を構築（entity_index.json を含める）
        skills_list = ""
        try:
            if skills_dir.exists():
                skill_dirs = sorted([d for d in skills_dir.iterdir()
                                    if d.is_dir() and d.name.startswith('skill-')])
                if skill_dirs:
                    skills_list = "\n## Available Skills\nTop-level skills in the hierarchy:\n"
                    for skill_dir in skill_dirs[:20]:  # 最大20個のスキルを表示
                        skill_name = skill_dir.name
                        # SKILL.md から概要を抽出（1行のサマリー）
                        skill_md = skill_dir / "SKILL.md"
                        summary = ""
                        if skill_md.exists():
                            try:
                                with open(skill_md, 'r', encoding='utf-8', errors='replace') as f:
                                    content = f.read()
                                    # Overview セクションを抽出
                                    import re
                                    match = re.search(r'## Overview\n(.+?)(?:\n##|$)', content, re.DOTALL)
                                    if match:
                                        summary = match.group(1).strip().split('\n')[0][:80]
                            except Exception:
                                pass
                        
                        # スキル内の entity_index.json から主要エンティティを抽出
                        entities_in_skill = ""
                        skill_entity_file = skill_dir / "entity_index.json"
                        if skill_entity_file.exists():
                            try:
                                with open(skill_entity_file, 'r', encoding='utf-8', errors='replace') as f:
                                    skill_entity_index = json.load(f)
                                    # トップ5エンティティを取得
                                    if skill_entity_index:
                                        top_skill_entities = sorted(
                                            skill_entity_index.items(),
                                            key=lambda x: x[1].get('count', 0) if isinstance(x[1], dict) else 0,
                                            reverse=True
                                        )[:5]
                                        if top_skill_entities:
                                            entity_names = [e[0] for e in top_skill_entities]
                                            entities_in_skill = f" [entities: {', '.join(entity_names)}]"
                            except Exception:
                                pass
                        
                        if summary:
                            skills_list += f"- `{skill_name}/`: {summary}{entities_in_skill}\n"
                        else:
                            skills_list += f"- `{skill_name}/`{entities_in_skill}\n"
        except Exception as e:
            pass

        # エンティティインデックスのサマリーを構築
        entity_summary = ""
        if entity_index:
            # トップの20エンティティを取得
            top_entities = sorted(
                entity_index.items(),
                key=lambda x: x[1].get('count', 0) if isinstance(x[1], dict) else 0,
                reverse=True
            )[:20]
            if top_entities:
                entity_summary = "\n## Entity Cross-Index\n"
                entity_summary += "Use this index to find all skills relevant to a specific entity:\n"
                for entity, info in top_entities:
                    if isinstance(info, dict):
                        count = info.get('count', 0)
                        entity_summary += f"- **{entity}**: mentioned in {count} skill(s)\n"
                    else:
                        entity_summary += f"- **{entity}**: referenced in skills\n"

        prompt = f"""You are a knowledge agent that answers questions by navigating a hierarchical skill directory.
You explore a structured file tree where documents are organized into topic clusters, and you have access
to an entity cross-index to triangulate evidence.{skills_list}

## Hard Rules
- Every factual claim must trace to a document you retrieved via get_document.
- SKILL.md / INDEX.md files are NAVIGATION AIDS — they tell you where to look, not what to say.
- Never fabricate steps, URLs, prices, or specifics not found in documents.
- Never guess. If you cannot find relevant content after thorough exploration, say so.

## Skill directory structure
```
skill-XX-topic/
  SKILL.md            ← top-level summary, exemplar docs, related skills, index
  group-YY-subtopic/
    INDEX.md          ← sub-group summary + document list
    group-ZZ/
      INDEX.md        ← leaf summary + document rows (id + title + phrases)
```

Each SKILL.md / INDEX.md may contain these sections:
- `## Overview` — what this skill covers
- `## Related skills` — sibling skills that share entities
- `## Entities & document types` — named entities present
- `## Example documents in this skill` — representative items
- `## Contents` — sub-groups and/or document rows
- `### See also` — stubs of documents whose primary entry is elsewhere

{entity_summary}

## Navigation Strategy (mandatory multi-step exploration)
IMPORTANT: You must follow this exact sequence. Never skip steps.
1. FIRST: Identify candidate skills from the list above that match the query.
   - Scan the available skill names for keywords matching the query.
   - Example: query "web start" → search for "web" in skill names.
2. SECOND: Read the SKILL.md file for each candidate skill.
   - Use: `cat skill-NN-topic/SKILL.md | grep -i <query_keyword>`
   - This reveals which sub-groups and documents cover your topic.
2-ALTERNATIVE: If query mentions a specific entity, use entity_index.json within the skill.
   - Use: `cat skill-NN-topic/entity_index.json | grep -i <entity_keyword>`
   - This returns entities mentioned in the skill and their metadata.
   - This is faster than reading SKILL.md for entity-based queries.
3. THIRD: Descend into sub-groups (read INDEX.md files).
   - Example: `cat skill-NN-topic/group-MM-subtopic/INDEX.md | grep -i <keyword>`
4. FOURTH: Identify specific doc_ids from the INDEX.md rows (tables show id | title | phrases).
   - Use `cat ... | grep` to find doc_ids matching your query.
5. FIFTH: Call get_document(doc_id) to retrieve the actual document content.
   - CRITICAL: You MUST call get_document at least once before answering.
6. SIXTH: Only after retrieving ≥1 full document, construct your final answer.

Candidate skills matching common topics:
- "web" → skill-01-start-stop-mcp-summary, skill-07-web-auth-cli-metadata
- "start" → skill-01-start-stop-mcp-summary
- "command" → skill-00-cli-agent-skill-tts, skill-01-start-stop-mcp-summary

## Available Tools
- **cat <file_path>**: Navigate the skill hierarchy
- **cat <file_path> | grep -i <term>**: Search within files
- **get_document(doc_id)**: Retrieve the full text of a document

## Answer Format
- First sentence = direct answer. No preamble.
- Factual questions: 1-3 sentences (~80 words max).
- Procedural questions: numbered steps only (~150 words max).
- Plain text. No bold, headers, or dividers.
- One approach only. Do not present alternatives.
- Never add "contact support" or closing remarks.
"""

        # キャッシュに保存
        self._prompt_cache[cache_key] = prompt
        return prompt

    def _find_relevant_skills(self, query_text: str, skills_dir: Path,
                             entity_index: Dict[str, List[str]], logger: logging.Logger) -> List[str]:
        """
        クエリに最も関連するスキルを特定します。

        スキルディレクトリから、クエリに関連性が高いスキルを検出して返します。
        最大5つのスキルを返します。

        Args:
            query_text: 質問テキスト
            skills_dir: スキルディレクトリパス
            entity_index: エンティティインデックス辞書
            logger: ログ出力用のロガーオブジェクト

        Returns:
            List[str]: 関連スキル名のリスト（最大5個）
        """
        relevant_skills = []

        try:
            # スキルディレクトリ内の最上位ディレクトリを検索
            if skills_dir.exists():
                for skill_dir in sorted(skills_dir.iterdir()):
                    if skill_dir.is_dir() and skill_dir.name.startswith('skill-'):
                        relevant_skills.append(skill_dir.name)

        except Exception as e:
            logger.warning(f"Error finding relevant skills: {e}")

        return relevant_skills[:5]  # 最大5つのスキル

    def _find_relevant_documents(self, query_text: str, skills_dir: Path,
                                skill_paths: List[str], logger: logging.Logger) -> List[str]:
        """
        関連スキル内の関連ドキュメントを検索します。

        指定されたスキル内のINDEX.mdファイルを探索し、クエリに関連するドキュメントIDを
        検出して返します。最大10個のドキュメントを返します。

        Args:
            query_text: 質問テキスト
            skills_dir: スキルディレクトリパス
            skill_paths: 対象スキルのパスリスト
            logger: ログ出力用のロガーオブジェクト

        Returns:
            List[str]: 関連ドキュメントIDのリスト（最大10個）
        """
        relevant_docs = []

        try:
            for skill_path in skill_paths:
                skill_dir = skills_dir / skill_path
                if not skill_dir.exists():
                    continue

                # INDEX.mdファイルを探索してドキュメントを特定
                for index_file in skill_dir.glob("**/INDEX.md"):
                    try:
                        content = index_file.read_text(encoding='utf-8', errors='replace')

                        # ドキュメント行を抽出（ID: ... のパターン）
                        doc_pattern = r'\|\s*([a-f0-9\-]+)\s*\|'
                        matches = re.findall(doc_pattern, content)
                        relevant_docs.extend(matches)
                    except Exception as e:
                        logger.debug(f"Error reading {index_file}: {e}")

        except Exception as e:
            logger.warning(f"Error finding relevant documents: {e}")

        return list(set(relevant_docs))[:10]  # 重複を除去して最大10個

    def output_schema(self) -> type:
        """
        コマンドの出力スキーマをPydanticモデルで定義して返します。

        Returns:
            type: 出力結果の構造を定義したPydanticモデルクラス
        """
        class Data(resdata.Data):
            message: str = pydantic.Field(description="処理結果のメッセージ")
            answer: str = pydantic.Field(description="クエリに対する回答")
            query: str = pydantic.Field(description="実行されたクエリ")
            usage: Dict[str, Any] = pydantic.Field(description="トークン使用情報")
            turns: List[Dict[str, str]] = pydantic.Field(description="マルチターンのやり取り履歴")

        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")

        return Result
