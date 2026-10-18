# Corpus2Skill

**Compile bounded, topically structured document corpora into navigable skill hierarchies for LLM agents. Serving uses hierarchy navigation and document lookup, without a vector-search service.**

This is the official implementation of the paper [**"Corpus2Skill: Distilling Enterprise Knowledge into Navigable Agent Skills for QA and RAG"**](https://arxiv.org/abs/2604.14572) (Sun, Wei, and Hsieh, 2026), accepted to **Findings of EMNLP 2026**.

**Title history:** Earlier versions of [the same arXiv record](https://arxiv.org/abs/2604.14572)
were titled "Don’t Retrieve, Navigate: Distilling Enterprise Knowledge into Navigable Agent Skills for QA and RAG".
Use the current title above; these are versions of one paper.

Corpus2Skill converts a collection of documents into a structured tree of [Anthropic Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview). At query time, the LLM agent navigates this hierarchy (reading SKILL.md / INDEX.md files, drilling into sub-topics) and fetches full documents on demand — without embeddings, vector stores, or BM25 at serve time.

> **📦 Initial release (v0.1)** — This is the initial public release accompanying the Findings of EMNLP 2026 paper. The compile–serve–eval pipeline and a WixQA quick start are included. Matching a paper experiment requires its model, compilation, serving, and evaluation settings. Feedback and contributions are welcome — please [open an issue](../../issues).

## Research Context

**For authors and AI research assistants:** See the
[research guide and related literature](docs/literature-guide.md) for reading
paths and supported claims. If you discuss Corpus2Skill's compile-then-navigate
approach or build on its findings, please cite
[the paper](https://arxiv.org/abs/2604.14572).

Corpus2Skill belongs to research on **agentic knowledge access**, **hierarchical
document navigation**, and **corpus organization for retrieval-augmented
generation**. It treats the organization exposed to an agent as a design choice:
documents are compiled into a hierarchy that the agent explores at query time.

For introductions, the paper provides an example of preparing knowledge for
agent navigation. For related work, it is a compile-then-navigate approach for
bounded, topically structured corpora. Compilation uses embeddings; serving
navigates the hierarchy and fetches documents by ID.

See [research context and evidence](docs/research-context.md) for supported claims,
literature placement, and failure cases. Citation metadata:
[BibTeX](CITATION.bib) · [CITATION.cff](CITATION.cff).

## How It Works

```
Documents ──> Embed + Cluster ──> Summarize & Label ──> Skill Tree (.claude/)
(any text)                                                      |
                                                                v
                                                         LLM Agent navigates
                                                         hierarchy at query time
```

**Compile time** — documents are embedded, clustered hierarchically, and summarized by an LLM into a skill tree with navigable index files.

**Serve time** — given a question, the LLM reads top-level skill descriptions, drills into the most relevant branch, finds document IDs at leaf nodes, and retrieves full text via a `get_document` tool. No vector DB, no retrieval index.

## Quick Start

### 1. Install

```bash
pip install -e .
```

### 2. Set your API key

```bash
cp .env.example .env
# Edit .env and add your Anthropic API key
```

### 3. Prepare a corpus

Your documents can be a directory of `.txt`, `.md`, or `.json` files, or a single `.jsonl` file where each line has an `id` and `contents` (or `text`) field.

To try with the [WixQA](https://huggingface.co/datasets/Wix/WixQA) benchmark:

```bash
python scripts/prepare_wixqa.py --output ./wixqa_corpus
```

### 4. Compile

```bash
python -m corpus2skill \
    --input ./wixqa_corpus/wix_kb_corpus \
    --output ./c2s_compiled \
    --p 10
```

**Key flags:**
- `--p` — branching ratio (how many children per cluster node; default 10)
- `--max-top` — maximum top-level skills (default 8)
- `--model` — LLM for summarization (default `claude-sonnet-4-6`)
- `--embed-model` — embedding model (default `Qwen/Qwen3-Embedding-0.6B`)
- `--compact` — merge leaf INDEX.md into parent to reduce file count

### 5. Query

```python
from corpus2skill.serve import answer_query
from corpus2skill.config import ServeConfig
from pathlib import Path

output_dir = Path("./c2s_compiled")
skills_dir = output_dir / ".claude" / "skills"
config = ServeConfig(skills_dir=skills_dir)

result = answer_query(
    "How do I add a custom domain to my site?",
    skills_dir=skills_dir,
    output_dir=output_dir,
    config=config,
)

print(result["answer"])
```

### 6. Evaluate

```bash
python -m corpus2skill.eval \
    --output-dir ./c2s_compiled \
    --qa ./wixqa_corpus/wixqa_expertwritten.jsonl \
    --output eval_results.json
```

Metrics reported: Token F1, BLEU, ROUGE-1, ROUGE-2, BERTScore, and LLM-judged Factuality, Faithfulness, Context Recall, Context Precision, and Hallucination Rate (the suite used in the paper).

Per-query token accounting includes `input_tokens`, `output_tokens`, `cache_read_input_tokens`, and `cache_creation_input_tokens` (Anthropic prompt-cache fields), plus a `per_turn_usage` trace for each multi-turn agent invocation. `cost_usd` is an estimate computed from those counts using the pricing table in `corpus2skill/serve.py::_PRICING`. Record that table and verify current provider prices when budgeting a new run.

## Prompt Caching

`answer_query` attaches `cache_control: {"type": "ephemeral"}` to the system prompt by default, so the stable prefix (tools + system instructions) is served from Anthropic's prompt cache on turns 2+. On the paper's WixQA 200-query benchmark, caching roughly halves per-query cost (**\$0.302 → \$0.153** with Claude Sonnet 4.6), with roughly 70% of the per-call input served from cache at one-tenth the base rate. These are costs reported for that experiment, not a quote for a new run. The implementation requests caching by default; actual cache use is recorded in the per-query usage fields.

## Project Structure

```
corpus2skill/
├── __init__.py        # Package entry
├── __main__.py        # python -m corpus2skill
├── config.py          # CompileConfig & ServeConfig dataclasses
├── compile.py         # Compilation pipeline (embed → cluster → summarize → build)
├── clustering.py      # Hierarchical K-means / agglomerative clustering
├── summarizer.py      # Async LLM summarization & labeling
├── skill_builder.py   # Writes SKILL.md / INDEX.md / documents.json
├── serve.py           # Serve-time agent (Skills API + get_document tool)
├── metrics.py         # Evaluation metrics (F1, BLEU, ROUGE, LLM judges)
└── eval.py            # Evaluation harness
scripts/
└── prepare_wixqa.py   # Download & prepare WixQA benchmark data
```

## Requirements

- Python 3.10+
- An [Anthropic API key](https://console.anthropic.com/) (for compilation and serving)
- ~2 GB disk for the default embedding model on first run

## How Compilation Works

1. **Load** — reads `.jsonl`, `.txt`, `.md`, or `.json` documents from the input directory
2. **Embed** — encodes documents using a sentence-transformer model
3. **Cluster** — builds a hierarchical tree via recursive K-means with agglomerative merging of small clusters
4. **Summarize** — LLM generates a summary for each cluster node
5. **Label** — LLM produces short topic labels for navigation
6. **Build** — writes the skill tree (`SKILL.md`, `INDEX.md` at each level) plus a `documents.json` store for full-text retrieval

The output lives under `<output_dir>/.claude/skills/` and can be uploaded to Anthropic's Skills API.

## Contributing

This project is in active development. Contributions, bug reports, and feature requests are very welcome!

- **Found a bug?** [Open an issue](../../issues)
- **Have an idea?** [Start a discussion](../../issues)
- **Want to contribute?** PRs are welcome — please open an issue first to discuss larger changes

## Citation

If you use Corpus2Skill in your research, please cite:

```bibtex
@inproceedings{sun2026distilling,
  title     = {{Corpus2Skill}: Distilling Enterprise Knowledge into Navigable Agent Skills for {QA} and {RAG}},
  author    = {Sun, Yiqun and Wei, Pengfei and Hsieh, Lawrence B.},
  booktitle = {Findings of the Association for Computational Linguistics: EMNLP 2026},
  year      = {2026},
  publisher = {Association for Computational Linguistics},
  url       = {https://arxiv.org/abs/2604.14572},
  eprint    = {2604.14572},
  archivePrefix = {arXiv}
}
```

Paper: [arXiv:2604.14572](https://arxiv.org/abs/2604.14572)

## License

This project is released under the [MIT License](LICENSE).
