"""LSP diagnostics — convert compiler diagnostics to LSP diagnostics."""

from __future__ import annotations

from typing import Any

from compiler.diagnostics import Severity
from compiler.lsp.protocol import (
    Diagnostic as LspDiagnostic,
)
from compiler.lsp.protocol import (
    Position,
    Range,
)


def get_diagnostics(doc: Any) -> list[dict[str, Any]]:
    """Convert compiler diagnostics to LSP diagnostics for a document."""
    doc.ensure_compiled()
    result: list[LspDiagnostic] = []

    for diag in doc.diagnostics:
        severity_map = {
            Severity.ERROR: 1,
            Severity.WARNING: 2,
            Severity.NOTE: 3,
        }
        severity = severity_map.get(diag.severity, 1)

        line = diag.line if diag.line is not None else 1
        col = diag.column if diag.column is not None else 0

        start_pos = Position(line - 1, max(col - 1, 0))
        end_pos = Position(line - 1, max(col, 0))
        rng = Range(start_pos, end_pos)

        result.append(
            LspDiagnostic(
                range=rng,
                message=f"[{diag.error_code.code}] {diag.message}",
                severity=severity,
                source="ailang",
            )
        )

    return [d.to_dict() for d in result]
