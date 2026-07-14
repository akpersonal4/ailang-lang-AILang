"""Regression test ensuring that malformed for‑loops do not crash the compiler.

The IR builder raises a ValueError when a for‑loop writes to more than one
accumulator variable. Previously this bubbled up as a traceback. After Sprint 2
the compiler should catch this and emit a CMP001 diagnostic.
"""

import tempfile
from pathlib import Path

from compiler.cli.main import _compile


def test_for_loop_multiple_accumulators() -> None:
    source = """
fn bad() {
    for i in [1,2,3] {
        let acc1 = i;
        let acc2 = i;
    }
}
fn main() { bad(); }
"""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        # Use experimental loops to enable the for‑loop construct.
        session, reporter = _compile(main_file, experimental_loops=True)
        # Expect compilation to fail before returning a session.
        assert session is None, "Session should be None on internal compiler error"
        # Check that a CMP001 diagnostic was emitted.
        cmp_errors = [d for d in reporter.diagnostics if d.error_code.code == "CMP001"]
        assert cmp_errors, "Expected at least one CMP001 internal compiler error"
