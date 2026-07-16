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

# Module error codes
MOD001_CIRCULAR_IMPORT = ErrorCode("MOD001", "Circular import detected")
MOD002_DUPLICATE_IMPORT = ErrorCode("MOD002", "Duplicate import")
MOD003_MODULE_NOT_FOUND = ErrorCode("MOD003", "Module not found")
MOD004_SYMBOL_NOT_FOUND = ErrorCode("MOD004", "Symbol not found in module")
MOD005_INVALID_MODULE_PATH = ErrorCode("MOD005", "Import path traversal attempt")

# Semantic error codes
SEM003_WRONG_ARG_COUNT = ErrorCode("SEM003", "Wrong number of arguments")

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
    # Type errors
    "TYP001": "  ail explain TYP001\n  ail heal",
    "TYP003": "  ail explain TYP003\n  ail heal",
    "TYP005": "  ail explain TYP005",
    "TYP006": "  ail explain TYP006",
    "TYP007": "  ail explain TYP007",
    "TYP008": "  ail explain TYP008\n  ail heal",
    # Semantic errors
    "SEM002": "  ail docs AGENTS.md\n  ail fmt",
    "SEM003": "  ail explain SEM003\n  ail heal",
    "SEM004": "  ail docs STDLIB_REFERENCE.md",
    # Module errors
    "MOD001": "  ail docs AGENTS.md",
    "MOD003": "  ail docs STDLIB_REFERENCE.md",
    "MOD004": "  ail docs STDLIB_REFERENCE.md",
}

# Error code descriptions for context
_ERROR_DESCRIPTIONS: dict[str, str] = {
    "TYP001": "Type mismatch",
    "TYP003": "Return type mismatch",
    "TYP005": "Arithmetic requires numeric types",
    "TYP006": "Comparison requires matching types",
    "TYP007": "Logical operator requires bool",
    "TYP008": "Assignment type mismatch",
    "SEM002": "Forward reference",
    "SEM003": "Wrong number of arguments",
    "SEM004": "Unknown stdlib function",
    "MOD001": "Circular import",
    "MOD003": "Module not found",
    "MOD004": "Symbol not found in module",
}


class DiagnosticReporter:
    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []

    def report(self, diagnostic: Diagnostic) -> None:
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
                location = f"{diagnostic.file_path}:{diagnostic.line}:{diagnostic.column}"
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
    def format_summary(reporter: 'DiagnosticReporter', file_path: str | None = None) -> str:
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
        error_codes = {d.error_code.code for d in reporter.diagnostics if d.severity == Severity.ERROR}
        
        suggestions = set()
        if error_codes & {"TYP001", "TYP003", "TYP005", "TYP006", "TYP007", "TYP008"}:
            suggestions.add("ail heal")
        if error_codes & {"SEM002"}:
            suggestions.add("ail docs AGENTS.md")
        if error_codes & {"MOD003", "MOD004"}:
            suggestions.add("ail docs STDLIB_REFERENCE.md")
        if len(reporter.diagnostics) > 3:
            suggestions.add("ail check")
        
        if suggestions:
            lines.append("")
            lines.append("Suggested next steps:")
            for s in sorted(suggestions):
                lines.append(f"  {s}")
        
        if file_path:
            lines.append(f"\nFor more help: ail explain <ERROR_CODE>")
        
        return "\n".join(lines)
