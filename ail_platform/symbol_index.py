from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from enum import Enum, auto


class SymbolKind(Enum):
    FUNCTION = auto()
    VARIABLE = auto()
    PARAMETER = auto()
    MODULE = auto()


@dataclass
class Symbol:
    name: str
    kind: SymbolKind
    file_path: str
    line: int
    column: int


@dataclass
class SymbolIndex:
    symbols: dict[str, list[Symbol]] = field(default_factory=lambda: defaultdict(list))

    def add_symbol(self, symbol: Symbol) -> None:
        self.symbols[symbol.name].append(symbol)

    def find(self, name: str) -> list[Symbol]:
        return list(self.symbols.get(name, []))

    def find_in_file(self, name: str, file_path: str) -> list[Symbol]:
        return [s for s in self.symbols.get(name, []) if s.file_path == file_path]

    def all_symbols(self) -> list[Symbol]:
        result: list[Symbol] = []
        for syms in self.symbols.values():
            result.extend(syms)
        return result

    def clear(self) -> None:
        self.symbols.clear()


def walk_ast(node: object, callback: callable) -> None:
    """Walk AST depth-first, calling callback at each node.

    The callback receives each AST node object.
    Stops recursing if the node has no children (no __dict__ or no attrs).
    """
    callback(node)
    if hasattr(node, "__dict__"):
        for value in node.__dict__.values():
            if isinstance(value, list):
                for item in value:
                    if hasattr(item, "__dict__") or hasattr(item, "_fields"):
                        walk_ast(item, callback)
            elif hasattr(value, "__dict__") or hasattr(value, "_fields"):
                walk_ast(value, callback)


def find_node_at_offset(node: object, offset: int) -> object | None:
    """Find the deepest AST node at a given character offset.

    Searches depth-first. Returns None if no node contains the offset.
    """
    result: object | None = None

    def _search(n: object) -> None:
        nonlocal result
        start = getattr(n, "start_pos", None) or getattr(n, "start", None)
        end = getattr(n, "end_pos", None) or getattr(n, "end", None)

        if start is not None and end is not None:
            start_offset = _get_offset(start)
            end_offset = _get_offset(end)
            if start_offset is not None and end_offset is not None:
                if start_offset <= offset < end_offset:
                    result = n

        if hasattr(n, "__dict__"):
            for value in n.__dict__.values():
                if isinstance(value, list):
                    for item in value:
                        if hasattr(item, "__dict__") or hasattr(item, "_fields"):
                            _search(item)
                elif hasattr(value, "__dict__") or hasattr(value, "_fields"):
                    _search(value)

    _search(node)
    return result


def _get_offset(pos: object) -> int | None:
    """Extract an integer offset from a position object.

    Handles both int positions and objects with a .offset attribute.
    """
    if isinstance(pos, int):
        return pos
    if hasattr(pos, "offset"):
        val = getattr(pos, "offset")
        if isinstance(val, int):
            return val
    return None


def position_to_offset(text: str, line: int, column: int) -> int:
    """Convert 0-based line/column to character offset.

    line and column are 0-based. Returns offset into text.
    """
    lines = text.splitlines(keepends=True)
    offset = 0
    for i in range(line):
        if i < len(lines):
            offset += len(lines[i])
    return offset + column


def offset_to_position(text: str, offset: int) -> tuple[int, int]:
    """Convert character offset to 0-based (line, column)."""
    line_start = 0
    for line_num, line_text in enumerate(text.splitlines(keepends=True)):
        line_end = line_start + len(line_text)
        if offset < line_end:
            return line_num, offset - line_start
        line_start = line_end
    return text.count("\n"), 0
