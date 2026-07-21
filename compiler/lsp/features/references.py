"""LSP find references — locate all usages of a symbol."""

from __future__ import annotations

from typing import Any

from compiler.lsp.protocol import (
    Location,
    Range,
    offset_to_position,
)
from compiler.lsp.utils import (
    find_node_at_offset,
    find_references,
    position_to_offset,
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
    offset = position_to_offset(line, char, text)

    node = find_node_at_offset(ast, offset)
    if node is None:
        return None

    name = getattr(node, "name", None)
    if name is None:
        return None

    locations: list[Location] = []
    for ref_node in find_references(ast, name):
        start_sp = getattr(ref_node, "start_span", None)
        end_sp = getattr(ref_node, "end_span", None)
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
