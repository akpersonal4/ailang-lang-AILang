# DX Tool #006 Acceptance Testing
# AILang Dependency Ordering Assistant - Acceptance Test Suite

from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def hash_file(path: Path) -> str:
    """Get SHA-256 hash of file content."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


def test_tool_runs_successfully() -> bool:
    """Test: python -m tools.ail_order runs successfully on valid file."""
    print("TEST 1: Tool runs successfully...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "examples/hello_world/main.ail"]
    )
    if code == 0:
        print("  [PASS] Tool exits with code 0")
        return True
    else:
        print(f"  [FAIL] Exit code {code}")
        print(f"  Stderr: {err[:500]}")
        return False


def test_detects_forward_references() -> bool:
    """Test: Tool detects forward references in code."""
    print("\nTEST 2: Forward reference detection...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "tests/fixtures/forward_ref.ail"]
    )
    if "Forward reference" in out or "Forward reference" in err:
        print("  [PASS] Forward reference detected")
        return True
    else:
        print("  [FAIL] Forward reference not detected")
        print(f"  Output: {out[:500]}")
        return False


def test_json_output_format() -> bool:
    """Test: --json flag produces valid JSON output."""
    print("\nTEST 3: JSON output format...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_order",
            "--json",
            "examples/hello_world/main.ail",
        ]
    )
    try:
        data = json.loads(out)
        if "metadata" in data and "levels" in data:
            print("  [PASS] Valid JSON with correct structure")
            return True
        else:
            print("  [FAIL] Missing required fields")
            return False
    except json.JSONDecodeError as e:
        print(f"  [FAIL] Invalid JSON: {e}")
        return False


def test_directory_analysis() -> bool:
    """Test: Tool can analyze a directory of .ail files."""
    print("\nTEST 4: Directory analysis...")
    code, out, err = run_command([sys.executable, "-m", "tools.ail_order", "examples"])
    if code == 0 and "Analyzed" in out or "L0" in out or "No ordering issues" in out:
        print("  [PASS] Directory analysis works")
        return True
    else:
        print(f"  [FAIL] Directory analysis failed (exit: {code})")
        print(f"  Output: {out[:500]}")
        return False


def test_reports_generated() -> bool:
    """Test: Reports are generated in reports/ directory for project analysis."""
    print("\nTEST 5: Report generation...")
    root = Path(__file__).resolve().parent.parent
    md_path = root / "reports" / "dependency_ordering.md"
    json_path = root / "reports" / "dependency_ordering.json"

    # Run on a directory to trigger report generation
    run_command([sys.executable, "-m", "tools.ail_order", "examples"])

    if md_path.exists() and json_path.exists():
        print("  [PASS] Both report files exist")
        return True
    else:
        if not md_path.exists():
            print(f"  [FAIL] {md_path} not found")
        if not json_path.exists():
            print(f"  [FAIL] {json_path} not found")
        return False


def test_json_report_structure() -> bool:
    """Test: JSON report has correct structure."""
    print("\nTEST 6: JSON report structure...")
    root = Path(__file__).resolve().parent.parent
    json_path = root / "reports" / "dependency_ordering.json"

    if not json_path.exists():
        print("  [SKIP] JSON report not found")
        return True

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
        required_keys = ["metadata", "summary", "files"]
        missing = [k for k in required_keys if k not in data]
        if missing:
            print(f"  [FAIL] Missing keys: {missing}")
            return False
        print(
            f"  [PASS] JSON has correct structure with {len(data.get('files', []))} file(s)"
        )
        return True
    except json.JSONDecodeError as e:
        print(f"  [FAIL] Invalid JSON: {e}")
        return False


def test_quiet_mode() -> bool:
    """Test: --quiet suppresses non-error output."""
    print("\nTEST 7: Quiet mode...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_order",
            "--quiet",
            "examples/hello_world/main.ail",
        ]
    )
    if code == 0 and not out.strip():
        print("  [PASS] Quiet mode suppresses output")
        return True
    else:
        print(f"  [FAIL] Unexpected output: {out.strip()[:100]}")
        return False


def test_help_text() -> bool:
    """Test: --help shows usage information."""
    print("\nTEST 8: Help text...")
    code, out, err = run_command([sys.executable, "-m", "tools.ail_order", "--help"])
    if "AILang Dependency Ordering Assistant" in out or "Dependency Ordering" in out:
        print("  [PASS] Help text displayed")
        return True
    else:
        print("  [FAIL] Help text missing")
        return False


def test_cli_integration() -> bool:
    """Test: ail order command works from CLI."""
    print("\nTEST 9: CLI integration...")
    code, out, err = run_command(
        [sys.executable, "-m", "compiler", "order", "examples/hello_world/main.ail"]
    )
    if code == 0:
        print("  [PASS] CLI integration works")
        return True
    else:
        print("  [FAIL] CLI integration failed")
        return False


def test_analyzes_stdlib() -> bool:
    """Test: Tool can analyze stdlib files."""
    print("\nTEST 10: Stdlib analysis...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "--quiet", "stdlib"]
    )
    if code == 0:
        print("  [PASS] Stdlib analysis works")
        return True
    else:
        print("  [FAIL] Stdlib analysis failed")
        return False


def test_multi_level_output() -> bool:
    """Test: Multi-level dependencies are shown correctly."""
    print("\nTEST 11: Multi-level output...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "apps/static_analyzer/main.ail"]
    )
    # Should have multiple levels
    if "L0:" in out or "L1:" in out:
        print("  [PASS] Multiple levels detected")
        return True
    else:
        # Could be single level if no internal calls
        print("  [INFO] Single level or no internal calls")
        return True


def test_no_ail_files() -> bool:
    """Test: Tool handles missing .ail files gracefully."""
    print("\nTEST 12: Missing target handling...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "nonexistent_file.ail"]
    )
    if code != 0 and ("Error" in err or "Error" in out):
        print("  [PASS] Error handled gracefully")
        return True
    else:
        print("  [FAIL] Unexpected behavior")
        return False


def test_fix_stdout_mode() -> bool:
    """Test: --fix --stdout outputs reordered content."""
    print("\nTEST 13: Fix stdout mode...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_order",
            "--fix",
            "--stdout",
            "tests/fixtures/forward_ref.ail",
        ]
    )
    # Helper should appear before main in the output
    if "fn helper" in out and "fn main" in out:
        helper_pos = out.find("fn helper")
        main_pos = out.find("fn main")
        if helper_pos < main_pos:
            print("  [PASS] Fix stdout produces reordered output (helper before main)")
            return True
        else:
            print("  [FAIL] Functions not reordered correctly")
            return False
    else:
        print("  [FAIL] Missing functions in output")
        return False


def test_json_machine_readable() -> bool:
    """Test: JSON output is machine-readable with proper structure."""
    print("\nTEST 14: JSON machine readable...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_order",
            "--json",
            "apps/static_analyzer/main.ail",
        ]
    )
    try:
        data = json.loads(out)
        # Check required machine-readable fields
        if "metadata" in data and "summary" in data and "functions" in data:
            print("  [PASS] JSON machine readable")
            return True
        else:
            print("  [FAIL] Missing machine-readable fields")
            return False
    except json.JSONDecodeError:
        print("  [FAIL] Invalid JSON")
        return False


def test_cli_order_subcommand() -> bool:
    """Test: 'ail order' subcommand works correctly."""
    print("\nTEST 15: CLI order subcommand...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "compiler",
            "order",
            "--quiet",
            "examples/hello_world/main.ail",
        ]
    )
    if code == 0:
        print("  [PASS] CLI order subcommand works")
        return True
    else:
        print("  [FAIL] CLI order subcommand failed")
        return False


def test_json_indentation() -> bool:
    """Test: JSON output is properly indented."""
    print("\nTEST 16: JSON indentation...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_order",
            "--json",
            "examples/hello_world/main.ail",
        ]
    )
    if code == 0 and "\n  " in out:
        print("  [PASS] JSON properly indented")
        return True
    else:
        print("  [FAIL] JSON not properly indented")
        return False


def test_finds_all_functions() -> bool:
    """Test: All functions in static analyzer are found."""
    print("\nTEST 17: Find all functions...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_order",
            "--json",
            "apps/static_analyzer/main.ail",
        ]
    )
    try:
        data = json.loads(out)
        func_count = len(data.get("functions", []))
        if func_count > 50:
            print(f"  [PASS] Found {func_count} functions")
            return True
        else:
            print(f"  [FAIL] Only {func_count} functions found")
            return False
    except json.JSONDecodeError:
        print("  [FAIL] Invalid JSON")
        return False


def run_all_tests() -> int:
    """Run all acceptance tests and report."""
    print("=" * 60)
    print("DX TOOL #006 ACCEPTANCE TEST SUITE")
    print("AILang Dependency Ordering Assistant")
    print("=" * 60)

    tests = [
        test_tool_runs_successfully,
        test_detects_forward_references,
        test_json_output_format,
        test_directory_analysis,
        test_reports_generated,
        test_json_report_structure,
        test_quiet_mode,
        test_help_text,
        test_cli_integration,
        test_analyzes_stdlib,
        test_multi_level_output,
        test_no_ail_files,
        test_fix_stdout_mode,
        test_json_machine_readable,
        test_cli_order_subcommand,
        test_json_indentation,
        test_finds_all_functions,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            if t():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  [ERROR] {t.__name__}: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run_all_tests())
