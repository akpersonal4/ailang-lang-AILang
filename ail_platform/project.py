from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path


def get_project_root() -> Path:
    """Return the project root directory.

    Assumes platform/project.py is 3 levels deep under the project root:
      platform/project.py → platform/ → <project_root>/
    """
    return Path(__file__).resolve().parent.parent


def _is_project_dir(candidate: Path) -> bool:
    """Return True if *candidate* is an AILang project root.

    ``ail.toml`` is the definitive user-project marker (`ail new` creates
    it). A bare ``.ail`` directory is NOT sufficient on its own: AILang's
    own config directory lives at ``~/.ail`` (state.json), so a walk-up
    would otherwise stop at the user's home directory and hijack every
    CWD-based tool. A ``.ail`` directory therefore only counts as a marker
    when the directory also looks like an AILang tree (has ``apps/``,
    ``compiler/``, ``stdlib/``, or ``tools/``) — e.g. the repository root,
    which has no ``ail.toml`` but does ship those trees.
    """
    if (candidate / "ail.toml").is_file():
        return True
    if (candidate / ".ail").is_dir():
        for tree_marker in ("apps", "compiler", "stdlib", "tools"):
            if (candidate / tree_marker).is_dir():
                return True
    return False


def resolve_project_root(start: Path | None = None) -> Path:
    """Resolve the user-facing AILang project root.

    Walks upward from *start* (default: the current working directory)
    looking for a project root (see :func:`_is_project_dir`), and falls
    back to *start* itself when no marker is found.

    This is distinct from :func:`get_project_root`, which returns the
    directory the *package* is installed in (a source checkout in dev, or
    ``site-packages`` under a wheel). User-facing tools (testgen, doctor,
    static-analyzer) must operate against the user's project, so they use
    this helper, not the package location.
    """
    if start is None:
        start = Path.cwd()
    current = start.resolve()
    while True:
        if _is_project_dir(current):
            return current
        if current == current.parent:
            break
        current = current.parent
    return start.resolve()


def bundled_apps_dir() -> Path:
    """Return the directory of AILang apps shipped inside the package.

    The wheel bundles a small set of internal AILang applications under
    ``ail_platform/data/apps/<name>/main.ail`` (mirroring the repository's
    ``apps/`` tree). These are what `ail benchmark` and `ail
    static-analyzer` fall back to when no source checkout is present.
    """
    return Path(__file__).resolve().parent / "data" / "apps"


def resolve_bundled_app(name: str) -> Path:
    """Resolve an internal AILang app (``apps/<name>/main.ail``).

    Priority:
      1. ``<project-root>/apps/<name>/main.ail`` — live source in a
         repository checkout (never bypassed in dev).
      2. The wheel-bundled copy under ``ail_platform/data/apps/``.

    Returns the path even if neither exists; callers are responsible for
    checking ``.is_file()`` and emitting a clear error.
    """
    live = get_project_root() / "apps" / name / "main.ail"
    if live.is_file():
        return live
    return bundled_apps_dir() / name / "main.ail"


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
