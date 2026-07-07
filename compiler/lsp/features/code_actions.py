"""LSP code actions (foundation) — quick fixes for diagnostics."""

from __future__ import annotations

from typing import Any

from compiler.diagnostics import Severity


def get_code_actions(
    doc: Any, _range: dict[str, Any], context: dict[str, Any]
) -> list[dict[str, Any]]:
    """Get available code actions for the given range and context."""
    actions: list[dict[str, Any]] = []

    diagnostics = context.get("diagnostics", [])
    for diag in diagnostics:
        if not isinstance(diag, dict):
            continue
        message = diag.get("message", "")
        diag_range = diag.get("range", {})
        diag_severity = diag.get("severity", 1)

        # Quick fix for import-related errors
        if "import" in message.lower() or "module not found" in message.lower():
            actions.append(
                _quick_fix(
                    title="Create missing module stub",
                    kind="quickfix",
                    diagnostics=[diag],
                    edit=None,
                )
            )

        # Quick fix for undefined identifiers that look like stdlib modules
        if diag_severity == 1 and _looks_like_stdlib(message):
            actions.append(
                _quick_fix(
                    title="Add import for stdlib module",
                    kind="quickfix",
                    diagnostics=[diag],
                    edit=None,
                )
            )

        # Quick fix for unused variable warnings
        if "unused" in message.lower():
            actions.append(
                _quick_fix(
                    title="Remove unused variable",
                    kind="quickfix",
                    diagnostics=[diag],
                    edit=None,
                )
            )

    return actions


def _looks_like_stdlib(message: str) -> bool:
    """Check if an error message refers to a possible stdlib module name."""
    _STDLIB_MODULES = [
        "string", "math", "list", "array", "map", "set",
        "file", "path", "json", "csv", "time", "random",
        "environment", "convert", "io", "system",
    ]
    msg_lower = message.lower()
    for mod in _STDLIB_MODULES:
        if mod in msg_lower:
            return True
    return False


def _quick_fix(
    title: str,
    kind: str,
    diagnostics: list[dict[str, Any]],
    edit: Any,
) -> dict[str, Any]:
    """Build a code action dict."""
    action: dict[str, Any] = {
        "title": title,
        "kind": kind,
        "diagnostics": diagnostics,
    }
    if edit is not None:
        action["edit"] = edit
    return action
