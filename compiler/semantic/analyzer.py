"""Semantic analyzer for AILang.

Performs lexical scope analysis, declaration registration,
and identifier resolution on the AST.
"""

from __future__ import annotations

from compiler.ast.nodes import (
    ASTNode,
    BinaryExpressionNode,
    BlockNode,
    BooleanLiteralNode,
    CallExpressionNode,
    ExpressionStatementNode,
    ForStatementNode,
    FunctionDeclarationNode,
    IdentifierNode,
    IfStatementNode,
    ImportDeclarationNode,
    MemberAccessNode,
    NumberLiteralNode,
    ProgramNode,
    ReturnStatementNode,
    StringLiteralNode,
    UnaryExpressionNode,
    VariableDeclarationNode,
)
from compiler.diagnostics import (
    SEM003_WRONG_ARG_COUNT,
    Diagnostic,
    Severity,
)
from compiler.semantic.symbol_table import SymbolTable


class SemanticAnalyzer:
    """Analyzes an AST for semantic correctness.

    Usage:
        analyzer = SemanticAnalyzer()
        analyzer.analyze(ast_root)
    """

    def __init__(self, symbol_table: SymbolTable | None = None) -> None:
        self.symbol_table = symbol_table or SymbolTable()
        # Tracks qualified names that have been explicitly imported by the
        # user in the current analysis pass – distinct from symbols
        # pre-registered by CompilationSession._register_export.
        self._imported_names: set[str] = set()

    def analyze(self, node: ASTNode) -> None:
        method_name = f"_analyze_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is not None:
            method(node)

    def analyze_module(self, node: ProgramNode) -> None:
        """Analyze a module's program node in its own scope."""
        self.symbol_table.enter_scope(node)
        try:
            self.analyze(node)
        finally:
            self.symbol_table.exit_scope()

    # ------------------------------------------------------------------
    # Top-level
    # ------------------------------------------------------------------

    def _analyze_ProgramNode(self, node: ProgramNode) -> None:
        for child in node.children:
            self.analyze(child)

    # ------------------------------------------------------------------
    # Declarations
    # ------------------------------------------------------------------

    def _analyze_VariableDeclarationNode(self, node: VariableDeclarationNode) -> None:
        self.symbol_table.declare(
            node.name.name, node.name.start_span, node.name.end_span
        )
        self.analyze(node.initializer)

    def _analyze_FunctionDeclarationNode(self, node: FunctionDeclarationNode) -> None:
        sym = self.symbol_table.declare(
            node.name.name, node.name.start_span, node.name.end_span
        )
        sym.param_count = len(node.parameters)
        sym.required_param_count = sum(
            1 for p in node.parameters if p.default_value is None
        )
        # Analyze default value expressions in the enclosing scope
        for parameter in node.parameters:
            if parameter.default_value is not None:
                self.analyze(parameter.default_value)
        self.symbol_table.enter_scope(node)
        for parameter in node.parameters:
            self.symbol_table.declare(
                parameter.name, parameter.start_span, parameter.end_span
            )
        self.analyze(node.body)
        self.symbol_table.exit_scope()

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    def _analyze_ExpressionStatementNode(self, node: ExpressionStatementNode) -> None:
        self.analyze(node.expression)

    def _analyze_ReturnStatementNode(self, node: ReturnStatementNode) -> None:
        self.analyze(node.value)

    def _analyze_IfStatementNode(self, node: IfStatementNode) -> None:
        self.analyze(node.condition)
        self.analyze(node.then_block)
        if node.else_block is not None:
            self.analyze(node.else_block)

    def _analyze_ForStatementNode(self, node: ForStatementNode) -> None:
        self.symbol_table.enter_scope(node)
        self.symbol_table.declare(
            node.variable.name, node.variable.start_span, node.variable.end_span
        )
        self.analyze(node.iterable)
        self.analyze(node.body)
        self.symbol_table.exit_scope()

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def _analyze_BinaryExpressionNode(self, node: BinaryExpressionNode) -> None:
        self.analyze(node.left)
        self.analyze(node.right)

    def _analyze_UnaryExpressionNode(self, node: UnaryExpressionNode) -> None:
        self.analyze(node.operand)

    def _analyze_ImportDeclarationNode(self, node: ImportDeclarationNode) -> None:
        """Analyze an import declaration and declare the imported symbol.

        When called through a CompilationSession, the session pre-registers all
        exported qualified names (e.g. ``math.add``) before analysis begins.
        This method uses that pre-registration to validate that the imported
        symbol actually exists (MOD004) and to skip duplicate imports (MOD002).

        Reports:
        - MOD002 if the same qualified name was already imported in this scope
        - MOD004 if the qualified name was never exported by any discovered module
        """
        from compiler.diagnostics import (
            MOD002_DUPLICATE_IMPORT,
            MOD004_SYMBOL_NOT_FOUND,
        )

        module_path = ".".join(node.module_path)

        scopes = self.symbol_table.scopes
        current_scope = scopes[-1] if scopes else None

        # ------------------------------------------------------------------
        # Duplicate-import guard (MOD002)
        # Use _imported_names (not the symbol table) to detect duplicate user
        # imports, since the session may pre-register the same qualified name
        # via _register_export before analysis begins.
        # ------------------------------------------------------------------
        if module_path in self._imported_names:
            if self.symbol_table.reporter is not None:
                diagnostic = Diagnostic(
                    Severity.WARNING,
                    MOD002_DUPLICATE_IMPORT,
                    f"Duplicate import of {module_path}",
                    None,
                    None,
                    file_path=self.symbol_table._file_path,
                )
                self.symbol_table.reporter.report(diagnostic)
            return

        # ------------------------------------------------------------------
        # Symbol existence check (MOD004)
        # When a CompilationSession is used it pre-declares every exported
        # qualified name via _register_export before analysis begins.
        # If the qualified name is absent from the symbol table at this point
        # it means no discovered module exported that symbol.
        # In standalone mode (no reporter) we skip this check and just
        # declare the name so MemberAccess resolution can proceed.
        # ------------------------------------------------------------------
        already_registered = current_scope is not None and (
            current_scope.resolve(module_path) is not None
        )

        if not already_registered and self.symbol_table.reporter is not None:
            # Check the full scope chain (not just current scope)
            full_chain_symbol = self.symbol_table.scopes[-1].resolve(module_path)
            if full_chain_symbol is None:
                # The symbol was never exported by any module in the session.
                diagnostic = Diagnostic(
                    Severity.ERROR,
                    MOD004_SYMBOL_NOT_FOUND,
                    f"Symbol not found in module: {module_path}",
                    None,
                    None,
                    file_path=self.symbol_table._file_path,
                )
                self.symbol_table.reporter.report(diagnostic)
                return

        # ------------------------------------------------------------------
        # Declaration
        # Only declare the qualified name if it is not already in the symbol
        # table.  ``_register_export`` pre-registers all exported qualified
        # names (e.g. ``math.add``) before analysis begins; calling
        # ``symbol_table.declare`` a second time for the same name would
        # trigger a spurious "Duplicate declaration" error.
        # ------------------------------------------------------------------
        self._imported_names.add(module_path)

        # ``already_registered`` was resolved against the full scope chain
        # above; only declare when the name is genuinely absent.
        if not already_registered:
            self.symbol_table.declare(module_path, node.start_span, node.end_span)

        root = node.module_path[0]
        if len(node.module_path) > 1 and (
            current_scope is None or current_scope.resolve(root) is None
        ):
            self.symbol_table.declare(root, node.start_span, node.end_span)

        if node.alias is not None:
            self.symbol_table.declare(node.alias, node.start_span, node.end_span)

    def _analyze_MemberAccessNode(self, node: MemberAccessNode) -> None:
        # When the receiver is a plain identifier that names an imported module
        # namespace (e.g. "math" in "math.add()") it was already declared by
        # _analyze_ImportDeclarationNode.  Delegating to the generic
        # _analyze_IdentifierNode path works correctly because the namespace is
        # now in the symbol table; we simply recurse normally.
        self.analyze(node.receiver)
        # The member identifier is part of the qualified import path and does
        # not exist as a standalone symbol – skip independent resolution.
        # (Type-checker / IR builder operate on the full qualified name.)

    def _analyze_CallExpressionNode(self, node: CallExpressionNode) -> None:
        self.analyze(node.callee)
        self._check_call_arity(node)
        for argument in node.arguments:
            self.analyze(argument)

    def _check_call_arity(self, node: CallExpressionNode) -> None:
        callee = node.callee
        symbol = None

        if isinstance(callee, IdentifierNode):
            func_name = callee.name
            symbol = self.symbol_table.resolve(
                func_name, callee.start_span, callee.end_span
            )
        elif isinstance(callee, MemberAccessNode) and isinstance(
            callee.receiver, IdentifierNode
        ):
            func_name = callee.receiver.name + "." + callee.member.name
            active = self.symbol_table.scopes[-1]
            symbol = active.resolve(func_name) if active else None
        else:
            return

        if symbol is None or symbol.param_count is None:
            return

        arg_count = len(node.arguments)
        min_required = (
            symbol.required_param_count
            if symbol.required_param_count is not None
            else symbol.param_count
        )
        if arg_count < min_required or arg_count > symbol.param_count:
            if self.symbol_table.reporter is not None:
                diagnostic = Diagnostic(
                    Severity.ERROR,
                    SEM003_WRONG_ARG_COUNT,
                    f"Function '{func_name}' expects {min_required}-{symbol.param_count} argument(s), got {arg_count}",
                    None,
                    None,
                    file_path=self.symbol_table._file_path,
                )
                self.symbol_table.reporter.report(diagnostic)

    # ------------------------------------------------------------------
    # Literals and identifiers
    # ------------------------------------------------------------------

    def _analyze_IdentifierNode(self, node: IdentifierNode) -> None:
        self.symbol_table.resolve(node.name, node.start_span, node.end_span)

    def _analyze_NumberLiteralNode(self, node: NumberLiteralNode) -> None:
        return

    def _analyze_StringLiteralNode(self, node: StringLiteralNode) -> None:
        return

    def _analyze_BooleanLiteralNode(self, node: BooleanLiteralNode) -> None:
        return

    def _analyze_BlockNode(self, node: BlockNode) -> None:
        self.symbol_table.enter_scope(node)
        for statement in node.statements:
            self.analyze(statement)
        self.symbol_table.exit_scope()
