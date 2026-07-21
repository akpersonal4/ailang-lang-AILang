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

    Experimental: for-in loops are lowered into recursive helper functions at
    the module level during IR construction. The for statement is replaced with
    a call to the generated helper.
    """

    def __init__(self) -> None:
        self._generated_functions: list[FunctionIR] = []
        self._for_counter = 0

    def build(self, node: ProgramNode) -> ProgramIR:
        body: list[IRNode] = []
        for child in node.children:
            body.append(self._build_statement(child))
        all_body = tuple(self._generated_functions + body)
        return ProgramIR(
            body=all_body, start_span=node.start_span, end_span=node.end_span
        )

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
        defaults: list[tuple[str, IRExpression]] = []
        for p in node.parameters:
            if p.default_value is not None:
                defaults.append((p.name, self._build_expression(p.default_value)))
        body = self._build_BlockNode(node.body)
        return FunctionIR(
            name=node.name.name,
            parameters=params,
            default_parameters=tuple(defaults),
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

    def _build_ForStatementNode(self, node: ForStatementNode) -> CallIR | AssignmentIR:
        """Lower a for-in loop into a recursive helper function + initial call.

        For ``for item in collection { body }`` generates:

        .. code-block:: text

            fn __for_fn_N(collection, index, ...captured) {
                if (index < list.len(collection)) {
                    let item = list.get(collection, index);
                    <body>
                    __for_fn_N(collection, index + 1, ...captured)
                } else {
                    <captured_var>   or nil if no writes
                }
            }

            <captured_var => __for_fn_N(collection, 0, ...captured)

        Variables from enclosing scopes that are referenced in the body are
        automatically threaded as parameters. If exactly one variable is
        assigned inside the body, the base case returns its final value and
        the call site captures it.
        """
        fn_name = f"__for_fn_{self._for_counter}"
        var_name = node.variable.name
        self._for_counter += 1

        list_param = f"__lst_{fn_name}"
        idx_param = f"__idx_{fn_name}"

        # --- Free variable detection ---
        local_names: set[str] = {var_name}
        self._collect_locals(node.body, local_names)
        reads: set[str] = set()
        writes: set[str] = set()
        self._collect_free_refs(node.body, local_names, reads, writes)
        reads_only = reads - writes
        captured_params = tuple(sorted(reads_only | writes))

        if len(writes) > 1:
            raise ValueError(
                f"For-loop body writes to {len(writes)} enclosing variables "
                f"({', '.join(sorted(writes))}). "
                "Only one accumulator variable is supported. "
                "Use a list or manual recursion for multiple accumulators."
            )

        all_params = (list_param, idx_param) + captured_params
        iterable_ir = self._build_expression(node.iterable)

        # let item = list.get(collection, index)
        get_call = CallIR(
            callee="list.get",
            arguments=(
                VariableReferenceIR(name=list_param),
                VariableReferenceIR(name=idx_param),
            ),
        )
        var_decl = VariableDeclarationIR(name=var_name, initializer=get_call)

        # Body statements: variable decl + user body
        body_stmts: list[IRNode] = [var_decl]
        for stmt in node.body.statements:
            body_stmts.append(self._build_statement(stmt))

        # Recursive call: __for_fn_N(collection, index + 1, captured...)
        next_idx = BinaryOperationIR(
            left=VariableReferenceIR(name=idx_param),
            operator="+",
            right=LiteralIR(value=1),
        )
        recursive_args: list[IRExpression] = [
            VariableReferenceIR(name=list_param),
            next_idx,
        ]
        for cap_name in captured_params:
            recursive_args.append(VariableReferenceIR(name=cap_name))
        recursive_call = CallIR(
            callee=fn_name,
            arguments=tuple(recursive_args),
        )
        body_stmts.append(recursive_call)

        # Condition: index < list.len(collection)
        len_call = CallIR(
            callee="list.len",
            arguments=(VariableReferenceIR(name=list_param),),
        )
        condition = BinaryOperationIR(
            left=VariableReferenceIR(name=idx_param),
            operator="<",
            right=len_call,
        )

        then_block = BlockIR(statements=tuple(body_stmts))

        # Else branch: return written variable value (or nil if no writes)
        if writes:
            written_name = next(iter(writes))
            else_stmts: tuple[IRNode, ...] = (
                ExpressionStatementIR(
                    expression=VariableReferenceIR(name=written_name)
                ),
            )
        else:
            else_stmts = (ExpressionStatementIR(expression=LiteralIR(value=None)),)
        else_block = BlockIR(statements=else_stmts)

        if_ir = IfIR(
            condition=condition,
            then_block=then_block,
            else_block=else_block,
        )

        func_body = BlockIR(statements=(if_ir,))
        func = FunctionIR(
            name=fn_name,
            parameters=all_params,
            body=func_body,
        )
        self._generated_functions.append(func)

        # Initial call args: iterable, 0, captured variable names
        call_args: list[IRExpression] = [iterable_ir, LiteralIR(value=0)]
        for cap_name in captured_params:
            call_args.append(VariableReferenceIR(name=cap_name))

        call_ir = CallIR(callee=fn_name, arguments=tuple(call_args))

        # If there is a written variable, wrap in AssignmentIR
        if writes:
            written_name = next(iter(writes))
            return AssignmentIR(target=written_name, value=call_ir)
        return call_ir

    # ------------------------------------------------------------------
    # Free variable detection helpers (for experimental loop capture)
    # ------------------------------------------------------------------
    @staticmethod
    def _collect_locals(node: ASTNode, locals_set: set[str]) -> None:
        """Recursively collect ``VariableDeclarationNode`` names within body."""
        if isinstance(node, VariableDeclarationNode):
            locals_set.add(node.name.name)
        elif isinstance(node, BlockNode):
            for stmt in node.statements:
                IRBuilder._collect_locals(stmt, locals_set)
        elif isinstance(node, IfStatementNode):
            IRBuilder._collect_locals(node.then_block, locals_set)
            if node.else_block:
                IRBuilder._collect_locals(node.else_block, locals_set)
        elif isinstance(node, ForStatementNode):
            locals_set.add(node.variable.name)
            IRBuilder._collect_locals(node.body, locals_set)

    @staticmethod
    def _collect_free_refs(
        node: ASTNode, local_names: set[str], reads: set[str], writes: set[str]
    ) -> None:
        """Walk the AST and collect references to non-local variables.

        * ``reads`` — identifiers referenced (read) that are not in *local_names*.
        * ``writes`` — identifiers that appear on the LHS of ``=`` and are not
          in *local_names*.
        """
        if isinstance(node, IdentifierNode):
            if node.name not in local_names:
                reads.add(node.name)
        elif isinstance(node, BinaryExpressionNode):
            if node.operator == "=":
                if isinstance(node.left, IdentifierNode):
                    if node.left.name not in local_names:
                        writes.add(node.left.name)
                    IRBuilder._collect_free_refs(node.right, local_names, reads, writes)
                else:
                    IRBuilder._collect_free_refs(node.left, local_names, reads, writes)
                    IRBuilder._collect_free_refs(node.right, local_names, reads, writes)
            else:
                IRBuilder._collect_free_refs(node.left, local_names, reads, writes)
                IRBuilder._collect_free_refs(node.right, local_names, reads, writes)
        elif isinstance(node, BlockNode):
            for stmt in node.statements:
                IRBuilder._collect_free_refs(stmt, local_names, reads, writes)
        elif isinstance(node, ExpressionStatementNode):
            IRBuilder._collect_free_refs(node.expression, local_names, reads, writes)
        elif isinstance(node, ReturnStatementNode):
            IRBuilder._collect_free_refs(node.value, local_names, reads, writes)
        elif isinstance(node, IfStatementNode):
            IRBuilder._collect_free_refs(node.condition, local_names, reads, writes)
            IRBuilder._collect_free_refs(node.then_block, local_names, reads, writes)
            if node.else_block:
                IRBuilder._collect_free_refs(
                    node.else_block, local_names, reads, writes
                )
        elif isinstance(node, ForStatementNode):
            IRBuilder._collect_free_refs(node.iterable, local_names, reads, writes)
            IRBuilder._collect_free_refs(node.body, local_names, reads, writes)
        elif isinstance(node, CallExpressionNode):
            IRBuilder._collect_free_refs(node.callee, local_names, reads, writes)
            for arg in node.arguments:
                IRBuilder._collect_free_refs(arg, local_names, reads, writes)
        elif isinstance(node, MemberAccessNode):
            IRBuilder._collect_free_refs(node.receiver, local_names, reads, writes)
        elif isinstance(node, UnaryExpressionNode):
            IRBuilder._collect_free_refs(node.operand, local_names, reads, writes)
        elif isinstance(node, VariableDeclarationNode):
            IRBuilder._collect_free_refs(node.initializer, local_names, reads, writes)

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

    def _build_expr_BooleanLiteralNode(self, node: BooleanLiteralNode) -> LiteralIR:
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
        callee_ir = self._build_expression(node.callee)
        # Callee is a simple identifier – use the variable name directly.
        if isinstance(callee_ir, VariableReferenceIR):
            callee_name: str = callee_ir.name
        elif isinstance(callee_ir, MemberAccessIR):
            # Flatten nested MemberAccess into a dotted qualified name so that
            # ``math.add(...)`` becomes callee ``"math.add"`` rather than the
            # string representation of the MemberAccessIR object.
            callee_name = self._flatten_member_access(callee_ir)
        else:
            callee_name = str(callee_ir)
        args = tuple(self._build_expression(arg) for arg in node.arguments)
        return CallIR(
            callee=callee_name,
            arguments=args,
            start_span=node.start_span,
            end_span=node.end_span,
        )

    def _flatten_member_access(self, node: MemberAccessIR) -> str:
        """Recursively flatten a MemberAccessIR tree into a dotted name string.

        Examples::

            MemberAccess(VariableRef("math"), "add")   -> "math.add"
            MemberAccess(MemberAccess(VariableRef("a"), "b"), "c")  -> "a.b.c"
        """
        if isinstance(node.receiver, VariableReferenceIR):
            return f"{node.receiver.name}.{node.member}"
        if isinstance(node.receiver, MemberAccessIR):
            return f"{self._flatten_member_access(node.receiver)}.{node.member}"
        return f"{node.receiver}.{node.member}"
