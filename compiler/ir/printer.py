"""Deterministic pretty‑printer for the IR.

The printer produces a human‑readable, indented representation of an IR tree.
It is used by golden‑file tests to ensure the lowering is stable.
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


class IRPrinter:
    """Pretty‑print an IR tree.

    The output format mirrors the example in the CTO directive and is stable
    across runs, making it suitable for golden‑file comparisons.
    """

    def __init__(self) -> None:
        self._lines: list[str] = []
        self._indent = 0

    def _write(self, text: str) -> None:
        self._lines.append("  " * self._indent + text)

    def _inc(self) -> None:
        self._indent += 1

    def _dec(self) -> None:
        self._indent = max(self._indent - 1, 0)

    # ---------------------------------------------------------------------
    def print(self, node: ProgramIR) -> str:
        self._visit(node)
        return "\n".join(self._lines)

    # ---------------------------------------------------------------------
    def _visit(self, node: IRNode) -> None:
        method_name = f"_visit_{type(node).__name__}"
        method = getattr(self, method_name, None)
        if method is None:
            raise NotImplementedError(f"IRPrinter missing visitor for {type(node)}")
        method(node)

    # ---------------------------------------------------------------------
    def _visit_ProgramIR(self, node: ProgramIR) -> None:
        self._write("Program")
        self._inc()
        for child in node.body:
            self._visit(child)
        self._dec()

    def _visit_FunctionIR(self, node: FunctionIR) -> None:
        self._write(f"Function {node.name}")
        self._inc()
        self._visit(node.body)
        self._dec()

    def _visit_BlockIR(self, node: BlockIR) -> None:
        self._write("Block")
        self._inc()
        for stmt in node.statements:
            self._visit(stmt)
        self._dec()

    def _visit_VariableDeclarationIR(self, node: VariableDeclarationIR) -> None:
        self._write(f"VariableDeclaration {node.name}")
        self._inc()
        self._visit(node.initializer)
        self._dec()

    def _visit_AssignmentIR(self, node: AssignmentIR) -> None:
        self._write(f"Assignment {node.target}")
        self._inc()
        self._visit(node.value)
        self._dec()

    def _visit_IfIR(self, node: IfIR) -> None:
        self._write("If")
        self._inc()
        self._write("Condition")
        self._inc()
        self._visit(node.condition)
        self._dec()
        self._write("Then")
        self._inc()
        self._visit(node.then_block)
        self._dec()
        if node.else_block:
            self._write("Else")
            self._inc()
            self._visit(node.else_block)
            self._dec()
        self._dec()

    def _visit_ReturnIR(self, node: ReturnIR) -> None:
        self._write("Return")
        self._inc()
        self._visit(node.value)
        self._dec()

    def _visit_ExpressionStatementIR(self, node: ExpressionStatementIR) -> None:
        self._write("ExpressionStatement")
        self._inc()
        self._visit(node.expression)
        self._dec()

    def _visit_BinaryOperationIR(self, node: BinaryOperationIR) -> None:
        self._write(f"BinaryOperation {node.operator}")
        self._inc()
        self._visit(node.left)
        self._visit(node.right)
        self._dec()

    def _visit_UnaryOperationIR(self, node: UnaryOperationIR) -> None:
        self._write(f"UnaryOperation {node.operator}")
        self._inc()
        self._visit(node.operand)
        self._dec()

    def _visit_CallIR(self, node: CallIR) -> None:
        self._write(f"Call {node.callee}")
        self._inc()
        for arg in node.arguments:
            self._visit(arg)
        self._dec()

    def _visit_LiteralIR(self, node: LiteralIR) -> None:
        self._write(f"Literal {node.value!r}")

    def _visit_VariableReferenceIR(self, node: VariableReferenceIR) -> None:
        self._write(f"VariableReference {node.name}")
