"""LSP diagnostics — convert compiler diagnostics to LSP diagnostics.

Uses platform.diagnostics for the conversion logic.
"""

from __future__ import annotations

from typing import Any

from ail_platform.diagnostics import from_compiler_diagnostic


def get_diagnostics(doc: Any) -> list[dict[str, Any]]:
    """Convert compiler diagnostics to LSP diagnostics for a document."""
    doc.ensure_compiled()
    result: list[dict[str, Any]] = []

    for diag in doc.diagnostics:
        pd = from_compiler_diagnostic(diag)
        result.append(pd.to_lsp_dict())

    return result
