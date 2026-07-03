"""Tests for module resolution in the compiler."""

from __future__ import annotations

import tempfile

import pytest

from compiler.compilation.graph import DependencyGraph, ModuleNode
from compiler.compilation.resolution import ModuleResolver


class TestModuleResolver:
    """Tests for module path to file path resolution."""

    def test_resolve_simple_module(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = __import__("pathlib").Path(tmpdir)
            module_file = tmp_path / "math.ail"
            module_file.write_text("fn add(a, b) { a + b }")

            resolver = ModuleResolver(root_dir=tmpdir)
            result = resolver.resolve(("math",))

            assert result == module_file
            assert result.exists()

    def test_resolve_nested_module(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = __import__("pathlib").Path(tmpdir)
            module_dir = tmp_path / "math"
            module_dir.mkdir()
            module_file = module_dir / "max.ail"
            module_file.write_text("fn max(a, b) { a }")

            resolver = ModuleResolver(root_dir=tmpdir)
            result = resolver.resolve(("math", "max"))

            assert result == module_file

    def test_resolve_missing_module(self) -> None:
        resolver = ModuleResolver(root_dir=".")
        with pytest.raises(Exception, match="Module not found"):
            resolver.resolve(("nonexistent",))

    def test_resolve_empty_path(self) -> None:
        resolver = ModuleResolver(root_dir=".")
        with pytest.raises(Exception, match="Empty module path"):
            resolver.resolve(())

    def test_path_traversal_detected(self) -> None:
        resolver = ModuleResolver(root_dir=".")
        with pytest.raises(Exception, match="Path traversal"):
            resolver.resolve(("..", "escape"))

    def test_hidden_module_allowed(self) -> None:
        """Hidden files (starting with .) are technically valid module names."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = __import__("pathlib").Path(tmpdir)
            module_file = tmp_path / ".hidden.ail"
            module_file.write_text("fn secret() { 42 }")

            resolver = ModuleResolver(root_dir=tmpdir)
            result = resolver.resolve((".hidden",))

            assert result == module_file


class TestDependencyGraph:
    """Tests for dependency graph construction and cycle detection."""

    def test_linear_dependency_chain(self) -> None:
        graph = DependencyGraph()
        graph.add_module("a", "a.ail")
        graph.add_module("b", "b.ail")
        graph.add_module("c", "c.ail")

        graph.add_dependency("c", "b")
        graph.add_dependency("b", "a")

        cycle = graph.detect_cycle()
        assert cycle is None

        order = graph.topological_sort()
        assert order == ["a", "b", "c"]

    def test_diamond_dependency(self) -> None:
        graph = DependencyGraph()
        graph.add_module("a", "a.ail")
        graph.add_module("b", "b.ail")
        graph.add_module("c", "c.ail")
        graph.add_module("d", "d.ail")

        # Diamond: d depends on b and c, both depend on a
        graph.add_dependency("d", "b")
        graph.add_dependency("d", "c")
        graph.add_dependency("b", "a")
        graph.add_dependency("c", "a")

        cycle = graph.detect_cycle()
        assert cycle is None

        order = graph.topological_sort()
        # a must come before b and c; b and c must come before d
        assert order.index("a") < order.index("b")
        assert order.index("a") < order.index("c")
        assert order.index("b") < order.index("d")
        assert order.index("c") < order.index("d")

    def test_circular_import_detection(self) -> None:
        graph = DependencyGraph()
        graph.add_module("a", "a.ail")
        graph.add_module("b", "b.ail")

        graph.add_dependency("a", "b")
        graph.add_dependency("b", "a")

        cycle = graph.detect_cycle()
        assert cycle is not None
        assert "a" in cycle
        assert "b" in cycle

    def test_no_dependencies(self) -> None:
        graph = DependencyGraph()
        graph.add_module("main", "main.ail")

        order = graph.topological_sort()
        assert order == ["main"]

    def test_deterministic_order(self) -> None:
        graph = DependencyGraph()
        graph.add_module("z", "z.ail")
        graph.add_module("a", "a.ail")
        graph.add_module("m", "m.ail")

        # No dependencies - preserves insertion order
        order = graph.topological_sort()
        assert order == ["z", "a", "m"]

    def test_ordered_insertion(self) -> None:
        """Pre-sorted insertion order is respected."""
        graph = DependencyGraph(insertion_order=["a", "m", "z"])

        # Simulate modules already in order
        graph._nodes["a"] = ModuleNode("a", "a.ail")
        graph._nodes["m"] = ModuleNode("m", "m.ail")
        graph._nodes["z"] = ModuleNode("z", "z.ail")
        graph._edges["a"] = set()
        graph._edges["m"] = set()
        graph._edges["z"] = set()

        # No dependencies - respects provided insertion order
        order = graph.topological_sort()
        assert order == ["a", "m", "z"]

    def test_module_node_iteration(self) -> None:
        graph = DependencyGraph()
        graph.add_module("a", "a.ail")
        graph.add_module("b", "b.ail")

        modules = list(graph)
        assert len(modules) == 2
        names = {m.name for m in modules}
        assert names == {"a", "b"}
