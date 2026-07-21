# DX Tool #005 Regression Testing
# Tests for idempotency, determinism, and safety guarantees

from __future__ import annotations

import hashlib
import shutil
import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def hash_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def clean_and_regenerate():
    """Clean and regenerate all tests."""
    root = Path(__file__).resolve().parent.parent
    gen_dir = root / "tests" / "generated"
    if gen_dir.exists():
        shutil.rmtree(str(gen_dir))
    run_command([sys.executable, "-m", "tools.ail_testgen", "--force", "--quiet"])


def test_deterministic_generation() -> bool:
    """Test: generating twice produces identical output."""
    print("TEST 1: Deterministic generation...")
    root = Path(__file__).resolve().parent.parent
    gen_dir = root / "tests" / "generated"

    # First generation
    clean_and_regenerate()
    hashes1 = {}
    for f in sorted(gen_dir.glob("*.py")):
        hashes1[f.name] = hash_file(f)

    # Second generation
    clean_and_regenerate()
    hashes2 = {}
    for f in sorted(gen_dir.glob("*.py")):
        hashes2[f.name] = hash_file(f)

    if hashes1 == hashes2:
        print("  [PASS] All %d files have identical hashes" % len(hashes1))
        return True
    else:
        for name in hashes1:
            if hashes1.get(name) != hashes2.get(name):
                print("  [FAIL] Mismatch: %s" % name)
        return False


def test_no_handwritten_tests_touched() -> bool:
    """Test: handwritten test hash is unchanged by generation."""
    print("\nTEST 2: Handwritten tests untouched...")
    root = Path(__file__).resolve().parent.parent
    # Hash a known handwritten test before regeneration
    test_file = root / "tests" / "test_runtime.py"
    original_hash = hash_file(test_file)

    # Regenerate
    run_command([sys.executable, "-m", "tools.ail_testgen", "--force", "--quiet"])

    # Verify hash unchanged
    new_hash = hash_file(test_file)
    if original_hash == new_hash:
        print("  [PASS] test_runtime.py unchanged")
        return True
    else:
        print("  [FAIL] test_runtime.py was modified!")
        return False


def test_force_overwrites_existing() -> bool:
    """Test: --force overwrites existing generated files."""
    print("\nTEST 3: --force overwrites existing...")
    root = Path(__file__).resolve().parent.parent
    gen_dir = root / "tests" / "generated"

    # Generate with force
    clean_and_regenerate()
    first_files = sorted(gen_dir.glob("*.py"))
    first_count = len(first_files)
    first_hash = hash_file(first_files[0]) if first_files else ""

    # Generate again with force
    run_command([sys.executable, "-m", "tools.ail_testgen", "--force", "--quiet"])
    second_files = sorted(gen_dir.glob("*.py"))
    second_count = len(second_files)
    second_hash = hash_file(second_files[0]) if second_files else ""

    if second_count == first_count and second_hash == first_hash:
        print("  [PASS] --force regenerated %d files identically" % second_count)
        return True
    else:
        print("  [FAIL] File count or hash changed")
        print("  Count: %d -> %d" % (first_count, second_count))
        return False


def test_app_filter() -> bool:
    """Test: --app filter generates only the specified app."""
    print("\nTEST 4: --app filter...")
    root = Path(__file__).resolve().parent.parent
    gen_dir = root / "tests" / "generated"

    # Clean and generate only dice_roller app
    gen_dir.mkdir(parents=True, exist_ok=True)
    for f in gen_dir.glob("*"):
        if f.is_file():
            f.unlink()
    run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_testgen",
            "--app",
            "dice_roller",
            "--force",
            "--quiet",
        ]
    )

    py_files = list(gen_dir.glob("*.py"))
    app_files = [f for f in py_files if "dice_roller" in f.name]
    other_files = [
        f for f in py_files if "dice_roller" not in f.name and f.name != "__init__.py"
    ]

    if len(app_files) > 0 and len(other_files) == 0:
        print("  [PASS] Only dice_roller tests generated")
        return True
    else:
        print("  [FAIL] Unexpected files found")
        for f in other_files:
            print("    %s" % f.name)
        return False


def run_all_tests() -> bool:
    tests = [
        test_deterministic_generation,
        test_no_handwritten_tests_touched,
        test_force_overwrites_existing,
        test_app_filter,
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
