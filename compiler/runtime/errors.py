"""Structured runtime error types for AILang diagnostics."""

from __future__ import annotations

from typing import Any


class RuntimeError(Exception):
    """Structured runtime error with full diagnostic context.

    Carries enough information for the CLI to render diagnostic output
    without exposing Python tracebacks or interpreter internals.

    Fields intentionally mirror the diagnostic format specified in M127:
    operation, reason, expected_type, actual_type, source_location, suggestion.
    """

    def __init__(
        self,
        operation: str = "",
        reason: str = "",
        expected_type: str = "",
        actual_type: str = "",
        source_file: str = "",
        source_line: int = 0,
        suggestion: str = "",
    ) -> None:
        self.operation = operation
        self.reason = reason
        self.expected_type = expected_type
        self.actual_type = actual_type
        self.source_file = source_file
        self.source_line = source_line
        self.suggestion = suggestion
        super().__init__(self._format_message())

    def _format_message(self) -> str:
        """Return a single-line summary for the exception chain."""
        loc = ""
        if self.source_file:
            loc = f" at {self.source_file}"
            if self.source_line:
                loc = f"{loc}:{self.source_line}"
        parts = [self.operation or "Runtime error"]
        if self.reason:
            parts.append(self.reason)
        if loc:
            parts.append(loc)
        return " — ".join(parts)

    def format_diagnostic(self) -> str:
        """Format as a structured multiline diagnostic (no Python internals)."""
        lines: list[str] = []
        lines.append("Runtime Error")
        lines.append("")
        lines.append(f"Operation:")
        lines.append(f"  {self.operation or '(unknown)'}")
        lines.append("")
        lines.append(f"Reason:")
        lines.append(f"  {self.reason or 'An unexpected error occurred.'}")
        if self.expected_type:
            lines.append("")
            lines.append("Expected:")
            lines.append(f"  {self.expected_type}")
        if self.actual_type:
            lines.append("")
            lines.append("Received:")
            lines.append(f"  {self.actual_type}")
        if self.source_file:
            lines.append("")
            lines.append("Location:")
            loc = self.source_file
            if self.source_line:
                loc = f"{loc}:{self.source_line}"
            lines.append(f"  {loc}")
        if self.suggestion:
            lines.append("")
            lines.append("Suggestion:")
            lines.append(f"  {self.suggestion}")
        return "\n".join(lines)

    @staticmethod
    def _type_name(value: Any) -> str:
        """Return a human-readable type name for an AILang runtime value."""
        if isinstance(value, list):
            return "List"
        if isinstance(value, dict):
            return "Map"
        if isinstance(value, str):
            return "String"
        if isinstance(value, bool):
            return "Bool"
        if isinstance(value, int):
            return "Int"
        if isinstance(value, float):
            return "Float"
        if isinstance(value, set):
            return "Set"
        if value is None:
            return "Null"
        return type(value).__name__

    @staticmethod
    def _span_to_line(source_text: str, span: int | None) -> int:
        """Convert a character offset to a 1-based line number."""
        if span is None or span < 0:
            return 0
        return source_text[:span].count("\n") + 1
