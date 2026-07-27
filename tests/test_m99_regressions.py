"""Regression tests for M99 validation findings.

Tests for:
- F13: import inside function body should emit LANG004, not crash
- F02: ail doctor should complete without hanging
- F16: Duplicate imports should emit MOD002 warning
- --help flag support for CLI commands
"""

import subprocess
import sys
import tempfile
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# F13: import inside function body (was AssertionError crash)
# ---------------------------------------------------------------------------

def test_import_inside_function_body_emits_lang004():
    """LANG004: import inside function body should produce a diagnostic, not crash."""
    from compiler.compilation.session import CompilationSession
    from compiler.diagnostics import DiagnosticReporter

    with tempfile.TemporaryDirectory() as tmpdir:
        main = Path(tmpdir) / "main.ail"
        main.write_text(
            "fn main() {\n"
            "    import math\n"
            "    return 0\n"
            "}\n"
        )
        reporter = DiagnosticReporter()
        session = CompilationSession()
        session._root = Path(tmpdir)
        session._resolver = type(session._resolver)(Path(tmpdir))
        session.discover(main, reporter)
        session.analyze(reporter)

        lang004 = [d for d in reporter.diagnostics if d.error_code.code == "LANG004"]
        assert len(lang004) >= 1, (
            f"Expected LANG004 for import inside function, got: "
            f"{[d.error_code.code for d in reporter.diagnostics]}"
        )


def test_import_inside_function_body_no_assertion_error():
    """F13: Verify no AssertionError crash on import inside function."""
    with tempfile.TemporaryDirectory() as tmpdir:
        main = Path(tmpdir) / "main.ail"
        main.write_text(
            "fn main() {\n"
            "    import math\n"
            "    return 0\n"
            "}\n"
        )
        from compiler.compilation.session import CompilationSession
        from compiler.diagnostics import DiagnosticReporter

        reporter = DiagnosticReporter()
        session = CompilationSession()
        session._root = Path(tmpdir)
        session._resolver = type(session._resolver)(Path(tmpdir))
        session.discover(main, reporter)
        # Should NOT raise AssertionError
        session.analyze(reporter)


# ---------------------------------------------------------------------------
# F02: ail doctor should complete quickly
# ---------------------------------------------------------------------------

def test_ail_doctor_completes():
    """F02: ail doctor should complete without hanging."""
    result = subprocess.run(
        [sys.executable, "-m", "tools.ail_doctor"],
        capture_output=True,
        text=True,
        timeout=30,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0, f"ail doctor failed: {result.stderr}"
    assert "Repository Health Score" in result.stdout


# ---------------------------------------------------------------------------
# F16: Duplicate imports produce MOD002
# ---------------------------------------------------------------------------

def test_duplicate_imports_mod002():
    """MOD002: Duplicate imports should produce a warning."""
    from compiler.compilation.session import CompilationSession
    from compiler.diagnostics import DiagnosticReporter

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        a_file = tmp_path / "a.ail"
        a_file.write_text("fn a() { 1 }")

        main_file = tmp_path / "main.ail"
        main_file.write_text("import a; import a; fn test() { 1 }")

        reporter = DiagnosticReporter()
        session = CompilationSession()
        session._root = tmp_path
        session._resolver = type(session._resolver)(tmp_path)
        session.discover(main_file)
        session.analyze(reporter)

        mod002 = [d for d in reporter.diagnostics if d.error_code.code == "MOD002"]
        assert len(mod002) == 1, (
            f"Expected 1 MOD002 warning, got {len(mod002)}"
        )


# ---------------------------------------------------------------------------
# --help flag support
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "command",
    ["check", "build", "fmt", "run", "test"],
)
def test_cli_help_flag(command):
    """--help should return 0 and print usage for all CLI commands."""
    result = subprocess.run(
        [sys.executable, "-m", "compiler.cli.main", command, "--help"],
        capture_output=True,
        text=True,
        timeout=10,
        cwd=str(Path(__file__).parent.parent),
    )
    assert result.returncode == 0, f"ail {command} --help failed: {result.stderr}"
    assert "Usage" in result.stdout, f"ail {command} --help missing Usage info"
