from pathlib import Path

from compiler.lexer import Lexer
from compiler.parser import Parser


def test_parser_parses_variable_declaration() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("let x = 10;"))

    cst = parser.parse_program()

    assert cst is not None
    assert len(cst.children) == 1
    assert cst.children[0].kind == "VariableDeclaration"
    assert cst.children[0].start_span == 0
    assert cst.children[0].end_span == 11


def test_parser_parses_function_declaration() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("fn add(a, b) {\n    return a + b;\n}"))

    cst = parser.parse_program()

    assert cst is not None
    assert len(cst.children) == 1
    assert cst.children[0].kind == "FunctionDeclaration"
    assert len(cst.children[0].children) == 3
    assert cst.children[0].start_span == 0
    assert cst.children[0].end_span is not None


def test_parser_generates_golden_cst_snapshot() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("let x = 10;"))

    cst = parser.parse_program()
    snapshot_path = Path("tests/golden/variable_declaration.txt")
    snapshot_path.write_text(str(cst), encoding="utf-8")

    assert snapshot_path.exists()


def test_parser_parses_expression_precedence() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("a + b * c"))

    expression = parser.parse_expression()

    assert expression.kind == "BinaryExpression"
    assert expression.children[0].kind == "Identifier"
    assert expression.children[1].kind == "BinaryExpression"
    assert expression.start_span == 0
    assert expression.end_span == 9


def test_parser_parses_grouping_and_unary_expressions() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("-(a + b)"))

    expression = parser.parse_expression()

    assert expression.kind == "UnaryExpression"
    assert expression.children[0].kind == "BinaryExpression"
    assert expression.start_span == 0
    assert expression.end_span == 7


def test_parser_parses_call_expressions() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("add(a, b)"))

    expression = parser.parse_expression()

    assert expression.kind == "CallExpression"
    assert expression.children[0].kind == "Identifier"
    assert expression.children[1].kind == "ArgumentList"


def test_parser_generates_expression_golden_snapshot() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("a + b * c"))

    expression = parser.parse_expression()
    snapshot_path = Path("tests/golden/expression_precedence.txt")
    snapshot_path.write_text(str(expression), encoding="utf-8")

    assert snapshot_path.exists()
