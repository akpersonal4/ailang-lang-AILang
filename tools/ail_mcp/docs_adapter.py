# AILang MCP Server - Document Adapter
# Provides document content retrieval without filesystem access

"""Document adapter for MCP server - retrieves AILang documentation content."""

from __future__ import annotations

from pathlib import Path
from typing import Any

DOCUMENTS = {
    "AGENTS.md": {
        "description": "AI agent instructions and language rules",
    },
    "LANGUAGE_SPEC.md": {
        "description": "Complete AILang language specification",
    },
    "STDLIB_REFERENCE.md": {
        "description": "Standard library API reference",
    },
}


def get_document(name: str) -> dict[str, Any]:
    """Retrieve document content by name.

    Args:
        name: Document filename (AGENTS.md, LANGUAGE_SPEC.md, STDLIB_REFERENCE.md)

    Returns:
        Dictionary with document content or error.
    """
    if name not in DOCUMENTS:
        return {
            "error": f"Unknown document: {name}",
            "available_documents": list(DOCUMENTS.keys()),
        }

    try:
        import compiler

        docs_path = Path(compiler.__file__).parent / "docs"
        filepath = docs_path / name
    except Exception:
        return {"error": "Cannot locate documentation directory"}

    if not filepath.exists():
        return {"error": f"Document file not found: {name}"}

    content = filepath.read_text(encoding="utf-8")
    return {
        "name": name,
        "description": DOCUMENTS[name]["description"],
        "content": content,
        "size_bytes": len(content.encode("utf-8")),
    }


def list_documents() -> dict[str, Any]:
    """List available documents with metadata."""
    try:
        import compiler

        docs_path = Path(compiler.__file__).parent / "docs"
    except Exception:
        docs_path = None

    available = []
    for name, meta in DOCUMENTS.items():
        entry: dict[str, Any] = {
            "name": name,
            "description": meta["description"],
        }
        if docs_path:
            entry["available"] = (docs_path / name).exists()
        else:
            entry["available"] = False
        available.append(entry)

    return {"documents": available}
