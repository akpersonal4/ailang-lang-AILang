"""Shared reporting utilities for DX tools.

Provides dual-format (Markdown + JSON) report writing, the standard
pattern used by all AILang DX tools.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def write_json_report(data: Any, path: Path) -> Path:
    """Write a JSON report to the given path.

    Returns the path for chaining.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, default=str), encoding="utf-8")
    return path


def write_markdown_report(content: str, path: Path) -> Path:
    """Write a Markdown report to the given path.

    Returns the path for chaining.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return path
