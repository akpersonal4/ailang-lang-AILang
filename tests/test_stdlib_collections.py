"""Tests for collection helpers in the standard library."""

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


def test_array_module_helpers_work() -> None:
    """The array module should provide basic list-like helpers."""
    result = _run_program("""
import array;

fn main() {
    let values = array.new();
    array.push(values, 1);
    array.push(values, 2);
    if (
        array.len(values) == 2
        && array.get(values, 0) == 1
        && array.contains(values, 2)
    ) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_module_helpers_work() -> None:
    """The list module should provide basic list helpers."""
    result = _run_program("""
import list;

fn main() {
    let values = list.new();
    list.append(values, 3);
    list.append(values, 4);
    if (
        list.len(values) == 2
        && list.get(values, 1) == 4
        && list.contains(values, 3)
    ) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_map_module_helpers_work() -> None:
    """The map module should support keyed lookups and membership checks."""
    result = _run_program("""
import map;

fn main() {
    let values = map.new();
    map.set(values, "answer", 42);
    if (map.has(values, "answer") && map.get(values, "answer") == 42) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_set_module_helpers_work() -> None:
    """The set module should support membership and size queries."""
    result = _run_program("""
import set;

fn main() {
    let values = set.new();
    set.add(values, 5);
    if (set.contains(values, 5) && set.len(values) == 1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_remove_removes_element() -> None:
    """list.remove should remove the first occurrence of a value."""
    result = _run_program("""
import list;

fn main() {
    let values = list.new();
    list.append(values, 1);
    list.append(values, 2);
    list.append(values, 3);
    list.remove(values, 2);
    if (list.len(values) == 2 && list.get(values, 0) == 1 && list.get(values, 1) == 3) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_clear_empties_list() -> None:
    """list.clear should remove all elements from a list."""
    result = _run_program("""
import list;

fn main() {
    let values = list.new();
    list.append(values, 1);
    list.append(values, 2);
    list.clear(values);
    if (list.len(values) == 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_array_remove_removes_element() -> None:
    """array.remove should remove the first occurrence of a value."""
    result = _run_program("""
import array;

fn main() {
    let values = array.new();
    array.push(values, 10);
    array.push(values, 20);
    array.push(values, 30);
    array.remove(values, 20);
    if (array.len(values) == 2
        && array.get(values, 0) == 10
        && array.get(values, 1) == 30) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_array_clear_empties_array() -> None:
    """array.clear should remove all elements from an array."""
    result = _run_program("""
import array;

fn main() {
    let values = array.new();
    array.push(values, 1);
    array.push(values, 2);
    array.clear(values);
    if (array.len(values) == 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_map_delete_removes_key() -> None:
    """map.delete should remove a key-value pair from a map."""
    result = _run_program("""
import map;

fn main() {
    let values = map.new();
    map.set(values, "x", 10);
    map.set(values, "y", 20);
    map.delete(values, "x");
    if (!map.has(values, "x") && map.has(values, "y")) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_map_keys_returns_list_of_keys() -> None:
    """map.keys should return a list of keys in the map."""
    result = _run_program("""
import map;
import list;

fn main() {
    let values = map.new();
    map.set(values, "a", 1);
    map.set(values, "b", 2);
    let ks = map.keys(values);
    if (list.contains(ks, "a") && list.contains(ks, "b") && list.len(ks) == 2) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_map_clear_empties_map() -> None:
    """map.clear should remove all entries from a map."""
    result = _run_program("""
import map;

fn main() {
    let values = map.new();
    map.set(values, "a", 1);
    map.set(values, "b", 2);
    map.clear(values);
    if (!map.has(values, "a") && !map.has(values, "b")) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_set_remove_removes_element() -> None:
    """set.remove should remove a value from a set."""
    result = _run_program("""
import set;

fn main() {
    let values = set.new();
    set.add(values, 5);
    set.add(values, 10);
    set.remove(values, 5);
    if (!set.contains(values, 5) && set.contains(values, 10) && set.len(values) == 1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_set_clear_empties_set() -> None:
    """set.clear should remove all entries from a set."""
    result = _run_program("""
import set;

fn main() {
    let values = set.new();
    set.add(values, 5);
    set.add(values, 10);
    set.clear(values);
    if (set.len(values) == 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_group_by_key_groups_items() -> None:
    """list.group_by_key should group items by a key field."""
    result = _run_program("""
import list;

fn main() {
    let items = list.new();
    list.append(items, map.set(map.set(map.new(), "type", "a"), "val", "1"));
    list.append(items, map.set(map.set(map.new(), "type", "b"), "val", "2"));
    list.append(items, map.set(map.set(map.new(), "type", "a"), "val", "3"));
    let grouped = list.group_by_key(items, "type");
    if (map.has(grouped, "a") && map.has(grouped, "b")) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_sum_by_key_sums_values() -> None:
    """list.sum_by_key should sum numeric values of a key field."""
    result = _run_program("""
import list;

fn main() {
    let items = list.new();
    list.append(items, map.set(map.new(), "amount", "10"));
    list.append(items, map.set(map.new(), "amount", "20"));
    list.append(items, map.set(map.new(), "amount", "30"));
    let total = list.sum_by_key(items, "amount");
    if (total == 60) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_take_returns_first_n_items() -> None:
    """list.take should return the first n items."""
    result = _run_program("""
import list;

fn main() {
    let items = list.new();
    list.append(items, "a");
    list.append(items, "b");
    list.append(items, "c");
    list.append(items, "d");
    let first_two = list.take(items, 2);
    if (list.len(first_two) == 2 && list.get(first_two, 0) == "a" && list.get(first_two, 1) == "b") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_skip_returns_items_after_n() -> None:
    """list.skip should return items after the first n."""
    result = _run_program("""
import list;

fn main() {
    let items = list.new();
    list.append(items, "a");
    list.append(items, "b");
    list.append(items, "c");
    list.append(items, "d");
    let rest = list.skip(items, 2);
    if (list.len(rest) == 2 && list.get(rest, 0) == "c" && list.get(rest, 1) == "d") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_search_by_name_finds_matches() -> None:
    """list.search_by_name should find items by case-insensitive name match."""
    result = _run_program("""
import list;

fn main() {
    let items = list.new();
    list.append(items, map.set(map.new(), "name", "Apple"));
    list.append(items, map.set(map.new(), "name", "Banana"));
    list.append(items, map.set(map.new(), "name", "Apricot"));
    let results = list.search_by_name(items, "ap");
    if (list.len(results) == 2) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_exists_by_key_checks_membership() -> None:
    """list.exists_by_key should check if any item has a matching key value."""
    result = _run_program("""
import list;

fn main() {
    let items = list.new();
    list.append(items, map.set(map.new(), "status", "active"));
    list.append(items, map.set(map.new(), "status", "inactive"));
    let exists = list.exists_by_key(items, "status", "active");
    let not_exists = list.exists_by_key(items, "status", "deleted");
    if (exists == true && not_exists == false) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_map_values_returns_all_values() -> None:
    """map.values should return a list of all values in the map."""
    result = _run_program("""
import map;
import list;

fn main() {
    let m = map.new();
    map.set(m, "x", "10");
    map.set(m, "y", "20");
    let vals = map.values(m);
    if (list.len(vals) == 2) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1
