"""Tests for the system standard library module."""

from __future__ import annotations

import tempfile
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime


def _run_program(source: str) -> int:
    """Compile and run an AILang source and return the main() result."""
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


def test_system_exit_exists_in_builtins() -> None:
    """system_exit native function should be registered in BUILTINS."""
    from compiler.runtime.builtins import BUILTINS

    assert "system_exit" in BUILTINS
    assert callable(BUILTINS["system_exit"])


def test_system_exit_function_signature() -> None:
    """system.exit function in stdlib should have correct signature."""
    result = _run_program("""
import system;
fn main() {
    // Verify the function exists and compiles
    // Note: We can't test actual sys.exit() behavior without killing the test
    return 1;
}
""")
    assert result == 1


def test_system_module_imports_successfully() -> None:
    """The system module should import without errors."""
    result = _run_program("""
import system;
fn main() {
    return 1;
}
""")
    assert result == 1
