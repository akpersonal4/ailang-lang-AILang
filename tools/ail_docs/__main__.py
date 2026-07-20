# AILang Developer Experience Tool: ail docs
# Retrieves embedded documentation without filesystem access

"""AILang Document Retrieval - provides documentation content via CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

DOCUMENTS = {
    "AGENTS": {
        "filename": "AGENTS.md",
        "description": "AI agent instructions and language rules",
    },
    "LANGUAGE_SPEC": {
        "filename": "LANGUAGE_SPEC.md",
        "description": "Complete AILang language specification",
    },
    "STDLIB_REFERENCE": {
        "filename": "STDLIB_REFERENCE.md",
        "description": "Standard library API reference",
    },
}


def _resolve_docs_path() -> Path | None:
    """Resolve the docs directory relative to the compiler package."""
    try:
        import compiler

        return Path(compiler.__file__).parent / "docs"
    except Exception:
        return None


def list_documents() -> dict:
    """List available documents with metadata."""
    docs_path = _resolve_docs_path()
    available = []
    for key, meta in DOCUMENTS.items():
        entry = {
            "name": key,
            "filename": meta["filename"],
            "description": meta["description"],
        }
        if docs_path:
            entry["available"] = (docs_path / meta["filename"]).exists()
        else:
            entry["available"] = False
        available.append(entry)
    return {"documents": available}


def get_document(name: str) -> dict:
    """Retrieve document content by name.

    Args:
        name: Document name (AGENTS, LANGUAGE_SPEC, STDLIB_REFERENCE)
              or filename (AGENTS.md, LANGUAGE_SPEC.md, STDLIB_REFERENCE.md)
    """
    key = name.upper().replace(".MD", "")
    if key not in DOCUMENTS:
        return {
            "error": f"Unknown document: {name}",
            "available": list(DOCUMENTS.keys()),
        }

    docs_path = _resolve_docs_path()
    if not docs_path:
        return {"error": "Cannot locate documentation directory"}

    filename = DOCUMENTS[key]["filename"]
    filepath = docs_path / filename
    if not filepath.exists():
        return {"error": f"Document file not found: {filename}"}

    content = filepath.read_text(encoding="utf-8")
    return {
        "name": key,
        "filename": filename,
        "description": DOCUMENTS[key]["description"],
        "content": content,
        "size_bytes": len(content.encode("utf-8")),
    }


def main() -> int:
    """Main entry point for ail docs."""
    # Ensure UTF-8 output on Windows
    if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if sys.stderr.encoding and sys.stderr.encoding.lower() != "utf-8":
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = argparse.ArgumentParser(
        prog="ail docs",
        description="Retrieve AILang documentation without filesystem access",
    )
    parser.add_argument(
        "document",
        nargs="?",
        default=None,
        help="Document name (AGENTS, LANGUAGE_SPEC, STDLIB_REFERENCE)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output machine-readable JSON",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available documents",
    )

    args = parser.parse_args()

    if args.list or not args.document:
        result = list_documents()
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print("Available AILang documents:\n")
            for doc in result["documents"]:
                status = "available" if doc["available"] else "missing"
                print(f"  {doc['name']:<20} {doc['description']} [{status}]")
            print("\nUsage: ail docs <DOCUMENT_NAME>")
        return 0

    result = get_document(args.document)
    if "error" in result:
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            print(f"Error: {result['error']}", file=sys.stderr)
            if "available" in result:
                print(f"Available: {', '.join(result['available'])}", file=sys.stderr)
        return 1

    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(result["content"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
