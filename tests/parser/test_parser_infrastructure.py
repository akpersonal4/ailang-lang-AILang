from compiler.lexer import Lexer, TokenKind
from compiler.parser import Parser


def test_parser_exposes_infrastructure_helpers() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("let x = 1;"))

    assert parser.peek().kind is TokenKind.LET
    assert parser.current().kind is TokenKind.LET
    assert parser.advance().kind is TokenKind.LET
    assert parser.current().kind is TokenKind.IDENTIFIER


def test_parser_can_match_and_expect_tokens() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize("let x = 1;"))

    assert parser.match(TokenKind.LET)
    assert parser.match(TokenKind.IDENTIFIER)
    assert parser.expect(TokenKind.ASSIGN)
    assert parser.expect(TokenKind.NUMBER)


def test_parser_reports_eof_and_diagnostics() -> None:
    lexer = Lexer()
    parser = Parser(lexer.tokenize(""))

    assert parser.is_at_end()
    assert parser.current().kind is TokenKind.EOF
    assert parser.peek().kind is TokenKind.EOF
