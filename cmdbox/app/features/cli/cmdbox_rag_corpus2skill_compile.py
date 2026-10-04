from collections import defaultdict
from pathlib import Path
from typing import Dict, Any, Tuple, List, Union, Set
import argparse
import logging
import json
import pydantic
import hashlib
import re
import numpy as np
import time
import sys

# Initialize sys.path for corpus2skill imports before importing from Corpus2Skill
_corpus2skill_root = Path(__file__).parent / "Corpus2Skill"
if str(_corpus2skill_root) not in sys.path:
    sys.path.insert(0, str(_corpus2skill_root))

from cmdbox.app import common, client, feature, filer
from cmdbox.app.commons import convert, redis_client, resdata, validator
from cmdbox.app.features.cli import cmdbox_llm_chat, cmdbox_llm_embed
from cmdbox.app.features.cli.Corpus2Skill.corpus2skill.clustering import build_hierarchy, tree_stats, ClusterNode
from cmdbox.app.features.cli.Corpus2Skill.corpus2skill.skill_builder import build_skill_tree
from cmdbox.app.options import Options


class RagCorpus2skillCompile(feature.OneshotResultEdgeFeature, validator.Validator):
    def __init__(self, appcls, ver, language):
        super().__init__(appcls, ver, language)
        self.llm_chat = cmdbox_llm_chat.LLMChat(self.appcls, self.ver, self.language)
        self.llm_embed = cmdbox_llm_embed.LLMEmbed(self.appcls, self.ver, self.language)

    """
    Corpus2Skillの コンパイルコマンド：ドキュメントコレクションをスキル階層に変換します。

    Redis 経由でサーバー側で実行します。

    処理フロー:
    1.  ドキュメント読み込み
    2.  (オプション)ドキュメント要約カード作成
    3.  ドキュメント埋め込み
    4.  階層的クラスタリング
    5.  クラスタの要約とラベリング
    6.  エンティティ抽出と相互リンク
    7.  スキルツリーの構築
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
            str: 'corpus2skill_compile'コマンド
        """
        return 'corpus2skill_compile'

    def get_option(self) -> Dict[str, Any]:
        """
        コマンドの実行オプションを取得します。

        Corpus2Skill処理に必要な各種オプション（ホスト、ポート、LLMモデル名、
        クラスタリング設定など）を定義して返します。

        Returns:
            Dict[str, Any]: オプション定義を含む辞書
        """
        return dict(
            use_redis=self.USE_REDIS_TRUE, nouse_webmode=False, use_agent=False,
            description_ja="ドキュメントコレクションをCorpus2Skillのスキル階層にコンパイルします。",
            description_en="Compile a document collection into a Corpus2Skill hierarchy.",
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
                dict(opt="svpath", type=Options.T_DIR, default="/", required=True, multi=False, hide=False, choice=None,
                     description_ja="サーバーのデータフォルダ以下のパスを指定します。テキスト(.txt)、マークダウン(.md)、JSON(.json)、JSONL(.jsonl)形式をサポートします。各ドキュメントは'id'と'contents'フィールドを持つ必要があります。",
                     description_en="Specify the directory path under the server's data folder. Supports text (.txt), markdown (.md), JSON (.json), and JSONL (.jsonl) formats. Each document should have 'id' and 'contents' fields."),
                dict(opt="scope", type=Options.T_STR, default="server", required=True, multi=False, hide=False, choice=["server", "current", "client"],
                     description_ja="アクセススコープを指定します。currentとclientはサポートしていません。serverのみ指定可能です。",
                     description_en="Specify the access scope. Only 'server' is supported. 'current' and 'client' are not supported."),
                dict(opt="fwpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが範囲外であるかどうかを判定するパスを指定します。このパスの配下でない場合、このパスを指定したと解釈します。",
                     description_en="Specify a path to determine whether the specified path is out of bounds. If it is not under this path, it is interpreted as having specified this path."),
                dict(opt="rjpath", type=Options.T_FILE, default=None, required=False, multi=True, hide=False, choice=None, web="mask",
                     description_ja="指定したパスが要求されたパスにマッチする場合、アクセスが拒否されます。正規表現として解釈します。",
                     description_en="If the specified path matches the requested path, access will be denied. Interpreted as a regular expression."),
                dict(opt="ragcorpus_name", type=Options.T_STR, default=None, required=True, multi=False, hide=False, choice=None,
                     description_ja="RAGコーパス名を指定します。スキルツリーはdata_dir/.ragcorpus/<ragcorpus_name>に生成されます。",
                     description_en="Specify the RAG corpus name. The skill tree will be generated in data_dir/.ragcorpus/<ragcorpus_name>."),
                dict(opt="llmname", type=Options.T_STR, default="claude-sonnet-4-6", required=False, multi=False, hide=False, choice=None,
                     description_ja="クラスタリングと要約処理に使用するLLMの名前を指定します。デフォルトはclaude-sonnet-4-6です。",
                     description_en="Specify the LLM name for clustering and summarization. Default is claude-sonnet-4-6."),
                dict(opt="llmname_embed", type=Options.T_STR, default="text-embedding-3-small", required=False, multi=False, hide=False, choice=None,
                     description_ja="埋め込み処理に使用するLLMの名前を指定します。デフォルトはtext-embedding-3-smallです。",
                     description_en="Specify the LLM name for embedding. Default is text-embedding-3-small."),
                dict(opt="doc_summary_model", type=Options.T_STR, default="claude-haiku-4-5", required=False, multi=False, hide=False, choice=None,
                     description_ja="ドキュメント要約カード生成に使用するLLMの名前を指定します。デフォルトはclaude-haiku-4-5です。",
                     description_en="Specify the LLM name for per-document summary card generation. Default is claude-haiku-4-5."),
                dict(opt="p", type=Options.T_INT, default=10, required=False, multi=False, hide=False, choice=None,
                     description_ja="分岐比（各クラスタあたりの子クラスタ数）を指定します。デフォルトは10です。",
                     description_en="Specify the branching ratio (children per cluster). Default is 10."),
                dict(opt="max_top", type=Options.T_INT, default=8, required=False, multi=False, hide=False, choice=None,
                     description_ja="トップレベルのスキル最大数を指定します。デフォルトは8です。",
                     description_en="Specify the maximum number of top-level skills. Default is 8."),
                dict(opt="min_cluster_size", type=Options.T_INT, default=3, required=False, multi=False, hide=False, choice=None,
                     description_ja="クラスタの最小サイズを指定します。デフォルトは3です。",
                     description_en="Specify the minimum cluster size. Default is 3."),
                dict(opt="max_doc_chars", type=Options.T_INT, default=8000, required=False, multi=False, hide=False, choice=None,
                     description_ja="1ドキュメントあたりの最大文字数を指定します。デフォルトは8000です。",
                     description_en="Specify the maximum characters per document. Default is 8000."),
                dict(opt="no_doc_summaries", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="Trueを指定するとドキュメント要約カード作成をスキップします。処理速度向上の代わりに品質低下があります。",
                     description_en="If True, skip document summary card generation. Faster but lower quality."),
                dict(opt="compact", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="Trueを指定するとスキルAPI制限に対応するため、リーフINDEX.mdを親に統合します。",
                     description_en="If True, merge leaf INDEX.md into parent to reduce file count."),
                dict(opt="dry_run", type=Options.T_BOOL, default=False, required=False, multi=False, hide=False, choice=[True, False],
                     description_ja="Trueを指定すると実際には処理を実行せず、実行計画のみ表示します。",
                     description_en="If True, show execution plan without actually running."),
            ]
        )

    def is_cluster_redirect(self):
        """
        クラスタリダイレクトが有効かどうかを判定します。

        Returns:
            bool: False（クラスタリダイレクト無効）
        """
        return False

    @validator.apprun_check
    def apprun(self, logger: logging.Logger, args: argparse.Namespace, tm: float,
               pf: List[Dict[str, float]] = []) -> Tuple[int, Dict[str, Any], Any]:
        """
        クライアント側の実行処理：Redis経由でサーバーにペイロードを送信します。

        引数の検証を行い、Corpus2Skillコンパイル処理をサーバー側で実行するための
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
            # Validate scope
            scope = str(args.scope) if args.scope else "server"
            if scope in ["current", "client"]:
                msg = dict(warn=f"Scope '{scope}' is not supported for corpus2skill_compile. Only 'server' scope is supported.")
                logger.warning(f"corpus2skill_compile: {msg['warn']}")
                common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
                return self.RESP_WARN, msg, None

            args.fwpath = args.fwpath if isinstance(args.fwpath, list) else [args.fwpath] if args.fwpath is not None and args.fwpath != "********" else []
            args.rjpath = args.rjpath if isinstance(args.rjpath, list) else [args.rjpath] if args.rjpath is not None and args.rjpath != "********" else []
            fwpaths = [str(p).replace('"','') for p in args.fwpath]
            rjpaths = [str(p).replace('"','') for p in args.rjpath]

            payload = dict(
                svpath=str(args.svpath).replace('"',''),
                scope=scope,
                fwpaths=fwpaths,
                rjpaths=rjpaths,
                ragcorpus_name=str(args.ragcorpus_name),
                llmname=str(args.llmname) if args.llmname else "claude-sonnet-4-6",
                llmname_embed=str(args.llmname_embed) if args.llmname_embed else "text-embedding-3-small",
                doc_summary_model=str(args.doc_summary_model) if args.doc_summary_model else "claude-haiku-4-5",
                p=int(args.p) if args.p else 10,
                max_top=int(args.max_top) if args.max_top else 8,
                min_cluster_size=int(args.min_cluster_size) if args.min_cluster_size else 3,
                max_doc_chars=int(args.max_doc_chars) if args.max_doc_chars else 8000,
                no_doc_summaries=bool(args.no_doc_summaries) if args.no_doc_summaries is not None else False,
                compact=bool(args.compact) if args.compact is not None else False,
                dry_run=bool(args.dry_run) if args.dry_run is not None else False,
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
            logger.warning(f"corpus2skill_compile apprun failed: {e}", exc_info=True)
            msg = dict(warn=dict(message=str(e)))
            common.print_format(msg, args.format, tm, args.output_json, args.output_json_append, pf=pf)
            return self.RESP_WARN, msg, None

    def svrun(self, data_dir: Path, logger: logging.Logger, redis_cli: redis_client.RedisClient, msg: List[str],
              sessions: Dict[str, Dict[str, Any]]) -> int:
        """
        サーバー側の実行処理：実際のCorpus2Skillコンパイル処理を実行します。

        ドキュメント読み込み、埋め込み、階層的クラスタリング、要約、エンティティ抽出、
        スキルツリー構築などの全処理を実行します。

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

            svpath = payload.get('svpath', '/')
            fwpaths = payload.get('fwpaths', [])
            rjpaths = payload.get('rjpaths', [])
            ragcorpus_name = payload.get('ragcorpus_name')
            ragcorpus_dir = data_dir / '.ragcorpus' / ragcorpus_name
            llmname = payload.get('llmname', 'claude-sonnet-4-6')
            llmname_embed = payload.get('llmname_embed', 'text-embedding-3-small')
            doc_summary_model = payload.get('doc_summary_model', 'claude-haiku-4-5')
            p = payload.get('p', 10)
            max_top = payload.get('max_top', 8)
            min_cluster_size = payload.get('min_cluster_size', 3)
            max_doc_chars = payload.get('max_doc_chars', 8000)
            no_doc_summaries = payload.get('no_doc_summaries', False)
            compact = payload.get('compact', False)
            dry_run = payload.get('dry_run', False)

            # Check access with filer
            f = filer.Filer(data_dir, logger)
            chk, access_msg = f.check_fwpath(svpath, fwpaths if fwpaths else None, rjpaths if rjpaths else None)
            if not chk:
                msg_result = dict(warn=f"Access denied: {access_msg.get('warn', 'Unknown error')}")
                logger.warning(f"Access check failed for {svpath}: {msg_result}")
                redis_cli.rpush(reskey, msg_result)
                return self.RESP_WARN

            # Resolve input_path from svpath
            input_path = data_dir / svpath.lstrip('/')
            logger.info(f"Starting Corpus2Skill compilation")
            logger.info(f"Input: {input_path}, Output: {ragcorpus_dir}")

            if not input_path.exists():
                msg_result = dict(warn=f"Input path does not exist: {input_path}")
                redis_cli.rpush(reskey, msg_result)
                return self.RESP_WARN

            t0 = time.time()

            # ドキュメント読み込み
            logger.info(f"Loading documents...")
            doc_ids, doc_texts, doc_metadata = self._load_documents(
                input_path, max_doc_chars, recursive=True, preserve_id=True, logger=logger
            )
            logger.info(f"Loaded {len(doc_ids)} documents")

            if not doc_ids:
                msg_result = dict(warn=f"No documents found in: {input_path}")
                redis_cli.rpush(reskey, msg_result)
                return self.RESP_WARN

            # コーパスディレクトリの準備
            if not dry_run:
                ragcorpus_dir.mkdir(parents=True, exist_ok=True)

            # 1.5 (optional) Per-document summary cards
            doc_cards: Dict[str, Dict[str, Any]] = {}
            if not no_doc_summaries:
                logger.info("Building per-document summary cards...")
                doc_cards = self._build_doc_cards(
                    data_dir=data_dir, logger=logger,
                    llmname=doc_summary_model, doc_ids=doc_ids, doc_texts=doc_texts,
                    cache_dir=ragcorpus_dir / ".cache",
                )

            # 2. Embedding
            logger.info("Embedding documents...")
            embed_inputs = self._build_leaf_embed_inputs(doc_ids, doc_texts, doc_cards, logger=logger)
            embeddings = self._embed_documents(
                data_dir=data_dir, logger=logger,
                llmname_embed=llmname_embed, texts=embed_inputs,
            )

            # 3. Hierarchy build
            logger.info("Building hierarchy...")

            def summarize_batch_fn(items: List[List[str]], level: int = 1) -> List[str]:
                return [
                    self._summarize_cluster(data_dir, logger, llmname, child_texts, level)
                    for child_texts in items
                ]

            def embed_fn(text: str, context: str = None):
                content = text if not context else f"{text}\n---\n{context}"
                vecs = self._embed_documents(
                    data_dir=data_dir, logger=logger,
                    llmname_embed=llmname_embed, texts=[content],
                )
                return vecs[0]

            roots = build_hierarchy(
                doc_ids=doc_ids, doc_texts=doc_texts, embeddings=embeddings,
                p=p, max_top=max_top, min_cluster_size=min_cluster_size,
                summarize_batch_fn=summarize_batch_fn, embed_fn=embed_fn,
                soft_assignment=True, soft_margin=0.05,
                repartition_fn=None,
                # Do not pass doc_cards into build_hierarchy: that path imports
                # corpus2skill.summarizer (anthropic dependency). We keep using
                # cmdbox LLM chat for card generation and downstream outputs.
                doc_cards=None,
            )

            stats = tree_stats(roots)
            logger.info(f"Hierarchy built: {stats}")

            # 4. Label clusters
            clusters = self._collect_all_clusters(roots)
            if clusters:
                logger.info(f"Labeling {len(clusters)} clusters...")
                for c in clusters:
                    c.label = self._label_cluster(data_dir, logger, llmname, c.summary)

            # 4.5. Exemplar documents per skill
            logger.info("Selecting exemplar documents per skill...")
            self._attach_exemplars(roots, k=3)

            # 5. Entity extraction + cross-linking
            logger.info("Extracting entities and building cross-links...")
            self._extract_entities(data_dir, logger, llmname, clusters)
            entity_index = self._build_entity_index(clusters, roots, num_related=3)

            if not dry_run:
                (ragcorpus_dir / "entity_index.json").write_text(
                    json.dumps(entity_index, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

            # 6. Build skill directories
            skills_dir = None
            if not dry_run:
                doc_content = dict(zip(doc_ids, doc_texts))
                skills_dir = build_skill_tree(
                    roots, ragcorpus_dir, doc_content=doc_content,
                    doc_cards=doc_cards or None, compact=compact,
                    rich_index=bool(doc_cards), exemplars=True,
                    related_skills=True, entity_index=entity_index or None,
                )

                # Save document metadata (including source file paths) for query output
                doc_metadata_dict = dict(zip(doc_ids, doc_metadata))
                (ragcorpus_dir / "doc_metadata.json").write_text(
                    json.dumps(doc_metadata_dict, indent=2, ensure_ascii=False),
                    encoding="utf-8",
                )

            compile_info = {
                "input_dir": str(input_path),
                "ragcorpus_dir": str(ragcorpus_dir),
                "num_documents": len(doc_ids),
                "llm_model": llmname,
                "embed_model": llmname_embed,
                "p": p, "max_top": max_top, "min_cluster_size": min_cluster_size,
                "doc_summary_cards_enabled": not no_doc_summaries,
                "compact": compact, "dry_run": dry_run,
                "hierarchy": stats,
                "num_entities": len(entity_index),
                "skills_dir": str(skills_dir) if skills_dir else None,
                "status": "COMPLETED" if not dry_run else "DRY_RUN",
            }

            elapsed = time.time() - t0

            msg_result = dict(
                success=dict(
                    message=f"Corpus2Skill compilation {'completed' if not dry_run else 'planned'}",
                    documents_count=len(doc_ids),
                    ragcorpus_dir=str(ragcorpus_dir),
                    compile_info=compile_info,
                    elapsed_seconds=round(elapsed, 2),
                )
            )
            redis_cli.rpush(reskey, msg_result)
            return self.RESP_SUCCESS

        except Exception as e:
            logger.warning(f"corpus2skill_compile svrun failed: {e}", exc_info=True)
            msg_result = dict(warn=f"corpus2skill_compile: {e}")
            redis_cli.rpush(reskey, msg_result)
            return self.RESP_WARN

    # === ヘルパーメソッド（以下の実装は前述のapprunから移行） ===

    def _llm_chat_text(self, data_dir: Path, logger: logging.Logger,
                       llmname: str, prompt: str) -> str:
        """
        LLMに対話形式でプロンプトを送信し、レスポンステキストを取得します。

        Args:
            data_dir: データディレクトリパス
            logger: ログ出力用のロガーオブジェクト
            llmname: 使用するLLMの名前
            prompt: LLMに送信するプロンプトテキスト

        Returns:
            str: LLMからのレスポンステキスト

        Raises:
            ValueError: LLM通信に失敗した場合
        """
        st, msg = self.llm_chat.chat(
            data_dir, logger, llmname, msg_role="user", msg_text=prompt,
            msg_text_system="次の依頼に従ってください。\\n\\n{{msg_text}}",
        )
        if st != self.RESP_SUCCESS:
            raise ValueError(msg.get("warn", "LLM chat failed"))
        rows = msg.get("success", {}).get("data", [])
        if not rows:
            return ""
        content = rows[0].get("content")
        return content if isinstance(content, str) else str(content)

    def _extract_json_obj(self, text: str) -> Dict[str, Any]:
        """
        テキストからJSON形式のオブジェクトを抽出します。

        正規表現を使用してテキスト内の最初のJSON形式の部分を検出し、
        パースして辞書として返します。

        Args:
            text: JSON形式を含むテキスト

        Returns:
            Dict[str, Any]: 抽出・パースされたJSON辞書、パース失敗時は空辞書
        """
        m = re.search(r"\{.*\}", text, re.DOTALL)
        if not m:
            return {}
        try:
            return json.loads(m.group(0))
        except Exception:
            return {}

    def _build_doc_cards(self, data_dir: Path, logger: logging.Logger,
                        llmname: str,
                        doc_ids: List[str], doc_texts: List[str],
                        cache_dir: Path = None) -> Dict[str, Dict[str, Any]]:
        """
        各ドキュメントの要約カード（タイトル、1行説明、キーフレーズ）を生成します。

        キャッシュがあれば再利用し、なければLLMで新規生成してキャッシュに保存します。
        各ドキュメントから以下の情報を抽出します：
        - title: ドキュメントのタイトル
        - one_line: 1行の説明文
        - phrases: 重要なキーフレーズ（2-4個）

        Args:
            data_dir: データディレクトリパス
            logger: ログ出力用のロガーオブジェクト
            llmname: 要約生成に使用するLLMの名前
            doc_ids: ドキュメントIDのリスト
            doc_texts: ドキュメントテキストのリスト
            cache_dir: キャッシュディレクトリパス（指定なければ.cacheを使用）

        Returns:
            Dict[str, Dict[str, Any]]: {doc_id: {"title": ..., "one_line": ..., "phrases": [...]}, ...}
        """
        cards: Dict[str, Dict[str, Any]] = {}

        # キャッシュパスの設定
        if cache_dir is None:
            cache_dir = data_dir / ".cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        cache_file = cache_dir / "doc_cards.json"

        # キャッシュチェック
        if cache_file.exists():
            try:
                cached = json.loads(cache_file.read_text(encoding="utf-8"))
                # キャッシュ内容がdoc_idsと一致するかチェック
                if isinstance(cached, dict) and set(cached.keys()) == set(doc_ids):
                    logger.info(f"Reusing cached doc cards from {cache_file}")
                    return cached
            except Exception as e:
                logger.debug(f"Failed to load cache: {e}, regenerating...")

        # キャッシュがない または 不一致の場合、新規生成
        total_docs = len(doc_ids)
        logger.debug(f"Building doc cards for {total_docs} documents...")

        for idx, (did, txt) in enumerate(zip(doc_ids, doc_texts), start=1):
            logger.debug(f"  Processing document {idx}/{total_docs}: {did}")
            prompt = (
                "次の文書の要約カードをJSONで返してください。"
                "キーは title, one_line, phrases(2-4個配列) のみ。\\n\\n"
                f"Document:\\n{txt[:4000]}"
            )
            raw = self._llm_chat_text(data_dir, logger, llmname, prompt)
            obj = self._extract_json_obj(raw)
            title = str(obj.get("title", "")).strip()
            one_line = str(obj.get("one_line", "")).strip()
            phrases = obj.get("phrases", [])
            if not isinstance(phrases, list):
                phrases = []
            phrases = [str(p).strip() for p in phrases if str(p).strip()]

            cards[did] = {
                "title": title or txt.split("\n", 1)[0][:80],
                "one_line": one_line or txt[:120],
                "phrases": phrases[:4],
            }

        # キャッシュに保存
        try:
            cache_file.write_text(
                json.dumps(cards, ensure_ascii=False, indent=2),
                encoding="utf-8"
            )
            logger.info(f"Cached doc cards to {cache_file}")
        except Exception as e:
            logger.debug(f"Failed to save cache: {e}")

        logger.debug(f"Completed building doc cards for {total_docs} documents.")
        return cards

    def _build_leaf_embed_inputs(self, doc_ids: List[str], doc_texts: List[str],
                                doc_cards: Dict[str, Dict[str, Any]], logger: logging.Logger = None) -> List[str]:
        """
        ドキュメントテキストに要約カード情報を付与した埋め込み入力を生成します。

        doc_cardsがない場合は元のテキストをそのまま返します。
        ある場合は「title、one_line、phrases」の要約情報をテキストの先頭に付加します。

        Args:
            doc_ids: ドキュメントIDのリスト
            doc_texts: ドキュメントテキストのリスト
            doc_cards: ドキュメント要約カード辞書（doc_id -> カード情報）
            logger: ログ出力用のロガーオブジェクト（オプション）

        Returns:
            List[str]: 埋め込み用に加工されたテキストのリスト
        """
        if not doc_cards:
            return doc_texts

        total_docs = len(doc_ids)
        if logger:
            logger.debug(f"Building leaf embed inputs for {total_docs} documents...")

        out: List[str] = []
        for idx, (did, txt) in enumerate(zip(doc_ids, doc_texts), start=1):
            card = doc_cards.get(did)
            if not card:
                out.append(txt)
                continue
            title = card.get("title", "")
            one_line = card.get("one_line", "")
            phrases = "; ".join(card.get("phrases", []))
            head = f"title: {title}\\none_line: {one_line}\\nphrases: {phrases}"
            out.append(f"{head}\\n---\\n{txt}")

        if logger:
            logger.debug(f"Completed building leaf embed inputs for {total_docs} documents.")
        return out

    def _embed_documents(self, data_dir: Path, logger: logging.Logger,
                        llmname_embed: str, texts: List[str]) -> np.ndarray:
        """
        複数のテキストを埋め込みモデルで処理して、ベクトル表現を生成します。

        各テキストをLLMの埋め込みモデルに送信し、得られたベクトルをnumpy配列として
        返します。

        Args:
            data_dir: データディレクトリパス
            logger: ログ出力用のロガーオブジェクト
            llmname_embed: 埋め込み処理に使用するLLMモデルの名前
            texts: 埋め込み対象のテキストリスト

        Returns:
            np.ndarray: 形状（テキスト数、埋め込み次元数）のfloat32配列

        Raises:
            ValueError: 埋め込み処理に失敗した場合
        """
        vectors: List[List[float]] = []
        total_texts = len(texts)

        logger.info(f"Embedding {total_texts} texts")

        batch_size = 1
        for batch_start in range(0, len(texts), batch_size):
            batch_end = min(batch_start + batch_size, len(texts))
            batch = texts[batch_start:batch_end]
            logger.debug(f"  Embedding texts {batch_start+1}-{batch_end}/{total_texts}")
            st, msg = self.llm_embed.embed(
                data_dir, logger, llmname_embed,
                input_text=batch
            )
            if st != self.RESP_SUCCESS:
                raise ValueError(msg.get("warn", f"LLM embed failed for batch {batch_start+1}-{batch_end}"))
            rows = msg.get("success", {}).get("data", [])
            for row in rows:
                emb = row.get("embedding", [])
                if emb:
                    vectors.append(emb)

        logger.info(f"Completed embedding {total_texts} texts")
        return np.array(vectors, dtype=np.float32)

    def _summarize_cluster(self, data_dir: Path, logger: logging.Logger,
                          llmname: str,
                          child_texts: List[str], level: int) -> str:
        """
        クラスタに含まれる子要素のテキストから、クラスタ全体の要約を生成します。

        LLMを使用して、複数のテキストの共通トピック、質問タイプ、主要用語を抽出し、
        2-3文の要約を作成します。

        Args:
            data_dir: データディレクトリパス
            logger: ログ出力用のロガーオブジェクト
            llmname: 要約生成に使用するLLMの名前
            child_texts: クラスタに属するテキストのリスト
            level: 階層レベル（1以上の整数）

        Returns:
            str: 生成されたクラスタ要約
        """
        snippets = "\\n\\n".join([t[:600] for t in child_texts[:20]])
        prompt = (
            f"level={level} のクラスタ要約を2-3文で作成してください。"
            "共通トピック・質問タイプ・主要用語を含めてください。\\n\\n"
            f"Texts:\\n{snippets}"
        )
        text = self._llm_chat_text(data_dir, logger, llmname, prompt).strip()
        return text or f"Cluster of {len(child_texts)} items."

    def _label_cluster(self, data_dir: Path, logger: logging.Logger,
                      llmname: str, summary: str) -> str:
        """
        クラスタの要約テキストから、簡潔なラベル（タグ）を生成します。

        2-5語の英小文字ハイフン区切りラベルをLLMで生成します。
        例：「data-processing」「machine-learning-basics」

        Args:
            data_dir: データディレクトリパス
            logger: ログ出力用のロガーオブジェクト
            llmname: ラベル生成に使用するLLMの名前
            summary: クラスタの要約テキスト

        Returns:
            str: クラスタのラベル（英小文字ハイフン区切り、最大50文字）
        """
        prompt = (
            "次の要約に対して、2-5語の英小文字ハイフン区切りラベルを1つだけ返してください。"
            "記号や説明は不要です。\\n\\n"
            f"Summary:\\n{summary[:800]}"
        )
        raw = self._llm_chat_text(data_dir, logger, llmname, prompt).strip().lower()
        label = "".join(ch if ch.isalnum() or ch == "-" else "-" for ch in raw).strip("-")
        return (label or "cluster")[:50]

    def _pick_exemplars(self, node: ClusterNode, k: int = 3) -> List[str]:
        """
        クラスタノードから最大k個の代表的なドキュメントIDを選択します。

        リーフクラスタの場合は、ドキュメントの埋め込みベクトルがクラスタの中心に
        最も近いドキュメントを選択します。分岐クラスタの場合は、各直接の子から
        その代表を取得し、それらを親のセントロイドに対してランク付けして選択します。

        Args:
            node: クラスタノード（ClusterNodeオブジェクト）
            k: 選択する代表ドキュメント数（デフォルト：3）

        Returns:
            List[str]: 選択されたドキュメントIDのリスト（最大k個）
        """
        if not node.children:
            # Doc-level leaf — return its own doc id.
            return node.doc_ids[:k]

        # If all children are doc-leaves, this is a level-1 (leaf) cluster.
        if all(not c.children for c in node.children):
            items = [(c.doc_ids[0], c.embedding) for c in node.children if c.doc_ids]
            items = [(did, e) for did, e in items if e is not None]
            if not items:
                return node.doc_ids[:k]
            embs = np.array([e for _, e in items], dtype=np.float32)
            ref = node.embedding if node.embedding is not None else embs.mean(axis=0)
            ref = ref / (np.linalg.norm(ref) + 1e-10)
            sims = embs @ ref
            order = np.argsort(-sims)
            picks: List[str] = []
            for j in order:
                did = items[int(j)][0]
                if did in picks:
                    continue
                picks.append(did)
                if len(picks) >= k:
                    break
            return picks

        # Branch cluster: each child donates its top exemplar.
        candidates: List[Tuple[str, np.ndarray]] = []
        for child in node.children:
            cid = self._pick_exemplars(child, k=1)
            if cid and child.embedding is not None:
                candidates.append((cid[0], child.embedding))

        if not candidates:
            return node.doc_ids[:k]

        embs = np.array([e for _, e in candidates], dtype=np.float32)
        ref = node.embedding if node.embedding is not None else embs.mean(axis=0)
        ref = ref / (np.linalg.norm(ref) + 1e-10)
        sims = embs @ ref
        order = np.argsort(-sims)
        seen: Set[str] = set()
        picks: List[str] = []
        for j in order:
            did = candidates[int(j)][0]
            if did in seen:
                continue
            seen.add(did)
            picks.append(did)
            if len(picks) >= k:
                break
        return picks

    def _attach_exemplars(self, roots: List[ClusterNode], k: int = 3) -> None:
        """
        全てのクラスタノードに対して、代表ドキュメントIDを付与します。
        ルートから全階層を走査して、各非リーフクラスタに対して
        exemplar_doc_idsプロパティを設定します。

        Args:
            roots: ルートクラスタノードのリスト
            k: 各クラスタで選択する代表ドキュメント数（デフォルト：3）
        """
        for node in self._collect_all_clusters(roots):
            node.exemplar_doc_ids = self._pick_exemplars(node, k=k)

    def _collect_all_clusters(self, roots: List[ClusterNode]) -> List[ClusterNode]:
        """
        ルートノードから全ての非リーフクラスタノードを収集します。
        階層構造を走査して、レベル1以上の全クラスタノードをリストで返します。

        Args:
            roots: ルートクラスタノードのリスト

        Returns:
            List[ClusterNode]: 全クラスタノードのリスト（レベル1以上のみ）
        """
        out: List[ClusterNode] = []
        stack = list(roots)
        while stack:
            n = stack.pop()
            if n.level > 0:
                out.append(n)
                stack.extend(n.children)
        return out

    def _extract_entities(self, data_dir: Path, logger: logging.Logger,
                         llmname: str, nodes: List[ClusterNode]) -> None:
        """
        クラスタノードから固有表現とドキュメントタイプを抽出します。

        各クラスタのラベル、要約、ドキュメントタイトルを基に、LLMを使用して
        以下の情報を抽出し、ノードに設定します：
        - named_entities: クラスタに関連する固有表現のリスト
        - doc_types: クラスタに含まれるドキュメントタイプのリスト

        Args:
            data_dir: データディレクトリパス
            logger: ログ出力用のロガーオブジェクト
            llmname: エンティティ抽出に使用するLLMの名前
            nodes: 処理対象のクラスタノードのリスト
        """
        total_nodes = len(nodes)
        logger.debug(f"Extracting entities from {total_nodes} nodes...")

        for idx, n in enumerate(nodes, start=1):
            logger.debug(f"  Processing node {idx}/{total_nodes}: {n.node_id}")

            titles = []
            # Sample up to 15 leaf-doc titles from cards or text first lines
            for did in n.doc_ids[:15]:
                card = n.doc_cards.get(did) if n.doc_cards else None
                if card and card.get("title"):
                    titles.append(card["title"])
                else:
                    # Fall back to first line of document text
                    for txt_did, txt in zip(n.doc_ids, n.doc_texts):
                        if txt_did == did:
                            titles.append(txt.split("\n", 1)[0].strip())
                            break

            prompt = (
                "次のクラスタ情報から named_entities と doc_types をJSONで返してください。"
                "形式: {\"named_entities\": [..], \"doc_types\": [..]}\\n\\n"
                f"Label: {n.label or n.node_id}\\n"
                f"Summary: {n.summary[:1200]}\\n"
                f"Titles: {titles}"
            )
            raw = self._llm_chat_text(data_dir, logger, llmname, prompt)
            obj = self._extract_json_obj(raw)
            ents = obj.get("named_entities", [])
            dtypes = obj.get("doc_types", [])
            n.named_entities = [str(x).strip() for x in ents if str(x).strip()] if isinstance(ents, list) else []
            n.doc_types = [str(x).strip() for x in dtypes if str(x).strip()] if isinstance(dtypes, list) else []

        logger.debug(f"Completed extracting entities from {total_nodes} nodes.")

    def _node_path(self, node: ClusterNode) -> str:
        """
        ノードのルートからの階層パスを取得します。

        ノードから親をさかのぼり、ルートまでのパスをスラッシュ区切りの文字列として
        返します。例：「root/cluster1/cluster2」

        Args:
            node: クラスタノード

        Returns:
            str: スラッシュ区切りの階層パス
        """
        chain = [node]
        cur = node.primary_parent
        while cur is not None:
            chain.append(cur)
            cur = cur.primary_parent
        chain.reverse()
        return "/".join(c.node_id for c in chain)

    def _build_entity_index(self, nodes: List[ClusterNode], roots: List[ClusterNode],
                           num_related: int) -> Dict[str, Dict[str, Any]]:
        """
        クラスタに含まれるエンティティをインデックス化し、関連スキルを検出します。

        各エンティティについて、出現回数、スキルパス、関連スキルの情報を保持する
        インデックスを構築します。Jaccard類似度を使用して、共通エンティティが多い
        スキル同士を関連スキルとして判定します。

        Args:
            nodes: クラスタノードのリスト
            roots: ルートクラスタノードのリスト
            num_related: 各スキルに付与する関連スキルの最大数

        Returns:
            Dict[str, Dict[str, Any]]: エンティティをキーとした、以下を含む辞書：
                - count: エンティティの出現回数
                - skill_paths: 出現するスキルのパスリスト
                - skill_ids: 出現するスキルのIDリスト
        """
        entity_index: Dict[str, Dict[str, Any]] = defaultdict(
            lambda: {"count": 0, "skill_paths": [], "skill_ids": []}
        )
        node_path = {n.node_id: self._node_path(n) for n in nodes}

        for n in nodes:
            path = node_path[n.node_id]
            for ent in n.named_entities + n.doc_types:
                ent = ent.strip().lower()
                if not ent:
                    continue
                rec = entity_index[ent]
                rec["count"] += 1
                rec["skill_paths"].append(path)
                rec["skill_ids"].append(n.node_id)

        sets = {n.node_id: set(e.lower() for e in n.named_entities + n.doc_types) for n in nodes}
        paths = {n.node_id: node_path[n.node_id] for n in nodes}
        labels = {n.node_id: (n.label or n.node_id) for n in nodes}

        for n in nodes:
            my_ents = sets[n.node_id]
            if not my_ents:
                continue
            candidates = []
            for other in nodes:
                if other.node_id == n.node_id:
                    continue
                other_ents = sets[other.node_id]
                if not other_ents:
                    continue
                inter = my_ents & other_ents
                if not inter:
                    continue
                union = my_ents | other_ents
                jacc = len(inter) / len(union)
                candidates.append((jacc, other, sorted(inter)))
            candidates.sort(key=lambda x: -x[0])
            related = []
            for jacc, other, shared in candidates[:num_related]:
                related.append({
                    "skill_id": other.node_id,
                    "label": labels[other.node_id],
                    "path": paths[other.node_id],
                    "shared_entities": shared,
                    "jaccard": round(jacc, 3),
                })
            n.related_skill_paths = related

        out: Dict[str, Dict[str, Any]] = {}
        for ent, rec in entity_index.items():
            seen_p = set()
            uniq_paths = []
            for p in rec["skill_paths"]:
                if p in seen_p:
                    continue
                seen_p.add(p)
                uniq_paths.append(p)
            seen_i = set()
            uniq_ids = []
            for i in rec["skill_ids"]:
                if i in seen_i:
                    continue
                seen_i.add(i)
                uniq_ids.append(i)
            out[ent] = {
                "count": rec["count"],
                "skill_paths": uniq_paths,
                "skill_ids": uniq_ids,
            }
        return out

    def _load_documents(self, input_path: Path, max_chars: int = 8000, recursive: bool = True,
                       preserve_id: bool = True, logger: logging.Logger = None) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
        """
        複数形式のドキュメントを読み込みます。

        テキスト(.txt)、マークダウン(.md)、JSON(.json)、JSONL(.jsonl)形式の
        ドキュメントを読み込み、ドキュメントID、テキスト、メタデータを抽出します。

        Args:
            input_path: 入力ファイルまたはディレクトリのパス
            max_chars: 1ドキュメントの最大文字数（デフォルト：8000）
            recursive: ディレクトリ配下を再帰的に検索するか（デフォルト：True）
            preserve_id: ドキュメント内のIDフィールドを保持するか（デフォルト：True）
            logger: ログ出力用のロガーオブジェクト（オプション）

        Returns:
            Tuple[List[str], List[str], List[Dict[str, Any]]]:
                - ドキュメントIDのリスト
                - ドキュメントテキストのリスト
                - メタデータ辞書のリスト
        """
        doc_ids = []
        doc_texts = []
        doc_metadata = []

        if input_path.is_file() and '.meta' not in input_path.parts:
            if input_path.suffix == ".jsonl":
                doc_ids, doc_texts, doc_metadata = self._load_jsonl_file(input_path, max_chars, preserve_id, logger)
            elif input_path.suffix == ".json":
                doc_ids, doc_texts, doc_metadata = self._load_json_file(input_path, max_chars, preserve_id, logger)
            elif input_path.suffix in (".md", ".txt"):
                text = input_path.read_text(encoding="utf-8", errors="replace")
                if text and text.strip():
                    doc_id = hashlib.sha256(
                        input_path.name.encode() + text[:200].encode()
                    ).hexdigest()[:16]
                    doc_ids.append(doc_id)
                    doc_texts.append(text[:max_chars])
                    doc_metadata.append({"source_file": str(input_path), "format": input_path.suffix.lstrip(".") })

        elif input_path.is_dir():
            pattern = "**/*" if recursive else "*"
            files = sorted(input_path.glob(pattern))

            for f in files:
                if not f.is_file() or '.meta' in f.parts:
                    continue

                if f.suffix == ".jsonl":
                    ids, texts, metadata = self._load_jsonl_file(f, max_chars, preserve_id, logger)
                    doc_ids.extend(ids)
                    doc_texts.extend(texts)
                    doc_metadata.extend(metadata)
                elif f.suffix in (".md", ".txt", ".json"):
                    ids, texts, metadata = self._load_file(f, max_chars, preserve_id, logger)
                    doc_ids.extend(ids)
                    doc_texts.extend(texts)
                    doc_metadata.extend(metadata)

        return doc_ids, doc_texts, doc_metadata

    def _load_file(self, file_path: Path, max_chars: int = 8000, preserve_id: bool = True,
                   logger: logging.Logger = None) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
        """
        単一ファイルからドキュメントを読み込みます。

        テキスト(.txt)、マークダウン(.md)、JSON(.json)形式に対応しています。
        ファイルの内容に応じて、適切なロード関数を呼び出します。

        Args:
            file_path: 入力ファイルのパス
            max_chars: 1ドキュメントの最大文字数（デフォルト：8000）
            preserve_id: ドキュメント内のIDフィールドを保持するか（デフォルト：True）
            logger: ログ出力用のロガーオブジェクト（オプション）

        Returns:
            Tuple[List[str], List[str], List[Dict[str, Any]]]:
                - ドキュメントIDのリスト
                - ドキュメントテキストのリスト
                - メタデータ辞書のリスト
        """
        doc_ids = []
        doc_texts = []
        doc_metadata = []

        try:
            if file_path.suffix == ".json":
                return self._load_json_file(file_path, max_chars, preserve_id, logger)

            elif file_path.suffix in (".md", ".txt"):
                text = file_path.read_text(encoding="utf-8", errors="replace")
                if text and text.strip():
                    doc_id = hashlib.sha256(
                        file_path.name.encode() + text[:200].encode()
                    ).hexdigest()[:16]
                    doc_ids.append(doc_id)
                    doc_texts.append(text[:max_chars])
                    doc_metadata.append({"source_file": str(file_path), "format": file_path.suffix.lstrip(".") })

        except Exception as e:
            if logger:
                logger.warning(f"Error loading file {file_path}: {e}")

        return doc_ids, doc_texts, doc_metadata

    def _load_jsonl_file(self, file_path: Path, max_chars: int = 8000, preserve_id: bool = True,
                        logger: logging.Logger = None) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
        """
        JSONL形式のファイルからドキュメントを読み込みます。

        1行につき1つのJSON形式のドキュメント定義を含むファイルを読み込みます。
        各行が"id"と"contents"フィールドを持つオブジェクトであることを想定しています。

        Args:
            file_path: 入力JSONLファイルのパス
            max_chars: 1ドキュメントの最大文字数（デフォルト：8000）
            preserve_id: ドキュメント内のIDフィールドを保持するか（デフォルト：True）
            logger: ログ出力用のロガーオブジェクト（オプション）

        Returns:
            Tuple[List[str], List[str], List[Dict[str, Any]]]:
                - ドキュメントIDのリスト
                - ドキュメントテキストのリスト
                - メタデータ辞書のリスト
        """
        doc_ids = []
        doc_texts = []
        doc_metadata = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        obj = json.loads(line)
                        if not isinstance(obj, dict):
                            continue

                        text = common.to_str(obj)
                        if not text or not str(text).strip():
                            continue

                        text = str(text)
                        doc_id = obj.get("id") if preserve_id else None
                        if not doc_id:
                            doc_id = hashlib.sha256(text[:500].encode()).hexdigest()[:16]

                        doc_ids.append(doc_id)
                        doc_texts.append(text[:max_chars])

                        metadata = {"source_file": str(file_path), "line": line_num, "format": "jsonl"}
                        if "url" in obj:
                            metadata["url"] = obj["url"]
                        if "article_type" in obj:
                            metadata["article_type"] = obj["article_type"]
                        doc_metadata.append(metadata)

                    except json.JSONDecodeError:
                        if logger:
                            logger.debug(f"Failed to parse line {line_num} in {file_path}")
                        continue

        except Exception as e:
            if logger:
                logger.warning(f"Error reading JSONL file {file_path}: {e}")

        return doc_ids, doc_texts, doc_metadata

    def _load_json_file(self, file_path: Path, max_chars: int = 8000, preserve_id: bool = True,
                       logger: logging.Logger = None) -> Tuple[List[str], List[str], List[Dict[str, Any]]]:
        """
        JSON形式のファイルからドキュメントを読み込みます。

        JSONファイルはリストまたは単一のオブジェクトに対応しています。
        リストの場合は各要素を、オブジェクトの場合はそれ自体をドキュメントとして扱います。

        Args:
            file_path: 入力JSONファイルのパス
            max_chars: 1ドキュメントの最大文字数（デフォルト：8000）
            preserve_id: ドキュメント内のIDフィールドを保持するか（デフォルト：True）
            logger: ログ出力用のロガーオブジェクト（オプション）

        Returns:
            Tuple[List[str], List[str], List[Dict[str, Any]]]:
                - ドキュメントIDのリスト
                - ドキュメントテキストのリスト
                - メタデータ辞書のリスト
        """
        doc_ids = []
        doc_texts = []
        doc_metadata = []

        try:
            data = json.loads(file_path.read_text(encoding="utf-8", errors="replace"))

            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        text = common.to_str(item)
                        if text and str(text).strip():
                            doc_id = item.get("id") if preserve_id else None
                            if not doc_id:
                                doc_id = hashlib.sha256(str(text)[:200].encode()).hexdigest()[:16]
                            doc_ids.append(doc_id)
                            doc_texts.append(str(text)[:max_chars])
                            doc_metadata.append({"source_file": str(file_path), "format": "json"})

            elif isinstance(data, dict):
                text = common.to_str(data)
                if text and str(text).strip():
                    doc_id = data.get("id") if preserve_id else None
                    if not doc_id:
                        doc_id = hashlib.sha256(str(text)[:200].encode()).hexdigest()[:16]
                    doc_ids.append(doc_id)
                    doc_texts.append(str(text)[:max_chars])
                    doc_metadata.append({"source_file": str(file_path), "format": "json"})

        except Exception as e:
            if logger:
                logger.warning(f"Error reading JSON file {file_path}: {e}")

        return doc_ids, doc_texts, doc_metadata

    def output_schema(self) -> type:
        """
        コマンドの出力スキーマをPydanticモデルで定義して返します。

        Returns:
            type: 出力結果の構造を定義したPydanticモデルクラス
        """
        class CompileInfo(pydantic.BaseModel):
            input_dir: str = pydantic.Field(description="入力ディレクトリ")
            ragcorpus_dir: str = pydantic.Field(description="コーパスディレクトリ")
            num_documents: int = pydantic.Field(description="ドキュメント数")
            llm_model: str = pydantic.Field(description="LLMモデル名")
            embed_model: str = pydantic.Field(description="埋め込みモデル名")
            p: int = pydantic.Field(description="分岐比")
            max_top: int = pydantic.Field(description="最大トップレベルスキル数")
            doc_summary_cards_enabled: bool = pydantic.Field(description="ドキュメント要約カード有効フラグ")
            compact: bool = pydantic.Field(description="コンパクト出力フラグ")
            dry_run: bool = pydantic.Field(description="ドライランフラグ")
            status: str = pydantic.Field(description="処理ステータス")

        class Data(resdata.Data):
            message: str = pydantic.Field(description="処理結果のメッセージ")
            documents_count: int = pydantic.Field(description="処理されたドキュメント数")
            ragcorpus_dir: str = pydantic.Field(description="コーパスディレクトリパス")
            compile_info: CompileInfo = pydantic.Field(description="コンパイル情報")
            elapsed_seconds: float = pydantic.Field(description="処理時間（秒）")

        class Result(resdata.Result):
            success: Union[Data, None] = pydantic.Field(default=None, description="成功した場合の結果")

        return Result
