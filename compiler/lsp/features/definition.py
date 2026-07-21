"""LSP go-to-definition — navigate to symbol definitions."""

from __future__ import annotations

from typing import Any

from compiler.lsp.protocol import (
    Location,
    Range,
    offset_to_position,
)
from compiler.lsp.utils import (
    find_definition_target,
    find_node_at_offset,
    position_to_offset,
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
    offset = position_to_offset(line, char, text)

    node = find_node_at_offset(ast, offset)
    if node is None:
        return None

    name = getattr(node, "name", None)
    if name is None:
        return None

    target = find_definition_target(ast, name)
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
