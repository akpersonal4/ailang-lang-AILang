"""Discovery stage — find apps and existing tests."""

from __future__ import annotations

from pathlib import Path

from tools.ail_testgen.models import AppInfo
from tools.common.filesystem import get_project_root, discover_apps as _discover_apps


def discover_apps() -> list[AppInfo]:
    """Discover all AILang apps in the project."""
    root = get_project_root()
    app_paths = _discover_apps(root)
    result = []
    for path in app_paths:
        name = path.parent.name
        line_count = _count_lines(path)
        result.append(AppInfo(name=name, source_file=path, line_count=line_count))
    return sorted(result, key=lambda a: a.name)


def discover_existing_tests() -> list[Path]:
    """Discover existing handwritten test files in tests/ (excluding generated)."""
    root = get_project_root()
    tests_dir = root / "tests"
    if not tests_dir.is_dir():
        return []
    result = []
    for path in tests_dir.rglob("*.py"):
        if "generated" in path.parts:
            continue
        result.append(path)
    return sorted(result)


def _count_lines(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        return 0
