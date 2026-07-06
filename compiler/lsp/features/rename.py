"""LSP rename — safely rename symbols across the document."""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from typing import Any

from compiler.ast.nodes import (
    IdentifierNode,
    ParameterNode,
)
from compiler.lsp.protocol import (
    Range,
    offset_to_position,
)


def get_rename_edits(
    doc: Any, position: dict[str, Any], new_name: str
) -> dict[str, Any] | None:
    """Get workspace edits for renaming the symbol at position."""
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

    symbol_name: str | None = None
    if isinstance(node, IdentifierNode):
        symbol_name = node.name
    elif isinstance(node, ParameterNode):
        symbol_name = node.name

    if symbol_name is None:
        return None

    edits: list[TextEdit] = []
    for child in _walk_ast(ast):
        target: IdentifierNode | ParameterNode | None = None
        if isinstance(child, IdentifierNode) and child.name == symbol_name:
            target = child
        elif isinstance(child, ParameterNode) and child.name == symbol_name:
            target = child

        if target is not None:
            start_sp = getattr(target, "start_span", None)
            end_sp = getattr(target, "end_span", None)
            if start_sp is not None and end_sp is not None:
                edits.append(
                    TextEdit(
                        range=Range(
                            start=offset_to_position(start_sp, text),
                            end=offset_to_position(end_sp, text),
                        ),
                        new_text=new_name,
                    )
                )

    if not edits:
        return None

    return WorkspaceEdit(changes={doc.uri: [e.to_dict() for e in edits]}).to_dict()


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


@dataclass
class TextEdit:
    range: Range
    new_text: str

    def to_dict(self) -> dict[str, Any]:
        return {"range": self.range.to_dict(), "newText": self.new_text}


@dataclass
class WorkspaceEdit:
    changes: dict[str, list[dict[str, Any]]]

    def to_dict(self) -> dict[str, Any]:
        return {"changes": self.changes}
