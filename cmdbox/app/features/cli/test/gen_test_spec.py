"""ユニットテスト仕様書生成ツール。

cmdboxを拡張して作成したコマンドでも利用できるよう、
入力JSONパスや出力先をパラメータとして受け取ります。

使い方 (コマンドライン):
    python -m cmdbox.tools.test.generate_unit_test_specifications \\
        --input-json path/to/Specifications/cli-command-specifications.json \\
        --output-dir path/to/Specifications_forUnitTest \\
        --root-dir path/to/project

使い方 (Python API):
    from cmdbox.tools.test.generate_unit_test_specifications import generate
    generate(
        input_json=Path("path/to/Specifications/cli-command-specifications.json"),
        output_dir=Path("path/to/Specifications_forUnitTest"),
        root_dir=Path("path/to/project"),
    )
"""
from __future__ import annotations

import argparse
import json
import re
from cmdbox.app.commons import validator
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


INT_BOUNDARY_CANDIDATES = [0, 1, -1, 2147483647]
FLOAT_BOUNDARY_CANDIDATES = [0.0, 1.0, -1.0, 1e308]
SPECIAL_TEXT = "a_日本語 space-_.#\"'&<>"
EXCLUDED_PARAM_NAMES = {"host", "port", "password", "svname",
                        "retry_count", "retry_interval", "timeout",
                        "capture_stdout", "capture_maxsize",
                        "stdout_log", "output_json", "output_json_append"}


@dataclass
class TestCase:
    category: str
    focus: str
    input_pattern: str
    expected_status: str
    expected_result: str
    post_checks: str


def generate(
    input_json: Path,
    output_dir: Path,
    root_dir: Path,
) -> list[dict[str, Any]]:
    """CLIコマンド仕様JSONからユニットテスト仕様を生成します。

    Args:
        input_json: 入力となる cli-command-specifications.json のパス
        output_dir: テスト仕様書の出力先ディレクトリ
        root_dir: プロジェクトルートディレクトリ
                  (詳細設計書マークダウンの参照に使用)

    Returns:
        生成されたテスト仕様書の辞書リスト
    """
    docs_dir = output_dir / "cli"
    index_file = output_dir / "README.md"
    json_file = output_dir / "cli-unit-test-specifications.json"

    command_specs = json.loads(input_json.read_text(encoding="utf-8"))

    output_dir.mkdir(parents=True, exist_ok=True)
    docs_dir.mkdir(exist_ok=True)

    documents: list[dict[str, Any]] = []
    for command_spec in command_specs:
        document = build_unit_test_spec(command_spec, docs_dir, root_dir, all_specs=command_specs)
        _write_document(document, root_dir)
        documents.append(document)

    _write_index(documents, index_file, json_file, output_dir, root_dir)

    # 入力値を全テストケースに追加
    _add_input_values_to_test_cases(documents)

    json_file.write_text(
        json.dumps(documents, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"generated {len(documents)} unit test specifications")
    print(index_file)
    return documents


def extract_test_cases_from_markdown(spec_file_path: Path) -> list[TestCase]:
    """マークダウン仕様ファイルからテストパターン表を抽出します。

    表の形式:
    | ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |
    | TC-001 | 正常系 | ... | ... | ... | ... | ... |
    """
    try:
        content = spec_file_path.read_text(encoding="utf-8")
    except (FileNotFoundError, OSError):
        return []

    cases: list[TestCase] = []
    lines = content.split("\n")

    in_test_pattern_section = False
    in_table = False
    header_row = None

    for line in lines:
        if "## テストパターン" in line:
            in_test_pattern_section = True
            continue
        if in_test_pattern_section and line.startswith("## "):
            break
        if not in_test_pattern_section:
            continue
        if not line.strip().startswith("|"):
            in_table = False
            continue
        if not in_table and "|" in line:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 7 and "ID" in parts[0] and "分類" in parts[1]:
                header_row = parts
                in_table = True
                continue
        if in_table and all(p.strip().startswith("-") for p in line.split("|")[1:-1]):
            continue
        if in_table and header_row:
            parts = [p.strip() for p in line.split("|")[1:-1]]
            if len(parts) >= 7:
                try:
                    case = TestCase(
                        category=parts[1],
                        focus=parts[2],
                        input_pattern=parts[3],
                        expected_status=parts[4],
                        expected_result=parts[5],
                        post_checks=parts[6],
                    )
                    cases.append(case)
                except (IndexError, ValueError):
                    continue

    return cases


def build_unit_test_spec(
    command_spec: dict[str, Any],
    docs_dir: Path,
    root_dir: Path,
    all_specs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """コマンドの完全なユニットテスト仕様を構築します。

    Args:
        command_spec: CLI仕様JSONからのコマンド仕様
        docs_dir: マークダウン出力先ディレクトリ
        root_dir: プロジェクトルートディレクトリ

    Returns:
        完全なユニットテスト仕様の辞書
    """
    mode = command_spec["mode"]
    cmd = command_spec["cmd"]
    parameters = command_spec.get("parameters", [])
    output_file = docs_dir / mode / f"{cmd}.md"
    output_file.parent.mkdir(parents=True, exist_ok=True)

    inferred_required = _infer_required_parameters(command_spec, parameters)
    artifact_checks = _build_artifact_checks(command_spec)

    # 詳細設計書マークダウンからテストケースを抽出
    spec_file_path = root_dir / command_spec.get("output_file", "")
    extracted_cases = (
        extract_test_cases_from_markdown(spec_file_path)
        if spec_file_path.exists()
        else []
    )

    if extracted_cases:
        test_cases = _dedupe_test_cases(extracted_cases)
    else:
        test_cases = _dedupe_test_cases(
            _build_test_cases(command_spec, artifact_checks, inferred_required)
        )

    try:
        output_file_rel = output_file.relative_to(root_dir).as_posix()
    except ValueError:
        output_file_rel = output_file.as_posix()

    nouse_webmode = bool(command_spec.get("nouse_webmode", False))

    return {
        "mode": mode,
        "cmd": cmd,
        "description_ja": command_spec.get("description_ja", ""),
        "description_en": command_spec.get("description_en", ""),
        "class_name": command_spec.get("class_name", ""),
        "module_name": command_spec.get("module_name", ""),
        "source_file": command_spec.get("source_file", ""),
        "specification_file": command_spec.get("output_file", ""),
        "output_file": output_file_rel,
        "nouse_webmode": nouse_webmode,
        "statuses": command_spec.get("statuses", []),
        "result_keys": command_spec.get("result_keys", []),
        "parameters": parameters,
        "inferred_required": inferred_required,
        "test_viewpoints": command_spec.get("test_viewpoints", []),
        "artifact_checks": artifact_checks,
        "boundary_policy": _build_boundary_policy(parameters),
        **_infer_pre_post_cmds(command_spec, all_specs or []),
        "test_cases": [
            {
                "id": f"TC-{index:03d}",
                "category": case.category,
                "focus": case.focus,
                "input_pattern": case.input_pattern,
                "expected_status": case.expected_status,
                "expected_result": case.expected_result,
                "post_checks": case.post_checks,
                "nouse_webmode": nouse_webmode,
            }
            for index, case in enumerate(test_cases, start=1)
        ],
        "generated_at": datetime.now().isoformat(timespec="seconds"),
    }


# ---------------------------------------------------------------------------
# テストケース生成
# ---------------------------------------------------------------------------

def _build_test_cases(
    command_spec: dict[str, Any],
    artifact_checks: list[str],
    inferred_required: list[str],
) -> list[TestCase]:
    """コマンド仕様からテストケース一覧を構築します。

    Args:
        command_spec: CLI仕様JSONからのコマンド仕様
        artifact_checks: 成果物確認項目のリスト
        inferred_required: コードから推定した必須パラメータ名のリスト

    Returns:
        生成されたTestCaseのリスト
    """
    cases: list[TestCase] = []
    parameters = command_spec.get("parameters", [])
    statuses = command_spec.get("statuses", [])
    result_keys = command_spec.get("result_keys", [])
    success_status = _choose_success_status(statuses)
    warning_status = _choose_warning_status(statuses, success_status)
    output_append = _find_parameter(parameters, "output_json_append")
    required_names = {parameter["name"] for parameter in parameters if parameter.get("required")}
    required_names.update(inferred_required)

    cases.append(
        TestCase(
            category="正常系",
            focus="最小有効入力",
            input_pattern=_build_minimum_valid_pattern(parameters, required_names),
            expected_status=success_status,
            expected_result=_build_success_result_text(result_keys),
            post_checks=_join_items(
                artifact_checks, fallback="戻り値以外の副作用がないことを確認する"
            ),
        )
    )

    for parameter in parameters:
        if parameter["name"] in EXCLUDED_PARAM_NAMES:
            continue
        is_required = parameter.get("required") or parameter["name"] in required_names
        has_default = parameter.get("default") not in (None, "None", "")
        if is_required and not has_default:
            cases.append(
                TestCase(
                    category="必須チェック",
                    focus=f"{parameter['name']} 未指定",
                    input_pattern=(
                        f"{_format_parameter_name(parameter)} を省略し、"
                        "他の必須パラメータは有効値を指定する"
                    ),
                    expected_status=warning_status,
                    expected_result=f"{_format_parameter_name(parameter)} の不足を示すエラーまたは警告が返る",
                    post_checks="処理を継続せず、副作用が発生しないことを確認する",
                )
            )

        cases.extend(
            _build_parameter_boundary_cases(
                parameter,
                success_status,
                warning_status,
                result_keys,
                output_append,
                is_required,
            )
        )

    if output_append is not None:
        cases.append(
            TestCase(
                category="ファイルI/O",
                focus="output_json 追記保存",
                input_pattern="既存の output_json を用意し、output_json_append=True で 2 回連続実行する",
                expected_status=success_status,
                expected_result="各回の結果が保存され、追記モードで既存内容が失われない",
                post_checks="1 回目より 2 回目のファイルサイズが増加し、追記後も JSON として解釈可能であることを確認する",
            )
        )

    if artifact_checks:
        cases.append(
            TestCase(
                category="副作用確認",
                focus="成果物検証",
                input_pattern="副作用を発生させる有効入力で実行する",
                expected_status=success_status,
                expected_result="戻り値が正常であり、関連する成果物が期待どおり更新される",
                post_checks=_join_items(artifact_checks, fallback="生成物を確認する"),
            )
        )

    if result_keys:
        cases.append(
            TestCase(
                category="結果検証",
                focus="結果キー整合性",
                input_pattern="正常系の代表入力で実行する",
                expected_status=success_status,
                expected_result=f"結果オブジェクトに {', '.join(result_keys)} が含まれる",
                post_checks="不要なキー欠落や型崩れがないことを確認する",
            )
        )

    return cases


def _build_parameter_boundary_cases(
    parameter: dict[str, Any],
    success_status: str,
    warning_status: str,
    result_keys: list[str],
    output_append: dict[str, Any] | None,
    is_required: bool,
) -> list[TestCase]:
    """1つのパラメータに対する境界値テストケースを構築します。

    Args:
        parameter: パラメータ仕様の辞書
        success_status: 正常終了時のステータス文字列
        warning_status: 異常系のステータス文字列
        result_keys: 期待する結果キーのリスト
        output_append: output_json_appendパラメータ仕様 (存在しない場合はNone)
        is_required: このパラメータが必須かどうか

    Returns:
        生成されたTestCaseのリスト
    """
    cases: list[TestCase] = []
    name = parameter["name"]
    param_type = parameter.get("type")
    choices = parameter.get("choices") or []

    if choices and param_type != "bool":
        first_choice = choices[0]
        last_choice = choices[-1]
        cases.append(
            TestCase(
                category="選択値境界",
                focus=f"{name} 先頭選択肢",
                input_pattern=f"{_format_parameter_name(parameter)} に選択肢の先頭値 {first_choice} を指定する",
                expected_status=success_status,
                expected_result=_build_success_result_text(result_keys),
                post_checks="先頭選択肢でも分岐が正しく処理されることを確認する",
            )
        )
        if last_choice != first_choice:
            cases.append(
                TestCase(
                    category="選択値境界",
                    focus=f"{name} 末尾選択肢",
                    input_pattern=f"{_format_parameter_name(parameter)} に選択肢の末尾値 {last_choice} を指定する",
                    expected_status=success_status,
                    expected_result=_build_success_result_text(result_keys),
                    post_checks="末尾選択肢でも分岐が正しく処理されることを確認する",
                )
            )
        cases.append(
            TestCase(
                category="選択値境界",
                focus=f"{name} 不正選択肢",
                input_pattern=f"{_format_parameter_name(parameter)} に選択肢外の値 INVALID_CHOICE を指定する",
                expected_status=warning_status,
                expected_result="パラメータ検証エラーまたは実行時警告になる",
                post_checks="不正値で副作用が発生しないことを確認する",
            )
        )

    if parameter.get("multi"):
        cases.extend(
            [
                TestCase(
                    category="複数値境界",
                    focus=f"{name} 0件",
                    input_pattern=f"{_format_parameter_name(parameter)} に空配列または未指定を与える",
                    expected_status=success_status if not is_required else warning_status,
                    expected_result="0 件入力時の既定動作が仕様どおりである",
                    post_checks="一覧条件や絞り込み結果が崩れないことを確認する",
                ),
                TestCase(
                    category="複数値境界",
                    focus=f"{name} 1件",
                    input_pattern=f"{_format_parameter_name(parameter)} に 1 件だけ指定する",
                    expected_status=success_status,
                    expected_result=_build_success_result_text(result_keys),
                    post_checks="単一値で期待したフィルタリングまたは処理が行われることを確認する",
                ),
                TestCase(
                    category="複数値境界",
                    focus=f"{name} 複数件",
                    input_pattern=f"{_format_parameter_name(parameter)} に 2 件以上指定する",
                    expected_status=success_status,
                    expected_result=_build_success_result_text(result_keys),
                    post_checks="順序・重複・集約結果が仕様どおりであることを確認する",
                ),
            ]
        )

    if param_type == "bool":
        cases.extend(
            [
                TestCase(
                    category="型境界",
                    focus=f"{name}=False",
                    input_pattern=f"{_format_parameter_name(parameter)} に False を指定する",
                    expected_status=success_status,
                    expected_result="False 分岐が正常に処理される",
                    post_checks="既定値との差分がある場合は挙動の変化を確認する",
                ),
                TestCase(
                    category="型境界",
                    focus=f"{name}=True",
                    input_pattern=f"{_format_parameter_name(parameter)} に True を指定する",
                    expected_status=success_status,
                    expected_result="True 分岐が正常に処理される",
                    post_checks="副作用がある場合は有効化に伴う成果物の差分を確認する",
                ),
            ]
        )

    elif param_type == "int":
        for candidate in INT_BOUNDARY_CANDIDATES:
            cases.append(
                TestCase(
                    category="型境界",
                    focus=f"{name}={candidate}",
                    input_pattern=f"{_format_parameter_name(parameter)} に {candidate} を指定する",
                    expected_status=success_status if candidate >= 0 else warning_status,
                    expected_result=(
                        _build_success_result_text(result_keys)
                        if candidate >= 0
                        else "負値を許容しない場合はエラーまたは警告になる"
                    ),
                    post_checks="数値が内部で丸められず、そのまま評価されることを確認する",
                )
            )

    elif param_type == "float":
        for candidate in FLOAT_BOUNDARY_CANDIDATES:
            cases.append(
                TestCase(
                    category="型境界",
                    focus=f"{name}={candidate}",
                    input_pattern=f"{_format_parameter_name(parameter)} に {candidate} を指定する",
                    expected_status=success_status if candidate >= 0 else warning_status,
                    expected_result=(
                        _build_success_result_text(result_keys)
                        if candidate >= 0
                        else "負値を許容しない場合はエラーまたは警告になる"
                    ),
                    post_checks="浮動小数の比較誤差やオーバーフローが起きないことを確認する",
                )
            )

    elif param_type in {"str", "text", "passwd"}:
        has_default = parameter.get("default") not in (None, "None", "")
        str_cases: list[TestCase] = []
        if not has_default:
            str_cases.append(
                TestCase(
                    category="型境界",
                    focus=f"{name} 空文字",
                    input_pattern=f"{_format_parameter_name(parameter)} に空文字を指定する",
                    expected_status=warning_status if is_required else success_status,
                    expected_result="空文字の扱いが省略と区別され、検証結果が仕様どおりになる",
                    post_checks="エラー時は副作用が発生しないことを確認する",
                )
            )
        if not choices:
            if param_type in {"text", "passwd"}:
                str_cases.extend(
                    [
                        TestCase(
                            category="型境界",
                            focus=f"{name} 1文字",
                            input_pattern=f"{_format_parameter_name(parameter)} に 1 文字値 X を指定する",
                            expected_status=success_status,
                            expected_result=_build_success_result_text(result_keys),
                            post_checks="最短相当の入力でも分岐や検索条件が崩れないことを確認する",
                        ),
                        TestCase(
                            category="型境界",
                            focus=f"{name} 特殊文字",
                            input_pattern=f"{_format_parameter_name(parameter)} に {SPECIAL_TEXT} を指定する",
                            expected_status=success_status,
                            expected_result="日本語・空白・記号を含む入力が正しく受理される",
                            post_checks="文字化けやエスケープ漏れがないことを確認する",
                        ),
                    ]
                )
            else:
                str_cases.extend(
                    [
                        TestCase(
                            category="型境界",
                            focus=f"{name} 1文字",
                            input_pattern=f"{_format_parameter_name(parameter)} に 1 文字値 X を指定する",
                            expected_status=success_status if choices!=[] else warning_status,
                            expected_result=_build_success_result_text(result_keys),
                            post_checks="最短相当の入力でも分岐や検索条件が崩れないことを確認する",
                        ),
                        TestCase(
                            category="型境界",
                            focus=f"{name} 特殊文字",
                            input_pattern=f"{_format_parameter_name(parameter)} に {SPECIAL_TEXT} を指定する",
                            expected_status=success_status if choices!=[] else warning_status,
                            expected_result="日本語・空白・記号を含む入力が正しく受理される",
                            post_checks="文字化けやエスケープ漏れがないことを確認する",
                        ),
                        TestCase(
                            category="型境界",
                            focus=f"{name} 長文",
                            input_pattern=f"{_format_parameter_name(parameter)} に {validator.LONG_TEXT_BOUNDARY} 文字相当の文字列を指定する",
                            expected_status=warning_status,
                            expected_result=f"{validator.LONG_TEXT_BOUNDARY} 文字を超える入力は検証エラーまたは警告になる",
                            post_checks="エラー時は副作用が発生しないことを確認する",
                        ),
                    ]
                )

        cases.extend(str_cases)

    elif param_type == "dir":
        cases.extend(
            [
                TestCase(
                    category="型境界",
                    focus=f"{name} 既存空ディレクトリ",
                    input_pattern=f"{_format_parameter_name(parameter)} に既存の空ディレクトリを指定する",
                    expected_status=success_status,
                    expected_result="空ディレクトリ前提の初期状態が正常に処理される",
                    post_checks="必要な初期化ファイルやサブディレクトリが作成される場合は生成を確認する",
                ),
                TestCase(
                    category="型境界",
                    focus=f"{name} 既存データありディレクトリ",
                    input_pattern=f"{_format_parameter_name(parameter)} に既存データを含むディレクトリを指定する",
                    expected_status=success_status,
                    expected_result="既存データを読み込む経路が正常に処理される",
                    post_checks="既存ファイルを意図せず破壊しないことを確認する",
                ),
                TestCase(
                    category="型境界",
                    focus=f"{name} 非存在ディレクトリ",
                    input_pattern=f"{_format_parameter_name(parameter)} に存在しないディレクトリを指定する",
                    expected_status=warning_status,
                    expected_result="存在チェックエラーまたは初期化失敗が返る",
                    post_checks="自動作成される仕様でない限り、ディレクトリが勝手に作成されないことを確認する",
                ),
            ]
        )

    elif param_type == "file":
        if parameter.get("fileio") == "in":
            cases.extend(
                [
                    TestCase(
                        category="ファイルI/O",
                        focus=f"{name} 有効入力ファイル",
                        input_pattern=f"{_format_parameter_name(parameter)} に存在する妥当なファイルを指定する",
                        expected_status=success_status,
                        expected_result=_build_success_result_text(result_keys),
                        post_checks="入力ファイル内容が意図どおり読み込まれることを確認する",
                    ),
                    TestCase(
                        category="ファイルI/O",
                        focus=f"{name} 存在しない入力ファイル",
                        input_pattern=f"{_format_parameter_name(parameter)} に存在しないパスを指定する",
                        expected_status=warning_status,
                        expected_result="ファイル未存在のエラーまたは警告が返る",
                        post_checks="後続処理に進まず、副作用が発生しないことを確認する",
                    ),
                    TestCase(
                        category="ファイルI/O",
                        focus=f"{name} 空ファイル",
                        input_pattern=f"{_format_parameter_name(parameter)} に 0 byte の空ファイルを指定する",
                        expected_status=warning_status,
                        expected_result="フォーマット不正または入力不足として扱われる",
                        post_checks="異常終了時のログやエラー文言が十分であることを確認する",
                    ),
                ]
            )
        elif parameter.get("fileio") == "out":
            output_check = _build_output_file_check(parameter, output_append)
            cases.extend(
                [
                    TestCase(
                        category="ファイルI/O",
                        focus=f"{name} 新規出力",
                        input_pattern=f"{_format_parameter_name(parameter)} に存在しない新規出力先を指定する",
                        expected_status=success_status,
                        expected_result=_build_success_result_text(result_keys),
                        post_checks=output_check,
                    ),
                    TestCase(
                        category="ファイルI/O",
                        focus=f"{name} 既存出力先",
                        input_pattern=f"{_format_parameter_name(parameter)} に既存ファイルを指定する",
                        expected_status=success_status,
                        expected_result="上書きまたは追記の仕様どおりに出力される",
                        post_checks=output_check,
                    ),
                    TestCase(
                        category="ファイルI/O",
                        focus=f"{name} 無効出力先",
                        input_pattern=f"{_format_parameter_name(parameter)} に親ディレクトリが存在しないパスを指定する",
                        expected_status=warning_status,
                        expected_result="保存失敗が検知され、エラーまたは警告になる",
                        post_checks="不完全ファイルが残らないことを確認する",
                    ),
                ]
            )

    return cases


# ---------------------------------------------------------------------------
# 入力値生成
# ---------------------------------------------------------------------------

def _add_input_values_to_test_cases(documents: list[dict[str, Any]]) -> None:
    """入力パターンに基づいて、すべてのテストケースに入力値を追加します。"""
    updated_count = 0

    for spec in documents:
        test_cases = spec.get("test_cases", [])
        parameters = spec.get("parameters", [])

        for tc in test_cases:
            if "input_values" not in tc or not tc["input_values"]:
                tc["input_values"] = _generate_input_values_from_pattern(
                    tc.get("input_pattern", ""),
                    tc.get("focus", ""),
                    parameters,
                )
                updated_count += 1

    if updated_count > 0:
        print(f"Generated input_values for {updated_count} test cases")


def _generate_input_values_from_pattern(
    input_pattern: str,
    focus: str,
    parameters: list[dict[str, Any]],
) -> dict[str, Any]:
    """入力パターン文字列と観点からテストの入力値辞書を生成します。

    Args:
        input_pattern: テストケースの入力パターン説明文
        focus: テストケースの観点文字列
        parameters: コマンドのパラメータ仕様リスト

    Returns:
        パラメータ名をキー、入力値を値とする辞書
    """
    input_values: dict[str, Any] = {}
    param_map = {p["name"]: p for p in parameters}

    explicit_values = re.findall(r"--(\w+)[\s=]+([^\s,。、]+)", input_pattern)
    for param_name_raw, value in explicit_values:
        param_name = param_name_raw.replace("-", "_")
        if param_name in param_map:
            input_values[param_name] = _parse_value(value, param_map[param_name])

    # 選択肢境界パターンの処理 (explicit_values の誤マッチを上書き)
    choice_first = re.search(r"--(\w+)(?:\(-\w+\))? に選択肢の先頭値 (.*?) を指定する", input_pattern)
    if choice_first:
        param_name = choice_first.group(1)
        value_str = choice_first.group(2)
        if param_name in param_map:
            input_values[param_name] = _parse_value(value_str, param_map[param_name])

    choice_last = re.search(r"--(\w+)(?:\(-\w+\))? に選択肢の末尾値 (.*?) を指定する", input_pattern)
    if choice_last:
        param_name = choice_last.group(1)
        value_str = choice_last.group(2)
        if param_name in param_map:
            input_values[param_name] = _parse_value(value_str, param_map[param_name])

    choice_invalid = re.search(r"--(\w+)(?:\(-\w+\))? に選択肢外の値 (\S+) を指定する", input_pattern)
    if choice_invalid:
        param_name = choice_invalid.group(1)
        value_str = choice_invalid.group(2)
        if param_name in param_map:
            input_values[param_name] = value_str

    omit_param = None
    test_value = None

    for param_name in param_map:
        if f"{param_name}" in input_pattern and (
            "未指定" in input_pattern or f"{param_name} を省略" in input_pattern
        ):
            omit_param = param_name
            break

    if "空文字" in focus or "空文字" in input_pattern:
        for param_name in param_map:
            if param_name in focus or param_name in input_pattern:
                test_value = (param_name, "")
                break
    elif "1文字" in focus or "1文字" in input_pattern:
        for param_name in param_map:
            if param_name in focus or param_name in input_pattern:
                test_value = (param_name, "X")
                break
    elif "特殊文字" in focus or "特殊文字" in input_pattern:
        for param_name in param_map:
            if param_name in focus or param_name in input_pattern:
                test_value = (param_name, SPECIAL_TEXT)
                break
    elif "長文" in focus or "長文" in input_pattern:
        for param_name in param_map:
            if param_name in focus or param_name in input_pattern:
                test_value = (param_name, "X" * validator.LONG_TEXT_BOUNDARY)
                break
    elif "既存データを含むディレクトリ" in focus or "既存データを含むディレクトリ" in input_pattern:
        for param_name in param_map:
            if param_name in focus or param_name in input_pattern:
                test_value = (param_name, param_map[param_name].get("default", "./"))
                break
    elif "存在しないディレクトリ" in focus or "存在しないディレクトリ" in input_pattern:
        for param_name in param_map:
            if param_name in focus or param_name in input_pattern:
                test_value = (param_name, f"{'X' * 30}/nonexistent_dir")
                break

    if test_value:
        param_name, value = test_value
        if param_name in param_map:
            input_values[param_name] = value

    if "=0" in input_pattern:
        for param_name in param_map:
            if param_name in input_pattern and param_map[param_name]["type"] == "int":
                input_values[param_name] = 0
    elif "=1" in input_pattern and "-1" not in input_pattern:
        for param_name in param_map:
            if param_name in input_pattern and param_map[param_name]["type"] == "int":
                input_values[param_name] = 1
    elif "=-1" in input_pattern:
        for param_name in param_map:
            if param_name in input_pattern and param_map[param_name]["type"] == "int":
                input_values[param_name] = -1

    if omit_param:
        input_values[omit_param] = None

    for param_name, param in param_map.items():
        if param_name not in input_values:
            if param["required"]:
                input_values[param_name] = _get_default_value(param)

    return input_values


def _parse_value(value: str, param: dict[str, Any]) -> Any:
    """文字列値をパラメータの型に合わせてPythonの値に変換します。

    Args:
        value: 変換前の文字列値
        param: パラメータ仕様の辞書

    Returns:
        型変換後のPython値
    """
    param_type = param.get("type")
    if param_type == "int":
        try:
            return int(value)
        except ValueError:
            return param.get("default", 1)
    elif param_type == "float":
        try:
            return float(value)
        except ValueError:
            return param.get("default", 1.0)
    elif param_type == "bool":
        return value.lower() in ("true", "1", "yes")
    else:
        return value


def _get_default_value(param: dict[str, Any]) -> Any:
    """パラメータ仕様からテスト用のデフォルト入力値を返します。

    defaultフィールドが有効な場合はそれを型変換して返します。
    無効な場合は型に応じたフォールバック値を返します。

    Args:
        param: パラメータ仕様の辞書

    Returns:
        テスト用デフォルト値
    """
    default = param.get("default")
    param_type = param.get("type")

    if default not in (None, "None", ""):
        if param_type == "int":
            try:
                return int(default)
            except (ValueError, TypeError):
                return 1
        elif param_type == "float":
            try:
                return float(default)
            except (ValueError, TypeError):
                return 1.0
        else:
            return default

    if param_type == "int":
        return 1
    elif param_type == "float":
        return 1.0
    elif param_type == "bool":
        return False
    elif param_type in ("dir", "file"):
        return f"/tmp/{param['name']}"
    else:
        return "default_value"


# ---------------------------------------------------------------------------
# 補助ユーティリティ
# ---------------------------------------------------------------------------

def _build_artifact_checks(command_spec: dict[str, Any]) -> list[str]:
    """コマンド仕様から成果物確認項目のリストを構築します。

    出力ファイルパラメータやステップ中のファイル操作を解析し、
    テストで確認すべき副作用チェック項目を生成します。

    Args:
        command_spec: CLI仕様JSONからのコマンド仕様

    Returns:
        重複排除済みの確認項目文字列リスト
    """
    checks: list[str] = []
    parameters = command_spec.get("parameters", [])
    output_append = _find_parameter(parameters, "output_json_append")

    for parameter in parameters:
        if parameter.get("fileio") == "out":
            checks.append(_build_output_file_check(parameter, output_append))

    step_texts = _collect_step_texts(command_spec)
    for step in step_texts:
        if ".unlink" in step:
            matches = re.findall(r"Path\(['\"]([^'\"]+)['\"].*?\.unlink", step)
            if matches:
                for matched_path in matches:
                    checks.append(f"実行後に {matched_path} が削除されていることを確認する")
            else:
                checks.append("削除処理が成功し、削除対象が残存しないことを確認する")
        if "mkdir" in step or "makedirs" in step:
            checks.append("必要なディレクトリが生成され、再実行時も競合しないことを確認する")
        if any(keyword in step for keyword in ["write", "save", "dump", "export"]):
            checks.append("生成物が空でなく、フォーマット不整合がないことを確認する")

    return _ordered_unique(checks)


def _build_output_file_check(
    parameter: dict[str, Any], output_append: dict[str, Any] | None
) -> str:
    """出力ファイルパラメータに対する確認メッセージを生成します。

    Args:
        parameter: fileio='out' のパラメータ仕様辞書
        output_append: output_json_appendパラメータ仕様 (存在しない場合はNone)

    Returns:
        テスト確認項目の文字列
    """
    name = parameter["name"]
    if name == "output_json":
        if output_append is not None:
            return "output_json が作成され、JSON として読めること、append 指定時は既存内容を保持したまま追記されることを確認する"
        return "output_json が作成され、JSON として読めることを確認する"
    return f"{name} で指定した出力ファイルが作成され、内容が空でないことを確認する"


def _build_boundary_policy(parameters: list[dict[str, Any]]) -> list[str]:
    """パラメータ一覧に基づいてテスト境界値ポリシーを生成します。

    Args:
        parameters: コマンドのパラメータ仕様リスト

    Returns:
        境界値ポリシーの説明文字列リスト
    """
    policy = [
        "数値型は仕様上の明示範囲がないため、0, 1, -1, 極大値を汎用境界値として扱う。",
        f"文字列型は空文字、1文字、特殊文字列、{validator.LONG_TEXT_BOUNDARY}文字相当の長文を境界として扱う。",
        "ファイル・ディレクトリは、存在する正常パス、存在しないパス、空リソースを境界として扱う。",
        "複数値パラメータは 0 件、1 件、複数件を境界として扱う。",
    ]
    if any(parameter.get("choices") for parameter in parameters):
        policy.append("選択肢付きパラメータは先頭値、末尾値、選択肢外の不正値を境界として扱う。")
    if any(parameter.get("fileio") == "out" for parameter in parameters):
        policy.append("出力ファイルを伴うコマンドは、戻り値に加えて成果物の生成・更新内容を必ず検証する。")
    return policy


def _build_minimum_valid_pattern(
    parameters: list[dict[str, Any]], required_names: set[str]
) -> str:
    """最小有効入力パターンの説明文字列を生成します。

    必須パラメータのみを有効値で指定し、任意パラメータを省略する
    入力パターン文字列を返します。

    Args:
        parameters: コマンドのパラメータ仕様リスト
        required_names: 必須パラメータ名の集合

    Returns:
        入力パターンの説明文字列
    """
    parts: list[str] = []
    for parameter in parameters:
        if parameter["name"] in EXCLUDED_PARAM_NAMES:
            continue
        if parameter["name"] in required_names:
            parts.append(
                f"{_format_parameter_name(parameter)}={_describe_valid_value(parameter)}"
            )
    if not parts:
        return "全パラメータ省略またはデフォルト値で実行する"
    return "、".join(parts) + "。任意パラメータは省略する"


def _infer_required_parameters(
    command_spec: dict[str, Any], parameters: list[dict[str, Any]]
) -> list[str]:
    """コマンドの実装ステップから必須パラメータを推定します。

    早期終了条件 (is None チェック) を解析して必須と推定される
    パラメータ名を返します。

    Args:
        command_spec: CLI仕様JSONからのコマンド仕様
        parameters: コマンドのパラメータ仕様リスト

    Returns:
        推定された必須パラメータ名のリスト
    """
    known_names = {parameter["name"] for parameter in parameters}
    inferred: list[str] = []
    for step in _collect_step_texts(command_spec):
        if "早期終了" not in step or "WARN" not in step.upper():
            continue
        matches = re.findall(r"args\.([A-Za-z0-9_]+)\s+is\s+None", step)
        matches.extend(re.findall(r"\b([A-Za-z0-9_]+)\s+is\s+None", step))
        for match in matches:
            if match in known_names and match not in inferred:
                inferred.append(match)
    return inferred


def _build_success_result_text(result_keys: list[str]) -> str:
    """正常終了時の期待結果テキストを生成します。

    Args:
        result_keys: 期待する結果キーのリスト

    Returns:
        期待結果の説明文字列
    """
    if result_keys:
        return f"正常終了し、結果オブジェクトに {', '.join(result_keys)} が含まれる"
    return "正常終了し、戻り値とログが期待どおりである"


def _choose_success_status(statuses: list[str]) -> str:
    """ステータスリストから正常終了ステータスを選択します。

    Args:
        statuses: コマンドが返しうるステータス文字列のリスト

    Returns:
        正常終了を表すステータス文字列
    """
    for status in statuses:
        upper = status.upper()
        if "SUCCESS" in upper or upper.endswith("_0"):
            return status
    return statuses[0] if statuses else "正常終了ステータス"


def _choose_warning_status(statuses: list[str], success_status: str) -> str:
    """ステータスリストから異常系ステータスを選択します。

    Args:
        statuses: コマンドが返しうるステータス文字列のリスト
        success_status: 正常終了ステータス (除外対象)

    Returns:
        異常系を表すステータス文字列
    """
    for status in statuses:
        upper = status.upper()
        if "WARN" in upper or "ERROR" in upper or "FAIL" in upper:
            return status
    for status in statuses:
        if status != success_status:
            return status
    return "異常系ステータス"


def _find_parameter(parameters: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    """名前でパラメータ仕様を検索します。

    Args:
        parameters: コマンドのパラメータ仕様リスト
        name: 検索するパラメータ名

    Returns:
        見つかったパラメータ仕様辞書、見つからない場合はNone
    """
    for parameter in parameters:
        if parameter.get("name") == name:
            return parameter
    return None


def _describe_valid_value(parameter: dict[str, Any]) -> str:
    """パラメータに対するテスト用有効値の説明文字列を返します。

    選択肢・デフォルト値・型に基づいて代表的な有効値を決定します。

    Args:
        parameter: パラメータ仕様の辞書

    Returns:
        有効値を表す文字列
    """
    choices = parameter.get("choices") or []
    default = parameter.get("default")
    param_type = parameter.get("type")

    if choices:
        return str(choices[0])
    if default not in {None, "None", ""}:
        return str(default)
    if parameter.get("fileio") == "in":
        return "既存の妥当な入力ファイル"
    if parameter.get("fileio") == "out":
        return "新規作成可能な出力先ファイル"
    if param_type == "dir":
        return "既存の作業ディレクトリ"
    if param_type == "int":
        return "1"
    if param_type == "float":
        return "1.0"
    if param_type == "bool":
        return "True"
    if parameter.get("multi"):
        return "enabled_value"
    return "enabled_value"


def _format_parameter_name(parameter: dict[str, Any]) -> str:
    """パラメータのCLI表記文字列を返します。

    短縮オプションがある場合は ``--name(-s)`` 形式で返します。

    Args:
        parameter: パラメータ仕様の辞書

    Returns:
        CLIオプション形式の文字列
    """
    short = parameter.get("short")
    if short:
        return f"--{parameter['name']}(-{short})"
    return f"--{parameter['name']}"


def _collect_step_texts(command_spec: dict[str, Any]) -> list[str]:
    """コマンド仕様からすべてのメソッドステップテキストを収集します。

    Args:
        command_spec: CLI仕様JSONからのコマンド仕様

    Returns:
        全メソッドのステップ文字列リスト
    """
    step_texts: list[str] = []
    method_infos = command_spec.get("method_infos", {})
    for method_info in method_infos.values():
        step_texts.extend(method_info.get("steps", []))
    return step_texts


def _dedupe_test_cases(cases: list[TestCase]) -> list[TestCase]:
    """テストケースリストから重複を排除します。

    (category, focus, input_pattern) の組み合わせで重複を判定し、
    先着を優先して順序を保持します。

    Args:
        cases: 重複を含む可能性があるTestCaseのリスト

    Returns:
        重複排除済みのTestCaseリスト
    """
    seen: set[tuple[str, str, str]] = set()
    unique_cases: list[TestCase] = []
    for case in cases:
        key = (case.category, case.focus, case.input_pattern)
        if key in seen:
            continue
        seen.add(key)
        unique_cases.append(case)
    return unique_cases


def _ordered_unique(values: list[str]) -> list[str]:
    """文字列リストから空文字と重複を排除し、順序を保持して返します。

    Args:
        values: 元の文字列リスト

    Returns:
        重複・空文字を排除した文字列リスト
    """
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        result.append(value)
    return result


def _join_items(items: list[str], fallback: str) -> str:
    """空文字を除いたアイテムを「 / 」で結合します。

    空のリストの場合はfallbackを返します。

    Args:
        items: 結合する文字列のリスト
        fallback: アイテムが空の場合に返すデフォルト文字列

    Returns:
        結合された文字列またはfallback
    """
    normalized = [item for item in items if item]
    return " / ".join(normalized) if normalized else fallback


# ---------------------------------------------------------------------------
# ファイル書き出し
# ---------------------------------------------------------------------------

def _infer_pre_post_cmds(
    command_spec: dict[str, Any],
    all_specs: list[dict[str, Any]],
) -> dict[str, Any]:
    """コマンド名のパターンに基づいて pre_cmds / post_cmds を推論します。

    - del / *_del コマンド: 対応する save / *_save を pre_cmds に追加
    - load コマンド: 対応する save を pre_cmds に追加
    - save コマンド: 対応する del を post_cmds に追加

    各コマンドリストは {"mode": ..., "cmd": ..., "note": ...} の辞書リストです。

    Args:
        command_spec: 対象コマンドの仕様
        all_specs: 全コマンド仕様リスト

    Returns:
        {"pre_cmds": [...], "post_cmds": [...]} を含む辞書
    """
    mode = command_spec["mode"]
    cmd = command_spec["cmd"]

    existing = {(s["mode"], s["cmd"]) for s in all_specs}

    pre_cmds: list[dict[str, Any]] = []
    post_cmds: list[dict[str, Any]] = []

    # del / *_del → 対応 save / *_save を pre_cmds に
    if cmd == "del" or cmd.endswith("_del"):
        prefix = cmd[: -len("_del")] if cmd.endswith("_del") else ""
        save_cmd = f"{prefix}_save" if prefix else "save"
        if (mode, save_cmd) in existing:
            pre_cmds.append({"mode": mode, "cmd": save_cmd, "note": f"Prepare data for {cmd}"})

    # load → 対応 save を pre_cmds に
    elif cmd == "load" or cmd.endswith("_load"):
        prefix = cmd[: -len("_load")] if cmd.endswith("_load") else ""
        save_cmd = f"{prefix}_save" if prefix else "save"
        if (mode, save_cmd) in existing:
            pre_cmds.append({"mode": mode, "cmd": save_cmd, "note": f"Prepare data for {cmd}"})

    # save → 対応 del を post_cmds に（クリーンアップ）
    elif cmd == "save" or cmd.endswith("_save"):
        prefix = cmd[: -len("_save")] if cmd.endswith("_save") else ""
        del_cmd = f"{prefix}_del" if prefix else "del"
        if (mode, del_cmd) in existing:
            post_cmds.append({"mode": mode, "cmd": del_cmd, "note": f"Cleanup data after {cmd}"})

    return {"pre_cmds": pre_cmds, "post_cmds": post_cmds}


def _write_document(document: dict[str, Any], root_dir: Path) -> None:
    """1つのユニットテスト仕様書をマークダウンファイルとして書き出します。

    Args:
        document: ユニットテスト仕様の辞書
        root_dir: プロジェクトルートディレクトリ
    """
    output_path = root_dir / document["output_file"]
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(_render_markdown(document), encoding="utf-8")


def _write_index(
    documents: list[dict[str, Any]],
    index_file: Path,
    json_file: Path,
    output_dir: Path,
    root_dir: Path,
) -> None:
    """全仕様書のインデックスとなるREADME.mdを生成して書き出します。

    modeごとにグループ化したテーブルを含むマークダウンを生成します。

    Args:
        documents: 全ユニットテスト仕様の辞書リスト
        index_file: 出力先のREADME.mdパス
        json_file: 生成元JSONファイルのパス (インデックス内参照用)
        output_dir: テスト仕様書の出力先ディレクトリ
        root_dir: プロジェクトルートディレクトリ
    """
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for document in documents:
        grouped[document["mode"]].append(document)

    lines = [
        "# Specifications_forUnitTest",
        "",
        "CLI コマンドごとの単体テスト仕様です。",
        "",
        f"- 対象コマンド数: {len(documents)}",
        f"- 生成元 JSON: {json_file.relative_to(output_dir).as_posix()}",
        f"- 生成日時: {datetime.now().isoformat(timespec='seconds')}",
        "",
        "## 使い方",
        "",
        "- 各仕様書は、最小有効入力、必須チェック、境界値、ファイル I/O、副作用確認の順でテストパターンを整理しています。",
        "- 数値の厳密な許容範囲がコードから判定できないものは、汎用境界値として 0, 1, -1, 極大値を採用しています。",
        "- fileio=out のパラメータを持つコマンドでは、戻り値だけでなく生成物の存在・内容・追記挙動も確認対象にしています。",
        "",
    ]

    for mode in sorted(grouped):
        lines.append(f"## {mode}")
        lines.append("")
        lines.append("| cmd | テストケース数 | 成果物確認 | 仕様書 |")
        lines.append("| --- | ---: | ---: | --- |")
        for document in sorted(grouped[mode], key=lambda item: item["cmd"]):
            try:
                relative_output = (root_dir / document["output_file"]).relative_to(output_dir).as_posix()
            except ValueError:
                relative_output = document["output_file"]
            lines.append(
                "| {cmd} | {case_count} | {artifact_count} | [{path}]({path}) |".format(
                    cmd=document["cmd"],
                    case_count=len(document["test_cases"]),
                    artifact_count=len(document["artifact_checks"]),
                    path=relative_output,
                )
            )
        lines.append("")

    index_file.write_text("\n".join(lines), encoding="utf-8")


def _render_markdown(document: dict[str, Any]) -> str:
    """ユニットテスト仕様辞書からマークダウン文字列を生成します。

    Args:
        document: ユニットテスト仕様の辞書

    Returns:
        マークダウン形式の仕様書文字列
    """
    lines = [
        f"# {document['mode']} {document['cmd']}",
        "",
        "## 基本情報",
        "",
        "| 項目 | 内容 |",
        "| --- | --- |",
        f"| mode | {document['mode']} |",
        f"| cmd | {document['cmd']} |",
        f"| クラス | {document['class_name']} |",
        f"| モジュール | {document['module_name']} |",
        f"| 実装ファイル | {document['source_file']} |",
        f"| 詳細設計書 | {document['specification_file']} |",
        f"| 実装上の必須推定 | {', '.join(document['inferred_required']) if document['inferred_required'] else '-'} |",
        "",
        "## 概要",
        "",
        f"- 日本語: {document['description_ja'] or '記載なし'}",
        f"- 英語: {document['description_en'] or '記載なし'}",
        "",
        "## 境界値ポリシー",
        "",
    ]

    for policy in document["boundary_policy"]:
        lines.append(f"- {policy}")

    lines.extend(
        [
            "",
            "## 共通期待結果",
            "",
            f"- 終了コード候補: {', '.join(document['statuses']) if document['statuses'] else '不明'}",
            f"- 結果キー候補: {', '.join(document['result_keys']) if document['result_keys'] else '特になし'}",
            "",
            "## 副作用確認観点",
            "",
        ]
    )

    if document["artifact_checks"]:
        for check in document["artifact_checks"]:
            lines.append(f"- {check}")
    else:
        lines.append("- 戻り値とログのみを確認対象とする")

    if document["test_viewpoints"]:
        lines.extend(["", "## 詳細設計からの観点", ""])
        for viewpoint in document["test_viewpoints"]:
            lines.append(f"- {viewpoint}")

    lines.extend(
        [
            "",
            "## テストパターン",
            "",
            "| ID | 分類 | 観点 | 入力パターン | 期待終了コード | 期待結果 | 追加確認 |",
            "| --- | --- | --- | --- | --- | --- | --- |",
        ]
    )

    for test_case in document["test_cases"]:
        lines.append(
            "| {id} | {category} | {focus} | {input_pattern} | {expected_status} | {expected_result} | {post_checks} |".format(
                id=test_case["id"],
                category=_escape_table(test_case["category"]),
                focus=_escape_table(test_case["focus"]),
                input_pattern=_escape_table(test_case["input_pattern"]),
                expected_status=_escape_table(test_case["expected_status"]),
                expected_result=_escape_table(test_case["expected_result"]),
                post_checks=_escape_table(test_case["post_checks"]),
            )
        )

    lines.extend(
        [
            "",
            "## ソース参照",
            "",
            f"- 実装ファイル: {document['source_file']}",
            f"- 詳細設計書: {document['specification_file']}",
            f"- 生成日時: {document['generated_at']}",
        ]
    )
    return "\n".join(lines)


def _escape_table(value: str) -> str:
    """マークダウンテーブル用に文字列をエスケープします。

    パイプ文字と改行をエスケープ・置換します。

    Args:
        value: エスケープ対象の文字列

    Returns:
        エスケープ済みの文字列
    """
    return str(value).replace("|", "\\|").replace("\n", "<br>")


# ---------------------------------------------------------------------------
# CLI エントリポイント
# ---------------------------------------------------------------------------

def main() -> None:
    """コマンドラインからユニットテスト仕様書を生成します。

    デフォルトでは <root-dir>/Specifications/cli-command-specifications.json を読み込み、
    <root-dir>/Specifications_forUnitTest に出力します。
    """
    parser = argparse.ArgumentParser(
        description="CLIコマンドユニットテスト仕様書を生成します"
    )
    parser.add_argument(
        "--input-json",
        type=Path,
        default=None,
        help="入力 cli-command-specifications.json のパス (デフォルト: <root-dir>/Specifications/cli-command-specifications.json)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=None,
        help="テスト仕様書の出力先ディレクトリ (デフォルト: <root-dir>/Specifications_forUnitTest)",
    )
    parser.add_argument(
        "--root-dir",
        type=Path,
        default=None,
        help="プロジェクトルートディレクトリ (デフォルト: このファイルから4階層上)",
    )
    args = parser.parse_args()

    root_dir = args.root_dir or Path(__file__).resolve().parents[3]
    input_json = args.input_json or (root_dir / "Specifications" / "cli-command-specifications.json")
    output_dir = args.output_dir or (root_dir / "Specifications_forUnitTest")

    generate(
        input_json=input_json,
        output_dir=output_dir,
        root_dir=root_dir,
    )


if __name__ == "__main__":
    main()
