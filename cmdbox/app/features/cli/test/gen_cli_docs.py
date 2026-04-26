"""コマンドリファレンスRST生成ツール。

gen_cli_spec.py が生成した cli-command-specifications.json を元に、
docs_src/docs/ 配下のコマンドリファレンスRSTファイルを新規生成します。

既存のRSTファイルがある場合は上書きします。

使い方 (Python API):
    from cmdbox.app.features.cli.test import gen_cli_docs
    result = gen_cli_docs.generate(
        specs_dir=Path("Specifications"),
        docs_dir=Path("docs_src/docs"),
        mode_filter=None,   # None で全モード
        cmd_filter=None,    # None で全コマンド
        dry_run=False,
    )
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any


def generate(
    specs_dir: Path,
    docs_dir: Path,
    mode_filter: str | None = None,
    cmd_filter: list[str] | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    """詳細設計書の内容からコマンドリファレンスRSTを生成します。

    Args:
        specs_dir: Specificationsディレクトリのパス（cli-command-specifications.json が存在する）
        docs_dir: cmd_*.rst を出力するディレクトリのパス
        mode_filter: 生成対象をモード名でフィルタ。None で全モード
        cmd_filter: 生成対象をコマンド名でフィルタ。None で全コマンド
        dry_run: True のとき実際にはファイルを書き込まない（変更内容のみ返す）

    Returns:
        generated, skipped, errors を含む辞書
    """
    json_file = specs_dir / "cli-command-specifications.json"
    if not json_file.exists():
        return dict(
            generated=[],
            skipped=[],
            errors=[f"cli-command-specifications.json not found: {json_file}"],
        )

    documents: list[dict[str, Any]] = json.loads(json_file.read_text(encoding="utf-8"))

    # フィルタ適用
    if mode_filter:
        documents = [d for d in documents if d.get("mode") == mode_filter]
    if cmd_filter:
        documents = [d for d in documents if d.get("cmd") in cmd_filter]

    # mode -> list of spec でグループ化（コマンド順を保持）
    by_mode: dict[str, list[dict[str, Any]]] = {}
    for doc in documents:
        mode = doc["mode"]
        by_mode.setdefault(mode, []).append(doc)

    generated: list[str] = []
    skipped: list[str] = []
    errors: list[str] = []

    for mode, specs in sorted(by_mode.items()):
        rst_path = docs_dir / f"cmd_{mode}.rst"
        content = _render_rst(mode, specs)

        if not dry_run:
            docs_dir.mkdir(parents=True, exist_ok=True)
            rst_path.write_text(content, encoding="utf-8")
        generated.append(rst_path.name)
        print(f"{'[dry-run] ' if dry_run else ''}Generated: {rst_path.name}")

    return dict(generated=generated, skipped=skipped, errors=errors)


def _render_rst(mode: str, specs: list[dict[str, Any]]) -> str:
    """1モード分のRSTコンテンツを生成します。"""
    lines: list[str] = []

    # ファイルヘッダ
    lines.append(".. -*- coding: utf-8 -*-\n")
    lines.append("\n")

    page_title = f"Command Reference ( {mode} mode )"
    title_bar = "*" * len(page_title)
    lines.append(f"{title_bar}\n")
    lines.append(f"{page_title}\n")
    lines.append(f"{title_bar}\n")
    lines.append("\n")
    lines.append(f"List of {mode} mode commands.\n")

    for spec in specs:
        lines.append("\n")
        lines.extend(_render_command_section(mode, spec))

    return "".join(lines)


def _render_command_section(mode: str, spec: dict[str, Any]) -> list[str]:
    """1コマンド分のRSTセクションを生成します。"""
    cmd = spec["cmd"]
    desc_en = spec.get("description_en", "").strip()
    parameters = spec.get("parameters", [])

    lines: list[str] = []

    # セクション見出し
    section_title = f"{mode} ( {cmd} ) : ``cmdbox -m {mode} -c {cmd} <Option>``"
    underline = "=" * len(section_title)
    lines.append(f"{section_title}\n")
    lines.append(f"{underline}\n")
    lines.append("\n")

    # 概要説明
    if desc_en:
        for sentence in _split_sentences(desc_en):
            lines.append(f"- {sentence}\n")
        lines.append("\n")

    # パラメータがなければ csv-table を省略
    if not parameters:
        return lines

    # csv-table
    lines.append(".. csv-table::\n")
    lines.append("    :widths: 20, 10, 70\n")
    lines.append("    :header-rows: 1\n")
    lines.append("\n")
    lines.append('    "Option","Required","Description"\n')

    for param in parameters:
        name = param.get("name", "")
        short = param.get("short")
        required = param.get("required", False)
        desc = param.get("description_en", "").strip()

        if short:
            opt_display = f"-{short}, --{name} <{name}>"
        else:
            opt_display = f"--{name} <{name}>"

        required_str = "required" if required else ""
        lines.append(f'    "{_escape_csv(opt_display)}","{required_str}","{_escape_csv(desc)}"\n')

    return lines


def _split_sentences(text: str) -> list[str]:
    """英文を文単位に分割します（ピリオド＋スペースで区切る）。"""
    sentences = re.split(r"(?<=\.)\s+", text.strip())
    return [s.strip() for s in sentences if s.strip()]


def _escape_csv(text: str) -> str:
    """RST csv-table内でダブルクォートをエスケープします。"""
    return text.replace('"', '""')
