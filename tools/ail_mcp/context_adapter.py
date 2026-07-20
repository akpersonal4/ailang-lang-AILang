# AILang MCP Server - Context Adapter
# Provides language context similar to ail context --json

"""Context adapter for MCP server - provides AILang language context."""

from __future__ import annotations

from typing import Any

VERSION = "1.0.8"

LANGUAGE_RULES = {
    "no_loops": {
        "enabled": True,
        "description": "Use recursion only (while/for don't exist in AILang)",
    },
    "no_forward_references": {
        "enabled": True,
        "description": "Callee must be defined before caller",
    },
    "no_nested_functions": {
        "enabled": True,
        "description": "All functions at top level",
    },
    "bottom_up_ordering": {
        "enabled": True,
        "description": "Write in dependency order (Level 0 -> main)",
    },
    "let_requires_initializer": {
        "enabled": True,
        "description": "let x = value, never let x;",
    },
    "return_requires_value": {
        "enabled": True,
        "description": "return expr, never return;",
    },
    "import_top_level_only": {
        "enabled": True,
        "description": "Never inside a function body",
    },
    "unique_variable_names": {
        "enabled": True,
        "description": "No reuse of i, x, result, acc across functions",
    },
    "map_get_needs_guard": {
        "enabled": True,
        "description": "Always check map.has before map.get",
    },
    "list_get_needs_guard": {
        "enabled": True,
        "description": "Always check list.len before list.get",
    },
    "string_concat_two_args": {
        "enabled": True,
        "description": "string.concat takes exactly 2 args, use + for 3+",
    },
    "eager_logical_operators": {
        "enabled": True,
        "description": "Both && and || operands always execute; use nested if when right side depends on left",
    },
}

WORKFLOW = ["fmt", "check", "build", "test", "run"]

DIAGNOSTICS = {
    "LEX001": "Unexpected character",
    "LEX002": "Unterminated string literal",
    "LEX003": "Invalid escape sequence",
    "SEM001": "Undefined identifier",
    "SEM002": "Forward reference",
    "SEM003": "Duplicate variable declaration",
    "TYP001": "Type mismatch in assignment",
    "TYP002": "Invalid operator for type",
    "TYP003": "Invalid arithmetic operand types",
    "TYP004": "Invalid comparison operand types",
    "TYP005": "Invalid arithmetic result type",
    "TYP006": "Invalid comparison result type",
    "TYP007": "Invalid logical operand types",
    "TYP008": "Mismatched return type",
    "TYP009": "Invalid function call arguments",
    "TYP010": "Invalid unary operator",
    "TYP011": "Invalid assignment target",
    "TYP012": "Argument count mismatch",
    "TYP013": "Assignment to function parameter",
    "CMP001": "Internal compiler error",
}

STDLIB_MODULES = [
    "string",
    "math",
    "list",
    "map",
    "set",
    "file",
    "path",
    "json",
    "csv",
    "time",
    "random",
    "environment",
    "convert",
    "io",
    "system",
]

TYPES = ["int", "float", "string", "bool", "list", "map", "set", "function", "None"]

OPERATORS = {
    "arithmetic": ["+", "-", "*", "/", "%"],
    "comparison": ["==", "!=", "<", "<=", ">", ">="],
    "logical": ["&&", "||", "!"],
    "assignment": ["="],
}


def get_language_context() -> dict[str, Any]:
    """Get AILang language context.

    Documentation is always embedded — only filenames are exposed, never paths.

    Returns:
        Dictionary with language rules, workflow, diagnostics, etc.
    """
    try:
        from pathlib import Path

        import compiler

        docs_path = Path(compiler.__file__).parent / "docs"
        documentation = {
            "agents_embedded": (docs_path / "AGENTS.md").exists(),
            "language_spec_embedded": (docs_path / "LANGUAGE_SPEC.md").exists(),
            "stdlib_reference_embedded": (docs_path / "STDLIB_REFERENCE.md").exists(),
            "documents": ["AGENTS.md", "LANGUAGE_SPEC.md", "STDLIB_REFERENCE.md"],
        }
    except Exception:
        documentation = {
            "agents_embedded": False,
            "language_spec_embedded": False,
            "stdlib_reference_embedded": False,
            "documents": ["AGENTS.md", "LANGUAGE_SPEC.md", "STDLIB_REFERENCE.md"],
        }

    return {
        "language": "AILang",
        "version": VERSION,
        "documentation": documentation,
        "rules": LANGUAGE_RULES,
        "workflow": WORKFLOW,
        "diagnostics": DIAGNOSTICS,
        "stdlib": STDLIB_MODULES,
        "types": TYPES,
        "operators": OPERATORS,
        "recommended_workflows": {
            "new_project": [
                "doctor",
                "docs AGENTS.md",
                "fmt",
                "check",
                "build",
                "run",
            ],
            "type_error": [
                "explain_diagnostic",
                "heal",
            ],
            "forward_reference": [
                "docs AGENTS.md",
                "fmt",
            ],
            "many_errors": [
                "check",
            ],
            "fresh_install": [
                "doctor",
                "docs AGENTS.md",
                "context --json",
            ],
        },
        "dx_tools": {
            "doctor": {
                "purpose": "Environment validation",
                "recommended_when": ["fresh_install", "unexpected_behavior"],
            },
            "heal": {
                "purpose": "Automatic fix suggestions",
                "recommended_when": ["type_errors", "import_errors"],
            },
            "fmt": {
                "purpose": "Canonical formatting",
                "recommended_when": ["before_build"],
            },
            "check": {
                "purpose": "Static validation",
                "recommended_when": ["many_errors", "before_build"],
            },
            "docs": {
                "purpose": "Documentation retrieval",
                "recommended_when": ["learning", "forward_reference"],
            },
            "context": {
                "purpose": "Machine-readable language context",
                "recommended_when": ["ai_assisted_development"],
            },
            "mcp": {
                "purpose": "AI tool integration via MCP",
                "recommended_when": ["ai_assisted_development"],
            },
        },
        "retrieval_policy": {
            "allowed": [
                "ail docs <DOCUMENT_NAME>",
                "MCP get_document(name=<filename>)",
                "ail context --json",
                "ail doctor",
                "ail heal",
            ],
            "forbidden": [
                "local filesystem access",
                "generated artifacts",
                "source tree inspection",
                "repository traversal",
                "compiler/ directory",
                "tools/ directory",
                "tests/ directory",
            ],
            "note": "All information must be retrieved through CLI commands or MCP tools. Never access the local filesystem directly.",
        },
    }
