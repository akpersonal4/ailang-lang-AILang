from pathlib import Path

from compiler.lexer import Lexer
from compiler.parser import Parser


def test_parser_parses_if_statement() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("if (a > b) { return a; } else { return b; }"))

    cst = parser.parse_program()

    assert cst is not None
    assert len(cst.children) == 1
    assert cst.children[0].kind == "IfStatement"
    assert cst.children[0].children[0].kind == "BinaryExpression"
    assert cst.children[0].children[1].kind == "Block"
    assert cst.children[0].children[2].kind == "Block"
    assert cst.children[0].start_span == 0
    assert cst.children[0].end_span is not None


def test_parser_parses_if_without_else() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("if (x) { let y = 1; }"))

    cst = parser.parse_program()

    assert len(cst.children) == 1
    assert cst.children[0].kind == "IfStatement"
    assert len(cst.children[0].children) == 2
    assert cst.children[0].children[0].kind == "Identifier"
    assert cst.children[0].children[1].kind == "Block"


def test_parser_parses_nested_if_else() -> None:
    lexer = Lexer()
    parser = Parser(
        lexer.tokenize(
            "if (a) { if (b) { return 1; } else { return 2; } } else { return 3; }"
        )
    )

    cst = parser.parse_program()

    assert len(cst.children) == 1
    outer = cst.children[0]
    assert outer.kind == "IfStatement"
    assert outer.children[0].kind == "Identifier"
    assert outer.children[1].kind == "Block"
    assert len(outer.children[1].children) == 1
    assert outer.children[1].children[0].kind == "IfStatement"
    assert outer.children[2].kind == "Block"


def test_parser_parses_if_inside_block() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("fn foo() { if (x) { return 1; } }"))

    cst = parser.parse_program()

    assert len(cst.children) == 1
    fn_decl = cst.children[0]
    assert fn_decl.kind == "FunctionDeclaration"
    block = fn_decl.children[2]
    assert block.kind == "Block"
    assert len(block.children) == 1
    assert block.children[0].kind == "IfStatement"


def test_parser_parses_comparison_in_node_text() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("a >= b"))

    expr = parser.parse_expression()

    assert expr.kind == "BinaryExpression"
    assert expr.token is not None
    assert expr.token.kind.name == "GTE"
    assert expr.token.value == ">="
    assert expr.start_span == 0
    assert expr.end_span == 6


def test_parser_parses_logical_and_or() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("a && b || c"))

    expr = parser.parse_expression()

    assert expr.kind == "BinaryExpression"
    assert expr.token is not None
    assert expr.token.value == "||"
    assert expr.children[0].kind == "BinaryExpression"
    assert expr.children[0].token is not None
    assert expr.children[0].token.value == "&&"
    assert expr.children[1].kind == "Identifier"


def test_parser_generates_if_statement_integration_snapshot() -> None:
    source_path = Path("examples/integration/max_function.ail")
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source_path.read_text(encoding="utf-8")))

    cst = parser.parse_program()
    snapshot_path = Path("tests/golden/max_function_cst.txt")
    snapshot_path.write_text(str(cst), encoding="utf-8")

    assert snapshot_path.exists()


def test_parser_generates_if_else_golden_snapshot() -> None:
    source_path = Path("examples/if_else.ail")
    lexer = Lexer()
    parser = Parser(lexer.tokenize(source_path.read_text(encoding="utf-8")))

    cst = parser.parse_program()
    snapshot_path = Path("tests/golden/if_else_cst.txt")
    snapshot_path.write_text(str(cst), encoding="utf-8")

    assert snapshot_path.exists()
