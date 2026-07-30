from __future__ import annotations

import difflib
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    ERROR = "error"
    WARNING = "warning"
    NOTE = "note"

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class ErrorCode:
    code: str
    message: str


# Parser error codes
PAR001_EXPECTED_TOKEN = ErrorCode("PAR001", "Expected token")
PAR002_INVALID_IMPORT_PATH = ErrorCode("PAR002", "Invalid import path")
PAR003_EXPECTED_IDENTIFIER = ErrorCode("PAR003", "Expected identifier")
PAR010_EXPECTED_ID_AFTER_FOR = ErrorCode("PAR010", "Expected identifier after 'for'")
PAR011_EXPECTED_IN_KEYWORD = ErrorCode("PAR011", "Expected 'in' after loop variable")
PAR012_EXPERIMENTAL_LOOPS = ErrorCode(
    "PAR012", "Use of 'for' requires --experimental-loops flag"
)

# Module error codes
MOD001_CIRCULAR_IMPORT = ErrorCode("MOD001", "Circular import detected")
MOD002_DUPLICATE_IMPORT = ErrorCode("MOD002", "Duplicate import")
MOD003_MODULE_NOT_FOUND = ErrorCode("MOD003", "Module not found")
MOD004_SYMBOL_NOT_FOUND = ErrorCode("MOD004", "Symbol not found in module")

# Semantic error codes
SEM001_DUPLICATE_DECLARATION = ErrorCode("SEM001", "Duplicate declaration")
SEM002_UNDEFINED_IDENTIFIER = ErrorCode("SEM002", "Undefined identifier")
SEM003_WRONG_ARG_COUNT = ErrorCode("SEM003", "Wrong number of arguments")
SEM004_UNKNOWN_STDLIB = ErrorCode("SEM004", "Unknown stdlib function")
SEM005_BUILTIN_SHADOW = ErrorCode("SEM005", "Shadowing built-in function")

# Type error codes
TYP001_UNKNOWN_TYPE = ErrorCode("TYP001", "Unknown type")
TYP002_RETURN_OUTSIDE_FN = ErrorCode("TYP002", "Return outside function")
TYP003_RETURN_TYPE_MISMATCH = ErrorCode("TYP003", "Return type mismatch")
TYP004_NON_BOOLEAN_CONDITION = ErrorCode("TYP004", "Non-boolean condition")
TYP005_NON_NUMERIC_OPERAND = ErrorCode("TYP005", "Non-numeric operand")
TYP006_TYPE_MISMATCH_COMPARISON = ErrorCode("TYP006", "Type mismatch in comparison")
TYP007_NON_BOOLEAN_LOGICAL = ErrorCode("TYP007", "Non-boolean logical operand")
TYP008_ASSIGNMENT_TYPE_MISMATCH = ErrorCode("TYP008", "Assignment type mismatch")
TYP009_NON_NUMERIC_UNARY = ErrorCode("TYP009", "Non-numeric unary operand")
TYP010_NON_BOOLEAN_NOT = ErrorCode("TYP010", "Non-boolean not operand")
TYP011_ARG_COUNT_MISMATCH = ErrorCode("TYP011", "Argument count mismatch")
TYP012_ARG_TYPE_MISMATCH = ErrorCode("TYP012", "Argument type mismatch")
TYP013_NON_FUNCTION_CALLEE = ErrorCode("TYP013", "Non-function callee")

# Compiler internal error codes
CMP001_INTERNAL_ERROR = ErrorCode("CMP001", "Internal compiler error")

# LSP error codes
LSP000_LSP_ERROR = ErrorCode("LSP000", "LSP server error")

# Language diagnostic codes (common mistakes)
WHILE001_NO_WHILE_LOOPS = ErrorCode("WHILE001", "AILang has no while loops")
LANG001_NESTED_FN = ErrorCode("LANG001", "Nested functions not allowed")
LANG002_LIST_SET_UNAVAILABLE = ErrorCode(
    "LANG002", "list.set() does not exist in AILang"
)
LANG003_STRING_REPLACE_UNAVAILABLE = ErrorCode(
    "LANG003", "string.replace() does not exist in AILang"
)
LANG004_IMPORT_IN_FUNCTION = ErrorCode(
    "LANG004", "Import statements are only allowed at the top level"
)

# Lex error codes
LEX001_UNEXPECTED_CHARACTER = ErrorCode("LEX001", "Unexpected character")
LEX002_UNTERMINATED_STRING = ErrorCode("LEX002", "Unterminated string literal")
LEX003_INVALID_ESCAPE_SEQUENCE = ErrorCode("LEX003", "Invalid escape sequence")


@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    error_code: ErrorCode
    message: str
    line: int | None = None
    column: int | None = None
    file_path: str | None = None  # Source file path for multi-module compilation
    suggestion: str | None = None  # Optional suggestion for typo fixes
    next_steps: str | None = None  # Context-aware tool suggestions


# Mapping of error codes to suggested next steps
_NEXT_STEPS: dict[str, str] = {
    # Parser errors
    "PAR001": "  Check syntax near the indicated location",
    "PAR002": "  Use a valid import path (e.g., import math)",
    "PAR003": "  Expected an identifier (variable or function name)",
    "PAR010": "  Expected identifier after 'for' keyword",
    "PAR011": "  Expected 'in' keyword after loop variable",
    "PAR012": "  Use --experimental-loops flag to enable for-in loops",
    # Type errors
    "TYP001": "  ail explain TYP001\n  ail heal",
    "TYP002": "  Return statements can only appear inside functions",
    "TYP003": "  ail explain TYP003\n  ail heal",
    "TYP004": "  if conditions must evaluate to true or false",
    "TYP005": "  ail explain TYP005",
    "TYP006": "  ail explain TYP006",
    "TYP007": "  ail explain TYP007",
    "TYP008": "  ail explain TYP008\n  ail heal",
    "TYP009": "  The unary minus operator requires a numeric operand",
    "TYP010": "  The ! operator requires a boolean operand",
    "TYP011": "  Check the function signature for expected argument count",
    "TYP012": "  Check the function signature for expected argument types",
    "TYP013": "  Only functions can be called",
    # Lexical errors
    "LEX001": "  Remove or replace the unexpected character",
    "LEX002": '  Add a closing quote (") at the end of the string literal',
    "LEX003": "  Use a valid escape sequence (\\n, \\t, \\\\, etc.)",
    # Semantic errors
    "SEM001": "  Rename one of the duplicate declarations to a unique name",
    "SEM002": "  ail docs AGENTS.md\n  ail fmt",
    "SEM003": "  ail explain SEM003\n  ail heal",
    "SEM004": "  ail docs STDLIB_REFERENCE.md",
    # Module errors
    "MOD001": "  ail docs AGENTS.md",
    "MOD002": "  Remove the duplicate import statement",
    "MOD003": "  ail docs STDLIB_REFERENCE.md",
    "MOD004": "  ail docs STDLIB_REFERENCE.md",
    # Compiler errors
    "CMP001": "  This is a compiler bug. Please report it.",
    "LSP000": "  Restart the LSP server",
    # Language diagnostic errors
    "WHILE001": "  ail explain WHILE001",
    "LANG001": "  ail explain LANG001",
    "LANG002": "  ail explain LANG002",
    "LANG003": "  ail explain LANG003",
    "LANG004": "  Move the import statement to the top level of the file",
}

# Error code descriptions for context
_ERROR_DESCRIPTIONS: dict[str, str] = {
    "PAR001": "Expected token",
    "PAR002": "Invalid import path",
    "PAR003": "Expected identifier",
    "PAR010": "Expected identifier after 'for'",
    "PAR011": "Expected 'in' after loop variable",
    "PAR012": "For requires --experimental-loops",
    "TYP001": "Type mismatch",
    "TYP002": "Return outside function",
    "TYP003": "Return type mismatch",
    "TYP004": "Non-boolean condition",
    "TYP005": "Arithmetic requires numeric types",
    "TYP006": "Comparison requires matching types",
    "TYP007": "Logical operator requires bool",
    "TYP008": "Assignment type mismatch",
    "TYP009": "Non-numeric unary operand",
    "TYP010": "Non-boolean not operand",
    "TYP011": "Argument count mismatch",
    "TYP012": "Argument type mismatch",
    "TYP013": "Non-function callee",
    "LEX001": "Unexpected character",
    "LEX002": "Unterminated string literal",
    "LEX003": "Invalid escape sequence",
    "SEM001": "Duplicate declaration",
    "SEM002": "Forward reference",
    "SEM003": "Wrong number of arguments",
    "SEM004": "Unknown stdlib function",
    "MOD001": "Circular import",
    "MOD002": "Duplicate import",
    "MOD003": "Module not found",
    "MOD004": "Symbol not found in module",
    "CMP001": "Internal compiler error",
    "LSP000": "LSP server error",
    "WHILE001": "AILang has no while loops",
    "LANG001": "Nested functions not allowed",
    "LANG002": "list.set() does not exist",
    "LANG003": "string.replace() does not exist",
    "LANG004": "Import in function body",
}


class DiagnosticReporter:
    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []

    def report(self, diagnostic: Diagnostic) -> None:
        # Skip duplicate diagnostics that are already in the list
        for existing in self.diagnostics:
            if (
                existing.error_code.code == diagnostic.error_code.code
                and existing.line == diagnostic.line
                and existing.column == diagnostic.column
                and existing.message == diagnostic.message
                and existing.file_path == diagnostic.file_path
            ):
                return
        # Auto-populate next_steps if not already set
        if diagnostic.next_steps is None and diagnostic.error_code.code in _NEXT_STEPS:
            # Create a new Diagnostic with next_steps (frozen dataclass)
            diagnostic = Diagnostic(
                severity=diagnostic.severity,
                error_code=diagnostic.error_code,
                message=diagnostic.message,
                line=diagnostic.line,
                column=diagnostic.column,
                file_path=diagnostic.file_path,
                suggestion=diagnostic.suggestion,
                next_steps=_NEXT_STEPS[diagnostic.error_code.code],
            )
        self.diagnostics.append(diagnostic)

    @property
    def error_count(self) -> int:
        return sum(
            1
            for diagnostic in self.diagnostics
            if diagnostic.severity is Severity.ERROR
        )

    @property
    def warning_count(self) -> int:
        return sum(
            1
            for diagnostic in self.diagnostics
            if diagnostic.severity is Severity.WARNING
        )


class DiagnosticFormatter:
    def format(self, diagnostic: Diagnostic) -> str:
        location = ""
        if diagnostic.file_path is not None:
            if diagnostic.line is not None and diagnostic.column is not None:
                location = (
                    f"{diagnostic.file_path}:{diagnostic.line}:{diagnostic.column}"
                )
            else:
                location = f"{diagnostic.file_path}"
        elif diagnostic.line is not None and diagnostic.column is not None:
            location = f"(line {diagnostic.line}, column {diagnostic.column})"

        result = (
            f"{location}  {diagnostic.severity.name} {diagnostic.error_code.code}:"
            f" {diagnostic.message}"
        )
        if diagnostic.suggestion:
            result += f"\n\nDid you mean: {diagnostic.suggestion}?"
        if diagnostic.next_steps:
            result += f"\n\nSuggested next steps:\n{diagnostic.next_steps}"
        return result

    @staticmethod
    def suggest_next_steps(error_code: str) -> str | None:
        """Get suggested next steps for an error code."""
        return _NEXT_STEPS.get(error_code)

    @staticmethod
    def get_error_description(error_code: str) -> str | None:
        """Get human-readable description for an error code."""
        return _ERROR_DESCRIPTIONS.get(error_code)

    @staticmethod
    def find_suggestion(unknown_name: str, known_names: set[str]) -> str | None:
        """Find a close matching identifier for spell-check suggestions."""
        matches = difflib.get_close_matches(unknown_name, known_names, n=1, cutoff=0.6)
        return matches[0] if matches else None

    @staticmethod
    def format_summary(
        reporter: DiagnosticReporter, file_path: str | None = None
    ) -> str:
        """Format a summary of diagnostics with suggested next steps."""
        error_count = reporter.error_count
        warning_count = reporter.warning_count

        if error_count == 0 and warning_count == 0:
            return ""

        lines = []
        if error_count > 0:
            lines.append(f"{error_count} diagnostic(s) found.")
        if warning_count > 0:
            lines.append(f"{warning_count} warning(s) found.")

        # Suggest next steps based on error types
        error_codes = {
            d.error_code.code
            for d in reporter.diagnostics
            if d.severity == Severity.ERROR
        }

        suggestions = set()
        if error_codes & {"TYP001", "TYP003", "TYP005", "TYP006", "TYP007", "TYP008"}:
            suggestions.add("ail heal")
        if error_codes & {"SEM002", "SEM001"}:
            suggestions.add("ail docs AGENTS.md")
        if error_codes & {"MOD003", "MOD004"}:
            suggestions.add("ail docs STDLIB_REFERENCE.md")
        if error_codes & {"WHILE001", "LANG001", "LANG002", "LANG003", "LANG004"}:
            suggestions.add("ail docs AGENTS.md")
        if len(reporter.diagnostics) > 3:
            suggestions.add("ail check")

        if suggestions:
            lines.append("")
            lines.append("Suggested next steps:")
            for s in sorted(suggestions):
                lines.append(f"  {s}")

        if file_path:
            lines.append("\nFor more help: ail explain <ERROR_CODE>")

        return "\n".join(lines)
