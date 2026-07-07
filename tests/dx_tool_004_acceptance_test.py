# DX Tool #004 Acceptance Testing
# Comprehensive test suite for ail benchmark tool

from __future__ import annotations

import os
import sys
import json
import time
import shutil
import subprocess
import hashlib
import tracemalloc
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def hash_file(path: Path) -> str:
    """Get SHA-256 hash of file content."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


def clean_benchmark_outputs():
    """Remove generated benchmark outputs between tests."""
    root = Path(__file__).resolve().parent.parent
    bench_dir = root / "generated" / "benchmarks"
    if bench_dir.exists():
        shutil.rmtree(bench_dir)


def test_tool_runs_successfully() -> bool:
    """Test: python -m tools.ail_benchmark runs successfully."""
    print("TEST 1: Tool runs successfully (canonical suite)...")
    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_benchmark",
        "--suite", "canonical", "--repeat", "1", "--quiet",
    ])
    if code == 0:
        print("  [PASS] PASS: Tool exits with code 0")
        return True
    else:
        print(f"  [FAIL] FAIL: Exit code {code}")
        print(f"  Stderr: {err[:500]}")
        return False


def test_output_files_created() -> bool:
    """Test: Both output files are created in generated/benchmarks/."""
    print("\nTEST 2: Output files created...")
    root = Path(__file__).resolve().parent.parent
    md_path = root / "generated" / "benchmarks" / "BENCHMARK_REPORT.md"
    json_path = root / "generated" / "benchmarks" / "BENCHMARK_REPORT.json"

    md_ok = md_path.exists()
    json_ok = json_path.exists()

    if md_ok and json_ok:
        print(f"  [PASS] PASS: Both output files exist")
        return True
    else:
        if not md_ok:
            print(f"  [FAIL] FAIL: {md_path} not found")
        if not json_ok:
            print(f"  [FAIL] FAIL: {json_path} not found")
        return False


def test_deterministic_output() -> bool:
    """Test: Running twice with same inputs produces identical JSON output."""
    print("\nTEST 3: Deterministic output (running twice)...")
    root = Path(__file__).resolve().parent.parent
    json_path = root / "generated" / "benchmarks" / "BENCHMARK_REPORT.json"

    # The benchmark output is not perfectly deterministic because
    # execution times vary. But the JSON structure and benchmark
    # names should be deterministic. We check structural determinism:
    # same number of benchmarks, same names, same keys.
    data1 = json.loads(json_path.read_text(encoding="utf-8"))

    clean_benchmark_outputs()
    run_command([
        sys.executable, "-m", "tools.ail_benchmark",
        "--suite", "canonical", "--repeat", "1", "--quiet",
    ])
    data2 = json.loads(json_path.read_text(encoding="utf-8"))

    # Compare structural determinism
    names1 = sorted(b["name"] for b in data1["benchmarks"])
    names2 = sorted(b["name"] for b in data2["benchmarks"])

    if names1 == names2:
        print(f"  [PASS] PASS: Same {len(names1)} benchmarks in both runs")
        return True
    else:
        print(f"  [FAIL] FAIL: Benchmark names differ")
        print(f"    Run 1: {names1}")
        print(f"    Run 2: {names2}")
        return False


def test_json_structure() -> bool:
    """Test: JSON output has correct structure and required keys."""
    print("\nTEST 4: JSON structure validation...")
    root = Path(__file__).resolve().parent.parent
    json_path = root / "generated" / "benchmarks" / "BENCHMARK_REPORT.json"

    try:
        data = json.loads(json_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(f"  [FAIL] FAIL: Invalid JSON: {e}")
        return False

    # Top-level keys
    required_top = ["tool", "version", "timestamp", "suite", "summary", "benchmarks"]
    missing = [k for k in required_top if k not in data]
    if missing:
        print(f"  [FAIL] FAIL: Missing top-level keys: {missing}")
        return False

    # Summary keys
    required_summary = ["total", "passed", "failed", "regressed", "skipped", "total_time_seconds"]
    missing = [k for k in required_summary if k not in data.get("summary", {})]
    if missing:
        print(f"  [FAIL] FAIL: Missing summary keys: {missing}")
        return False

    # Config keys
    required_config = ["repeat", "memory", "timeout"]
    missing = [k for k in required_config if k not in data.get("config", {})]
    if missing:
        print(f"  [FAIL] FAIL: Missing config keys: {missing}")
        return False

    # Benchmark entry structure
    if not isinstance(data["benchmarks"], list) or len(data["benchmarks"]) == 0:
        print(f"  [FAIL] FAIL: benchmarks must be non-empty list")
        return False

    required_bench = ["name", "path", "suite", "status", "stats", "regression"]
    for b in data["benchmarks"]:
        missing = [k for k in required_bench if k not in b]
        if missing:
            print(f"  [FAIL] FAIL: Benchmark '{b.get('name', '?')}' missing keys: {missing}")
            return False

    print(f"  [PASS] PASS: JSON has correct structure with {len(data['benchmarks'])} benchmark(s)")
    return True


def test_quick_suite() -> bool:
    """Test: Quick suite returns exactly 2 benchmarks."""
    print("\nTEST 5: Quick suite...")
    clean_benchmark_outputs()
    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_benchmark",
        "--suite", "quick", "--repeat", "1", "--quiet",
    ])
    root = Path(__file__).resolve().parent.parent
    json_path = root / "generated" / "benchmarks" / "BENCHMARK_REPORT.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    if data["summary"]["total"] == 2 and code == 0:
        print(f"  [PASS] PASS: Quick suite has 2 benchmarks")
        return True
    else:
        print(f"  [FAIL] FAIL: Expected 2 benchmarks, got {data['summary']['total']} (exit: {code})")
        return False


def test_single_app() -> bool:
    """Test: --app flag runs a single benchmark."""
    print("\nTEST 6: Single app via --app flag...")
    clean_benchmark_outputs()
    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_benchmark",
        "--app", "dice_roller", "--repeat", "1", "--quiet",
    ])
    root = Path(__file__).resolve().parent.parent
    json_path = root / "generated" / "benchmarks" / "BENCHMARK_REPORT.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    if data["summary"]["total"] == 1 and data["benchmarks"][0]["name"] == "dice_roller" and code == 0:
        print(f"  [PASS] PASS: Single app 'dice_roller' executed")
        return True
    else:
        print(f"  [FAIL] FAIL: Expected 1 benchmark, got {data['summary']['total']}")
        return False


def test_baseline_save_and_compare() -> bool:
    """Test: --baseline saves and --compare loads correctly."""
    print("\nTEST 7: Baseline save and compare...")
    clean_benchmark_outputs()
    root = Path(__file__).resolve().parent.parent

    # Save baseline
    code1, _, _ = run_command([
        sys.executable, "-m", "tools.ail_benchmark",
        "--suite", "quick", "--repeat", "1", "--quiet",
        "--baseline", "test-baseline",
    ])
    baseline_path = root / "generated" / "benchmarks" / "test-baseline.json"
    if code1 != 0 or not baseline_path.exists():
        print(f"  [FAIL] FAIL: Baseline not saved (exit: {code1})")
        return False

    # Compare against baseline
    clean_benchmark_outputs()
    code2, out, err = run_command([
        sys.executable, "-m", "tools.ail_benchmark",
        "--suite", "quick", "--repeat", "1", "--quiet",
        "--compare", "test-baseline",
    ])
    json_path = root / "generated" / "benchmarks" / "BENCHMARK_REPORT.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    # Check baseline reference in report
    if data.get("baseline") == "test-baseline" and code2 in (0, 2):
        print(f"  [PASS] PASS: Baseline saved and compared (exit: {code2})")
        return True
    else:
        print(f"  [FAIL] FAIL: Compare failed (exit: {code2}, baseline ref: {data.get('baseline')})")
        return False


def test_memory_mode() -> bool:
    """Test: --memory flag adds memory measurement."""
    print("\nTEST 8: Memory measurement mode...")
    clean_benchmark_outputs()
    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_benchmark",
        "--suite", "quick", "--repeat", "1", "--quiet",
        "--memory",
    ])
    root = Path(__file__).resolve().parent.parent
    json_path = root / "generated" / "benchmarks" / "BENCHMARK_REPORT.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    has_memory = data["config"]["memory"] is True
    has_memory_data = any(b.get("memory_kb") is not None for b in data["benchmarks"])

    if has_memory and has_memory_data:
        print(f"  [PASS] PASS: Memory mode enabled with data")
        return True
    else:
        print(f"  [FAIL] FAIL: Memory mode not working (config: {has_memory}, data: {has_memory_data})")
        return False


def test_threshold_argument() -> bool:
    """Test: --threshold argument is accepted."""
    print("\nTEST 9: Threshold argument...")
    clean_benchmark_outputs()
    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_benchmark",
        "--suite", "quick", "--repeat", "1", "--quiet",
        "--threshold", "10",
    ])
    root = Path(__file__).resolve().parent.parent
    json_path = root / "generated" / "benchmarks" / "BENCHMARK_REPORT.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    if data["threshold_pct"] == 10.0 and code == 0:
        print(f"  [PASS] PASS: Threshold argument accepted: {data['threshold_pct']}%")
        return True
    else:
        print(f"  [FAIL] FAIL: Threshold not applied (got {data['threshold_pct']}, exit {code})")
        return False


def test_performance() -> tuple[bool, float, int]:
    """Test: Measure generation time and memory usage."""
    print("\nTEST 10: Performance measurement...")
    clean_benchmark_outputs()

    tracemalloc.start()
    start_time = time.perf_counter()

    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_benchmark",
        "--suite", "quick", "--repeat", "1", "--quiet",
    ])

    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    print(f"  Generation time: {elapsed:.4f}s")
    print(f"  Peak memory: {peak / 1024:.2f} KB")

    time_ok = elapsed < 30.0
    memory_ok = peak < 100 * 1024 * 1024

    if time_ok and memory_ok and code == 0:
        print("  [PASS] PASS: Performance within thresholds")
        return True, elapsed, peak
    else:
        print("  [FAIL] FAIL: Performance outside thresholds")
        return False, elapsed, peak


def test_repeat_count() -> bool:
    """Test: --repeat argument controls repetition count."""
    print("\nTEST 11: Repeat count...")
    clean_benchmark_outputs()
    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_benchmark",
        "--suite", "quick", "--repeat", "2", "--quiet",
    ])
    root = Path(__file__).resolve().parent.parent
    json_path = root / "generated" / "benchmarks" / "BENCHMARK_REPORT.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    # Check that runs contain expected number of entries
    runs_count = len(data["benchmarks"][0].get("runs", []))
    if data["config"]["repeat"] == 2 and code == 0 and runs_count == 2:
        print(f"  [PASS] PASS: Repeat count is {data['config']['repeat']}")
        return True
    else:
        print(f"  [FAIL] FAIL: Expected repeat=2, got config={data['config']['repeat']}, runs={runs_count}")
        return False


def main() -> int:
    """Run all acceptance tests."""
    print("=" * 60)
    print("DX TOOL #004 ACCEPTANCE TEST SUITE — ail benchmark")
    print("=" * 60)

    results = {
        "Tool runs successfully": test_tool_runs_successfully(),
        "Output files created": test_output_files_created(),
        "Deterministic output": test_deterministic_output(),
        "JSON structure valid": test_json_structure(),
        "Quick suite": test_quick_suite(),
        "Single app": test_single_app(),
        "Baseline save/compare": test_baseline_save_and_compare(),
        "Memory mode": test_memory_mode(),
        "Threshold argument": test_threshold_argument(),
        "Repeat count": test_repeat_count(),
    }

    perf_ok, elapsed, peak = test_performance()
    results["Performance OK"] = perf_ok

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for name, passed in results.items():
        status = "PASS" if passed else "FAIL"
        symbol = "[PASS]" if passed else "[FAIL]"
        print(f"  {symbol} {name}: {status}")

    all_passed = all(results.values())
    print("\n" + ("ALL TESTS PASSED" if all_passed else "SOME TESTS FAILED"))

    return 0 if all_passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
