"""P0-1 regression tests: process exit codes (V2 Foundation Hardening).

Verifies the process exit-code contract end-to-end through the real CLI
(`python -m compiler run <file>`) so automation and AI agents can rely on
the exit status to detect failure:

- successful program (main returns 0 or a non-Int value) -> exit 0
- application failure (main returns a non-zero Int) -> that exit code
- runtime failure -> non-zero
- compile/type-check failure -> non-zero
- explicit system.exit(code) keeps precedence -> that exit code
- stdout carries program output only; diagnostics go to stderr
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest


def _run_file(tmp_path: Path, source: str, *cli_args: str) -> subprocess.CompletedProcess[str]:
    """Write *source* to a temp .ail file and run it through the CLI."""
    prog = tmp_path / "app.ail"
    prog.write_text(source, encoding="utf-8")
    return subprocess.run(
        [sys.executable, "-m", "compiler", "run", *cli_args, str(prog)],
        capture_output=True,
        text=True,
    )


class TestP01ExitCodes:
    def test_success_zero_return_exits_zero(self, tmp_path: Path) -> None:
        result = _run_file(tmp_path, "fn main() { return 0; }")
        assert result.returncode == 0
        assert result.stdout == ""
        assert result.stderr == ""

    def test_success_no_return_exits_zero(self, tmp_path: Path) -> None:
        result = _run_file(tmp_path, "fn main() { print(\"ok\"); }")
        assert result.returncode == 0
        assert result.stdout == "ok\n"

    def test_success_string_return_exits_zero(self, tmp_path: Path) -> None:
        """Non-Int return values mean the program ran to completion."""
        result = _run_file(tmp_path, 'fn main() { return "done"; }')
        assert result.returncode == 0

    def test_success_bool_return_exits_zero(self, tmp_path: Path) -> None:
        """A Bool return is not an Int exit code and must not exit 1."""
        result = _run_file(tmp_path, "fn main() { return true; }")
        assert result.returncode == 0

    def test_nonzero_main_return_becomes_exit_code(self, tmp_path: Path) -> None:
        """Regression: main returning 1 used to exit 0."""
        result = _run_file(tmp_path, "fn main() { return 1; }")
        assert result.returncode == 1

    def test_arbitrary_main_return_becomes_exit_code(self, tmp_path: Path) -> None:
        result = _run_file(tmp_path, "fn main() { return 7; }")
        assert result.returncode == 7

    def test_runtime_failure_exits_nonzero(self, tmp_path: Path) -> None:
        result = _run_file(
            tmp_path,
            "import list;\n"
            "fn main() {\n"
            "    let items = list.new();\n"
            "    return list.get(items, 0);\n"
            "}\n",
        )
        assert result.returncode == 1
        assert result.stdout == ""
        assert "Runtime Error" in result.stderr

    def test_missing_file_exits_nonzero(self) -> None:
        result = subprocess.run(
            [sys.executable, "-m", "compiler", "run", "/nonexistent/file.ail"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "File not found" in result.stderr

    def test_compile_failure_exits_nonzero(self, tmp_path: Path) -> None:
        prog = tmp_path / "bad.ail"
        prog.write_text("fn main() { let x = missing; return x; }", encoding="utf-8")
        result = subprocess.run(
            [sys.executable, "-m", "compiler", "run", str(prog)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert result.stdout == ""
        assert "ERROR" in result.stderr

    def test_system_exit_keeps_precedence(self, tmp_path: Path) -> None:
        """system.exit(code) wins even when main would return 0."""
        result = _run_file(
            tmp_path,
            "import system;\n"
            "fn main() {\n"
            "    system.exit(3);\n"
            "    return 0;\n"
            "}\n",
        )
        assert result.returncode == 3

    def test_system_exit_zero(self, tmp_path: Path) -> None:
        result = _run_file(
            tmp_path,
            "import system;\n"
            "fn main() {\n"
            "    system.exit(0);\n"
            "}\n",
        )
        assert result.returncode == 0
