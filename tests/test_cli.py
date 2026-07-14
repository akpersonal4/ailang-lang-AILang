"""CLI integration tests for the `ail` command.

Tests both the Python API (run, build, check, version, help) and
the installed `ail` command via subprocess.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

from compiler.cli.main import (
    cmd_build,
    cmd_check,
    cmd_fmt,
    cmd_help,
    cmd_run,
    cmd_version,
)

# =============================================================================
# Existing integration tests (preserved from earlier milestones)
# =============================================================================


# =============================================================================
# Direct API tests (fast, no subprocess)
# =============================================================================


class TestCliAPI:
    """Test the CLI command functions directly."""

    def test_run_valid_program(self) -> None:
        """run on a valid program returns 0."""
        path = Path(__file__).resolve().parents[1] / "examples" / "collections.ail"
        result = cmd_run([str(path)])
        assert result == 0

    def test_run_missing_file(self) -> None:
        """run on a missing file returns 1."""
        result = cmd_run(["/nonexistent/file.ail"])
        assert result == 1

    def test_run_no_args(self) -> None:
        """run with no args returns 1."""
        result = cmd_run([])
        assert result == 1

    def test_build_valid_program(self) -> None:
        """build on a valid program returns 0."""
        path = Path(__file__).resolve().parents[1] / "examples" / "collections.ail"
        result = cmd_build([str(path)])
        assert result == 0

    def test_build_missing_file(self) -> None:
        """build on a missing file returns 1."""
        result = cmd_build(["/nonexistent/file.ail"])
        assert result == 1

    def test_build_invalid_program(self) -> None:
        """build on a program with errors returns 1."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "bad.ail"
            source.write_text(
                "fn main() { let x = missing; return x; }", encoding="utf-8"
            )
            result = cmd_build([str(source)])
            assert result == 1

    def test_check_alias(self) -> None:
        """check is an alias for build and returns the same result."""
        path = Path(__file__).resolve().parents[1] / "examples" / "collections.ail"
        assert cmd_check([str(path)]) == cmd_build([str(path)])

    def test_version(self) -> None:
        """version returns 0 and prints a version string."""
        result = cmd_version([])
        assert result == 0

    def test_help(self) -> None:
        """help returns 0 and prints usage info."""
        result = cmd_help([])
        assert result == 0

    # ------------------------------------------------------------------
    # fmt command tests
    # ------------------------------------------------------------------

    def test_fmt_formats_file(self) -> None:
        """fmt formats a file in-place and returns 0."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "test.ail"
            source.write_text("fn main(){return 0;}", encoding="utf-8")
            result = cmd_fmt([str(source)])
            assert result == 0
            content = source.read_text(encoding="utf-8")
            assert "fn main() {" in content
            assert "    return 0;" in content

    def test_fmt_idempotent(self) -> None:
        """fmt on already-formatted file returns 0 (no changes)."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "test.ail"
            source.write_text("fn main() {\n    return 0;\n}\n", encoding="utf-8")
            result = cmd_fmt([str(source)])
            assert result == 0
            content = source.read_text(encoding="utf-8")
            assert content == "fn main() {\n    return 0;\n}\n"

    def test_fmt_check_formatted(self) -> None:
        """fmt --check on formatted file returns 0."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "test.ail"
            source.write_text("fn main() {\n    return 0;\n}\n", encoding="utf-8")
            result = cmd_fmt(["--check", str(source)])
            assert result == 0

    def test_fmt_check_unformatted(self) -> None:
        """fmt --check on unformatted file returns 1."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "test.ail"
            source.write_text("fn main(){return 0;}", encoding="utf-8")
            result = cmd_fmt(["--check", str(source)])
            assert result == 1

    def test_fmt_missing_file(self) -> None:
        """fmt on missing file returns 1."""
        result = cmd_fmt(["/nonexistent/file.ail"])
        assert result == 1

    def test_fmt_invalid_syntax(self) -> None:
        """fmt on file with syntax errors returns 1."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "bad.ail"
            source.write_text("fn main() { let x = ; }", encoding="utf-8")
            result = cmd_fmt([str(source)])
            assert result == 1

    def test_fmt_no_args(self) -> None:
        """fmt with no args returns 1."""
        result = cmd_fmt([])
        assert result == 1

    def test_fmt_diff_formatted(self) -> None:
        """fmt --diff on formatted file returns 0."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "test.ail"
            source.write_text("fn main() {\n    return 0;\n}\n", encoding="utf-8")
            result = cmd_fmt(["--diff", str(source)])
            assert result == 0

    def test_fmt_diff_unformatted(self) -> None:
        """fmt --diff on unformatted file returns 1."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "test.ail"
            source.write_text("fn main(){return 0;}", encoding="utf-8")
            result = cmd_fmt(["--diff", str(source)])
            assert result == 1

    def test_fmt_quiet(self) -> None:
        """fmt --quiet suppresses status output."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "test.ail"
            source.write_text("fn main(){return 0;}", encoding="utf-8")
            result = cmd_fmt(["--quiet", str(source)])
            assert result == 0
            content = source.read_text(encoding="utf-8")
            assert "    return 0;" in content

    def test_fmt_directory(self) -> None:
        """fmt formats all files in a directory."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "a.ail").write_text("fn main(){return 0;}", encoding="utf-8")
            (d / "b.ail").write_text("fn add(a,b){return a+b;}", encoding="utf-8")
            result = cmd_fmt([str(d)])
            assert result == 0
            assert "    return 0;" in (d / "a.ail").read_text(encoding="utf-8")
            assert "    return a + b;" in (d / "b.ail").read_text(encoding="utf-8")

    def test_fmt_directory_check(self) -> None:
        """fmt --check on unformatted directory returns 1."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "a.ail").write_text("fn main(){return 0;}", encoding="utf-8")
            result = cmd_fmt(["--check", str(d)])
            assert result == 1

    def test_fmt_directory_check_formatted(self) -> None:
        """fmt --check on formatted directory returns 0."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            f = d / "test.ail"
            f.write_text("fn main() {\n    return 0;\n}\n", encoding="utf-8")
            result = cmd_fmt(["--check", str(d)])
            assert result == 0

    def test_fmt_directory_diff(self) -> None:
        """fmt --diff on unformatted directory returns 1."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            d = Path(tmpdir)
            (d / "a.ail").write_text("fn main(){return 0;}", encoding="utf-8")
            result = cmd_fmt(["--diff", str(d)])
            assert result == 1

    def test_fmt_multiple_paths(self) -> None:
        """fmt accepts multiple file/directory paths."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            d1 = Path(tmpdir) / "dir1"
            d2 = Path(tmpdir) / "dir2"
            d1.mkdir()
            d2.mkdir()
            (d1 / "a.ail").write_text("fn main(){return 0;}", encoding="utf-8")
            (d2 / "b.ail").write_text("fn main(){return 0;}", encoding="utf-8")
            result = cmd_fmt(["--check", str(d1), str(d2)])
            assert result == 1

    def test_fmt_unknown_flag(self) -> None:
        """fmt with unknown flag returns 1."""
        result = cmd_fmt(["--unknown", "test.ail"])
        assert result == 1

    def test_run_stdout_output(self, capsys: pytest.CaptureFixture[str]) -> None:
        """run on a program with print() captures stdout."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "test.ail"
            source.write_text(
                'fn main() { print("hello from ail"); return 0 }', encoding="utf-8"
            )
            result = cmd_run([str(source)])
            captured = capsys.readouterr()
            assert result == 0
            assert "hello from ail" in captured.out

    def test_run_stderr_on_error(self, capsys: pytest.CaptureFixture[str]) -> None:
        """run on an invalid program prints errors to stderr."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "bad.ail"
            source.write_text("fn main() { bad syntax }", encoding="utf-8")
            result = cmd_run([str(source)])
            captured = capsys.readouterr()
            assert result == 1
            assert "ERROR SEM" in captured.err


# =============================================================================
# Integration tests using the `ail` subprocess
# =============================================================================


class TestAilCommand:
    """Test the installed `ail` command via subprocess."""

    def test_ail_version(self) -> None:
        """`ail version` prints version."""
        result = subprocess.run(
            [sys.executable, "-m", "compiler", "version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "AILang v" in result.stdout

    def test_ail_help(self) -> None:
        """`ail help` prints usage info."""
        result = subprocess.run(
            [sys.executable, "-m", "compiler", "help"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Usage:" in result.stdout

    def test_ail_run_example(self) -> None:
        """`ail run <example>` runs successfully."""
        example = Path(__file__).resolve().parents[1] / "examples" / "collections.ail"
        result = subprocess.run(
            [sys.executable, "-m", "compiler", "run", str(example)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"

    def test_ail_build_example(self) -> None:
        """`ail build <example>` succeeds."""
        example = Path(__file__).resolve().parents[1] / "examples" / "collections.ail"
        result = subprocess.run(
            [sys.executable, "-m", "compiler", "build", str(example)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Build successful" in result.stdout

    def test_ail_check_example(self) -> None:
        """`ail check <example>` succeeds (checks for forward references)."""
        example = Path(__file__).resolve().parents[1] / "examples" / "collections.ail"
        result = subprocess.run(
            [sys.executable, "-m", "compiler", "check", str(example)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0
        assert "Check passed" in result.stdout

    def test_ail_run_missing_file(self) -> None:
        """`ail run <missing>` returns error."""
        result = subprocess.run(
            [sys.executable, "-m", "compiler", "run", "/nonexistent/file.ail"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1
        assert "File not found" in result.stderr

    def test_ail_build_invalid_program(self) -> None:
        """`ail build <invalid>` returns error."""
        import tempfile

        with tempfile.TemporaryDirectory() as tmpdir:
            source = Path(tmpdir) / "bad.ail"
            source.write_text(
                "fn main() { let x = missing; return x; }", encoding="utf-8"
            )
            result = subprocess.run(
                [sys.executable, "-m", "compiler", "build", str(source)],
                capture_output=True,
                text=True,
            )
            assert result.returncode == 1
            assert "ERROR SEM" in result.stderr

    def test_ail_no_args(self) -> None:
        """`ail` with no args prints help and returns 1."""
        result = subprocess.run(
            [sys.executable, "-m", "compiler"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1

    def test_ail_invalid_subcommand(self) -> None:
        """`ail <unknown>` treats it as a file path and errors."""
        result = subprocess.run(
            [sys.executable, "-m", "compiler", "invalid_command"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 1

    def test_ail_shorthand_file(self) -> None:
        """`ail <file>` is shorthand for `ail run <file>`."""
        example = Path(__file__).resolve().parents[1] / "examples" / "collections.ail"
        result = subprocess.run(
            [sys.executable, "-m", "compiler", str(example)],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, f"stderr: {result.stderr}"


def _run_file(path_str: str) -> int:
    """Compat helper: wraps cmd_run to accept a single file path string."""
    return cmd_run([path_str])


def test_cli_can_run_collection_example() -> None:
    """The CLI should execute the bundled collection example successfully."""
    repo_root = Path(__file__).resolve().parents[1]
    result = _run_file(str(repo_root / "examples" / "collections.ail"))
    assert result == 0


def test_cli_can_run_file_io_example(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The CLI should execute the file I/O example successfully in a sandbox."""
    import os

    old_cwd = Path.cwd()
    os.chdir(tmp_path)
    try:
        repo_root = Path(__file__).resolve().parents[1]
        result = _run_file(str(repo_root / "examples" / "file_io.ail"))
        captured = capsys.readouterr()
        assert result == 0
        assert "File I/O Demo" in captured.out
        assert "Hello, AILang!" in captured.out
    finally:
        os.chdir(old_cwd)


def test_cli_can_run_json_example(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The CLI should execute the JSON demo example successfully."""
    repo_root = Path(__file__).resolve().parents[1]
    result = _run_file(str(repo_root / "examples" / "json_demo.ail"))
    captured = capsys.readouterr()
    assert result == 0
    assert "JSON Demo" in captured.out


def test_cli_can_run_csv_example(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The CLI should execute the CSV demo example successfully."""
    repo_root = Path(__file__).resolve().parents[1]
    result = _run_file(str(repo_root / "examples" / "csv_demo.ail"))
    captured = capsys.readouterr()
    assert result == 0
    assert "CSV Demo" in captured.out
