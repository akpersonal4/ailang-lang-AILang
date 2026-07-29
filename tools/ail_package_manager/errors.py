"""Structured package validation error with deterministic diagnostics.

Follows the M127 P0 diagnostic pattern established by compiler.runtime.errors.RuntimeError.
"""

from __future__ import annotations


class PackageError(Exception):
    """Structured exception for package validation failures.

    Fields:
        reason: Concise description of what failed.
        suggestion: Actionable guidance to fix the problem.
        detail: Optional additional context.
        manifest_path: Optional path to the ail.toml that failed validation.
        location: Optional location within the file (e.g. field name or line).

    All diagnostics are deterministic — no Python tracebacks,
    no implementation details, no non-deterministic content.
    """

    def __init__(
        self,
        reason: str,
        suggestion: str = "",
        detail: str = "",
        manifest_path: str = "",
        location: str = "",
    ) -> None:
        self.reason = reason
        self.suggestion = suggestion
        self.detail = detail
        self.manifest_path = manifest_path
        self.location = location
        super().__init__(self._format_short())

    def _format_short(self) -> str:
        """Compact single-line representation for __str__ fallback."""
        parts = [f"Package Validation Error: {self.reason}"]
        if self.manifest_path:
            parts.append(f" ({self.manifest_path})")
        return "".join(parts)

    def format_diagnostic(self) -> str:
        """Deterministic human-readable diagnostic."""
        lines: list[str] = []
        lines.append("Package Validation Error")
        lines.append("")

        lines.append("Reason:")
        lines.append(f"  {self.reason}")
        lines.append("")

        if self.manifest_path:
            lines.append("Manifest:")
            lines.append(f"  {self.manifest_path}")
            lines.append("")

        if self.location:
            lines.append("Location:")
            lines.append(f"  {self.location}")
            lines.append("")

        if self.detail:
            lines.append("Detail:")
            lines.append(f"  {self.detail}")
            lines.append("")

        if self.suggestion:
            lines.append("Suggestion:")
            lines.append(f"  {self.suggestion}")
            lines.append("")

        return "\n".join(lines)
