"""Tests for type checking."""

from pathlib import Path

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import ProgramNode
from compiler.diagnostics import DiagnosticReporter
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable
from compiler.types.checker import TypeChecker


def _parse(source: str) -> ProgramNode:
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source))
    cst = parser.parse_program()
    ast = ASTBuilder().build(cst)
    assert isinstance(ast, ProgramNode)
    return ast


def _type_check(source: str) -> tuple[TypeChecker, DiagnosticReporter]:
    ast = _parse(source)
    reporter = DiagnosticReporter()
    symbol_table = SymbolTable(reporter)
    SemanticAnalyzer(symbol_table).analyze(ast)
    checker = TypeChecker(symbol_table, reporter)
    checker.check(ast)
    return checker, reporter


# ------------------------------------------------------------------
# Valid programs
# ------------------------------------------------------------------


def test_type_checker_accepts_valid_int_program() -> None:
    source = "let x = 10; fn foo() { return x; }"
    _, reporter = _type_check(source)
    assert reporter.error_count == 0


def test_type_checker_accepts_arithmetic() -> None:
    source = "fn foo() { let x = 1 + 2; return x; }"
    _, reporter = _type_check(source)
    assert reporter.error_count == 0


def test_type_checker_accepts_comparison() -> None:
    source = "fn foo() { let x = 1 < 2; }"
    _, reporter = _type_check(source)
    assert reporter.error_count == 0


# ------------------------------------------------------------------
# Type mismatch errors
# ------------------------------------------------------------------


def test_type_checker_rejects_return_type_mismatch() -> None:
    source = 'fn foo() { return "hello"; return 42; }'
    _, reporter = _type_check(source)
    assert reporter.error_count == 1
    assert "TYP003" in reporter.diagnostics[0].error_code.code


def test_type_checker_rejects_assignment_type_mismatch() -> None:
    source = 'fn foo() { let x = 1; x = "hello"; }'
    _, reporter = _type_check(source)
    assert reporter.error_count == 1
    assert "TYP008" in reporter.diagnostics[0].error_code.code


# ------------------------------------------------------------------
# Condition type checking
# ------------------------------------------------------------------


def test_type_checker_rejects_non_bool_condition() -> None:
    source = "fn foo() { let x = 1; if (x) { return 1; } }"
    _, reporter = _type_check(source)
    assert reporter.error_count == 1
    assert "TYP004" in reporter.diagnostics[0].error_code.code


# ------------------------------------------------------------------
# Unary operator type checking
# ------------------------------------------------------------------


# ------------------------------------------------------------------
# String concatenation with UnknownType
# ------------------------------------------------------------------


def test_type_checker_allows_string_concat_with_unknown() -> None:
    """String + unknown should return string, not error."""
    # map.get returns UnknownType; string + UnknownType should be allowed
    source = (
        "import map;\n"
        "let m = map.new();\n"
        "fn foo() {\n"
        '    let name = map.get(m, "key");\n'
        '    let msg = "Hello, " + name;\n'
        "    return msg;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    # Should have no TYP005 errors for the string concatenation
    typ005_errors = [d for d in reporter.diagnostics if "TYP005" in d.error_code.code]
    assert len(typ005_errors) == 0


# ------------------------------------------------------------------
# Arithmetic with UnknownType (M76.1 fix)
# ------------------------------------------------------------------


def test_type_checker_allows_unknown_plus_int() -> None:
    """UnknownType + INT_TYPE should infer to INT_TYPE.

    This enables natural patterns like map.get(m, "qty") + 1
    without requiring explicit initialization workarounds.
    """
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let total = qty + 1;\n"
        "    return total;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    # Should have no TYP001 errors for the arithmetic with unknown
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_int_plus_unknown() -> None:
    """INT_TYPE + UnknownType should infer to INT_TYPE."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let total = 1 + qty;\n"
        "    return total;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_unknown_minus_int() -> None:
    """UnknownType - INT_TYPE should infer to INT_TYPE."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let left = qty - 1;\n"
        "    return left;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_unknown_mul_int() -> None:
    """UnknownType * INT_TYPE should infer to INT_TYPE."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let total = qty * 2;\n"
        "    return total;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_unknown_div_int() -> None:
    """UnknownType / INT_TYPE should infer to FLOAT_TYPE (division returns float)."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let avg = qty / 2;\n"
        "    return avg;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_unknown_mod_int() -> None:
    """UnknownType % INT_TYPE should infer to INT_TYPE."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let rem = qty % 3;\n"
        "    return rem;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_unknown_float_arithmetic() -> None:
    """UnknownType + FLOAT_TYPE should infer to FLOAT_TYPE."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let total = qty + 1.5;\n"
        "    return total;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


# ------------------------------------------------------------------
# Arithmetic with UnknownType - INT on left (M76.1 fix)
# ------------------------------------------------------------------


def test_type_checker_allows_int_minus_unknown() -> None:
    """INT_TYPE - UnknownType should infer to INT_TYPE."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let diff = 10 - qty;\n"
        "    return diff;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_int_mul_unknown() -> None:
    """INT_TYPE * UnknownType should infer to INT_TYPE."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let product = 2 * qty;\n"
        "    return product;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_int_div_unknown() -> None:
    """INT_TYPE / UnknownType should infer to FLOAT_TYPE (division returns float)."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let avg = 10 / qty;\n"
        "    return avg;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_int_mod_unknown() -> None:
    """INT_TYPE % UnknownType should infer to INT_TYPE."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let qty = map.get(m, "key");\n'
        "    let rem = 10 % qty;\n"
        "    return rem;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


# ------------------------------------------------------------------
# Source-diverse UnknownType arithmetic (M76.1 fix)
# ------------------------------------------------------------------


def test_type_checker_allows_json_parse_arithmetic() -> None:
    """UnknownType from json.parse should support arithmetic operations."""
    source = (
        "import json;\n"
        "import map;\n"
        "fn foo() {\n"
        '    let data = json.parse("{\\"count\\": 5}");\n'
        '    let count = map.get(data, "count") + 1;\n'
        "    return count;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_unknown_function_arithmetic() -> None:
    """UnknownType from unknown function should support arithmetic operations."""
    source = (
        "fn get_value() { return 42; }\n"
        "fn foo() {\n"
        "    let val = get_value() + 1;\n"
        "    return val;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


def test_type_checker_allows_module_fn_arithmetic() -> None:
    """UnknownType from module function should support arithmetic operations."""
    source = (
        "import math;\n"
        "fn foo() {\n"
        "    let result = math.add(1, 2) + 1;\n"
        "    return result;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ001_errors = [d for d in reporter.diagnostics if "TYP001" in d.error_code.code]
    assert len(typ001_errors) == 0, f"Unexpected TYP001: {typ001_errors}"


# ------------------------------------------------------------------
# M76.2A — UnknownType + UnknownType arithmetic (NumericUnknownType)
# ------------------------------------------------------------------


def test_type_checker_allows_unknown_plus_unknown() -> None:
    """UnknownType + UnknownType should infer to NumericUnknownType.

    This enables the Developer #3 pattern without 0-initialization:
        map.get(a) + map.get(b)
    """
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let a = map.get(m, "x");\n'
        '    let b = map.get(m, "y");\n'
        "    let total = a + b;\n"
        "    return total;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ_errors = [
        d for d in reporter.diagnostics if d.error_code.code.startswith("TYP")
    ]
    assert len(typ_errors) == 0, f"Unexpected type errors: {typ_errors}"


def test_type_checker_allows_unknown_mul_unknown() -> None:
    """UnknownType * UnknownType should not error (NumericUnknownType)."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let price = map.get(m, "price");\n'
        '    let qty = map.get(m, "qty");\n'
        "    let line_total = price * qty;\n"
        "    return line_total;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ_errors = [
        d for d in reporter.diagnostics if d.error_code.code.startswith("TYP")
    ]
    assert len(typ_errors) == 0, f"Unexpected type errors: {typ_errors}"


def test_type_checker_allows_unknown_function_arithmetic_both_sides() -> None:
    """unknown_fn() + unknown_fn() should not error."""
    source = (
        "fn get_value() {\n"
        "    return 42;\n"
        "}\n"
        "fn foo() {\n"
        "    let a = get_value();\n"
        "    let b = get_value();\n"
        "    let result = a + b;\n"
        "    return result;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ_errors = [
        d for d in reporter.diagnostics if d.error_code.code.startswith("TYP")
    ]
    assert len(typ_errors) == 0, f"Unexpected type errors: {typ_errors}"


def test_type_checker_allows_accumulator_plus_expression() -> None:
    """Accumulator pattern: recursive accumulator + unknown expression."""
    source = (
        "import map;\n"
        "fn sum_values(m, keys, idx, acc) {\n"
        "    if (idx >= list.len(keys)) {\n"
        "        return acc;\n"
        "    }\n"
        "    let key = list.get(keys, idx);\n"
        "    let val = map.get(m, key);\n"
        "    let new_acc = acc + val;\n"
        "    return sum_values(m, keys, idx + 1, new_acc);\n"
        "}\n"
        "fn main() {\n"
        "    let m = map.new();\n"
        "    let keys = list.new();\n"
        "    let result = sum_values(m, keys, 0, 0);\n"
        "    return result;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ_errors = [
        d for d in reporter.diagnostics if d.error_code.code.startswith("TYP")
    ]
    assert len(typ_errors) == 0, f"Unexpected type errors: {typ_errors}"


def test_type_checker_numeric_unknown_sub() -> None:
    """UnknownType - UnknownType should not error."""
    source = (
        "import map;\n"
        "fn foo() {\n"
        "    let m = map.new();\n"
        '    let a = map.get(m, "x");\n'
        '    let b = map.get(m, "y");\n'
        "    let diff = a - b;\n"
        "    return diff;\n"
        "}\n"
    )
    _, reporter = _type_check(source)
    typ_errors = [
        d for d in reporter.diagnostics if d.error_code.code.startswith("TYP")
    ]
    assert len(typ_errors) == 0, f"Unexpected type errors: {typ_errors}"


# ------------------------------------------------------------------
# Golden snapshot
# ------------------------------------------------------------------


def test_type_checker_generates_golden_snapshot() -> None:
    source = (
        "let x = 10;\n"
        "fn add(a, b) {\n"
        "    return a + b;\n"
        "}\n"
        "if (x > 0) {\n"
        "    return x;\n"
        "} else {\n"
        "    return 0 - x;\n"
        "}\n"
    )
    ast = _parse(source)
    reporter = DiagnosticReporter()
    symbol_table = SymbolTable(reporter)
    SemanticAnalyzer(symbol_table).analyze(ast)
    checker = TypeChecker(symbol_table, reporter)
    checker.check(ast)
    snapshot_path = Path("tests/golden/type_checker_valid_program.txt")
    snapshot_path.write_text(
        f"errors: {reporter.error_count}\n"
        + "\n".join(
            f"{d.severity.name} {d.error_code.code}: {d.message}"
            for d in reporter.diagnostics
        ),
        encoding="utf-8",
    )
    assert snapshot_path.exists()
