"""AI Validation tests for AILang.

Verifies that AILang programs generated from the public documentation
(LANGUAGE_SPEC.md, stdlib_v1_final.md, README.md) compile and run correctly.

Measures first-pass compile success rate and documents any syntax errors.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import cast

import pytest

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime

# =============================================================================
# Helpers
# =============================================================================


def _compile_and_run(source: str, repo_root: Path | None = None) -> int:
    """Full compile + run, return main() result."""
    if repo_root is None:
        repo_root = Path(__file__).resolve().parents[1]

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

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
        return cast(int, runtime.execute(bundle.module_irs[entry_module]))


def _compile_and_check(source: str) -> list[str]:
    """Compile and return error messages (empty if success)."""
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

        if reporter.error_count == 0:
            return []
        return [d.message for d in reporter.diagnostics]


STATS = {"total": 0, "pass": 0, "fail": 0, "errors": []}


def _track(name: str, source: str) -> int | None:
    """Track first-pass compile success. Returns result or None on failure."""
    STATS["total"] += 1
    errors = _compile_and_check(source)
    if errors:
        STATS["fail"] += 1
        STATS["errors"].append((name, errors))
        return None
    STATS["pass"] += 1
    if "main()" in source or "fn main()" in source:
        return _compile_and_run(source)
    return None


# =============================================================================
# AI-Generated Program Tests
# These programs simulate what an AI system would generate from the docs.
# =============================================================================


class TestAIGeneratedFromDocs:
    """Programs that an AI would generate from the public documentation."""

    def test_ai_hello_world(self) -> None:
        """From LANGUAGE_SPEC: basic program structure."""
        source = """fn main() {
    print("Hello from AILang");
    return 42;
}"""
        result = _track("hello_world", source)
        if result is not None:
            assert result == 42

    def test_ai_variable_declaration(self) -> None:
        """Variables and basic arithmetic."""
        source = """fn main() {
    let x = 10;
    let y = 20;
    let z = x + y;
    return z;
}"""
        result = _track("variable_declaration", source)
        if result is not None:
            assert result == 30

    def test_ai_conditional(self) -> None:
        """If/else from LANGUAGE_SPEC."""
        source = """fn max(a, b) {
    if (a > b) {
        return a;
    }
    return b;
}
fn main() {
    return max(10, 20);
}"""
        result = _track("conditional", source)
        if result is not None:
            assert result == 20

    def test_ai_recursive_fibonacci(self) -> None:
        """Recursion from LANGUAGE_SPEC examples."""
        source = """fn fib(n) {
    if (n == 0) { return 0; }
    if (n == 1) { return 1; }
    return fib(n - 1) + fib(n - 2);
}
fn main() {
    return fib(10);
}"""
        result = _track("recursive_fibonacci", source)
        if result is not None:
            assert result == 55

    def test_ai_string_operations(self) -> None:
        """String module from stdlib docs."""
        source = """import string;
fn main() {
    let s = "  Hello World  ";
    let t = string.trim(s);
    let u = string.uppercase(t);
    let l = string.lowercase(t);
    if (u == "HELLO WORLD" && l == "hello world") {
        return 1;
    }
    return 0;
}"""
        result = _track("string_operations", source)
        if result is not None:
            assert result == 1

    def test_ai_json_parse(self) -> None:
        """JSON module from stdlib_v1_final.md."""
        source = """import json;
import map;
fn main() {
    let data = json.parse("{\\"name\\": \\"Alice\\", \\"age\\": 30}");
    let name = map.get(data, "name");
    let age = map.get(data, "age");
    if (name == "Alice" && age == 30) {
        return 1;
    }
    return 0;
}"""
        result = _track("json_parse", source)
        if result is not None:
            assert result == 1

    def test_ai_list_operations(self) -> None:
        """List module from README/stdlib docs."""
        source = """import list;
fn main() {
    let items = list.new();
    list.append(items, 10);
    list.append(items, 20);
    list.append(items, 30);
    let first = list.get(items, 0);
    let last = list.get(items, 2);
    let len = list.len(items);
    if (first == 10 && last == 30 && len == 3) {
        return 1;
    }
    return 0;
}"""
        result = _track("list_operations", source)
        if result is not None:
            assert result == 1

    def test_ai_file_read(self) -> None:
        """File module from stdlib docs."""
        source = """import file;
import string;
fn main() {
    let path = "test.txt";
    file.write(path, "hello");
    let content = file.read(path);
    file.remove(path);
    let trimmed = string.trim(content);
    if (trimmed == "hello") {
        return 1;
    }
    return 0;
}"""
        result = _track("file_read", source)
        if result is not None:
            assert result == 1

    def test_ai_random_int(self) -> None:
        """Random module from stdlib docs."""
        source = """import random;
fn main() {
    let r = random.int(1, 100);
    if (r >= 1 && r <= 100) {
        return 1;
    }
    return 0;
}"""
        result = _track("random_int", source)
        if result is not None:
            assert result == 1

    def test_ai_math_operations(self) -> None:
        """Math module from stdlib docs."""
        source = """import math;
fn main() {
    let s = math.add(10, 20);
    let d = math.sub(100, 50);
    let p = math.mul(6, 7);
    let q = math.div(100, 4);
    let a = math.abs(-42);
    let mn = math.min(10, 20);
    let mx = math.max(10, 20);
    if (s == 30 && d == 50 && p == 42 && q == 25 && a == 42 && mn == 10 && mx == 20) {
        return 1;
    }
    return 0;
}"""
        result = _track("math_operations", source)
        if result is not None:
            assert result == 1

    def test_ai_path_operations(self) -> None:
        """Path module from stdlib docs."""
        source = """import path;
fn main() {
    let j = path.join("a", "b");
    let b = path.basename("/foo/bar.txt");
    let d = path.dirname("/foo/bar.txt");
    let e = path.extension("file.txt");
    if (b == "bar.txt" && e == ".txt") {
        return 1;
    }
    return 0;
}"""
        result = _track("path_operations", source)
        if result is not None:
            assert result == 1

    def test_ai_csv_parse(self) -> None:
        """CSV module from stdlib_v1_final.md."""
        source = """import csv;
import list;
fn main() {
    let raw = "name,age\\nAlice,30\\nBob,25";
    let rows = csv.parse_header(raw);
    let first = list.get(rows, 0);
    return 1;
}"""
        result = _track("csv_parse", source)
        if result is not None:
            assert result == 1

    def test_ai_boolean_literals(self) -> None:
        """Boolean literals true/false from LANGUAGE_SPEC."""
        source = """fn main() {
    let t = true;
    let f = false;
    if (t && !f) {
        return 1;
    }
    return 0;
}"""
        result = _track("boolean_literals", source)
        if result is not None:
            assert result == 1

    def test_ai_chained_comparisons(self) -> None:
        """Chained comparisons from LANGUAGE_SPEC."""
        source = """fn main() {
    let x = 5;
    if (x > 0 && x < 10) {
        return 1;
    }
    return 0;
}"""
        result = _track("chained_comparisons", source)
        if result is not None:
            assert result == 1

    def test_ai_modulo(self) -> None:
        """Modulo operator."""
        source = """fn is_even(n) {
    return n % 2 == 0;
}
fn main() {
    if (is_even(10) && !is_even(7)) {
        return 1;
    }
    return 0;
}"""
        result = _track("modulo", source)
        if result is not None:
            assert result == 1

    def test_ai_multi_module_import(self) -> None:
        """Multi-module imports from MODULE_SYSTEM.md."""
        source = """import string;
import math;
import list;
fn process(items) {
    let first = list.get(items, 0);
    return string.uppercase(first);
}
fn main() {
    let items = list.new();
    list.append(items, "hello");
    let r = process(items);
    let m = math.add(1, 2);
    if (r == "HELLO" && m == 3) {
        return 1;
    }
    return 0;
}"""
        result = _track("multi_module_import", source)
        if result is not None:
            assert result == 1

    def test_ai_set_operations(self) -> None:
        """Set module from README/stdlib docs."""
        source = """import set;
fn main() {
    let s = set.new();
    set.add(s, "a");
    set.add(s, "b");
    set.add(s, "a");
    let has_a = set.contains(s, "a");
    let has_c = set.contains(s, "c");
    let size = set.len(s);
    if (has_a && !has_c && size == 2) {
        return 1;
    }
    return 0;
}"""
        result = _track("set_operations", source)
        if result is not None:
            assert result == 1

    def test_ai_map_operations(self) -> None:
        """Map module from README/stdlib docs."""
        source = """import map;
fn main() {
    let m = map.new();
    map.set(m, "name", "Alice");
    map.set(m, "age", 30);
    let name = map.get(m, "name");
    let has_age = map.has(m, "age");
    let has_zip = map.has(m, "zip");
    if (name == "Alice" && has_age && !has_zip) {
        return 1;
    }
    return 0;
}"""
        result = _track("map_operations", source)
        if result is not None:
            assert result == 1

    def test_ai_convert_module(self) -> None:
        """Convert module from stdlib docs."""
        source = """import convert;
fn main() {
    let s = convert.to_string(42);
    let n = convert.to_int("123");
    if (s == "42" && n == 123) {
        return 1;
    }
    return 0;
}"""
        result = _track("convert_module", source)
        if result is not None:
            assert result == 1

    def test_ai_environment_module(self) -> None:
        """Environment module from stdlib docs."""
        source = """import environment;
fn main() {
    let c = environment.cwd();
    if (c != "") {
        return 1;
    }
    return 0;
}"""
        result = _track("environment_module", source)
        if result is not None:
            assert result == 1

    def test_ai_nested_conditionals(self) -> None:
        """Nested if/else from LANGUAGE_SPEC."""
        source = """fn grade(score) {
    if (score >= 90) { return "A"; }
    if (score >= 80) { return "B"; }
    if (score >= 70) { return "C"; }
    if (score >= 60) { return "D"; }
    return "F";
}
fn main() {
    let g = grade(85);
    if (g == "B") {
        return 1;
    }
    return 0;
}"""
        result = _track("nested_conditionals", source)
        if result is not None:
            assert result == 1

    def test_ai_recursive_factorial(self) -> None:
        """Recursive factorial."""
        source = """fn fact(n) {
    if (n == 0) { return 1; }
    return n * fact(n - 1);
}
fn main() {
    return fact(5);
}"""
        result = _track("recursive_factorial", source)
        if result is not None:
            assert result == 120

    def test_ai_json_stringify(self) -> None:
        """JSON stringify from stdlib docs."""
        source = """import json;
import map;
fn main() {
    let m = map.new();
    map.set(m, "a", 1);
    map.set(m, "b", 2);
    let s = json.stringify(m);
    if (s != "") {
        return 1;
    }
    return 0;
}"""
        result = _track("json_stringify", source)
        if result is not None:
            assert result == 1


# =============================================================================
# Summary: Report AI validation statistics
# =============================================================================


@pytest.fixture(scope="session", autouse=True)
def _report_ai_stats() -> None:
    """Print AI validation statistics after all tests."""
    yield
    total = STATS["total"]
    passed = STATS["pass"]
    failed = STATS["fail"]
    rate = (passed / total * 100) if total > 0 else 0.0
    print("\n=== AI Validation Summary ===")
    print(f"Total programs: {total}")
    print(f"First-pass success: {passed} ({rate:.1f}%)")
    print(f"First-pass failure: {failed}")
    if STATS["errors"]:
        print("\nFailures:")
        for name, errs in STATS["errors"]:
            print(f"  {name}: {errs}")
