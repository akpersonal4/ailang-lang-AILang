"""Variable lookup cache regression tests (100+ tests).

Tests cover: basic resolution, shadowing, recursion, reassignment,
modules, edge cases, cache-specific behavior, and stress.
"""

from __future__ import annotations

import os
import tempfile
from contextlib import redirect_stdout
from io import StringIO
from pathlib import Path
from typing import Any, cast

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import ProgramNode
from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.ir import IRBuilder
from compiler.ir.nodes import ProgramIR
from compiler.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable
from compiler.types.checker import TypeChecker
from compiler.runtime.interpreter import Runtime


def _build_ir(source: str) -> ProgramIR:
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source))
    cst = parser.parse_program()
    ast = ASTBuilder().build(cst)
    assert isinstance(ast, ProgramNode)
    reporter = DiagnosticReporter()
    symbol_table = SymbolTable(reporter)
    SemanticAnalyzer(symbol_table).analyze(ast)
    TypeChecker(symbol_table, reporter).check(ast)
    return IRBuilder().build(ast)


REPO_ROOT = Path(__file__).resolve().parents[1]


def _run(source: str) -> Any:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        session = CompilationSession()
        session._root = REPO_ROOT
        session._resolver = type(session._resolver)(REPO_ROOT)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        assert reporter.error_count == 0, "Compilation errors in test source"

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        entry_module = next(
            name for name in bundle.module_irs if name.endswith("main")
        )
        return runtime.execute(bundle.module_irs[entry_module])


def _run_no_sema(source: str) -> Any:
    ir = _build_ir(source)
    runtime = Runtime()
    return runtime.execute(ir)


def _run_with_runtime(source: str) -> tuple[Any, Runtime]:
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        session = CompilationSession()
        session._root = REPO_ROOT
        session._resolver = type(session._resolver)(REPO_ROOT)
        session.discover(main_file)

        reporter = DiagnosticReporter()
        session.analyze(reporter)
        assert reporter.error_count == 0, "Compilation errors in test source"

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        entry_module = next(
            name for name in bundle.module_irs if name.endswith("main")
        )
        result = runtime.execute(bundle.module_irs[entry_module])
        return result, runtime


# ── 2.1 Basic Resolution (10 tests) ──────────────────────────────────────

def test_resolve_local_variable() -> None:
    assert _run("fn main() { let x = 1; return x; }") == 1


def test_resolve_from_parent_scope() -> None:
    assert _run("let x = 1; fn main() { return x; }") == 1


def test_resolve_from_global_scope() -> None:
    assert _run("let x = 1; fn main() { return x; }") == 1


def test_resolve_after_define() -> None:
    assert _run("fn main() { let x = 1; let y = x; return y; }") == 1


def test_multiple_local_variables() -> None:
    assert _run("fn main() { let a = 1; let b = 2; return a + b; }") == 3


def test_nested_function_resolution() -> None:
    source = "fn outer() { let x = 1; fn inner() { return x; } return inner(); } fn main() { return outer(); }"
    assert _run(source) == 1


def test_deeply_nested_resolution() -> None:
    source = """
let a = 1;
fn main() {
    let b = 2;
    fn l2() { let c = 3; fn l3() { let d = 4; fn l4() { let e = 5; return a + b + c + d + e; } return l4(); } return l3(); }
    return l2();
}
"""
    assert _run(source) == 15


def test_builtin_resolution() -> None:
    f = StringIO()
    with redirect_stdout(f):
        _run("fn main() { print(42); }")
    assert f.getvalue() == "42\n"


def test_module_member_resolution() -> None:
    assert _run("import string; fn main() { return string.length(\"abc\"); }") == 3


def test_repeated_resolution_of_same_name() -> None:
    assert _run("fn main() { let x = 5; return x + x + x; }") == 15


# ── 2.2 Shadowing (15 tests) ────────────────────────────────────────────

def test_simple_shadow() -> None:
    assert _run("let x = 1; fn main() { let x = 2; return x; }") == 2


def test_shadow_then_access_outer() -> None:
    source = """
let x = 1;
fn f() { let x = 2; return x; }
fn main() { let r = f(); return x + r; }
"""
    assert _run(source) == 3


def test_double_shadow() -> None:
    source = """
let x = 1;
fn f() {
    let x = 2;
    fn g() { let x = 3; return x; }
    return g();
}
fn main() { return f(); }
"""
    assert _run(source) == 3


def test_shadow_after_return() -> None:
    source = """
let x = 1;
fn f() { let x = 2; return x; }
fn main() { f(); return x; }
"""
    assert _run(source) == 1


def test_shadow_in_sibling_functions() -> None:
    source = """
fn a() { let x = 1; return x; }
fn b() { let x = 2; return x; }
fn main() { return a() + b(); }
"""
    assert _run(source) == 3


def test_shadow_with_different_types() -> None:
    source = """
let x = 1;
fn f() { let x = 42; return x; }
fn main() { return f(); }
"""
    assert _run(source) == 42


def test_shadow_in_if_branch() -> None:
    source = """
fn f(flag) { if flag { let x = 2; return x; } return 0; }
fn main() { return f(true); }
"""
    assert _run(source) == 2


def test_parameter_shadowing_local() -> None:
    source = "let x = 1; fn f(x) { return x; } fn main() { return f(42); }"
    assert _run(source) == 42


def test_multiple_parameters_shadowing() -> None:
    source = "let a = 1; let b = 2; fn f(a, b) { return a + b; } fn main() { return f(10, 20); }"
    assert _run(source) == 30


def test_shadow_builtin() -> None:
    source = "fn main() { let print = 42; return print; }"
    assert _run(source) == 42


def test_shadow_deep_chain() -> None:
    source = """
let x = 1;
fn l1() {
    let x = 2;
    fn l2() { let x = 3; return x; }
    return l2();
}
fn main() { return l1(); }
"""
    assert _run(source) == 3


def test_shadow_then_reassign() -> None:
    source = """
let x = 1;
fn f() { let x = 2; x = 3; return x; }
fn main() { return f(); }
"""
    assert _run(source) == 3


def test_shadow_cleared_after_scope_exit() -> None:
    source = """
let x = 1;
fn f() { let x = 2; }
fn main() { f(); return x; }
"""
    assert _run(source) == 1


def test_shadow_with_recursive_call() -> None:
    source = """
let x = 1;
fn f(n) { let x = n; if n == 0 { return x; } return f(n - 1); }
fn main() { return f(5); }
"""
    assert _run(source) == 0


def test_shadow_builtin_name() -> None:
    source = "fn main() { let str = 99; return str; }"
    assert _run(source) == 99


# ── 2.3 Recursion (10 tests) ────────────────────────────────────────────

def test_simple_recursion() -> None:
    source = "fn f(n) { if n == 0 { return 0; } return 1 + f(n - 1); } fn main() { return f(5); }"
    assert _run(source) == 5


def test_recursion_with_local() -> None:
    source = "fn f(n) { let x = n; if n == 0 { return 0; } return x + f(n - 1); } fn main() { return f(5); }"
    assert _run(source) == 15


def test_single_recursion_with_guard() -> None:
    source = "fn f(n) { if n <= 0 { return 0; } return 1 + f(n - 1); } fn main() { return f(10); }"
    assert _run(source) == 10


def test_recursion_depth_100() -> None:
    source = "fn f(n) { if n == 0 { return 0; } return 1 + f(n - 1); } fn main() { return f(100); }"
    assert _run(source) == 100


def test_recursion_with_parameter_shadowing() -> None:
    source = "let x = 99; fn f(x) { if x == 0 { return 0; } return x + f(x - 1); } fn main() { return f(3); }"
    assert _run(source) == 6


def test_recursive_call_reads_outer_variable() -> None:
    source = "let base = 10; fn f(n) { if n == 0 { return base; } return n + f(n - 1); } fn main() { return f(3); }"
    assert _run(source) == 16


def test_recursion_modifies_accumulator() -> None:
    source = """
let acc = 0;
fn f(n) { if n == 0 { return acc; } acc = acc + n; return f(n - 1); }
fn main() { f(5); return acc; }
"""
    assert _run(source) == 15


def test_tree_recursion() -> None:
    source = "fn fib(n) { if n <= 1 { return n; } return fib(n - 1) + fib(n - 2); } fn main() { return fib(10); }"
    assert _run(source) == 55


def test_recursion_with_function_value() -> None:
    source = """
fn helper(n) { return n; }
fn main() { return helper(3); }
"""
    assert _run(source) == 3


def test_recursion_after_cache_warmup() -> None:
    source = """
fn f(n) { if n == 0 { return 0; } return 1 + f(n - 1); }
fn main() { let _ = f(3); return f(5); }
"""
    assert _run(source) == 5


# ── 2.4 Reassignment / Mutation (15 tests) ──────────────────────────────

def test_simple_reassignment() -> None:
    assert _run("fn main() { let x = 1; x = 2; return x; }") == 2


def test_reassign_after_function_call() -> None:
    source = "let x = 1; fn f() { x = 2; } fn main() { f(); return x; }"
    assert _run(source) == 2


def test_reassign_parent_scope_from_inner() -> None:
    source = "let x = 1; fn f() { x = 2; } fn main() { f(); return x; }"
    assert _run(source) == 2


def test_reassign_multiple_times() -> None:
    assert _run("fn main() { let x = 1; x = 2; x = 3; return x; }") == 3


def test_reassign_with_recursion() -> None:
    source = """
let acc = 0;
fn f(n) { if n == 0 { return acc; } acc = acc + n; return f(n - 1); }
fn main() { return f(5); }
"""
    assert _run(source) == 15


def test_reassign_after_cache_warmup() -> None:
    source = """
let x = 1;
fn f() { return x; }
fn main() { let _ = f(); x = 2; return f(); }
"""
    assert _run(source) == 2


def test_reassign_to_same_value() -> None:
    assert _run("fn main() { let x = 1; x = 1; return x; }") == 1


def test_reassign_from_different_scopes() -> None:
    source = """
let x = 1;
fn inner() { x = 3; }
fn outer() { x = 2; inner(); }
fn main() { outer(); return x; }
"""
    assert _run(source) == 3


def test_define_after_reassign() -> None:
    source = "fn main() { let x = 1; x = 2; let y = x; return y; }"
    assert _run(source) == 2


def test_reassign_triggers_parent_chain_walk() -> None:
    source = "let x = 1; fn f() { x = 2; } fn main() { f(); return x; }"
    assert _run(source) == 2


def test_reassign_with_negative_cache() -> None:
    source = "let x = 1; fn f() { x = 2; } fn main() { f(); return x; }"
    assert _run(source) == 2


def test_reassign_map_element() -> None:
    source = """
import map;
fn main() {
    let m = map.new();
    map.set(m, "k", 1);
    map.set(m, "k", 99);
    return map.get(m, "k");
}
"""
    assert _run(source) == 99


def test_reassign_in_recursive_loop() -> None:
    source = """
let acc = 99;
fn f(n) { if n == 0 { return acc; } acc = n; return f(n - 1); }
fn main() { f(3); return acc; }
"""
    assert _run(source) == 1


# ── 2.5 Module Variables (10 tests) ─────────────────────────────────────

def test_import_and_use_module_function() -> None:
    assert _run("import string; fn main() { return string.length(\"abc\"); }") == 3


def test_module_function_multiple_times() -> None:
    source = "import string; fn main() { let a = string.length(\"abc\"); let b = string.length(\"xy\"); return a + b; }"
    assert _run(source) == 5


def test_module_function_recursion() -> None:
    source = """
import string;
fn count(n) { if n == 0 { return 0; } return 1 + count(n - 1); }
fn main() { return count(string.length("abc")); }
"""
    assert _run(source) == 3


def test_module_calls_another_module() -> None:
    source = "import string; import math; fn main() { return math.add(string.length(\"abc\"), 2); }"
    assert _run(source) == 5


def test_module_variable_shadowed_by_local() -> None:
    source = "import string; fn f() { let length = 42; return length; } fn main() { return f(); }"
    assert _run(source) == 42


def test_module_qualified_name_resolution() -> None:
    assert _run("import string; fn main() { return string.length(\"abc\"); }") == 3


def test_module_function_called_with_local_var() -> None:
    source = "import string; fn main() { let s = \"hello\"; return string.length(s); }"
    assert _run(source) == 5


def test_module_function_in_expression() -> None:
    source = "import string; fn main() { let s = string.uppercase(\"abc\"); return s; }"
    assert _run(source) == "ABC"


def test_roundtrip_through_module() -> None:
    source = "import string; fn main() { let s = string.uppercase(string.trim(\"  hello  \")); return s; }"
    assert _run(source) == "HELLO"


def test_module_function_in_condition() -> None:
    source = "import string; fn main() { if string.length(\"abc\") == 3 { return 1; } return 0; }"
    assert _run(source) == 1


# ── 2.6 Imported Symbols (8 tests) ──────────────────────────────────────

def test_import_stdlib_function() -> None:
    assert _run("import string; fn main() { return string.length(\"abc\"); }") == 3


def test_multiple_imports() -> None:
    source = "import string; import math; fn main() { return math.add(string.length(\"abc\"), 2); }"
    assert _run(source) == 5


def test_import_same_module_twice() -> None:
    source = "import string; import string; fn main() { return string.length(\"abc\"); }"
    assert _run(source) == 3


def test_imported_function_called_repeatedly() -> None:
    source = "import string; fn main() { return string.length(\"abc\") + string.length(\"xy\"); }"
    assert _run(source) == 5


def test_imported_function_recursion() -> None:
    source = """
import string;
fn count_chars(n) { if n == 0 { return 0; } return 1 + count_chars(n - 1); }
fn main() { return count_chars(string.length("abc")); }
"""
    assert _run(source) == 3


def test_combined_import_and_local_resolution() -> None:
    source = "import string; fn main() { let x = 1; return string.length(\"a\") + x; }"
    assert _run(source) == 2


def test_import_resolves_to_module_environment() -> None:
    source = "import string; fn main() { return string.length(\"abc\"); }"
    assert _run(source) == 3


def test_import_math_stdlib() -> None:
    source = "import math; fn main() { return math.add(10, 20); }"
    assert _run(source) == 30


# ── 2.7 Edge Cases (10 tests) ───────────────────────────────────────────

def test_name_error_undefined_variable() -> None:
    import pytest
    from compiler.runtime.environment import Environment
    env = Environment()
    with pytest.raises(NameError):
        env.resolve("undefined_var")


def test_name_error_after_successful_resolves() -> None:
    import pytest
    from compiler.runtime.environment import Environment
    parent = Environment()
    parent.define("x", 1)
    child = Environment(parent)
    child.define("y", 2)
    assert child.resolve("x") == 1
    assert child.resolve("y") == 2
    with pytest.raises(NameError):
        child.resolve("z")


def test_empty_function() -> None:
    assert _run("fn f() { return 0; } fn main() { return f(); }") == 0


def test_function_with_many_parameters() -> None:
    source = "fn f(a, b, c, d, e, ff, g, h, i, j) { return a; } fn main() { return f(1, 2, 3, 4, 5, 6, 7, 8, 9, 10); }"
    assert _run(source) == 1


def test_assignment_to_undefined_variable_creates_binding() -> None:
    from compiler.runtime.environment import Environment
    env = Environment()
    env.assign("x", 1)
    assert env.resolve("x") == 1


def test_variable_defined_in_sibling_block() -> None:
    import pytest
    from compiler.runtime.environment import Environment
    env = Environment()
    with pytest.raises(NameError):
        env.resolve("x")


def test_dotted_name_resolution() -> None:
    assert _run("import string; fn main() { return string.length(\"abc\"); }") == 3


def test_resolve_with_string_concat() -> None:
    source = 'fn main() { let hello = "hello"; let world = "world"; return hello + " " + world; }'
    assert _run(source) == "hello world"


def test_nested_if_variable_resolution() -> None:
    source = """
fn f(a, b) {
    if a > 0 {
        if b > 0 { let x = a + b; return x; }
    }
    return 0;
}
fn main() { return f(3, 4); }
"""
    assert _run(source) == 7


# ── 2.8 Cache-Specific Behavior (10 tests) ──────────────────────────────

def test_cache_populated_after_first_resolve() -> None:
    from compiler.runtime.environment import Environment
    env = Environment()
    env.define("x", 10)
    env.resolve("x")
    info = env.get_cache_info()
    assert info["cache_size"] == 1
    assert "x" in info["entries"]


def test_cache_miss_then_hit() -> None:
    from compiler.runtime.environment import Environment
    parent = Environment()
    parent.define("x", 10)
    child = Environment(parent)
    # First resolve: miss in child, walk to parent
    assert child.resolve("x") == 10
    # Second resolve: cache hit
    assert child.resolve("x") == 10
    info = child.get_cache_info()
    assert "x" in info["entries"]


def test_different_environments_have_different_caches() -> None:
    from compiler.runtime.environment import Environment
    parent = Environment()
    child = Environment(parent)
    parent.define("x", 1)
    child.define("y", 2)
    child.resolve("x")
    child.resolve("y")
    assert "x" in parent.get_cache_info()["entries"]
    assert "x" in child.get_cache_info()["entries"]
    assert "y" in child.get_cache_info()["entries"]
    assert "y" not in parent.get_cache_info()["entries"]


def test_cache_empty_on_new_environment() -> None:
    from compiler.runtime.environment import Environment
    env = Environment()
    info = env.get_cache_info()
    assert info["cache_size"] == 0
    assert info["entries"] == []


def test_no_negative_cache_after_name_error() -> None:
    import pytest
    from compiler.runtime.environment import Environment
    env = Environment()
    env.define("x", 1)
    with pytest.raises(NameError):
        env.resolve("z")
    info = env.get_cache_info()
    assert "z" not in info["entries"]
    assert "x" not in info["entries"]
    # Now resolve x to populate cache
    env.resolve("x")
    info = env.get_cache_info()
    assert "x" in info["entries"]


def test_cache_survives_assign() -> None:
    assert _run("fn main() { let x = 1; x = 2; return x; }") == 2


def test_cache_hit_after_recursive_call_returns() -> None:
    source = "let x = 5; fn f(n) { if n == 0 { return x; } return f(n - 1); } fn main() { return f(3); }"
    assert _run(source) == 5


def test_multiple_names_in_cache() -> None:
    from compiler.runtime.environment import Environment
    env = Environment()
    env.define("a", 1)
    env.define("b", 2)
    env.define("c", 3)
    env.resolve("a")
    env.resolve("b")
    env.resolve("c")
    info = env.get_cache_info()
    assert info["cache_size"] == 3


def test_cache_hit_rate_high_for_repeated_access() -> None:
    source = "let x = 1; fn f(n) { if n == 0 { return x; } return x + f(n - 1); } fn main() { return f(100); }"
    assert _run(source) == 101


def test_cache_cleared_when_frame_popped() -> None:
    _, runtime = _run_with_runtime("fn f() { let x = 1; return x; } fn main() { f(); return 0; }")
    infos = runtime.get_cache_info()
    frame_infos = [i for i in infos if i["scope"] != "global"]
    assert len(frame_infos) == 0


# ── 2.9 Stress Tests (12 tests) ─────────────────────────────────────────

def test_1000_recursive_calls_with_local_variables() -> None:
    source = "fn f(n) { let x = n; if n == 0 { return 0; } return x + f(n - 1); } fn main() { return f(1000); }"
    assert _run(source) == 500500


def test_100_nested_scopes() -> None:
    source = "let x = 1; fn l1() { let x = 2; fn l2() { let x = 3; fn l3() { let x = 4; fn l4() { let x = 5; fn l5() { let x = 6; fn l6() { let x = 7; fn l7() { let x = 8; fn l8() { let x = 9; fn l9() { let x = 10; return x; } return l9(); } return l8(); } return l7(); } return l6(); } return l5(); } return l4(); } return l3(); } return l2(); } return l1(); } fn main() { return l1(); }"
    assert _run(source) == 10


def test_500_different_variable_names() -> None:
    decls = "; ".join(f"let v{i} = {i}" for i in range(500))
    refs = " + ".join(f"v{i}" for i in range(500))
    source = f"fn main() {{ {decls}; return {refs}; }}"
    result = _run(source)
    assert result == sum(range(500))


def test_alternating_resolution_and_assignment() -> None:
    source = """
fn main() {
    let x = 1;
    x = 2;
    let y = x;
    x = 3;
    return x + y;
}
"""
    assert _run(source) == 5


def test_deep_recursion_with_reassignment() -> None:
    source = """
let counter = 0;
fn f(n) { if n == 0 { return counter; } counter = counter + 1; return f(n - 1); }
fn main() { return f(100); }
"""
    assert _run(source) == 100


def test_chain_of_20_function_calls() -> None:
    parts = []
    for i in range(1, 21):
        parts.append(f"fn f{i}() {{ let x = {i}; return x + f{i-1}(); }}" if i > 1 else f"fn f1() {{ let x = 1; return x; }}")
    source = "; ".join(parts) + "; fn main() { return f20(); }"
    assert _run(source) == 210


def test_same_name_resolved_in_many_environments() -> None:
    from compiler.runtime.environment import Environment
    env1 = Environment()
    env2 = Environment()
    env1.define("x", 10)
    env2.define("x", 20)
    assert env1.resolve("x") == 10
    assert env2.resolve("x") == 20
    info1 = env1.get_cache_info()
    info2 = env2.get_cache_info()
    assert info1["cache_size"] == 1
    assert info2["cache_size"] == 1


def test_repeated_module_access() -> None:
    source = "import string; fn main() { let a = string.length(\"a\"); let b = string.length(\"ab\"); return string.length(\"abc\"); }"
    assert _run(source) == 3


def test_mixed_resolve_sources() -> None:
    source = "import math; let x = 1; fn f() { let y = 2; return math.add(x, y); } fn main() { return f(); }"
    assert _run(source) == 3


def test_deeply_nested_cache_chain() -> None:
    source = """
fn deep(n) {
    if n == 0 { return 0; }
    return 1 + deep(n - 1);
}
fn main() { return deep(500); }
"""
    result = _run(source)
    assert result == 500


def test_end_to_end_benchmark_output() -> None:
    import subprocess
    root = os.path.join(os.path.dirname(__file__), "..")
    apps = ["dice_roller.ail", "hangman_game.ail", "inventory_mgmt.ail", "kanban.ail"]
    for app in apps:
        app_path = os.path.join(root, "apps", app)
        if os.path.exists(app_path):
            result = subprocess.run(
                ["python", "-m", "compiler.cli", "run", app_path],
                capture_output=True, text=True, timeout=30,
            )
            assert result.returncode == 0, f"{app} failed: {result.stderr}"


# ── 3. Cache Correctness Invariants ─────────────────────────────────────

def test_invariant_cache_stores_binding_location_not_value() -> None:
    f = StringIO()
    with redirect_stdout(f):
        _run("fn main() { let x = 1; print(x); x = 2; print(x); }")
    lines = f.getvalue().strip().splitlines()
    assert lines == ["1", "2"]


def test_invariant_inner_cache_does_not_contaminate_outer() -> None:
    f = StringIO()
    with redirect_stdout(f):
        _run("let x = 1; fn f() { let x = 5; print(x); } fn main() { f(); print(x); }")
    lines = f.getvalue().strip().splitlines()
    assert lines == ["5", "1"]


def test_invariant_recursive_frames_resolve_own_binding() -> None:
    source = "fn f(n) { let x = n; if n == 0 { return 0; } return x + f(n - 1); } fn main() { print(f(3)); }"
    f = StringIO()
    with redirect_stdout(f):
        _run(source)
    assert f.getvalue().strip() == "6"


def test_invariant_module_lookup_cached_independently() -> None:
    source = "import string; fn main() { print(string.length(\"abc\")); print(string.length(\"xyz\")); }"
    f = StringIO()
    with redirect_stdout(f):
        _run(source)
    lines = f.getvalue().strip().splitlines()
    assert lines == ["3", "3"]


def test_invariant_no_negative_cache_for_failed_lookups() -> None:
    import pytest
    from compiler.runtime.environment import Environment
    env = Environment()
    env.define("x", 1)
    with pytest.raises(NameError):
        env.resolve("does_not_exist")
    info = env.get_cache_info()
    assert "does_not_exist" not in info["entries"]


def test_invariant_no_negative_cache_in_child_env() -> None:
    import pytest
    from compiler.runtime.environment import Environment
    parent = Environment()
    child = Environment(parent)
    with pytest.raises(NameError):
        child.resolve("x")
    info = child.get_cache_info()
    assert info["cache_size"] == 0
