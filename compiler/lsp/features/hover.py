"""LSP hover — show information about symbols under cursor."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from compiler.ast.nodes import (
    FunctionDeclarationNode,
    IdentifierNode,
    ImportDeclarationNode,
    MemberAccessNode,
    ParameterNode,
)
from compiler.lsp.protocol import Hover, offset_to_position

_STDLIB_DOCS: dict[str, str] = {
    "string.concat": "`string.concat(a, b)` — Concatenates two strings.",
    "string.equals": "`string.equals(a, b)` — Checks string equality.",
    "string.uppercase": "`string.uppercase(value)` — Converts to uppercase.",
    "string.lowercase": "`string.lowercase(value)` — Converts to lowercase.",
    "string.length": "`string.length(value)` — Returns character count.",
    "string.contains": "`string.contains(value, needle)` — Checks substring.",
    "string.starts_with": "`string.starts_with(value, prefix)` — Checks prefix.",
    "string.ends_with": "`string.ends_with(value, suffix)` — Checks suffix.",
    "string.trim": "`string.trim(value)` — Removes leading/trailing whitespace.",
    "string.substring": "`string.substring(value, start, end)` — Extracts substring.",
    "math.add": "`math.add(a, b)` — Addition.",
    "math.sub": "`math.sub(a, b)` — Subtraction.",
    "math.mul": "`math.mul(a, b)` — Multiplication.",
    "math.div": "`math.div(a, b)` — Division.",
    "math.abs": "`math.abs(value)` — Absolute value.",
    "math.min": "`math.min(a, b)` — Minimum of two values.",
    "math.max": "`math.max(a, b)` — Maximum of two values.",
    "list.new": "`list.new()` — Creates a new empty list.",
    "list.append": "`list.append(list, value)` — Appends a value.",
    "list.len": "`list.len(list)` — Returns element count.",
    "list.get": "`list.get(list, index)` — Gets element at index.",
    "list.contains": "`list.contains(list, value)` — Checks containment.",
    "list.remove": "`list.remove(list, value)` — Removes first occurrence.",
    "list.clear": "`list.clear(list)` — Removes all elements.",
    "map.new": "`map.new()` — Creates a new empty map.",
    "map.set": "`map.set(map, key, value)` — Sets a key-value pair.",
    "map.get": "`map.get(map, key)` — Gets value by key (raises if missing).",
    "map.has": "`map.has(map, key)` — Checks key existence.",
    "map.delete": "`map.delete(map, key)` — Removes a key.",
    "map.keys": "`map.keys(map)` — Returns list of keys.",
    "map.clear": "`map.clear(map)` — Removes all entries.",
    "set.new": "`set.new()` — Creates a new empty set.",
    "set.add": "`set.add(set, value)` — Adds a value.",
    "set.contains": "`set.contains(set, value)` — Checks membership.",
    "set.len": "`set.len(set)` — Returns element count.",
    "set.remove": "`set.remove(set, value)` — Removes a value.",
    "set.clear": "`set.clear(set)` — Removes all elements.",
    "file.exists": "`file.exists(path)` — Checks if file exists.",
    "file.read": "`file.read(path)` — Reads entire file as string.",
    "file.write": "`file.write(path, content)` — Writes to file.",
    "file.append": "`file.append(path, content)` — Appends to file.",
    "file.remove": "`file.remove(path)` — Deletes a file.",
    "path.join": "`path.join(a, b)` — Joins path components.",
    "path.basename": "`path.basename(path)` — Returns file name.",
    "path.dirname": "`path.dirname(path)` — Returns directory portion.",
    "path.extension": "`path.extension(path)` — Returns file extension.",
    "path.normalize": "`path.normalize(path)` — Normalizes path.",
    "json.parse": "`json.parse(text)` — Parses JSON string.",
    "json.stringify": "`json.stringify(value)` — Serializes to JSON.",
    "csv.parse": "`csv.parse(text)` — Parses CSV text.",
    "csv.parse_header": "`csv.parse_header(text)` — Parses CSV with header.",
    "csv.stringify": "`csv.stringify(rows)` — Serializes to CSV.",
    "time.now": "`time.now()` — Current date/time as string.",
    "time.timestamp": "`time.timestamp()` — Unix timestamp (seconds).",
    "time.sleep": "`time.sleep(ms)` — Sleeps for milliseconds.",
    "time.format": "`time.format(ts)` — Formats timestamp to string.",
    "random.int": "`random.int(min, max)` — Random integer in range.",
    "random.float": "`random.float()` — Random float in [0.0, 1.0).",
    "random.choice": "`random.choice(collection)` — Random element.",
    "environment.get": "`environment.get(name)` — Gets env var value.",
    "environment.cwd": "`environment.cwd()` — Current working directory.",
    "environment.args": "`environment.args()` — Command-line arguments.",
    "convert.to_string": "`convert.to_string(value)` — Converts to string.",
    "convert.to_int": "`convert.to_int(value)` — Converts to integer.",
    "convert.to_bool": "`convert.to_bool(value)` — Converts to boolean.",
    "convert.to_number": "`convert.to_number(value)` — Identity for numbers.",
    "io.write": "`io.write(value)` — Prints to stdout (no newline).",
    "io.writeln": "`io.writeln(value)` — Prints with newline.",
    "io.println": "`io.println(value)` — Prints with newline.",
    "system.exit": "`system.exit()` — Exits the process.",
}


def get_hover(doc: Any, position: dict[str, Any]) -> dict[str, Any] | None:
    """Get hover information at a given position."""
    doc.ensure_compiled()
    ast = doc.ast
    if ast is None:
        return None

    text = doc.text
    line = position["line"]
    char = position["character"]

    # Convert LSP position to offset
    offset = _position_to_offset(line, char, text)

    # Find the identifier under the cursor
    node = _find_node_at_offset(ast, offset)
    if node is None:
        return None

    # Determine hover content based on node type
    if isinstance(node, IdentifierNode):
        name = node.name
        # Check if it's a known builtin
        if name == "print":
            return Hover(
                contents="`print(value, ...)` — Builtin function. Writes to stdout.",
                range=_node_range(node, text),
            ).to_dict()

        # Check symbol table
        if doc.symbol_table is not None:
            for scope in reversed(doc.symbol_table.scopes):
                if scope is None:
                    continue
                sym = scope.resolve(name)
                if sym is not None:
                    return Hover(
                        contents=f"**{name}**  \nVariable",
                        range=_node_range(node, text),
                    ).to_dict()

        # Check if it's a known function by looking at the AST
        for child in _walk_ast(ast):
            if isinstance(child, FunctionDeclarationNode) and child.name.name == name:
                params = ", ".join(p.name for p in child.parameters)
                return Hover(
                    contents=f"**{name}({params})**  \nFunction",
                    range=_node_range(node, text),
                ).to_dict()

        return Hover(
            contents=f"Identifier: `{name}`",
            range=_node_range(node, text),
        ).to_dict()

    if isinstance(node, MemberAccessNode):
        name = _member_access_name(node)
        if name in _STDLIB_DOCS:
            return Hover(
                contents=_STDLIB_DOCS[name],
                range=_node_range(node, text),
            ).to_dict()
        return Hover(
            contents=f"Member: `{name}`",
            range=_node_range(node, text),
        ).to_dict()

    if isinstance(node, ImportDeclarationNode):
        path = ".".join(node.module_path)
        return Hover(
            contents=f"Module: `{path}`",
            range=_node_range(node, text),
        ).to_dict()

    if isinstance(node, FunctionDeclarationNode):
        params = ", ".join(p.name for p in node.parameters)
        return Hover(
            contents=f"**{node.name.name}({params})**  \nFunction definition",
            range=_node_range(node, text),
        ).to_dict()

    if isinstance(node, ParameterNode):
        return Hover(
            contents=f"Parameter: `{node.name}`",
            range=_node_range(node, text),
        ).to_dict()

    return None


def _position_to_offset(line: int, character: int, text: str) -> int:
    """Convert LSP 0-based position to source offset."""
    current_line = 0
    for i, ch in enumerate(text):
        if current_line == line:
            return i + character
        if ch == "\n":
            current_line += 1
    return len(text)


def _find_node_at_offset(node: Any, offset: int) -> Any | None:
    """Walk AST and find the deepest node containing the offset."""
    best = None

    for child in _walk_ast(node):
        if child is None:
            continue
        start = getattr(child, "start_span", None)
        end = getattr(child, "end_span", None)
        if start is not None and end is not None and start <= offset < end:
            best = child

    return best


def _walk_ast(node: Any) -> Generator[Any, None, None]:
    """Yield all nodes in the AST tree."""
    if node is None:
        return
    yield node
    if isinstance(node, (list, tuple)):
        for item in node:
            yield from _walk_ast(item)
    elif hasattr(node, "__dataclass_fields__"):
        for field_name in node.__dataclass_fields__:
            val = getattr(node, field_name)
            if isinstance(val, (list, tuple)):
                for item in val:
                    yield from _walk_ast(item)
            elif hasattr(val, "__dataclass_fields__"):
                yield from _walk_ast(val)


def _node_range(node: Any, text: str) -> Any:
    """Create an LSP Range from a node's source spans."""
    from compiler.lsp.protocol import Range as LspRange

    start = getattr(node, "start_span", None)
    end = getattr(node, "end_span", None)
    if start is None or end is None:
        return None
    return LspRange(
        start=offset_to_position(start, text),
        end=offset_to_position(end, text),
    )


def _member_access_name(node: MemberAccessNode) -> str:
    """Get the qualified name of a member access expression."""
    parts: list[str] = []
    current: Any = node
    while isinstance(current, MemberAccessNode):
        parts.append(current.member.name)
        current = current.receiver
    if isinstance(current, IdentifierNode):
        parts.append(current.name)
    return ".".join(reversed(parts))
