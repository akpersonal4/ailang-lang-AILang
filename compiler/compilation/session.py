"""Compilation session orchestrating multi-source compilation."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import cast

from compiler.ast.builder import ASTBuilder
from compiler.ast.nodes import ProgramNode
from compiler.diagnostics import Diagnostic, DiagnosticReporter, ErrorCode, Severity
from compiler.ir.builder import IRBuilder
from compiler.ir.nodes import ProgramIR
from compiler.lexer import Lexer, LexicalError
from compiler.parser import Parser
from compiler.semantic.analyzer import SemanticAnalyzer
from compiler.semantic.symbol_table import SymbolTable
from compiler.source import Source

from .graph import DependencyGraph
from .resolution import ModuleResolver


class ModuleIRBundle:
    """Holds all IR for a compilation session with module metadata."""

    def __init__(self) -> None:
        self.module_irs: dict[str, ProgramIR] = {}  # module_name -> IR
        self.initialized: set[str] = set()

    def get_or_initialize(self, module_name: str) -> ProgramIR | None:
        """Return IR for module, marking it as initialized."""
        if module_name not in self.module_irs:
            return None
        self.initialized.add(module_name)
        return self.module_irs[module_name]


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
        self._cycle_detected: bool = False

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
                file_path = str(source.path)
                lexer = Lexer(source_path=file_path)
                parser = Parser(lexer.tokenize(source.text), source_path=file_path)
                cst = parser.parse_program()
                ast = cast(ProgramNode, ASTBuilder().build(cst))
                self._asts[module_name] = ast

    def discover(self, entry_path: str | Path,
                 reporter: DiagnosticReporter | None = None) -> None:
        """Discover all modules starting from an entry point.

        Traverses import declarations recursively and builds the
        dependency graph.
        """
        entry_file = Path(entry_path).resolve()
        self._discover_stdlib_modules()
        self._discover_recursive(entry_file, None, reporter)
        self._compile_all(reporter)

    def _discover_stdlib_modules(self) -> None:
        """Register standard library modules from the project tree."""
        current = self._root.resolve()
        while True:
            stdlib_dir = current / "stdlib"
            if stdlib_dir.exists():
                for path in sorted(stdlib_dir.rglob("*.ail")):
                    if not path.is_file():
                        continue
                    module_name = self._path_to_module_name(path)
                    if module_name in self._sources:
                        continue
                    source = Source.from_file(str(path))
                    self._sources[module_name] = source
                    self._graph.add_module(module_name, str(path))
                    self._registration_order.append(module_name)
            if current == current.parent:
                break
            current = current.parent

    def _path_to_module_name(self, file_path: Path) -> str:
        """Convert a file path to a module name relative to root or stdlib.

        Walks up from self._root looking for the stdlib/ directory that
        contains the file, to handle cases where stdlib is discovered
        via upward traversal (e.g. root is a subdirectory of the project).
        """
        current = self._root.resolve()
        while True:
            stdlib_dir = current / "stdlib"
            if stdlib_dir in file_path.parents or file_path == stdlib_dir:
                try:
                    relative = file_path.relative_to(stdlib_dir)
                except ValueError:
                    relative = file_path
                stem = relative.with_suffix("")
                return ".".join(stem.parts)
            if current == current.parent:
                break
            current = current.parent

        try:
            relative = file_path.relative_to(self._root)
        except ValueError:
            relative = file_path

        stem = relative.with_suffix("")
        return ".".join(stem.parts)

    def _discover_recursive(self, file_path: Path, importer: str | None,
                            reporter: DiagnosticReporter | None = None) -> None:
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
        try:
            lexer = Lexer(reporter, source_path=str(source.path))
            tokens = lexer.tokenize(source.text)
            parser = Parser(tokens, reporter, source_path=str(source.path))
            cst = parser.parse_program()
        except LexicalError:
            # Lexer error during discovery — skip import extraction
            return

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
                        self._discover_recursive(sub_path, module_name, reporter)
                    except Exception:
                        # Will be reported during semantic analysis
                        pass

    def _compile_all(self, reporter: DiagnosticReporter | None = None) -> None:
        """Compile all discovered modules in dependency order."""
        for module_name in self._graph.topological_sort():
            if module_name in self._asts:
                continue
            if module_name in self._sources:
                source = self._sources[module_name]
                file_path = str(source.path)
                try:
                    lexer = Lexer(reporter, source_path=file_path)
                    tokens = lexer.tokenize(source.text)
                    parser = Parser(tokens, reporter, source_path=file_path)
                    cst = parser.parse_program()
                    ast = cast(ProgramNode, ASTBuilder().build(cst))
                    self._asts[module_name] = ast
                except LexicalError as e:
                    if reporter is not None:
                        diag = Diagnostic(
                            e.diagnostic.severity,
                            e.diagnostic.error_code,
                            e.diagnostic.message,
                            e.diagnostic.line,
                            e.diagnostic.column,
                            file_path=file_path,
                        )
                        reporter.report(diag)
                    self._asts[module_name] = ProgramNode(())
                except ValueError as e:
                    msg = str(e) or "Compilation error"
                    if reporter is not None:
                        diag = Diagnostic(
                            Severity.ERROR,
                            ErrorCode("CMP001", msg),
                            msg,
                            file_path=file_path,
                        )
                        reporter.report(diag)
                    self._asts[module_name] = ProgramNode(())

    def analyze(self, reporter: DiagnosticReporter | None = None) -> None:
        """Run semantic analysis on all modules.

        Performs cross-module symbol resolution.
        Also reports circular import errors (MOD001).
        """
        # Check for cycles first
        cycle = self._graph.detect_cycle()
        if cycle is not None and reporter is not None:
            from compiler.diagnostics import (
                MOD001_CIRCULAR_IMPORT,
                Diagnostic,
                Severity,
            )

            modules = " → ".join(sorted(cycle))
            diagnostic = Diagnostic(
                Severity.ERROR,
                MOD001_CIRCULAR_IMPORT,
                f"Circular import detected: {modules}",
            )
            reporter.report(diagnostic)
            self._cycle_detected = True

        symbol_table = SymbolTable(reporter)

        # Pre-register built-in functions so semantic analysis does not flag
        # calls to e.g. ``print`` as undefined identifiers.
        from compiler.runtime.builtins import BUILTINS

        for builtin_name in BUILTINS:
            symbol_table.declare(builtin_name)

        # First, register exported symbols from all modules.
        from compiler.ast.nodes import (
            FunctionDeclarationNode,
            VariableDeclarationNode,
        )

        for module_name, ast in self._asts.items():
            has_same_name_declaration = any(
                (
                    isinstance(child, FunctionDeclarationNode)
                    and child.name.name == module_name.split(".")[-1]
                )
                or (
                    isinstance(child, VariableDeclarationNode)
                    and child.name.name == module_name.split(".")[-1]
                )
                for child in ast.children
            )
            if not has_same_name_declaration:
                symbol_table.declare_module_namespace(module_name)
            for child in ast.children:
                self._register_export(symbol_table, child, module_name)

        # Then analyze each module in its own scope.
        for module_name in self._graph.topological_sort():
            if module_name in self._sources:
                source = self._sources[module_name]
                symbol_table.set_source_text(source.text)
                symbol_table.set_file_path(str(source.path))
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
        """Analyze a single module in a dedicated scope."""
        analyzer = SemanticAnalyzer(symbol_table)
        analyzer.analyze_module(self._asts[module_name])

    def build_ir(self) -> ModuleIRBundle:
        """Build IR for all compiled modules.

        Returns:
            ModuleIRBundle containing IR for each module in dependency order.
        """
        bundle = ModuleIRBundle()
        ir_builder = IRBuilder()

        for module_name in self._graph.topological_sort():
            if module_name in self._asts:
                ast = self._asts[module_name]
                ir = ir_builder.build(ast)
                bundle.module_irs[module_name] = ir

        return bundle

    def type_check(self, reporter: DiagnosticReporter | None = None) -> None:
        """Run type checking on all modules.

        Performs cross-module type checking.
        """
        from compiler.types.checker import TypeChecker

        local_reporter = reporter or DiagnosticReporter()

        # Type check each module (type checking uses its own symbol resolution)
        for module_name in self._graph.topological_sort():
            if module_name in self._asts:
                source_text_tc = (
                    self._sources[module_name].text
                    if module_name in self._sources
                    else None
                )
                type_checker = TypeChecker(
                    SymbolTable(), local_reporter, source_text=source_text_tc
                )
                type_checker.check(self._asts[module_name])
