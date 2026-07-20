"""Dataset management for benchmarks.

Each dataset is a version-controlled project directory with known metadata
(LOC, file count, module count, symbols, documentation size). Datasets are
immutable for a given benchmark run.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetMetadata:
    """Immutable metadata describing a benchmark dataset."""

    name: str
    description: str
    language: str  # "ailang" | "python" | etc.
    loc: int
    file_count: int
    module_count: int
    symbol_count: int
    function_count: int
    variable_count: int
    doc_size_bytes: int
    dependency_count: int
    path: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class Dataset:
    """A benchmark dataset — project source + immutable metadata."""

    metadata: DatasetMetadata
    root: Path

    def resolve(self, *parts: str) -> Path:
        return self.root.joinpath(*parts)

    @property
    def ail_files(self) -> list[Path]:
        if not self.root.is_dir():
            return []
        return sorted(f for f in self.root.rglob("*.ail") if _is_project_file(f))

    @property
    def py_files(self) -> list[Path]:
        if not self.root.is_dir():
            return []
        return sorted(f for f in self.root.rglob("*.py") if _is_project_file(f))

    @property
    def all_source_files(self) -> list[Path]:
        return self.ail_files + self.py_files


IGNORE_DIRS = {
    ".venv",
    "venv",
    "env",
    ".env",
    ".git",
    ".svn",
    "__pycache__",
    "node_modules",
    ".mypy_cache",
    ".pytest_cache",
    ".vscode",
    ".idea",
}


def _is_project_file(path: Path) -> bool:
    """Check if a file should be included in project scanning.

    Excludes common non-project directories (virtualenvs, git, caches).
    """
    for parent in path.parents:
        if parent.name in IGNORE_DIRS:
            return False
    return True


def scan_project(
    root: Path, name: str = "", language: str = "ailang"
) -> DatasetMetadata:
    """Scan a project directory and compute its metadata.

    This is the canonical metadata extractor. All datasets use this.
    """
    if not root.is_dir():
        raise NotADirectoryError(f"Dataset root not found: {root}")

    ail_files = sorted(f for f in root.rglob("*.ail") if _is_project_file(f))
    py_files = sorted(f for f in root.rglob("*.py") if _is_project_file(f))
    all_files = ail_files + py_files

    loc = 0
    doc_size_bytes = 0
    symbols: set[str] = set()
    deps: set[str] = set()
    function_count = 0
    variable_count = 0

    for f in all_files:
        try:
            text = f.read_text(encoding="utf-8")
            lines = [l for l in text.splitlines() if l.strip()]
            loc += len(lines)
            doc_size_bytes += len(text.encode("utf-8"))
        except Exception:
            pass

    for f in ail_files:
        try:
            text = f.read_text(encoding="utf-8")
            for line in text.splitlines():
                stripped = line.strip()
                if stripped.startswith("fn "):
                    parts = stripped.split("(", 1)
                    fn_name = parts[0].removeprefix("fn ").strip()
                    if fn_name:
                        symbols.add(fn_name)
                        function_count += 1
                elif stripped.startswith("import "):
                    mod = stripped.removeprefix("import ").strip().rstrip(";")
                    if mod:
                        deps.add(mod)
                elif stripped.startswith("let "):
                    var_name = stripped.removeprefix("let ").split("=", 1)[0].strip()
                    if var_name:
                        symbols.add(var_name)
                        variable_count += 1
        except Exception:
            pass

    return DatasetMetadata(
        name=name or root.name,
        description=f"Project at {root}",
        language=language,
        loc=loc,
        file_count=len(all_files),
        module_count=len(set(f.parent for f in ail_files)),
        symbol_count=len(symbols),
        function_count=function_count,
        variable_count=variable_count,
        doc_size_bytes=doc_size_bytes,
        dependency_count=len(deps),
        path=str(root),
    )


def load_dataset(root: Path, metadata: DatasetMetadata | None = None) -> Dataset:
    """Load a dataset, optionally with pre-computed metadata."""
    if metadata is None:
        metadata = scan_project(root, name=root.name)
    return Dataset(metadata=metadata, root=root)


def save_metadata(metadata: DatasetMetadata, path: Path) -> Path:
    """Save dataset metadata as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(metadata.to_dict(), indent=2, default=str),
        encoding="utf-8",
    )
    return path
