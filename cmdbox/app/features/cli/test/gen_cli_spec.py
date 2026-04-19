"""CLIコマンド詳細設計書生成ツール。

cmdboxを拡張して作成したコマンドでも利用できるよう、
フィーチャーパッケージ名や出力先をパラメータとして受け取ります。

使い方 (コマンドライン):
    python -m cmdbox.tools.test.generate_cli_specifications \\
        --feature-package myapp.app.features.cli \\
        --output-dir path/to/Specifications \\
        --root-dir path/to/project

使い方 (Python API):
    from cmdbox.tools.test.generate_cli_specifications import generate
    generate(
        feature_package="myapp.app.features.cli",
        output_dir=Path("path/to/Specifications"),
        root_dir=Path("path/to/project"),
        appcls=MyApp,
        ver=my_version_module,
    )
"""
from __future__ import annotations

import argparse
import ast
import importlib
import inspect
import json
import textwrap
from collections import OrderedDict, defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

from cmdbox.app import feature as feature_module
from cmdbox.app.commons import module as module_loader


TYPE_LABELS = {
    "int": "整数",
    "float": "浮動小数",
    "bool": "真偽値",
    "str": "文字列",
    "date": "日付",
    "datetime": "日時",
    "dict": "辞書",
    "text": "複数行文字列",
    "file": "ファイル",
    "dir": "ディレクトリ",
    "passwd": "パスワード",
    "mlist": "複数選択リスト",
}

RESULT_VAR_NAMES = {"msg", "ret", "res", "row", "result"}

REDIS_LABELS = {
    feature_module.Feature.USE_REDIS_FALSE: "不要",
    feature_module.Feature.USE_REDIS_MEIGHT: "任意",
    feature_module.Feature.USE_REDIS_TRUE: "必須",
}


@dataclass
class MethodInfo:
    name: str
    defining_class: str
    docstring: str
    steps: list[str]
    result_keys: list[str]
    statuses: list[str]
    source_lines: str


def generate(
    feature_package: str,
    output_dir: Path,
    root_dir: Path,
    prefix: str = "cmdbox_",
    appcls: Any = None,
    ver: Any = None,
    language: str = "ja_JP",
) -> list[dict[str, Any]]:
    """フィーチャーパッケージからCLIコマンド仕様を生成します。

    Args:
        feature_package: フィーチャーを含むPythonパッケージ名
                         (例: "cmdbox.app.features.cli", "myapp.app.features.cli")
        output_dir: 仕様書の出力先ディレクトリ
        root_dir: プロジェクトルートディレクトリ (ソースファイルの相対パス計算に使用)
        prefix: フィーチャーモジュールのファイル名プレフィックス (デフォルト: "cmdbox_")
        appcls: アプリケーションクラス (省略時はCmdBoxAppを使用)
        ver: バージョンモジュール (省略時はcmdbox.versionを使用)
        language: 言語設定 (デフォルト: "ja_JP")

    Returns:
        生成された仕様書の辞書リスト
    """
    if appcls is None:
        from cmdbox.app.app import CmdBoxApp
        appcls = CmdBoxApp
    if ver is None:
        from cmdbox import version as _ver
        ver = _ver

    docs_dir = output_dir / "cli"
    index_file = output_dir / "README.md"
    json_file = output_dir / "cli-command-specifications.json"

    features = module_loader.load_features(
        feature_package,
        prefix=prefix,
        excludes=[],
        appcls=appcls,
        ver=ver,
        language=language,
    )

    output_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(exist_ok=True)

    documents: list[dict[str, Any]] = []
    for mode in sorted(features):
        for cmd in sorted(features[mode]):
            opt = dict(features[mode][cmd])
            feature_obj = opt.pop("feature")
            documents.append(
                build_command_spec(mode, cmd, feature_obj, opt, docs_dir, root_dir)
            )

    _write_documents(documents)
    _write_index(documents, index_file, json_file, output_dir)
    json_file.write_text(
        json.dumps(documents, ensure_ascii=False, indent=2, default=_json_default),
        encoding="utf-8",
    )

    print(f"generated {len(documents)} command specifications")
    print(index_file)
    return documents


def build_command_spec(
    mode: str,
    cmd: str,
    feature_obj: Any,
    option_def: dict[str, Any],
    docs_dir: Path,
    root_dir: Path,
) -> dict[str, Any]:
    """フィーチャーオブジェクトから完全なコマンド仕様を構築します。

    Args:
        mode: コマンドモード (例: 'app', 'sv')
        cmd: コマンド名
        feature_obj: フィーチャーオブジェクトのインスタンス
        option_def: フィーチャーのオプション定義
        docs_dir: マークダウン出力先ディレクトリ
        root_dir: プロジェクトルートディレクトリ

    Returns:
        完全なコマンド仕様を含む辞書
    """
    cls = feature_obj.__class__
    source_file = Path(inspect.getsourcefile(cls) or "")
    try:
        relative_source = source_file.relative_to(root_dir).as_posix()
    except ValueError:
        relative_source = source_file.as_posix()
    file_text = source_file.read_text(encoding="utf-8")
    tree = ast.parse(file_text)

    method_infos = {
        name: collect_method_info(cls, source_file, name)
        for name in ["apprun", "svrun", "is_cluster_redirect"]
    }
    helper_methods = collect_helper_methods(cls, source_file)

    output_path = docs_dir / mode / f"{cmd}.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    parameter_specs = _normalize_parameters(option_def.get("choice", []))
    status_candidates = _ordered_unique(
        method_infos["apprun"].statuses + method_infos["svrun"].statuses
    )
    result_keys = _ordered_unique(
        method_infos["apprun"].result_keys + method_infos["svrun"].result_keys
    )

    try:
        output_file_rel = output_path.relative_to(root_dir).as_posix()
    except ValueError:
        output_file_rel = output_path.as_posix()

    spec = {
        "mode": mode,
        "cmd": cmd,
        "description_ja": option_def.get("description_ja", ""),
        "description_en": option_def.get("description_en", ""),
        "class_name": cls.__name__,
        "module_name": cls.__module__,
        "base_classes": [base.__name__ for base in cls.__mro__[1:] if base is not object],
        "source_file": relative_source,
        "output_file": output_file_rel,
        "use_redis": option_def.get("use_redis"),
        "nouse_webmode": bool(option_def.get("nouse_webmode", False)),
        "use_agent": bool(option_def.get("use_agent", False)),
        "cluster_redirect": _resolve_cluster_redirect(feature_obj, method_infos["is_cluster_redirect"]),
        "parameters": parameter_specs,
        "statuses": status_candidates,
        "result_keys": result_keys,
        "method_infos": {
            key: {
                "defining_class": info.defining_class,
                "docstring": info.docstring,
                "steps": info.steps,
                "result_keys": info.result_keys,
                "statuses": info.statuses,
            }
            for key, info in method_infos.items()
        },
        "helper_methods": helper_methods,
        "test_viewpoints": _build_test_viewpoints(parameter_specs, method_infos),
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }

    output_path.write_text(_render_markdown(spec), encoding="utf-8")
    return spec


def find_class_node(tree: ast.AST, class_name: str) -> ast.ClassDef | None:
    """ASTから名前でクラス定義ノードを検索します。"""
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            return node
    return None


def collect_method_info(cls: type, source_file: Path, method_name: str) -> MethodInfo:
    """メソッドの詳細情報を収集します。"""
    defining_class = _resolve_defining_class(cls, method_name)
    method = getattr(defining_class, method_name)
    source = textwrap.dedent(inspect.getsource(method))
    method_node = ast.parse(source).body[0]
    if not isinstance(method_node, (ast.FunctionDef, ast.AsyncFunctionDef)):
        raise TypeError(f"Unexpected node for {method_name}: {type(method_node)!r}")

    steps = _summarize_method(method_node)
    result_keys = collect_result_keys(method_node)
    statuses = collect_statuses(method_node)
    docstring = _clean_text(ast.get_docstring(method_node) or "")
    try:
        _, start_line = inspect.getsourcelines(method)
        source_lines = f"{start_line}-{start_line + len(source.splitlines()) - 1}"
    except OSError:
        source_lines = ""

    return MethodInfo(
        name=method_name,
        defining_class=defining_class.__name__,
        docstring=docstring,
        steps=steps,
        result_keys=result_keys,
        statuses=statuses,
        source_lines=source_lines,
    )


def collect_helper_methods(cls: type, source_file: Path) -> list[dict[str, Any]]:
    """クラス内の補助メソッド情報を収集します。"""
    helper_names = []
    for name, value in cls.__dict__.items():
        if name.startswith("_") and name not in {"__init__"}:
            continue
        if name in {"__init__", "get_mode", "get_cmd", "get_option", "apprun", "svrun", "is_cluster_redirect"}:
            continue
        if inspect.isfunction(value):
            helper_names.append(name)

    helpers: list[dict[str, Any]] = []
    for name in sorted(helper_names):
        info = collect_method_info(cls, source_file, name)
        helpers.append(
            {
                "name": name,
                "defining_class": info.defining_class,
                "docstring": info.docstring,
                "steps": info.steps,
                "result_keys": info.result_keys,
                "statuses": info.statuses,
                "source_lines": info.source_lines,
            }
        )
    return helpers


def collect_result_keys(node: ast.AST) -> list[str]:
    """returnステートメントと代入からの結果辞書キーを抽出します。"""
    keys: list[str] = []
    for child in ast.walk(node):
        if isinstance(child, ast.Assign):
            target_names = {
                target.id
                for target in child.targets
                if isinstance(target, ast.Name)
            }
            if not target_names.intersection(RESULT_VAR_NAMES):
                continue
            keys.extend(_extract_dict_keys(child.value))
        elif isinstance(child, ast.AnnAssign) and isinstance(child.target, ast.Name):
            if child.target.id not in RESULT_VAR_NAMES or child.value is None:
                continue
            keys.extend(_extract_dict_keys(child.value))
        elif isinstance(child, ast.Return) and child.value is not None:
            keys.extend(_extract_return_result_keys(child.value))
    return _ordered_unique(keys)


def collect_statuses(node: ast.AST) -> list[str]:
    """ASTからステータスコード (RESP_* 属性と整数定数) を抽出します。"""
    statuses: list[str] = []
    for child in ast.walk(node):
        if (
            isinstance(child, ast.Attribute)
            and isinstance(child.value, ast.Name)
            and child.value.id == "self"
            and child.attr.startswith("RESP_")
        ):
            statuses.append(child.attr)
        elif (
            isinstance(child, ast.Constant)
            and isinstance(child.value, int)
            and not isinstance(child.value, bool)
        ):
            if child.value in {0, 1, 2}:
                statuses.append(f"INT_{child.value}")
    return _ordered_unique(statuses)


# ---------------------------------------------------------------------------
# 内部ユーティリティ関数 (プレフィックス _ )
# ---------------------------------------------------------------------------

def _resolve_defining_class(cls: type, method_name: str) -> type:
    for base in cls.__mro__:
        if method_name in base.__dict__:
            return base
    return cls


def _summarize_method(node: ast.FunctionDef | ast.AsyncFunctionDef) -> list[str]:
    statements = []
    body = node.body
    if (
        body
        and isinstance(body[0], ast.Expr)
        and isinstance(body[0].value, ast.Constant)
        and isinstance(body[0].value.value, str)
    ):
        body = body[1:]
    for stmt in body:
        summary = _summarize_statement(stmt)
        if summary:
            statements.extend(summary)
    return statements or ["実装の主要ステップは自動抽出できませんでした。ソースコードを確認してください。"]


def _summarize_statement(stmt: ast.stmt) -> list[str]:
    if isinstance(stmt, ast.If):
        condition = _shorten(ast.unparse(stmt.test))
        if _contains_return(stmt):
            statuses = collect_statuses(stmt)
            keys = collect_result_keys(stmt)
            status_text = ", ".join(statuses) if statuses else "戻り値あり"
            key_text = f"。結果キー: {', '.join(keys)}" if keys else ""
            return [f"条件 {condition} を満たす場合は早期終了し、{status_text}{key_text}"]
        calls = _collect_call_names(stmt)
        call_text = f"。主な呼出: {', '.join(calls)}" if calls else ""
        return [f"条件 {condition} に応じて分岐する{call_text}"]
    if isinstance(stmt, (ast.For, ast.AsyncFor)):
        target = _shorten(ast.unparse(stmt.target))
        iterator = _shorten(ast.unparse(stmt.iter))
        calls = _collect_call_names(stmt)
        call_text = f"。主な呼出: {', '.join(calls)}" if calls else ""
        return [f"{iterator} を走査し、{target} ごとに処理する{call_text}"]
    if isinstance(stmt, ast.While):
        condition = _shorten(ast.unparse(stmt.test))
        return [f"条件 {condition} のあいだ繰り返し処理する"]
    if isinstance(stmt, ast.Try):
        calls = _collect_call_names(stmt)
        call_text = f"。主な呼出: {', '.join(calls)}" if calls else ""
        lines = [f"例外処理を伴って処理する{call_text}"]
        for handler in stmt.handlers:
            exc = ast.unparse(handler.type) if handler.type is not None else "Exception"
            statuses = collect_statuses(handler)
            keys = collect_result_keys(handler)
            suffix = []
            if statuses:
                suffix.append(f"終了コード候補: {', '.join(statuses)}")
            if keys:
                suffix.append(f"結果キー: {', '.join(keys)}")
            joined = f"（{' / '.join(suffix)}）" if suffix else ""
            lines.append(f"{exc} を捕捉した場合の代替経路を持つ{joined}")
        return lines
    if isinstance(stmt, ast.With):
        items = ", ".join(_shorten(ast.unparse(item.context_expr)) for item in stmt.items)
        calls = _collect_call_names(stmt)
        call_text = f"。主な呼出: {', '.join(calls)}" if calls else ""
        return [f"コンテキスト {items} を利用して処理する{call_text}"]
    if isinstance(stmt, (ast.Assign, ast.AnnAssign)):
        value = stmt.value
        if isinstance(value, ast.Call):
            targets = []
            if isinstance(stmt, ast.Assign):
                targets = [_shorten(ast.unparse(target)) for target in stmt.targets]
            else:
                targets = [_shorten(ast.unparse(stmt.target))]
            callee = _shorten(_call_name(value))
            return [f"{', '.join(targets)} に {callee} の結果を格納する"]
    if isinstance(stmt, ast.Expr) and isinstance(stmt.value, ast.Call):
        callee = _shorten(_call_name(stmt.value))
        return [f"{callee} を呼び出す"]
    if isinstance(stmt, ast.Return):
        statuses = collect_statuses(stmt)
        keys = collect_result_keys(stmt)
        parts = []
        if statuses:
            parts.append(f"終了コード {', '.join(statuses)}")
        if keys:
            parts.append(f"結果キー {', '.join(keys)}")
        if parts:
            return [f"{ ' / '.join(parts) } を返却する"]
        return [f"{_shorten(ast.unparse(stmt.value)) if stmt.value is not None else 'None'} を返却する"]
    return []


def _contains_return(node: ast.AST) -> bool:
    return any(isinstance(child, ast.Return) for child in ast.walk(node))


def _collect_call_names(node: ast.AST) -> list[str]:
    calls = _ordered_unique(
        _shorten(_call_name(child))
        for child in ast.walk(node)
        if isinstance(child, ast.Call)
    )
    return [call for call in calls if call][:6]


def _call_name(node: ast.Call) -> str:
    func = node.func
    if isinstance(func, ast.Name):
        return func.id
    if isinstance(func, ast.Attribute):
        return _call_name_from_attribute(func)
    return ast.unparse(func)


def _call_name_from_attribute(node: ast.Attribute) -> str:
    parts = []
    current: ast.AST = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    else:
        parts.append(ast.unparse(current))
    return ".".join(reversed(parts))


def _extract_dict_keys(node: ast.AST) -> list[str]:
    keys: list[str] = []
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "dict":
        for keyword in node.keywords:
            if keyword.arg is not None:
                keys.append(keyword.arg)
    elif isinstance(node, ast.Dict):
        for key in node.keys:
            if isinstance(key, ast.Constant) and isinstance(key.value, str):
                keys.append(key.value)
    return keys


def _extract_return_result_keys(node: ast.AST) -> list[str]:
    if isinstance(node, ast.Tuple) and len(node.elts) >= 2:
        return _extract_dict_keys(node.elts[1])
    return _extract_dict_keys(node)


def _normalize_parameters(parameters: list[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized = []
    for param in parameters:
        choices = param.get("choice")
        if isinstance(choices, list):
            display_choices = []
            for choice in choices:
                if isinstance(choice, dict):
                    display_choices.append(str(choice.get("opt", "")))
                else:
                    display_choices.append(str(choice))
        else:
            display_choices = []
        normalized.append(
            {
                "name": param.get("opt", ""),
                "short": param.get("short"),
                "type": param.get("type", ""),
                "type_label": TYPE_LABELS.get(param.get("type", ""), str(param.get("type", ""))),
                "required": bool(param.get("required", False)),
                "default": param.get("default"),
                "multi": bool(param.get("multi", False)),
                "hide": bool(param.get("hide", False)),
                "fileio": param.get("fileio"),
                "web": param.get("web"),
                "choices": display_choices,
                "description_ja": param.get("description_ja", ""),
                "description_en": param.get("description_en", ""),
            }
        )
    return normalized


def _resolve_cluster_redirect(feature_obj: Any, method_info: MethodInfo) -> bool | str:
    try:
        return bool(feature_obj.is_cluster_redirect())
    except Exception:
        return "不明"


def _build_test_viewpoints(
    parameters: list[dict[str, Any]], method_infos: dict[str, MethodInfo]
) -> list[str]:
    viewpoints = []
    required_params = [param["name"] for param in parameters if param["required"] and not param["default"]]
    if required_params:
        viewpoints.append(f"必須パラメータ {', '.join(required_params)} が不足した場合の警告応答を確認する")

    choice_params = [param["name"] for param in parameters if param["choices"]]
    if choice_params:
        viewpoints.append(f"選択肢を持つパラメータ {', '.join(choice_params)} の境界値と不正値を確認する")

    multi_params = [param["name"] for param in parameters if param["multi"]]
    if multi_params:
        viewpoints.append(f"複数値パラメータ {', '.join(multi_params)} の 0 件・1 件・複数件入力を確認する")

    result_keys = _ordered_unique(
        method_infos["apprun"].result_keys + method_infos["svrun"].result_keys
    )
    if result_keys:
        viewpoints.append(f"結果オブジェクトのキー {', '.join(result_keys)} が期待どおり構成されることを確認する")

    statuses = _ordered_unique(
        method_infos["apprun"].statuses + method_infos["svrun"].statuses
    )
    if statuses:
        viewpoints.append(f"終了コード {', '.join(statuses)} の到達条件をそれぞれ検証する")

    return viewpoints


def _render_markdown(spec: dict[str, Any]) -> str:
    lines = [
        f"# {spec['mode']} {spec['cmd']}",
        "",
        "## 基本情報",
        "",
        "| 項目 | 内容 |",
        "| --- | --- |",
        f"| mode | {_escape_table(spec['mode'])} |",
        f"| cmd | {_escape_table(spec['cmd'])} |",
        f"| クラス | {_escape_table(spec['class_name'])} |",
        f"| モジュール | {_escape_table(spec['module_name'])} |",
        f"| 実装ファイル | {_escape_table(spec['source_file'])} |",
        f"| 継承元 | {_escape_table(', '.join(spec['base_classes'][:4]))} |",
        f"| Redis | {_escape_table(REDIS_LABELS.get(spec['use_redis'], str(spec['use_redis'])))} |",
        f"| Web モード禁止 | {'はい' if spec['nouse_webmode'] else 'いいえ'} |",
        f"| Agent 利用 | {'はい' if spec['use_agent'] else 'いいえ'} |",
        f"| クラスタ転送 | {_escape_table(str(spec['cluster_redirect']))} |",
        "",
        "## 概要",
        "",
        f"- 日本語: {spec['description_ja'] or '記載なし'}",
        f"- 英語: {spec['description_en'] or '記載なし'}",
        "",
        "## パラメータ",
        "",
        "| パラメータ | 型 | 必須 | 複数 | 非表示 | デフォルト | 選択肢 | 説明 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for param in spec["parameters"]:
        default_text = _format_default(param["default"])
        choices_text = ", ".join(param["choices"]) if param["choices"] else "-"
        param_name = f"-{param['short']}, --{param['name']}" if param["short"] else f"--{param['name']}"
        lines.append(
            "| {name} | {type_label} | {required} | {multi} | {hide} | {default} | {choices} | {desc} |".format(
                name=_escape_table(param_name),
                type_label=_escape_table(param["type_label"]),
                required="はい" if param["required"] else "いいえ",
                multi="はい" if param["multi"] else "いいえ",
                hide="はい" if param["hide"] else "いいえ",
                default=_escape_table(default_text),
                choices=_escape_table(choices_text),
                desc=_escape_table(param["description_ja"] or param["description_en"] or "-"),
            )
        )

    lines.extend(
        [
            "",
            "## 処理内容",
            "",
            _render_method_section("apprun", spec["method_infos"]["apprun"]),
            "",
            _render_method_section("svrun", spec["method_infos"]["svrun"]),
            "",
            "## 処理結果",
            "",
            f"- 終了コード候補: {', '.join(spec['statuses']) if spec['statuses'] else '抽出なし'}",
            f"- 結果キー候補: {', '.join(spec['result_keys']) if spec['result_keys'] else '抽出なし'}",
            "- 戻り値の基本形: Tuple[int, Dict[str, Any], Any]",
            "",
        ]
    )

    if spec["helper_methods"]:
        lines.extend(["## 主な補助メソッド", ""])
        for helper in spec["helper_methods"]:
            lines.append(f"### {helper['name']}")
            lines.append("")
            lines.append(f"- 実装元: {helper['defining_class']}")
            if helper["docstring"]:
                lines.append(f"- 役割: {helper['docstring']}")
            if helper["steps"]:
                lines.append("- 処理概要:")
                for step in helper["steps"]:
                    lines.append(f"  - {step}")
            lines.append("")

    if spec["test_viewpoints"]:
        lines.extend(["## 単体テスト観点", ""])
        for viewpoint in spec["test_viewpoints"]:
            lines.append(f"- {viewpoint}")
        lines.append("")

    lines.extend(
        [
            "## ソース参照",
            "",
            f"- 実装ファイル: {spec['source_file']}",
            f"- apprun 実装元: {spec['method_infos']['apprun']['defining_class']}",
            f"- svrun 実装元: {spec['method_infos']['svrun']['defining_class']}",
            f"- 生成日時: {spec['generated_at']}",
            "",
        ]
    )
    return "\n".join(lines)


def _render_method_section(name: str, method_info: dict[str, Any]) -> str:
    lines = [f"### {name}", "", f"- 実装元: {method_info['defining_class']}"]
    if method_info["docstring"]:
        lines.append(f"- 役割: {method_info['docstring']}")
    if method_info["statuses"]:
        lines.append(f"- 終了コード候補: {', '.join(method_info['statuses'])}")
    if method_info["result_keys"]:
        lines.append(f"- 結果キー候補: {', '.join(method_info['result_keys'])}")
    lines.append("- 処理フロー:")
    for step in method_info["steps"]:
        lines.append(f"  - {step}")
    return "\n".join(lines)


def _write_documents(documents: list[dict[str, Any]]) -> None:
    return None


def _write_index(
    documents: list[dict[str, Any]],
    index_file: Path,
    json_file: Path,
    output_dir: Path,
) -> None:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for document in documents:
        grouped[document["mode"]].append(document)

    lines = [
        "# CLI Specifications",
        "",
        "フィーチャーパッケージのコマンド実装から生成した詳細設計書です。",
        "",
        f"- 生成対象コマンド数: {len(documents)}",
        f"- 生成日時: {datetime.now().isoformat(timespec='seconds')}",
        f"- JSON メタデータ: {json_file.relative_to(output_dir).as_posix()}",
        "",
        "## 共通仕様",
        "",
        "- すべての CLI コマンドは mode と cmd の組で識別されます。",
        "- get_option() の choice 配列が、受け付けるパラメータ定義の原本です。",
        "- apprun() はクライアント側処理、svrun() はサーバー側処理を表します。",
        "- 終了コードは Feature.RESP_SUCCESS, Feature.RESP_WARN, Feature.RESP_ERROR を中心に返します。",
        "",
        "## 一覧",
        "",
    ]

    for mode in sorted(grouped):
        lines.append(f"### {mode} ({len(grouped[mode])})")
        lines.append("")
        lines.append("| cmd | 概要 | ファイル |")
        lines.append("| --- | --- | --- |")
        for document in sorted(grouped[mode], key=lambda item: item["cmd"]):
            try:
                file_path = Path(document["output_file"]).relative_to(
                    Path(document["output_file"]).parts[0]
                ).as_posix()
            except Exception:
                file_path = document["output_file"]
            # output_file は "Specifications/cli/mode/cmd.md" 形式
            # index は output_dir/README.md なので cli/mode/cmd.md の相対パスにする
            try:
                rel = Path(document["output_file"]).relative_to(
                    index_file.parent
                ).as_posix()
            except ValueError:
                rel = document["output_file"]
            lines.append(
                f"| {_escape_table(document['cmd'])} | "
                f"{_escape_table(document['description_ja'] or document['description_en'] or '-')} | "
                f"[{document['cmd']}]({rel}) |"
            )
        lines.append("")

    index_file.write_text("\n".join(lines), encoding="utf-8")


def _ordered_unique(values: Any) -> list[Any]:
    return list(
        OrderedDict(
            (value, None) for value in values if value not in {None, ""}
        ).keys()
    )


def _clean_text(text: str) -> str:
    return " ".join(line.strip() for line in text.strip().splitlines()).strip()


def _shorten(text: str, limit: int = 100) -> str:
    text = text.replace("\n", " ").strip()
    if len(text) <= limit:
        return text
    return text[: limit - 3] + "..."


def _escape_table(text: Any) -> str:
    return str(text).replace("|", "\\|").replace("\n", "<br>")


def _format_default(value: Any) -> str:
    if value is None:
        return "None"
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, default=_json_default)


def _json_default(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value)
    return str(value)


# ---------------------------------------------------------------------------
# CLI エントリポイント
# ---------------------------------------------------------------------------

def main() -> None:
    """コマンドラインから詳細設計書を生成します。

    デフォルトでは cmdbox.app.features.cli を対象にします。
    --feature-package オプションで任意のフィーチャーパッケージを指定できます。
    """
    parser = argparse.ArgumentParser(
        description="CLIコマンド詳細設計書を生成します"
    )
    parser.add_argument(
        "--feature-package",
        default="cmdbox.app.features.cli",
        help="フィーチャーを含むPythonパッケージ名 (デフォルト: cmdbox.app.features.cli)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="仕様書の出力先ディレクトリ (デフォルト: <root-dir>/Specifications)",
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=None,
        help="プロジェクトルートディレクトリ (デフォルト: このファイルから4階層上)",
    )
    parser.add_argument(
        "--prefix",
        default="cmdbox_",
        help="フィーチャーモジュールのファイル名プレフィックス (デフォルト: cmdbox_)",
    )
    parser.add_argument(
        "--app-module",
        default=None,
        help="アプリケーションクラスのモジュールパス (例: myapp.app.MyApp)。省略時はCmdBoxApp",
    )
    parser.add_argument(
        "--ver-module",
        default=None,
        help="バージョンモジュールのパス (例: myapp.version)。省略時はcmdbox.version",
    )
    args = parser.parse_args()

    root_dir = args.root_dir or Path(__file__).resolve().parents[3]
    output_dir = args.output_dir or (root_dir / "Specifications")

    appcls = None
    if args.app_module:
        module_path, _, class_name = args.app_module.rpartition(".")
        mod = importlib.import_module(module_path)
        appcls = getattr(mod, class_name)

    ver = None
    if args.ver_module:
        ver = importlib.import_module(args.ver_module)

    generate(
        feature_package=args.feature_package,
        output_dir=output_dir,
        root_dir=root_dir,
        prefix=args.prefix,
        appcls=appcls,
        ver=ver,
    )


if __name__ == "__main__":
    main()
