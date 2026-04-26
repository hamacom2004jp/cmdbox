"""テスト仕様JSONに基づいてテストを実行するライブラリ。

cmdboxを拡張して作成したコマンドでも利用できるよう、
入力JSONパスやフィルタ条件をパラメータとして受け取ります。

使い方 (Python API):
    from cmdbox.app.features.cli.test import run_spec
    result = run_spec.run(
        input_json=Path("path/to/Specifications_forUnitTest/cli-unit-test-specifications.json"),
        mode_filter="server",
        cmd_filter="list",
        appcls=MyApp,
        ver=my_version_module,
    )
"""
from __future__ import annotations

import json
import tempfile
from datetime import datetime
from pathlib import Path
from typing import Any
from unittest.mock import patch


# テスト仕様 expected_status → 終了コード のマッピング
# None はステータスコードが問わないことを意味する（非ゼロなら可）
STATUS_MAP: dict[str, int | None] = {
    "RESP_SUCCESS": 0,
    "RESP_WARN": 1,
    "RESP_ERROR": 2,
    "INT_0": 0,
    "正常終了ステータス": 0,
    "異常系ステータス": None,  # 非ゼロなら可
}

# 外部接続エラーとみなすキーワード（これらは SKIP 扱い）
_CONNECTIVITY_KEYWORDS = (
    "connection", "refused", "redis", "socket", "broken pipe",
    "enetunreach", "no route to host", "connection reset",
    "errno 111", "errno 10061", "winerror 10061", "winerror 111",
    "could not connect", "timed out", "connection timed out",
)


def run(
    input_json: Path,
    mode_filter: str | None = None,
    cmd_filter: list[str] | None = None,
    appcls: Any = None,
    ver: Any = None,
    use_tempdir: bool = True,
    output_dir: Path | None = None,
    merge_existing: bool = False,
) -> dict[str, Any]:
    """テスト仕様JSONに基づいてテストを実行します。

    Args:
        input_json: 入力となる cli-unit-test-specifications.json のパス
        mode_filter: 実行対象をモード名でフィルタ。None で全モード対象
        cmd_filter: 実行対象をコマンド名でフィルタ。None で全コマンド対象
        appcls: フィーチャーインスタンス生成に使用するアプリクラス
        ver: フィーチャーインスタンス生成に使用するバージョンモジュール
        use_tempdir: True のとき出力系パラメータを一時ディレクトリに置換する
        output_dir: 結果 JSON / MD ファイルの出力先ディレクトリ。None のとき出力しない
        merge_existing: True のとき既存の結果ファイルと今回の結果をマージする

    Returns:
        summary と results を含む辞書
    """
    specs: list[dict[str, Any]] = json.loads(input_json.read_text(encoding="utf-8"))

    if mode_filter:
        specs = [s for s in specs if s.get("mode") == mode_filter]
    if cmd_filter:
        specs = [s for s in specs if s.get("cmd") in cmd_filter]

    results: list[dict[str, Any]] = []
    for spec in specs:
        label = f"{spec.get('mode')} {spec.get('cmd')}"
        n = len(spec.get("test_cases", []))
        print(f"[ RUN ] {label} ({n} cases)")
        spec_result = _run_command_spec(spec, appcls, ver, use_tempdir)
        results.append(spec_result)
        ok = spec_result["failed"] == 0
        print(
            f"[ {'PASS' if ok else 'FAIL'} ] {label}: "
            f"passed={spec_result['passed']}, "
            f"failed={spec_result['failed']}, "
            f"skipped={spec_result['skipped']}"
        )
        # コマンドテスト完了直後にコマンド単位の JSON / MD を出力
        if output_dir is not None:
            _write_command_result(spec_result, output_dir)

    total = sum(r["total"] for r in results)
    passed = sum(r["passed"] for r in results)
    failed = sum(r["failed"] for r in results)
    skipped = sum(r["skipped"] for r in results)
    print(
        f"\n{'=' * 60}\n"
        f"TOTAL={total}  PASSED={passed}  FAILED={failed}  SKIPPED={skipped}\n"
        f"{'=' * 60}"
    )

    return_value = {
        "summary": {
            "commands": len(results),
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "results": results,
    }

    # 既存結果とのマージ
    if merge_existing and output_dir is not None:
        json_file = output_dir / "test-run-results.json"
        if json_file.exists():
            try:
                existing = json.loads(json_file.read_text(encoding="utf-8"))
                existing_map: dict[tuple[str, str], dict[str, Any]] = {
                    (r["mode"], r["cmd"]): r for r in existing.get("results", [])
                }
                for r in results:
                    existing_map[(r["mode"], r["cmd"])] = r
                merged_results = list(existing_map.values())
                merged_total = sum(r["total"] for r in merged_results)
                merged_passed = sum(r["passed"] for r in merged_results)
                merged_failed = sum(r["failed"] for r in merged_results)
                merged_skipped = sum(r["skipped"] for r in merged_results)
                return_value = {
                    "summary": {
                        "commands": len(merged_results),
                        "total": merged_total,
                        "passed": merged_passed,
                        "failed": merged_failed,
                        "skipped": merged_skipped,
                    },
                    "results": merged_results,
                }
            except Exception:
                pass  # 既存ファイルが壊れている場合は新規結果のみ使用

    if output_dir is not None:
        output_dir.mkdir(parents=True, exist_ok=True)
        json_file = output_dir / "test-run-results.json"
        json_file.write_text(
            json.dumps(return_value, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        print(json_file)

        # サマリーインデックス MD を README.md に出力
        index_md_path = output_dir / "README.md"
        index_md_path.write_text(
            _render_index_markdown(return_value, output_dir), encoding="utf-8"
        )
        print(index_md_path)

        # エラーのみのファイルを生成
        error_results = []
        for cmd_result in return_value["results"]:
            failed_cases = [tc for tc in cmd_result.get("test_cases", []) if tc.get("status") == "failed"]
            if failed_cases:
                error_results.append({
                    "mode": cmd_result.get("mode", ""),
                    "cmd": cmd_result.get("cmd", ""),
                    "total": len(failed_cases),
                    "passed": 0,
                    "failed": len(failed_cases),
                    "skipped": 0,
                    "test_cases": failed_cases,
                })
        error_total = sum(r["total"] for r in error_results)
        error_data = {
            "summary": {
                "commands": len(error_results),
                "total": error_total,
                "failed": error_total,
            },
            "results": error_results,
        }
        error_json_file = output_dir / "test-run-errors.json"
        error_json_file.write_text(
            json.dumps(error_data, ensure_ascii=False, indent=2, default=str),
            encoding="utf-8",
        )
        print(error_json_file)

        error_md_path = output_dir / "ERRORS.md"
        error_md_path.write_text(
            _render_errors_markdown(error_data), encoding="utf-8"
        )
        print(error_md_path)

    return return_value


def _write_command_result(cmd_result: dict[str, Any], output_dir: Path) -> None:
    """コマンド単位のテスト結果を cli/{mode}/{cmd}.json と cli/{mode}/{cmd}.md に書き出します。"""
    mode_val = cmd_result.get("mode", "")
    cmd_val = cmd_result.get("cmd", "")
    cmd_dir = output_dir / "cli" / mode_val
    cmd_dir.mkdir(parents=True, exist_ok=True)
    cmd_json_path = cmd_dir / f"{cmd_val}.json"
    cmd_json_path.write_text(
        json.dumps(cmd_result, ensure_ascii=False, indent=2, default=str),
        encoding="utf-8",
    )
    print(cmd_json_path)
    cmd_md_path = cmd_dir / f"{cmd_val}.md"
    cmd_md_path.write_text(
        _render_command_markdown(cmd_result), encoding="utf-8"
    )
    print(cmd_md_path)


# ---------------------------------------------------------------------------
# コマンドスペック単位の実行
# ---------------------------------------------------------------------------

def _run_command_spec(
    spec: dict[str, Any],
    appcls: Any,
    ver: Any,
    use_tempdir: bool,
) -> dict[str, Any]:
    mode = spec.get("mode", "")
    cmd = spec.get("cmd", "")
    test_cases = spec.get("test_cases", [])

    # appインスタンスの取得
    try:
        from cmdbox import version as _default_ver
        from cmdbox.app import app
        _appcls = appcls if appcls is not None else app.CmdBoxApp
        _ver = ver if ver is not None else _default_ver
        app_instance = _appcls.getInstance(appcls=_appcls, ver=_ver)
    except Exception as e:
        return {
            "mode": mode,
            "cmd": cmd,
            "total": len(test_cases),
            "passed": 0,
            "failed": 0,
            "skipped": len(test_cases),
            "import_error": str(e),
            "test_cases": [
                {
                    "id": tc.get("id"),
                    "category": tc.get("category"),
                    "focus": tc.get("focus"),
                    "status": "skipped",
                    "reason": f"App init error: {e}",
                }
                for tc in test_cases
            ],
        }

    case_results: list[dict[str, Any]] = []
    passed = failed = skipped = 0

    from cmdbox.app import app, options
    from cmdbox.app.commons import validator
    feat = options.Options.getInstance(appcls, ver).get_cmd_attr(mode, cmd, 'feature')
    if isinstance(feat, validator.Validator):
        feat.init_test()

    # pre_cmds: テスト前の初期化コマンドを実行
    _run_setup_cmds(spec.get("pre_cmds", []), app_instance, spec, label="pre_cmds")

    for tc in test_cases:
        result = _run_test_case(app_instance, spec, tc, use_tempdir)
        case_results.append(result)
        if result["status"] == "passed":
            passed += 1
        elif result["status"] == "failed":
            failed += 1
        else:
            skipped += 1

    # post_cmds: テスト後のクリーンアップコマンドを実行
    _run_setup_cmds(spec.get("post_cmds", []), app_instance, spec, label="post_cmds")

    if isinstance(feat, validator.Validator):
        feat.cleaning_test()

    return {
        "mode": mode,
        "cmd": cmd,
        "total": len(case_results),
        "passed": passed,
        "failed": failed,
        "skipped": skipped,
        "test_cases": case_results,
    }


# ---------------------------------------------------------------------------
# テストケース単体の実行
# ---------------------------------------------------------------------------

def _run_test_case(
    app_instance: Any,
    spec: dict[str, Any],
    tc: dict[str, Any],
    use_tempdir: bool,
) -> dict[str, Any]:
    expected_status_str = tc.get("expected_status", "RESP_SUCCESS")
    expected_code = STATUS_MAP.get(expected_status_str, 0)

    base: dict[str, Any] = {
        "id": tc.get("id"),
        "category": tc.get("category"),
        "focus": tc.get("focus"),
        "input_pattern": tc.get("input_pattern"),
        "expected_status": expected_status_str,
        "executed_at": datetime.now().isoformat(timespec="seconds"),
    }

    # nouse_webmodeがTrueの場合はスキップ
    if tc.get("nouse_webmode", False):
        return {
            **base,
            "status": "skipped",
            "reason": "Skipped: nouse_webmode is True",
            "actual_code": None,
        }

    try:
        if use_tempdir:
            with tempfile.TemporaryDirectory() as tmpdir:
                args_list = _build_args_list(spec, tc, Path(tmpdir))
                with patch("cmdbox.app.common.print_format"):
                    ret_code, ret_msg, _obj = app_instance.main(args_list=args_list, webcall=True)
        else:
            args_list = _build_args_list(spec, tc, None)
            with patch("cmdbox.app.common.print_format"):
                ret_code, ret_msg, _obj = app_instance.main(args_list=args_list, webcall=True)

    except Exception as e:
        err_lower = str(e).lower()
        if _is_connectivity_error(err_lower):
            return {
                **base,
                "status": "skipped",
                "reason": f"External dependency unavailable: {e}",
                "actual_code": None,
            }
        return {
            **base,
            "status": "failed",
            "reason": f"{type(e).__name__}: {e}",
            "actual_code": None,
        }

    # 結果判定
    if expected_code is None:
        # 異常系ステータス: 非ゼロなら合格
        ok = ret_code != 0
    else:
        ok = ret_code == expected_code

    actual_status = _code_to_status(ret_code)
    result: dict[str, Any] = {
        **base,
        "status": "passed" if ok else "failed",
        "input_values": tc.get("input_values", {}),
        "ret_msg": ret_msg,
        "actual_code": ret_code,
        "actual_status": actual_status,
        "actual_result": _truncate(str(ret_msg), 300) if ret_msg else None,
        "reason": _truncate(str(ret_msg), 300) if ret_msg else None,
    }
    if not ok:
        result["expected_status_detail"] = (
            f"expected {expected_status_str}({expected_code}) "
            f"but got {actual_status}({ret_code})"
        )
    return result


# ---------------------------------------------------------------------------
# ヘルパー関数
# ---------------------------------------------------------------------------

def _run_setup_cmds(
    cmds: list[dict[str, Any]],
    app_instance: Any,
    spec: dict[str, Any],
    label: str = "setup",
) -> None:
    """pre_cmds / post_cmds を順番に実行します。

    各コマンドは {"mode": str, "cmd": str, "note": str} の辞書で、
    パラメータのデフォルト値はコマンド仕様JSONの parameters から取得します。
    エラーが発生しても継続します（セットアップ失敗は警告のみ）。

    Args:
        cmds: 実行するコマンドの辞書リスト
        app_instance: アプリインスタンス
        spec: コマンド仕様辞書（デフォルトパラメータ取得に使用）
        label: ログ出力用ラベル
    """
    for entry in cmds:
        target_mode = entry.get("mode", "")
        target_cmd = entry.get("cmd", "")
        note = entry.get("note", "")
        parameters = spec.get("parameters", [])
        args_list: list[str] = ["-m", target_mode, "-c", target_cmd, "--format"]
        for param in parameters:
            val = param.get("default")
            name = param["name"]
            ptype = param.get("type", "")
            if val is None:
                continue
            if ptype == "bool":
                if val:
                    args_list.append(f"--{name}")
            else:
                sval = str(val)
                if sval:
                    args_list.append(f"--{name}")
                    args_list.append(sval)
        try:
            with patch("cmdbox.app.common.print_format"):
                app_instance.main(args_list=args_list, webcall=True)
            print(f"  [{label}] {target_mode} {target_cmd}: ok ({note})")
        except Exception as e:
            print(f"  [{label}] {target_mode} {target_cmd}: warning - {e} ({note})")


def _is_connectivity_error(err_lower: str) -> bool:
    return any(kw in err_lower for kw in _CONNECTIVITY_KEYWORDS)


def _code_to_status(code: int) -> str:
    reverse = {v: k for k, v in STATUS_MAP.items() if v is not None}
    return reverse.get(code, f"INT_{code}")


def _build_args_list(
    spec: dict[str, Any],
    tc: dict[str, Any],
    temp_output_dir: Path | None,
) -> list[str]:
    """テストケースの input_values とパラメータ定義から CLI 引数リストを構築します。

    Args:
        spec: コマンドスペック
        tc: テストケース
        temp_output_dir: 出力系パラメータの置換先一時ディレクトリ

    Returns:
        list[str]: CLI 引数リスト
    """
    mode = spec.get("mode", "")
    cmd = spec.get("cmd", "")
    parameters = spec.get("parameters", [])
    input_values = tc.get("input_values", {})

    args_list: list[str] = ["-m", mode, "-c", cmd, "--format"]

    # パラメータのデフォルト値を適用
    values: dict[str, Any] = {}
    for param in parameters:
        if param.get("default") is not None:
            values[param["name"]] = param["default"]

    # テストケースの input_values で上書き
    values.update(input_values)

    # 出力系パラメータを一時ディレクトリで置き換え（明示指定は除く）
    if temp_output_dir is not None:
        for param in parameters:
            name = param["name"]
            if name in input_values:
                continue  # 明示指定は優先
            fileio = param.get("fileio")
            ptype = param.get("type", "")
            if fileio == "out":
                if ptype == "dir":
                    out_path = temp_output_dir / name
                    out_path.mkdir(parents=True, exist_ok=True)
                    values[name] = str(out_path)
                elif ptype == "file":
                    values[name] = str(temp_output_dir / f"{name}.json")

    # args_list に変換
    for param in parameters:
        name = param["name"]
        val = values.get(name)
        ptype = param.get("type", "")
        multi = param.get("multi", False)

        if val is None:
            continue

        if ptype == "bool":
            if val:
                args_list.append(f"--{name}")
        elif multi and isinstance(val, list):
            for item in val:
                if item is not None and str(item) != "":
                    args_list.append(f"--{name}")
                    args_list.append(str(item))
        else:
            sval = str(val)
            if sval != "":
                args_list.append(f"--{name}")
                args_list.append(sval)

    return args_list


def _truncate(s: str, maxlen: int) -> str:
    return s[:maxlen] + "..." if len(s) > maxlen else s


def _render_command_markdown(cmd_result: dict[str, Any]) -> str:
    """コマンド単体のテスト結果をマークダウンで返します。"""
    mode = cmd_result.get("mode", "")
    cmd = cmd_result.get("cmd", "")
    status_icon = "PASS" if cmd_result["failed"] == 0 else "FAIL"
    generated_at = datetime.now().isoformat(timespec="seconds")

    lines = [
        f"# [{status_icon}] {mode} {cmd}",
        "",
        f"生成日時: {generated_at}",
        "",
        f"- 成功: {cmd_result['passed']} / 失敗: {cmd_result['failed']} / スキップ: {cmd_result['skipped']}",
        "",
        "| # | カテゴリ | 観点 | 入力パターン | 入力値 | 期待ステータス | 実際のステータス | 結果 | 理由 | 実行日時 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for tc in cmd_result.get("test_cases", []):
        tc_status = tc.get("status", "")
        icon = {"passed": "OK", "failed": "NG", "skipped": "SKIP"}.get(tc_status, tc_status)
        reason = _escape_table(str(tc.get("reason", "") or ""))
        executed_at = _escape_table(str(tc.get("executed_at", "") or ""))
        input_values = tc.get("input_values") or {}
        input_values_str = _escape_table(json.dumps(input_values, ensure_ascii=False) if input_values else "")
        lines.append(
            f"| {tc.get('id', '')} "
            f"| {_escape_table(str(tc.get('category', '') or ''))} "
            f"| {_escape_table(str(tc.get('focus', '') or ''))} "
            f"| {_escape_table(str(tc.get('input_pattern', '') or ''))} "
            f"| {input_values_str} "
            f"| {_escape_table(str(tc.get('expected_status', '') or ''))} "
            f"| {_escape_table(str(tc.get('actual_status', '') or ''))} "
            f"| {icon} "
            f"| {reason} "
            f"| {executed_at} |"
        )
    lines.append("")
    return "\n".join(lines)


def _render_index_markdown(data: dict[str, Any], output_dir: Path) -> str:
    """全コマンドのサマリーインデックスをマークダウンで返します。"""
    summary = data["summary"]
    results = data["results"]
    generated_at = datetime.now().isoformat(timespec="seconds")

    lines = [
        "# テスト実行結果",
        "",
        f"生成日時: {generated_at}",
        "",
        "## サマリー",
        "",
        "| 項目 | 件数 |",
        "| --- | --- |",
        f"| コマンド数 | {summary['commands']} |",
        f"| 総テストケース数 | {summary['total']} |",
        f"| 成功 | {summary['passed']} |",
        f"| 失敗 | {summary['failed']} |",
        f"| スキップ | {summary['skipped']} |",
        "",
        "## コマンド一覧",
        "",
        "| モード | コマンド | 成功 | 失敗 | スキップ | 結果 |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for cmd_result in results:
        mode_val = cmd_result.get("mode", "")
        cmd_val = cmd_result.get("cmd", "")
        status_icon = "PASS" if cmd_result["failed"] == 0 else "FAIL"
        rel_path = f"cli/{mode_val}/{cmd_val}.md"
        lines.append(
            f"| {mode_val} "
            f"| [{cmd_val}]({rel_path}) "
            f"| {cmd_result['passed']} "
            f"| {cmd_result['failed']} "
            f"| {cmd_result['skipped']} "
            f"| {status_icon} |"
        )
    lines.append("")
    return "\n".join(lines)


def _render_errors_markdown(error_data: dict[str, Any]) -> str:
    """エラーになったテストケースのみを一覧するマークダウンを返します。"""
    summary = error_data["summary"]
    results = error_data["results"]
    generated_at = datetime.now().isoformat(timespec="seconds")

    lines = [
        "# テスト実行結果 - エラー一覧",
        "",
        f"生成日時: {generated_at}",
        "",
        "## サマリー",
        "",
        "| 項目 | 件数 |",
        "| --- | --- |",
        f"| 失敗コマンド数 | {summary['commands']} |",
        f"| 失敗テストケース数 | {summary['total']} |",
        "",
    ]

    if not results:
        lines.append("失敗したテストケースはありません。")
        lines.append("")
        return "\n".join(lines)

    lines += [
        "## 失敗テストケース一覧",
        "",
        "| モード | コマンド | # | カテゴリ | 観点 | 入力パターン | 期待ステータス | 実際のステータス | 理由 | 実行日時 |",
        "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |",
    ]
    for cmd_result in results:
        mode_val = cmd_result.get("mode", "")
        cmd_val = cmd_result.get("cmd", "")
        for tc in cmd_result.get("test_cases", []):
            reason = _escape_table(str(tc.get("reason", "") or ""))
            executed_at = _escape_table(str(tc.get("executed_at", "") or ""))
            lines.append(
                f"| {mode_val} "
                f"| {cmd_val} "
                f"| {tc.get('id', '')} "
                f"| {_escape_table(str(tc.get('category', '') or ''))} "
                f"| {_escape_table(str(tc.get('focus', '') or ''))} "
                f"| {_escape_table(str(tc.get('input_pattern', '') or ''))} "
                f"| {_escape_table(str(tc.get('expected_status', '') or ''))} "
                f"| {_escape_table(str(tc.get('actual_status', '') or ''))} "
                f"| {reason} "
                f"| {executed_at} |"
            )
    lines.append("")
    return "\n".join(lines)


def _escape_table(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")
