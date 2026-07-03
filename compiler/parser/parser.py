from __future__ import annotations

from compiler.diagnostics import DiagnosticReporter
from compiler.lexer import Token, TokenKind
from compiler.parser.declarations import (
    parse_function_declaration,
    parse_variable_declaration,
)
from compiler.parser.expressions import parse_expression as _parse_expression
from compiler.parser.nodes import CSTNode
from compiler.parser.recovery import synchronize
from compiler.parser.statements import parse_block as _parse_block
from compiler.parser.statements import parse_if_statement
from compiler.parser.token_stream import TokenStream


class Parser:
    """Recursive-descent parser that produces a CST from a token stream."""

    def __init__(
        self,
        tokens: list[Token],
        reporter: DiagnosticReporter | None = None,
    ) -> None:
        self.stream = TokenStream(tokens, reporter)

    @property
    def tokens(self) -> list[Token]:
        return self.stream.tokens

    @property
    def reporter(self) -> DiagnosticReporter | None:
        return self.stream.reporter

    @reporter.setter
    def reporter(self, value: DiagnosticReporter | None) -> None:
        self.stream.reporter = value

    @property
    def index(self) -> int:
        return self.stream.index

    @index.setter
    def index(self, value: int) -> None:
        self.stream.index = value

    # ------------------------------------------------------------------
    # Delegated helpers (preserved for backward-compatible test access)
    # ------------------------------------------------------------------

    def current(self) -> Token:
        return self.stream.current()

    def previous(self) -> Token:
        return self.stream.previous()

    def peek(self) -> Token:
        return self.stream.peek()

    def advance(self) -> Token:
        return self.stream.advance()

    def match(self, *kinds: TokenKind) -> bool:
        return self.stream.match(*kinds)

    def expect(self, kind: TokenKind) -> bool:
        return self.stream.expect(kind)

    def report(self, message: str, code: str = "PAR001") -> None:
        self.stream.report(message, code)

    def synchronize(self) -> None:
        synchronize(self.stream)

    def is_at_end(self) -> bool:
        return self.stream.is_at_end()

    # ------------------------------------------------------------------
    # Public parse entry points
    # ------------------------------------------------------------------

    def parse_program(self) -> CSTNode:
        program = CSTNode("Program")
        if self.tokens:
            program.start_span = self.tokens[0].start_offset
            program.end_span = self.tokens[-1].end_offset
        while not self.is_at_end():
            cur = self.stream.current()
            if cur.kind is TokenKind.EOF:
                break
            if cur.kind is TokenKind.SEMICOLON:
                self.stream.advance()
                continue
            if cur.kind is TokenKind.LET:
                program.children.append(parse_variable_declaration(self.stream))
            elif cur.kind is TokenKind.FN:
                program.children.append(parse_function_declaration(self.stream))
            elif cur.kind is TokenKind.IF:
                program.children.append(parse_if_statement(self.stream))
            elif cur.kind in {
                TokenKind.IDENTIFIER,
                TokenKind.NUMBER,
                TokenKind.STRING,
                TokenKind.LPAREN,
                TokenKind.MINUS,
                TokenKind.BANG,
            }:
                expr = _parse_expression(self.stream)
                program.children.append(CSTNode("ExpressionStatement", [expr]))
                if self.stream.current().kind is TokenKind.SEMICOLON:
                    self.stream.advance()
            else:
                self.stream.report("Unexpected token in program")
                if cur.kind is TokenKind.RBRACE:
                    self.stream.advance()
                else:
                    synchronize(self.stream)
        return program

    def parse_expression(self) -> CSTNode:
        return _parse_expression(self.stream)

    def parse_block(self) -> CSTNode:
        return _parse_block(self.stream)
