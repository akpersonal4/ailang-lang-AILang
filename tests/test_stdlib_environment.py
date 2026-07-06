"""Tests for the environment standard library module."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime import builtins as runtime_builtins
from compiler.runtime.interpreter import Runtime


@pytest.fixture(autouse=True)
def _reset_program_argv() -> None:
    """Reset _program_argv so env_args() falls back to sys.argv."""
    runtime_builtins._program_argv = None


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


def test_env_get_returns_empty_for_missing() -> None:
    """environment.get should return empty string for missing env vars."""
    result = _run_program("""
import environment;

fn main() {
    let val = environment.get("__AILANG_TEST_NONEXISTENT__");
    if (val == "") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_env_get_returns_value_for_set_var() -> None:
    """environment.get should return the value of a set environment variable."""
    os.environ["__AILANG_TEST_VAR__"] = "test_value_42"
    try:
        result = _run_program("""
import environment;

fn main() {
    let val = environment.get("__AILANG_TEST_VAR__");
    if (val == "test_value_42") {
        return 1;
    }
    return 0;
}
""")
        assert result == 1
    finally:
        os.environ.pop("__AILANG_TEST_VAR__", None)


def test_env_cwd_returns_non_empty() -> None:
    """environment.cwd should return the current working directory."""
    result = _run_program("""
import environment;

fn main() {
    let dir = environment.cwd();
    if (dir != "") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_env_args_returns_list() -> None:
    """environment.args should return a list (non-empty in test context)."""
    result = _run_program("""
import environment;
import list;

fn main() {
    let a = environment.args();
    if (list.len(a) > 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1
