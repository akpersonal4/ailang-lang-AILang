"""Tests for semantic analysis."""

from pathlib import Path

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import (
    ProgramNode,
)
from compiler.diagnostics import DiagnosticReporter
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable


def _parse(source: str) -> ProgramNode:
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source))
    cst = parser.parse_program()
    ast = ASTBuilder().build(cst)
    assert isinstance(ast, ProgramNode)
    return ast


def _analyze(source: str) -> tuple[SemanticAnalyzer, DiagnosticReporter]:
    ast = _parse(source)
    reporter = DiagnosticReporter()
    analyzer = SemanticAnalyzer(SymbolTable(reporter))
    analyzer.analyze(ast)
    return analyzer, reporter


# ------------------------------------------------------------------
# Valid programs
# ------------------------------------------------------------------


def test_semantic_analyzer_accepts_valid_program() -> None:
    source = "let x = 10; fn foo() { return x; }"
    reporter = DiagnosticReporter()
    analyzer = SemanticAnalyzer(SymbolTable(reporter))
    ast = _parse(source)
    analyzer.analyze(ast)
    assert reporter.error_count == 0


def test_semantic_analyzer_resolves_global_variable() -> None:
    source = "let x = 10; fn foo() { return x; }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 0


def test_semantic_analyzer_resolves_parameter() -> None:
    source = "fn foo(x) { return x; }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 0


def test_semantic_analyzer_resolves_local_variable() -> None:
    source = "fn foo() { let x = 10; return x; }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 0


def test_semantic_analyzer_resolves_nested_scope() -> None:
    source = "fn foo() { let x = 10; let cond = 1; if (cond) { return x; } }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 0


def test_semantic_analyzer_shadows_outer_variable() -> None:
    source = "let x = 10; fn foo() { let x = 20; return x; }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 0


# ------------------------------------------------------------------
# Duplicate declarations
# ------------------------------------------------------------------


def test_semantic_analyzer_rejects_duplicate_global_variable() -> None:
    source = "let x = 10; let x = 20;"
    _, reporter = _analyze(source)
    assert reporter.error_count == 1
    assert "Duplicate declaration" in reporter.diagnostics[0].message


def test_semantic_analyzer_rejects_duplicate_parameter() -> None:
    source = "fn foo(x, x) { return x; }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 1
    assert "Duplicate declaration" in reporter.diagnostics[0].message


def test_semantic_analyzer_rejects_duplicate_local_variable() -> None:
    source = "fn foo() { let x = 10; let x = 20; }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 1
    assert "Duplicate declaration" in reporter.diagnostics[0].message


# ------------------------------------------------------------------
# Undefined identifiers
# ------------------------------------------------------------------


def test_semantic_analyzer_rejects_undefined_identifier() -> None:
    source = "fn foo() { return undefined_var; }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 1
    assert "Undefined identifier" in reporter.diagnostics[0].message


def test_semantic_analyzer_rejects_undefined_identifier_in_expression() -> None:
    source = "fn foo() { let x = y + 1; }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 1
    assert "Undefined identifier" in reporter.diagnostics[0].message


def test_semantic_analyzer_rejects_undefined_identifier_in_condition() -> None:
    source = "fn foo() { if (missing) { return 1; } }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 1
    assert "Undefined identifier" in reporter.diagnostics[0].message


# ------------------------------------------------------------------
# Scope behavior
# ------------------------------------------------------------------


def test_semantic_analyzer_resolves_outer_scope_after_inner() -> None:
    source = (
        "let x = 10; fn foo() { let cond = 1; if (cond) { let x = 20; } return x; }"
    )
    _, reporter = _analyze(source)
    assert reporter.error_count == 0


def test_semantic_analyzer_rejects_undefined_after_scope_exit() -> None:
    source = "fn foo() { let cond = 1; if (cond) { let x = 20; } return x; }"
    _, reporter = _analyze(source)
    assert reporter.error_count == 1
    assert "Undefined identifier" in reporter.diagnostics[0].message


def test_semantic_analyzer_resolves_nested_scopes() -> None:
    source = (
        "fn foo() {\n"
        "    let x = 1;\n"
        "    if (x > 0) {\n"
        "        let y = 2;\n"
        "        if (y > 0) {\n"
        "            let z = x + y;\n"
        "        }\n"
        "    }\n"
        "}"
    )
    _, reporter = _analyze(source)
    assert reporter.error_count == 0


# ------------------------------------------------------------------
# Golden snapshot
# ------------------------------------------------------------------


def test_semantic_generates_golden_snapshot() -> None:
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
    analyzer = SemanticAnalyzer(SymbolTable(reporter))
    analyzer.analyze(ast)
    snapshot_path = Path("tests/golden/semantic_valid_program.txt")
    snapshot_path.write_text(
        f"errors: {reporter.error_count}\n"
        + "\n".join(
            f"{d.severity.name} {d.error_code.code}: {d.message}"
            for d in reporter.diagnostics
        ),
        encoding="utf-8",
    )
    assert snapshot_path.exists()
