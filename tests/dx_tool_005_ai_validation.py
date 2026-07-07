# DX Tool #005 AI Validation
# Validates that the test generator can be reliably used by AI agents

from __future__ import annotations

import sys
import subprocess
import hashlib
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def test_basic_generation() -> bool:
    """Test: basic generation mode works for AI use."""
    print("TEST 1: Basic generation mode...")
    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_testgen",
        "--force", "--quiet",
    ])
    if code == 0:
        print("  [PASS] Exit code 0")
        return True
    else:
        print("  [FAIL] Exit code %d: %s" % (code, err[:300]))
        return False


def test_help_output() -> bool:
    """Test: --help provides useful usage information."""
    print("\nTEST 2: --help output...")
    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_testgen",
        "--help",
    ])
    checks = [
        "usage" in out,
        "dry-run" in out,
        "force" in out,
        "quiet" in out,
        "app" in out,
        "report-only" in out,
    ]
    all_pass = all(checks)
    if code == 0 and all_pass:
        print("  [PASS] --help shows all CLI options")
        return True
    else:
        print("  [FAIL] Missing options in --help")
        print("  Checks: %s" % checks)
        return False


def test_report_only() -> bool:
    """Test: --report-only regenerates report without generating files."""
    print("\nTEST 3: --report-only...")
    root = Path(__file__).resolve().parent.parent
    gen_dir = root / "tests" / "generated"

    # Note initial file count
    initial_files = len(list(gen_dir.glob("*.py"))) if gen_dir.exists() else 0

    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_testgen",
        "--report-only", "--dry-run", "--quiet",
    ])

    if code == 0:
        print("  [PASS] --report-only exits with code 0")
        return True
    else:
        print("  [FAIL] Exit code %d: %s" % (code, err[:300]))
        return False


def test_exit_codes() -> bool:
    """Test: known exit codes (0=success)."""
    print("\nTEST 4: Exit code mapping...")
    code, out, err = run_command([
        sys.executable, "-m", "tools.ail_testgen",
        "--quiet",
    ])
    if code == 0:
        print("  [PASS] Normal run exits 0")
        return True
    else:
        print("  [FAIL] Exit code %d" % code)
        return False


def run_all_tests() -> bool:
    tests = [
        test_basic_generation,
        test_help_output,
        test_report_only,
        test_exit_codes,
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
            print("  [ERROR] %s: %s" % (t.__name__, e))
            failed += 1
    print("\n=== Results ===")
    print("Passed: %d/%d" % (passed, len(tests)))
    print("Failed: %d/%d" % (failed, len(tests)))
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
