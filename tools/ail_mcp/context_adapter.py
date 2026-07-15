# AILang MCP Server - Context Adapter
# Provides language context similar to ail context --json

"""Context adapter for MCP server - provides AILang language context."""

from __future__ import annotations

from typing import Any

VERSION = "1.0.5"

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

    Returns:
        Dictionary with language rules, workflow, diagnostics, etc.
    """
    # Find the documentation path (relative to compiler package)
    try:
        import compiler
        from pathlib import Path
        docs_path = Path(compiler.__file__).parent / "docs"
        documentation = {
            "agents": str(docs_path / "AGENTS.md"),
            "language_spec": str(docs_path / "LANGUAGE_SPEC.md"),
            "stdlib_reference": str(docs_path / "STDLIB_REFERENCE.md"),
            "agents_embedded": (docs_path / "AGENTS.md").exists(),
            "language_spec_embedded": (docs_path / "LANGUAGE_SPEC.md").exists(),
            "stdlib_reference_embedded": (docs_path / "STDLIB_REFERENCE.md").exists(),
        }
    except Exception:
        documentation = {
            "agents_embedded": False,
            "language_spec_embedded": False,
            "stdlib_reference_embedded": False,
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
    }
