# DX Tool #003 Acceptance Testing
# Comprehensive test suite for ail static_analyzer tool

import os
import sys
import subprocess
import time
import tracemalloc
import hashlib
import json
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def hash_file(path: Path) -> str:
    """Get SHA-256 hash of file content."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


def test_tool_runs_successfully() -> bool:
    """Test: python -m tools.ail_static_analyzer runs successfully."""
    print("TEST 1: Tool runs successfully...")
    code, out, err = run_command([sys.executable, "-m", "tools.ail_static_analyzer", "apps/static_analyzer/main.ail"])
    if code == 0:
        print("  ✓ PASS: Tool exits with code 0")
        return True
    else:
        print(f"  ✗ FAIL: Exit code {code}")
        print(f"  Stderr: {err[:500]}")
        return False


def test_output_files_created() -> bool:
    """Test: Both output files are created."""
    print("\nTEST 2: Output files created...")
    root = Path(__file__).resolve().parent.parent
    md_path = root / "generated" / "STATIC_ANALYZER_REPORT.md"
    json_path = root / "generated" / "STATIC_ANALYZER_REPORT.json"

    if md_path.exists() and json_path.exists():
        print(f"  ✓ PASS: Both output files exist")
        return True
    else:
        if not md_path.exists():
            print(f"  ✗ FAIL: {md_path} not found")
        if not json_path.exists():
            print(f"  ✗ FAIL: {json_path} not found")
        return False


def test_deterministic_output() -> bool:
    """Test: Running twice produces identical JSON output."""
    print("\nTEST 3: Deterministic output (running twice)...")
    root = Path(__file__).resolve().parent.parent
    json_path = root / "generated" / "STATIC_ANALYZER_REPORT.json"

    hash1 = hash_file(json_path)
    run_command([sys.executable, "-m", "tools.ail_static_analyzer", "apps/static_analyzer/main.ail"])
    hash2 = hash_file(json_path)

    if hash1 == hash2:
        print(f"  ✓ PASS: Hashes match ({hash1[:16]}...)")
        return True
    else:
        print(f"  ✗ FAIL: Hashes differ")
        return False


def test_json_structure() -> bool:
    """Test: JSON output has correct structure."""
    print("\nTEST 4: JSON structure validation...")
    root = Path(__file__).resolve().parent.parent
    json_path = root / "generated" / "STATIC_ANALYZER_REPORT.json"

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  ✗ FAIL: Invalid JSON: {e}")
        return False

    if not isinstance(data, list):
        print(f"  ✗ FAIL: JSON should be a list")
        return False

    if len(data) == 0:
        print(f"  ✗ FAIL: JSON list is empty")
        return False

    required_keys = ["path", "total_lines", "functions", "unreachable_functions", "undocumented_functions"]
    missing = [k for k in required_keys if k not in data[0]]
    if missing:
        print(f"  ✗ FAIL: Missing keys: {missing}")
        return False

    print(f"  ✓ PASS: JSON has correct structure with {len(data)} file(s)")
    return True


def test_directory_analysis() -> bool:
    """Test: Tool can analyze a directory."""
    print("\nTEST 5: Directory analysis...")
    code, out, err = run_command([sys.executable, "-m", "tools.ail_static_analyzer", "apps"])
    file_count = out.count("Analyzed:")
    if file_count > 0:
        print(f"  ✓ PASS: Analyzed {file_count} file(s) (exit: {code})")
        return True
    else:
        print(f"  ✗ FAIL: Directory analysis failed (exit: {code})")
        return False


def test_performance() -> tuple[bool, float, int, int]:
    """Test: Measure generation time and memory usage."""
    print("\nTEST 6: Performance measurement...")

    tracemalloc.start()
    start_time = time.perf_counter()

    code, out, err = run_command([sys.executable, "-m", "tools.ail_static_analyzer", "apps/static_analyzer"])

    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  Generation time: {elapsed:.4f}s")
    print(f"  Peak memory: {peak / 1024:.2f} KB")

    time_ok = elapsed < 30.0
    memory_ok = peak < 100 * 1024 * 1024

    if time_ok and memory_ok and code == 0:
        print("  ✓ PASS: Performance within thresholds")
        return True, elapsed, peak, code
    else:
        print("  ✗ FAIL: Performance outside thresholds")
        return False, elapsed, peak, code


def test_thresholds() -> bool:
    """Test: Threshold arguments work."""
    print("\nTEST 7: Threshold arguments...")
    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_static_analyzer",
        "apps/static_analyzer/main.ail",
        "--max-depth", "20",
        "--large-file-threshold", "5000",
        "--many-functions-threshold", "200"
    ])

    if code == 0:
        print("  ✓ PASS: Thresholds accepted")
        return True
    else:
        print(f"  ✗ FAIL: Threshold arguments failed")
        return False


def test_output_modes() -> bool:
    """Test: --json-only and --markdown-only work."""
    print("\nTEST 8: Output mode arguments...")
    root = Path(__file__).resolve().parent.parent
    orig_md = (root / "generated" / "STATIC_ANALYZER_REPORT.md").read_text(encoding="utf-8") if (root / "generated" / "STATIC_ANALYZER_REPORT.md").exists() else ""

    # Test json-only
    code1, _, _ = run_command([sys.executable, "-m", "tools.ail_static_analyzer", "apps/static_analyzer/main.ail", "--json-only"])

    # Test markdown-only
    code2, _, _ = run_command([sys.executable, "-m", "tools.ail_static_analyzer", "apps/static_analyzer/main.ail", "--markdown-only"])

    if code1 == 0 and code2 == 0:
        print("  ✓ PASS: Output modes work")
        return True
    else:
        print(f"  ✗ FAIL: Output modes failed")
        return False


def main() -> int:
    """Run all acceptance tests."""
    print("=" * 60)
    print("DX TOOL #003 ACCEPTANCE TEST SUITE")
    print("=" * 60)

    results = {
        "Tool runs successfully": test_tool_runs_successfully(),
        "Output files created": test_output_files_created(),
        "Deterministic output": test_deterministic_output(),
        "JSON structure valid": test_json_structure(),
        "Directory analysis": test_directory_analysis(),
        "Threshold arguments": test_thresholds(),
        "Output modes": test_output_modes(),
    }

    perf_ok, elapsed, peak, code = test_performance()
    results["Performance OK"] = perf_ok

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "✓" if passed else "✗"
        print(f"  {symbol} {name}: {status}")

    all_passed = all(results.values())
    print("\n" + ("ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"))

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())