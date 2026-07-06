"""Tests for the file standard library module."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime


def _run_in_sandbox(source: str) -> int:
    """Compile and run an AILang program in a temp sandbox directory.

    The CWD is temporarily changed so that file operations in the AILang
    program are confined to the sandbox.
    """
    old_cwd = Path.cwd()
    with tempfile.TemporaryDirectory() as sandbox:
        sandbox_path = Path(sandbox)
        os.chdir(sandbox)
        try:
            main_file = sandbox_path / "main.ail"
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

            entry_module = next(
                name for name in bundle.module_irs if name.endswith("main")
            )
            return int(runtime.execute(bundle.module_irs[entry_module]))
        finally:
            os.chdir(old_cwd)


def test_file_write_and_read() -> None:
    """file.write should create a file and file.read should return its content."""
    result = _run_in_sandbox("""
import file;

fn main() {
    file.write("test.txt", "hello world");
    let content = file.read("test.txt");
    if (content == "hello world") {
        file.remove("test.txt");
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_file_append_adds_to_existing() -> None:
    """file.append should add content to an existing file."""
    result = _run_in_sandbox("""
import file;

fn main() {
    file.write("test.txt", "first");
    file.append("test.txt", "second");
    let content = file.read("test.txt");
    if (content == "firstsecond") {
        file.remove("test.txt");
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_file_exists_returns_true_for_existing() -> None:
    """file.exists should return 1 for an existing file."""
    result = _run_in_sandbox("""
import file;

fn main() {
    file.write("test.txt", "data");
    let ok = file.exists("test.txt");
    file.remove("test.txt");
    if (ok == 1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_file_exists_returns_false_for_missing() -> None:
    """file.exists should return 0 for a non-existent file."""
    result = _run_in_sandbox("""
import file;

fn main() {
    let ok = file.exists("nonexistent_file_12345.txt");
    if (ok == 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_file_remove_deletes_file() -> None:
    """file.remove should delete a file so exists returns 0."""
    result = _run_in_sandbox("""
import file;

fn main() {
    file.write("test.txt", "delete me");
    file.remove("test.txt");
    let ok = file.exists("test.txt");
    if (ok == 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1
