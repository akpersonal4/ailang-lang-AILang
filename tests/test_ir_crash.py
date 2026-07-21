"""Regression test ensuring that malformed for‑loops do not crash the compiler.

The IR builder raises a ValueError when a for‑loop writes to more than one
accumulator variable. Previously this bubbled up as a traceback. After Sprint 2
the compiler should catch this and emit a CMP001 diagnostic.
"""

import tempfile
from pathlib import Path

import pytest

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter


def test_for_loop_multiple_accumulators() -> None:
    """Two accumulator variables in a for-loop raise ValueError."""
    source = """
import list;
fn main() {
    let items = list.new();
    list.append(items, 1);
    list.append(items, 2);
    let total = 0;
    let count = 0;
    for item in items {
        total = total + item;
        count = count + 1;
    }
    return total;
}
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        repo_root = Path(__file__).resolve().parents[1]
        session = CompilationSession(experimental_loops=True)
        session._root = repo_root
        session._resolver = type(session._resolver)(repo_root)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        session.type_check(reporter)

        with pytest.raises(ValueError, match="Only one accumulator"):
            session.build_ir()
