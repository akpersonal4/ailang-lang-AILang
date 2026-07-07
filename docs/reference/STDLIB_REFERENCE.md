# Standard Library Reference

## Module Index

| Module | Description |
|--------|-------------|
| [string](#string) | String manipulation |
| [math](#math) | Basic arithmetic operations |
| [list](#list) | Dynamic array (ordered, indexable) |
| [array](#array) | Array (alias for list) |
| [map](#map) | Key-value dictionary |
| [set](#set) | Unique-element collection |
| [file](#file) | File system read/write |
| [path](#path) | File path manipulation |
| [json](#json) | JSON parse/stringify |
| [csv](#csv) | CSV parse/stringify |
| [time](#time) | Time utilities |
| [random](#random) | Random number generation |
| [environment](#environment) | Process environment access |
| [convert](#convert) | Type conversion |
| [io](#io) | Simple I/O helpers |
| [system](#system) | System-level operations |

---

## string

```ail
import string;
```

### `concat(a, b)`
Concatenates two strings.
```ail
string.concat("hello", " world")  // "hello world"
```

### `equals(a, b)`
Checks string equality.
```ail
string.equals("abc", "abc")  // true
```

### `uppercase(value)`
Converts to uppercase.
```ail
string.uppercase("hello")  // "HELLO"
```

### `lowercase(value)`
Converts to lowercase.
```ail
string.lowercase("HELLO")  // "hello"
```

### `length(value)`
Returns the number of characters.
```ail
string.length("hello")  // 5
```

### `contains(value, needle)`
Checks if `value` contains the substring `needle`.
```ail
string.contains("hello world", "world")  // true
```

### `starts_with(value, prefix)`
Checks if `value` starts with `prefix`.
```ail
string.starts_with("hello", "he")  // true
```

### `ends_with(value, suffix)`
Checks if `value` ends with `suffix`.
```ail
string.ends_with("hello", "lo")  // true
```

### `trim(value)`
Removes leading and trailing whitespace.
```ail
string.trim("  hello  ")  // "hello"
```

### `substring(value, start, end)`
Extracts a portion of a string from `start` to `end` (exclusive).
```ail
string.substring("hello", 1, 4)  // "ell"
```

---

## math

```ail
import math;
```

### `add(a, b)`
Addition.
```ail
math.add(3, 4)  // 7
```

### `sub(a, b)`
Subtraction.
```ail
math.sub(10, 3)  // 7
```

### `mul(a, b)`
Multiplication.
```ail
math.mul(3, 4)  // 12
```

### `div(a, b)`
Division.
```ail
math.div(10, 3)  // 3.333...
```

### `abs(value)`
Absolute value.
```ail
math.abs(-5)    // 5
math.abs(5)     // 5
```

### `min(a, b)`
Minimum of two values.
```ail
math.min(3, 7)  // 3
```

### `max(a, b)`
Maximum of two values.
```ail
math.max(3, 7)  // 7
```

---

## list

```ail
import list;
```

A `list` is an ordered, indexable collection. Indexes start at 0.

### `new()`
Creates a new empty list.
```ail
let items = list.new();
```

### `append(values, value)`
Appends a value to the end.
```ail
list.append(items, 10);
list.append(items, 20);
```

### `len(values)`
Returns the number of elements.
```ail
list.len(items)  // 2
```

### `get(values, index)`
Returns the element at `index`.
```ail
list.get(items, 0)  // 10
```

### `contains(values, value)`
Checks if the list contains a value.
```ail
list.contains(items, 10)  // true
```

### `remove(values, value)`
Removes the first occurrence of `value`.
```ail
list.remove(items, 10);
```

### `clear(values)`
Removes all elements.
```ail
list.clear(items);
```

### Known Missing Operations

These are **not** available in the stdlib and must be implemented manually:

| Operation | Fallback |
|-----------|----------|
| `list.copy(list)` | Write recursive `list_copy(src, result, pos)` |
| `list.sort(list, comp)` | Write recursive selection sort |
| `list.set(list, idx, val)` | Use map-based wrappers |

---

## array

```ail
import array;
```

The `array` module is identical to `list`. See [list](#list) for the full API.

### `new()`, `push(values, value)`, `len(values)`, `get(values, index)`, `contains(values, value)`, `remove(values, value)`, `clear(values)`

---

## map

```ail
import map;
```

A `map` is a key-value dictionary.

### `new()`
Creates a new empty map.
```ail
let data = map.new();
```

### `set(values, key, value)`
Sets a key-value pair.
```ail
map.set(data, "name", "Alice");
map.set(data, "age", 30);
```

### `get(values, key)`
Returns the value for `key`. Raises error if key does not exist.
```ail
map.get(data, "name")  // "Alice"
```

### `has(values, key)`
Checks if `key` exists.
```ail
map.has(data, "name")  // true
```

### `delete(values, key)`
Removes a key-value pair.
```ail
map.delete(data, "age");
```

### `keys(values)`
Returns a list of all keys.
```ail
map.keys(data)  // ["name", "age"]
```

### `clear(values)`
Removes all entries.
```ail
map.clear(data);
```

---

## set

```ail
import set;
```

A `set` is an unordered collection of unique elements.

### `new()`
Creates a new empty set.
```ail
let s = set.new();
```

### `add(values, value)`
Adds a value to the set.
```ail
set.add(s, "a");
set.add(s, "b");
set.add(s, "a");  // No effect — "a" already exists
```

### `contains(values, value)`
Checks if the set contains a value.
```ail
set.contains(s, "a")  // true
set.contains(s, "c")  // false
```

### `len(values)`
Returns the number of elements.
```ail
set.len(s)  // 2
```

### `remove(values, value)`
Removes a value.
```ail
set.remove(s, "a");
```

### `clear(values)`
Removes all elements.
```ail
set.clear(s);
```

---

## file

```ail
import file;
```

### `exists(path)`
Checks if a file exists.
```ail
file.exists("data.txt")  // true or false
```

### `read(path)`
Reads the entire file as a string.
```ail
let content = file.read("data.txt");
```

### `write(path, content)`
Writes content to a file (overwrites).
```ail
file.write("output.txt", "hello world");
```

### `append(path, content)`
Appends content to a file.
```ail
file.append("log.txt", "new entry\n");
```

### `remove(path)`
Deletes a file.
```ail
file.remove("temp.txt");
```

---

## path

```ail
import path;
```

### `join(a, b)`
Joins two path components.
```ail
path.join("dir", "file.txt")  // "dir/file.txt" on Unix, "dir\\file.txt" on Windows
```

### `basename(path)`
Returns the file name from a path.
```ail
path.basename("/foo/bar.txt")  // "bar.txt"
```

### `dirname(path)`
Returns the directory portion.
```ail
path.dirname("/foo/bar.txt")  // "/foo"
```

### `extension(path)`
Returns the file extension (including dot).
```ail
path.extension("file.txt")  // ".txt"
path.extension("archive.tar.gz")  // ".gz"
```

### `normalize(path)`
Normalizes a path (resolves `..` and `.`).
```ail
path.normalize("foo/../bar/./baz")  // "bar/baz"
```

---

## json

```ail
import json;
```

### `parse(text)`
Parses a JSON string into an AILang value.
```ail
let data = json.parse("{\"name\": \"Alice\", \"age\": 30}");
let items = json.parse("[1, 2, 3]");
let empty = json.parse("null");  // Returns Python None (no AILang literal)
```

### `stringify(value)`
Serializes an AILang value to a JSON string.
```ail
import map;
let data = map.new();
map.set(data, "name", "Bob");
let output = json.stringify(data);  // '{"name": "Bob"}'
```

### Type Mapping

| JSON | AILang |
|------|--------|
| `null` | Python `None` (no literal) |
| `true` / `false` | `true` / `false` |
| number | `int` or `float` |
| string | `str` |
| array | `list` |
| object | `map` |

### Known Limitations

- No `json.pretty()` or custom indentation
- No streaming parse (JSON Lines)
- Sets are serialized as arrays
- `null` cannot be written or compared in AILang source

---

## csv

```ail
import csv;
```

### `parse(text)`
Parses CSV text into a list of rows (each row is a list of strings).
```ail
let rows = csv.parse("a,b\n1,2");
// rows = [["a", "b"], ["1", "2"]]
```

### `parse_header(text)`
Parses CSV with a header row. Returns a list of maps keyed by column names.
```ail
let rows = csv.parse_header("name,age\nAlice,30\nBob,25");
let first = list.get(rows, 0);
// map.get(first, "name") -> "Alice"
```

### `stringify(rows)`
Serializes a list of rows back to CSV text.
```ail
import list;

fn main() {
    let row1 = list.new();
    list.append(row1, "a");
    list.append(row1, "b");
    let row2 = list.new();
    list.append(row2, "1");
    list.append(row2, "2");
    let data = list.new();
    list.append(data, row1);
    list.append(data, row2);
    let csv_text = csv.stringify(data);
    print(csv_text);
    return 0
}
```

### Known Limitations

- No custom delimiter or quote character
- All values are strings (use `convert.to_int` for numbers)
- RFC 4180 dialect only

---

## time

```ail
import time;
```

### `now()`
Returns the current date/time as a formatted string.
```ail
time.now()  // "2026-07-05 12:34:56"
```

### `timestamp()`
Returns the current Unix timestamp (seconds since epoch).
```ail
time.timestamp()  // 1751698496.123
```

### `sleep(ms)`
Sleeps for the specified number of milliseconds.
```ail
time.sleep(500);  // Sleep for 500ms
```

### `format(ts)`
Formats a Unix timestamp to a human-readable string.
```ail
time.format(1751698496)  // "2026-07-05 12:34:56"
```

---

## random

```ail
import random;
```

### `int(min, max)`
Returns a random integer in the range `[min, max]` (inclusive).
```ail
let dice = random.int(1, 6);
```

### `float()`
Returns a random float in the range `[0.0, 1.0)`.
```ail
let f = random.float();
```

### `choice(collection)`
Returns a random element from a collection (list or array).
```ail
let colors = list.new();
list.append(colors, "red");
list.append(colors, "green");
let c = random.choice(colors);
```

---

## environment

```ail
import environment;
```

### `get(name)`
Returns the value of an environment variable.
```ail
let home = environment.get("HOME");  // or "USERPROFILE" on Windows
```

### `cwd()`
Returns the current working directory.
```ail
let dir = environment.cwd();  // "/home/user/project"
```

### `args()`
Returns the command-line arguments as a list.
```ail
let args = environment.args();  // ["program.ail", "arg1", "arg2"]
```

---

## convert

```ail
import convert;
```

### `to_string(value)`
Converts a value to its string representation.
```ail
convert.to_string(42)    // "42"
convert.to_string(true)  // "True"
```

### `to_int(value)`
Converts a string or int to an integer.
```ail
convert.to_int("123")  // 123
convert.to_int(42)     // 42
```

### `to_bool(value)`
Converts a string to a boolean. Recognizes `"true"`, `"1"`, `"yes"` as `true`.
```ail
convert.to_bool("true")  // true
convert.to_bool("false")  // false
```

### `to_number(value)`
Identity function — returns the value unchanged. Reserved for future numeric conversion.
```ail
convert.to_number(42)  // 42
```

---

## io

```ail
import io;
```

### `write(value)`
Prints a value to stdout (alias for `print`).
```ail
io.write("hello");
```

### `writeln(value)`
Prints a value followed by a newline.
```ail
io.writeln("line 1");
```

### `println(value)`
Prints a value followed by a newline.
```ail
io.println("line 2");
```

---

## system

```ail
import system;
```

### `exit(code)`
Exits the process with the given exit code. If `code` is omitted, defaults to 0.
```ail
system.exit(0);  // Normal exit
system.exit(1);  // Error exit
```
