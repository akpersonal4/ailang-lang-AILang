"""Tests for the random standard library module."""

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


def test_random_int_in_range() -> None:
    """random.int should return an integer between min and max (inclusive)."""
    result = _run_program("""
import random;

fn main() {
    let val = random.int(1, 100);
    if (val >= 1) {
        if (val <= 100) {
            return 1;
        }
    }
    return 0;
}
""")
    assert result == 1


def test_random_int_deterministic_range() -> None:
    """random.int should respect exact range boundaries when min == max."""
    result = _run_program("""
import random;

fn main() {
    let val = random.int(5, 5);
    if (val == 5) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_random_float_in_012_range() -> None:
    """random.float should return a value in [0,1), verified by scaling."""
    result = _run_program("""
import random;

fn main() {
    let val = random.float();
    let scaled = val * 10;
    if (scaled >= 0) {
        if (scaled < 10) {
            return 1;
        }
    }
    return 0;
}
""")
    assert result == 1


def test_random_choice_from_list() -> None:
    """random.choice should return an element from the given list."""
    result = _run_program("""
import random;
import list;

fn main() {
    let lst = list.new();
    list.append(lst, 10);
    list.append(lst, 20);
    list.append(lst, 30);
    let chosen = random.choice(lst);
    if (chosen >= 10) {
        if (chosen <= 30) {
            return 1;
        }
    }
    return 0;
}
""")
    assert result == 1
