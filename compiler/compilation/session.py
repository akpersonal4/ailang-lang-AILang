"""Compilation session orchestrating multi-source compilation."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import cast

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import ProgramNode
from compiler.diagnostics import DiagnosticReporter
from compiler.lexer import Lexer
from compiler.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable
from compiler.source import Source

from .graph import DependencyGraph
from .resolution import ModuleResolver


class CompilationSession:
    """Manages multi-file compilation with module resolution.

    Accepts either:
    - A single entry point file for auto-discovery of imports
    - A list of paths for manual source management
    """

    def __init__(self, paths: Sequence[str | Path] | None = None) -> None:
        self._sources: dict[str, Source] = {}  # module_name -> Source
        self._asts: dict[str, ProgramNode] = {}  # module_name -> AST
        self._file_set: set[Path] = set()
        self._graph = DependencyGraph()
        self._root = Path(".").resolve()
        self._resolver = ModuleResolver(self._root)
        self._registration_order: list[str] = []  # Track explicit order

        if paths is not None:
            for p in paths:
                self.add_source(p)

    def source_count(self) -> int:
        """Return the number of registered source files."""
        return len(self._sources)

    @property
    def sources(self) -> list[Source]:
        """Return sources in compilation order (respecting registration order)."""
        order = self._graph.topological_sort()
        result = []
        for name in order:
            if name in self._sources:
                result.append(self._sources[name])
        return result

    def add_source(self, path: str | Path) -> Source:
        """Add a source file directly (for testing)."""
        file_path = Path(path).resolve()
        if file_path in self._file_set:
            raise ValueError(f"Duplicate source file: {file_path}")
        module_name = self._path_to_module_name(file_path)
        source = Source.from_file(str(file_path))
        self._sources[module_name] = source
        self._file_set.add(file_path)
        self._graph.add_module(module_name, str(file_path))
        self._registration_order.append(module_name)
        return source

    def compile(self) -> None:
        """Run full compilation pipeline on all registered sources.

        Raises:
            RuntimeError: If no source files are registered
        """
        if not self._sources:
            raise RuntimeError("No source files registered for compilation")
        # Compile all modules to AST
        for module_name in self._graph.topological_sort():
            if module_name not in self._asts:
                source = self._sources[module_name]
                lexer = Lexer()
                parser = Parser(lexer.tokenize(source.text))
                cst = parser.parse_program()
                ast = cast(ProgramNode, ASTBuilder().build(cst))
                self._asts[module_name] = ast

    def discover(self, entry_path: str | Path) -> None:
        """Discover all modules starting from an entry point.

        Traverses import declarations recursively and builds the
        dependency graph.
        """
        entry_file = Path(entry_path).resolve()
        self._discover_recursive(entry_file, None)
        self._compile_all()

    def _path_to_module_name(self, file_path: Path) -> str:
        """Convert a file path to a module name relative to root."""
        try:
            relative = file_path.relative_to(self._root)
        except ValueError:
            relative = file_path

        stem = relative.with_suffix("")
        return ".".join(stem.parts)

    def _discover_recursive(self, file_path: Path, importer: str | None) -> None:
        """Recursively discover modules and add to graph."""
        module_name = self._path_to_module_name(file_path)
        if module_name in self._sources:
            if importer is not None:
                self._graph.add_dependency(importer, module_name)
            return

        source = Source.from_file(str(file_path))
        self._sources[module_name] = source
        self._graph.add_module(module_name, str(file_path))
        self._registration_order.append(module_name)

        if importer is not None:
            self._graph.add_dependency(importer, module_name)

        # Parse and extract imports
        lexer = Lexer()
        parser = Parser(lexer.tokenize(source.text))
        cst = parser.parse_program()

        # Extract imports and discover them
        for child in cst.children:
            if hasattr(child, "kind") and child.kind == "ImportDeclaration":
                path_node = child.children[0]
                segments = []
                for segment_node in path_node.children:
                    if (
                        hasattr(segment_node, "token")
                        and segment_node.token is not None
                    ):
                        segments.append(segment_node.token.value)
                if segments:
                    try:
                        sub_path = self._resolver.resolve(tuple(segments))
                        self._discover_recursive(sub_path, module_name)
                    except Exception:
                        # Will be reported during semantic analysis
                        pass

    def _compile_all(self) -> None:
        """Compile all discovered modules in dependency order."""
        for module_name in self._graph.topological_sort():
            if module_name in self._sources:
                source = self._sources[module_name]
                lexer = Lexer()
                parser = Parser(lexer.tokenize(source.text))
                cst = parser.parse_program()
                ast = cast(ProgramNode, ASTBuilder().build(cst))
                self._asts[module_name] = ast

    def analyze(self, reporter: DiagnosticReporter | None = None) -> None:
        """Run semantic analysis on all modules.

        Performs cross-module symbol resolution.
        """
        symbol_table = SymbolTable(reporter)

        # First, register all exports from all modules
        for module_name, ast in self._asts.items():
            for child in ast.children:
                self._register_export(symbol_table, child, module_name)

        # Then analyze each module
        for module_name in self._graph.topological_sort():
            self._analyze_module(module_name, symbol_table)

    def _register_export(
        self, symbol_table: SymbolTable, node: object, module_name: str
    ) -> None:
        """Register a top-level declaration as an export."""
        from compiler.ast.nodes import (
            FunctionDeclarationNode,
            VariableDeclarationNode,
        )

        if isinstance(node, FunctionDeclarationNode):
            qualified_name = f"{module_name}.{node.name.name}"
            symbol_table.declare(qualified_name, node.start_span, node.end_span)
        elif isinstance(node, VariableDeclarationNode):
            qualified_name = f"{module_name}.{node.name.name}"
            symbol_table.declare(qualified_name, node.start_span, node.end_span)

    def _analyze_module(self, module_name: str, symbol_table: SymbolTable) -> None:
        """Analyze a single module."""
        analyzer = SemanticAnalyzer(symbol_table)
        analyzer.analyze(self._asts[module_name])
