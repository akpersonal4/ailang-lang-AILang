"""LSP workspace symbol search — find symbols across all open documents."""

from __future__ import annotations

from typing import Any

from compiler.lsp.protocol import (
    Location,
    Range,
    SymbolInformation,
    offset_to_position,
)


def get_workspace_symbols(
    documents: dict[str, Any], query: str
) -> list[dict[str, Any]]:
    """Search for symbols matching query across all open documents."""
    results: list[SymbolInformation] = []
    query_lower = query.lower()

    for uri, doc in documents.items():
        doc.ensure_compiled()
        ast = doc.ast
        if ast is None:
            continue

        text = doc.text
        for child in getattr(ast, "children", []):
            kind_name = type(child).__name__

            if kind_name == "FunctionDeclarationNode":
                name = child.name.name
                if query_lower not in name.lower():
                    continue
                start_sp = getattr(child.name, "start_span", None)
                end_sp = getattr(child.name, "end_span", None)
                if start_sp is not None and end_sp is not None:
                    results.append(
                        SymbolInformation(
                            name=name,
                            kind=12,
                            location=Location(
                                uri=uri,
                                range=Range(
                                    start=offset_to_position(start_sp, text),
                                    end=offset_to_position(end_sp, text),
                                ),
                            ),
                        )
                    )

            elif kind_name == "VariableDeclarationNode":
                name = child.name.name
                if query_lower not in name.lower():
                    continue
                start_sp = getattr(child.name, "start_span", None)
                end_sp = getattr(child.name, "end_span", None)
                if start_sp is not None and end_sp is not None:
                    results.append(
                        SymbolInformation(
                            name=name,
                            kind=13,
                            location=Location(
                                uri=uri,
                                range=Range(
                                    start=offset_to_position(start_sp, text),
                                    end=offset_to_position(end_sp, text),
                                ),
                            ),
                        )
                    )

            elif kind_name == "ImportDeclarationNode":
                name = ".".join(child.module_path)
                if query_lower not in name.lower():
                    continue
                span = getattr(child, "start_span", None)
                if span is not None:
                    results.append(
                        SymbolInformation(
                            name=f"import {name}",
                            kind=9,
                            location=Location(
                                uri=uri,
                                range=Range(
                                    start=offset_to_position(span, text),
                                    end=offset_to_position(
                                        span + len(name) + 7, text
                                    ),
                                ),
                            ),
                        )
                    )

    return [s.to_dict() for s in results]
