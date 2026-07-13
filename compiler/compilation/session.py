"""Compilation session orchestrating multi-source compilation."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import cast as _cast

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
from .resolution import ModuleResolver, _read_package_entry


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

    def __init__(
        self,
        paths: Sequence[str | Path] | None = None,
        experimental_loops: bool = False,
    ) -> None:
        self._sources: dict[str, Source] = {}  # module_name -> Source
        self._asts: dict[str, ProgramNode] = {}  # module_name -> AST
        self._file_set: set[Path] = set()
        self._graph = DependencyGraph()
        self._root = Path(".").resolve()
        self._resolver = ModuleResolver(self._root)
        self._registration_order: list[str] = []  # Track explicit order
        self._cycle_detected: bool = False
        self._experimental_loops = experimental_loops
        self._pkg_stdlib_dirs: list[Path] = []

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
                parser = Parser(
                    lexer.tokenize(source.text),
                    source_path=file_path,
                    experimental_loops=self._experimental_loops,
                )
                cst = parser.parse_program()
                ast = _cast(ProgramNode, ASTBuilder().build(cst))
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
        found = False
        current = self._root.resolve()
        while True:
            stdlib_dir = current / "stdlib"
            if stdlib_dir.exists():
                found = True
                self._register_stdlib_dir(stdlib_dir)
            if current == current.parent:
                break
            current = current.parent

        # Fallback: use the same logic as CLI's _find_stdlib()
        if not found:
            self._try_discover_stdlib_via_package()

    def _register_stdlib_dir(self, stdlib_dir: Path) -> None:
        """Register all .ail files in a stdlib directory."""
        for path in sorted(stdlib_dir.rglob("*.ail")):
            if not path.is_file():
                continue
            module_name = self._path_to_module_name(path)
            if module_name in self._sources:
                existing = self._sources[module_name].path
                if existing and "stdlib" in str(existing):
                    continue
            source = Source.from_file(str(path))
            self._sources[module_name] = source
            self._graph.add_module(module_name, str(path))
            self._registration_order.append(module_name)

    def _try_discover_stdlib_via_package(self) -> None:
        """Try to locate stdlib via the compiler package installation path."""
        from pathlib import Path as _Path
        this_file = _Path(__file__).resolve()
        # compiler/compilation/session.py -> compiler/ -> site-packages/
        pkg_dir = this_file.parent.parent
        candidates = [
            pkg_dir / "stdlib",                 # site-packages/stdlib/
            pkg_dir.parent / "stdlib",           # repo root in dev tree
        ]
        import site as _site
        for site_dir in _site.getsitepackages():
            candidates.append(_Path(site_dir) / "ailang" / "stdlib")
            candidates.append(_Path(site_dir) / "stdlib")
        seen: set[str] = set()
        for cand in candidates:
            if cand.is_dir() and cand not in seen:
                seen.add(str(cand))
                self._pkg_stdlib_dirs.append(cand)
                self._register_stdlib_dir(cand)

    def _path_to_module_name(self, file_path: Path) -> str:
        """Convert a file path to a module name relative to root or stdlib.

        Walks up from self._root looking for the stdlib/ directory that
        contains the file, to handle cases where stdlib is discovered
        via upward traversal (e.g. root is a subdirectory of the project).
        Also handles packages installed under lib/ by using the package
        name as the module name (e.g. lib/mylib/main.ail -> "mylib").
        """
        resolved_file = file_path.resolve()
        resolved_root = self._root.resolve()

        current = resolved_root
        while True:
            stdlib_dir = current / "stdlib"
            if stdlib_dir in resolved_file.parents or resolved_file == stdlib_dir:
                try:
                    relative = resolved_file.relative_to(stdlib_dir)
                except ValueError:
                    relative = resolved_file
                stem = relative.with_suffix("")
                return ".".join(stem.parts)
            if current == current.parent:
                break
            current = current.parent

        # Check against stdlib dirs discovered via package fallback.
        for pkg_stdlib_dir in self._pkg_stdlib_dirs:
            try:
                relative = resolved_file.relative_to(pkg_stdlib_dir)
                stem = relative.with_suffix("")
                return ".".join(stem.parts)
            except ValueError:
                continue

        # Check if the file is inside a lib/<pkg>/ directory with an ail.toml.
        # The entry file (from ail.toml) gets the package name as its module name.
        # Other files in the package get their stem as module name.
        lib_dir = resolved_root / "lib"
        if lib_dir in resolved_file.parents:
            try:
                relative = resolved_file.relative_to(lib_dir)
            except ValueError:
                relative = resolved_file
            parts = relative.with_suffix("").parts
            if len(parts) >= 2:
                pkg_name = parts[0]
                file_stem = ".".join(parts[1:])
                # If it's the entry file for the package, use the package name
                pkg_toml = lib_dir / pkg_name / "ail.toml"
                if pkg_toml.exists():
                    pkg_entry = _read_package_entry(pkg_toml)
                    pkg_entry_stem = Path(pkg_entry).with_suffix("").as_posix().replace("/", ".")
                    if file_stem == pkg_entry_stem:
                        return pkg_name
                # Otherwise use the file stem as module name
                return file_stem
            if parts:
                return parts[0]

        try:
            relative = resolved_file.relative_to(resolved_root)
        except ValueError:
            relative = resolved_file

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
            parser = Parser(
                tokens, reporter, source_path=str(source.path),
                experimental_loops=self._experimental_loops,
            )
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
                    parser = Parser(
                        tokens, reporter, source_path=file_path,
                        experimental_loops=self._experimental_loops,
                    )
                    cst = parser.parse_program()
                    ast = _cast(ProgramNode, ASTBuilder().build(cst))
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

        # Collect all top-level function names for forward-reference detection.
        from compiler.ast.nodes import (
            FunctionDeclarationNode,
            VariableDeclarationNode,
        )

        all_function_names: set[str] = set()
        for module_name, ast in self._asts.items():
            for child in ast.children:
                if isinstance(child, FunctionDeclarationNode):
                    all_function_names.add(child.name.name)

        # Pre-populate the symbol table's forward-reference set.
        symbol_table._all_function_names = all_function_names

        # First, register exported symbols from all modules.
        # Always declare the module namespace first so that ``import module``
        # can resolve the module name, regardless of whether a top-level
        # declaration shares the module name.
        for module_name, ast in self._asts.items():
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
            sym = symbol_table.declare(qualified_name, node.start_span, node.end_span)
            sym.param_count = len(node.parameters)
            sym.required_param_count = sum(
                1 for p in node.parameters if p.default_value is None
            )
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

        # ------------------------------------------------------------------
        # Incremental compilation support
        # ------------------------------------------------------------------

    def compile_module_to_ast(
        self, module_name: str, reporter: DiagnosticReporter | None = None
    ) -> bool:
        """Compile a single module to AST (lex + parse + build).

        Returns ``True`` on success (even if the AST is empty due to errors).
        """
        if module_name not in self._sources:
            return False
        source = self._sources[module_name]
        file_path = str(source.path)
        try:
            lexer = Lexer(reporter, source_path=file_path)
            tokens = lexer.tokenize(source.text)
            parser = Parser(
                tokens, reporter, source_path=file_path,
                experimental_loops=self._experimental_loops,
            )
            cst = parser.parse_program()
            ast = _cast(ProgramNode, ASTBuilder().build(cst))
            self._asts[module_name] = ast
            return True
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
            return False
        except ValueError as e:
            msg = str(e) or "Compilation error"
            if reporter is not None:
                reporter.report(Diagnostic(
                    Severity.ERROR, ErrorCode("CMP001", msg), msg,
                    file_path=file_path,
                ))
            self._asts[module_name] = ProgramNode(())
            return False

    def get_dependents(self, module_name: str) -> list[str]:
        """Return list of modules that directly depend on *module_name*."""
        return [
            m for m in self._graph._edges
            if module_name in self._graph._edges[m]
        ]

    def get_transitive_dependents(self, module_name: str) -> list[str]:
        """Return all modules that transitively depend on *module_name*."""
        result: list[str] = []
        visited: set[str] = set()
        queue = [module_name]
        while queue:
            current = queue.pop(0)
            for dep_mod in self.get_dependents(current):
                if dep_mod not in visited:
                    visited.add(dep_mod)
                    result.append(dep_mod)
                    queue.append(dep_mod)
        return result

    def update_source_text(self, module_name: str, text: str) -> None:
        """Replace the source text for a module (for incremental recompiles)."""
        if module_name not in self._sources:
            return
        file_path = self._sources[module_name].path
        self._sources[module_name] = Source(path=file_path, text=text)

    def incremental_recompile(
        self, file_path: str, reporter: DiagnosticReporter
    ) -> tuple[bool, list[str]]:
        """Recompile a changed file and all its transitive dependents.

        Returns ``(success, list_of_affected_module_names)``.
        """
        fp = Path(file_path).resolve()

        module_name: str | None = None
        for name, src in self._sources.items():
            if Path(src.path).resolve() == fp:
                module_name = name
                break

        if module_name is None:
            reporter.report(Diagnostic(
                Severity.ERROR, ErrorCode("CMP001", f"File not in session: {file_path}"),
                f"File not in session: {file_path}", file_path=file_path,
            ))
            return False, []

        source_text = fp.read_text(encoding="utf-8")
        self.update_source_text(module_name, source_text)

        ok = self.compile_module_to_ast(module_name, reporter)
        if not ok:
            return False, [module_name]

        dependents = self.get_transitive_dependents(module_name)

        for dep_name in dependents:
            dep_path = self._sources[dep_name].path
            dep_text = dep_path.read_text(encoding="utf-8")
            self.update_source_text(dep_name, dep_text)
            self.compile_module_to_ast(dep_name, reporter)

        affected = [module_name] + dependents

        self._incremental_analyze(set(affected), reporter)

        return reporter.error_count == 0, affected

    def _incremental_analyze(
        self, affected: set[str], reporter: DiagnosticReporter | None = None
    ) -> None:
        """Re-run semantic analysis for a subset of modules.

        Cross-module exports are re-registered for *all* modules (fast),
        but deep analysis only runs for the affected modules.
        """
        from compiler.runtime.builtins import BUILTINS

        symbol_table = SymbolTable(reporter)

        for builtin_name in BUILTINS:
            symbol_table.declare(builtin_name)

        for module_name, ast in self._asts.items():
            symbol_table.declare_module_namespace(module_name)
            for child in ast.children:
                self._register_export(symbol_table, child, module_name)

        for module_name in self._graph.topological_sort():
            if module_name not in affected:
                continue
            if module_name not in self._asts:
                continue
            if module_name in self._sources:
                source = self._sources[module_name]
                symbol_table.set_source_text(source.text)
                symbol_table.set_file_path(str(source.path))
            self._analyze_module(module_name, symbol_table)

    def incremental_build_ir(self, module_name: str) -> ModuleIRBundle:
        """Build IR for the changed module and its transitive dependents.

        Returns a ``ModuleIRBundle`` containing only the affected modules.
        """
        dependents = self.get_transitive_dependents(module_name)
        affected = [module_name] + dependents

        bundle = ModuleIRBundle()
        ir_builder = IRBuilder()

        for mod_name in affected:
            if mod_name in self._asts:
                ast = self._asts[mod_name]
                ir = ir_builder.build(ast)
                bundle.module_irs[mod_name] = ir

        return bundle
