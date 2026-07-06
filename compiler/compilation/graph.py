"""Dependency graph for module resolution.

Builds a directed acyclic graph of module dependencies and provides
topological sorting for deterministic compilation order.
"""

from __future__ import annotations

from collections.abc import Iterator, Sequence
from dataclasses import dataclass


@dataclass(frozen=True)
class ModuleNode:
    """Represents a module in the dependency graph."""

    name: str
    file_path: str


class DependencyGraph:
    """Directed acyclic graph of module dependencies."""

    def __init__(self, insertion_order: Sequence[str] | None = None) -> None:
        self._nodes: dict[str, ModuleNode] = {}
        self._edges: dict[str, set[str]] = {}  # module -> set of dependencies
        self._insertion_order: list[str] = []
        if insertion_order is not None:
            # Pre-populate insertion order
            self._insertion_order = list(insertion_order)

    def add_module(self, name: str, file_path: str) -> None:
        """Add a module to the graph."""
        if name not in self._nodes:
            self._nodes[name] = ModuleNode(name, file_path)
            self._edges[name] = set()
            if name not in self._insertion_order:
                self._insertion_order.append(name)

    def add_dependency(self, module: str, dependency: str) -> None:
        """Add a dependency edge from module to dependency."""
        if module not in self._edges:
            self._edges[module] = set()
        self._edges[module].add(dependency)

    def detect_cycle(self) -> tuple[str, ...] | None:
        """Detect if there's a circular import.

        Returns:
            Tuple representing the cycle path if found, None otherwise
        """
        visited: set[str] = set()
        rec_stack: set[str] = set()
        path: list[str] = []

        def visit(node: str) -> tuple[str, ...] | None:
            visited.add(node)
            rec_stack.add(node)
            path.append(node)

            for dep in self._edges.get(node, set()):
                if dep not in visited:
                    cycle = visit(dep)
                    if cycle is not None:
                        return cycle
                elif dep in rec_stack:
                    # Found cycle - extract the path
                    cycle_start = path.index(dep)
                    return tuple(path[cycle_start:] + [dep])

            path.pop()
            rec_stack.remove(node)
            return None

        for node in self._nodes:
            if node not in visited:
                cycle = visit(node)
                if cycle is not None:
                    return cycle

        return None

    def topological_sort(self) -> list[str]:
        """Return modules in compilation order (dependencies first).

        Uses insertion order for deterministic tie-breaking when
        multiple modules have no dependencies.

        Returns:
            List of module names in topological order
        """
        in_degree: dict[str, int] = {name: 0 for name in self._nodes}

        # Calculate in-degrees
        for module in self._edges:
            for dep in self._edges[module]:
                if dep in in_degree:
                    in_degree[module] += 1

        # Start with modules that have no dependencies, respecting insertion order
        queue = [m for m in self._insertion_order if in_degree[m] == 0]
        result: list[str] = []

        while queue:
            node = queue.pop(0)
            result.append(node)

            # Reduce in-degree for dependents
            for module, deps in self._edges.items():
                if node in deps:
                    in_degree[module] -= 1
                    if in_degree[module] == 0 and module not in result:
                        # Insert in insertion-order position for determinism
                        idx = 0
                        while idx < len(queue) and self._insertion_order.index(
                            queue[idx]
                        ) < self._insertion_order.index(module):
                            idx += 1
                        queue.insert(idx, module)

        return result

    def get_dependencies(self, module: str) -> set[str]:
        """Get all direct dependencies of a module."""
        return self._edges.get(module, set())

    def topological_order(self) -> list[str]:
        """Return modules in compilation order."""
        return self.topological_sort()

    def __iter__(self) -> Iterator[ModuleNode]:
        return iter(self._nodes.values())
