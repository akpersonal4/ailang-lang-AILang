"""LSP find references — locate all usages of a symbol."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from compiler.ast.nodes import (
    IdentifierNode,
    ParameterNode,
)
from compiler.lsp.protocol import (
    Location,
    Range,
    offset_to_position,
)


def get_references(doc: Any, position: dict[str, Any]) -> list[dict[str, Any]] | None:
    """Find all references to the symbol at the given position."""
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

    # Determine the symbol name
    symbol_name = None
    if isinstance(node, IdentifierNode):
        symbol_name = node.name
    elif isinstance(node, ParameterNode):
        symbol_name = node.name

    if symbol_name is None:
        return None

    # Find all references to this symbol
    locations: list[Location] = []
    for child in _walk_ast(ast):
        if isinstance(child, IdentifierNode) and child.name == symbol_name:
            start_sp = getattr(child, "start_span", None)
            end_sp = getattr(child, "end_span", None)
            if start_sp is not None and end_sp is not None:
                locations.append(
                    Location(
                        uri=doc.uri,
                        range=Range(
                            start=offset_to_position(start_sp, text),
                            end=offset_to_position(end_sp, text),
                        ),
                    )
                )

    return [loc.to_dict() for loc in locations]


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
