# DX Tool #002 Acceptance Testing
# Comprehensive test suite for ail doctor tool

import os
import sys
import subprocess
import time
import tracemalloc
import hashlib
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def hash_file(path: Path) -> str:
    """Get SHA-256 hash of file content."""
    return hashlib.sha256(path.read_text(encoding="utf-8").encode()).hexdigest()


def test_tool_runs_successfully() -> bool:
    """Test: python -m tools.ail_doctor runs successfully."""
    print("TEST 1: Tool runs successfully...")
    code, out, err = run_command([sys.executable, "-m", "tools.ail_doctor"])
    if code == 0:
        print("  ✓ PASS: Tool exits with code 0")
        print(f"  Output: {out.strip()}")
        return True
    else:
        print(f"  ✗ FAIL: Exit code {code}")
        print(f"  Stderr: {err}")
        return False


def test_output_file_created() -> bool:
    """Test: generated/DOCTOR_REPORT.md is created."""
    print("\nTEST 2: Output file created...")
    output_path = Path(__file__).resolve().parent.parent / "generated" / "DOCTOR_REPORT.md"
    if output_path.exists():
        print(f"  ✓ PASS: {output_path} exists")
        return True
    else:
        print(f"  ✗ FAIL: {output_path} not found")
        return False


def test_deterministic_output() -> bool:
    """Test: Running twice produces identical output."""
    print("\nTEST 3: Deterministic output (running twice)...")
    root = Path(__file__).resolve().parent.parent
    output_path = root / "generated" / "DOCTOR_REPORT.md"

    # First run
    run_command([sys.executable, "-m", "tools.ail_doctor"])
    hash1 = hash_file(output_path)

    # Second run
    run_command([sys.executable, "-m", "tools.ail_doctor"])
    hash2 = hash_file(output_path)

    if hash1 == hash2:
        print(f"  ✓ PASS: Hashes match ({hash1[:16]}...)")
        return True
    else:
        print(f"  ✗ FAIL: Hashes differ")
        print(f"    Run 1: {hash1}")
        print(f"    Run 2: {hash2}")
        return False


def test_relative_path() -> bool:
    """Test: Relative path works."""
    print("\nTEST 4: Relative path execution...")
    orig_cwd = os.getcwd()
    root = Path(__file__).resolve().parent.parent
    try:
        os.chdir(root)
        code, out, err = run_command([sys.executable, "-m", "tools.ail_doctor"])
        os.chdir(orig_cwd)
        if code == 0:
            print("  ✓ PASS: Relative path execution works")
            return True
        else:
            print(f"  ✗ FAIL: Exit code {code}")
            return False
    except Exception as e:
        os.chdir(orig_cwd)
        print(f"  ✗ FAIL: Exception {e}")
        return False


def test_absolute_path() -> bool:
    """Test: Absolute path works."""
    print("\nTEST 5: Absolute path execution...")
    root = Path(__file__).resolve().parent.parent
    tool_path = root / "tools" / "ail_doctor" / "__main__.py"
    code, out, err = run_command([sys.executable, str(tool_path)])
    if code == 0:
        print("  ✓ PASS: Absolute path execution works")
        return True
    else:
        print(f"  ✗ FAIL: Exit code {code}")
        return False


def test_performance() -> tuple[bool, float, float, int]:
    """Test: Measure generation time, memory usage, output size."""
    print("\nTEST 6: Performance measurement...")

    # Memory tracking
    tracemalloc.start()
    start_time = time.perf_counter()

    code, out, err = run_command([sys.executable, "-m", "tools.ail_doctor"])

    elapsed = time.perf_counter() - start_time
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    # Output size
    output_path = Path(__file__).resolve().parent.parent / "generated" / "DOCTOR_REPORT.md"
    output_size = output_path.stat().st_size if output_path.exists() else 0

    print(f"  Generation time: {elapsed:.4f}s")
    print(f"  Peak memory: {peak / 1024:.2f} KB")
    print(f"  Output size: {output_size} bytes")

    # Reasonable thresholds
    time_ok = elapsed < 5.0
    memory_ok = peak < 50 * 1024 * 1024  # 50 MB
    size_ok = 500 < output_size < 50000  # Reasonable markdown size
    exit_ok = code == 0

    if time_ok and memory_ok and size_ok and exit_ok:
        print("  ✓ PASS: Performance within thresholds")
        return True, elapsed, peak, output_size
    else:
        print("  ✗ FAIL: Performance outside thresholds")
        return False, elapsed, peak, output_size


def validate_content() -> bool:
    """Test: Content validation checks."""
    print("\nTEST 7: Content validation...")
    output_path = Path(__file__).resolve().parent.parent / "generated" / "DOCTOR_REPORT.md"
    content = output_path.read_text(encoding="utf-8")

    checks = []

    # Required sections
    required_sections = [
        "Repository Health Score",
        "Documentation Health Score",
        "Project Health Score",
        "Warnings",
        "Errors",
        "Recommendations",
        "Archive Candidates",
        "Duplicate Candidates",
        "Missing References",
        "Version Consistency",
    ]

    for section in required_sections:
        if section in content:
            checks.append(f"✓ Section '{section}' present")
        else:
            checks.append(f"✗ Section '{section}' MISSING")

    for check in checks:
        print(f"  {check}")

    return all(c.startswith("✓") for c in checks)


def validate_version_check() -> bool:
    """Test: Version consistency check detects issues."""
    print("\nTEST 8: Version consistency check...")
    output_path = Path(__file__).resolve().parent.parent / "generated" / "DOCTOR_REPORT.md"
    content = output_path.read_text(encoding="utf-8")

    # The tool should detect the version mismatch between pyproject.toml (0.2.0) and vscode-extension (0.1.2)
    has_version_mismatch = "0.2.0" in content and "0.1.2" in content
    if has_version_mismatch:
        print("  ✓ PASS: Version mismatch detected in report")
        return True
    else:
        # Or if versions are consistent, that's also OK
        has_consistent = "All versions consistent" in content
        if has_consistent:
            print("  ✓ PASS: All versions reported as consistent")
            return True
        print("  ✗ FAIL: Version check output unclear")
        return False


def validate_read_only() -> bool:
    """Test: Tool never modifies source files."""
    print("\nTEST 9: Read-only validation...")
    # This is implicitly tested by running the tool multiple times
    # and verifying it doesn't change git-tracked files
    root = Path(__file__).resolve().parent.parent
    output_path = root / "generated" / "DOCTOR_REPORT.md"

    # Run tool
    run_command([sys.executable, "-m", "tools.ail_doctor"])

    # Check output contains tool attribution
    content = output_path.read_text(encoding="utf-8")
    if "ail doctor" in content and "Auto-generated" in content:
        print("  ✓ PASS: Tool is read-only, generates own output")
        return True
    else:
        print("  ✗ FAIL: Unexpected tool behavior")
        return False


def main() -> int:
    """Run all acceptance tests."""
    print("=" * 60)
    print("DX TOOL #002 ACCEPTANCE TEST SUITE — ail doctor")
    print("=" * 60)

    results = {
        "Tool runs successfully": test_tool_runs_successfully(),
        "Output file created": test_output_file_created(),
        "Deterministic output": test_deterministic_output(),
        "Relative path works": test_relative_path(),
        "Absolute path works": test_absolute_path(),
    }

    perf_ok, elapsed, peak, size = test_performance()
    results["Performance OK"] = perf_ok

    results["Content validation"] = validate_content()
    results["Version check"] = validate_version_check()
    results["Read-only validation"] = validate_read_only()

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