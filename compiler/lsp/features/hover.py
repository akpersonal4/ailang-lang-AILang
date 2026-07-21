"""LSP hover — show information about symbols under cursor."""

from __future__ import annotations

from typing import Any

from compiler.ast.nodes import (
    FunctionDeclarationNode,
    IdentifierNode,
    ImportDeclarationNode,
    MemberAccessNode,
    ParameterNode,
)
from compiler.lsp.protocol import Hover
from compiler.lsp.utils import (
    find_node_at_offset,
    member_access_name,
    node_range,
    position_to_offset,
    walk_ast,
)

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

    offset = position_to_offset(line, char, text)
    node = find_node_at_offset(ast, offset)
    if node is None:
        return None

    if isinstance(node, IdentifierNode):
        name = node.name
        if name == "print":
            return Hover(
                contents="`print(value, ...)` — Builtin function. Writes to stdout.",
                range=node_range(node, text),
            ).to_dict()

        if doc.symbol_table is not None:
            for scope in reversed(doc.symbol_table.scopes):
                if scope is None:
                    continue
                sym = scope.resolve(name)
                if sym is not None:
                    return Hover(
                        contents=f"**{name}**  \nVariable",
                        range=node_range(node, text),
                    ).to_dict()

        for child in walk_ast(ast):
            if isinstance(child, FunctionDeclarationNode) and child.name.name == name:
                params = ", ".join(p.name for p in child.parameters)
                return Hover(
                    contents=f"**{name}({params})**  \nFunction",
                    range=node_range(node, text),
                ).to_dict()

        return Hover(
            contents=f"Identifier: `{name}`",
            range=node_range(node, text),
        ).to_dict()

    if isinstance(node, MemberAccessNode):
        name = member_access_name(node)
        if name in _STDLIB_DOCS:
            return Hover(
                contents=_STDLIB_DOCS[name],
                range=node_range(node, text),
            ).to_dict()
        return Hover(
            contents=f"Member: `{name}`",
            range=node_range(node, text),
        ).to_dict()

    if isinstance(node, ImportDeclarationNode):
        path = ".".join(node.module_path)
        return Hover(
            contents=f"Module: `{path}`",
            range=node_range(node, text),
        ).to_dict()

    if isinstance(node, FunctionDeclarationNode):
        params = ", ".join(p.name for p in node.parameters)
        return Hover(
            contents=f"**{node.name.name}({params})**  \nFunction definition",
            range=node_range(node, text),
        ).to_dict()

    if isinstance(node, ParameterNode):
        return Hover(
            contents=f"Parameter: `{node.name}`",
            range=node_range(node, text),
        ).to_dict()

    return None
