"""Test new stdlib APIs (list.sort, list.copy, etc.)."""

from __future__ import annotations

import tempfile
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime


def _run_program(source: str):
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
        assert reporter.error_count == 0, f"Errors: {list(reporter.all_errors)}"

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        entry_module = next(name for name in bundle.module_irs if name.endswith("main"))
        return runtime.execute(bundle.module_irs[entry_module])


def test_list_sort() -> None:
    """list.sort should sort numbers in ascending order."""
    result = _run_program("""
import list;

fn main() {
    let nums = list.new();
    list.append(nums, 3);
    list.append(nums, 1);
    list.append(nums, 2);
    let sorted = list.sort(nums);
    if (list.get(sorted, 0) == 1 && list.get(sorted, 1) == 2 && list.get(sorted, 2) == 3) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1, f"Expected 1, got {result}"


def test_list_sort_by_key() -> None:
    """list.sort by key should sort maps by a field."""
    result = _run_program("""
import list;

fn main() {
    let items = list.new();
    let a = map.new();
    map.set(a, "name", "zara");
    let b = map.new();
    map.set(b, "name", "alice");
    list.append(items, a);
    list.append(items, b);
    let sorted = list.sort_by_key(items, "name");
    let first = list.get(sorted, 0);
    let firstName = map.get(first, "name");
    let second = list.get(sorted, 1);
    let secondName = map.get(second, "name");
    if (firstName == "alice" && secondName == "zara") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1, f"Expected 1, got {result}"


def test_list_copy() -> None:
    """list.copy should return a shallow copy."""
    result = _run_program("""
import list;

fn main() {
    let nums = list.new();
    list.append(nums, 1);
    list.append(nums, 2);
    let c = list.copy(nums);
    if (list.len(c) == 2 && list.get(c, 0) == 1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1, f"Expected 1, got {result}"


def test_map_get_or_default_found() -> None:
    """map.get_or_default should return value when key exists."""
    result = _run_program("""
import map;

fn main() {
    let m = map.new();
    map.set(m, "x", 42);
    let v = map.get_or_default(m, "x", -1);
    if (v == 42) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1, f"Expected 1, got {result}"


def test_map_get_or_default_missing() -> None:
    """map.get_or_default should return default when key missing."""
    result = _run_program("""
import map;

fn main() {
    let m = map.new();
    map.set(m, "x", 42);
    let v = map.get_or_default(m, "missing", -1);
    if (v == -1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1, f"Expected 1, got {result}"


def test_string_join() -> None:
    """string.join should join list elements with separator."""
    result = _run_program("""
import string;
import list;

fn main() {
    let items = list.new();
    list.append(items, "a");
    list.append(items, "b");
    list.append(items, "c");
    let joined = string.join(items, ",");
    if (joined == "a,b,c") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1, f"Expected 1, got {result}"


def test_list_filter_by_key() -> None:
    """list.filter_by_key should filter list of maps."""
    result = _run_program("""
import list;
import map;

fn main() {
    let items = list.new();
    let m1 = map.new();
    map.set(m1, "status", "active");
    let m2 = map.new();
    map.set(m2, "status", "inactive");
    let m3 = map.new();
    map.set(m3, "status", "active");
    list.append(items, m1);
    list.append(items, m2);
    list.append(items, m3);
    let filtered = list.filter_by_key(items, "status", "active");
    if (list.len(filtered) == 2) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1, f"Expected 1, got {result}"


def test_list_filter_by_key_none() -> None:
    """list.filter_by_key should return empty list when no match."""
    result = _run_program("""
import list;
import map;

fn main() {
    let items = list.new();
    let m1 = map.new();
    map.set(m1, "status", "inactive");
    list.append(items, m1);
    let filtered = list.filter_by_key(items, "status", "active");
    if (list.len(filtered) == 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1, f"Expected 1, got {result}"
