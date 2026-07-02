"""Tests for the CST-to-AST transformation."""

from pathlib import Path

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import (
    ASTNode,
    BinaryExpressionNode,
    BlockNode,
    CallExpressionNode,
    ExpressionStatementNode,
    FunctionDeclarationNode,
    IdentifierNode,
    IfStatementNode,
    NumberLiteralNode,
    ProgramNode,
    ReturnStatementNode,
    StringLiteralNode,
    UnaryExpressionNode,
    VariableDeclarationNode,
)
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.parser.nodes import CSTNode


def _parse(source: str) -> CSTNode:
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source))
    return parser.parse_program()


def _build(source: str) -> ProgramNode:
    ast = ASTBuilder().build(_parse(source))
    assert isinstance(ast, ProgramNode)
    return ast


def _parse_expr(source: str) -> CSTNode:
    """Parse an expression directly (for expression-level tests)."""
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source))
    return parser.parse_expression()


def _build_expr(source: str) -> ASTNode:
    cst = _parse_expr(source)
    return ASTBuilder().build(cst)


# ------------------------------------------------------------------
# Program
# ------------------------------------------------------------------


def test_ast_builds_empty_program() -> None:
    ast = _build("")
    assert isinstance(ast, ProgramNode)
    assert ast.children == ()


def test_ast_builds_program_with_multiple_children() -> None:
    ast = _build("let x = 1; let y = 2;")
    assert isinstance(ast, ProgramNode)
    assert len(ast.children) == 2
    assert all(isinstance(c, VariableDeclarationNode) for c in ast.children)


# ------------------------------------------------------------------
# Variable declarations
# ------------------------------------------------------------------


def test_ast_builds_variable_declaration() -> None:
    ast = _build("let x = 10;")
    assert isinstance(ast, ProgramNode)
    decl = ast.children[0]
    assert isinstance(decl, VariableDeclarationNode)
    assert decl.name.name == "x"
    assert isinstance(decl.initializer, NumberLiteralNode)
    assert decl.initializer.value == "10"
    assert decl.start_span == 0
    assert decl.end_span == 11


def test_ast_builds_variable_declaration_with_expression() -> None:
    ast = _build("let result = a + b;")
    assert isinstance(ast, ProgramNode)
    decl = ast.children[0]
    assert isinstance(decl, VariableDeclarationNode)
    assert decl.name.name == "result"
    assert isinstance(decl.initializer, BinaryExpressionNode)


# ------------------------------------------------------------------
# Function declarations
# ------------------------------------------------------------------


def test_ast_builds_function_declaration() -> None:
    ast = _build("fn add(a, b) { return a + b; }")
    assert isinstance(ast, ProgramNode)
    func = ast.children[0]
    assert isinstance(func, FunctionDeclarationNode)
    assert func.name.name == "add"
    assert len(func.parameters) == 2
    assert func.parameters[0].name == "a"
    assert func.parameters[1].name == "b"
    assert isinstance(func.body, BlockNode)
    assert len(func.body.statements) == 1
    assert isinstance(func.body.statements[0], ReturnStatementNode)


def test_ast_builds_function_with_no_parameters() -> None:
    ast = _build("fn foo() { return 1; }")
    assert isinstance(ast, ProgramNode)
    func = ast.children[0]
    assert isinstance(func, FunctionDeclarationNode)
    assert func.name.name == "foo"
    assert func.parameters == ()


# ------------------------------------------------------------------
# Return statements
# ------------------------------------------------------------------


def test_ast_builds_return_statement() -> None:
    ast = _build("fn f() { return 42; }")
    func = ast.children[0]
    assert isinstance(func, FunctionDeclarationNode)
    ret = func.body.statements[0]
    assert isinstance(ret, ReturnStatementNode)
    assert isinstance(ret.value, NumberLiteralNode)
    assert ret.value.value == "42"


# ------------------------------------------------------------------
# If/else statements
# ------------------------------------------------------------------


def test_ast_builds_if_statement() -> None:
    ast = _build("fn f() { if (x) { return 1; } }")
    func = ast.children[0]
    assert isinstance(func, FunctionDeclarationNode)
    if_stmt = func.body.statements[0]
    assert isinstance(if_stmt, IfStatementNode)
    assert isinstance(if_stmt.condition, IdentifierNode)
    assert if_stmt.condition.name == "x"
    assert isinstance(if_stmt.then_block, BlockNode)
    assert len(if_stmt.then_block.statements) == 1
    assert if_stmt.else_block is None


def test_ast_builds_if_else_statement() -> None:
    ast = _build("fn f() { if (x) { return 1; } else { return 2; } }")
    func = ast.children[0]
    assert isinstance(func, FunctionDeclarationNode)
    if_stmt = func.body.statements[0]
    assert isinstance(if_stmt, IfStatementNode)
    assert if_stmt.else_block is not None
    assert isinstance(if_stmt.else_block, BlockNode)
    assert len(if_stmt.else_block.statements) == 1


def test_ast_builds_if_else_if_chain() -> None:
    source = (
        "fn f() { if (a) { return 1; } else if (b) { return 2; } else { return 3; } }"
    )
    ast = _build(source)
    func = ast.children[0]
    assert isinstance(func, FunctionDeclarationNode)
    if_stmt = func.body.statements[0]
    assert isinstance(if_stmt, IfStatementNode)
    assert if_stmt.else_block is not None
    assert len(if_stmt.else_block.statements) == 1
    inner = if_stmt.else_block.statements[0]
    assert isinstance(inner, IfStatementNode)
    assert inner.else_block is not None
    assert len(inner.else_block.statements) == 1


# ------------------------------------------------------------------
# Expression statements (inside function bodies)
# ------------------------------------------------------------------


def test_ast_builds_expression_statement() -> None:
    ast = _build("fn f() { a + b; }")
    func = ast.children[0]
    assert isinstance(func, FunctionDeclarationNode)
    stmt = func.body.statements[0]
    assert isinstance(stmt, ExpressionStatementNode)
    assert isinstance(stmt.expression, BinaryExpressionNode)


def test_ast_builds_number_literal() -> None:
    ast = _build("fn f() { 42; }")
    func = ast.children[0]
    assert isinstance(func, FunctionDeclarationNode)
    stmt = func.body.statements[0]
    assert isinstance(stmt, ExpressionStatementNode)
    assert isinstance(stmt.expression, NumberLiteralNode)
    assert stmt.expression.value == "42"


def test_ast_builds_string_literal() -> None:
    ast = _build('fn f() { "hello"; }')
    func = ast.children[0]
    assert isinstance(func, FunctionDeclarationNode)
    stmt = func.body.statements[0]
    assert isinstance(stmt, ExpressionStatementNode)
    assert isinstance(stmt.expression, StringLiteralNode)
    assert stmt.expression.value == "hello"


def test_ast_builds_identifier() -> None:
    ast = _build("fn f() { myVar; }")
    func = ast.children[0]
    assert isinstance(func, FunctionDeclarationNode)
    stmt = func.body.statements[0]
    assert isinstance(stmt, ExpressionStatementNode)
    assert isinstance(stmt.expression, IdentifierNode)
    assert stmt.expression.name == "myVar"


# ------------------------------------------------------------------
# Binary expressions
# ------------------------------------------------------------------


def test_ast_builds_binary_expression() -> None:
    expr = _build_expr("a + b")
    assert isinstance(expr, BinaryExpressionNode)
    assert expr.operator == "+"
    assert isinstance(expr.left, IdentifierNode)
    assert expr.left.name == "a"
    assert isinstance(expr.right, IdentifierNode)
    assert expr.right.name == "b"


def test_ast_builds_comparison_expression() -> None:
    expr = _build_expr("a >= b")
    assert isinstance(expr, BinaryExpressionNode)
    assert expr.operator == ">="


def test_ast_builds_logical_expression() -> None:
    expr = _build_expr("a && b || c")
    assert isinstance(expr, BinaryExpressionNode)
    assert expr.operator == "||"
    assert isinstance(expr.left, BinaryExpressionNode)
    assert expr.left.operator == "&&"


def test_ast_builds_assignment_expression() -> None:
    expr = _build_expr("x = 42")
    assert isinstance(expr, BinaryExpressionNode)
    assert expr.operator == "="
    assert isinstance(expr.left, IdentifierNode)
    assert expr.left.name == "x"
    assert isinstance(expr.right, NumberLiteralNode)
    assert expr.right.value == "42"


# ------------------------------------------------------------------
# Unary expressions
# ------------------------------------------------------------------


def test_ast_builds_unary_expression() -> None:
    expr = _build_expr("-x")
    assert isinstance(expr, UnaryExpressionNode)
    assert expr.operator == "-"
    assert isinstance(expr.operand, IdentifierNode)
    assert expr.operand.name == "x"


def test_ast_builds_logical_not() -> None:
    expr = _build_expr("!flag")
    assert isinstance(expr, UnaryExpressionNode)
    assert expr.operator == "!"


# ------------------------------------------------------------------
# Call expressions
# ------------------------------------------------------------------


def test_ast_builds_call_expression() -> None:
    expr = _build_expr("foo(a, b)")
    assert isinstance(expr, CallExpressionNode)
    assert isinstance(expr.callee, IdentifierNode)
    assert expr.callee.name == "foo"
    assert len(expr.arguments) == 2
    assert isinstance(expr.arguments[0], IdentifierNode)
    assert expr.arguments[0].name == "a"
    assert isinstance(expr.arguments[1], IdentifierNode)
    assert expr.arguments[1].name == "b"


def test_ast_builds_call_with_no_arguments() -> None:
    expr = _build_expr("foo()")
    assert isinstance(expr, CallExpressionNode)
    assert expr.arguments == ()


# ------------------------------------------------------------------
# Source spans
# ------------------------------------------------------------------


def test_ast_preserves_source_spans() -> None:
    ast = _build("let x = 10;")
    decl = ast.children[0]
    assert isinstance(decl, VariableDeclarationNode)
    assert decl.start_span == 0
    assert decl.end_span == 11
    assert decl.name.start_span == 4
    assert decl.name.end_span == 5
    assert decl.initializer.start_span == 8
    assert decl.initializer.end_span == 10


def test_ast_preserves_spans_on_expression_nodes() -> None:
    expr = _build_expr("1 + 2")
    assert isinstance(expr, BinaryExpressionNode)
    assert expr.start_span == 0
    assert expr.end_span == 5


# ------------------------------------------------------------------
# Golden snapshot
# ------------------------------------------------------------------


def test_ast_generates_golden_snapshot() -> None:
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
    cst = _parse(source)
    ast = ASTBuilder().build(cst)
    snapshot_path = Path("tests/golden/ast_program.txt")
    snapshot_path.write_text(str(ast), encoding="utf-8")
    assert snapshot_path.exists()
