"""Tests for the JSON standard library module."""

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


def test_json_parse_string() -> None:
    """json.parse should parse a JSON string to an AILang string."""
    result = _run_program("""
import json;

fn main() {
    let val = json.parse("\\"hello\\"");
    if (val == "hello") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_parse_number() -> None:
    """json.parse should parse a JSON number to an AILang int."""
    result = _run_program("""
import json;

fn main() {
    let val = json.parse("42");
    if (val == 42) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_parse_float() -> None:
    """json.parse should parse a JSON float, verifiable via arithmetic."""
    result = _run_program("""
import json;

fn main() {
    let val = json.parse("3.14");
    let scaled = val * 100;
    if (scaled > 300) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_parse_true() -> None:
    """json.parse should parse 'true' to the AILang true literal."""
    result = _run_program("""
import json;

fn main() {
    let val = json.parse("true");
    if (val == true) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_parse_false() -> None:
    """json.parse should parse 'false' to the AILang false literal."""
    result = _run_program("""
import json;

fn main() {
    let val = json.parse("false");
    if (val == false) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_parse_null() -> None:
    """json.parse should parse 'null' to None, detectable via stringify."""
    result = _run_program("""
import json;

fn main() {
    let val = json.parse("null");
    if (json.stringify(val) == "null") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_parse_array() -> None:
    """json.parse should parse a JSON array to an AILang list."""
    result = _run_program("""
import json;
import list;

fn main() {
    let val = json.parse("[1, 2, 3]");
    let first = list.get(val, 0);
    if (first == 1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_parse_object() -> None:
    """json.parse should parse a JSON object to an AILang dict."""
    result = _run_program("""
import json;
import map;

fn main() {
    let val = json.parse("{\\"a\\": 1}");
    let a = map.get(val, "a");
    if (a == 1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_parse_nested() -> None:
    """json.parse should handle nested objects and arrays."""
    result = _run_program("""
import json;
import list;
import map;

fn main() {
    let val = json.parse("{\\"items\\": [{\\"x\\": 1}, {\\"x\\": 2}]}");
    let items = map.get(val, "items");
    let first = list.get(items, 0);
    let x = map.get(first, "x");
    if (x == 1) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_parse_invalid_returns_false() -> None:
    """Parsing invalid JSON should return false, not crash."""
    result = _run_program("""
import json;

fn main() {
    let val = json.parse("{invalid}");
    if (val == false) {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_stringify_int() -> None:
    """json.stringify should serialize an int to a JSON number string."""
    result = _run_program("""
import json;

fn main() {
    let out = json.stringify(42);
    if (out == "42") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_stringify_string() -> None:
    """json.stringify should serialize a string to a JSON string."""
    result = _run_program("""
import json;

fn main() {
    let out = json.stringify("hello");
    if (out == "\\"hello\\"") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_stringify_list() -> None:
    """json.stringify should serialize a list to a JSON array."""
    result = _run_program("""
import json;
import list;

fn main() {
    let lst = list.new();
    list.append(lst, 1);
    list.append(lst, 2);
    list.append(lst, 3);
    let out = json.stringify(lst);
    if (out == "[1, 2, 3]") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_stringify_map() -> None:
    """json.stringify should serialize a map to a JSON object."""
    result = _run_program("""
import json;
import map;

fn main() {
    let obj = map.new();
    map.set(obj, "a", 1);
    let out = json.stringify(obj);
    if (out == "{\\"a\\": 1}") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_stringify_set() -> None:
    """json.stringify should serialize a set to a JSON array."""
    result = _run_program("""
import json;
import set;

fn main() {
    let s = set.new();
    set.add(s, 42);
    let out = json.stringify(s);
    if (out == "[42]") {
        return 1;
    }
    return 0;
}
""")
    assert result == 1


def test_json_roundtrip() -> None:
    """Parse then stringify should produce equivalent JSON."""
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
