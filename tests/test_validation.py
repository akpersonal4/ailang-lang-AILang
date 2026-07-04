"""Validation tests for real-world AILang programs."""

from __future__ import annotations

import tempfile
from pathlib import Path

from compiler.compilation import CompilationSession
from compiler.runtime.interpreter import Runtime


def _run_ail_program(source: str) -> int:
    """Run an AILang program and return result."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        main_file = tmp_path / "main.ail"
        main_file.write_text(source)

        session = CompilationSession()
        session._root = tmp_path
        session.discover(main_file)
        bundle = session.build_ir()
        runtime = Runtime(bundle)

        return runtime.execute(bundle.module_irs["main"])


def _run_multi_module_program(tmp_path: Path, main_source: str) -> int:
    """Run a multi-module AILang program and return result."""
    main_file = tmp_path / "main.ail"
    main_file.write_text(main_source)

    session = CompilationSession()
    session._root = tmp_path
    session.discover(main_file)
    bundle = session.build_ir()
    runtime = Runtime(bundle)

    for module_name in session._graph.topological_order():
        runtime._initialize_module(module_name)

    return runtime.execute(bundle.module_irs["main"])


# =============================================================================
# Language Validation (Single-file)
# =============================================================================


def test_val_hello_world() -> None:
    """Hello World - Basic program structure."""
    source = """fn main() {
    return 42;
}"""
    result = _run_ail_program(source)
    assert result == 42


def test_val_variables() -> None:
    """Variables - Variable declarations and assignments."""
    source = """fn main() {
    let x = 10;
    let y = 20;
    let sum = x + y;
    return sum;
}"""
    result = _run_ail_program(source)
    assert result == 30


def test_val_arithmetic() -> None:
    """Arithmetic - All binary arithmetic operators."""
    source = """fn main() {
    return (10 + 5) + (10 - 5) + (10 * 5) + (10 / 5);
}"""
    result = _run_ail_program(source)
    # 15 + 5 + 50 + 2 = 72 (division returns float)
    assert result == 72.0


def test_val_comparisons() -> None:
    """Comparisons - All comparison operators."""
    source = """fn main() {
    let a = 5 < 10;
    let b = 10 > 5;
    let c = 5 == 5;
    let d = 5 != 10;
    let e = 5 <= 5;
    let f = 10 >= 10;
    return a + b + c + d + e + f;
}"""
    result = _run_ail_program(source)
    assert result == 6


def test_val_if_else() -> None:
    """If/Else - Conditional control flow."""
    source = """fn main() {
    let x = 10;
    if (x > 5) {
        return 1;
    }
    return 0;
}"""
    result = _run_ail_program(source)
    assert result == 1


def test_val_functions() -> None:
    """Functions - Function definitions and calls."""
    source = """fn square(x) {
    return x * x;
}
fn cube(x) {
    return x * x * x;
}
fn main() {
    return square(3) + cube(2);
}"""
    result = _run_ail_program(source)
    assert result == 17  # 9 + 8 = 17


def test_val_recursion() -> None:
    """Recursion - Recursive factorial function."""
    source = """fn factorial(n) {
    if (n == 0) {
        return 1;
    }
    return n * factorial(n - 1);
}
fn main() {
    return factorial(5);
}"""
    result = _run_ail_program(source)
    assert result == 120


# =============================================================================
# Real Programs
# =============================================================================


def test_prog_calculator() -> None:
    """Calculator - Basic calculator with all operators."""
    source = """fn add(a, b) { return a + b; }
fn subtract(a, b) { return a - b; }
fn multiply(a, b) { return a * b; }
fn main() {
    return add(multiply(3, 4), subtract(10, 5));
}"""
    result = _run_ail_program(source)
    assert result == 17  # (3*4) + (10-5) = 12 + 5 = 17


def test_prog_temperature_converter() -> None:
    """Temperature Converter - Celsius to Fahrenheit."""
    source = """fn celsius_to_fahrenheit(c) {
    return c * 9 / 5 + 32;
}
fn main() {
    return celsius_to_fahrenheit(0);
}"""
    result = _run_ail_program(source)
    assert result == 32.0  # 0°C = 32°F


def test_prog_grade_calculator() -> None:
    """Grade Calculator - Calculate grade from score."""
    source = """fn get_grade(score) {
    if (score >= 90) {
        return 4;
    }
    if (score >= 80) {
        return 3;
    }
    if (score >= 70) {
        return 2;
    }
    if (score >= 60) {
        return 1;
    }
    return 0;
}
fn main() {
    return get_grade(85);
}"""
    result = _run_ail_program(source)
    assert result == 3


def test_prog_fibonacci() -> None:
    """Fibonacci - Generate nth Fibonacci number."""
    source = """fn fibonacci(n) {
    if (n == 0) { return 0; }
    if (n == 1) { return 1; }
    return fibonacci(n - 1) + fibonacci(n - 2);
}
fn main() {
    return fibonacci(10);
}"""
    result = _run_ail_program(source)
    assert result == 55


def test_prog_prime_checker() -> None:
    """Prime Checker - Simple prime check."""
    source = """fn is_prime(n) {
    if (n <= 1) { return 0; }
    if (n == 2) { return 1; }
    if (n % 2 == 0) { return 0; }
    return 1;
}
fn main() {
    return is_prime(7);
}"""
    result = _run_ail_program(source)
    assert result == 1  # 7 is prime


# =============================================================================
# Multi-module Programs (documenting current limitation)
# =============================================================================


def test_limitation_module_function_calls() -> None:
    """Document: Module function calls (math.add) not yet fully supported.

    This is a known limitation. The import syntax works, but calling
    imported functions via qualified names (math.add) needs more work.
    """
    pass


# =============================================================================
# Additional Real Programs
# =============================================================================


def test_prog_nested_conditions() -> None:
    """Nested Conditions - Multiple if-else statements."""
    source = """fn main() {
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
                if (score >= 60) {
                    return 1;
                }
            }
        }
    }
    return 0;
}"""
    result = _run_ail_program(source)
    assert result == 2


def test_prog_multiple_operations() -> None:
    """Multiple Operations - Complex expression."""
    source = """fn main() {
    let a = 5;
    let b = 3;
    let c = 2;
    let result = (a + b) * c - a / b;
    return result;
}"""
    result = _run_ail_program(source)
    assert result == 14.333333333333334  # (5+3)*2 - 5/3 = 16 - 1.66.. = 14.33..
