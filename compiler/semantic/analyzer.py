"""Semantic analyzer for AILang.

Performs lexical scope analysis, declaration registration,
and identifier resolution on the AST.
"""

from __future__ import annotations

from compiler.ast.nodes import (
    ASTNode,
    BinaryExpressionNode,
    BlockNode,
    CallExpressionNode,
    ExpressionStatementNode,
    FunctionDeclarationNode,
    IdentifierNode,
    IfStatementNode,
    MemberAccessNode,
    NumberLiteralNode,
    ProgramNode,
    ReturnStatementNode,
    StringLiteralNode,
    UnaryExpressionNode,
    VariableDeclarationNode,
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

    def analyze(self, node: ASTNode) -> None:
        method_name = f"_analyze_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is not None:
            method(node)

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
        self.symbol_table.declare(
            node.name.name, node.name.start_span, node.name.end_span
        )
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

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    def _analyze_BinaryExpressionNode(self, node: BinaryExpressionNode) -> None:
        self.analyze(node.left)
        self.analyze(node.right)

    def _analyze_UnaryExpressionNode(self, node: UnaryExpressionNode) -> None:
        self.analyze(node.operand)

    def _analyze_MemberAccessNode(self, node: MemberAccessNode) -> None:
        self.analyze(node.receiver)
        self.analyze(node.member)

    def _analyze_CallExpressionNode(self, node: CallExpressionNode) -> None:
        self.analyze(node.callee)
        for argument in node.arguments:
            self.analyze(argument)

    # ------------------------------------------------------------------
    # Literals and identifiers
    # ------------------------------------------------------------------

    def _analyze_IdentifierNode(self, node: IdentifierNode) -> None:
        self.symbol_table.resolve(node.name, node.start_span, node.end_span)

    def _analyze_NumberLiteralNode(self, node: NumberLiteralNode) -> None:
        return

    def _analyze_StringLiteralNode(self, node: StringLiteralNode) -> None:
        return

    def _analyze_BlockNode(self, node: BlockNode) -> None:
        self.symbol_table.enter_scope(node)
        for statement in node.statements:
            self.analyze(statement)
        self.symbol_table.exit_scope()
