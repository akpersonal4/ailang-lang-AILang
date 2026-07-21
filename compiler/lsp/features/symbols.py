"""LSP document/workspace symbols — outline and project-wide search."""

from __future__ import annotations

from typing import Any

from compiler.ast.nodes import (
    FunctionDeclarationNode,
    ImportDeclarationNode,
    VariableDeclarationNode,
)
from compiler.lsp.protocol import (
    Location,
    Range,
    SymbolInformation,
    offset_to_position,
)


def get_document_symbols(doc: Any) -> list[dict[str, Any]] | None:
    """Get document symbols (outline view) for a document."""
    doc.ensure_compiled()
    ast = doc.ast
    if ast is None:
        return None

    text = doc.text
    symbols: list[SymbolInformation] = []

    for child in ast.children:
        if isinstance(child, FunctionDeclarationNode):
            start_sp = getattr(child.name, "start_span", None)
            end_sp = getattr(child.name, "end_span", None)
            if start_sp is not None and end_sp is not None:
                symbols.append(
                    SymbolInformation(
                        name=child.name.name,
                        kind=12,  # Function
                        location=Location(
                            uri=doc.uri,
                            range=Range(
                                start=offset_to_position(start_sp, text),
                                end=offset_to_position(end_sp, text),
                            ),
                        ),
                    )
                )
        elif isinstance(child, VariableDeclarationNode):
            start_sp = getattr(child.name, "start_span", None)
            end_sp = getattr(child.name, "end_span", None)
            if start_sp is not None and end_sp is not None:
                symbols.append(
                    SymbolInformation(
                        name=f"let {child.name.name}",
                        kind=13,  # Variable
                        location=Location(
                            uri=doc.uri,
                            range=Range(
                                start=offset_to_position(start_sp, text),
                                end=offset_to_position(end_sp, text),
                            ),
                        ),
                    )
                )
        elif isinstance(child, ImportDeclarationNode):
            symbol_name = ".".join(child.module_path)
            span = getattr(child, "start_span", None)
            if span is not None:
                symbols.append(
                    SymbolInformation(
                        name=f"import {symbol_name}",
                        kind=9,  # Module
                        location=Location(
                            uri=doc.uri,
                            range=Range(
                                start=offset_to_position(span, text),
                                end=offset_to_position(
                                    span + len(symbol_name) + 7, text
                                ),
                            ),
                        ),
                    )
                )

    return [s.to_dict() for s in symbols]
