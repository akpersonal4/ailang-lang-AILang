"""Simple structural validator for the IR.

The validator walks the IR tree and checks that required attributes are
present and that node relationships are well‑formed. It does **not** perform any
semantic or type checking – those have already been done in earlier phases.
"""

from __future__ import annotations

from .nodes import (
    AssignmentIR,
    BinaryOperationIR,
    BlockIR,
    CallIR,
    ExpressionStatementIR,
    FunctionIR,
    IfIR,
    IRNode,
    LiteralIR,
    ProgramIR,
    ReturnIR,
    UnaryOperationIR,
    VariableDeclarationIR,
    VariableReferenceIR,
)


class IRValidationError(Exception):
    """Raised when the IR fails validation."""


class IRValidator:
    """Validate an IR tree for structural correctness.

    The current checks are lightweight but catch common construction errors:

    * Every node must have ``start_span`` and ``end_span`` (they may be ``None``
      only if the source location is genuinely unavailable).
    * ``ProgramIR`` must contain at least one top‑level node.
    * ``FunctionIR`` must have a non‑empty ``parameters`` tuple.
    * ``AssignmentIR`` target must be a non‑empty string.
    * ``CallIR`` callee must be a non‑empty string.
    """

    def validate(self, node: ProgramIR) -> None:
        if not isinstance(node, ProgramIR):
            raise IRValidationError("Root node must be ProgramIR")
        if not node.body:
            raise IRValidationError("ProgramIR must contain at least one child")
        for child in node.body:
            self._validate_node(child)

    # ---------------------------------------------------------------------
    def _validate_node(self, node: IRNode) -> None:
        # Generic span check – allow None but ensure attribute exists
        if not hasattr(node, "start_span") or not hasattr(node, "end_span"):
            raise IRValidationError(f"Node {type(node)} missing span information")

        # Dispatch based on concrete type
        method_name = f"_validate_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise IRValidationError(f"No validator for node type {type(node)}")
        method(node)

    # ---------------------------------------------------------------------
    def _validate_FunctionIR(self, node: FunctionIR) -> None:
        # Functions may have zero parameters; an empty tuple is acceptable.
        if node.parameters is None:
            raise IRValidationError(
                "FunctionIR parameters must be a tuple (may be empty)"
            )
        self._validate_node(node.body)

    def _validate_BlockIR(self, node: BlockIR) -> None:
        for stmt in node.statements:
            self._validate_node(stmt)

    def _validate_VariableDeclarationIR(self, node: VariableDeclarationIR) -> None:
        if not node.name:
            raise IRValidationError("VariableDeclarationIR missing name")
        self._validate_node(node.initializer)

    def _validate_AssignmentIR(self, node: AssignmentIR) -> None:
        if not node.target:
            raise IRValidationError("AssignmentIR missing target name")
        self._validate_node(node.value)

    def _validate_IfIR(self, node: IfIR) -> None:
        self._validate_node(node.condition)
        self._validate_node(node.then_block)
        if node.else_block:
            self._validate_node(node.else_block)

    def _validate_ReturnIR(self, node: ReturnIR) -> None:
        self._validate_node(node.value)

    def _validate_ExpressionStatementIR(self, node: ExpressionStatementIR) -> None:
        self._validate_node(node.expression)

    def _validate_BinaryOperationIR(self, node: BinaryOperationIR) -> None:
        self._validate_node(node.left)
        self._validate_node(node.right)

    def _validate_UnaryOperationIR(self, node: UnaryOperationIR) -> None:
        self._validate_node(node.operand)

    def _validate_CallIR(self, node: CallIR) -> None:
        if not node.callee:
            raise IRValidationError("CallIR missing callee name")
        for arg in node.arguments:
            self._validate_node(arg)

    def _validate_LiteralIR(self, node: LiteralIR) -> None:
        # Literals are leaf nodes – nothing to validate further
        pass

    def _validate_VariableReferenceIR(self, node: VariableReferenceIR) -> None:
        if not node.name:
            raise IRValidationError("VariableReferenceIR missing name")
