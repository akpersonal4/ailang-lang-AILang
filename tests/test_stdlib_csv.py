"""Tests for the CSV standard library module."""

from __future__ import annotations

import os
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


def _run_in_sandbox(source: str) -> int:
    """Compile and run an AILang program inside a temp directory sandbox."""
    old_cwd = Path.cwd()
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        os.chdir(tmp_path)
        try:
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

            entry_module = next(
                name for name in bundle.module_irs if name.endswith("main")
            )
            return int(runtime.execute(bundle.module_irs[entry_module]))
        finally:
            os.chdir(old_cwd)


def test_csv_parse_basic() -> None:
    """csv.parse should return a list of rows from CSV text."""
    result = _run_program("""
import csv;
import list;

fn main() {
    let rows = csv.parse("a,b\\n1,2");
    let row0 = list.get(rows, 0);
    let cell = list.get(row0, 0);
    if (cell == "a") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_csv_parse_empty() -> None:
    """csv.parse of empty string returns an empty list of rows."""
    result = _run_program("""
import csv;
import list;

fn main() {
    let rows = csv.parse("");
    let count = list.len(rows);
    if (count == 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_csv_parse_single_cell() -> None:
    """csv.parse of a single value returns one row with one cell."""
    result = _run_program("""
import csv;
import list;

fn main() {
    let rows = csv.parse("hello");
    let row0 = list.get(rows, 0);
    let cell = list.get(row0, 0);
    if (cell == "hello") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_csv_parse_quoted() -> None:
    """csv.parse should handle quoted fields containing commas."""
    result = _run_program("""
import csv;
import list;

fn main() {
    let rows = csv.parse("\\"a,b\\",c");
    let row0 = list.get(rows, 0);
    let cell = list.get(row0, 0);
    if (cell == "a,b") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_csv_parse_header_basic() -> None:
    """csv.parse_header returns list of maps keyed by header."""
    result = _run_program("""
import csv;
import list;
import map;

fn main() {
    let rows = csv.parse_header("name,age\\nAlice,30");
    let row0 = list.get(rows, 0);
    let name = map.get(row0, "name");
    if (name == "Alice") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_csv_parse_header_empty_data() -> None:
    """csv.parse_header with header only (no data rows) returns empty list."""
    result = _run_program("""
import csv;
import list;

fn main() {
    let rows = csv.parse_header("a,b");
    let count = list.len(rows);
    if (count == 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_csv_parse_header_access() -> None:
    """csv.parse_header allows column access by name via map.get."""
    result = _run_program("""
import csv;
import list;
import map;

fn main() {
    let rows = csv.parse_header("x,y,z\\n10,20,30");
    let row0 = list.get(rows, 0);
    let y = map.get(row0, "y");
    if (y == "20") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_csv_stringify_basic() -> None:
    """csv.stringify should serialize rows to CSV text."""
    result = _run_program("""
import csv;
import list;

fn main() {
    let row = list.new();
    list.append(row, "a");
    list.append(row, "b");
    let rows = list.new();
    list.append(rows, row);
    let out = csv.stringify(rows);
    if (out == "a,b\\n") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_csv_stringify_empty() -> None:
    """csv.stringify of an empty list returns an empty string."""
    result = _run_program("""
import csv;
import list;

fn main() {
    let rows = list.new();
    let out = csv.stringify(rows);
    if (out == "") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_csv_roundtrip() -> None:
    """Parse then stringify then parse should preserve structure."""
    result = _run_program("""
import csv;
import list;

fn main() {
    let rows = csv.parse("a,b\\n1,2");
    let text = csv.stringify(rows);
    let rows2 = csv.parse(text);
    let row0 = list.get(rows2, 0);
    let cell = list.get(row0, 0);
    if (cell == "a") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_csv_with_file_read() -> None:
    """Write CSV via file module, read it back, and parse it."""
    result = _run_in_sandbox("""
import csv;
import file;
import list;
import map;

fn main() {
    file.write("test.csv", "name,role\\nAlice,Engineer");
    let content = file.read("test.csv");
    let rows = csv.parse_header(content);
    let row0 = list.get(rows, 0);
    let name = map.get(row0, "name");
    if (name == "Alice") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1
