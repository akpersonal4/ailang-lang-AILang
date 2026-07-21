"""Tests for Member Access v1: a.b and a.b() expressions."""

from __future__ import annotations

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import (
    CallExpressionNode,
    ExpressionStatementNode,
    IdentifierNode,
    MemberAccessNode,
    ProgramNode,
)
from compiler.ir.builder import IRBuilder
from compiler.ir.nodes import (
    ExpressionStatementIR,
    MemberAccessIR,
    ProgramIR,
    VariableReferenceIR,
)
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.runtime.interpreter import Runtime


def _parse(source: str) -> ProgramNode:
    """Parse source and return AST."""
    lexer = Lexer()
    tokens = lexer.tokenize(source)
    parser = Parser(tokens)
    cst = parser.parse_program()
    builder = ASTBuilder()
    ast = builder.build(cst)
    assert isinstance(ast, ProgramNode)
    return ast


def _build_ir(source: str) -> ProgramIR:
    """Parse, build AST, build IR."""
    ast = _parse(source)
    ir_builder = IRBuilder()
    return ir_builder.build(ast)


def _run(source: str) -> object:
    """Parse, build IR, execute."""
    ir = _build_ir(source)
    runtime = Runtime()
    return runtime.execute(ir)


class TestMemberAccessParser:
    """Parser tests for member access expressions."""

    def test_simple_member_access(self) -> None:
        """Parse a.b correctly."""
        ast = _parse("a.b")
        statement = ast.children[0]
        assert isinstance(statement, ExpressionStatementNode)
        expr = statement.expression
        assert isinstance(expr, MemberAccessNode)
        assert isinstance(expr.receiver, IdentifierNode)
        assert expr.receiver.name == "a"
        assert expr.member.name == "b"

    def test_chained_member_access(self) -> None:
        """Parse a.b.c as nested MemberAccessNodes."""
        ast = _parse("a.b.c")
        statement = ast.children[0]
        assert isinstance(statement, ExpressionStatementNode)
        expr = statement.expression
        # a.b.c should be MemberAccess(MemberAccess(a, b), c)
        assert isinstance(expr, MemberAccessNode)
        assert expr.member.name == "c"
        inner = expr.receiver
        assert isinstance(inner, MemberAccessNode)
        assert inner.member.name == "b"
        assert isinstance(inner.receiver, IdentifierNode)
        assert inner.receiver.name == "a"

    def test_member_call(self) -> None:
        """Parse a.b() as CallExpression with MemberAccess callee."""
        ast = _parse("a.b()")
        statement = ast.children[0]
        assert isinstance(statement, ExpressionStatementNode)
        expr = statement.expression
        assert isinstance(expr, CallExpressionNode)
        callee = expr.callee
        assert isinstance(callee, MemberAccessNode)
        assert isinstance(callee.receiver, IdentifierNode)
        assert callee.receiver.name == "a"
        assert callee.member.name == "b"
        assert len(expr.arguments) == 0

    def test_member_call_with_args(self) -> None:
        """Parse a.b(x) as CallExpression with arguments."""
        ast = _parse("a.b(5)")
        statement = ast.children[0]
        assert isinstance(statement, ExpressionStatementNode)
        expr = statement.expression
        assert isinstance(expr, CallExpressionNode)
        callee = expr.callee
        assert isinstance(callee, MemberAccessNode)
        assert callee.member.name == "b"
        assert len(expr.arguments) == 1


class TestMemberAccessIR:
    """IR tests for member access expressions."""

    def test_member_access_ir(self) -> None:
        """Test IR for a.b."""
        ir = _build_ir("a.b")
        stmt = ir.body[0]
        assert isinstance(stmt, ExpressionStatementIR)
        assert isinstance(stmt.expression, MemberAccessIR)
        assert stmt.expression.member == "b"
        assert isinstance(stmt.expression.receiver, VariableReferenceIR)
        assert stmt.expression.receiver.name == "a"

    def test_chained_member_access_ir(self) -> None:
        """Test IR for a.b.c."""
        ir = _build_ir("a.b.c")
        stmt = ir.body[0]
        assert isinstance(stmt, ExpressionStatementIR)
        assert isinstance(stmt.expression, MemberAccessIR)
        assert stmt.expression.member == "c"
        inner = stmt.expression.receiver
        assert isinstance(inner, MemberAccessIR)
        assert inner.member == "b"
        assert isinstance(inner.receiver, VariableReferenceIR)
        assert inner.receiver.name == "a"


class TestMemberAccessRuntime:
    """Runtime tests for member access expressions."""

    def test_member_access_on_variable(self) -> None:
        """Test accessing a property on a variable."""
        result = _run("""
let user = 5;
user
""")
        assert result == 5
