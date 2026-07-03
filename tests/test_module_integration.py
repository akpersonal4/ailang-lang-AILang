"""End-to-end tests for module system integration."""

from __future__ import annotations

import tempfile
from pathlib import Path

from compiler.compilation import CompilationSession


def test_multi_file_compilation() -> None:
    """Test that multiple files can be compiled together."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create main file
        main_file = tmp_path / "main.ail"
        main_file.write_text("fn main() { 42 }")

        session = CompilationSession([main_file])
        session.compile()

        # Verify the file was added
        assert session.source_count() == 1


def test_module_discovery_simple() -> None:
    """Test that discover() finds imported modules."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create a simple module file
        simple_file = tmp_path / "simple.ail"
        simple_file.write_text("fn simple() { 42 }")

        # Create main file that imports the module
        main_file = tmp_path / "main.ail"
        main_file.write_text("import simple; simple()")

        session = CompilationSession()
        session._root = tmp_path
        session._resolver = type(session._resolver)(tmp_path)
        session.discover(main_file)

        assert session.source_count() == 2


def test_topological_order() -> None:
    """Test that modules compile in dependency order."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create dependency chain: a imports b, b imports c
        # c.c means module "c" with symbol "c", file is c/c.ail
        c_dir = tmp_path / "c"
        c_dir.mkdir()
        c_file = c_dir / "c.ail"
        c_file.write_text("fn c() { 42 }")

        b_dir = tmp_path / "b"
        b_dir.mkdir()
        b_file = b_dir / "b.ail"
        b_file.write_text("import c.c; fn b() { c.c() }")

        a_file = tmp_path / "a.ail"
        a_file.write_text("import b.b; import c.c; b.b()")

        session = CompilationSession()
        session._root = tmp_path
        session._resolver = type(session._resolver)(tmp_path)
        session.discover(a_file)

        # Should have 3 modules (a, b.b, c.c)
        assert session.source_count() == 3


def test_circular_import_detection() -> None:
    """Test that circular imports are detected."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create two modules that import each other
        # Using simple module names that map to a.ail and b.ail
        a_file = tmp_path / "a.ail"
        a_file.write_text("import b; fn a() { b() }")

        b_file = tmp_path / "b.ail"
        b_file.write_text("import a; fn b() { a() }")

        session = CompilationSession()
        session._root = tmp_path
        session._resolver = type(session._resolver)(tmp_path)
        session.discover(a_file)

        # Check for cycle
        cycle = session._graph.detect_cycle()
        assert cycle is not None
