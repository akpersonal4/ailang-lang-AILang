from __future__ import annotations

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


@dataclass(frozen=True)
class Diagnostic:
    severity: Severity
    error_code: ErrorCode
    message: str
    line: int | None = None
    column: int | None = None


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
        if diagnostic.line is not None and diagnostic.column is not None:
            location = f" (line {diagnostic.line}, column {diagnostic.column})"
        return (
            f"{diagnostic.severity.name} {diagnostic.error_code.code}"
            f"{location}: {diagnostic.message}"
        )
