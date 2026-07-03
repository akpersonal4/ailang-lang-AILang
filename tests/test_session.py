"""Tests for CompilationSession multi-source foundation."""

from __future__ import annotations

import tempfile

import pytest

from compiler.compilation import CompilationSession


def _write_tmp(content: str) -> str:
    tmp = tempfile.NamedTemporaryFile(
        mode="w", suffix=".ail", delete=False, encoding="utf-8"
    )
    tmp.write(content)
    tmp.close()
    return tmp.name


class TestCompilationSession:
    def test_single_source(self):
        path = _write_tmp("let x = 5;")
        session = CompilationSession([path])
        assert session.source_count() == 1
        assert session.sources[0].text == "let x = 5;"

    def test_multiple_sources(self):
        p1 = _write_tmp("let a = 1;")
        p2 = _write_tmp("let b = 2;")
        session = CompilationSession([p1, p2])
        assert session.source_count() == 2

    def test_deterministic_order(self):
        p1 = _write_tmp("first;")
        p2 = _write_tmp("second;")
        session = CompilationSession([p1, p2])
        assert session.sources[0].text == "first;"
        assert session.sources[1].text == "second;"

    def test_duplicate_source(self):
        path = _write_tmp("data;")
        with pytest.raises(ValueError, match="Duplicate"):
            CompilationSession([path, path])

    def test_empty_compile(self):
        session = CompilationSession()
        with pytest.raises(RuntimeError, match="No source files"):
            session.compile()
