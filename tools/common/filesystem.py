"""Shared filesystem utilities for DX tools."""

from __future__ import annotations

from pathlib import Path


def get_project_root() -> Path:
    """Return the project root directory (assumes tools/common/ is 3 levels deep)."""
    return Path(__file__).resolve().parent.parent.parent


def read_file_safe(path: Path) -> str | None:
    """Read a file if it exists and is readable, return None otherwise."""
    if path.exists():
        try:
            return path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            return None
    return None


def ensure_output_dir(path: Path) -> Path:
    """Ensure an output directory exists and return it."""
    path.mkdir(parents=True, exist_ok=True)
    return path
