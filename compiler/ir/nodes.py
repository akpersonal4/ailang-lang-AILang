"""Immutable IR node definitions for AILang.

The IR mirrors the executable semantics of the language while discarding any
syntax‑only artifacts (punctuation, token ordering, etc.). Each node is a frozen
dataclass and carries the original source ``start_span``/``end_span`` for later
diagnostics.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TypeAlias, Union


@dataclass(frozen=True)
class ProgramIR:
    body: tuple[IRNode, ...]
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class FunctionIR:
    name: str
    parameters: tuple[str, ...]
    body: BlockIR
    default_parameters: tuple[tuple[str, IRExpression], ...] = ()
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class BlockIR:
    statements: tuple[IRNode, ...]
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class VariableDeclarationIR:
    name: str
    initializer: IRExpression
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class AssignmentIR:
    target: str
    value: IRExpression
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class IfIR:
    condition: IRExpression
    then_block: BlockIR
    else_block: BlockIR | None = None
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class ReturnIR:
    value: IRExpression
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class ExpressionStatementIR:
    expression: IRExpression
    start_span: int | None = None
    end_span: int | None = None


# ---- Expressions ----------------------------------------------------------


IRExpression: TypeAlias = Union[
    "BinaryOperationIR",
    "UnaryOperationIR",
    "CallIR",
    "LiteralIR",
    "VariableReferenceIR",
    "MemberAccessIR",
]


@dataclass(frozen=True)
class BinaryOperationIR:
    left: IRExpression
    operator: str
    right: IRExpression
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class UnaryOperationIR:
    operator: str
    operand: IRExpression
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class CallIR:
    callee: str
    arguments: tuple[IRExpression, ...]
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class LiteralIR:
    value: object
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class MemberAccessIR:
    receiver: IRExpression
    member: str
    start_span: int | None = None
    end_span: int | None = None


@dataclass(frozen=True)
class VariableReferenceIR:
    name: str
    start_span: int | None = None
    end_span: int | None = None


# Helper type for type checking
IRNode: TypeAlias = (
    ProgramIR
    | FunctionIR
    | BlockIR
    | VariableDeclarationIR
    | AssignmentIR
    | IfIR
    | ReturnIR
    | ExpressionStatementIR
    | BinaryOperationIR
    | UnaryOperationIR
    | CallIR
    | LiteralIR
    | MemberAccessIR
    | VariableReferenceIR
)
