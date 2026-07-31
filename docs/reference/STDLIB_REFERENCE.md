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

### `find(value, needle)`
Returns the index of the first occurrence of `needle` in `value`, or -1 if not found.
```ail
string.find("hello world", "world")  // 6
string.find("hello", "xyz")  // -1
```

### `find_from(value, needle, start_pos)`
Returns the index of the first occurrence of `needle` in `value` starting from `start_pos`, or -1 if not found.
```ail
string.find_from("hello world", "l", 3)  // 9
```

### `split(value, delim)`
Splits `value` into a list of strings using `delim` as the delimiter.
```ail
let parts = string.split("a,b,c", ",");
// parts contains: "a", "b", "c"
```

### `join(values, separator)`
Joins a list of strings into a single string, separated by `separator`.
```ail
let words = list.new();
list.append(words, "hello");
list.append(words, "world");
string.join(words, " ")  // "hello world"
```

### `from_int(value)`
Converts an integer to its string representation.
```ail
string.from_int(42)  // "42"
```

### `from_bool(value)`
Converts a boolean to its string representation.
```ail
string.from_bool(true)  // "True"
string.from_bool(false)  // "False"
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

### `sum(values)`
Returns the sum of all numeric values in the list.
```ail
let nums = list.new();
list.append(nums, 10);
list.append(nums, 20);
list.append(nums, 30);
list.sum(nums)  // 60
```

### `sort(values)`
Sorts a list of primitive values (numbers, strings) in ascending order. Returns the sorted list.
```ail
let nums = list.new();
list.append(nums, 30);
list.append(nums, 10);
list.append(nums, 20);
let sorted = list.sort(nums);
// sorted contains: 10, 20, 30
```

### `sort_by_key(values, key)`
Sorts a list of maps by the value of `key` in ascending order. Returns the sorted list.
```ail
let people = list.new();
let p1 = map.new();
map.set(p1, "name", "Bob");
map.set(p1, "age", 25);
let p2 = map.new();
map.set(p2, "name", "Alice");
map.set(p2, "age", 30);
list.append(people, p1);
list.append(people, p2);
let sorted = list.sort_by_key(people, "age");
// sorted ordered by age: Bob (25), Alice (30)
```

### `copy(values)`
Returns a shallow copy of the list.
```ail
let original = list.new();
list.append(original, 10);
list.append(original, 20);
let cloned = list.copy(original);
list.append(original, 30);
// original has 3 items, cloned has 2 items
```

### `find(values, key, value)`
Finds the first map in the list where `map.get(item, key)` equals `value`. Returns the matching map or `false` if not found.
```ail
list.find(people, "name", "Bob")  // {name: "Bob", age: 25}
```

### `filter(values, key, value)`
Returns a new list containing all items where `map.get(item, key)` equals `value`. Alias for `filter_by_key`.
```ail
let adults = list.filter(people, "status", "active");
```

### `filter_by_key(values, key, value)`
Returns a new list containing all items where `map.get(item, key)` equals `value`.
```ail
let adults = list.filter_by_key(people, "status", "active");
```

### `filter_by_contains(values, key, substring)`
Returns a new list containing all items where `map.get(item, key)` contains `substring`.
```ail
let matches = list.filter_by_contains(people, "name", "li");
// Returns items whose name field contains "li"
```

### `collect_key(values, key)`
Extracts the values for `key` from each item into a new list.
```ail
let names = list.collect_key(people, "name");
// Returns a list of all "name" values
```

### `group_by_key(values, key)`
Groups items by the value of `key`. Returns a map where each key is a distinct value and each value is a list of matching items.
```ail
let grouped = list.group_by_key(people, "department");
// map.get(grouped, "engineering") -> list of engineering people
```

### `sum_by_key(values, key)`
Sums the numeric values of `key` across all items in the list.
```ail
let total = list.sum_by_key(invoices, "amount");
```

### `take(values, n)`
Returns a new list containing the first `n` items.
```ail
let first_three = list.take(people, 3);
```

### `skip(values, n)`
Returns a new list with the first `n` items removed.
```ail
let rest = list.skip(people, 3);
```

### `search_by_name(values, query)`
Searches items by their `name` field (case-insensitive substring match). Returns a list of matching items.
```ail
let results = list.search_by_name(people, "alice");
```

### `exists_by_key(values, key, value)`
Returns `true` if any item in the list has `map.get(item, key)` equal to `value`, `false` otherwise.
```ail
list.exists_by_key(people, "name", "Bob")  // true
```

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

### `get_or_default(values, key, default)`
Returns the value for `key` if it exists, otherwise returns `default`.
```ail
map.get_or_default(data, "age", 0)  // 0 if "age" not set
map.get_or_default(data, "name", "unknown")  // "Alice" if set
```

### `safe_get(values, key, default)`
Returns the value for `key` if it exists, otherwise returns `default`. Alias for `get_or_default`.
```ail
map.safe_get(data, "missing_key", "fallback")  // "fallback"
```

### `values(values)`
Returns a list of all values in the map.
```ail
map.values(data)  // ["Alice", 30]
```

---

### Map Iteration Patterns

Since AILang uses recursion (not loops), iterating over a map follows a recursive pattern using `map.keys()`.

#### Basic iteration over keys

```ail
fn visit_keys(keys, index) {
    if (index >= list.len(keys)) {
        return 0
    }
    let key = list.get(keys, index);
    print("Key:", key);
    return visit_keys(keys, math.add(index, 1))
}

fn main() {
    let data = map.new();
    map.set(data, "name", "Alice");
    map.set(data, "role", "admin");
    map.set(data, "active", true);

    let all_keys = map.keys(data);
    visit_keys(all_keys, 0);
    return 0
}
```

#### Iterating over keys and values

```ail
fn visit_items(keys, index, data) {
    if (index >= list.len(keys)) {
        return 0
    }
    let key = list.get(keys, index);
    let value = map.get(data, key);
    print(key, value);
    return visit_items(keys, math.add(index, 1), data)
}

fn main() {
    let data = map.new();
    map.set(data, "name", "Alice");
    map.set(data, "role", "admin");

    let all_keys = map.keys(data);
    visit_items(all_keys, 0, data);
    return 0
}
```

#### Safe access with guard

Always guard `map.get` with `map.has` when the key may not exist:

```ail
fn display_value(data, key) {
    if (map.has(data, key)) {
        let value = map.get(data, key);
        print(key, value)
    } else {
        print("Key not found:", key)
    }
}
```

#### Building a filtered map (copy with condition)

```ail
fn copy_matching(keys, index, source, target) {
    if (index >= list.len(keys)) {
        return target
    }
    let key = list.get(keys, index);
    let value = map.get(source, key);
    if (value > 10) {
        map.set(target, key, value)
    }
    return copy_matching(keys, math.add(index, 1), source, target)
}
```

### Common Mistakes

#### Using `list.get` on a map

Maps are not lists. Calling `list.get(map_value, 0)` produces a runtime diagnostic:

```
Runtime Error

Operation:
  list.get

Reason:
  Expected a List, but received a Map

Expected:
  List

Received:
  Map

Location:
  main.ail:12

Suggestion:
  Use map.get() or map.keys() to access map contents.
```

#### Calling `map.get` without a guard

If the key does not exist, `map.get` raises a diagnostic. Always check with `map.has` first or use `map.get_or_default` / `map.safe_get`:

```ail
// WRONG — will fail if key is missing:
let value = map.get(data, "missing_key");

// RIGHT:
let value = map.get_or_default(data, "missing_key", 0);
```

#### Forgetting that `map.keys` returns a list of strings

Even if keys are numeric concepts, `map.keys` always returns a list of strings. Use `convert.to_int` if you need numeric keys:

```ail
map.set(data, "100", "value");
let keys = map.keys(data);     // ["100"] - list of strings, not numbers
let first = list.get(keys, 0); // "100" - still a string
let num = convert.to_int(first); // 100 - now a number
```

> See `docs/guides/PACKAGE_VALIDATION.md` for package manifest validation diagnostics, and `compiler/runtime/errors.py` for the full runtime diagnostic format.

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

### `listdir(path)`
Returns a sorted list of entries in the given directory.
```ail
let entries = file.listdir(".");
// ["dir1", "dir2", "file.txt"]
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
Parses a JSON string into an AILang value. On invalid JSON input, `parse` returns `false` (rather than raising an error), so callers should validate the result before use.
```ail
let data = json.parse("{\"name\": \"Alice\", \"age\": 30}");
let items = json.parse("[1, 2, 3]");
let empty = json.parse("null");  // Returns Python None (no AILang literal)
let bad = json.parse("{not valid json");  // false
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
Returns the command-line arguments as a list. When run via `ail run`, the script path is excluded — only user-provided arguments are returned.
```ail
// ail run hello.ail one two three
let args = environment.args();  // ["one", "two", "three"]
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
Converts a string or int to an integer. Equivalent to `to_int`.
```ail
convert.to_number("42")  // 42
convert.to_number(42)     // 42
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

### `read()`
Reads a line from stdin and returns it as a string. Returns an empty string on EOF.
```ail
let name = io.read();
io.writeln("Hello, " + name);
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

---

## Language Rules & Behaviors

This section documents language behaviors that are not obvious from function signatures alone.

### Recursion Only (No While/For Loops)

AILang has **no while loops and no for loops** (except the experimental `for-in` with `--experimental-loops`). All iteration must use **recursion**.

```ail
// WRONG — this will produce WHILE001 error
let i = 0;
while (i < 10) {
    print(i);
    i = i + 1;
}

// CORRECT — use recursion
fn count_up(n) {
    if (n == 0) {
        return 0;
    }
    print(n);
    return count_up(n - 1);
}
count_up(10);
```

### No Nested Functions

All functions must be at the **top level** of the file. Defining a function inside another function produces LANG001.

```ail
// WRONG — LANG001 error
fn main() {
    fn helper() { return 1; }
    let x = helper();
}

// CORRECT — helper at top level
fn helper() { return 1; }
fn main() {
    let x = helper();
}
```

### Bottom-Up Ordering (No Forward References)

Functions must be defined **before** they are called. AILang uses single-pass compilation, so forward references produce SEM002.

```ail
// WRONG — SEM002: Forward reference
fn main() { greet(); }
fn greet() { print("hello"); }

// CORRECT — callee above caller
fn greet() { print("hello"); }
fn main() { greet(); }
```

### Return Requires Expression

Every `return` statement must have a value expression. Bare `return;` is not allowed.

```ail
// WRONG — missing expression
fn do_nothing() { return; }

// CORRECT
fn do_nothing() { return 0; }
```

### Import Rules

- Imports must be at the **top level** (never inside a function body).
- Each import declares a module namespace (e.g., `import list;` creates `list.` prefix).
- Use `as` to alias: `import list as lst;`.
- All 16 stdlib modules require explicit import before use.

```ail
import list;
import map;
import io;

fn main() {
    let items = list.new();
    list.append(items, 1);
    io.writeln(list.get(items, 0));
}
```

### Integer Division

The `/` operator performs **floating-point division**, not integer division. `10 / 3` returns `3.333...`, not `3`.

```ail
math.div(10, 3)  // 3.333...
10 / 3           // 3.333...
```

To get integer division, use `math.div` and convert: `convert.to_int(math.div(10, 3))` → `3`.

### Boolean Printing

Booleans print as `True` / `False` (Python-style capitalization):

```ail
print(true);   // prints: True
print(false);  // prints: False
```

### `convert.to_number` Behavior

`convert.to_number(value)` is equivalent to `convert.to_int(value)`. It converts a string to an integer, or returns the integer as-is. It does **not** return floats.

```ail
convert.to_number("42")  // 42
convert.to_number(42)    // 42
```

### `list.sort()` Returns NEW List

`list.sort()` returns a **new sorted list**. The original list is not modified.

```ail
let nums = list.new();
list.append(nums, 30);
list.append(nums, 10);
let sorted = list.sort(nums);
// nums still: [30, 10]
// sorted is:  [10, 30]
```

### `list.set()` Does Not Exist

There is no `list.set()` function. To modify a list:
- Use `list.append(value)` to add to the end.
- Use `map.set(key, value)` for key-value storage.

### `string.replace()` Does Not Exist

There is no `string.replace()` function. To modify strings:
- Use `string.substring()` to extract parts.
- Use `string.concat()` to join parts with the replacement.

```ail
import string;
// Replace "world" with "AILang" in "hello world"
let before = string.substring("hello world", 0, 6);
let after = string.substring("hello world", 11, 11);
let result = string.concat(before, "AILang");
result = string.concat(result, after);
// result: "hello AILang"
```

### `&&` Is Eager

Both operands of `&&` always execute. When the right side depends on the left side, use nested `if` instead:

```ail
// DANGEROUS — right side executes even if left is false
if (map.has(m, "key") && map.get(m, "key") > 0) { ... }

// SAFE — nested if
if (map.has(m, "key")) {
    if (map.get(m, "key") > 0) { ... }
}
```

### `string.concat` Takes Exactly 2 Arguments

Use `+` operator for concatenating 3 or more strings:

```ail
// WRONG — string.concat takes exactly 2 args
string.concat("a", "b", "c")

// CORRECT — use +
let result = "a" + "b" + "c";
```

### Variable Names Must Be Unique

Each function must use unique variable names. Reusing `i`, `x`, `result`, etc. across functions produces SEM001.

```ail
fn a() {
    let counter = 0;
    return counter;
}
fn b() {
    let counter = 1;  // OK — different function scope
    return counter;
}
```
