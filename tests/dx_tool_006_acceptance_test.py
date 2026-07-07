# DX Tool #006 Acceptance Testing
# Comprehensive test suite for ail package manager tool

import os
import sys
import subprocess
import tempfile
import shutil
import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent


def run_command(cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
    """Run a command and return exit code, stdout, stderr."""
    env = os.environ.copy()
    env["PYTHONPATH"] = str(PROJECT_ROOT)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env=env)
    return result.returncode, result.stdout, result.stderr


def create_temp_project(tmp_dir: Path, name: str = "test-pkg", version: str = "0.1.0") -> Path:
    """Create a temporary project directory."""
    proj_dir = tmp_dir / name
    return proj_dir


def create_ail_toml(path: Path, name: str, version: str = "0.1.0", deps: dict | None = None) -> None:
    """Create an ail.toml file."""
    lines = [
        '[project]',
        f'name = "{name}"',
        f'version = "{version}"',
        'description = "Test package"',
        'entry = "main.ail"',
        '',
        '[language]',
        'version = "0.3"',
        '',
    ]
    if deps:
        lines.append('[dependencies]')
        for dep_name, dep_value in deps.items():
            if isinstance(dep_value, str):
                lines.append(f'{dep_name} = "{dep_value}"')
            elif isinstance(dep_value, dict):
                items = ", ".join(f'{k} = "{v}"' for k, v in dep_value.items())
                lines.append(f'{dep_name} = {{ {items} }}')
    text = "\n".join(lines) + "\n"
    # Replace Windows backslashes with forward slashes for TOML compatibility
    text = text.replace("\\", "/")
    path.write_text(text, encoding="utf-8")


def test_init_creates_project() -> bool:
    """Test: ail init creates ail.toml, main.ail, and ail.lock."""
    print("TEST 1: ail init creates project structure...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        proj_dir = tmp_path / "my-project"
        code, out, err = run_command([
            sys.executable, "-m", "tools.ail_package_manager", "init",
            str(proj_dir), "--name", "my-project", "--version", "0.1.0",
            "--description", "Test project", "-y",
        ], cwd=tmp_path)

        if code != 0:
            print(f"  X FAIL: Exit code {code}, stderr: {err}")
            return False

        if not (proj_dir / "ail.toml").exists():
            print(f"  X FAIL: ail.toml not created")
            return False
        if not (proj_dir / "main.ail").exists():
            print(f"  X FAIL: main.ail not created")
            return False
        if not (proj_dir / "ail.lock").exists():
            print(f"  X FAIL: ail.lock not created")
            return False

        # Verify ail.toml content
        toml_content = (proj_dir / "ail.toml").read_text(encoding="utf-8")
        if 'name = "my-project"' not in toml_content:
            print(f"  X FAIL: Project name not in ail.toml")
            return False
        if 'version = "0.1.0"' not in toml_content:
            print(f"  X FAIL: Version not in ail.toml")
            return False

        print("  V PASS: ail init creates correct project structure")
        return True


def test_init_refuses_nonempty_dir() -> bool:
    """Test: ail init refuses to initialize in a non-empty directory."""
    print("TEST 2: ail init refuses non-empty directory...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        # Create a file in the directory
        (tmp_path / "existing.txt").write_text("hello", encoding="utf-8")

        code, out, err = run_command([
            sys.executable, "-m", "tools.ail_package_manager", "init",
            str(tmp_path), "--name", "test", "-y",
        ], cwd=tmp_path)

        if code != 3:
            print(f"  X FAIL: Expected exit code 3, got {code}")
            return False
        if "not empty" not in err and "not empty" not in out:
            print(f"  X FAIL: Expected 'not empty' error")
            print(f"  stdout: {out}")
            print(f"  stderr: {err}")
            return False

        print("  V PASS: ail init correctly refuses non-empty directory")
        return True


def _run_python_code(code: str, tmp_path: Path) -> tuple[int, str, str]:
    """Run a Python snippet as a file (avoids -c quoting issues with try/except)."""
    script_path = tmp_path / "_test_script.py"
    script_path.write_text(code, encoding="utf-8")
    return run_command([sys.executable, str(script_path)], cwd=tmp_path)


def test_parse_valid_manifest() -> bool:
    """Test: parsing a valid ail.toml succeeds."""
    print("TEST 3: Parse valid manifest...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        toml_path = tmp_path / "ail.toml"
        create_ail_toml(toml_path, "valid-pkg", "2.0.0")

        code = f"""
from pathlib import Path
from tools.ail_package_manager.manifest import parse_manifest
m = parse_manifest(Path(r'{toml_path}'))
assert m.name == 'valid-pkg', f'Expected valid-pkg, got {{m.name}}'
assert m.version == '2.0.0', f'Expected 2.0.0, got {{m.version}}'
print('OK')
"""
        _code, out, err = _run_python_code(code, tmp_path)

        if _code != 0 or "OK" not in out:
            print(f"  X FAIL: Parse failed. stdout: {code_out}, stderr: {err}")
            return False

        print("  V PASS: Valid manifest parses correctly")
        return True


def test_parse_invalid_manifest() -> bool:
    """Test: parsing an invalid ail.toml raises ValueError."""
    print("TEST 4: Parse invalid manifest...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        toml_path = tmp_path / "ail.toml"
        toml_path.write_text("[project]\nname = '_INVALID_'\n", encoding="utf-8")

        code = f"""
from pathlib import Path
from tools.ail_package_manager.manifest import parse_manifest
try:
    m = parse_manifest(Path(r'{toml_path}'))
    print('No error')
except ValueError as e:
    print('OK', str(e))
"""
        _code, out, err = _run_python_code(code, tmp_path)

        if "OK" not in out:
            print(f"  X FAIL: Expected ValueError for invalid manifest")
            print(f"  stdout: {code_out}")
            return False

        print("  V PASS: Invalid manifest correctly raises error")
        return True


def test_validate_package_name() -> bool:
    """Test: package name validation rejects invalid names."""
    print("TEST 5: Package name validation...")
    import sys as _sys
    _sys.path.insert(0, str(PROJECT_ROOT))
    from tools.ail_package_manager.manifest import validate_package_name

    tests = [
        ("valid-name", None),
        ("my-pkg-123", None),
        ("a", None),
        ("-invalid", "Invalid"),
        ("invalid-", "Invalid"),
        ("UPPERCASE", "Invalid"),
        ("has_underscore", "Invalid"),
        ("a" * 65, "too long"),
    ]

    for name, expected in tests:
        result = validate_package_name(name)
        if expected is None:
            if result is not None:
                print(f"  X FAIL: '{name}' should be valid, got: {result}")
                return False
        else:
            if result is None:
                print(f"  X FAIL: '{name}' should be invalid")
                return False
            if expected not in result:
                print(f"  X FAIL: '{name}' error missing '{expected}': {result}")
                return False

    print("  V PASS: Package name validation correct")
    return True


def test_dependency_parsing() -> bool:
    """Test: dependency parsing for all three source types."""
    print("TEST 6: Dependency parsing...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        toml_path = tmp_path / "ail.toml"
        create_ail_toml(toml_path, "test-pkg", "0.1.0", deps={
            "str-utils": ">=1.0.0",
            "local-lib": {"path": "../local-lib"},
            "git-lib": {"git": "https://github.com/user/repo.git", "tag": "v1.0"},
        })

        code, out, err = run_command([
            sys.executable, "-c",
            f"from pathlib import Path; from tools.ail_package_manager.manifest import parse_manifest; "
            f"m = parse_manifest(Path(r'{toml_path}')); "
            f"assert len(m.dependencies) == 3, f'Expected 3 deps, got {{len(m.dependencies)}}'; "
            f"d = m.dependencies['str-utils']; "
            f"assert d.version_req == '>=1.0.0', f'Expected >=1.0.0, got {{d.version_req}}'; "
            f"d2 = m.dependencies['local-lib']; "
            f"assert d2.path == '../local-lib', f'Expected ../local-lib, got {{d2.path}}'; "
            f"d3 = m.dependencies['git-lib']; "
            f"assert d3.git == 'https://github.com/user/repo.git', f'Git mismatch'; "
            f"print('OK')"
        ], cwd=tmp_path)

        if code != 0 or "OK" not in out:
            print(f"  X FAIL: Dep parsing failed. stdout: {out}, stderr: {err}")
            return False

        print("  V PASS: All dependency types parse correctly")
        return True


def test_install_local_dep() -> bool:
    """Test: installing a local path dependency."""
    print("TEST 7: Install local dependency...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Create a dependency package
        dep_dir = tmp_path / "dep-pkg"
        dep_dir.mkdir()
        create_ail_toml(dep_dir / "ail.toml", "dep-pkg", "1.0.0")
        (dep_dir / "lib.ail").write_text("let greet = fn() => {}\n", encoding="utf-8")

        # Create the main project
        proj_dir = tmp_path / "main-proj"
        proj_dir.mkdir()
        create_ail_toml(proj_dir / "ail.toml", "main-proj", "0.1.0", deps={
            "dep-pkg": {"path": dep_dir.as_posix()},
        })
        (proj_dir / "main.ail").write_text("let main = fn() => {}\n", encoding="utf-8")

        code, out, err = run_command([
            sys.executable, "-m", "tools.ail_package_manager", "install",
        ], cwd=proj_dir)

        if code != 0:
            print(f"  X FAIL: Install returned exit code {code}")
            print(f"  stdout: {out}")
            print(f"  stderr: {err}")
            return False

        # Verify the dependency was installed
        lib_dep = proj_dir / "lib" / "dep-pkg"
        if not lib_dep.exists():
            print(f"  X FAIL: lib/dep-pkg not created")
            return False
        if not (lib_dep / "ail.toml").exists():
            print(f"  X FAIL: lib/dep-pkg/ail.toml missing")
            return False
        if not (proj_dir / "ail.lock").exists():
            print(f"  X FAIL: ail.lock not created")
            return False

        print("  V PASS: Local dependency installed correctly")
        return True


def test_lock_file_content() -> bool:
    """Test: lock file contains expected schema."""
    print("TEST 8: Lock file content...")
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        dep_dir = tmp_path / "dep-pkg"
        dep_dir.mkdir()
        create_ail_toml(dep_dir / "ail.toml", "dep-pkg", "1.0.0")
        (dep_dir / "lib.ail").write_text("let x = 1\n", encoding="utf-8")

        proj_dir = tmp_path / "main-proj"
        proj_dir.mkdir()
        create_ail_toml(proj_dir / "ail.toml", "main-proj", "0.1.0", deps={
            "dep-pkg": {"path": dep_dir.as_posix()},
        })
        (proj_dir / "main.ail").write_text("let main = fn() => {}\n", encoding="utf-8")

        code, _, err = run_command([
            sys.executable, "-m", "tools.ail_package_manager", "install",
        ], cwd=proj_dir)

        if code != 0:
            print(f"  X FAIL: Install failed (exit {code}): {err}")
            return False

        lock = (proj_dir / "ail.lock").read_text(encoding="utf-8")
        checks = [
            "version = 1" in lock,
            "input_hash" in lock,
            "[[packages]]" in lock,
            'name = "dep-pkg"' in lock,
            'version = "1.0.0"' in lock,
            'source = "local"' in lock,
        ]

        if not all(checks):
            print(f"  X FAIL: Lock file missing expected fields")
            print(f"  Lock content:\n{lock}")
            return False

        print("  V PASS: Lock file has correct schema")
        return True


def run_all_tests() -> bool:
    tests = [
        test_validate_package_name,
        test_init_creates_project,
        test_init_refuses_nonempty_dir,
        test_parse_valid_manifest,
        test_parse_invalid_manifest,
        test_dependency_parsing,
        test_install_local_dep,
        test_lock_file_content,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"  X EXCEPTION: {e}")
            failed += 1
        print()

    print(f"\n{'='*50}")
    print(f"Results: {passed} passed, {failed} failed, {len(tests)} total")
    print(f"{'='*50}")

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    raise SystemExit(0 if success else 1)
