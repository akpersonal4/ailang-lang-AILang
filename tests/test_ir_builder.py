"""Tests for the IR Builder, Validator and Printer (IR Builder v1)."""

from pathlib import Path

from compiler.ast.builder import ASTBuilder
from compiler.diagnostics import DiagnosticReporter
from compiler.ir import IRBuilder, IRPrinter, IRValidator
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable
from compiler.types.checker import TypeChecker


def _build_ir(source: str):
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source))
    cst = parser.parse_program()
    ast = ASTBuilder().build(cst)
    reporter = DiagnosticReporter()
    symbol_table = SymbolTable(reporter)
    SemanticAnalyzer(symbol_table).analyze(ast)
    TypeChecker(symbol_table, reporter).check(ast)
    ir = IRBuilder().build(ast)
    return ir


def test_ir_builder_and_printer_matches_golden(tmp_path: Path):
    source = "let x = 10; fn foo() { return x; }"
    ir = _build_ir(source)
    # Validate structure
    IRValidator().validate(ir)
    # Print IR
    printer = IRPrinter()
    output = printer.print(ir)
    # Write golden file for comparison (if not exists)
    golden_path = Path(__file__).parent / "golden" / "ir_program.txt"
    expected = golden_path.read_text(encoding="utf-8")
    assert output == expected
