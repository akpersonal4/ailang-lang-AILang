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

# Lex error codes
LEX001_UNEXPECTED_CHARACTER = ErrorCode("LEX001", "Unexpected character")
LEX002_UNTERMINATED_STRING = ErrorCode("LEX002", "Unterminated string literal")
LEX003_INVALID_ESCAPE_SEQUENCE = ErrorCode("LEX003", "Invalid escape sequence")
LEX004_FLOAT_LITERAL = ErrorCode("LEX004", "Float literals are not supported")


@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    error_code: ErrorCode
    message: str
    line: int | None = None
    column: int | None = None
    file_path: str | None = None  # Source file path for multi-module compilation
    suggestion: str | None = None  # Optional suggestion for typo fixes


class DiagnosticReporter:
    def __init__(self) -> None:
        self.diagnostics: list[Diagnostic] = []

    def report(self, diagnostic: Diagnostic) -> None:
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
        return result

    @staticmethod
    def find_suggestion(unknown_name: str, known_names: set[str]) -> str | None:
        """Find a close matching identifier for spell-check suggestions."""
        matches = difflib.get_close_matches(unknown_name, known_names, n=1, cutoff=0.6)
        return matches[0] if matches else None
