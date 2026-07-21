"""LSP code actions — quick fixes with actual TextEdit operations."""

from __future__ import annotations

import re
from typing import Any


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

        # Quick fix: add import for stdlib module
        if diag_severity == 1:
            module_name = _extract_stdlib_module(message)
            if module_name:
                edit = _make_add_import_edit(doc, module_name)
                actions.append(
                    _quick_fix(
                        title=f"Import stdlib module '{module_name}'",
                        kind="quickfix",
                        diagnostics=[diag],
                        edit=edit,
                    )
                )

        # Quick fix: create missing module stub (for import errors)
        if (
            "import" in message.lower() or "module not found" in message.lower()
        ) and diag_severity == 1:
            missing = _extract_missing_module(message)
            if missing:
                actions.append(
                    _quick_fix(
                        title=f"Create module stub for '{missing}'",
                        kind="quickfix",
                        diagnostics=[diag],
                        edit=None,
                    )
                )

        # Quick fix: remove unused variable
        if "unused" in message.lower() and diag_severity == 2:
            edit = _make_remove_unused_edit(doc, diag_range)
            if edit:
                actions.append(
                    _quick_fix(
                        title="Remove unused variable",
                        kind="quickfix",
                        diagnostics=[diag],
                        edit=edit,
                    )
                )

    return actions


_STDLIB_MODULES = [
    "string",
    "math",
    "list",
    "array",
    "map",
    "set",
    "file",
    "path",
    "json",
    "csv",
    "time",
    "random",
    "environment",
    "convert",
    "io",
    "system",
]


def _extract_stdlib_module(message: str) -> str | None:
    """Extract a stdlib module name from an error message.

    Looks for patterns like:
        - 'Undefined identifier: string.concat'
        - 'Symbol not found in module: convert'
        - 'string not found'
    """
    msg_lower = message.lower()
    for mod in _STDLIB_MODULES:
        if mod in msg_lower:
            return mod
    return None


def _extract_missing_module(message: str) -> str | None:
    """Extract the missing module name from a 'Module not found' error."""
    match = re.search(r"[Mm]odule not found:\s*(\S+)", message)
    if match:
        return match.group(1)
    match = re.search(r"[Uu]ndefined identifier:\s*(\S+)", message)
    if match:
        name = match.group(1)
        if "." in name:
            return name.split(".")[0]
    return None


def _make_add_import_edit(doc: Any, module_name: str) -> dict[str, Any] | None:
    """Create a TextEdit that adds an import statement at the top of the file."""
    text = doc.text
    lines = text.split("\n")

    # Find the insertion point: after existing imports, before first non-import
    insert_line = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if (
            stripped.startswith("import ")
            or stripped == ""
            or stripped.startswith("//")
        ):
            insert_line = i + 1
        else:
            break

    # Check if this import already exists
    import_line = f"import {module_name};"
    for line in lines:
        if line.strip() == import_line:
            return None  # Already imported

    # Build the edit
    position = {"line": insert_line, "character": 0}
    return {
        "changes": {
            doc.uri: [
                {
                    "range": {
                        "start": position,
                        "end": position,
                    },
                    "newText": import_line + "\n",
                }
            ]
        }
    }


def _make_remove_unused_edit(
    doc: Any, diag_range: dict[str, Any]
) -> dict[str, Any] | None:
    """Create a TextEdit that removes the line containing an unused variable."""
    start = diag_range.get("start", {})
    line_num = start.get("line", 0)

    lines = doc.text.split("\n")
    if line_num >= len(lines):
        return None

    target_line = lines[line_num]
    stripped = target_line.strip()

    # Only remove if it's a let declaration
    if not stripped.startswith("let "):
        return None

    # Calculate range to remove the entire line (including newline)
    start_pos = {"line": line_num, "character": 0}
    if line_num + 1 < len(lines):
        end_pos = {"line": line_num + 1, "character": 0}
    else:
        end_pos = {"line": line_num, "character": len(target_line)}

    return {
        "changes": {
            doc.uri: [
                {
                    "range": {
                        "start": start_pos,
                        "end": end_pos,
                    },
                    "newText": "",
                }
            ]
        }
    }


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
