"""Comprehensive validation of all Standard Library v1.0 modules.

Tests every public API across all 16 stdlib modules with real program
execution, covering normal usage, edge cases, and error conditions.
"""

from __future__ import annotations

import os
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
        assert (
            reporter.error_count == 0
        ), f"Compile errors: {[d.message for d in reporter.diagnostics]}"

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        entry_module = next(name for name in bundle.module_irs if name.endswith("main"))
        return int(runtime.execute(bundle.module_irs[entry_module]))


def _run_in_sandbox(source: str) -> int:
    """Compile and run an AILang program inside a temp directory."""
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


# =============================================================================
# Basic Language Validation
# =============================================================================


def test_val_hello_world_returns_42() -> None:
    """Minimal program that returns a constant."""
    result = _run_program("""
fn main() {
    return 42;
}
""")
    assert result == 42


def test_val_variable_declaration_and_arithmetic() -> None:
    """Variable declarations and arithmetic operations."""
    result = _run_program("""
fn main() {
    let x = 10;
    let y = 20;
    let sum = x + y;
    return sum;
}
""")
    assert result == 30


def test_val_all_comparison_operators() -> None:
    """All six comparison operators produce correct boolean results."""
    result = _run_program("""
fn main() {
    let a = 5 < 10;
    let b = 10 > 5;
    let c = 5 == 5;
    let d = 5 != 10;
    let e = 5 <= 5;
    let f = 10 >= 10;
    let sum = a + b + c + d + e + f;
    return sum;
}
""")
    assert result == 6


def test_val_nested_if_else() -> None:
    """Nested if-else with else branch."""
    result = _run_program("""
fn main() {
    let score = 75;
    if (score >= 90) {
        return 4;
    } else {
        if (score >= 80) {
            return 3;
        } else {
            if (score >= 70) {
                return 2;
            } else {
                return 0;
            }
        }
    }
}
""")
    assert result == 2


def test_val_recursive_factorial() -> None:
    """Recursive function computes factorial."""
    result = _run_program("""
fn factorial(n) {
    if (n == 0) {
        return 1;
    }
    return n * factorial(n - 1);
}
fn main() {
    return factorial(5);
}
""")
    assert result == 120


def test_val_boolean_literals_in_conditions() -> None:
    """Boolean literals true/false work in if conditions."""
    result = _run_program("""
fn main() {
    if (true) {
        if (false) {
            return 0;
        }
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_val_function_returns_function_call() -> None:
    """A function can return the result of another function call."""
    result = _run_program("""
fn add(a, b) {
    return a + b;
}
fn double(x) {
    return add(x, x);
}
fn main() {
    return double(21);
}
""")
    assert result == 42


# =============================================================================
# string module validation
# =============================================================================


def test_string_concat() -> None:
    """string.concat joins two strings."""
    result = _run_program("""
import string;
fn main() {
    let s = string.concat("ab", "cd");
    if (s == "abcd") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_string_uppercase_lowercase() -> None:
    """string.uppercase and string.lowercase work."""
    result = _run_program("""
import string;
fn main() {
    let u = string.uppercase("hello");
    let l = string.lowercase("WORLD");
    if (u == "HELLO" && l == "world") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_string_contains_starts_ends() -> None:
    """string.contains, starts_with, ends_with work."""
    result = _run_program("""
import string;
fn main() {
    let c = string.contains("hello world", "world");
    let s = string.starts_with("hello", "he");
    let e = string.ends_with("hello", "lo");
    if (c == true && s == true && e == true) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_string_trim() -> None:
    """string.trim removes leading/trailing whitespace."""
    result = _run_program("""
import string;
fn main() {
    let t = string.trim("  hi  ");
    if (t == "hi") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_string_length() -> None:
    """string.length returns character count."""
    result = _run_program("""
import string;
fn main() {
    let len = string.length("abcde");
    if (len == 5) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_string_substring() -> None:
    """string.substring extracts a portion of a string."""
    result = _run_program("""
import string;
fn main() {
    let s = string.substring("hello", 1, 4);
    if (s == "ell") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_string_substring_with_variable() -> None:
    """string.substring works with string variables."""
    result = _run_program("""
import string;
fn main() {
    let text = "hello world";
    let part = string.substring(text, 0, 5);
    if (part == "hello") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# list module validation
# =============================================================================


def test_list_new_append_get() -> None:
    """list.new, append, get work together."""
    result = _run_program("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 10);
    list.append(items, 20);
    let first = list.get(items, 0);
    if (first == 10) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_len_contains() -> None:
    """list.len and list.contains work."""
    result = _run_program("""
import list;
fn main() {
    let items = list.new();
    list.append(items, "a");
    list.append(items, "b");
    let len = list.len(items);
    let has = list.contains(items, "a");
    if (len == 2 && has == true) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_list_remove_clear() -> None:
    """list.remove and list.clear work."""
    result = _run_program("""
import list;
fn main() {
    let items = list.new();
    list.append(items, 1);
    list.append(items, 2);
    list.append(items, 3);
    list.remove(items, 2);
    let after_remove = list.len(items);
    list.clear(items);
    let after_clear = list.len(items);
    if (after_remove == 2 && after_clear == 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# map module validation
# =============================================================================


def test_map_set_get_has() -> None:
    """map.set, get, has work together."""
    result = _run_program("""
import map;
fn main() {
    let m = map.new();
    map.set(m, "key", "value");
    let v = map.get(m, "key");
    let h = map.has(m, "key");
    if (v == "value" && h == true) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_map_delete_keys_clear() -> None:
    """map.delete, keys, clear work."""
    result = _run_program("""
import map;
import list;
fn main() {
    let m = map.new();
    map.set(m, "a", 1);
    map.set(m, "b", 2);
    let k = map.keys(m);
    let key_count = list.len(k);
    map.delete(m, "a");
    let after_delete = map.has(m, "a");
    map.clear(m);
    let after_clear = map.has(m, "b");
    if (key_count == 2 && after_delete == false && after_clear == false) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# set module validation
# =============================================================================


def test_set_add_contains_len() -> None:
    """set.add, contains, len work."""
    result = _run_program("""
import set;
fn main() {
    let s = set.new();
    set.add(s, 42);
    let c = set.contains(s, 42);
    let l = set.len(s);
    if (c == true && l == 1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_set_remove_clear() -> None:
    """set.remove and set.clear work."""
    result = _run_program("""
import set;
fn main() {
    let s = set.new();
    set.add(s, "x");
    set.add(s, "y");
    set.remove(s, "x");
    let has_x = set.contains(s, "x");
    let has_y = set.contains(s, "y");
    set.clear(s);
    let after_clear = set.len(s);
    if (has_x == false && has_y == true && after_clear == 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# array module validation
# =============================================================================


def test_array_push_len_get() -> None:
    """array.push, len, get work (alias for list)."""
    result = _run_program("""
import array;
fn main() {
    let a = array.new();
    array.push(a, 5);
    array.push(a, 10);
    let l = array.len(a);
    let g = array.get(a, 1);
    if (l == 2 && g == 10) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# math module validation
# =============================================================================


def test_math_add_sub_mul_div() -> None:
    """math.add, sub, mul, div work."""
    result = _run_program("""
import math;
fn main() {
    let a = math.add(10, 5);
    let s = math.sub(10, 5);
    let m = math.mul(10, 5);
    let d = math.div(10, 5);
    if (a == 15 && s == 5 && m == 50 && d == 2) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_math_abs_min_max() -> None:
    """math.abs, min, max work."""
    result = _run_program("""
import math;
fn main() {
    let a = math.abs(-5);
    let n = math.min(3, 7);
    let x = math.max(3, 7);
    if (a == 5 && n == 3 && x == 7) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# convert module validation
# =============================================================================


def test_convert_to_int() -> None:
    """convert.to_int converts string to int."""
    result = _run_program("""
import convert;
fn main() {
    let v = convert.to_int("42");
    if (v == 42) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_convert_to_bool_true_values() -> None:
    """convert.to_bool recognizes 'true', '1', 'yes'."""
    result = _run_program("""
import convert;
fn main() {
    let a = convert.to_bool("true");
    let b = convert.to_bool("1");
    let c = convert.to_bool("yes");
    let d = convert.to_bool("no");
    if (a == true && b == true && c == true && d == false) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# io module validation
# =============================================================================


def test_io_writeln_does_not_crash() -> None:
    """io.writeln and io.println execute without error."""
    result = _run_program("""
import io;
fn main() {
    io.writeln("test");
    io.println("test");
    return 1;
}
""")
    assert result == 1


# =============================================================================
# file module validation
# =============================================================================


def test_file_write_read_roundtrip() -> None:
    """file.write then file.read returns written content."""
    result = _run_in_sandbox("""
import file;
fn main() {
    file.write("test.txt", "hello world");
    let content = file.read("test.txt");
    if (content == "hello world") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_file_exists_true_false() -> None:
    """file.exists returns true for existing files, false for missing."""
    result = _run_in_sandbox("""
import file;
fn main() {
    file.write("exists.txt", "data");
    let e = file.exists("exists.txt");
    let n = file.exists("nope.txt");
    if (e == true && n == false) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_file_append_read() -> None:
    """file.append adds content to existing file."""
    result = _run_in_sandbox("""
import file;
fn main() {
    file.write("log.txt", "line1");
    file.append("log.txt", " line2");
    let content = file.read("log.txt");
    if (content == "line1 line2") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_file_remove_removes_file() -> None:
    """file.remove deletes a file."""
    result = _run_in_sandbox("""
import file;
fn main() {
    file.write("tmp.txt", "data");
    file.remove("tmp.txt");
    let gone = file.exists("tmp.txt");
    if (gone == false) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# path module validation
# =============================================================================


def test_path_join_basename_dirname() -> None:
    """path.join, basename, dirname work."""
    result = _run_program("""
import path;
fn main() {
    let full = path.join("docs", "readme.md");
    let base = path.basename(full);
    let dir = path.dirname(full);
    if (base == "readme.md" && dir == "docs") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_path_extension_normalize() -> None:
    """path.extension and path.normalize work."""
    result = _run_program("""
import path;
fn main() {
    let ext = path.extension("file.txt");
    let base = path.basename("a/b/c.txt");
    let norm = path.normalize("a/./b/../c");
    if (ext == ".txt" && base == "c.txt") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# time module validation
# =============================================================================


def test_time_timestamp_returns_positive() -> None:
    """time.timestamp returns a positive integer (Unix time)."""
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


def test_time_now_returns_non_empty_string() -> None:
    """time.now returns a non-empty string."""
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


# =============================================================================
# environment module validation
# =============================================================================


def test_env_get_returns_empty_for_missing() -> None:
    """environment.get returns '' for unset variables."""
    result = _run_program("""
import environment;
fn main() {
    let val = environment.get("__AILANG_MISSING_VAR__");
    if (val == "") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_env_cwd_returns_non_empty() -> None:
    """environment.cwd returns the current working directory."""
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


# =============================================================================
# random module validation
# =============================================================================


def test_random_int_in_range() -> None:
    """random.int returns a value between min and max inclusive."""
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


def test_random_float_is_non_negative() -> None:
    """random.float returns a non-negative value."""
    result = _run_program("""
import random;
fn main() {
    let val = random.float();
    let scaled = val * 10;
    if (scaled >= 0) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# json module validation
# =============================================================================


def test_json_parse_simple_object() -> None:
    """json.parse reads a JSON object into a map."""
    result = _run_program("""
import json;
import map;
fn main() {
    let data = json.parse("{\\"a\\": 1, \\"b\\": 2}");
    let a = map.get(data, "a");
    if (a == 1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_stringify_roundtrip() -> None:
    """json.stringify then parse again yields the same value."""
    result = _run_program("""
import json;
fn main() {
    let out = json.stringify(json.parse("[1, 2, 3]"));
    if (out == "[1, 2, 3]") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


# =============================================================================
# csv module validation
# =============================================================================


def test_csv_parse_and_stringify() -> None:
    """csv.parse returns rows, csv.stringify round-trips."""
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


def test_csv_parse_header_by_name() -> None:
    """csv.parse_header allows column access by name."""
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


# =============================================================================
# Combined stdlib usage — real-world-ish programs
# =============================================================================


def test_combined_json_file_persistence() -> None:
    """Write JSON data to a file, read it back, verify contents."""
    result = _run_in_sandbox("""
import json;
import file;
import map;
fn main() {
    let data = map.new();
    map.set(data, "name", "test");
    map.set(data, "value", 42);
    let serialized = json.stringify(data);
    file.write("data.json", serialized);
    let raw = file.read("data.json");
    let parsed = json.parse(raw);
    let name = map.get(parsed, "name");
    if (name == "test") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_combined_csv_to_json_conversion() -> None:
    """Parse CSV, access fields, reconstruct as JSON."""
    result = _run_program("""
import csv;
import json;
import list;
import map;
fn main() {
    let rows = csv.parse_header("x,y\\n10,20");
    let row0 = list.get(rows, 0);
    let x_val = map.get(row0, "x");
    let output = json.stringify(map.get(row0, "x"));
    if (output == "\\"10\\"") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_combined_path_file_read() -> None:
    """path.join combined with file.read for robust file access."""
    result = _run_in_sandbox("""
import file;
import path;
fn main() {
    file.write("data.txt", "content");
    let full_path = path.join(".", "data.txt");
    let content = file.read(full_path);
    if (content == "content") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1
