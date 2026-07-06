"""LSP go-to-definition — navigate to symbol definitions."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from compiler.ast.nodes import (
    FunctionDeclarationNode,
    IdentifierNode,
    ParameterNode,
    VariableDeclarationNode,
)
from compiler.lsp.protocol import (
    Location,
    Range,
    offset_to_position,
)


def get_definition(doc: Any, position: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Get the definition location for the symbol at position."""
    doc.ensure_compiled()
    ast = doc.ast
    if ast is None:
        return None

    text = doc.text
    line = position["line"]
    char = position["character"]
    offset = _position_to_offset(line, char, text)

    node = _find_node_at_offset(ast, offset)
    if node is None:
        return None

    target: IdentifierNode | ParameterNode | None = None

    if isinstance(node, IdentifierNode):
        name = node.name
        # Search AST for variable/function declarations with this name
        for child in _walk_ast(ast):
            if isinstance(child, VariableDeclarationNode) and child.name.name == name:
                target = child.name
                break
            if isinstance(child, FunctionDeclarationNode) and child.name.name == name:
                target = child.name
                break
            if isinstance(child, ParameterNode) and child.name == name:
                target = child
                break

    if target is not None:
        start_sp = getattr(target, "start_span", None)
        end_sp = getattr(target, "end_span", None)
        if start_sp is not None and end_sp is not None:
            loc = Location(
                uri=doc.uri,
                range=Range(
                    start=offset_to_position(start_sp, text),
                    end=offset_to_position(end_sp, text),
                ),
            )
            return [loc.to_dict()]

    return None


def _position_to_offset(line: int, character: int, text: str) -> int:
    current_line = 0
    for i, ch in enumerate(text):
        if current_line == line:
            return i + character
        if ch == "\n":
            current_line += 1
    return len(text)


def _find_node_at_offset(node: Any, offset: int) -> Any | None:
    best = None
    for child in _walk_ast(node):
        if child is None:
            continue
        start = getattr(child, "start_span", None)
        end = getattr(child, "end_span", None)
        if start is not None and end is not None and start <= offset < end:
            best = child
    return best


def _walk_ast(node: Any) -> Generator[Any, None, None]:
    if node is None:
        return
    yield node
    if isinstance(node, (list, tuple)):
        for item in node:
            yield from _walk_ast(item)
    elif hasattr(node, "__dataclass_fields__"):
        for field_name in node.__dataclass_fields__:
            val = getattr(node, field_name)
            if isinstance(val, (list, tuple)):
                for item in val:
                    yield from _walk_ast(item)
            elif hasattr(val, "__dataclass_fields__"):
                yield from _walk_ast(val)
