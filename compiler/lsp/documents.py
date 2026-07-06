"""Document manager — tracks open files and manages compilation state."""

from __future__ import annotations

from typing import Any, cast

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import ASTNode, ProgramNode
from compiler.diagnostics import DiagnosticReporter
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable
from compiler.source import Source


class Document:
    """State for a single open document."""

    def __init__(self, uri: str, text: str) -> None:
        self.uri = uri
        self._text = text
        self._source: Source | None = None
        self._ast: ASTNode | None = None
        self._symbol_table: SymbolTable | None = None
        self._diagnostics: list[Any] = []
        self._dirty = True

    @property
    def text(self) -> str:
        return self._text

    @text.setter
    def text(self, value: str) -> None:
        self._text = value
        self._dirty = True

    @property
    def source(self) -> Source | None:
        return self._source

    @property
    def ast(self) -> ASTNode | None:
        return self._ast

    @property
    def symbol_table(self) -> SymbolTable | None:
        return self._symbol_table

    @property
    def diagnostics(self) -> list[Any]:
        return self._diagnostics

    def compile(self) -> None:
        """Run full compilation pipeline on this document."""
        reporter = DiagnosticReporter()
        try:
            lexer = Lexer()
            tokens = lexer.tokenize(self._text)
            parser = Parser(tokens)
            cst = parser.parse_program()
            ast = ASTBuilder().build(cst)
            self._ast = ast

            symbol_table = SymbolTable(reporter)
            symbol_table.set_source_text(self._text)
            analyzer = SemanticAnalyzer(symbol_table)
            analyzer.analyze_module(cast(ProgramNode, ast))

            self._symbol_table = symbol_table
            self._diagnostics = reporter.diagnostics
            self._source = None
        except Exception as exc:
            self._ast = None
            self._symbol_table = None
            self._diagnostics = reporter.diagnostics
            if reporter.error_count == 0:
                self._diagnostics.append(
                    _make_diagnostic_from_exception(exc, self._text)
                )
        self._dirty = False

    def ensure_compiled(self) -> None:
        """Recompile if the document is dirty."""
        if self._dirty:
            self.compile()


def _make_diagnostic_from_exception(exc: Exception, text: str) -> Any:
    """Create a generic diagnostic from an unexpected exception."""
    from compiler.diagnostics import Diagnostic, ErrorCode, Severity

    return Diagnostic(Severity.ERROR, ErrorCode("LSP000", str(exc)), str(exc), 1, 1)
