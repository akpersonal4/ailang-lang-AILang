"""IR Builder – lowers the AST into the intermediate representation.

The builder walks the immutable AST nodes and creates corresponding immutable
IR nodes defined in ``compiler.ir.nodes``. No optimisations or type checking are
performed – the AST has already been type‑checked.
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
    ImportDeclarationNode,
    MemberAccessNode,
    NumberLiteralNode,
    ProgramNode,
    ReturnStatementNode,
    StringLiteralNode,
    UnaryExpressionNode,
    VariableDeclarationNode,
)

from .nodes import (
    AssignmentIR,
    BinaryOperationIR,
    BlockIR,
    CallIR,
    ExpressionStatementIR,
    FunctionIR,
    IfIR,
    IRExpression,
    IRNode,
    LiteralIR,
    MemberAccessIR,
    ProgramIR,
    ReturnIR,
    UnaryOperationIR,
    VariableDeclarationIR,
    VariableReferenceIR,
)


class IRBuilder:
    """Convert an AST into an IR tree.

    The public entry point is :meth:`build` which accepts a ``ProgramNode`` and
    returns a ``ProgramIR``.
    """

    def build(self, node: ProgramNode) -> ProgramIR:
        body = tuple(self._build_statement(child) for child in node.children)
        return ProgramIR(body=body, start_span=node.start_span, end_span=node.end_span)

    # ---------------------------------------------------------------------
    # Statement helpers
    # ---------------------------------------------------------------------
    def _build_statement(self, node: ASTNode) -> IRNode:
        method_name = f"_build_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise NotImplementedError(f"IRBuilder has no method for {type(node)}")
        return cast(IRNode, method(node))

    def _build_VariableDeclarationNode(
        self, node: VariableDeclarationNode
    ) -> VariableDeclarationIR:
        init = self._build_expression(node.initializer)
        return VariableDeclarationIR(
            name=node.name.name,
            initializer=init,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    def _build_FunctionDeclarationNode(
        self, node: FunctionDeclarationNode
    ) -> FunctionIR:
        params = tuple(p.name for p in node.parameters)
        body = self._build_BlockNode(node.body)
        return FunctionIR(
            name=node.name.name,
            parameters=params,
            body=body,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    def _build_BlockNode(self, node: BlockNode) -> BlockIR:
        stmts = tuple(self._build_statement(s) for s in node.statements)
        return BlockIR(
            statements=stmts, start_span=node.start_span, end_span=node.end_span
        )

    def _build_ExpressionStatementNode(
        self, node: ExpressionStatementNode
    ) -> ExpressionStatementIR:
        expr = self._build_expression(node.expression)
        return ExpressionStatementIR(
            expression=expr,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    def _build_ReturnStatementNode(self, node: ReturnStatementNode) -> ReturnIR:
        val = self._build_expression(node.value)
        return ReturnIR(value=val, start_span=node.start_span, end_span=node.end_span)

    def _build_IfStatementNode(self, node: IfStatementNode) -> IfIR:
        cond = self._build_expression(node.condition)
        then_b = self._build_BlockNode(node.then_block)
        else_b = self._build_BlockNode(node.else_block) if node.else_block else None
        return IfIR(
            condition=cond,
            then_block=then_b,
            else_block=else_b,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    # ---------------------------------------------------------------------
    # Expression helpers
    # ---------------------------------------------------------------------
    def _build_expression(self, node: ASTNode) -> IRExpression:
        method_name = f"_build_expr_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise NotImplementedError(
                f"IRBuilder expression for {type(node)} not implemented"
            )
        return cast(IRExpression, method(node))

    def _build_expr_IdentifierNode(self, node: IdentifierNode) -> VariableReferenceIR:
        return VariableReferenceIR(
            name=node.name, start_span=node.start_span, end_span=node.end_span
        )

    def _build_expr_NumberLiteralNode(self, node: NumberLiteralNode) -> LiteralIR:
        # Preserve numeric type as Python int/float
        value: int | float = float(node.value) if "." in node.value else int(node.value)
        return LiteralIR(
            value=value, start_span=node.start_span, end_span=node.end_span
        )

    def _build_expr_StringLiteralNode(self, node: StringLiteralNode) -> LiteralIR:
        return LiteralIR(
            value=node.value, start_span=node.start_span, end_span=node.end_span
        )

    def _build_expr_UnaryExpressionNode(
        self, node: UnaryExpressionNode
    ) -> UnaryOperationIR:
        operand = self._build_expression(node.operand)
        return UnaryOperationIR(
            operator=node.operator,
            operand=operand,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    def _build_expr_BinaryExpressionNode(
        self, node: BinaryExpressionNode
    ) -> BinaryOperationIR | AssignmentIR:
        left = self._build_expression(node.left)
        right = self._build_expression(node.right)
        if node.operator == "=":
            # Assignment – left must be an identifier
            if isinstance(left, VariableReferenceIR):
                return AssignmentIR(
                    target=left.name,
                    value=right,
                    start_span=node.start_span,
                    end_span=node.end_span,
                )
            # Fallback to binary operation if not a simple variable reference
        return BinaryOperationIR(
            left=left,
            operator=node.operator,
            right=right,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    def _build_ImportDeclarationNode(self, node: ImportDeclarationNode) -> IRNode:
        return ExpressionStatementIR(
            expression=LiteralIR(value=None),
            start_span=node.start_span,
            end_span=node.end_span,
        )

    def _build_expr_MemberAccessNode(self, node: MemberAccessNode) -> MemberAccessIR:
        receiver = self._build_expression(node.receiver)
        return MemberAccessIR(
            receiver=receiver,
            member=node.member.name,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    def _build_expr_CallExpressionNode(self, node: CallExpressionNode) -> CallIR:
        callee = self._build_expression(node.callee)
        # In our language the callee is always an identifier; extract its name
        if isinstance(callee, VariableReferenceIR):
            callee_name = callee.name
        else:
            callee_name = str(callee)
        args = tuple(self._build_expression(arg) for arg in node.arguments)
        return CallIR(
            callee=callee_name,
            arguments=args,
            start_span=node.start_span,
            end_span=node.end_span,
        )
