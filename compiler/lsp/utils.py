"""Shared utility functions for LSP feature modules.

Consolidates AST traversal, offset conversion, and node range
helpers that were previously duplicated across 5+ feature files.
"""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from compiler.ast.nodes import (
    CallExpressionNode,
    FunctionDeclarationNode,
    IdentifierNode,
    MemberAccessNode,
    ParameterNode,
    VariableDeclarationNode,
)
from compiler.lsp.protocol import Range as LspRange
from compiler.lsp.protocol import offset_to_position


def walk_ast(node: Any) -> Generator[Any, None, None]:
    """Yield all nodes in the AST tree in depth-first order."""
    if node is None:
        return
    yield node
    if isinstance(node, (list, tuple)):
        for item in node:
            yield from walk_ast(item)
    elif hasattr(node, "__dataclass_fields__"):
        for field_name in node.__dataclass_fields__:
            val = getattr(node, field_name)
            if isinstance(val, (list, tuple)):
                for item in val:
                    yield from walk_ast(item)
            elif hasattr(val, "__dataclass_fields__"):
                yield from walk_ast(val)


def find_node_at_offset(node: Any, offset: int) -> Any | None:
    """Find the deepest AST node containing the given source offset."""
    best = None
    for child in walk_ast(node):
        if child is None:
            continue
        start = getattr(child, "start_span", None)
        end = getattr(child, "end_span", None)
        if start is not None and end is not None and start <= offset < end:
            best = child
    return best


def position_to_offset(line: int, character: int, text: str) -> int:
    """Convert LSP 0-based (line, character) to source byte offset."""
    current_line = 0
    for i, ch in enumerate(text):
        if current_line == line:
            return i + character
        if ch == "\n":
            current_line += 1
    return len(text)


def node_range(node: Any, text: str) -> LspRange | None:
    """Create an LSP Range from a node's start_span / end_span."""
    start = getattr(node, "start_span", None)
    end = getattr(node, "end_span", None)
    if start is None or end is None:
        return None
    return LspRange(
        start=offset_to_position(start, text),
        end=offset_to_position(end, text),
    )


def find_definition_target(
    ast: Any, name: str
) -> IdentifierNode | ParameterNode | None:
    """Search the AST for the declaration site of a named symbol."""
    for child in walk_ast(ast):
        if isinstance(child, VariableDeclarationNode) and child.name.name == name:
            return child.name
        if isinstance(child, FunctionDeclarationNode) and child.name.name == name:
            return child.name
        if isinstance(child, ParameterNode) and child.name == name:
            return child
    return None


def find_references(ast: Any, name: str) -> list[Any]:
    """Find all IdentifierNode and ParameterNode with the given name."""
    refs: list[Any] = []
    for child in walk_ast(ast):
        if isinstance(child, IdentifierNode) and child.name == name:
            refs.append(child)
        elif isinstance(child, ParameterNode) and child.name == name:
            refs.append(child)
    return refs


def find_enclosing_call(ast: Any, offset: int) -> Any | None:
    """Find the innermost CallExpressionNode containing the offset."""
    best = None
    for child in walk_ast(ast):
        if isinstance(child, CallExpressionNode):
            start = getattr(child, "start_span", None)
            end = getattr(child, "end_span", None)
            if start is not None and end is not None and start <= offset < end:
                if best is None or (
                    getattr(child, "start_span", 0) >= getattr(best, "start_span", 0)
                ):
                    best = child
    return best


def callee_name(node: Any) -> str | None:
    """Extract the qualified name from a call callee (e.g. 'string.concat')."""
    if isinstance(node, IdentifierNode):
        return node.name
    if hasattr(node, "member") and hasattr(node, "receiver"):
        rcv = callee_name(node.receiver)
        if rcv:
            return f"{rcv}.{node.member.name}"
    return None


def member_access_name(node: MemberAccessNode) -> str:
    """Get the fully qualified name of a member access expression."""
    parts: list[str] = []
    current: Any = node
    while isinstance(current, MemberAccessNode):
        parts.append(current.member.name)
        current = current.receiver
    if isinstance(current, IdentifierNode):
        parts.append(current.name)
    return ".".join(reversed(parts))
