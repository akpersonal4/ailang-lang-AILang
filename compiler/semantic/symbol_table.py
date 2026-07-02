"""Lexical scope symbol table for AILang semantic analysis."""

from __future__ import annotations

from dataclasses import dataclass

from compiler.diagnostics import Diagnostic, DiagnosticReporter, ErrorCode, Severity


@dataclass
class Symbol:
    name: str
    start_span: int | None = None
    end_span: int | None = None


class Scope:
    def __init__(self) -> None:
        self.symbols: dict[str, Symbol] = {}

    def declare(
        self, name: str, start_span: int | None = None, end_span: int | None = None
    ) -> Symbol:
        if name in self.symbols:
            return self.symbols[name]
        symbol = Symbol(name, start_span, end_span)
        self.symbols[name] = symbol
        return symbol

    def resolve(self, name: str) -> Symbol | None:
        return self.symbols.get(name)


class SymbolTable:
    def __init__(self, reporter: DiagnosticReporter | None = None) -> None:
        self.reporter = reporter
        self.scopes: list[Scope] = [Scope()]

    def enter_scope(self) -> None:
        self.scopes.append(Scope())

    def exit_scope(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(
        self, name: str, start_span: int | None = None, end_span: int | None = None
    ) -> Symbol:
        scope = self.scopes[-1]
        if name in scope.symbols:
            self._report_error(
                f"Duplicate declaration: {name}", "SEM001", start_span, end_span
            )
            return scope.symbols[name]
        return scope.declare(name, start_span, end_span)

    def resolve(
        self, name: str, start_span: int | None = None, end_span: int | None = None
    ) -> Symbol | None:
        for scope in reversed(self.scopes):
            symbol = scope.resolve(name)
            if symbol is not None:
                return symbol
        self._report_error(
            f"Undefined identifier: {name}", "SEM002", start_span, end_span
        )
        return None

    def _report_error(
        self, message: str, code: str, start_span: int | None, end_span: int | None
    ) -> None:
        if self.reporter is None:
            return
        line = None
        column = None
        if start_span is not None:
            line = 1
            column = start_span + 1
        diagnostic = Diagnostic(
            Severity.ERROR,
            ErrorCode(code, message),
            message,
            line,
            column,
        )
        self.reporter.report(diagnostic)
