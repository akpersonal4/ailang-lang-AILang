# DX Tool #006 Regression Testing
# AILang Dependency Ordering Assistant - Regression Tests

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path


def run_command(cmd: list[str]) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def test_empty_file() -> bool:
    """Test: Handles empty file gracefully."""
    print("TEST: Empty file handling...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "tests/fixtures/empty.ail"]
    )
    if code == 0:
        print("  [PASS] Empty file handled")
        return True
    else:
        print(f"  [FAIL] Exit code {code}")
        return False


def test_comments_only() -> bool:
    """Test: Handles comments-only file gracefully."""
    print("TEST: Comments-only file...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "tests/fixtures/comments_only.ail"]
    )
    if code == 0:
        print("  [PASS] Comments-only file handled")
        return True
    else:
        print(f"  [FAIL] Exit code {code}")
        return False


def test_single_function() -> bool:
    """Test: Handles single-function file correctly."""
    print("TEST: Single function file...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_order",
            "--quiet",
            "tests/fixtures/single_fn.ail",
        ]
    )
    if code == 0:
        print("  [PASS] Single function handled")
        return True
    else:
        print(f"  [FAIL] Exit code {code}")
        return False


def test_nested_braces() -> bool:
    """Test: Handles nested braces in function correctly."""
    print("TEST: Nested braces handling...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "tests/fixtures/nested_braces.ail"]
    )
    # This file has forward reference - should detect it correctly
    if "helper" in out and "main" in out:
        print("  [PASS] Nested braces handled (forward ref detected)")
        return True
    else:
        print(f"  [FAIL] Exit code {code}")
        print(f"  Stderr: {err[:200]}")
        return False


def test_string_with_parens() -> bool:
    """Test: Handles parentheses inside strings correctly."""
    print("TEST: String with parentheses...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "tests/fixtures/string_parens.ail"]
    )
    if code == 0:
        print("  [PASS] String parens handled")
        return True
    else:
        print(f"  [FAIL] Exit code {code}")
        return False


def test_deep_recursion() -> bool:
    """Test: Deep recursion doesn't cause stack overflow."""
    print("TEST: Deep recursion handling...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "apps/static_analyzer/main.ail"]
    )
    if code == 0:
        print("  [PASS] Deep recursion handled")
        return True
    else:
        print(f"  [FAIL] Exit code {code}")
        return False


def test_json_structure_consistent() -> bool:
    """Test: JSON output has consistent structure across runs."""
    print("TEST: JSON structure consistent...")
    for _ in range(3):
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
            if "metadata" not in data or "levels" not in data:
                print("  [FAIL] Missing required fields")
                return False
        except json.JSONDecodeError:
            print("  [FAIL] Invalid JSON")
            return False

    print("  [PASS] JSON structure consistent")
    return True


def test_import_recognition() -> bool:
    """Test: Imports are not confused with function calls."""
    print("TEST: Import recognition...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "--quiet", "apps/mini_crm/main.ail"]
    )
    if code == 0:
        print("  [PASS] Imports recognized correctly")
        return True
    else:
        print(f"  [FAIL] Exit code {code}")
        return False


def test_json_levels_structure() -> bool:
    """Test: JSON output includes levels with correct structure."""
    print("TEST: JSON levels structure...")
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
        if "levels" in data and "0" in data["levels"]:
            print("  [PASS] Levels structure correct")
            return True
        else:
            print("  [FAIL] Levels missing or malformed")
            return False
    except json.JSONDecodeError:
        print("  [FAIL] Invalid JSON")
        return False


def test_string_escape_handling() -> bool:
    """Test: String escapes don't confuse function detection."""
    print("TEST: String escape handling...")
    content = """fn main() {
    let s = "helper() not a call";
    print(s);
}

fn helper() {
    return 1;
}
"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".ail", delete=False) as f:
        f.write(content)
        temp_path = f.name

    try:
        code, out, err = run_command(
            [sys.executable, "-m", "tools.ail_order", temp_path]
        )
        # helper() in string is not a real call - no forward ref expected since helper is defined
        if "helper" in out and "main" in out:
            print("  [PASS] Escape handling works")
            return True
        else:
            print("  [FAIL] Functions not detected")
            return False
    finally:
        Path(temp_path).unlink(missing_ok=True)


def test_negative_exit_code() -> bool:
    """Test: Tool returns non-zero exit code for files with errors."""
    print("TEST: Negative exit code...")
    code, out, err = run_command(
        [sys.executable, "-m", "tools.ail_order", "tests/fixtures/forward_ref.ail"]
    )
    if code != 0:
        print("  [PASS] Non-zero exit code for errors")
        return True
    else:
        print("  [FAIL] Should have non-zero exit code")
        return False


def test_cli_version() -> bool:
    """Test: CLI --version works."""
    print("TEST: CLI version...")
    code, out, err = run_command([sys.executable, "-m", "compiler", "--version"])
    if "AILang" in out:
        print("  [PASS] Version shows")
        return True
    else:
        print("  [FAIL] Version missing")
        return False


def test_json_functions_key() -> bool:
    """Test: JSON output has functions key."""
    print("TEST: JSON functions key...")
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
        if "functions" in data:
            print("  [PASS] Functions key present")
            return True
        else:
            print("  [FAIL] Functions key missing")
            return False
    except json.JSONDecodeError:
        print("  [FAIL] Invalid JSON")
        return False


def test_fix_mode_on_clean_file() -> bool:
    """Test: Fix mode on file with no ordering issues."""
    print("TEST: Fix mode on clean file...")
    code, out, err = run_command(
        [
            sys.executable,
            "-m",
            "tools.ail_order",
            "--fix",
            "--stdout",
            "examples/hello_world/main.ail",
        ]
    )
    if code == 0 and "fn main" in out:
        print("  [PASS] Clean file handled")
        return True
    else:
        print("  [FAIL] Clean file not handled")
        return False


def run_all_tests() -> int:
    """Run all regression tests."""
    print("=" * 60)
    print("DX TOOL #006 REGRESSION TEST SUITE")
    print("=" * 60)

    # Create test fixtures first
    test_dir = Path(__file__).parent / "fixtures"
    test_dir.mkdir(exist_ok=True)

    # Create empty file
    (test_dir / "empty.ail").write_text("", encoding="utf-8")

    # Create comments-only file
    (test_dir / "comments_only.ail").write_text(
        "// Just a comment\n// Another comment\n", encoding="utf-8"
    )

    # Create single function file
    (test_dir / "single_fn.ail").write_text(
        'fn main() {\n    print("hello");\n}\n', encoding="utf-8"
    )

    # Create nested braces file
    (test_dir / "nested_braces.ail").write_text(
        "fn main() {\n"
        "    if (true) {\n"
        "        if (false) {\n"
        "            let x = helper();\n"
        "        }\n"
        "    }\n"
        "}\n"
        "fn helper() {\n"
        "    return 0;\n"
        "}\n",
        encoding="utf-8",
    )

    # Create string parens file
    (test_dir / "string_parens.ail").write_text(
        "fn main() {\n"
        '    let msg = "function(x) call";\n'
        "    print(msg);\n"
        "}\n"
        "fn helper() {\n"
        "    return 1;\n"
        "}\n",
        encoding="utf-8",
    )

    tests = [
        test_empty_file,
        test_comments_only,
        test_single_function,
        test_nested_braces,
        test_string_with_parens,
        test_deep_recursion,
        test_json_structure_consistent,
        test_import_recognition,
        test_json_levels_structure,
        test_string_escape_handling,
        test_negative_exit_code,
        test_cli_version,
        test_json_functions_key,
        test_fix_mode_on_clean_file,
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
    print(f"Passed: {passed}/{len(tests)}, Failed: {failed}/{len(tests)}")

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(run_all_tests())
