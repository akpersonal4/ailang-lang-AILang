"""Lexical scope symbol table for AILang semantic analysis."""

from __future__ import annotations

from dataclasses import dataclass

from compiler.diagnostics import Diagnostic, DiagnosticReporter, ErrorCode, Severity


@dataclass
class Symbol:
    name: str
    start_span: int | None = None
    end_span: int | None = None
    type: object | None = None


class Scope:
    def __init__(self, parent: Scope | None = None) -> None:
        self.parent = parent
        self.symbols: dict[str, Symbol] = {}

    def declare(
        self,
        name: str,
        start_span: int | None = None,
        end_span: int | None = None,
        type: object | None = None,
    ) -> Symbol:
        if name in self.symbols:
            return self.symbols[name]
        symbol = Symbol(name, start_span, end_span, type)
        self.symbols[name] = symbol
        return symbol

    def resolve(self, name: str) -> Symbol | None:
        if name in self.symbols:
            return self.symbols[name]
        if self.parent is not None:
            return self.parent.resolve(name)
        return None


class SymbolTable:
    def __init__(
        self,
        reporter: DiagnosticReporter | None = None,
    ) -> None:
        self.reporter = reporter
        self._source_lines: list[str] | None = None
        self.scopes: list[Scope] = [Scope()]
        self.node_scopes: dict[int, Scope] = {}

    def set_source_text(self, source_text: str | None) -> None:
        """Set source text for offset-to-line/col conversion.

        Must be called before analyzing each module in a multi-module
        session so that error positions reference the correct file.
        """
        self._source_lines = source_text.split("\n") if source_text else None

    def enter_scope(self, node: object | None = None) -> None:
        if node is not None and id(node) in self.node_scopes:
            self.scopes.append(self.node_scopes[id(node)])
        else:
            parent = self.scopes[-1] if self.scopes else None
            new_scope = Scope(parent=parent)
            self.scopes.append(new_scope)
            if node is not None:
                self.node_scopes[id(node)] = new_scope

    def exit_scope(self) -> None:
        if len(self.scopes) > 1:
            self.scopes.pop()

    def declare(
        self,
        name: str,
        start_span: int | None = None,
        end_span: int | None = None,
        type: object | None = None,
    ) -> Symbol:
        scope = self.scopes[-1]
        if name in scope.symbols:
            self._report_error(
                f"Duplicate declaration: {name}", "SEM001", start_span, end_span
            )
            return scope.symbols[name]
        return scope.declare(name, start_span, end_span, type)

    def declare_module_namespace(
        self,
        name: str,
        start_span: int | None = None,
        end_span: int | None = None,
        type: object | None = None,
    ) -> Symbol:
        scope = self.scopes[-1]
        if name in scope.symbols:
            return scope.symbols[name]
        symbol = Symbol(name, start_span, end_span, type)
        scope.symbols[name] = symbol
        return symbol

    def resolve(
        self, name: str, start_span: int | None = None, end_span: int | None = None
    ) -> Symbol | None:
        active_scope = self.scopes[-1]
        symbol = active_scope.resolve(name)
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
        if start_span is not None and self._source_lines is not None:
            # Convert character offset to 1-based line/column
            line = 1
            col_offset = start_span
            for lineno, src_line in enumerate(self._source_lines, 1):
                if col_offset <= len(src_line):
                    line = lineno
                    column = col_offset + 1
                    break
                col_offset -= len(src_line) + 1  # +1 for newline char
        elif start_span is not None:
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
