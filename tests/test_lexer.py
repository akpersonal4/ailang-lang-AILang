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


def test_lexer_tokenizes_keywords_and_punctuation() -> None:
    lexer = Lexer()

    tokens = lexer.tokenize("let fn if else return ( ) { } , ;")

    assert tokens == [
        Token(TokenKind.LET, "let", 0, 3),
        Token(TokenKind.FN, "fn", 4, 6),
        Token(TokenKind.IF, "if", 7, 9),
        Token(TokenKind.ELSE, "else", 10, 14),
        Token(TokenKind.RETURN, "return", 15, 21),
        Token(TokenKind.LPAREN, "(", 22, 23),
        Token(TokenKind.RPAREN, ")", 24, 25),
        Token(TokenKind.LBRACE, "{", 26, 27),
        Token(TokenKind.RBRACE, "}", 28, 29),
        Token(TokenKind.COMMA, ",", 30, 31),
        Token(TokenKind.SEMICOLON, ";", 32, 33),
        Token(TokenKind.EOF, "", 33, 33),
    ]
