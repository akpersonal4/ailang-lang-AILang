# AILang MCP Server
# JSON-RPC 2.0 over stdio transport

"""AILang MCP Server - JSON-RPC 2.0 over stdio for AI tool integration."""

from __future__ import annotations

import json
import sys
from typing import Any

from .context_adapter import get_language_context
from .compiler_adapter import compile_source
from .stdlib_adapter import get_stdlib
from .diagnostics_adapter import explain_diagnostic
from .examples_adapter import get_examples
from .docs_adapter import get_document, list_documents

VERSION = "1.0.8"

TOOLS = [
    {
        "name": "get_language_context",
        "description": "Get AILang language context including rules, workflow, and diagnostics",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    {
        "name": "get_stdlib",
        "description": "Get AILang standard library modules, functions, and signatures",
        "inputSchema": {
            "type": "object",
            "properties": {
                "module": {
                    "type": "string",
                    "description": "Optional module name to get details for",
                },
            },
            "required": [],
        },
    },
    {
        "name": "compile_source",
        "description": "Compile AILang source code and return diagnostics",
        "inputSchema": {
            "type": "object",
            "properties": {
                "source": {
                    "type": "string",
                    "description": "AILang source code to compile",
                },
            },
            "required": ["source"],
        },
    },
    {
        "name": "explain_diagnostic",
        "description": "Get detailed explanation for a diagnostic code",
        "inputSchema": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "Diagnostic code (e.g., SEM002, TYP005)",
                },
            },
            "required": ["code"],
        },
    },
    {
        "name": "get_examples",
        "description": "Get canonical AILang code examples",
        "inputSchema": {
            "type": "object",
            "properties": {
                "category": {
                    "type": "string",
                    "description": "Optional category (hello, inventory, csv, json)",
                },
            },
            "required": [],
        },
    },
    {
        "name": "get_document",
        "description": "Retrieve AILang documentation content (AGENTS.md, LANGUAGE_SPEC.md, STDLIB_REFERENCE.md)",
        "inputSchema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Document filename (AGENTS.md, LANGUAGE_SPEC.md, STDLIB_REFERENCE.md)",
                },
            },
            "required": [],
        },
    },
]


def handle_request(request: dict[str, Any]) -> dict[str, Any]:
    """Handle a JSON-RPC 2.0 request."""
    method = request.get("method")
    params = request.get("params", {})
    request_id = request.get("id")

    try:
        if method == "initialize":
            result = {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                },
                "serverInfo": {
                    "name": "ailang-mcp",
                    "version": VERSION,
                },
            }
        elif method == "tools/list":
            result = {"tools": TOOLS}
        elif method == "tools/call":
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            result = call_tool(tool_name, arguments)
        elif method == "ping":
            result = {}
        else:
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}",
                },
            }

        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
        }

    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": -32603,
                "message": str(e),
            },
        }


def call_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Call an MCP tool and return the result."""
    if name == "get_language_context":
        result = get_language_context()
    elif name == "get_stdlib":
        module = arguments.get("module")
        result = get_stdlib(module)
    elif name == "compile_source":
        source = arguments.get("source", "")
        result = compile_source(source)
    elif name == "explain_diagnostic":
        code = arguments.get("code", "")
        result = explain_diagnostic(code)
    elif name == "get_examples":
        category = arguments.get("category")
        result = get_examples(category)
    elif name == "get_document":
        doc_name = arguments.get("name", "")
        if doc_name:
            result = get_document(doc_name)
        else:
            result = list_documents()
    else:
        raise ValueError(f"Unknown tool: {name}")

    return {
        "content": [
            {
                "type": "text",
                "text": json.dumps(result, indent=2),
            }
        ]
    }


def run_server() -> None:
    """Run the MCP server on stdio."""
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue

        try:
            request = json.loads(line)
        except json.JSONDecodeError:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {
                    "code": -32700,
                    "message": "Parse error",
                },
            }
            print(json.dumps(response), flush=True)
            continue

        response = handle_request(request)
        print(json.dumps(response), flush=True)


def main() -> int:
    """Main entry point for the MCP server."""
    print(f"AILang MCP Server v{VERSION}", file=sys.stderr)
    print("Transport: stdio", file=sys.stderr)
    print("Ready.", file=sys.stderr)
    run_server()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
