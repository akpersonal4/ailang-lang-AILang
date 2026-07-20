# AILang MCP Server - Diagnostics Adapter
# Provides detailed explanations for diagnostic codes

"""Diagnostics adapter for MCP server - explains AILang diagnostic codes."""

from __future__ import annotations

from typing import Any

DIAGNOSTICS = {
    "LEX001": {
        "title": "Unexpected Character",
        "description": "The lexer encountered a character that is not valid in AILang syntax.",
        "cause": "Typo, unsupported character, or encoding issue.",
        "fix": "Check for typos, unsupported characters (e.g., curly quotes), or encoding issues.",
        "example": {
            "bad": 'fn main() { let x = "hello"; return 0 }',
            "good": 'fn main() { let x = "hello"; return 0 }',
        },
    },
    "LEX002": {
        "title": "Unterminated String Literal",
        "description": "A string literal was opened but never closed.",
        "cause": "Missing closing double quote.",
        "fix": "Add the closing double quote to complete the string.",
        "example": {
            "bad": 'fn main() { let x = "hello; return 0 }',
            "good": 'fn main() { let x = "hello"; return 0 }',
        },
    },
    "LEX003": {
        "title": "Invalid Escape Sequence",
        "description": "The string contains an escape sequence that is not supported.",
        "cause": "Using unsupported escape sequences like \\x, \\u, or \\0.",
        "fix": 'Use only supported escape sequences: \\n, \\t, \\r, \\\\, \\"',
        "example": {
            "bad": 'fn main() { let x = "\\x41"; return 0 }',
            "good": 'fn main() { let x = "\\n"; return 0 }',
        },
    },
    "SEM001": {
        "title": "Undefined Identifier",
        "description": "The code references a variable or function that has not been declared.",
        "cause": "Typo, missing declaration, or forward reference.",
        "fix": "Check spelling, ensure the identifier is declared before use.",
        "example": {
            "bad": "fn main() { let x = y; return 0 }\nfn y() { return 42 }",
            "good": "fn y() { return 42 }\nfn main() { let x = y; return 0 }",
        },
    },
    "SEM002": {
        "title": "Forward Reference",
        "description": "The code references a function that is defined later in the file.",
        "cause": "Function is called before it is defined.",
        "fix": "Move the function definition before its first use (bottom-up ordering).",
        "example": {
            "bad": "fn main() { let x = y(); return 0 }\nfn y() { return 42 }",
            "good": "fn y() { return 42 }\nfn main() { let x = y(); return 0 }",
        },
    },
    "SEM003": {
        "title": "Duplicate Variable Declaration",
        "description": "A variable with the same name has already been declared in this scope.",
        "cause": "Using the same variable name twice in the same scope.",
        "fix": "Use a different variable name or reuse the existing variable.",
        "example": {
            "bad": "fn main() { let x = 1; let x = 2; return 0 }",
            "good": "fn main() { let x = 1; let y = 2; return 0 }",
        },
    },
    "TYP001": {
        "title": "Type Mismatch in Assignment",
        "description": "The value being assigned does not match the expected type.",
        "cause": "Assigning a value of incompatible type.",
        "fix": "Ensure the value matches the expected type, or use convert functions.",
        "example": {
            "bad": 'fn main() { let x = "hello"; x = 42; return 0 }',
            "good": 'fn main() { let x = "hello"; x = "world"; return 0 }',
        },
    },
    "TYP002": {
        "title": "Invalid Operator for Type",
        "description": "The operator is not supported for the given type.",
        "cause": "Using an operator with incompatible types.",
        "fix": "Use operators only with compatible types (e.g., + with numbers or strings).",
        "example": {
            "bad": 'fn main() { let x = "hello" - "world"; return 0 }',
            "good": 'fn main() { let x = "hello" + "world"; return 0 }',
        },
    },
    "TYP003": {
        "title": "Invalid Arithmetic Operand Types",
        "description": "The operands for an arithmetic operation are not valid.",
        "cause": "Using arithmetic operators with non-numeric types.",
        "fix": "Ensure both operands are numbers (int or float).",
        "example": {
            "bad": 'fn main() { let x = "hello" + 42; return 0 }',
            "good": "fn main() { let x = 42 + 42; return 0 }",
        },
    },
    "TYP004": {
        "title": "Invalid Comparison Operand Types",
        "description": "The operands for a comparison operation are not valid.",
        "cause": "Using comparison operators with incompatible types.",
        "fix": "Ensure both operands are of compatible types.",
        "example": {
            "bad": 'fn main() { let x = "hello" < 42; return 0 }',
            "good": "fn main() { let x = 42 < 42; return 0 }",
        },
    },
    "TYP005": {
        "title": "Invalid Arithmetic Result Type",
        "description": "The result of an arithmetic operation is not a valid type.",
        "cause": "Arithmetic operation that produces an invalid result type.",
        "fix": "Ensure the operation produces a numeric result.",
        "example": {
            "bad": "fn main() { let x = true + 1; return 0 }",
            "good": "fn main() { let x = 1 + 1; return 0 }",
        },
    },
    "TYP006": {
        "title": "Invalid Comparison Result Type",
        "description": "The result of a comparison operation is not a valid type.",
        "cause": "Comparison operation that produces an invalid result type.",
        "fix": "Ensure the operation produces a boolean result.",
        "example": {
            "bad": "fn main() { let x = (1 + 1); return 0 }",
            "good": "fn main() { let x = 1 == 1; return 0 }",
        },
    },
    "TYP007": {
        "title": "Invalid Logical Operand Types",
        "description": "The operands for a logical operation are not valid.",
        "cause": "Using logical operators with non-boolean types.",
        "fix": "Ensure both operands are booleans.",
        "example": {
            "bad": "fn main() { let x = 1 && true; return 0 }",
            "good": "fn main() { let x = true && true; return 0 }",
        },
    },
    "TYP008": {
        "title": "Mismatched Return Type",
        "description": "The return value does not match the function's expected return type.",
        "cause": "Returning a value of incompatible type.",
        "fix": "Ensure the return value matches the function's declared return type.",
        "example": {
            "bad": 'fn y() { return "hello" }\nfn main() { let x = y(); return 0 }',
            "good": "fn y() { return 42 }\nfn main() { let x = y(); return 0 }",
        },
    },
    "TYP009": {
        "title": "Invalid Function Call Arguments",
        "description": "The arguments passed to a function do not match its signature.",
        "cause": "Wrong number or types of arguments.",
        "fix": "Check the function signature and pass the correct arguments.",
        "example": {
            "bad": "fn add(a, b) { return a + b }\nfn main() { let x = add(1); return 0 }",
            "good": "fn add(a, b) { return a + b }\nfn main() { let x = add(1, 2); return 0 }",
        },
    },
    "TYP010": {
        "title": "Invalid Unary Operator",
        "description": "The unary operator is not valid for the given type.",
        "cause": "Using a unary operator with an incompatible type.",
        "fix": "Use unary operators only with compatible types (e.g., - with numbers).",
        "example": {
            "bad": 'fn main() { let x = -"hello"; return 0 }',
            "good": "fn main() { let x = -42; return 0 }",
        },
    },
    "TYP011": {
        "title": "Invalid Assignment Target",
        "description": "The left side of an assignment is not a valid target.",
        "cause": "Trying to assign to a value that cannot be assigned.",
        "fix": "Assign only to variables, not to literals or expressions.",
        "example": {
            "bad": "fn main() { 42 = x; return 0 }",
            "good": "fn main() { let x = 42; return 0 }",
        },
    },
    "TYP012": {
        "title": "Argument Count Mismatch",
        "description": "The number of arguments passed to a function does not match its definition.",
        "cause": "Calling a function with wrong number of arguments.",
        "fix": "Check the function definition and pass the correct number of arguments.",
        "example": {
            "bad": "fn add(a, b) { return a + b }\nfn main() { let x = add(1, 2, 3); return 0 }",
            "good": "fn add(a, b) { return a + b }\nfn main() { let x = add(1, 2); return 0 }",
        },
    },
    "TYP013": {
        "title": "Assignment to Function Parameter",
        "description": "Trying to assign a value to a function parameter.",
        "cause": "Function parameters are read-only in AILang.",
        "fix": "Create a new local variable instead of modifying the parameter.",
        "example": {
            "bad": "fn add(a, b) { a = a + b; return a }\nfn main() { let x = add(1, 2); return 0 }",
            "good": "fn add(a, b) { let result = a + b; return result }\nfn main() { let x = add(1, 2); return 0 }",
        },
    },
    "CMP001": {
        "title": "Internal Compiler Error",
        "description": "An unexpected error occurred in the compiler.",
        "cause": "Bug in the compiler implementation.",
        "fix": "Report this issue to the AILang maintainers with the source code that triggered it.",
        "example": None,
    },
}


def explain_diagnostic(code: str) -> dict[str, Any]:
    """Get detailed explanation for a diagnostic code.

    Args:
        code: Diagnostic code (e.g., SEM002, TYP005)

    Returns:
        Dictionary with diagnostic explanation
    """
    if code in DIAGNOSTICS:
        return {
            "code": code,
            **DIAGNOSTICS[code],
        }

    return {
        "code": code,
        "error": f"Unknown diagnostic code: {code}",
        "available_codes": list(DIAGNOSTICS.keys()),
    }
