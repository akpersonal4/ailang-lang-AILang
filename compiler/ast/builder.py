"""CST-to-AST transformation for AILang.

Transforms a CST (produced by the parser) into an immutable AST
by discarding syntax-only tokens and preserving only semantics-
relevant structure with source spans.
"""

from __future__ import annotations

from typing import cast

from compiler.ast.nodes import (
    ASTNode,
    BinaryExpressionNode,
    BlockNode,
    CallExpressionNode,
    ExpressionStatementNode,
    FunctionDeclarationNode,
    IdentifierNode,
    IfStatementNode,
    NumberLiteralNode,
    ParameterNode,
    ProgramNode,
    ReturnStatementNode,
    StringLiteralNode,
    UnaryExpressionNode,
    VariableDeclarationNode,
)
from compiler.parser.nodes import CSTNode


class ASTBuilder:
    """Builds an immutable AST from a CST.

    Usage:
        builder = ASTBuilder()
        ast = builder.build(cst_root)
    """

    def build(self, node: CSTNode) -> ASTNode:
        """Transform a CST node into an AST node."""
        method_name = f"_build_{node.kind}"
        builder = getattr(self, method_name, None)
        if builder is not None:
            return cast(ASTNode, builder(node))
        raise ValueError(f"Unknown CST node kind: {node.kind}")

    # ------------------------------------------------------------------
    # Top-level
    # ------------------------------------------------------------------

    @staticmethod
    def _build_Program(node: CSTNode) -> ProgramNode:
        children = tuple(
            child
            for c in node.children
            if (child := ASTBuilder._try_build(c)) is not None
        )
        return ProgramNode(children, start_span=node.start_span, end_span=node.end_span)

    @staticmethod
    def _build_Block(node: CSTNode) -> BlockNode:
        statements = tuple(
            child
            for c in node.children
            if (child := ASTBuilder._try_build(c)) is not None
        )
        return BlockNode(statements, start_span=node.start_span, end_span=node.end_span)

    # ------------------------------------------------------------------
    # Declarations
    # ------------------------------------------------------------------

    @staticmethod
    def _build_VariableDeclaration(node: CSTNode) -> VariableDeclarationNode:
        name = ASTBuilder._try_build(node.children[0])
        assert isinstance(name, IdentifierNode)
        initializer = ASTBuilder._try_build(node.children[1])
        assert initializer is not None
        return VariableDeclarationNode(
            name=name,
            initializer=initializer,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    @staticmethod
    def _build_FunctionDeclaration(node: CSTNode) -> FunctionDeclarationNode:
        name_node = ASTBuilder._try_build(node.children[0])
        assert isinstance(name_node, IdentifierNode)

        # ParameterList CST node
        params_cst = node.children[1]
        parameters: tuple[ParameterNode, ...] = ()
        for child in params_cst.children:
            param = ASTBuilder._try_build(child)
            if isinstance(param, IdentifierNode):
                parameters = parameters + (
                    ParameterNode(
                        name=param.name,
                        start_span=param.start_span,
                        end_span=param.end_span,
                    ),
                )

        body = ASTBuilder._try_build(node.children[2])
        assert isinstance(body, BlockNode)

        return FunctionDeclarationNode(
            name=name_node,
            parameters=parameters,
            body=body,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------

    @staticmethod
    def _build_ExpressionStatement(node: CSTNode) -> ExpressionStatementNode:
        expr = ASTBuilder._try_build(node.children[0])
        assert expr is not None
        return ExpressionStatementNode(
            expression=expr,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    @staticmethod
    def _build_ReturnStatement(node: CSTNode) -> ReturnStatementNode:
        value = ASTBuilder._try_build(node.children[0])
        assert value is not None
        return ReturnStatementNode(
            value=value,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    @staticmethod
    def _build_IfStatement(node: CSTNode) -> IfStatementNode:
        condition = ASTBuilder._try_build(node.children[0])
        assert condition is not None

        then_cst = node.children[1]
        then_block = ASTBuilder._try_build(then_cst)
        assert isinstance(then_block, BlockNode)

        else_block: BlockNode | None = None
        if len(node.children) > 2:
            else_cst = node.children[2]
            # Nested if/else is lifted to an else-if block
            if else_cst.kind == "IfStatement":
                inner = ASTBuilder._build_IfStatement(else_cst)
                # Wrap in a synthetic Block for uniform AST
                else_block = BlockNode(
                    statements=(inner,),
                    start_span=else_cst.start_span,
                    end_span=else_cst.end_span,
                )
            else:
                built = ASTBuilder._try_build(else_cst)
                assert isinstance(built, BlockNode)
                else_block = built

        return IfStatementNode(
            condition=condition,
            then_block=then_block,
            else_block=else_block,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    # ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------

    @staticmethod
    def _build_BinaryExpression(node: CSTNode) -> BinaryExpressionNode:
        left = ASTBuilder._try_build(node.children[0])
        right = ASTBuilder._try_build(node.children[1])
        assert left is not None and right is not None
        assert node.token is not None
        return BinaryExpressionNode(
            left=left,
            right=right,
            operator=node.token.value,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    @staticmethod
    def _build_UnaryExpression(node: CSTNode) -> UnaryExpressionNode:
        operand = ASTBuilder._try_build(node.children[0])
        assert operand is not None
        assert node.token is not None
        return UnaryExpressionNode(
            operand=operand,
            operator=node.token.value,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    @staticmethod
    def _build_CallExpression(node: CSTNode) -> CallExpressionNode:
        callee = ASTBuilder._try_build(node.children[0])
        assert callee is not None

        # ArgumentList CST node
        arg_cst = node.children[1]
        arguments: tuple[ASTNode, ...] = ()
        for child in arg_cst.children:
            arg = ASTBuilder._try_build(child)
            if arg is not None:
                arguments = arguments + (arg,)

        return CallExpressionNode(
            callee=callee,
            arguments=arguments,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    @staticmethod
    def _build_AssignmentExpression(node: CSTNode) -> BinaryExpressionNode:
        left = ASTBuilder._try_build(node.children[0])
        right = ASTBuilder._try_build(node.children[1])
        assert left is not None and right is not None
        return BinaryExpressionNode(
            left=left,
            right=right,
            operator="=",
            start_span=node.start_span,
            end_span=node.end_span,
        )

    # ------------------------------------------------------------------
    # Literals and identifiers
    # ------------------------------------------------------------------

    @staticmethod
    def _build_Identifier(node: CSTNode) -> IdentifierNode:
        assert node.token is not None
        return IdentifierNode(
            name=node.token.value,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    @staticmethod
    def _build_NumberLiteral(node: CSTNode) -> NumberLiteralNode:
        assert node.token is not None
        return NumberLiteralNode(
            value=node.token.value,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    @staticmethod
    def _build_StringLiteral(node: CSTNode) -> StringLiteralNode:
        assert node.token is not None
        return StringLiteralNode(
            value=node.token.value,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _try_build(node: CSTNode) -> ASTNode | None:
        """Build an AST node from a CST node, returning None for structural nodes
        that do not map to AST nodes (e.g. ParameterList, ArgumentList)."""
        builder = getattr(ASTBuilder, f"_build_{node.kind}", None)
        if builder is not None:
            return cast(ASTNode, builder(node))
        return None
