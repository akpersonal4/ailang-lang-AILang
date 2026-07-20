# Test Suite — Static Analyzer Enhancement

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(
        cmd, capture_output=True, text=True, cwd=Path(__file__).resolve().parent.parent
    )
    return result.returncode, result.stdout, result.stderr


def test_analyzer_builds() -> bool:
    """Test: The static analyzer builds successfully."""
    print("TEST 1: Analyzer builds...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "compiler",
            "apps/static_analyzer/main.ail",
            "examples/hello_world/main.ail",
        ]
    )
    if code == 0:
        print("  ✓ PASS: Analyzer builds successfully")
        return True
    else:
        print(f"  ✗ FAIL: Build failed with code {code}")
        print(f"  Stderr: {err[:500]}")
        return False


def test_analyzer_runs() -> bool:
    """Test: The static analyzer runs on itself."""
    print("\nTEST 2: Analyzer runs on its own source...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "compiler",
            "apps/static_analyzer/main.ail",
            "apps/static_analyzer/main.ail",
        ]
    )
    if code == 0 and "Function Analysis" in out:
        print("  ✓ PASS: Analyzer produces expected output")
        return True
    else:
        print("  ✗ FAIL: Unexpected output")
        return False


def test_unreachable_detection() -> bool:
    """Test: Unreachable functions are detected in output."""
    print("\nTEST 3: Unreachable function detection...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "compiler",
            "apps/static_analyzer/main.ail",
            "apps/static_analyzer/main.ail",
        ]
    )
    if "Reachability Analysis" in out:
        print("  ✓ PASS: Reachability section present in output")
        return True
    else:
        print("  ✗ FAIL: Reachability section missing")
        return False


def test_documentation_detection() -> bool:
    """Test: Documentation analysis is present in output."""
    print("\nTEST 4: Documentation detection...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "compiler",
            "apps/static_analyzer/main.ail",
            "apps/static_analyzer/main.ail",
        ]
    )
    if "Documentation Analysis" in out:
        print("  ✓ PASS: Documentation section present in output")
        return True
    else:
        print("  ✗ FAIL: Documentation section missing")
        return False


def test_existing_functionality_preserved() -> bool:
    """Test: Existing analyzer functionality still works."""
    print("\nTEST 5: Existing functionality preserved...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "compiler",
            "apps/static_analyzer/main.ail",
            "apps/static_analyzer/main.ail",
        ]
    )
    required_sections = [
        "Source Statistics",
        "Function Analysis",
        "Variable Analysis",
        "Call Analysis",
        "Module Analysis",
        "Complexity Report",
        "Dependency Tree",
    ]
    missing = [s for s in required_sections if s not in out]
    if not missing:
        print("  ✓ PASS: All existing sections present")
        return True
    else:
        print(f"  ✗ FAIL: Missing sections: {missing}")
        return False


def test_complexity_metrics() -> bool:
    """Test: Complexity metrics are computed."""
    print("\nTEST 6: Complexity metrics...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "compiler",
            "apps/static_analyzer/main.ail",
            "apps/static_analyzer/main.ail",
        ]
    )
    if "Max call depth:" in out:
        print("  ✓ PASS: Complexity metrics present")
        return True
    else:
        print("  ✗ FAIL: Complexity metrics missing")
        return False


def main() -> int:
    """Run all tests."""
    print("=" * 60)
    print("Static Analyzer Enhancement Tests")
    print("=" * 60)

    results = {
        "Analyzer builds": test_analyzer_builds(),
        "Analyzer runs": test_analyzer_runs(),
        "Unreachable detection": test_unreachable_detection(),
        "Documentation detection": test_documentation_detection(),
        "Existing functionality preserved": test_existing_functionality_preserved(),
        "Complexity metrics": test_complexity_metrics(),
    }

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
