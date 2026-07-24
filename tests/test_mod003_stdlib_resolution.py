"""Regression test for MOD003: stdlib module resolution from outside project tree.

This test ensures that AILang programs importing stdlib modules can be
compiled and run from any directory, not just from within the project tree.
This permanently protects against the MOD003 issue fixed in v1.1.4.
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


@pytest.mark.slow
class TestMOD003StdlibResolution:
    """Regression tests for MOD003: stdlib module resolution from outside project tree."""

    def test_stdlib_import_from_temp_directory(self) -> None:
        """Verify stdlib modules resolve when running from a temp directory."""
        ail_program = """\
import string;
import math;

fn main() {
    let msg = string.uppercase("hello");
    print(msg);
    let result = math.add(2, 3);
    print(result);
    return 0
}
"""
        with tempfile.TemporaryDirectory(prefix="ailang_mod003_") as tmp:
            tmp_path = Path(tmp)
            program_file = tmp_path / "mod003_test.ail"
            program_file.write_text(ail_program, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "compiler", "run", str(program_file)],
                capture_output=True,
                text=True,
                cwd=tmp,
                timeout=30,
            )

            assert result.returncode == 0, (
                f"MOD003 regression: stdlib import failed from temp directory.\n"
                f"returncode: {result.returncode}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
            assert "HELLO" in result.stdout, f"Expected HELLO in output, got: {result.stdout}"
            assert "5" in result.stdout, f"Expected 5 in output, got: {result.stdout}"

    def test_stdlib_import_list_map_from_temp_directory(self) -> None:
        """Verify list and map stdlib modules resolve from a temp directory."""
        ail_program = """\
import list;
import map;

fn main() {
    let items = list.new();
    list.append(items, "world");
    let greeting = string.concat("Hello, ", list.get(items, 0));
    print(greeting);
    return 0
}
"""
        with tempfile.TemporaryDirectory(prefix="ailang_mod003_list_") as tmp:
            tmp_path = Path(tmp)
            program_file = tmp_path / "mod003_list_test.ail"
            program_file.write_text(ail_program, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "compiler", "run", str(program_file)],
                capture_output=True,
                text=True,
                cwd=tmp,
                timeout=30,
            )

            assert result.returncode == 0, (
                f"MOD003 regression: list/map stdlib import failed from temp directory.\n"
                f"returncode: {result.returncode}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
            assert "Hello, world" in result.stdout, (
                f"Expected 'Hello, world' in output, got: {result.stdout}"
            )

    def test_stdlib_import_json_from_temp_directory(self) -> None:
        """Verify json stdlib module resolves from a temp directory."""
        ail_program = """\
import json;

fn main() {
    let raw = json.stringify(42);
    print(raw);
    return 0
}
"""
        with tempfile.TemporaryDirectory(prefix="ailang_mod003_json_") as tmp:
            tmp_path = Path(tmp)
            program_file = tmp_path / "mod003_json_test.ail"
            program_file.write_text(ail_program, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "compiler", "run", str(program_file)],
                capture_output=True,
                text=True,
                cwd=tmp,
                timeout=30,
            )

            assert result.returncode == 0, (
                f"MOD003 regression: json stdlib import failed from temp directory.\n"
                f"returncode: {result.returncode}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
            assert "42" in result.stdout, f"Expected '42' in output, got: {result.stdout}"

    def test_multiple_stdlib_imports_from_nested_temp_directory(self) -> None:
        """Verify stdlib modules resolve from a deeply nested temp directory."""
        ail_program = """\
import string;
import math;

fn main() {
    let msg = string.uppercase("deep test");
    let result = math.mul(3, 4);
    print(msg);
    print(result);
    return 0
}
"""
        with tempfile.TemporaryDirectory(prefix="ailang_mod003_") as tmp:
            nested = Path(tmp) / "a" / "b" / "c"
            nested.mkdir(parents=True)
            program_file = nested / "mod003_nested_test.ail"
            program_file.write_text(ail_program, encoding="utf-8")

            result = subprocess.run(
                [sys.executable, "-m", "compiler", "run", str(program_file)],
                capture_output=True,
                text=True,
                cwd=nested,
                timeout=30,
            )

            assert result.returncode == 0, (
                f"MOD003 regression: stdlib import failed from nested temp directory.\n"
                f"returncode: {result.returncode}\n"
                f"stdout: {result.stdout}\n"
                f"stderr: {result.stderr}"
            )
            assert "DEEP TEST" in result.stdout, (
                f"Expected 'DEEP TEST' in output, got: {result.stdout}"
            )
            assert "12" in result.stdout, f"Expected '12' in output, got: {result.stdout}"
