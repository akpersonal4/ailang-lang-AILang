from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum


class Severity(IntEnum):
    """Diagnostic severity levels, aligned with LSP DiagnosticSeverity."""
    ERROR = 1
    WARNING = 2
    INFO = 3
    HINT = 4


@dataclass
class DiagnosticPosition:
    line: int
    column: int

    def to_dict(self) -> dict:
        return {"line": self.line, "character": self.column}

    @classmethod
    def from_lsp_position(cls, pos: dict) -> DiagnosticPosition:
        return cls(line=pos.get("line", 0), column=pos.get("character", 0))


@dataclass
class DiagnosticRange:
    start: DiagnosticPosition
    end: DiagnosticPosition

    def to_dict(self) -> dict:
        return {"start": self.start.to_dict(), "end": self.end.to_dict()}

    @classmethod
    def from_lsp_range(cls, rng: dict) -> DiagnosticRange:
        return cls(
            start=DiagnosticPosition.from_lsp_position(rng.get("start", {})),
            end=DiagnosticPosition.from_lsp_position(rng.get("end", {})),
        )


@dataclass
class Diagnostic:
    range: DiagnosticRange
    severity: Severity
    message: str
    source: str = "ailang"
    code: str = ""

    def to_lsp_dict(self) -> dict:
        """Convert to LSP JSON-RPC diagnostic dict."""
        return {
            "range": self.range.to_dict(),
            "severity": self.severity.value,
            "message": self.message,
            "source": self.source,
            "code": self.code,
        }


def from_compiler_diagnostic(
    compiler_diag: object, source_text: str = ""
) -> Diagnostic:
    """Convert a compiler Diagnostic to a platform Diagnostic.

    Handles the compiler's Diagnostic type which has:
      - severity: Severity enum (ERROR/WARNING/NOTE)
      - error_code: ErrorCode enum
      - message: str
      - line: int (1-based)
      - column: int (1-based)

    Maps compiler severities:
      Severity.ERROR   → Severity.ERROR   (1)
      Severity.WARNING → Severity.WARNING (2)
      Severity.NOTE    → Severity.INFO    (3)
    """
    try:
        line = max(int(getattr(compiler_diag, "line", 1)) - 1, 0)
        column = max(int(getattr(compiler_diag, "column", 1)) - 1, 0)
    except (ValueError, TypeError):
        line = 0
        column = 0

    sev_raw = getattr(compiler_diag, "severity", None)
    sev_name = str(sev_raw) if sev_raw is not None else ""

    if "ERROR" in sev_name or sev_name == "Severity.ERROR":
        severity = Severity.ERROR
    elif "WARNING" in sev_name or sev_name == "Severity.WARNING":
        severity = Severity.WARNING
    else:
        severity = Severity.INFO

    message = str(getattr(compiler_diag, "message", ""))
    code = str(getattr(compiler_diag, "error_code", ""))

    return Diagnostic(
        range=DiagnosticRange(
            start=DiagnosticPosition(line=line, column=column),
            end=DiagnosticPosition(line=line, column=column + max(len(message.splitlines()[0]) if message else 1, 1)),
        ),
        severity=severity,
        message=message,
        source="ailang",
        code=code,
    )


def to_lsp_diagnostic(diag: Diagnostic) -> dict:
    """Convert platform Diagnostic to LSP JSON-RPC diagnostic dict.

    This is a convenience wrapper around Diagnostic.to_lsp_dict().
    """
    return diag.to_lsp_dict()
