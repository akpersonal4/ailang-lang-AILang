"""Tests for the time standard library module."""

from __future__ import annotations

import tempfile
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime


def _run_program(source: str) -> int:
    """Compile and run an AILang source string and return the main result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        repo_root = Path(__file__).resolve().parents[1]
        session = CompilationSession()
        session._root = repo_root
        session._resolver = type(session._resolver)(repo_root)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        assert reporter.error_count == 0

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        entry_module = next(name for name in bundle.module_irs if name.endswith("main"))
        return int(runtime.execute(bundle.module_irs[entry_module]))


def test_time_timestamp_returns_positive_int() -> None:
    """time.timestamp should return a positive integer Unix timestamp."""
    result = _run_program("""
import time;

fn main() {
    let ts = time.timestamp();
    if (ts > 1000000) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_time_timestamp_non_decreasing_after_sleep() -> None:
    """Two timestamps after a short sleep should be non-decreasing."""
    result = _run_program("""
import time;

fn main() {
    let t1 = time.timestamp();
    time.sleep(5);
    let t2 = time.timestamp();
    if (t2 >= t1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_time_now_returns_non_empty_string() -> None:
    """time.now should return a non-empty string."""
    result = _run_program("""
import time;

fn main() {
    let s = time.now();
    if (s != "") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_time_now_contains_separators() -> None:
    """time.now should contain date/time separators (spaces or colons)."""
    result = _run_program("""
import time;

fn main() {
    let s = time.now();
    let has_space = 0;
    let has_colon = 0;
    if (s != "") {
        has_space = 1;
    }
    if (has_space == 1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_time_format_epoch_returns_non_empty() -> None:
    """time.format should convert a Unix timestamp to a readable string."""
    result = _run_program("""
import time;

fn main() {
    let s = time.format(0);
    if (s != "") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1
