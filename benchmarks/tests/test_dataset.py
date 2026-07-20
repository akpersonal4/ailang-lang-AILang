"""Tests for dataset scanning and metadata computation."""

from __future__ import annotations

from pathlib import Path

import pytest

from benchmarks.framework.dataset import (
    DatasetMetadata,
    load_dataset,
    save_metadata,
    scan_project,
)
from benchmarks.framework.metrics import compute_repo_metrics

# ── Fixtures ─────────────────────────────────────────────────────────


@pytest.fixture
def repo_root() -> Path:
    """Find the repository root."""
    here = Path(__file__).resolve().parent
    for parent in [here] + list(here.parents):
        if (parent / "AGENTS.md").exists():
            return parent
    return here


@pytest.fixture
def apps_dir(repo_root: Path) -> Path:
    return repo_root / "apps"


@pytest.fixture
def compiler_dir(repo_root: Path) -> Path:
    return repo_root / "compiler"


# ── Acceptance Tests ─────────────────────────────────────────────────


class TestScanProject:
    """Verify dataset scanning produces correct, deterministic metadata."""

    def test_scans_existing_directory(self, apps_dir: Path):
        metadata = scan_project(apps_dir, name="apps")
        assert metadata.name == "apps"
        assert metadata.file_count > 0
        assert metadata.loc > 0
        assert metadata.symbol_count >= 0

    def test_scans_compiler_directory(self, compiler_dir: Path):
        metadata = scan_project(compiler_dir, name="compiler")
        assert metadata.name == "compiler"
        assert metadata.file_count > 0
        assert metadata.loc > 0
        assert metadata.symbol_count >= 0

    def test_deterministic_metadata(self, apps_dir: Path):
        m1 = scan_project(apps_dir, name="test")
        m2 = scan_project(apps_dir, name="test")
        assert m1.loc == m2.loc
        assert m1.file_count == m2.file_count
        assert m1.symbol_count == m2.symbol_count

    def test_raises_on_nonexistent_directory(self):
        with pytest.raises(NotADirectoryError):
            scan_project(Path("/nonexistent/path"))

    def test_detects_function_symbols(self, tmp_path: Path):
        src = tmp_path / "test.ail"
        src.write_text("fn main() { return 0; }\nfn helper(x) { return x; }")
        metadata = scan_project(tmp_path, name="test")
        assert metadata.symbol_count >= 2

    def test_detects_imports(self, tmp_path: Path):
        src = tmp_path / "main.ail"
        src.write_text("import math;\nimport string;\nfn main() { return 0; }")
        metadata = scan_project(tmp_path, name="test")
        assert metadata.dependency_count >= 2


class TestLoadDataset:
    """Verify dataset loading produces correct Dataset objects."""

    def test_loads_from_directory(self, apps_dir: Path):
        dataset = load_dataset(apps_dir)
        assert dataset.metadata.file_count > 0
        assert dataset.root == apps_dir

    def test_ail_files_returns_sorted_list(self, apps_dir: Path):
        dataset = load_dataset(apps_dir)
        files = dataset.ail_files
        if files:
            assert all(f.suffix == ".ail" for f in files)
            assert files == sorted(files)


class TestSaveMetadata:
    """Verify metadata serialization round-trips correctly."""

    def test_round_trip(self, tmp_path: Path):
        src = tmp_path / "project"
        src.mkdir()
        (src / "main.ail").write_text("fn main() { return 0; }")

        metadata = scan_project(src, name="test")
        save_metadata(metadata, tmp_path / "meta.json")

        import json

        loaded = json.loads((tmp_path / "meta.json").read_text(encoding="utf-8"))
        assert loaded["name"] == "test"
        assert loaded["loc"] > 0
        assert loaded["file_count"] == 1

    def test_metadata_is_frozen(self):
        metadata = DatasetMetadata(
            name="test",
            description="",
            language="ailang",
            loc=100,
            file_count=5,
            module_count=2,
            symbol_count=10,
            function_count=8,
            variable_count=2,
            doc_size_bytes=500,
            dependency_count=3,
            path="/tmp",
        )
        with pytest.raises(Exception):
            metadata.loc = 200  # frozen dataclass, should raise


# ── Regression Tests ────────────────────────────────────────────────


class TestRegression:
    """Verify no regressions in metric computation."""

    def test_empty_directory(self, tmp_path: Path):
        metadata = scan_project(tmp_path, name="empty")
        assert metadata.loc == 0
        assert metadata.file_count == 0
        assert metadata.symbol_count == 0
        assert metadata.dependency_count == 0

    def test_handles_binary_files_gracefully(self, tmp_path: Path):
        (tmp_path / "binary.ail").write_bytes(b"\x00\x01\x02\x03")
        metadata = scan_project(tmp_path, name="binary")
        assert metadata.loc >= 0  # should not crash

    def test_repo_metrics_consistency(self, compiler_dir: Path):
        """RepositoryMetrics should match DatasetMetadata for same directory."""
        meta = scan_project(compiler_dir, name="compiler")
        metrics = compute_repo_metrics(compiler_dir)
        assert metrics.files == meta.file_count
        assert metrics.loc == meta.loc
