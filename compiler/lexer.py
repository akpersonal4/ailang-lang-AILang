from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from compiler.diagnostics import Diagnostic, DiagnosticReporter, ErrorCode, Severity


class TokenKind(Enum):
    IDENTIFIER = "identifier"
    NUMBER = "number"
    TRUE = "true"
    FALSE = "false"
    ASSIGN = "assign"
    LET = "let"
    FN = "fn"
    IF = "if"
    ELSE = "else"
    RETURN = "return"
    IMPORT = "import"
    AS = "as"
    LPAREN = "lparen"
    RPAREN = "rparen"
    LBRACE = "lbrace"
    RBRACE = "rbrace"
    COMMA = "comma"
    SEMICOLON = "semicolon"
    PLUS = "plus"
    MINUS = "minus"
    STAR = "star"
    SLASH = "slash"
    PERCENT = "percent"
    EQEQ = "eqeq"
    NEQ = "neq"
    LT = "lt"
    LTE = "lte"
    GT = "gt"
    GTE = "gte"
    ANDAND = "andand"
    OROR = "oror"
    BANG = "bang"
    STRING = "string"
    DOT = "dot"
    EOF = "eof"


@dataclass(frozen=True, eq=False)
class Token:
    kind: TokenKind
    value: str
    start: int
    end: int
    line: int | None = None
    column: int | None = None
    start_offset: int | None = None
    end_offset: int | None = None

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Token):
            return NotImplemented
        return (
            self.kind == other.kind
            and self.value == other.value
            and self.start == other.start
            and self.end == other.end
        )


class LexicalError(ValueError):
    def __init__(self, message: str, diagnostic: Diagnostic) -> None:
        super().__init__(message)
        self.diagnostic = diagnostic


class Lexer:
    def __init__(self, reporter: DiagnosticReporter | None = None) -> None:
        self.reporter = reporter

    def tokenize(self, text: str) -> list[Token]:
        tokens: list[Token] = []
        index = 0
        length = len(text)
        line = 1
        column = 1

        def make_token(
            kind: TokenKind,
            value: str,
            start: int,
            end: int,
            start_line: int,
            start_column: int,
        ) -> Token:
            return Token(
                kind,
                value,
                start,
                end,
                start_line,
                start_column,
                start,
                end,
            )

        def report_error(
            message: str, code: str, line_number: int, column_number: int
        ) -> None:
            diagnostic = Diagnostic(
                Severity.ERROR,
                ErrorCode(code, message),
                message,
                line_number,
                column_number,
            )
            if self.reporter is not None:
                self.reporter.report(diagnostic)
                return
            raise LexicalError(message, diagnostic)

        while index < length:
            char = text[index]
            start_line = line
            start_column = column

            if char in " \t":
                index += 1
                column += 1
                continue
            if char == "\n":
                index += 1
                line += 1
                column = 1
                continue
            if char == "\r":
                index += 1
                if index < length and text[index] == "\n":
                    index += 1
                line += 1
                column = 1
                continue
            if char == "/" and index + 1 < length and text[index + 1] == "/":
                index += 2
                column += 2
                while index < length and text[index] not in "\r\n":
                    index += 1
                    column += 1
                continue

            if self._is_identifier_start(char):
                start = index
                index += 1
                column += 1
                while index < length and self._is_identifier_part(text[index]):
                    index += 1
                    column += 1
                text_value = text[start:index]
                keyword_kind = {
                    "let": TokenKind.LET,
                    "fn": TokenKind.FN,
                    "if": TokenKind.IF,
                    "else": TokenKind.ELSE,
                    "return": TokenKind.RETURN,
                    "import": TokenKind.IMPORT,
                    "as": TokenKind.AS,
                    "true": TokenKind.TRUE,
                    "false": TokenKind.FALSE,
                }.get(text_value)
                if keyword_kind is None:
                    tokens.append(
                        make_token(
                            TokenKind.IDENTIFIER,
                            text_value,
                            start,
                            index,
                            start_line,
                            start_column,
                        )
                    )
                else:
                    tokens.append(
                        make_token(
                            keyword_kind,
                            text_value,
                            start,
                            index,
                            start_line,
                            start_column,
                        )
                    )
                continue
            if self._is_digit(char):
                start = index
                index += 1
                column += 1
                while index < length and self._is_digit(text[index]):
                    index += 1
                    column += 1
                tokens.append(
                    make_token(
                        TokenKind.NUMBER,
                        text[start:index],
                        start,
                        index,
                        start_line,
                        start_column,
                    )
                )
                if (
                    index < length
                    and text[index] == "."
                    and index + 1 < length
                    and self._is_digit(text[index + 1])
                ):
                    report_error(
                        "Float literals not supported. Use integer division (22 / 7)",
                        "LEX004",
                        start_line,
                        start_column,
                    )
                continue
            if char == "=":
                if index + 1 < length and text[index + 1] == "=":
                    tokens.append(
                        make_token(
                            TokenKind.EQEQ,
                            "==",
                            index,
                            index + 2,
                            start_line,
                            start_column,
                        )
                    )
                    index += 2
                    column += 2
                else:
                    tokens.append(
                        make_token(
                            TokenKind.ASSIGN,
                            char,
                            index,
                            index + 1,
                            start_line,
                            start_column,
                        )
                    )
                    index += 1
                    column += 1
                continue
            if char == "!":
                if index + 1 < length and text[index + 1] == "=":
                    tokens.append(
                        make_token(
                            TokenKind.NEQ,
                            "!=",
                            index,
                            index + 2,
                            start_line,
                            start_column,
                        )
                    )
                    index += 2
                    column += 2
                else:
                    tokens.append(
                        make_token(
                            TokenKind.BANG,
                            char,
                            index,
                            index + 1,
                            start_line,
                            start_column,
                        )
                    )
                    index += 1
                    column += 1
                continue
            if char == "<":
                if index + 1 < length and text[index + 1] == "=":
                    tokens.append(
                        make_token(
                            TokenKind.LTE,
                            "<=",
                            index,
                            index + 2,
                            start_line,
                            start_column,
                        )
                    )
                    index += 2
                    column += 2
                else:
                    tokens.append(
                        make_token(
                            TokenKind.LT,
                            char,
                            index,
                            index + 1,
                            start_line,
                            start_column,
                        )
                    )
                    index += 1
                    column += 1
                continue
            if char == ">":
                if index + 1 < length and text[index + 1] == "=":
                    tokens.append(
                        make_token(
                            TokenKind.GTE,
                            ">=",
                            index,
                            index + 2,
                            start_line,
                            start_column,
                        )
                    )
                    index += 2
                    column += 2
                else:
                    tokens.append(
                        make_token(
                            TokenKind.GT,
                            char,
                            index,
                            index + 1,
                            start_line,
                            start_column,
                        )
                    )
                    index += 1
                    column += 1
                continue
            if char == "&":
                if index + 1 < length and text[index + 1] == "&":
                    tokens.append(
                        make_token(
                            TokenKind.ANDAND,
                            "&&",
                            index,
                            index + 2,
                            start_line,
                            start_column,
                        )
                    )
                    index += 2
                    column += 2
                else:
                    report_error(
                        f"Unexpected character: {char}",
                        "LEX001",
                        start_line,
                        start_column,
                    )
                    index += 1
                    column += 1
                continue
            if char == "|":
                if index + 1 < length and text[index + 1] == "|":
                    tokens.append(
                        make_token(
                            TokenKind.OROR,
                            "||",
                            index,
                            index + 2,
                            start_line,
                            start_column,
                        )
                    )
                    index += 2
                    column += 2
                else:
                    report_error(
                        f"Unexpected character: {char}",
                        "LEX001",
                        start_line,
                        start_column,
                    )
                    index += 1
                    column += 1
                continue
            if char == ".":
                tokens.append(
                    make_token(
                        TokenKind.DOT,
                        char,
                        index,
                        index + 1,
                        start_line,
                        start_column,
                    )
                )
                index += 1
                column += 1
                continue

            if char == '"':
                start = index
                index += 1
                column += 1
                value_chars: list[str] = []
                while index < length:
                    current = text[index]
                    if current == '"':
                        index += 1
                        column += 1
                        break
                    if current == "\\":
                        if index + 1 >= length:
                            report_error(
                                "Unterminated string",
                                "LEX002",
                                start_line,
                                start_column,
                            )
                            index += 1
                            column += 1
                            break
                        escaped = text[index + 1]
                        if escaped == "n":
                            value_chars.append("\n")
                        elif escaped == "t":
                            value_chars.append("\t")
                        elif escaped == "r":
                            value_chars.append("\r")
                        elif escaped == "\\":
                            value_chars.append("\\")
                        elif escaped == '"':
                            value_chars.append('"')
                        else:
                            report_error(
                                "Invalid escape sequence", "LEX003", line, column
                            )
                            index += 2
                            column += 2
                            break
                        index += 2
                        column += 2
                        continue
                    value_chars.append(current)
                    index += 1
                    column += 1
                else:
                    report_error(
                        "Unterminated string", "LEX002", start_line, start_column
                    )
                    continue
                tokens.append(
                    make_token(
                        TokenKind.STRING,
                        "".join(value_chars),
                        start,
                        index,
                        start_line,
                        start_column,
                    )
                )
                continue
            if char == "+":
                tokens.append(
                    make_token(
                        TokenKind.PLUS, char, index, index + 1, start_line, start_column
                    )
                )
                index += 1
                column += 1
                continue
            if char == "-":
                tokens.append(
                    make_token(
                        TokenKind.MINUS,
                        char,
                        index,
                        index + 1,
                        start_line,
                        start_column,
                    )
                )
                index += 1
                column += 1
                continue
            if char == "*":
                tokens.append(
                    make_token(
                        TokenKind.STAR, char, index, index + 1, start_line, start_column
                    )
                )
                index += 1
                column += 1
                continue
            if char == "/":
                tokens.append(
                    make_token(
                        TokenKind.SLASH,
                        char,
                        index,
                        index + 1,
                        start_line,
                        start_column,
                    )
                )
                index += 1
                column += 1
                continue
            if char == "%":
                tokens.append(
                    make_token(
                        TokenKind.PERCENT,
                        char,
                        index,
                        index + 1,
                        start_line,
                        start_column,
                    )
                )
                index += 1
                column += 1
                continue
            if char == "(":
                tokens.append(
                    make_token(
                        TokenKind.LPAREN,
                        char,
                        index,
                        index + 1,
                        start_line,
                        start_column,
                    )
                )
                index += 1
                column += 1
                continue
            if char == ")":
                tokens.append(
                    make_token(
                        TokenKind.RPAREN,
                        char,
                        index,
                        index + 1,
                        start_line,
                        start_column,
                    )
                )
                index += 1
                column += 1
                continue
            if char == "{":
                tokens.append(
                    make_token(
                        TokenKind.LBRACE,
                        char,
                        index,
                        index + 1,
                        start_line,
                        start_column,
                    )
                )
                index += 1
                column += 1
                continue
            if char == "}":
                tokens.append(
                    make_token(
                        TokenKind.RBRACE,
                        char,
                        index,
                        index + 1,
                        start_line,
                        start_column,
                    )
                )
                index += 1
                column += 1
                continue
            if char == ",":
                tokens.append(
                    make_token(
                        TokenKind.COMMA,
                        char,
                        index,
                        index + 1,
                        start_line,
                        start_column,
                    )
                )
                index += 1
                column += 1
                continue
            if char == ";":
                tokens.append(
                    make_token(
                        TokenKind.SEMICOLON,
                        char,
                        index,
                        index + 1,
                        start_line,
                        start_column,
                    )
                )
                index += 1
                column += 1
                continue
            report_error(
                f"Unexpected character: {char}", "LEX001", start_line, start_column
            )
            index += 1
            column += 1
            continue

        tokens.append(
            Token(TokenKind.EOF, "", length, length, line, column, length, length)
        )
        return tokens

    @staticmethod
    def _is_identifier_start(char: str) -> bool:
        return char == "_" or ("a" <= char <= "z") or ("A" <= char <= "Z")

    @staticmethod
    def _is_identifier_part(char: str) -> bool:
        return Lexer._is_identifier_start(char) or ("0" <= char <= "9")

    @staticmethod
    def _is_digit(char: str) -> bool:
        return "0" <= char <= "9"
