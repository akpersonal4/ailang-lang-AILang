# Standard Library v1.0 — Final Module Specifications

## Status: Design Proposal — Ready for Review

## 1. Overview

This document specifies the final four modules for AILang Standard Library v1.0:

| Module | Priority | Rationale |
|--------|----------|-----------|
| `json` | v1.0 (this sprint) | Universal data-interchange format; foundational for AI/data workflows |
| `csv` | v1.0 (this sprint) | Ubiquitous tabular data format; complements file and string modules |
| `ini` | v1.1 (deferred) | Low demand; partially handled by existing `configparser` examples |
| `toml` | v1.1 (deferred) | Full round-trip complex; read-only subset possible later |
| `xml` | v1.1 (deferred) | Verbose API; lowest priority for AI-first language |

**Deferral justification (INI, TOML, XML):**

- **INI**: Python's `configparser` provides no `dumps`/`loads` parity; the format has no standard quoting or type system. Users who need INI can parse it manually with `string` and `file` modules.
- **TOML**: Valuable for config files (pyproject.toml), but full round-trip requires preserving inline-table vs. standard-table distinctions, comments, and ordering. A read-only `toml.parse()` could be added in v1.1 without breaking changes.
- **XML**: Large API surface (`ElementTree`, XPath, namespaces) with little AI/data use-case overlap. Deferring avoids committing to a complex interface before user demand materializes.

---

## 2. JSON Module (`stdlib/json.ail`)

### 2.1 Module Overview

Provides JSON serialization and deserialization using Python's `json` standard library.

### 2.2 API Specification

```ail
import json;

// Parse a JSON string into an AILang value.
// Returns: int, float, str, bool, null (None), list, or map
fn parse(text) -> json_parse(text)

// Serialize an AILang value to a JSON string.
// Accepts: int, float, str, bool, null, list, map, set
// Raises: error for unsupported types (function references, etc.)
fn stringify(value) -> json_stringify(value)
```

### 2.3 Type Mapping

| JSON type | AILang type | Python type |
|-----------|-------------|-------------|
| `null` | `None` (no literal) | `None` |
| `true` / `false` | `true` / `false` | `bool` |
| number (integer) | `int` | `int` |
| number (float) | `float` | `float` |
| string | `str` | `str` |
| array | `list` | `list` |
| object | `map` | `dict` |

### 2.4 Error Handling

| Condition | Behavior |
|-----------|----------|
| `parse("")` | Raises `json.JSONDecodeError` via Python |
| `parse("invalid")` | Raises `json.JSONDecodeError` with position info |
| `parse("null")` | Returns `None` (Python `None`) |
| `parse("[1,2,]")` | Raises `json.JSONDecodeError` (trailing comma not allowed) |
| `stringify(fn_ref)` | Raises `TypeError` via Python |
| `stringify(set)` | Set converted to list automatically (custom encoder) |

### 2.5 Builtins Required (in `compiler/runtime/builtins.py`)

```python
import json as _json

def json_parse(args: tuple[RuntimeValue, ...]) -> RuntimeValue:
    """Parse JSON string → AILang value."""
    return _json.loads(str(args[0]))

class _SetEncoder(_json.JSONEncoder):
    def default(self, obj: object) -> object:
        if isinstance(obj, set):
            return list(obj)
        return super().default(obj)

def json_stringify(args: tuple[RuntimeValue, ...]) -> str:
    """Serialize AILang value → JSON string. Sets become arrays."""
    return _json.dumps(args[0], cls=_SetEncoder)
```

Registration in `BUILTINS`:
```python
"json_parse": json_parse,
"json_stringify": json_stringify,
```

### 2.6 AILang Wrapper (`stdlib/json.ail`)

```ail
fn parse(text) {
    return json_parse(text)
}

fn stringify(value) {
    return json_stringify(value)
}
```

### 2.7 Example Program (`examples/json_demo.ail`)

```ail
import json;
import list;
import map;

fn main() {
    print("=== JSON Demo ===");

    // Parse a JSON object
    let raw = "{\"name\": \"Alice\", \"age\": 30, \"active\": true}";
    let data = json.parse(raw);

    print("Parsed JSON object:");
    print("Name: " + map.get(data, "name"));
    print("Age: " + map.get(data, "age"));
    print("Active: " + map.get(data, "active"));

    // Parse a JSON array
    let items = json.parse("[10, 20, 30]");
    print("First item: " + list.get(items, 0));

    // Stringify a value
    let person = map.new();
    map.set(person, "name", "Bob");
    map.set(person, "age", 25);
    let output = json.stringify(person);
    print("Stringified: " + output);

    // Null handling
    let empty = json.parse("null");
    print("Null value:");
    print(empty);
}
```

Note: String concatenation with non-string values (e.g., `"Age: " + map.get(data, "age")`) requires the result to be a string. The `stringify` output is always a string. For display purposes, the demo either uses `stringify` directly or relies on the `print` builtin's per-argument `str()` conversion by passing values as separate arguments (e.g., `print("Age:"); print(map.get(data, "age"));`). The example above uses the latter pattern for reliability.

### 2.8 Required Tests (`tests/test_stdlib_json.py`)

| Test | Description |
|------|-------------|
| `test_json_parse_string` | Parse `"\"hello\""` → str `"hello"` |
| `test_json_parse_number` | Parse `"42"` → int `42` |
| `test_json_parse_float` | Parse `"3.14"` → float `3.14` |
| `test_json_parse_boolean` | Parse `"true"` → True, `"false"` → False |
| `test_json_parse_null` | Parse `"null"` → None |
| `test_json_parse_array` | Parse `"[1,2,3]"` → list `[1,2,3]` |
| `test_json_parse_object` | Parse `'{"a":1}'` → dict `{"a": 1}` |
| `test_json_parse_nested` | Parse nested object/array |
| `test_json_parse_invalid` | Raises error on invalid JSON |
| `test_json_stringify_int` | Stringify int → `"42"` |
| `test_json_stringify_string` | Stringify str → `'"hello"'` |
| `test_json_stringify_list` | Stringify list → `"[1,2,3]"` |
| `test_json_stringify_map` | Stringify dict → `'{"a":1}'` |
| `test_json_stringify_set` | Stringify set → `"[...]"` (converted to array) |
| `test_json_roundtrip` | Parse then stringify yields equivalent value |

### 2.9 Known Limitations

- No `json.pretty()` or custom indentation in v1.0 (can be added as `json.stringify_pretty(value, indent)` later)
- No streaming parse (JSON Lines support) — defer to v1.1 as `json.parse_lines(text)` → list
- Sets are serialized as arrays (ordering is not guaranteed by Python's `set`)
- Parsed `null` returns Python `None`, which has **no literal syntax in AILang**. Users cannot write `v == None` directly. Detection workaround: `json.stringify(v) == "null"` or check for absence of expected keys in objects. A `nil`/`null` language literal is tracked as a future enhancement.

---

## 3. CSV Module (`stdlib/csv.ail`)

### 3.1 Module Overview

Provides CSV parsing and serialization using Python's `csv` standard library. Since AILang has no loop constructs, the module returns structured data (list of lists or list of maps) that users can access indexically.

### 3.2 API Specification

```ail
import csv;

// Parse CSV text into a list of rows, where each row is a list of strings.
fn parse(text) -> csv_parse(text)

// Parse CSV text with header row. Returns list of maps keyed by header names.
fn parse_header(text) -> csv_parse_header(text)

// Serialize a list of rows (each row a list of strings) back to CSV text.
fn stringify(rows) -> csv_stringify(rows)
```

### 3.3 Data Model

```
csv.parse("a,b,c\n1,2,3") →
  [
    ["a", "b", "c"],    // row 0
    ["1", "2", "3"]     // row 1
  ]

csv.parse_header("name,age\nAlice,30\nBob,25") →
  [
    {"name": "Alice", "age": "30"},   // row 0
    {"name": "Bob", "age": "25"}      // row 1
  ]

csv.stringify([["a","b"],["1","2"]]) →
  "a,b\r\n1,2\r\n"
```

### 3.4 Error Handling

| Condition | Behavior |
|-----------|----------|
| `parse("")` | Returns `[]` (empty list — no data rows) |
| `parse("a,b")` | Returns `[["a", "b"]]` |
| `parse_header("")` | Returns `[]` (empty list) |
| `parse_header("a,b")` | Returns `[]` (header row only, no data rows → empty result) |
| Malformed CSV (unclosed quote) | Raises Python `csv.Error` |
| `stringify([])` | Returns `""` (empty string) |

### 3.5 Builtins Required (in `compiler/runtime/builtins.py`)

```python
import csv as _csv
import io as _io

def csv_parse(args: tuple[RuntimeValue, ...]) -> list[list[str]]:
    """Parse CSV text → list of rows (each row a list of strings)."""
    return [list(row) for row in _csv.reader(_io.StringIO(str(args[0])))]


def csv_parse_header(args: tuple[RuntimeValue, ...]) -> list[dict[str, str]]:
    """Parse CSV text with header → list of dicts keyed by column name."""
    return [dict(row) for row in _csv.DictReader(_io.StringIO(str(args[0])))]


def csv_stringify(args: tuple[RuntimeValue, ...]) -> str:
    """Serialize rows (list of lists) → CSV string."""
    output = _io.StringIO()
    writer = _csv.writer(output, lineterminator="\n")
    writer.writerows(args[0])
    return output.getvalue()
```

Registration in `BUILTINS`:
```python
"csv_parse": csv_parse,
"csv_parse_header": csv_parse_header,
"csv_stringify": csv_stringify,
```

### 3.6 AILang Wrapper (`stdlib/csv.ail`)

```ail
fn parse(text) {
    return csv_parse(text)
}

fn parse_header(text) {
    return csv_parse_header(text)
}

fn stringify(rows) {
    return csv_stringify(rows)
}
```

### 3.7 Example Program (`examples/csv_demo.ail`)

```ail
import csv;
import list;
import map;
import file;

fn read_and_parse(filepath) {
    let content = file.read(filepath);
    return csv.parse_header(content);
}

fn main() {
    print("=== CSV Demo ===");

    // Parse inline CSV
    let raw = "name,age,role\nAlice,30,Engineer\nBob,25,Designer";
    let rows = csv.parse_header(raw);

    print("Header parse:");
    let first = list.get(rows, 0);
    print("Name: " + map.get(first, "name"));
    print("Age: " + map.get(first, "age"));

    let second = list.get(rows, 1);
    print("Name: " + map.get(second, "name"));

    // Stringify back to CSV
    let header = list.new();
    list.append(header, "x");
    list.append(header, "y");
    let row1 = list.new();
    list.append(row1, "1");
    list.append(row1, "2");
    let row2 = list.new();
    list.append(row2, "3");
    list.append(row2, "4");

    let new_csv = csv.stringify(header);
    print("Single row CSV: " + new_csv);
}
```

### 3.8 Required Tests (`tests/test_stdlib_csv.py`)

| Test | Description |
|------|-------------|
| `test_csv_parse_basic` | Parse `"a,b\n1,2"` → list of lists |
| `test_csv_parse_empty` | Parse `""` → `[[""]]` |
| `test_csv_parse_single_cell` | Parse `"hello"` → `[["hello"]]` |
| `test_csv_parse_quoted` | Parse `'"a,b",c'` → `[["a,b", "c"]]` |
| `test_csv_parse_header_basic` | Parse with header → list of dicts |
| `test_csv_parse_header_empty_data` | Header with no data rows → list with single dict |
| `test_csv_parse_header_access` | Parse header CSV and verify `map.get(row, "col")` works |
| `test_csv_stringify_basic` | Serialize rows → `"a,b\n1,2\n"` |
| `test_csv_stringify_empty` | Serialize `[]` → `""` |
| `test_csv_roundtrip` | Parse → Stringify → Parse yields equivalent structure |
| `test_csv_with_file_read` | Write CSV via `file`, read it back, parse it |

### 3.9 Known Limitations

- No custom delimiter or quote character in v1.0 (defer to v1.1 as `csv.parse_delim(text, delim)`)
- No type inference — all values are strings (users call `convert.to_int` for numbers)
- `stringify` uses comma delimiter and double-quote quoting only
- Dialect/format customization is not exposed (RFC 4180 default only)

---

## 4. Implementation Plan

### 4.1 Implementation Order

1. **Builtins**: Add `json_parse`, `json_stringify`, `csv_parse`, `csv_parse_header`, `csv_stringify` to `compiler/runtime/builtins.py`
2. **Stdlib files**: Create `stdlib/json.ail` and `stdlib/csv.ail` with thin wrappers
3. **Tests**: Create `tests/test_stdlib_json.py` and `tests/test_stdlib_csv.py`
4. **Examples**: Create `examples/json_demo.ail` and `examples/csv_demo.ail`
5. **CLI tests**: Add CLI validation tests in `tests/test_cli.py`
6. **Documentation**: Update `README.md` table and `PROJECT_STATE.json`

### 4.2 What Goes in `.ail` vs. Runtime

| Layer | Responsibility |
|-------|----------------|
| `.ail` wrapper | Name binding, parameter passthrough, documentation surface |
| Builtin (Python) | All format logic, error handling, type conversion |
| Runtime (interpreter) | No changes needed — existing `CallIR` → `BUILTINS` → `print` pipeline handles everything |

### 4.3 No Compiler Changes Required

Both modules follow the exact same pattern as `file`, `path`, `time`, `environment`, and `random`:
- Register Python functions in `BUILTINS` dict
- Create `.ail` wrappers that call the builtins
- No new AST nodes, IR nodes, parser rules, or semantic rules

---

## 5. Testing Strategy

### 5.1 Unit Tests (`test_stdlib_json.py`, `test_stdlib_csv.py`)

- Use the `_run_program` helper identical to existing test files (duplicate ~20 lines boilerplate per file; consider extracting to a shared helper in a later refactor)
- Each test encodes a small AILang program inline, compiles, runs, and asserts the integer return value
- Test data files (JSON/CSV strings) are embedded in the source code — no external fixtures
- `csv` round-trip and file-read tests use `tempfile.TemporaryDirectory` with `os.chdir` sandboxing

### 5.2 CLI Integration Tests

- Add `test_cli_can_run_json_example` and `test_cli_can_run_csv_example` to `tests/test_cli.py`
- Run each example `.ail` file through `compiler.cli.main.run` and assert exit code 0 plus expected output substrings

### 5.3 Existing Example Validation

- The existing `test_all_examples_in_repo_compile_and_run` in `tests/test_validation.py` only discovers `**/main.ail` (subdirectory examples). New top-level examples (`json_demo.ail`, `csv_demo.ail`) are covered by the CLI integration tests above.

### 5.4 Manual Verification Commands

```bash
python -m pytest tests/test_stdlib_json.py -v
python -m pytest tests/test_stdlib_csv.py -v
python -c "from compiler.cli.main import run; print(run('examples/json_demo.ail'))"
python -c "from compiler.cli.main import run; print(run('examples/csv_demo.ail'))"
```

---

## 6. Documentation Changes

### 6.1 `README.md`

Extend the operations table with two new rows:

| json | `parse(text)`, `stringify(value)` |
| csv | `parse(text)`, `parse_header(text)`, `stringify(rows)` |

Add to the prose paragraph: "JSON and CSV format helpers are available via `import json;` and `import csv;`."

### 6.2 `PROJECT_STATE.json`

- Set `current_component` to `"JSON and CSV Modules"`
- Update `completion` to 100.0 for v1.0
- Update `tests.passed` to reflect new test count
- Update `last_session_summary`

---

## 7. Compatibility Considerations

### 7.1 Backward Compatibility

- Both modules are additive — no existing code breaks
- No new reserved words, token kinds, or syntax changes
- No changes to the existing module discovery, compilation, or runtime pipeline

### 7.2 AILang Version Alignment

- Both modules target the existing AILang v0.1.0 runtime
- No dependency on future language features (loops, iterators, etc.)
- Users of `json.parse` receive AILang-native values (int, float, bool, None, str, list, map) that work with all existing `list`, `map`, `string` module functions

### 7.3 Python Version

- `json` and `csv` are part of the Python 3.11+ standard library
- No additional dependencies required

---

## 8. Future Extensions (v1.1+)

| Feature | Module | Rationale |
|---------|--------|-----------|
| `json.stringify_pretty(value, indent)` | json | Human-readable output |
| `json.parse_lines(text)` | json | JSON Lines (NDJSON) support |
| `csv.parse_delim(text, delim)` | csv | Custom delimiter (TSV, etc.) |
| `csv.parse_header_delim(text, delim)` | csv | Header CSV with custom delimiter |
| `toml.parse(text)` | toml | Read-only TOML parsing |
| `ini.parse(text)` | ini | Read-only INI parsing |
| `xml.parse(text)` | xml | Minimal XML parse |

---

## 9. Design Decisions Log

| Decision | Rationale |
|----------|-----------|
| JSON and CSV as Python builtins, not pure AILang | Format parsing requires iteration and character-level scanning, which AILang doesn't support |
| `csv.parse_header` returns list of maps | Enables column access by name via `map.get` — compensates for lack of destructuring |
| Sets auto-convert to arrays in `json.stringify` | Prevents cryptic Python `TypeError`; conversion is lossy but predictable |
| No custom delimiter in csv v1.0 | Keeps API surface minimal; delimiter parameter can be added as a new function |
| No `json.pretty` in v1.0 | Single-argument `stringify` is the minimum viable; pretty-printing is a cosmetic enhancement |
| INI/TOML/XML deferred | Lower user demand, larger API surface, partial overlap with existing examples |
