from __future__ import annotations

from compiler.diagnostics import Diagnostic, DiagnosticReporter, ErrorCode, Severity
from compiler.lexer import Token, TokenKind


class TokenStream:
    """Manages token iteration and provides helper methods for parser consumption."""

    def __init__(
        self,
        tokens: list[Token],
        reporter: DiagnosticReporter | None = None,
        source_path: str | None = None,
        experimental_loops: bool = False,
    ) -> None:
        self.tokens = tokens
        self.reporter = reporter
        self.source_path = source_path
        self.experimental_loops = experimental_loops
        self.index = 0

    def current(self) -> Token:
        return self._token_at(self.index)

    def previous(self) -> Token:
        return self._token_at(self.index - 1)

    def peek(self) -> Token:
        return self.current()

    def advance(self) -> Token:
        token = self.current()
        if not self.is_at_end():
            self.index += 1
        return token

    def match(self, *kinds: TokenKind) -> bool:
        if self.current().kind in kinds:
            self.advance()
            return True
        return False

    def expect(self, kind: TokenKind) -> bool:
        if self.current().kind is kind:
            self.advance()
            return True
        self._report_error(f"Expected {kind.name}", "PAR001")
        return False

    def report(self, message: str, code: str = "PAR001") -> None:
        self._report_error(message, code)

    def is_at_end(self) -> bool:
        return self.current().kind is TokenKind.EOF

    def _token_at(self, index: int) -> Token:
        if index >= len(self.tokens):
            return self.tokens[-1]
        return self.tokens[index]

    def _report_error(self, message: str, code: str) -> None:
        diagnostic = Diagnostic(
            Severity.ERROR,
            ErrorCode(code, message),
            message,
            self.current().line,
            self.current().column,
            file_path=self.source_path,
        )
        if self.reporter is not None:
            self.reporter.report(diagnostic)
