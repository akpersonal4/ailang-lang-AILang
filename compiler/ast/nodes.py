"""Immutable AST node definitions for AILang.

Each node preserves source spans for diagnostics and debugging.
Syntax-only tokens (semicolons, commas, braces, parentheses) are
not represented in the AST.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class ProgramNode:
    children: tuple[ASTNode, ...]
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class BlockNode:
    statements: tuple[ASTNode, ...]
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class VariableDeclarationNode:
    name: IdentifierNode
    initializer: ASTNode
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class FunctionDeclarationNode:
    name: IdentifierNode
    parameters: tuple[ParameterNode, ...]
    body: BlockNode
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class ParameterNode:
    name: str
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class ExpressionStatementNode:
    expression: ASTNode
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class ReturnStatementNode:
    value: ASTNode
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class IfStatementNode:
    condition: ASTNode
    then_block: BlockNode
    else_block: BlockNode | None = None
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class BinaryExpressionNode:
    left: ASTNode
    right: ASTNode
    operator: str
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class UnaryExpressionNode:
    operand: ASTNode
    operator: str
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class CallExpressionNode:
    callee: ASTNode
    arguments: tuple[ASTNode, ...]
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class MemberAccessNode:
    """Represents qualified member access: object.member"""

    receiver: ASTNode
    member: IdentifierNode
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class ImportDeclarationNode:
    """Represents an import declaration: import path as alias"""

    module_path: tuple[str, ...]
    alias: str | None = None
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class IdentifierNode:
    name: str
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class NumberLiteralNode:
    value: str
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class StringLiteralNode:
    value: str
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class BooleanLiteralNode:
    value: bool
    start_span: int | None = None
    end_span: int | None = None


ASTNode = (
    ProgramNode
    | BlockNode
    | VariableDeclarationNode
    | FunctionDeclarationNode
    | ParameterNode
    | ExpressionStatementNode
    | ReturnStatementNode
    | IfStatementNode
    | BinaryExpressionNode
    | UnaryExpressionNode
    | CallExpressionNode
    | MemberAccessNode
    | ImportDeclarationNode
    | IdentifierNode
    | NumberLiteralNode
    | StringLiteralNode
    | BooleanLiteralNode
)
"""Union type for all AST node kinds."""
