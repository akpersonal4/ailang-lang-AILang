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


def test_lexer_tokenizes_arithmetic_operators() -> None:
    lexer = Lexer()

    tokens = lexer.tokenize("a + b - c * d / e % f")

    assert tokens == [
        Token(TokenKind.IDENTIFIER, "a", 0, 1),
        Token(TokenKind.PLUS, "+", 2, 3),
        Token(TokenKind.IDENTIFIER, "b", 4, 5),
        Token(TokenKind.MINUS, "-", 6, 7),
        Token(TokenKind.IDENTIFIER, "c", 8, 9),
        Token(TokenKind.STAR, "*", 10, 11),
        Token(TokenKind.IDENTIFIER, "d", 12, 13),
        Token(TokenKind.SLASH, "/", 14, 15),
        Token(TokenKind.IDENTIFIER, "e", 16, 17),
        Token(TokenKind.PERCENT, "%", 18, 19),
        Token(TokenKind.IDENTIFIER, "f", 20, 21),
        Token(TokenKind.EOF, "", 21, 21),
    ]


def test_lexer_tokenizes_comparison_and_logical_operators() -> None:
    lexer = Lexer()

    tokens = lexer.tokenize("a == b != c < d <= e > f >= g && h || i ! j")

    assert tokens == [
        Token(TokenKind.IDENTIFIER, "a", 0, 1),
        Token(TokenKind.EQEQ, "==", 2, 4),
        Token(TokenKind.IDENTIFIER, "b", 5, 6),
        Token(TokenKind.NEQ, "!=", 7, 9),
        Token(TokenKind.IDENTIFIER, "c", 10, 11),
        Token(TokenKind.LT, "<", 12, 13),
        Token(TokenKind.IDENTIFIER, "d", 14, 15),
        Token(TokenKind.LTE, "<=", 16, 18),
        Token(TokenKind.IDENTIFIER, "e", 19, 20),
        Token(TokenKind.GT, ">", 21, 22),
        Token(TokenKind.IDENTIFIER, "f", 23, 24),
        Token(TokenKind.GTE, ">=", 25, 27),
        Token(TokenKind.IDENTIFIER, "g", 28, 29),
        Token(TokenKind.ANDAND, "&&", 30, 32),
        Token(TokenKind.IDENTIFIER, "h", 33, 34),
        Token(TokenKind.OROR, "||", 35, 37),
        Token(TokenKind.IDENTIFIER, "i", 38, 39),
        Token(TokenKind.BANG, "!", 40, 41),
        Token(TokenKind.IDENTIFIER, "j", 42, 43),
        Token(TokenKind.EOF, "", 43, 43),
    ]


def test_lexer_tokenizes_string_literals_and_escapes() -> None:
    lexer = Lexer()

    tokens = lexer.tokenize('"hello" "" "\\n" "\\t" "\\""')

    assert tokens == [
        Token(TokenKind.STRING, "hello", 0, 7),
        Token(TokenKind.STRING, "", 8, 10),
        Token(TokenKind.STRING, "\n", 11, 15),
        Token(TokenKind.STRING, "\t", 16, 20),
        Token(TokenKind.STRING, '"', 21, 25),
        Token(TokenKind.EOF, "", 25, 25),
    ]


def test_lexer_reports_unterminated_string() -> None:
    lexer = Lexer()

    try:
        lexer.tokenize('"unterminated')
    except ValueError as error:
        assert "Unterminated string" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_lexer_reports_invalid_escape_sequence() -> None:
    lexer = Lexer()

    try:
        lexer.tokenize('"\\q"')
    except ValueError as error:
        assert "Invalid escape sequence" in str(error)
    else:
        raise AssertionError("expected ValueError")


def test_lexer_skips_comments_and_whitespace() -> None:
    lexer = Lexer()

    tokens = lexer.tokenize("let x = 1 // comment\nlet y = 2")

    assert tokens == [
        Token(TokenKind.LET, "let", 0, 3),
        Token(TokenKind.IDENTIFIER, "x", 4, 5),
        Token(TokenKind.ASSIGN, "=", 6, 7),
        Token(TokenKind.NUMBER, "1", 8, 9),
        Token(TokenKind.LET, "let", 21, 24),
        Token(TokenKind.IDENTIFIER, "y", 25, 26),
        Token(TokenKind.ASSIGN, "=", 27, 28),
        Token(TokenKind.NUMBER, "2", 29, 30),
        Token(TokenKind.EOF, "", 30, 30),
    ]


def test_tokens_expose_source_location_information() -> None:
    lexer = Lexer()

    tokens = lexer.tokenize("a\n")

    assert tokens[0].line == 1
    assert tokens[0].column == 1
    assert tokens[0].start_offset == 0
    assert tokens[0].end_offset == 1
    assert tokens[1].line == 2
    assert tokens[1].column == 1
    assert tokens[1].start_offset == 2
    assert tokens[1].end_offset == 2


def test_lexer_rejects_float_literal() -> None:
    """Float literals are not supported and must produce a clear diagnostic."""
    lexer = Lexer()

    try:
        lexer.tokenize("3.14")
    except ValueError as error:
        assert "Float literals not supported" in str(error)
    else:
        raise AssertionError("expected ValueError")

    try:
        lexer.tokenize("0.5")
    except ValueError as error:
        assert "Float literals not supported" in str(error)
    else:
        raise AssertionError("expected ValueError")

    # Ensure member access on identifiers still works
    lexer2 = Lexer()
    tokens = lexer2.tokenize("a.b")
    assert tokens[0].kind == TokenKind.IDENTIFIER
    assert tokens[0].value == "a"
    assert tokens[1].kind == TokenKind.DOT
    assert tokens[2].kind == TokenKind.IDENTIFIER
    assert tokens[2].value == "b"
