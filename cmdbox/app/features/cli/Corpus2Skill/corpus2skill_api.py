"""Self-contained Corpus2Skill API surface for cmdbox CLI commands."""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable

import numpy as np


@dataclass
class ClusterNode:
    """A node in the hierarchy tree."""

    node_id: str
    level: int
    label: str = ""
    summary: str = ""
    embedding: np.ndarray | None = None
    children: list["ClusterNode"] = field(default_factory=list)
    doc_ids: list[str] = field(default_factory=list)
    doc_texts: list[str] = field(default_factory=list)

    primary_parent: "ClusterNode | None" = None
    secondary_parent: "ClusterNode | None" = None
    secondary_children: list["ClusterNode"] = field(default_factory=list)

    named_entities: list[str] = field(default_factory=list)
    doc_types: list[str] = field(default_factory=list)
    related_skill_paths: list[dict] = field(default_factory=list)
    exemplar_doc_ids: list[str] = field(default_factory=list)
    doc_cards: dict[str, dict] = field(default_factory=dict)


def _card_to_summary(card: dict) -> str:
    parts = [card.get("title", ""), card.get("one_line", "")]
    phrases = card.get("phrases") or []
    if phrases:
        parts.append("Key phrases: " + "; ".join(phrases))
    return "\n".join(p for p in parts if p)


def _kmeans_labels(normed: np.ndarray, k: int) -> np.ndarray:
    from sklearn.cluster import AgglomerativeClustering, KMeans

    try:
        km = KMeans(n_clusters=k, n_init=3, max_iter=100, random_state=42)
        return km.fit_predict(normed)
    except Exception:
        agg = AgglomerativeClustering(n_clusters=k)
        return agg.fit_predict(normed)


def cluster_level_soft(
    embeddings: np.ndarray,
    k: int,
    min_size: int = 1,
    soft_margin: float = 0.05,
) -> tuple[list[list[int]], dict[int, int]]:
    n = embeddings.shape[0]
    k = min(k, n)
    if k <= 1:
        return [list(range(n))], {}

    normed = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10)
    labels = _kmeans_labels(normed, k)

    clusters: dict[int, list[int]] = {}
    for idx, lab in enumerate(labels):
        clusters.setdefault(int(lab), []).append(idx)

    primary = [v for v in clusters.values() if len(v) >= min_size]
    orphans: list[int] = []
    for v in clusters.values():
        if len(v) < min_size:
            orphans.extend(v)

    if not primary:
        primary = [list(range(n))]

    centroids = []
    for cl in primary:
        c_emb = normed[cl].mean(axis=0)
        centroids.append(c_emb / (np.linalg.norm(c_emb) + 1e-10))
    centroids_arr = np.array(centroids)

    for oidx in orphans:
        sims = centroids_arr @ normed[oidx]
        best = int(np.argmax(sims))
        primary[best].append(oidx)

    secondary: dict[int, int] = {}
    if soft_margin > 0 and len(primary) >= 2:
        centroids = []
        for cl in primary:
            c_emb = normed[cl].mean(axis=0)
            centroids.append(c_emb / (np.linalg.norm(c_emb) + 1e-10))
        centroids_arr = np.array(centroids)

        item_to_primary = {}
        for ci, members in enumerate(primary):
            for m in members:
                item_to_primary[m] = ci

        sims_all = normed @ centroids_arr.T
        for i in range(n):
            row = sims_all[i]
            order = np.argsort(-row)
            top1, top2 = int(order[0]), int(order[1])
            pi = item_to_primary.get(i)
            if pi is None:
                continue
            if top1 != pi:
                if row[pi] - row[top1] >= -soft_margin:
                    continue
                secondary[i] = top1
                continue
            gap = row[top1] - row[top2]
            if gap < soft_margin:
                secondary[i] = top2

    return primary, secondary


def cluster_level(embeddings: np.ndarray, k: int, min_size: int = 1) -> list[list[int]]:
    primary, _ = cluster_level_soft(embeddings, k, min_size, soft_margin=0.0)
    return primary


def _sampled_member_excerpts(
    member_indices: list[int],
    current_nodes: list[ClusterNode],
    embeddings: np.ndarray,
    n_samples: int = 5,
    excerpt_chars: int = 400,
) -> str:
    if not member_indices:
        return ""
    member_embs = embeddings[member_indices]
    normed = member_embs / (np.linalg.norm(member_embs, axis=1, keepdims=True) + 1e-10)
    mean = normed.mean(axis=0)
    mean = mean / (np.linalg.norm(mean) + 1e-10)
    sims = normed @ mean
    order = np.argsort(-sims)
    top = [member_indices[int(j)] for j in order[: max(n_samples, 1)]]

    chunks = []
    for idx in top:
        node = current_nodes[idx]
        snippet = (node.summary or "").strip()[:excerpt_chars]
        if snippet:
            chunks.append(snippet)
    return "\n---\n".join(chunks)


def _aggregate_doc_content(
    children: list[ClusterNode],
) -> tuple[list[str], list[str], dict[str, dict]]:
    ids: list[str] = []
    texts: list[str] = []
    cards: dict[str, dict] = {}
    for child in children:
        ids.extend(child.doc_ids)
        texts.extend(child.doc_texts)
        if child.doc_cards:
            cards.update(child.doc_cards)
    return ids, texts, cards


def _apply_repartition(
    clusters: list[dict],
    changes: list[dict],
    current_nodes: list[ClusterNode],
    embeddings: np.ndarray,
    repartitioned_cluster_ids: set[str],
    level: int,
) -> tuple[list[dict], list[int]]:
    if not changes:
        return clusters, []

    id_to_cluster_idx = {c["cluster_id"]: i for i, c in enumerate(clusters)}
    node_id_to_global = {n.node_id: i for i, n in enumerate(current_nodes)}

    drop_indices: set[int] = set()
    new_clusters: list[dict] = []
    repart_counter = 0

    for change in changes:
        old_ids = change.get("old_cluster_ids") or []
        new_part = change.get("new_partition") or {}
        if not old_ids or not new_part:
            continue
        if any(oid in repartitioned_cluster_ids for oid in old_ids):
            continue
        if not all(oid in id_to_cluster_idx for oid in old_ids):
            continue

        union_indices: set[int] = set()
        for oid in old_ids:
            union_indices.update(clusters[id_to_cluster_idx[oid]]["member_indices"])
        union_node_ids = {current_nodes[i].node_id for i in union_indices}

        new_assignments: list[tuple[str, list[int]]] = []
        seen_indices: set[int] = set()
        for new_label, raw_id_list in new_part.items():
            if not isinstance(raw_id_list, list):
                continue
            mapped: list[int] = []
            for raw in raw_id_list:
                if raw not in union_node_ids:
                    continue
                gi = node_id_to_global.get(raw)
                if gi is None or gi in seen_indices:
                    continue
                mapped.append(gi)
                seen_indices.add(gi)
            if mapped:
                new_assignments.append((new_label, mapped))

        leftover = union_indices - seen_indices
        if not new_assignments:
            continue
        if leftover:
            normed = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-10)
            new_centroids = []
            for _, mems in new_assignments:
                c_emb = normed[mems].mean(axis=0)
                new_centroids.append(c_emb / (np.linalg.norm(c_emb) + 1e-10))
            new_centroids_arr = np.array(new_centroids)
            for li in leftover:
                sims = new_centroids_arr @ normed[li]
                best = int(np.argmax(sims))
                new_assignments[best][1].append(li)

        for oid in old_ids:
            drop_indices.add(id_to_cluster_idx[oid])
            repartitioned_cluster_ids.add(oid)

        for new_label, mems in new_assignments:
            cid = f"L{level}-CR{repart_counter}"
            repart_counter += 1
            new_clusters.append(
                {
                    "cluster_id": cid,
                    "member_indices": mems,
                    "secondary_member_indices": [],
                    "summary": None,
                    "repartitioned_from": list(old_ids),
                }
            )
            repartitioned_cluster_ids.add(cid)

    if not new_clusters:
        return clusters, []

    surviving = [c for i, c in enumerate(clusters) if i not in drop_indices]
    start = len(surviving)
    merged = surviving + new_clusters
    affected_new_indices = list(range(start, len(merged)))
    return merged, affected_new_indices


def build_hierarchy(
    doc_ids: list[str],
    doc_texts: list[str],
    embeddings: np.ndarray,
    p: int = 10,
    max_top: int = 10,
    min_cluster_size: int = 3,
    summarize_fn=None,
    summarize_batch_fn=None,
    embed_fn: Callable[..., np.ndarray] | None = None,
    soft_assignment: bool = True,
    soft_margin: float = 0.05,
    repartition_fn: Callable[[list[dict], int], dict] | None = None,
    doc_cards: dict[str, dict] | None = None,
) -> list[ClusterNode]:
    n = len(doc_ids)
    assert n == embeddings.shape[0]

    leaf_nodes = []
    for i, (did, txt) in enumerate(zip(doc_ids, doc_texts)):
        card = (doc_cards or {}).get(did)
        leaf_summary = txt[:500]
        if card:
            leaf_summary = _card_to_summary(card) or leaf_summary
        leaf = ClusterNode(
            node_id=f"doc-{did[:12]}",
            level=0,
            label=did,
            summary=leaf_summary,
            embedding=embeddings[i],
            doc_ids=[did],
            doc_texts=[txt],
        )
        if card:
            leaf.doc_cards = {did: card}
        leaf_nodes.append(leaf)

    current_nodes = leaf_nodes
    current_embeddings = embeddings.copy()
    level = 0
    repartitioned_cluster_ids: set[str] = set()

    while len(current_nodes) > max_top:
        level += 1
        k = max(max_top, math.ceil(len(current_nodes) / p))
        k = min(k, len(current_nodes))

        print(f"  Level {level}: clustering {len(current_nodes)} items → {k} clusters")

        if soft_assignment:
            prim_assign, sec_assign = cluster_level_soft(
                current_embeddings, k, min_cluster_size, soft_margin
            )
        else:
            prim_assign = cluster_level(current_embeddings, k, min_cluster_size)
            sec_assign = {}

        if not prim_assign:
            break

        clusters: list[dict] = []
        for ci, members in enumerate(prim_assign):
            clusters.append(
                {
                    "cluster_id": f"L{level}-C{ci}",
                    "member_indices": list(members),
                    "secondary_member_indices": [],
                    "summary": None,
                }
            )
        for item_idx, parent_ci in sec_assign.items():
            if 0 <= parent_ci < len(clusters):
                clusters[parent_ci]["secondary_member_indices"].append(item_idx)

        def _summarize(clusters_to_run: list[dict]) -> None:
            if not clusters_to_run:
                return
            inputs = [[current_nodes[i].summary for i in c["member_indices"]] for c in clusters_to_run]
            if summarize_batch_fn:
                summaries = summarize_batch_fn(inputs, level=level)
            elif summarize_fn:
                summaries = [summarize_fn(si, level=level) for si in inputs]
            else:
                summaries = [f"Cluster of {len(c['member_indices'])} items." for c in clusters_to_run]
            for c, s in zip(clusters_to_run, summaries):
                c["summary"] = s

        print(f"    Summarizing {len(clusters)} clusters concurrently...")
        _summarize(clusters)

        if repartition_fn is not None:
            eligible = [c for c in clusters if c["cluster_id"] not in repartitioned_cluster_ids]
            records = []
            for c in eligible:
                if not c.get("summary"):
                    continue
                records.append(
                    {
                        "cluster_id": c["cluster_id"],
                        "label": c["cluster_id"],
                        "summary": c["summary"],
                        "members": [
                            {
                                "id": current_nodes[i].node_id,
                                "title": next(
                                    (
                                        ln.strip()
                                        for ln in (current_nodes[i].summary or "").splitlines()
                                        if ln.strip()
                                    ),
                                    "",
                                ),
                            }
                            for i in c["member_indices"][:12]
                        ],
                    }
                )
            if records:
                try:
                    print(f"    Repartition pass over {len(records)} clusters...")
                    out = repartition_fn(records, level)
                    changes = (out or {}).get("changes") or []
                    if changes:
                        print(f"      LLM proposed {len(changes)} repartition change(s)")
                    clusters, affected = _apply_repartition(
                        clusters,
                        changes,
                        current_nodes,
                        current_embeddings,
                        repartitioned_cluster_ids,
                        level,
                    )
                    if affected:
                        _summarize([clusters[i] for i in affected])
                except Exception as e:
                    print(f"      repartition skipped: {e}")

        next_nodes: list[ClusterNode] = []
        next_embeddings: list[np.ndarray] = []
        for ci, c in enumerate(clusters):
            children = [current_nodes[i] for i in c["member_indices"]]
            secondary_children = [current_nodes[i] for i in c["secondary_member_indices"]]
            all_doc_ids, all_doc_texts, all_cards = _aggregate_doc_content(children)

            summary = c["summary"] or f"Cluster of {len(c['member_indices'])} items."
            if embed_fn:
                ctx = _sampled_member_excerpts(c["member_indices"], current_nodes, current_embeddings)
                try:
                    emb = embed_fn(summary, context=ctx)
                except TypeError:
                    emb = embed_fn(summary)
            else:
                member_embs = current_embeddings[c["member_indices"]]
                emb = member_embs.mean(axis=0)
                emb = emb / (np.linalg.norm(emb) + 1e-10)

            node_id = f"L{level}-C{ci}"
            node = ClusterNode(
                node_id=node_id,
                level=level,
                summary=summary,
                embedding=emb,
                children=children,
                secondary_children=secondary_children,
                doc_ids=all_doc_ids,
                doc_texts=all_doc_texts,
            )
            if all_cards:
                node.doc_cards = all_cards
            for ch in children:
                ch.primary_parent = node
            for sch in secondary_children:
                if sch.secondary_parent is None:
                    sch.secondary_parent = node
            next_nodes.append(node)
            next_embeddings.append(emb)

        if not next_nodes:
            break

        current_nodes = next_nodes
        current_embeddings = np.array(next_embeddings, dtype=np.float32)
        print(
            f"    → {len(current_nodes)} clusters (docs per cluster: "
            f"min={min(len(n.doc_ids) for n in current_nodes)}, "
            f"max={max(len(n.doc_ids) for n in current_nodes)}, "
            f"mean={sum(len(n.doc_ids) for n in current_nodes)/len(current_nodes):.0f})"
        )

    return current_nodes


def tree_stats(roots: list[ClusterNode]) -> dict:
    def _depth(node: ClusterNode) -> int:
        if not node.children:
            return 0
        return 1 + max(_depth(c) for c in node.children)

    def _count_nodes(node: ClusterNode) -> int:
        return 1 + sum(_count_nodes(c) for c in node.children)

    max_depth = max(_depth(r) for r in roots)
    total_nodes = sum(_count_nodes(r) for r in roots)
    total_docs = sum(len(r.doc_ids) for r in roots)
    total_secondary = 0
    for r in roots:
        stack = [r]
        while stack:
            n = stack.pop()
            total_secondary += len(n.secondary_children)
            stack.extend(n.children)

    return {
        "num_top_clusters": len(roots),
        "max_depth": max_depth,
        "total_nodes": total_nodes,
        "total_documents": total_docs,
        "total_secondary_stubs": total_secondary,
    }


_MAX_SKILL_NAME = 60


def _merge_unique_name(parent: str, child: str, max_len: int = _MAX_SKILL_NAME) -> str:
    combined = f"{parent}__{child}" if parent else child
    if len(combined) <= max_len:
        return combined
    import hashlib

    h = hashlib.md5(combined.encode("utf-8")).hexdigest()[:6]
    keep = max_len - len(h) - 1
    keep = max(keep, 1)
    head = combined[: keep // 2]
    tail = combined[-(keep - len(head)) :]
    return f"{head}~{tail}-{h}" if tail else f"{head}-{h}"


def _safe_name(text: str, prefix: str = "", max_len: int = 50) -> str:
    name = (text or "").lower().strip()
    name = re.sub(r"[^a-z0-9\s-]", "", name)
    name = re.sub(r"\s+", "-", name)
    name = name.strip("-")[:max_len]
    if prefix:
        name = f"{prefix}-{name}" if name else prefix
    return name or prefix or "item"


def build_skill_tree(
    roots: list[ClusterNode],
    output_dir: Path,
    doc_content: dict[str, str] | None = None,
    doc_cards: dict[str, dict] | None = None,
    compact: bool = False,
    rich_index: bool = True,
    exemplars: bool = True,
    related_skills: bool = True,
    entity_index: dict | None = None,
) -> Path:
    skills_dir = output_dir / ".claude" / "skills"
    skills_dir.mkdir(parents=True, exist_ok=True)

    node_paths: dict[str, str] = {}
    render_ctx = {
        "doc_cards": doc_cards or {},
        "rich_index": rich_index,
        "exemplars": exemplars,
        "related_skills": related_skills,
        "node_paths": node_paths,
        "skills_dir": skills_dir,
    }

    for i, root in enumerate(roots):
        skill_name = _safe_name(root.label, prefix=f"skill-{i:02d}")
        root._folder_name = skill_name
        node_paths[root.node_id] = skill_name
        _assign_paths(root, parent_rel=skill_name, compact=compact, node_paths=node_paths)

    for root in roots:
        skill_dir = skills_dir / node_paths[root.node_id]
        skill_dir.mkdir(exist_ok=True)
        _write_node(root, skill_dir, depth=0, compact=compact, ctx=render_ctx)
        if entity_index:
            (skill_dir / "entity_index.json").write_text(
                json.dumps(entity_index, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )

    if doc_content:
        doc_store_path = output_dir / "documents.json"
        doc_store_path.write_text(json.dumps(doc_content, ensure_ascii=False), encoding="utf-8")
        print(f"  Document store: {doc_store_path} ({len(doc_content)} docs)")

    node_paths_path = output_dir / "node_paths.json"
    node_paths_path.write_text(json.dumps(node_paths, ensure_ascii=False, indent=2), encoding="utf-8")

    total_skills = sum(1 for _ in skills_dir.iterdir() if _.is_dir())
    total_nav = sum(1 for _ in skills_dir.rglob("*") if _.is_file() and _.name in ("SKILL.md", "INDEX.md"))
    print(f"  Built {total_skills} skills ({total_nav} nav files) in {skills_dir}")
    return skills_dir


def _nav_filename(depth: int) -> str:
    return "SKILL.md" if depth == 0 else "INDEX.md"


def _assign_paths(
    node: ClusterNode,
    parent_rel: str,
    compact: bool,
    node_paths: dict[str, str],
) -> None:
    if not node.children:
        return
    for ci, child in enumerate(node.children):
        if not child.children:
            continue
        if compact and _is_near_leaf(child):
            continue
        child_name = _safe_name(child.label, prefix=f"group-{ci:02d}")
        parent_unique = getattr(node, "_folder_name", None) or parent_rel.split("/")[-1]
        child._folder_name = _merge_unique_name(parent_unique, child_name)
        child_rel = f"{parent_rel}/{child_name}"
        node_paths[child.node_id] = child_rel
        _assign_paths(child, child_rel, compact, node_paths)


def _write_node(node: ClusterNode, node_dir: Path, depth: int, compact: bool, ctx: dict):
    if node.children:
        _write_branch_node(node, node_dir, depth, compact, ctx)
    else:
        _write_leaf_node(node, node_dir, depth, ctx)


def _is_near_leaf(node: ClusterNode) -> bool:
    return bool(node.children) and all(not c.children for c in node.children)


def _doc_row(doc_id: str, doc_text: str, ctx: dict) -> str:
    cards = ctx["doc_cards"]
    card = cards.get(doc_id)
    first_line = doc_text.split("\n", 1)[0].strip() if doc_text else ""

    if ctx["rich_index"] and card:
        title = card.get("title") or first_line or doc_id
        one_line = card.get("one_line") or ""
        phrases = "; ".join(card.get("phrases") or [])
        pieces = [f"`{doc_id}`", title]
        if one_line:
            pieces.append(one_line)
        if phrases:
            pieces.append(f"[{phrases}]")
        return " — ".join(pieces)
    return f"`{doc_id}`: {first_line}"


def _secondary_row(child: ClusterNode, ctx: dict) -> str:
    primary_id = None
    if child.primary_parent is not None:
        primary_id = child.primary_parent.node_id
    primary_path = ctx["node_paths"].get(primary_id, "?") if primary_id else "?"
    label = child.label or child.node_id
    return f"@see `{label}` ({len(child.doc_ids)} docs) — primary parent: `{primary_path}`"


def _write_branch_node(
    node: ClusterNode,
    node_dir: Path,
    depth: int,
    compact: bool,
    ctx: dict,
):
    child_entries: list[dict] = []
    merged_sections: list[dict] = []

    for ci, child in enumerate(node.children):
        if child.children:
            if compact and _is_near_leaf(child):
                merged_sections.append(
                    {
                        "label": child.label or child.node_id,
                        "summary": child.summary,
                        "num_docs": len(child.doc_ids),
                        "child_node": child,
                    }
                )
                child_entries.append(
                    {
                        "type": "merged_section",
                        "label": child.label or child.node_id,
                        "summary": child.summary,
                        "num_docs": len(child.doc_ids),
                    }
                )
            else:
                child_rel = ctx["node_paths"].get(child.node_id)
                if child_rel:
                    child_name = child_rel.split("/")[-1]
                else:
                    child_name = _safe_name(child.label, prefix=f"group-{ci:02d}")
                    parent_unique = getattr(node, "_folder_name", None) or node_dir.name
                    child._folder_name = _merge_unique_name(parent_unique, child_name)
                    ctx["node_paths"][child.node_id] = str((node_dir / child_name).relative_to(ctx["skills_dir"]))
                child_dir = node_dir / child_name
                child_dir.mkdir(exist_ok=True)
                _write_node(child, child_dir, depth + 1, compact, ctx)
                child_entries.append(
                    {
                        "type": "directory",
                        "name": child_name,
                        "summary": child.summary,
                        "num_docs": len(child.doc_ids),
                    }
                )
        else:
            for doc_id, doc_text in zip(child.doc_ids, child.doc_texts):
                child_entries.append({"type": "doc_ref", "doc_id": doc_id, "doc_text": doc_text})

    fname = _nav_filename(depth)
    skill_md = _format_skill_md(node, child_entries, depth, merged_sections, ctx)
    (node_dir / fname).write_text(skill_md, encoding="utf-8")


def _write_leaf_node(node: ClusterNode, node_dir: Path, depth: int, ctx: dict):
    child_entries: list[dict] = []
    for doc_id, doc_text in zip(node.doc_ids, node.doc_texts):
        child_entries.append({"type": "doc_ref", "doc_id": doc_id, "doc_text": doc_text})

    fname = _nav_filename(depth)
    skill_md = _format_skill_md(node, child_entries, depth, None, ctx)
    (node_dir / fname).write_text(skill_md, encoding="utf-8")


def _format_skill_md(
    node: ClusterNode,
    child_entries: list[dict],
    depth: int,
    merged_sections: list[dict] | None,
    ctx: dict,
) -> str:
    folder_name = getattr(node, "_folder_name", None)
    name = folder_name if folder_name else (node.label or node.node_id)
    desc_oneliner = " ".join((node.summary or "").split())[:500]
    lines = [
        "---",
        f"name: {name}",
        "description: >",
        f"  {desc_oneliner}",
        f"level: {node.level}",
        f"num_documents: {len(node.doc_ids)}",
        "---",
        "",
        "## Overview",
        "",
        node.summary,
        "",
    ]

    if ctx["related_skills"] and node.related_skill_paths:
        lines.append("## Related skills")
        lines.append("")
        lines.append(
            "If your query overlaps with these sibling skills, cross-jump rather than digging deeper here:"
        )
        lines.append("")
        for rel in node.related_skill_paths:
            shared = ", ".join(rel.get("shared_entities") or [])
            fs_path = ctx["node_paths"].get(rel.get("skill_id"), rel.get("path", "?"))
            lines.append(
                f"- `{fs_path}` ({rel.get('label', '?')}) — "
                f"shared: {shared} [overlap={rel.get('jaccard', 0):.2f}]"
            )
        lines.append("")

    if ctx["related_skills"] and (node.named_entities or node.doc_types):
        lines.append("## Entities & document types")
        lines.append("")
        if node.named_entities:
            lines.append("- entities: " + ", ".join(node.named_entities))
        if node.doc_types:
            lines.append("- doc types: " + ", ".join(node.doc_types))
        lines.append("")

    if ctx["exemplars"] and node.exemplar_doc_ids:
        lines.append("## Example documents in this skill")
        lines.append("")
        lines.append("Representative items — reading one gives you the shape of content here:")
        lines.append("")
        cards = ctx["doc_cards"]
        for did in node.exemplar_doc_ids:
            card = cards.get(did)
            if card:
                title = card.get("title") or did
                one = card.get("one_line") or ""
                lines.append(f"- `{did}` — {title} — {one}")
            else:
                lines.append(f"- `{did}`")
        lines.append("")

    lines.append("## Contents")
    lines.append("")

    dirs = [e for e in child_entries if e["type"] == "directory"]
    docs = [e for e in child_entries if e["type"] == "doc_ref"]

    if dirs:
        lines.append("### Sub-groups (directories)")
        lines.append("")
        lines.append("Read the INDEX.md in each sub-group to understand what it covers.")
        lines.append("")
        for d in dirs:
            lines.append(f"- **{d['name']}/** ({d['num_docs']} docs): {d['summary']}")
        lines.append("")

    if docs:
        lines.append(f"### Documents ({len(docs)} items)")
        lines.append("")
        lines.append("Use `get_document` with the doc_id to read full content.")
        if ctx["rich_index"] and ctx["doc_cards"]:
            lines.append("Rows: `id` — title — one-line summary — [distinctive phrases]")
        lines.append("")
        for d in docs:
            lines.append(f"- {_doc_row(d['doc_id'], d['doc_text'], ctx)}")
        lines.append("")

    if merged_sections:
        lines.append(f"### Merged sub-groups ({len(merged_sections)} groups below)")
        lines.append("")
        lines.append("Use `get_document` with any doc_id to read full content.")
        lines.append("")
        for sec in merged_sections:
            child_node = sec["child_node"]
            lines.append(f"#### {sec['label']} ({sec['num_docs']} docs)")
            lines.append("")
            lines.append(sec["summary"])
            lines.append("")
            for doc_id, doc_text in zip(child_node.doc_ids, child_node.doc_texts):
                lines.append(f"- {_doc_row(doc_id, doc_text, ctx)}")
            lines.append("")

    if node.secondary_children:
        lines.append("### See also (also relevant here)")
        lines.append("")
        lines.append("These items have their primary entry elsewhere but are also relevant to this skill:")
        lines.append("")
        for sc in node.secondary_children:
            lines.append(f"- {_secondary_row(sc, ctx)}")
        lines.append("")

    return "\n".join(lines)


__all__ = ["ClusterNode", "build_hierarchy", "tree_stats", "build_skill_tree"]
