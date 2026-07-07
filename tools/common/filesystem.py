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


def discover_apps(root: Path) -> list[Path]:
    """Discover all AILang app main files under root/apps/."""
    apps_dir = root / "apps"
    if not apps_dir.is_dir():
        return []
    return sorted(apps_dir.glob("*/main.ail"))


def list_py_files(root: Path) -> list[Path]:
    """Recursively list all .py files under root, excluding common noise dirs."""
    exclude = {".venv", ".venv_test", ".git", ".mypy_cache", ".pytest_cache", ".ruff_cache", "node_modules", "__pycache__"}
    result = []
    for path in root.rglob("*.py"):
        if not any(part in exclude for part in path.parts):
            result.append(path)
    return sorted(result)
