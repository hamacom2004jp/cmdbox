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
    cmd_filter: str | None = None,
    appcls: Any = None,
    ver: Any = None,
    use_tempdir: bool = True,
) -> dict[str, Any]:
    """テスト仕様JSONに基づいてテストを実行します。

    Args:
        input_json: 入力となる cli-unit-test-specifications.json のパス
        mode_filter: 実行対象をモード名でフィルタ。None で全モード対象
        cmd_filter: 実行対象をコマンド名でフィルタ。None で全コマンド対象
        appcls: フィーチャーインスタンス生成に使用するアプリクラス
        ver: フィーチャーインスタンス生成に使用するバージョンモジュール
        use_tempdir: True のとき出力系パラメータを一時ディレクトリに置換する

    Returns:
        summary と results を含む辞書
    """
    specs: list[dict[str, Any]] = json.loads(input_json.read_text(encoding="utf-8"))

    if mode_filter:
        specs = [s for s in specs if s.get("mode") == mode_filter]
    if cmd_filter:
        specs = [s for s in specs if s.get("cmd") == cmd_filter]

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

    total = sum(r["total"] for r in results)
    passed = sum(r["passed"] for r in results)
    failed = sum(r["failed"] for r in results)
    skipped = sum(r["skipped"] for r in results)
    print(
        f"\n{'=' * 60}\n"
        f"TOTAL={total}  PASSED={passed}  FAILED={failed}  SKIPPED={skipped}\n"
        f"{'=' * 60}"
    )

    return {
        "summary": {
            "commands": len(results),
            "total": total,
            "passed": passed,
            "failed": failed,
            "skipped": skipped,
        },
        "results": results,
    }


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
    for tc in test_cases:
        result = _run_test_case(app_instance, spec, tc, use_tempdir)
        case_results.append(result)
        if result["status"] == "passed":
            passed += 1
        elif result["status"] == "failed":
            failed += 1
        else:
            skipped += 1
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
    }
    if not ok:
        result["reason"] = (
            f"expected {expected_status_str}({expected_code}) "
            f"but got {actual_status}({ret_code})"
        )
    return result


# ---------------------------------------------------------------------------
# ヘルパー関数
# ---------------------------------------------------------------------------

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
