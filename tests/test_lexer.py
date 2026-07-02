from compiler.lexer import Lexer, Token, TokenKind


def test_lexer_tokenizes_identifiers_and_numbers() -> None:
    lexer = Lexer()

    tokens = lexer.tokenize("alpha123 42")

    assert tokens == [
        Token(TokenKind.IDENTIFIER, "alpha123", 0, 8),
        Token(TokenKind.NUMBER, "42", 9, 11),
        Token(TokenKind.EOF, "", 11, 11),
    ]


def test_lexer_tokenizes_basic_punctuation() -> None:
    lexer = Lexer()

    tokens = lexer.tokenize("x = 1")

    assert tokens == [
        Token(TokenKind.IDENTIFIER, "x", 0, 1),
        Token(TokenKind.ASSIGN, "=", 2, 3),
        Token(TokenKind.NUMBER, "1", 4, 5),
        Token(TokenKind.EOF, "", 5, 5),
    ]
