from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def get_project_root() -> Path:
    """Return the project root directory.

    Assumes platform/project.py is 3 levels deep under the project root:
      platform/project.py → platform/ → <project_root>/
    """
    return Path(__file__).resolve().parent.parent


def read_file_safe(path: Path) -> str | None:
    """Read a file if it exists and is readable.

    Returns None (never raises) for:
    - Missing file
    - Binary content (UnicodeDecodeError)
    - Permission error (OSError)
    - Encoding error (LookupError)
    """
    if not path.exists():
        return None
    try:
        return path.read_text(encoding="utf-8")
    except (UnicodeDecodeError, OSError, LookupError):
        return None


@dataclass
class AppInfo:
    name: str
    root: Path
    main_file: Path
    ail_files: list[Path] = field(default_factory=list)


def discover_apps(root: Path | None = None) -> list[AppInfo]:
    """Discover all AILang apps under root/apps/.

    Returns sorted list of AppInfo objects. Returns empty list if
    apps/ doesn't exist or contains no valid apps.
    """
    if root is None:
        root = get_project_root()
    apps_dir = root / "apps"
    if not apps_dir.is_dir():
        return []

    results: list[AppInfo] = []
    for entry in sorted(apps_dir.iterdir()):
        if not entry.is_dir():
            continue
        main_file = entry / "main.ail"
        if not main_file.is_file():
            continue
        ail_files = sorted(entry.rglob("*.ail"))
        results.append(
            AppInfo(
                name=entry.name,
                root=entry,
                main_file=main_file,
                ail_files=ail_files,
            )
        )
    return results


def ensure_output_dir(
    tool_name: str, root: Path | None = None, override: Path | None = None
) -> Path:
    """Return (and create) the output directory for a tool.

    Default: <project_root>/generated/<tool_name>/
    Override via --output-dir argument.
    """
    if override is not None:
        output_path = override.resolve()
    else:
        if root is None:
            root = get_project_root()
        output_path = root / "generated" / tool_name
    output_path.mkdir(parents=True, exist_ok=True)
    return output_path
