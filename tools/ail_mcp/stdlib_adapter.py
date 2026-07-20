# AILang MCP Server - Stdlib Adapter
# Provides standard library information

"""Stdlib adapter for MCP server - provides AILang standard library information."""

from __future__ import annotations

from typing import Any

STDLIB = {
    "string": {
        "description": "String manipulation functions",
        "functions": {
            "concat": {
                "args": ["str", "str"],
                "returns": "str",
                "description": "Concatenate two strings",
            },
            "length": {
                "args": ["str"],
                "returns": "int",
                "description": "Get string length",
            },
            "contains": {
                "args": ["str", "str"],
                "returns": "bool",
                "description": "Check if string contains substring",
            },
            "uppercase": {
                "args": ["str"],
                "returns": "str",
                "description": "Convert to uppercase",
            },
            "lowercase": {
                "args": ["str"],
                "returns": "str",
                "description": "Convert to lowercase",
            },
            "trim": {
                "args": ["str"],
                "returns": "str",
                "description": "Remove leading/trailing whitespace",
            },
            "substring": {
                "args": ["str", "int", "int"],
                "returns": "str",
                "description": "Extract substring",
            },
            "find": {
                "args": ["str", "str"],
                "returns": "int",
                "description": "Find first occurrence of substring",
            },
            "find_from": {
                "args": ["str", "str", "int"],
                "returns": "int",
                "description": "Find substring starting from position",
            },
            "split": {
                "args": ["str", "str"],
                "returns": "list",
                "description": "Split string by delimiter",
            },
        },
    },
    "math": {
        "description": "Mathematical operations",
        "functions": {
            "add": {
                "args": ["number", "number"],
                "returns": "number",
                "description": "Add two numbers",
            },
            "sub": {
                "args": ["number", "number"],
                "returns": "number",
                "description": "Subtract two numbers",
            },
            "mul": {
                "args": ["number", "number"],
                "returns": "number",
                "description": "Multiply two numbers",
            },
            "div": {
                "args": ["number", "number"],
                "returns": "number",
                "description": "Divide two numbers",
            },
            "abs": {
                "args": ["number"],
                "returns": "number",
                "description": "Absolute value",
            },
            "min": {
                "args": ["number", "number"],
                "returns": "number",
                "description": "Minimum of two numbers",
            },
            "max": {
                "args": ["number", "number"],
                "returns": "number",
                "description": "Maximum of two numbers",
            },
        },
    },
    "list": {
        "description": "List (array) operations",
        "functions": {
            "new": {"args": [], "returns": "list", "description": "Create empty list"},
            "append": {
                "args": ["list", "any"],
                "returns": "none",
                "description": "Append item to list",
            },
            "len": {
                "args": ["list"],
                "returns": "int",
                "description": "Get list length",
            },
            "get": {
                "args": ["list", "int"],
                "returns": "any",
                "description": "Get item at index",
            },
            "contains": {
                "args": ["list", "any"],
                "returns": "bool",
                "description": "Check if list contains item",
            },
            "remove": {
                "args": ["list", "int"],
                "returns": "none",
                "description": "Remove item at index",
            },
            "clear": {
                "args": ["list"],
                "returns": "none",
                "description": "Clear all items",
            },
        },
    },
    "map": {
        "description": "Map (dictionary) operations",
        "functions": {
            "new": {"args": [], "returns": "map", "description": "Create empty map"},
            "set": {
                "args": ["map", "string", "any"],
                "returns": "none",
                "description": "Set key-value pair",
            },
            "get": {
                "args": ["map", "string"],
                "returns": "any",
                "description": "Get value by key",
            },
            "has": {
                "args": ["map", "string"],
                "returns": "bool",
                "description": "Check if key exists",
            },
            "delete": {
                "args": ["map", "string"],
                "returns": "none",
                "description": "Delete key-value pair",
            },
            "keys": {"args": ["map"], "returns": "list", "description": "Get all keys"},
            "clear": {
                "args": ["map"],
                "returns": "none",
                "description": "Clear all entries",
            },
        },
    },
    "set": {
        "description": "Set (unique collection) operations",
        "functions": {
            "new": {"args": [], "returns": "set", "description": "Create empty set"},
            "add": {
                "args": ["set", "any"],
                "returns": "none",
                "description": "Add item to set",
            },
            "contains": {
                "args": ["set", "any"],
                "returns": "bool",
                "description": "Check if item exists",
            },
            "len": {"args": ["set"], "returns": "int", "description": "Get set size"},
            "remove": {
                "args": ["set", "any"],
                "returns": "none",
                "description": "Remove item from set",
            },
            "clear": {
                "args": ["set"],
                "returns": "none",
                "description": "Clear all items",
            },
        },
    },
    "file": {
        "description": "File system operations",
        "functions": {
            "exists": {
                "args": ["str"],
                "returns": "bool",
                "description": "Check if file exists",
            },
            "read": {
                "args": ["str"],
                "returns": "str",
                "description": "Read file contents",
            },
            "write": {
                "args": ["str", "str"],
                "returns": "none",
                "description": "Write to file",
            },
            "append": {
                "args": ["str", "str"],
                "returns": "none",
                "description": "Append to file",
            },
            "remove": {
                "args": ["str"],
                "returns": "none",
                "description": "Delete file",
            },
        },
    },
    "path": {
        "description": "Path manipulation",
        "functions": {
            "join": {
                "args": ["str", "str"],
                "returns": "str",
                "description": "Join path components",
            },
            "basename": {
                "args": ["str"],
                "returns": "str",
                "description": "Get filename from path",
            },
            "dirname": {
                "args": ["str"],
                "returns": "str",
                "description": "Get directory from path",
            },
            "extension": {
                "args": ["str"],
                "returns": "str",
                "description": "Get file extension",
            },
            "normalize": {
                "args": ["str"],
                "returns": "str",
                "description": "Normalize path",
            },
        },
    },
    "json": {
        "description": "JSON parsing and serialization",
        "functions": {
            "parse": {
                "args": ["str"],
                "returns": "any",
                "description": "Parse JSON string",
            },
            "stringify": {
                "args": ["any"],
                "returns": "str",
                "description": "Convert to JSON string",
            },
        },
    },
    "csv": {
        "description": "CSV parsing and serialization",
        "functions": {
            "parse": {
                "args": ["str"],
                "returns": "list",
                "description": "Parse CSV string",
            },
            "parse_header": {
                "args": ["str"],
                "returns": "list",
                "description": "Parse CSV header row",
            },
            "stringify": {
                "args": ["list"],
                "returns": "str",
                "description": "Convert to CSV string",
            },
        },
    },
    "time": {
        "description": "Time and date operations",
        "functions": {
            "now": {
                "args": [],
                "returns": "int",
                "description": "Get current timestamp",
            },
            "timestamp": {
                "args": [],
                "returns": "int",
                "description": "Get Unix timestamp",
            },
            "sleep": {
                "args": ["int"],
                "returns": "none",
                "description": "Sleep for seconds",
            },
            "format": {
                "args": ["int", "str"],
                "returns": "str",
                "description": "Format timestamp",
            },
        },
    },
    "random": {
        "description": "Random number generation",
        "functions": {
            "int": {
                "args": ["int", "int"],
                "returns": "int",
                "description": "Random integer in range",
            },
            "float": {
                "args": [],
                "returns": "float",
                "description": "Random float between 0 and 1",
            },
            "choice": {
                "args": ["list"],
                "returns": "any",
                "description": "Random item from list",
            },
        },
    },
    "environment": {
        "description": "Environment variable access",
        "functions": {
            "get": {
                "args": ["str"],
                "returns": "str",
                "description": "Get environment variable",
            },
            "cwd": {
                "args": [],
                "returns": "str",
                "description": "Get current working directory",
            },
            "args": {
                "args": [],
                "returns": "list",
                "description": "Get command line arguments",
            },
        },
    },
    "convert": {
        "description": "Type conversion functions",
        "functions": {
            "to_string": {
                "args": ["any"],
                "returns": "str",
                "description": "Convert to string",
            },
            "to_int": {
                "args": ["any"],
                "returns": "int",
                "description": "Convert to integer",
            },
            "to_bool": {
                "args": ["any"],
                "returns": "bool",
                "description": "Convert to boolean",
            },
            "to_number": {
                "args": ["any"],
                "returns": "number",
                "description": "Convert to number",
            },
        },
    },
    "io": {
        "description": "Input/output operations",
        "functions": {
            "write": {
                "args": ["str"],
                "returns": "none",
                "description": "Write to stdout",
            },
            "writeln": {
                "args": ["str"],
                "returns": "none",
                "description": "Write line to stdout",
            },
            "println": {
                "args": ["str"],
                "returns": "none",
                "description": "Print line to stdout",
            },
        },
    },
    "system": {
        "description": "System operations",
        "functions": {
            "exit": {
                "args": ["int"],
                "returns": "none",
                "description": "Exit program with code",
            },
        },
    },
}


def get_stdlib(module: str | None = None) -> dict[str, Any]:
    """Get standard library information.

    Args:
        module: Optional module name to get details for

    Returns:
        Dictionary with module information
    """
    if module:
        if module in STDLIB:
            return {
                "module": module,
                **STDLIB[module],
            }
        else:
            return {
                "error": f"Module not found: {module}",
                "available_modules": list(STDLIB.keys()),
            }

    return {
        "modules": list(STDLIB.keys()),
        "details": STDLIB,
    }
