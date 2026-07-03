"""Compilation session orchestrating multi-source compilation."""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from compiler.source import Source


class CompilationSession:
    """Manages multiple source files as a single compilation unit.

    Accepts a list of file paths and provides access to their Source objects.
    All sources are compiled deterministically in registration order.
    No import resolution or module graph is performed.
    """

    def __init__(self, paths: Sequence[str | Path] | None = None) -> None:
        self._sources: list[Source] = []
        self._file_set: set[Path] = set()
        if paths is not None:
            for p in paths:
                self.add_source(p)

    @property
    def sources(self) -> list[Source]:
        return list(self._sources)

    def add_source(self, path: str | Path) -> Source:
        file_path = Path(path).resolve()
        if file_path in self._file_set:
            raise ValueError(f"Duplicate source file: {file_path}")
        source = Source.from_file(str(file_path))
        self._sources.append(source)
        self._file_set.add(file_path)
        return source

    def source_count(self) -> int:
        return len(self._sources)

    def compile(self) -> None:
        """Run full compilation pipeline on all registered sources.

        For now this is a stub that loads each source and associates
        it with the session. Real pipeline phases will be added later.
        """
        if not self._sources:
            raise RuntimeError("No source files registered for compilation")
