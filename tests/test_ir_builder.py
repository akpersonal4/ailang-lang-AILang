"""Tests for the IR Builder, Validator, and Printer (IR Builder v1)."""

from pathlib import Path

import pytest

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import ProgramNode
from compiler.diagnostics import DiagnosticReporter
from compiler.ir import (
    AssignmentIR,
    BinaryOperationIR,
    BlockIR,
    CallIR,
    ExpressionStatementIR,
    FunctionIR,
    IfIR,
    IRBuilder,
    IRPrinter,
    IRValidationError,
    IRValidator,
    LiteralIR,
    ProgramIR,
    UnaryOperationIR,
    VariableDeclarationIR,
    VariableReferenceIR,
)
from compiler.lexer import Lexer
from compiler.parser.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable
from compiler.types.checker import TypeChecker


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
    ir = IRBuilder().build(ast)
    return ir


def test_ir_builder_and_printer_matches_golden() -> None:
    source = "let x = 10; fn foo() { return x; }"
    ir = _build_ir(source)
    # Validate structure
    IRValidator().validate(ir)
    # Print IR
    printer = IRPrinter()
    output = printer.print(ir)
    # Write golden file for comparison
    golden_path = Path(__file__).parent / "golden" / "ir_program.txt"
    expected = golden_path.read_text(encoding="utf-8")
    assert output == expected


def test_ir_builder_lowers_binary_and_unary_operations() -> None:
    source = "fn main() { let a = 1 + 2 * 3; let b = -a; }"
    ir = _build_ir(source)
    IRValidator().validate(ir)

    func = ir.body[0]
    assert isinstance(func, FunctionIR)
    assert func.name == "main"
    assert len(func.body.statements) == 2

    decl1 = func.body.statements[0]
    assert isinstance(decl1, VariableDeclarationIR)
    assert decl1.name == "a"
    assert isinstance(decl1.initializer, BinaryOperationIR)
    assert decl1.initializer.operator == "+"
    assert isinstance(decl1.initializer.right, BinaryOperationIR)
    assert decl1.initializer.right.operator == "*"

    decl2 = func.body.statements[1]
    assert isinstance(decl2, VariableDeclarationIR)
    assert decl2.name == "b"
    assert isinstance(decl2.initializer, UnaryOperationIR)
    assert decl2.initializer.operator == "-"
    assert isinstance(decl2.initializer.operand, VariableReferenceIR)
    assert decl2.initializer.operand.name == "a"


def test_ir_builder_lowers_if_else() -> None:
    source = "fn main() { let x = 1; if (x > 0) { x = 2; } else { x = 3; } }"
    ir = _build_ir(source)
    IRValidator().validate(ir)

    func = ir.body[0]
    assert isinstance(func, FunctionIR)
    if_stmt = func.body.statements[1]
    assert isinstance(if_stmt, IfIR)
    assert isinstance(if_stmt.condition, BinaryOperationIR)
    assert if_stmt.condition.operator == ">"
    assert isinstance(if_stmt.then_block, BlockIR)
    assert isinstance(if_stmt.then_block.statements[0], ExpressionStatementIR)
    assert isinstance(if_stmt.then_block.statements[0].expression, AssignmentIR)
    assert if_stmt.then_block.statements[0].expression.target == "x"
    assert isinstance(if_stmt.else_block, BlockIR)
    assert isinstance(if_stmt.else_block.statements[0], ExpressionStatementIR)
    assert isinstance(if_stmt.else_block.statements[0].expression, AssignmentIR)
    assert if_stmt.else_block.statements[0].expression.target == "x"


def test_ir_builder_lowers_call() -> None:
    source = "fn add(a, b) { return a + b; } fn main() { let res = add(1, 2); }"
    ir = _build_ir(source)
    IRValidator().validate(ir)

    main_func = ir.body[1]
    assert isinstance(main_func, FunctionIR)
    decl = main_func.body.statements[0]
    assert isinstance(decl, VariableDeclarationIR)
    assert isinstance(decl.initializer, CallIR)
    assert decl.initializer.callee == "add"
    assert len(decl.initializer.arguments) == 2


def test_ir_builder_preserves_spans() -> None:
    source = "let x = 100;"
    ir = _build_ir(source)
    IRValidator().validate(ir)

    decl = ir.body[0]
    assert isinstance(decl, VariableDeclarationIR)
    assert decl.start_span is not None
    assert decl.end_span is not None
    assert decl.initializer.start_span is not None
    assert decl.initializer.end_span is not None


def test_ir_validator_raises_on_invalid_structure() -> None:
    validator = IRValidator()

    # 1. Root must be ProgramIR
    with pytest.raises(IRValidationError, match="Root node must be ProgramIR"):
        validator.validate(LiteralIR(1, 0, 0))  # type: ignore[arg-type]

    # 2. ProgramIR must not be empty
    empty_prog = ProgramIR(body=(), start_span=0, end_span=0)
    with pytest.raises(
        IRValidationError, match="ProgramIR must contain at least one child"
    ):
        validator.validate(empty_prog)

    # 3. Missing spans
    @dataclass_no_spans
    class FakeNode:
        pass

    with pytest.raises(IRValidationError, match="missing span information"):
        validator._validate_node(FakeNode())  # type: ignore[arg-type]

    # 4. FunctionIR parameters is None
    bad_func = FunctionIR(
        name="foo",
        parameters=None,  # type: ignore[arg-type]
        body=BlockIR((), start_span=0, end_span=0),
        start_span=0,
        end_span=0,
    )
    with pytest.raises(IRValidationError, match="parameters must be a tuple"):
        validator.validate(ProgramIR((bad_func,), start_span=0, end_span=0))

    # 5. AssignmentIR missing target
    bad_assign = AssignmentIR(
        target="",
        value=LiteralIR(1, 0, 0),
        start_span=0,
        end_span=0,
    )
    with pytest.raises(IRValidationError, match="AssignmentIR missing target name"):
        validator.validate(ProgramIR((bad_assign,), start_span=0, end_span=0))

    # 6. CallIR missing callee
    bad_call = CallIR(
        callee="",
        arguments=(),
        start_span=0,
        end_span=0,
    )
    with pytest.raises(IRValidationError, match="CallIR missing callee name"):
        validator.validate(ProgramIR((ExpressionStatementIR(bad_call, 0, 0),), 0, 0))


# Helper for creating a dataclass without spans
def dataclass_no_spans(cls: type) -> type:
    from dataclasses import dataclass

    return dataclass(cls)
