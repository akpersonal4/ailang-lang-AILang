"""LSP rename — safely rename symbols across the document."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from compiler.lsp.protocol import (
    Range,
    offset_to_position,
)
from compiler.lsp.utils import (
    find_node_at_offset,
    find_references,
    position_to_offset,
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
    offset = position_to_offset(line, char, text)

    node = find_node_at_offset(ast, offset)
    if node is None:
        return None

    name = getattr(node, "name", None)
    if name is None:
        return None

    edits: list[TextEdit] = []
    for ref_node in find_references(ast, name):
        start_sp = getattr(ref_node, "start_span", None)
        end_sp = getattr(ref_node, "end_span", None)
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
