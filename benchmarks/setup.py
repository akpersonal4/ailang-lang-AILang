"""Benchmark dataset initialization.

Usage:
    python -m benchmarks.setup

Scans and registers benchmark datasets at benchmarks/datasets/<name>.
"""

from __future__ import annotations

import sys
from pathlib import Path

from benchmarks.framework.dataset import save_metadata, scan_project

HERE = Path(__file__).resolve().parent
DATASETS_DIR = HERE / "datasets"
METADATA_FILE = "metadata.json"


def find_repo_root() -> Path:
    """Find the repository root by walking up from this file."""
    for parent in [HERE] + list(HERE.parents):
        if (parent / "AGENTS.md").exists():
            return parent
    return HERE


def create_dataset(name: str, source_dir: Path) -> Path:
    """Create a dataset entry by scanning a source directory."""
    dataset_dir = DATASETS_DIR / name
    dataset_dir.mkdir(parents=True, exist_ok=True)

    metadata = scan_project(source_dir, name=name)
    meta_path = dataset_dir / METADATA_FILE
    save_metadata(metadata, meta_path)

    # Create a symlink or copy reference to the source
    ref_path = dataset_dir / "source_path.txt"
    ref_path.write_text(str(source_dir.resolve()), encoding="utf-8")

    print(
        f"  [OK] {name}: {metadata.loc} LOC, {metadata.file_count} files, "
        f"{metadata.symbol_count} symbols"
    )
    return dataset_dir


def main() -> int:
    """Initialize all benchmark datasets."""
    root = find_repo_root()

    print("AILang Benchmark Dataset Setup")
    print("=" * 40)
    print()

    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Small project ───────────────────────────────────────────
    small_src = root / "apps" / "calculator"
    if not small_src.is_dir():
        small_src = root / "ai_benchmarks" / "benchmark01_task_manager"
    if small_src.is_dir():
        create_dataset("small", small_src)
    else:
        print("  [SKIP] small — no source found")

    # ── Medium project ──────────────────────────────────────────
    medium_src = root / "apps" / "inventory_mgmt"
    if not medium_src.is_dir():
        medium_src = root / "apps" / "hotel_management"
    if medium_src.is_dir():
        create_dataset("medium", medium_src)
    else:
        print("  [SKIP] medium — no source found")

    # ── Current AILang repository ───────────────────────────────
    create_dataset("current_repo", root)

    print()
    print("Done. Datasets registered at benchmarks/datasets/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
