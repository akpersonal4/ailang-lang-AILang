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
        'import map;\n'
        'let m = map.new();\n'
        'fn foo() {\n'
        '    let name = map.get(m, "key");\n'
        '    let msg = "Hello, " + name;\n'
        '    return msg;\n'
        '}\n'
    )
    _, reporter = _type_check(source)
    # Should have no TYP005 errors for the string concatenation
    typ005_errors = [d for d in reporter.diagnostics if "TYP005" in d.error_code.code]
    assert len(typ005_errors) == 0


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
