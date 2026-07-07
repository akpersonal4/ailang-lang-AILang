"""LSP signature help — show function parameter information."""

from __future__ import annotations

from typing import Any

from compiler.ast.nodes import FunctionDeclarationNode
from compiler.lsp.protocol import (
    ParameterInformation,
    SignatureHelp,
    SignatureInformation,
)
from compiler.lsp.utils import callee_name, find_enclosing_call, position_to_offset, walk_ast

_STDLIB_SIGNATURES: dict[str, tuple[str, list[tuple[str, str]]]] = {
    "string.concat": (
        "string.concat(a, b)",
        [("a", "First string"), ("b", "Second string")],
    ),
    "string.equals": (
        "string.equals(a, b)",
        [("a", "First string"), ("b", "Second string")],
    ),
    "string.uppercase": ("string.uppercase(value)", [("value", "String to convert")]),
    "string.lowercase": ("string.lowercase(value)", [("value", "String to convert")]),
    "string.length": ("string.length(value)", [("value", "String to measure")]),
    "string.contains": (
        "string.contains(value, needle)",
        [("value", "String to search"), ("needle", "Substring to find")],
    ),
    "string.starts_with": (
        "string.starts_with(value, prefix)",
        [("value", "String to check"), ("prefix", "Prefix to find")],
    ),
    "string.ends_with": (
        "string.ends_with(value, suffix)",
        [("value", "String to check"), ("suffix", "Suffix to find")],
    ),
    "string.trim": ("string.trim(value)", [("value", "String to trim")]),
    "string.substring": (
        "string.substring(value, start, end)",
        [("value", "String"), ("start", "Start index"), ("end", "End index")],
    ),
    "math.add": ("math.add(a, b)", [("a", "First operand"), ("b", "Second operand")]),
    "math.sub": ("math.sub(a, b)", [("a", "First operand"), ("b", "Second operand")]),
    "math.mul": ("math.mul(a, b)", [("a", "First operand"), ("b", "Second operand")]),
    "math.div": ("math.div(a, b)", [("a", "Dividend"), ("b", "Divisor")]),
    "math.abs": ("math.abs(value)", [("value", "Numeric value")]),
    "math.min": ("math.min(a, b)", [("a", "First value"), ("b", "Second value")]),
    "math.max": ("math.max(a, b)", [("a", "First value"), ("b", "Second value")]),
    "list.new": ("list.new()", []),
    "list.append": (
        "list.append(list, value)",
        [("list", "Target list"), ("value", "Value to append")],
    ),
    "list.len": ("list.len(list)", [("list", "Target list")]),
    "list.get": (
        "list.get(list, index)",
        [("list", "Target list"), ("index", "Element index")],
    ),
    "list.contains": (
        "list.contains(list, value)",
        [("list", "Target list"), ("value", "Value to check")],
    ),
    "list.remove": (
        "list.remove(list, value)",
        [("list", "Target list"), ("value", "Value to remove")],
    ),
    "list.clear": ("list.clear(list)", [("list", "Target list")]),
    "map.new": ("map.new()", []),
    "map.set": (
        "map.set(map, key, value)",
        [("map", "Target map"), ("key", "Key"), ("value", "Value")],
    ),
    "map.get": ("map.get(map, key)", [("map", "Target map"), ("key", "Key")]),
    "map.has": ("map.has(map, key)", [("map", "Target map"), ("key", "Key")]),
    "map.delete": ("map.delete(map, key)", [("map", "Target map"), ("key", "Key")]),
    "map.keys": ("map.keys(map)", [("map", "Target map")]),
    "map.clear": ("map.clear(map)", [("map", "Target map")]),
    "file.exists": ("file.exists(path)", [("path", "File path")]),
    "file.read": ("file.read(path)", [("path", "File path")]),
    "file.write": (
        "file.write(path, content)",
        [("path", "File path"), ("content", "Content to write")],
    ),
    "file.append": (
        "file.append(path, content)",
        [("path", "File path"), ("content", "Content to append")],
    ),
    "file.remove": ("file.remove(path)", [("path", "File path")]),
    "json.parse": ("json.parse(text)", [("text", "JSON string to parse")]),
    "json.stringify": ("json.stringify(value)", [("value", "Value to serialize")]),
    "csv.parse": ("csv.parse(text)", [("text", "CSV string to parse")]),
    "csv.parse_header": (
        "csv.parse_header(text)",
        [("text", "CSV string with header")],
    ),
    "csv.stringify": ("csv.stringify(rows)", [("rows", "List of rows")]),
    "time.now": ("time.now()", []),
    "time.timestamp": ("time.timestamp()", []),
    "time.sleep": ("time.sleep(ms)", [("ms", "Milliseconds to sleep")]),
    "time.format": ("time.format(ts)", [("ts", "Unix timestamp")]),
    "random.int": (
        "random.int(min, max)",
        [("min", "Minimum (inclusive)"), ("max", "Maximum (inclusive)")],
    ),
    "random.float": ("random.float()", []),
    "random.choice": (
        "random.choice(collection)",
        [("collection", "List to pick from")],
    ),
    "environment.get": (
        "environment.get(name)",
        [("name", "Environment variable name")],
    ),
    "environment.cwd": ("environment.cwd()", []),
    "environment.args": ("environment.args()", []),
    "convert.to_string": ("convert.to_string(value)", [("value", "Value to convert")]),
    "convert.to_int": ("convert.to_int(value)", [("value", "String or int")]),
    "convert.to_bool": ("convert.to_bool(value)", [("value", "String to parse")]),
    "convert.to_number": ("convert.to_number(value)", [("value", "Numeric value")]),
    "io.write": ("io.write(value)", [("value", "Value to print")]),
    "io.writeln": ("io.writeln(value)", [("value", "Value to print")]),
    "io.println": ("io.println(value)", [("value", "Value to print")]),
    "system.exit": ("system.exit()", []),
}


def get_signature_help(doc: Any, position: dict[str, Any]) -> dict[str, Any] | None:
    """Get signature help for the function call at position."""
    doc.ensure_compiled()
    ast = doc.ast
    if ast is None:
        return None

    text = doc.text
    line = position["line"]
    char = position["character"]
    offset = position_to_offset(line, char, text)

    call_node = find_enclosing_call(ast, offset)
    if call_node is None:
        return None

    callee = call_node.callee
    name = callee_name(callee)
    if name is None:
        return None

    if name == "print":
        sig = SignatureInformation(
            label="print(value, ...)",
            documentation="Writes values to stdout.",
            parameters=[ParameterInformation("value", "Value to print")],
        )
        return SignatureHelp(signatures=[sig]).to_dict()

    if name in _STDLIB_SIGNATURES:
        label, params = _STDLIB_SIGNATURES[name]
        sig = SignatureInformation(
            label=label,
            parameters=[ParameterInformation(p, d) for p, d in params],
        )
        return SignatureHelp(signatures=[sig]).to_dict()

    for child in walk_ast(ast):
        if isinstance(child, FunctionDeclarationNode) and child.name.name == name:
            pnames = [p.name for p in child.parameters]
            param_infos = [
                ParameterInformation(p, f"Parameter {i}") for i, p in enumerate(pnames)
            ]
            sig = SignatureInformation(
                label=f"{name}({', '.join(pnames)})",
                parameters=param_infos,
            )
            return SignatureHelp(signatures=[sig]).to_dict()

    return None
