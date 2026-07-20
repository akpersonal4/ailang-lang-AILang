"""Environment recording for benchmark reproducibility.

Captures system state at measurement time so that another engineer can
independently reproduce results.
"""

from __future__ import annotations

import platform
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def get_project_root() -> Path:
    """Walk up from this file to find the repository root."""
    here = Path(__file__).resolve().parent
    for parent in [here] + list(here.parents):
        if (parent / "AGENTS.md").exists():
            return parent
    return here


def get_git_commit(root: Path | None = None) -> str:
    """Get the current git commit hash."""
    if root is None:
        root = get_project_root()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def get_git_branch(root: Path | None = None) -> str:
    """Get the current git branch name."""
    if root is None:
        root = get_project_root()
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=10,
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except Exception:
        pass
    return "unknown"


def get_git_dirty(root: Path | None = None) -> bool:
    """Check if the working tree has uncommitted changes."""
    if root is None:
        root = get_project_root()
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            capture_output=True,
            text=True,
            cwd=root,
            timeout=10,
        )
        return bool(result.stdout.strip())
    except Exception:
        return True


def snapshot() -> dict[str, Any]:
    """Capture the current environment as a dict.

    Returns immutable metadata about the machine, OS, Python, and git state
    at the time of measurement.
    """
    root = get_project_root()
    return {
        "os": {
            "system": platform.system(),
            "release": platform.release(),
            "version": platform.version(),
            "machine": platform.machine(),
            "processor": platform.processor(),
        },
        "python": {
            "version": sys.version,
            "executable": sys.executable,
        },
        "git": {
            "commit": get_git_commit(root),
            "branch": get_git_branch(root),
            "dirty": get_git_dirty(root),
            "root": str(root),
        },
        "timestamp": datetime.now(UTC).isoformat(),
    }
