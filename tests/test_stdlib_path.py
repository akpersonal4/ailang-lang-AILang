"""Tests for the path standard library module."""

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


def test_path_join_combines_two_parts() -> None:
    """path.join should combine path components with the OS separator."""
    result = _run_program("""
import path;

fn main() {
    let p = path.join("foo", "bar");
    if (p == "foo/bar" || p == "foo\\\\bar") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_path_basename_returns_filename() -> None:
    """path.basename should return the file name from a path."""
    result = _run_program("""
import path;

fn main() {
    let name = path.basename("foo/bar.txt");
    if (name == "bar.txt") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_path_dirname_returns_directory() -> None:
    """path.dirname should return the directory portion of a path."""
    result = _run_program("""
import path;

fn main() {
    let dir = path.dirname("foo/bar.txt");
    if (dir == "foo") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_path_extension_returns_suffix() -> None:
    """path.extension should return the file extension including the dot."""
    result = _run_program("""
import path;

fn main() {
    let ext = path.extension("data.txt");
    if (ext == ".txt") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_path_extension_empty_for_no_ext() -> None:
    """path.extension should return empty string when there is no extension."""
    result = _run_program("""
import path;

fn main() {
    let ext = path.extension("Makefile");
    if (ext == "") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_path_normalize_cleans_dot_segments() -> None:
    """path.normalize should resolve dot and dot-dot segments."""
    result = _run_program("""
import path;

fn main() {
    let p = path.normalize("foo/./bar/../baz");
    let expected = path.normalize("foo/baz");
    if (p == expected) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_path_module_imports_and_uses_all_functions() -> None:
    """All path module functions should work together."""
    result = _run_program("""
import path;

fn main() {
    let full = path.join("dir", "file.txt");
    let base = path.basename(full);
    let dir = path.dirname(full);
    let ext = path.extension(full);
    if (base == "file.txt" && ext == ".txt") {
        if (dir == "dir") {
            return 1;
        }
    }
    return 0;
}
""")
    assert result == 1
