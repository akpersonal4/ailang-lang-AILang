"""Tests for watch mode incremental compilation (DX-016)."""

from __future__ import annotations

import tempfile
import time
from pathlib import Path

import pytest

from compiler.watch import FileCache, FileCacheEntry, IncrementalCompiler, file_hash


# =============================================================================
# File hash tests
# =============================================================================


class TestFileHash:
    def test_hash_is_deterministic(self, tmp_path: Path) -> None:
        fp = tmp_path / "test.ail"
        fp.write_text("fn main() { return 0 }", encoding="utf-8")
        h1 = file_hash(str(fp))
        h2 = file_hash(str(fp))
        assert h1 == h2

    def test_hash_changes_on_modification(self, tmp_path: Path) -> None:
        fp = tmp_path / "test.ail"
        fp.write_text("fn main() { return 0 }", encoding="utf-8")
        h1 = file_hash(str(fp))
        fp.write_text("fn main() { return 1 }", encoding="utf-8")
        h2 = file_hash(str(fp))
        assert h1 != h2

    def test_hash_differs_for_different_content(self, tmp_path: Path) -> None:
        a = tmp_path / "a.ail"
        b = tmp_path / "b.ail"
        a.write_text("fn foo() { return 0 }", encoding="utf-8")
        b.write_text("fn bar() { return 0 }", encoding="utf-8")
        assert file_hash(str(a)) != file_hash(str(b))


# =============================================================================
# File cache tests
# =============================================================================


class TestFileCache:
    def test_unknown_file_has_no_hash(self) -> None:
        cache = FileCache()
        assert cache.get_hash("no_such_file.ail") is None

    def test_has_changed_on_new_file(self, tmp_path: Path) -> None:
        fp = tmp_path / "test.ail"
        fp.write_text("fn main() { return 0 }", encoding="utf-8")
        cache = FileCache()
        h = file_hash(str(fp))
        assert cache.has_changed(str(fp), h) is True

    def test_has_changed_after_update(self, tmp_path: Path) -> None:
        fp = tmp_path / "test.ail"
        fp.write_text("fn main() { return 0 }", encoding="utf-8")
        cache = FileCache()
        h1 = file_hash(str(fp))
        cache.update(str(fp), FileCacheEntry(
            file_path=str(fp), file_hash=h1, compile_time_ms=0, ok=True,
        ))
        assert cache.has_changed(str(fp), h1) is False
        fp.write_text("fn main() { return 1 }", encoding="utf-8")
        h2 = file_hash(str(fp))
        assert cache.has_changed(str(fp), h2) is True

    def test_remove_file(self, tmp_path: Path) -> None:
        fp = tmp_path / "test.ail"
        cache = FileCache()
        h = file_hash(str(fp)) if fp.exists() else "dummy"
        cache.update(str(fp), FileCacheEntry(
            file_path=str(fp), file_hash=h, compile_time_ms=0, ok=True,
        ))
        assert cache.get_hash(str(fp)) is not None
        cache.remove(str(fp))
        assert cache.get_hash(str(fp)) is None


# =============================================================================
# Incremental compiler smoke tests
# =============================================================================


class TestIncrementalCompiler:
    """Smoke tests for IncrementalCompiler.

    These tests create small AILang repos and verify the compiler
    can do an initial build and detect file changes.
    """

    def _create_minimal_repo(self, root: Path) -> Path:
        """Create a minimal compilable AILang project."""
        stdlib = root / "stdlib"
        stdlib.mkdir(parents=True)
        (stdlib / "list.ail").write_text(
            "fn len(items) { return 0 }\nfn get(items, i) { return 0 }\n",
            encoding="utf-8",
        )
        (root / "pyproject.toml").write_text("""[project]
name = "test"
version = "0.1.0"
""")
        main = root / "main.ail"
        main.write_text("fn main() { return 0 }\n", encoding="utf-8")
        return main

    def test_initial_build_succeeds(self, tmp_path: Path) -> None:
        main = self._create_minimal_repo(tmp_path)
        ic = IncrementalCompiler(tmp_path, str(main))
        ok = ic.initial_build()
        assert ok is True

    def test_initial_build_populates_cache(self, tmp_path: Path) -> None:
        main = self._create_minimal_repo(tmp_path)
        ic = IncrementalCompiler(tmp_path, str(main))
        ic.initial_build()
        h = file_hash(str(main))
        assert ic._cache.get_hash(str(main)) == h

    def test_incremental_compile_no_change(self, tmp_path: Path) -> None:
        main = self._create_minimal_repo(tmp_path)
        ic = IncrementalCompiler(tmp_path, str(main))
        ic.initial_build()
        ok, affected, ms = ic.incremental_compile(str(main))
        assert ok is True
        assert affected == []
        assert ms == 0.0

    def test_incremental_compile_after_change(self, tmp_path: Path) -> None:
        main = self._create_minimal_repo(tmp_path)
        ic = IncrementalCompiler(tmp_path, str(main))
        ic.initial_build()
        # Change the file
        main.write_text("fn main() { let x = 10; return x }\n", encoding="utf-8")
        ok, affected, ms = ic.incremental_compile(str(main))
        assert ok is True
        assert len(affected) >= 1
        assert ms > 0.0

    def test_incremental_cache_updates(self, tmp_path: Path) -> None:
        main = self._create_minimal_repo(tmp_path)
        ic = IncrementalCompiler(tmp_path, str(main))
        ic.initial_build()
        old_hash = ic._cache.get_hash(str(main))
        main.write_text("fn main() { return 42 }\n", encoding="utf-8")
        ic.incremental_compile(str(main))
        new_hash = ic._cache.get_hash(str(main))
        assert new_hash is not None
        assert new_hash != old_hash
