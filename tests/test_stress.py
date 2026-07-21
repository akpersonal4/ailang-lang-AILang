"""Stress tests for AILang compiler and runtime.

Tests compiler stability with large programs, deep recursion,
many function definitions, multi-module projects, and edge cases.
"""

from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.diagnostics import DiagnosticReporter
from compiler.runtime.interpreter import Runtime

# Increase recursion limit for deep recursion / large call-chain stress tests.
# The interpreter uses recursive calls for both name resolution and execution,
# so chain depths beyond ~300 hit Python's default limit of 1000.
sys.setrecursionlimit(5000)


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
        assert reporter.error_count == 0

        bundle = session.build_ir()
        runtime = Runtime(bundle)
        for module_name in session._graph.topological_sort():
            runtime._initialize_module(module_name)

        entry_module = next(name for name in bundle.module_irs if name.endswith("main"))
        return int(runtime.execute(bundle.module_irs[entry_module]))


def _generate_large_program(num_functions: int) -> str:
    """Generate a program with num_functions helper functions.

    Functions are defined in reverse order so each call refers to an
    already-defined function, avoiding forward-reference diagnostics.
    fn_0 calls fn_1, fn_1 calls fn_2, ..., fn_{N-1} returns 42.
    main() calls fn_0 which chains through all functions.
    """
    lines: list[str] = []
    for i in range(num_functions - 1, -1, -1):
        if i == num_functions - 1:
            next_call = "42"
        else:
            next_call = f"fn_{i + 1}()"
        lines.append(f"fn fn_{i}() {{ return {next_call}; }}")
    lines.append("fn main() { return fn_0(); }")
    return "\n".join(lines)


def _generate_deep_nesting(depth: int) -> str:
    """Generate a program with deeply nested if statements."""
    lines: list[str] = []
    lines.append("fn main() {")
    lines.append("    let x = 1;")
    current_indent = "    "
    for _i in range(depth):
        lines.append(f"{current_indent}if (x == 1) {{")
        current_indent += "    "
    lines.append(f"{current_indent}return 1;")
    for _i in range(depth):
        current_indent = current_indent[:-4]
        lines.append(f"{current_indent}}}")
    lines.append("}")
    return "\n".join(lines)


# =============================================================================
# Large Single-File Programs
# =============================================================================


class TestLargeSingleFile:
    """Compiler handles programs with many functions and deep call chains."""

    def test_100_functions(self) -> None:
        """100 function definitions with a call chain of 100."""
        source = _generate_large_program(100)
        result = _compile_and_run(source)
        assert result == 42

    def test_200_functions(self) -> None:
        """200 function definitions with a call chain of 200."""
        source = _generate_large_program(200)
        result = _compile_and_run(source)
        assert result == 42

    def test_deep_nesting_50(self) -> None:
        """50 levels of nested if statements compile and run correctly."""
        source = _generate_deep_nesting(50)
        result = _compile_and_run(source)
        assert result == 1

    def test_deep_nesting_100(self) -> None:
        """100 levels of nested if statements compile and run correctly."""
        source = _generate_deep_nesting(100)
        result = _compile_and_run(source)
        assert result == 1


# =============================================================================
# Deep Recursion
# =============================================================================


class TestDeepRecursion:
    """Runtime handles deep recursive calls."""

    def test_recursion_depth_500(self) -> None:
        """Recursive function with depth 500 completes."""
        source = """
fn count(n) {
    if (n == 0) {
        return 0;
    }
    return count(n - 1);
}
fn main() {
    return count(500);
}
"""
        result = _compile_and_run(source)
        assert result == 0

    def test_recursive_sum_200(self) -> None:
        """Recursive sum to 200 completes."""
        source = """
fn sum(n) {
    if (n == 0) {
        return 0;
    }
    return n + sum(n - 1);
}
fn main() {
    return sum(200);
}
"""
        result = _compile_and_run(source)
        assert result == 20100

    def test_deep_fibonacci_20(self) -> None:
        """Fibonacci(20) via double recursion."""
        source = """
fn fib(n) {
    if (n <= 1) {
        return n;
    }
    return fib(n - 1) + fib(n - 2);
}
fn main() {
    return fib(20);
}
"""
        result = _compile_and_run(source)
        assert result == 6765


# =============================================================================
# Multi-Module Stress Tests
# =============================================================================


def _build_multi_module_project(tmp_path: Path, num_modules: int) -> Path:
    """Create a multi-module project with num_modules interdependent files.

    Module structure:
      mod_0 -> depends on mod_1 -> depends on mod_2 -> ... -> mod_N
      Each module defines fn get_value() that returns its index.
      The last module returns 42 regardless.
    """
    for i in range(num_modules, 0, -1):
        if i == num_modules:
            content = "fn get_value() {\n" "    return 42;\n" "}\n"
        else:
            content = (
                f"import mod_{i + 1};\n"
                "fn get_value() {\n"
                f"    return mod_{i + 1}.get_value();\n"
                "}\n"
            )
        mod_file = tmp_path / f"mod_{i}.ail"
        mod_file.write_text(content)

    main_content = (
        "import mod_1;\n" "fn main() {\n" "    return mod_1.get_value();\n" "}\n"
    )
    main_file = tmp_path / "main.ail"
    main_file.write_text(main_content)
    return main_file


class TestMultiModuleStress:
    """Compiler handles multi-module projects with deep dependency chains."""

    def test_10_modules(self) -> None:
        """10 modules with a dependency chain length of 10."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            main_file = _build_multi_module_project(tmp_path, 10)

            session = CompilationSession()
            session._root = tmp_path
            session._resolver = type(session._resolver)(tmp_path)
            session.discover(main_file)

            reporter = DiagnosticReporter()
            session.analyze(reporter)
            assert reporter.error_count == 0

            bundle = session.build_ir()
            runtime = Runtime(bundle)
            for module_name in session._graph.topological_sort():
                runtime._initialize_module(module_name)

            result = int(runtime.execute(bundle.module_irs["main"]))
            assert result == 42

    def test_20_modules(self) -> None:
        """20 modules with a dependency chain length of 20."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            main_file = _build_multi_module_project(tmp_path, 20)

            session = CompilationSession()
            session._root = tmp_path
            session._resolver = type(session._resolver)(tmp_path)
            session.discover(main_file)

            reporter = DiagnosticReporter()
            session.analyze(reporter)
            assert reporter.error_count == 0

            bundle = session.build_ir()
            runtime = Runtime(bundle)
            for module_name in session._graph.topological_sort():
                runtime._initialize_module(module_name)

            result = int(runtime.execute(bundle.module_irs["main"]))
            assert result == 42

    def test_50_modules(self) -> None:
        """50 modules with a dependency chain length of 50."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            main_file = _build_multi_module_project(tmp_path, 50)

            session = CompilationSession()
            session._root = tmp_path
            session._resolver = type(session._resolver)(tmp_path)
            session.discover(main_file)

            reporter = DiagnosticReporter()
            session.analyze(reporter)
            assert reporter.error_count == 0

            bundle = session.build_ir()
            runtime = Runtime(bundle)
            for module_name in session._graph.topological_sort():
                runtime._initialize_module(module_name)

            result = int(runtime.execute(bundle.module_irs["main"]))
            assert result == 42

    def test_100_modules(self) -> None:
        """100 modules with a dependency chain length of 100."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            main_file = _build_multi_module_project(tmp_path, 100)

            session = CompilationSession()
            session._root = tmp_path
            session._resolver = type(session._resolver)(tmp_path)
            session.discover(main_file)

            reporter = DiagnosticReporter()
            session.analyze(reporter)
            assert reporter.error_count == 0

            bundle = session.build_ir()
            runtime = Runtime(bundle)
            for module_name in session._graph.topological_sort():
                runtime._initialize_module(module_name)

            result = int(runtime.execute(bundle.module_irs["main"]))
            assert result == 42


# =============================================================================
# Compiler Edge Cases
# =============================================================================


class TestCompilerEdgeCases:
    """Edge cases for the compiler pipeline."""

    def test_empty_function(self) -> None:
        """Calling a function with an empty body does not crash."""
        source = """
fn empty() {}
fn main() {
    empty();
    return 1;
}
"""
        result = _compile_and_run(source)
        assert result == 1

    def test_boolean_in_arithmetic(self) -> None:
        """Boolean values in arithmetic: true=1, false=0."""
        source = """
fn main() {
    let x = true + true + false;
    if (x == 2) {
        return 1;
    }
    return 0;
}
"""
        result = _compile_and_run(source)
        assert result == 1

    def test_modulo_operator(self) -> None:
        """Modulo operator works correctly."""
        source = """
fn main() {
    let r = 17 % 5;
    if (r == 2) {
        return 1;
    }
    return 0;
}
"""
        result = _compile_and_run(source)
        assert result == 1

    def test_negation_operator(self) -> None:
        """Unary negation works."""
        source = """
fn main() {
    let x = -42;
    if (x == -42) {
        return 1;
    }
    return 0;
}
"""
        result = _compile_and_run(source)
        assert result == 1

    def test_logical_not(self) -> None:
        """Logical NOT (!) works."""
        source = """
fn main() {
    if (!false) {
        if (!(true == false)) {
            return 1;
        }
    }
    return 0;
}
"""
        result = _compile_and_run(source)
        assert result == 1

    def test_multiple_parameters(self) -> None:
        """Functions with multiple parameters work."""
        source = """
fn sum4(a, b, c, d) {
    return a + b + c + d;
}
fn main() {
    let r = sum4(1, 2, 3, 4);
    if (r == 10) {
        return 1;
    }
    return 0;
}
"""
        result = _compile_and_run(source)
        assert result == 1

    def test_chained_comparisons(self) -> None:
        """Chained comparisons using &&."""
        source = """
fn main() {
    let x = 5;
    if (x > 0 && x < 10) {
        if (x >= 5 && x <= 5) {
            return 1;
        }
    }
    return 0;
}
"""
        result = _compile_and_run(source)
        assert result == 1

    def test_function_as_variable_value(self) -> None:
        """A function can return another function's result via variable."""
        source = """
fn get_val() {
    return 42;
}
fn main() {
    let f = get_val();
    return f;
}
"""
        result = _compile_and_run(source)
        assert result == 42

    def test_deep_binary_expression_tree(self) -> None:
        """Deeply nested binary expression evaluates correctly."""
        source = """
fn main() {
    let r = (((((1 + 2) + 3) + 4) + 5) + 6);
    if (r == 21) {
        return 1;
    }
    return 0;
}
"""
        result = _compile_and_run(source)
        assert result == 1

    def test_string_escape_sequences(self) -> None:
        """String literals with escape sequences."""
        source = """
fn main() {
    let s = "hello\\nworld\\ttab";
    if (s != "") {
        return 1;
    }
    return 0;
}
"""
        result = _compile_and_run(source)
        assert result == 1


# =============================================================================
# Large LOC Stress Tests
# =============================================================================


class TestLargeLOC:
    """Compiler handles programs with 500+ and 1000+ LOC."""

    def test_100_loc_program(self) -> None:
        """Generate and run a ~100 LOC program."""
        lines = ["fn main() {"]
        for i in range(80):
            lines.append(f"    let x{i} = {i};")
        lines.append("    return 1;")
        lines.append("}")
        source = "\n".join(lines)
        result = _compile_and_run(source)
        assert result == 1

    def test_500_loc_program(self) -> None:
        """Generate and run a ~500 LOC program."""
        lines = ["fn main() {"]
        for i in range(480):
            lines.append(f"    let x{i} = {i};")
        lines.append("    return 1;")
        lines.append("}")
        source = "\n".join(lines)
        result = _compile_and_run(source)
        assert result == 1

    def test_1000_loc_program(self) -> None:
        """Generate and run a ~1000 LOC program."""
        lines = ["fn main() {"]
        for i in range(980):
            lines.append(f"    let x{i} = {i};")
        lines.append("    return 1;")
        lines.append("}")
        source = "\n".join(lines)
        result = _compile_and_run(source)
        assert result == 1

    def test_5000_loc_program(self) -> None:
        """Generate and run a ~5000 LOC program."""
        lines = ["fn main() {"]
        for i in range(4980):
            lines.append(f"    let x{i} = {i};")
        lines.append("    return 1;")
        lines.append("}")
        source = "\n".join(lines)
        result = _compile_and_run(source)
        assert result == 1

    def test_10000_loc_program(self) -> None:
        """Generate and run a ~10000 LOC program."""
        lines = ["fn main() {"]
        for i in range(9980):
            lines.append(f"    let x{i} = {i};")
        lines.append("    return 1;")
        lines.append("}")
        source = "\n".join(lines)
        result = _compile_and_run(source)
        assert result == 1


# =============================================================================
# Regression: Edge Cases That Previously Failed
# =============================================================================


def test_regression_unary_minus_in_expression() -> None:
    """Unary minus in a larger expression."""
    source = """
fn main() {
    let x = -5 + 10;
    if (x == 5) {
        return 1;
    }
    return 0;
}
"""
    result = _compile_and_run(source)
    assert result == 1


def test_regression_nested_function_calls() -> None:
    """Nested function calls in expressions."""
    source = """
fn add(a, b) { return a + b; }
fn mul(a, b) { return a * b; }
fn main() {
    let r = mul(add(2, 3), add(4, 5));
    if (r == 45) {
        return 1;
    }
    return 0;
}
"""
    result = _compile_and_run(source)
    assert result == 1
