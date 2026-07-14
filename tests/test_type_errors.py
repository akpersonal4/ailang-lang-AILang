"""Tests for compile‑time type error detection (M69.7 Sprint 1)."""

import tempfile
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter, Severity


def test_type_errors() -> None:
    """Verify that illegal arithmetic and comparison produce diagnostics.

    The source contains three offending statements:
    1. string + int (TYP005)
    2. int + bool   (TYP005)
    3. string == list[int] (TYP006)
    """
    source = """
fn bad1() { let x = "hello" + 1; }
fn bad2() { let y = 10 + true; }
fn bad3() { if "hello" == [1,2,3] { }
}
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        # Set up session with temporary root to ensure relative imports resolve correctly
        session = CompilationSession()
        session._root = tmp_path
        session._resolver = type(session._resolver)(tmp_path)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        session.type_check(reporter)

        errors = [d for d in reporter.diagnostics if d.severity == Severity.ERROR]
        codes = {d.error_code.code for d in errors}
        assert "TYP005" in codes, "Expected arithmetic type error TYP005"
        assert "TYP006" in codes, "Expected comparison type error TYP006"
        assert len(errors) >= 3, "Expected at least three error diagnostics"
