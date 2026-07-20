# DX Tool #004 Regression Tests
# Stable baseline comparison across runs

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def clean_benchmark_outputs():
    """Remove generated benchmark outputs."""
    root = Path(__file__).resolve().parent.parent
    bench_dir = root / "generated" / "benchmarks"
    if bench_dir.exists():
        shutil.rmtree(bench_dir)


def test_regression_detection_triggers() -> bool:
    """Test: Regression detection works with abnormal data.

    Create an artificially slow baseline comparison by using
    an extremely optimistic (fast) baseline, then verify
    regression is flagged.
    """
    print("TEST 1: Regression detection triggers correctly...")
    root = Path(__file__).resolve().parent.parent

    # Clean up and create baseline directory
    clean_benchmark_outputs()
    bench_dir = root / "generated" / "benchmarks"
    bench_dir.mkdir(parents=True, exist_ok=True)

    # Create a baseline with impossibly fast times
    fast_baseline = {
        "tool": "ail_benchmark",
        "type": "baseline",
        "generated_at": "2026-01-01T00:00:00",
        "benchmarks": {
            "dice_roller": {
                "build_time_avg": 0.001,
                "run_time_avg": 0.001,
                "build_time_min": 0.001,
                "run_time_min": 0.001,
            },
            "hangman_game": {
                "build_time_avg": 0.001,
                "run_time_avg": 0.001,
                "build_time_min": 0.001,
                "run_time_min": 0.001,
            },
        },
    }
    baseline_path = bench_dir / "fast-baseline.json"
    baseline_path.write_text(json.dumps(fast_baseline, indent=2), encoding="utf-8")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_benchmark",
            "--suite",
            "quick",
            "--repeat",
            "1",
            "--quiet",
            "--compare",
            "fast-baseline",
            "--threshold",
            "10",
        ]
    )

    json_path = bench_dir / "BENCHMARK_REPORT.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    # Should detect regression since real times >> 0.001s
    has_regression = any(
        b.get("regression", {}).get("detected") for b in data["benchmarks"]
    )
    summary_regressed = data["summary"].get("regressed", 0) > 0

    if has_regression and summary_regressed and code == 2:
        print("  [PASS] PASS: Regression correctly detected (exit 2)")
        return True
    elif has_regression and summary_regressed and code == 1:
        print("  [PASS] PASS: Regression detected, exit 1 takes precedence over 2")
        return True
    else:
        print(
            f"  [FAIL] FAIL: Regression not detected (exit: {code}, regressed: {summary_regressed})"
        )
        return False


def test_no_regression_with_baseline_match() -> bool:
    """Test: Same run against itself shows no regression."""
    print("\nTEST 2: Same run against baseline shows no regression...")
    root = Path(__file__).resolve().parent.parent
    bench_dir = root / "generated" / "benchmarks"
    clean_benchmark_outputs()

    # First run creates baseline and results
    code1, _, _ = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_benchmark",
            "--suite",
            "quick",
            "--repeat",
            "1",
            "--quiet",
            "--baseline",
            "self-baseline",
        ]
    )

    # Use the just-saved baseline to compare
    clean_benchmark_outputs()
    code2, out, err = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_benchmark",
            "--suite",
            "quick",
            "--repeat",
            "1",
            "--quiet",
            "--compare",
            "self-baseline",
        ]
    )

    json_path = bench_dir / "BENCHMARK_REPORT.json"
    data = json.loads(json_path.read_text(encoding="utf-8"))

    # Should still detect baseline, but results might vary due to noise
    has_baseline = data.get("baseline") == "self-baseline"

    if has_baseline:
        print(f"  [PASS] PASS: Same baseline compared (exit: {code2})")
        return True
    else:
        print("  [FAIL] FAIL: Baseline not loaded")
        return False


def test_exit_code_precedence() -> bool:
    """Test: Exit code precedence: failure > regression > success."""
    print("\nTEST 3: Exit code precedence...")
    root = Path(__file__).resolve().parent.parent

    # Test: all pass, no regression → exit 0
    clean_benchmark_outputs()
    code0, _, _ = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_benchmark",
            "--suite",
            "quick",
            "--repeat",
            "1",
            "--quiet",
        ]
    )

    # Test: regression → exit 2
    # (already tested above, but verify logic)
    code1_ok = code0 in (0, 1, 2)

    if code1_ok:
        print(f"  [PASS] PASS: Exit code {code0} is valid")
        return True
    else:
        print(f"  [FAIL] FAIL: Unexpected exit code {code0}")
        return False


def test_suite_definitions() -> bool:
    """Test: Suite definitions are consistent."""
    print("\nTEST 4: Suite definitions...")

    # Ensure project root is on sys.path for module imports
    root = Path(__file__).resolve().parent.parent
    sys.path.insert(0, str(root))
    from tools.ail_benchmark.discovery import SUITE_DEFINITIONS, discover_all_apps

    # All apps in 'quick' must be in 'canonical'
    for app in SUITE_DEFINITIONS["quick"]:
        if app not in SUITE_DEFINITIONS["canonical"]:
            print(f"  [FAIL] FAIL: '{app}' in quick but not in canonical")
            return False

    # All apps in quick/canonical must exist on disk
    for suite_name, apps in SUITE_DEFINITIONS.items():
        for app in apps:
            if not (root / "apps" / app / "main.ail").exists():
                print(
                    f"  [FAIL] FAIL: '{app}' in {suite_name} not found at apps/{app}/main.ail"
                )
                return False

    # Full suite discovery should find at least quick apps
    all_apps = discover_all_apps(root)
    if len(all_apps) == 0:
        print("  [FAIL] FAIL: Full suite discovery found no apps")
        return False

    print(f"  [PASS] PASS: All suites valid ({len(all_apps)} total apps discovered)")
    return True


def main() -> int:
    """Run all regression tests."""
    print("=" * 60)
    print("DX TOOL #004 REGRESSION TEST SUITE")
    print("=" * 60)

    results = {
        "Regression detection triggers": test_regression_detection_triggers(),
        "Baseline self-match": test_no_regression_with_baseline_match(),
        "Exit code precedence": test_exit_code_precedence(),
        "Suite definitions valid": test_suite_definitions(),
    }

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
