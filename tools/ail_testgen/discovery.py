"""Discovery stage — find apps and existing tests."""

from __future__ import annotations

from pathlib import Path

from ail_platform.project import resolve_project_root
from tools.ail_testgen.models import AppInfo
from tools.common.filesystem import discover_apps as _discover_apps


def discover_apps() -> list[AppInfo]:
    """Discover all AILang apps in the project."""
    root = resolve_project_root()
    app_paths = _discover_apps(root)
    result = []
    for path in app_paths:
        name = path.parent.name
        line_count = _count_lines(path)
        result.append(AppInfo(name=name, source_file=path, line_count=line_count))
    return sorted(result, key=lambda a: a.name)


def discover_existing_tests() -> list[Path]:
    """Discover existing handwritten test files.

    Tests live alongside the apps they cover (the convention used by the
    AILang project: ``apps/<name>/tests/test_*.ail``). Generated tests
    are skipped by filename (``*_generated.ail``).
    """
    root = resolve_project_root()
    result: list[Path] = []
    apps_dir = root / "apps"
    if apps_dir.is_dir():
        for path in apps_dir.rglob("test_*.ail"):
            if path.name.endswith("_generated.ail"):
                continue
            result.append(path)
        for path in apps_dir.rglob("*_test.ail"):
            if path.name.endswith("_generated.ail"):
                continue
            result.append(path)
    # Honour legacy ``tests/`` directory layout too.
    tests_dir = root / "tests"
    if tests_dir.is_dir():
        for path in tests_dir.rglob("test_*.ail"):
            if "generated" in path.parts:
                continue
            result.append(path)
    return sorted(set(result))


def _count_lines(path: Path) -> int:
    try:
        return len(path.read_text(encoding="utf-8").splitlines())
    except (OSError, UnicodeDecodeError):
        return 0
