"""LSP completion — provide auto-completion suggestions."""

from __future__ import annotations

from collections.abc import Generator
from typing import Any

from compiler.ast.nodes import FunctionDeclarationNode, ProgramNode
from compiler.lsp.protocol import CompletionItem

_KEYWORDS: list[CompletionItem] = [
    CompletionItem("fn", kind=1, detail="Keyword", insert_text="fn "),
    CompletionItem("let", kind=1, detail="Keyword", insert_text="let "),
    CompletionItem("if", kind=1, detail="Keyword", insert_text="if () {\n    \n}"),
    CompletionItem("else", kind=1, detail="Keyword", insert_text="else {\n    \n}"),
    CompletionItem("return", kind=1, detail="Keyword", insert_text="return "),
    CompletionItem("import", kind=1, detail="Keyword", insert_text="import "),
    CompletionItem("for", kind=1, detail="Keyword (experimental)", insert_text="for item in collection {\n    \n}"),
    CompletionItem("true", kind=21, detail="Boolean literal", insert_text="true"),
    CompletionItem("false", kind=21, detail="Boolean literal", insert_text="false"),
]

_BUILTINS: list[CompletionItem] = [
    CompletionItem("print", kind=14, detail="Builtin function", insert_text="print()"),
]

_STDLIB_MODULES: list[CompletionItem] = [
    CompletionItem(
        "string", kind=9, detail="String manipulation module", insert_text="string"
    ),
    CompletionItem("math", kind=9, detail="Arithmetic module", insert_text="math"),
    CompletionItem("list", kind=9, detail="List collection module", insert_text="list"),
    CompletionItem(
        "array", kind=9, detail="Array collection module", insert_text="array"
    ),
    CompletionItem("map", kind=9, detail="Map dictionary module", insert_text="map"),
    CompletionItem("set", kind=9, detail="Set collection module", insert_text="set"),
    CompletionItem("file", kind=9, detail="File I/O module", insert_text="file"),
    CompletionItem(
        "path", kind=9, detail="Path manipulation module", insert_text="path"
    ),
    CompletionItem(
        "json", kind=9, detail="JSON parse/stringify module", insert_text="json"
    ),
    CompletionItem(
        "csv", kind=9, detail="CSV parse/stringify module", insert_text="csv"
    ),
    CompletionItem("time", kind=9, detail="Time utilities module", insert_text="time"),
    CompletionItem(
        "random", kind=9, detail="Random generation module", insert_text="random"
    ),
    CompletionItem(
        "environment",
        kind=9,
        detail="Environment access module",
        insert_text="environment",
    ),
    CompletionItem(
        "convert", kind=9, detail="Type conversion module", insert_text="convert"
    ),
    CompletionItem("io", kind=9, detail="I/O helpers module", insert_text="io"),
    CompletionItem(
        "system", kind=9, detail="System operations module", insert_text="system"
    ),
]

_STDLIB_FUNCTIONS: list[CompletionItem] = [
    CompletionItem("string.concat", kind=6, detail="string.concat(a, b)"),
    CompletionItem("string.equals", kind=6, detail="string.equals(a, b)"),
    CompletionItem("string.uppercase", kind=6, detail="string.uppercase(value)"),
    CompletionItem("string.lowercase", kind=6, detail="string.lowercase(value)"),
    CompletionItem("string.length", kind=6, detail="string.length(value)"),
    CompletionItem("string.contains", kind=6, detail="string.contains(value, needle)"),
    CompletionItem(
        "string.starts_with", kind=6, detail="string.starts_with(value, prefix)"
    ),
    CompletionItem(
        "string.ends_with", kind=6, detail="string.ends_with(value, suffix)"
    ),
    CompletionItem("string.trim", kind=6, detail="string.trim(value)"),
    CompletionItem(
        "string.substring", kind=6, detail="string.substring(value, start, end)"
    ),
    CompletionItem("math.add", kind=6, detail="math.add(a, b)"),
    CompletionItem("math.sub", kind=6, detail="math.sub(a, b)"),
    CompletionItem("math.mul", kind=6, detail="math.mul(a, b)"),
    CompletionItem("math.div", kind=6, detail="math.div(a, b)"),
    CompletionItem("math.abs", kind=6, detail="math.abs(value)"),
    CompletionItem("math.min", kind=6, detail="math.min(a, b)"),
    CompletionItem("math.max", kind=6, detail="math.max(a, b)"),
    CompletionItem("list.new", kind=6, detail="list.new()"),
    CompletionItem("list.append", kind=6, detail="list.append(list, value)"),
    CompletionItem("list.len", kind=6, detail="list.len(list)"),
    CompletionItem("list.get", kind=6, detail="list.get(list, index)"),
    CompletionItem("list.contains", kind=6, detail="list.contains(list, value)"),
    CompletionItem("list.remove", kind=6, detail="list.remove(list, value)"),
    CompletionItem("list.clear", kind=6, detail="list.clear(list)"),
    CompletionItem("map.new", kind=6, detail="map.new()"),
    CompletionItem("map.set", kind=6, detail="map.set(map, key, value)"),
    CompletionItem("map.get", kind=6, detail="map.get(map, key)"),
    CompletionItem("map.has", kind=6, detail="map.has(map, key)"),
    CompletionItem("map.delete", kind=6, detail="map.delete(map, key)"),
    CompletionItem("map.keys", kind=6, detail="map.keys(map)"),
    CompletionItem("map.clear", kind=6, detail="map.clear(map)"),
    CompletionItem("set.new", kind=6, detail="set.new()"),
    CompletionItem("set.add", kind=6, detail="set.add(set, value)"),
    CompletionItem("set.contains", kind=6, detail="set.contains(set, value)"),
    CompletionItem("set.len", kind=6, detail="set.len(set)"),
    CompletionItem("set.remove", kind=6, detail="set.remove(set, value)"),
    CompletionItem("set.clear", kind=6, detail="set.clear(set)"),
    CompletionItem("file.exists", kind=6, detail="file.exists(path)"),
    CompletionItem("file.read", kind=6, detail="file.read(path)"),
    CompletionItem("file.write", kind=6, detail="file.write(path, content)"),
    CompletionItem("file.append", kind=6, detail="file.append(path, content)"),
    CompletionItem("file.remove", kind=6, detail="file.remove(path)"),
    CompletionItem("path.join", kind=6, detail="path.join(a, b)"),
    CompletionItem("path.basename", kind=6, detail="path.basename(path)"),
    CompletionItem("path.dirname", kind=6, detail="path.dirname(path)"),
    CompletionItem("path.extension", kind=6, detail="path.extension(path)"),
    CompletionItem("path.normalize", kind=6, detail="path.normalize(path)"),
    CompletionItem("json.parse", kind=6, detail="json.parse(text)"),
    CompletionItem("json.stringify", kind=6, detail="json.stringify(value)"),
    CompletionItem("csv.parse", kind=6, detail="csv.parse(text)"),
    CompletionItem("csv.parse_header", kind=6, detail="csv.parse_header(text)"),
    CompletionItem("csv.stringify", kind=6, detail="csv.stringify(rows)"),
    CompletionItem("time.now", kind=6, detail="time.now()"),
    CompletionItem("time.timestamp", kind=6, detail="time.timestamp()"),
    CompletionItem("time.sleep", kind=6, detail="time.sleep(ms)"),
    CompletionItem("time.format", kind=6, detail="time.format(ts)"),
    CompletionItem("random.int", kind=6, detail="random.int(min, max)"),
    CompletionItem("random.float", kind=6, detail="random.float()"),
    CompletionItem("random.choice", kind=6, detail="random.choice(collection)"),
    CompletionItem("environment.get", kind=6, detail="environment.get(name)"),
    CompletionItem("environment.cwd", kind=6, detail="environment.cwd()"),
    CompletionItem("environment.args", kind=6, detail="environment.args()"),
    CompletionItem("convert.to_string", kind=6, detail="convert.to_string(value)"),
    CompletionItem("convert.to_int", kind=6, detail="convert.to_int(value)"),
    CompletionItem("convert.to_bool", kind=6, detail="convert.to_bool(value)"),
    CompletionItem("convert.to_number", kind=6, detail="convert.to_number(value)"),
    CompletionItem("io.write", kind=6, detail="io.write(value)"),
    CompletionItem("io.writeln", kind=6, detail="io.writeln(value)"),
    CompletionItem("io.println", kind=6, detail="io.println(value)"),
    CompletionItem("system.exit", kind=6, detail="system.exit()"),
]


def get_completions(doc: Any, position: dict[str, Any]) -> list[dict[str, Any]]:
    """Get completion items at a given position."""
    doc.ensure_compiled()
    result: list[CompletionItem] = []

    result.extend(_KEYWORDS)
    result.extend(_BUILTINS)
    result.extend(_STDLIB_MODULES)
    result.extend(_STDLIB_FUNCTIONS)

    # Add user-defined functions from the AST
    if doc.ast is not None:
        for node in _iter_functions(doc.ast):
            params = ", ".join(p.name for p in node.parameters)
            result.append(
                CompletionItem(
                    node.name.name,
                    kind=14,
                    detail=f"Function: {node.name.name}({params})",
                    insert_text=f"{node.name.name}()",
                )
            )

    return [item.to_dict() for item in result]


def _iter_functions(node: Any) -> Generator[FunctionDeclarationNode, None, None]:
    """Yield all FunctionDeclarationNode instances from the AST."""
    if node is None:
        return

    if isinstance(node, ProgramNode):
        for child in node.children:
            if isinstance(child, FunctionDeclarationNode):
                yield child
