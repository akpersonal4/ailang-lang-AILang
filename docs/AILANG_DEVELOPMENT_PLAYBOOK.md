# AILang Development Playbook

**Informed by:** 10 benchmarks, 66 applications, 522 tests, ~6,610 LOC of AILang  
**Goal:** Eliminate predictable iterations through upfront planning  

---

## Dependency Planning

### The Iteration Problem

Every AILang benchmark follows the same failure pattern:

```
FIRST COMPILE → FAIL (always — wrong function order)
SECOND COMPILE → PASS
FIRST RUNTIME → FAIL (usually — map key / guard / concat issue)
SECOND RUNTIME → PASS (or cascade to more runtime fixes)
```

Root cause: 100% of first compiles fail due to forward references. 90% of first runtimes fail due to missing guards, wrong map keys, or argument count errors.

### Dependency Map Method

```
□ Identify every function the program needs
□ Draw the call graph: who calls whom
□ Number functions by dependency depth:
    Level 0: No dependencies (pure utilities, helpers with no deps)
    Level 1: Depends only on Level 0
    Level 2: Depends on Level 0-1
    ...
    Level N: main() — depends on everyone
□ Write functions in Level 0 → Level N order
```

**Rule:** If `fn a()` calls `fn b()`, `b` must appear before `a` in the file.

### Stdlib Existence Table

| Function | Exists? | Fallback |
|----------|:-------:|----------|
| `string.concat(a, b)` | ✅ Yes (2 args only) | Use `+` for 3+ strings |
| `string.length(s)` | ✅ Yes | — |
| `string.substring(s, start, end)` | ✅ Yes | — |
| `string.contains(s, pattern)` | ✅ Yes | — |
| `string.split(s, delim)` | ❌ **No** | Write recursive `split_string` |
| `string.find(s, pattern)` | ❌ **No** | Write recursive `find_in_string` |
| `string.join(list, sep)` | ❌ **No** | Write recursive join |
| `string.replace(s, from, to)` | ❌ **No** | Write character-by-character |
| `list.copy(list)` | ❌ **No** | Write recursive `list_copy(src, result, pos)` |
| `list.sort(list, comparator)` | ❌ **No** | Write recursive selection sort |
| `list.set(list, index, value)` | ❌ **No** | Use map-based wrappers |
| `map.get(map, key)` | ✅ Yes (raises on missing) | Guard with `map.has(map, key)` |
| `map.has(map, key)` | ✅ Yes | — |

### Evidence

| Iteration Type | Without Planning | With Playbook |
|---------------|:----------------:|:-------------:|
| Compile iterations | Always (10/10) | ~0 |
| Runtime (map key) | 40% (4/10) | ~0 |
| Runtime (missing guard) | 20% (2/10) | ~0 |
| Runtime (concat args) | 30% (3/10) | ~0 |
| Runtime (variable collision) | 20% (2/10) | ~0 |
| Runtime (stdlib missing) | 60% (6/10) | ~0 |

**Expected result:** First compile ~90%+, first runtime ~70%+, total revisions 1–2 (was 3–9).

---

## Bottom-up Function Ordering

Write in this order:

```
Level 0: Pure utilities (is_digit, find_substring — no deps)
Level 1: Combine utilities (depends on Level 0)
Level 2: Business logic (depends on Level 0-1)
...
Level N: main() (depends on everyone)
```

**Convention:** Each function must be defined before any function that calls it. The compiler reports `Undefined identifier: X` when violated. Fix: move `X` above its caller.

---

## Recursion Patterns

### Universal Iteration Wrapper

```
fn process_helper(coll, i, acc) {
    if (i >= list.len(coll)) { return acc }
    let item = list.get(coll, i);
    list.append(acc, transformed_item);
    return process_helper(coll, i + 1, acc)
}
fn process_all(coll) { return process_helper(coll, 0, list.new()) }
```

### Patterns Available (see `examples/patterns/`)

- `recursive_filter.ail` — keep elements matching a predicate
- `recursive_map.ail` — transform every element
- `recursive_reduce.ail` — fold list to single value
- `recursive_search.ail` — find element by predicate
- `dependency_graph.ail` — transitive dependency collection
- `topological_sort.ail` — DFS-based dependency ordering

---

## Map Safety Patterns

**Golden rule:** Every `map.get` must be guarded by `map.has`.

```
// WRONG — crashes if key missing:
let val = map.get(data, "key");

// RIGHT:
if (map.has(data, "key")) {
    let val = map.get(data, "key")
}
```

**Key audit:** Map keys are case-sensitive strings. A mismatch between `map.set` and `map.get` only surfaces at runtime — there is no compile-time check. Audit all key names upfront.

---

## String Handling Patterns

### Existing stdlib APIs (use these, don't reimplement)

`string.length`, `string.equals`, `string.concat(a, b)`, `string.substring(s, start, end)`, `string.contains(s, pattern)`, `string.starts_with`, `string.ends_with`, `string.uppercase`, `string.lowercase`, `string.trim`

### Must be written manually

- **split:** `string.split(text, delim)` does not exist. See `examples/patterns/string_split.ail`
- **find:** `string.find(text, pattern)` does not exist. See `examples/patterns/string_find.ail`
- **join:** `string.join(list, sep)` does not exist. Write recursive join.
- **replace:** `string.replace(s, from, to)` does not exist. Write character-by-character.

### concat constraint

`string.concat` takes exactly 2 arguments. For 3+ strings, use `+`:
```ail
let s = a + b + c;  // correct
let s = string.concat(a, b, c);  // Error: Expected 2 arguments, got 3
```

---

## File Handling

### Stdlib API

`file.exists(path)`, `file.read(path)`, `file.write(path, content)`, `file.append(path, content)`, `file.remove(path)`

### File I/O Pattern

```ail
import file;
import string;

fn read_lines(path) {
    let content = file.read(path);
    if (string.length(content) == 0) { return list.new() }
    return split_string(content, "\n")  // see examples/patterns/string_split.ail
}

fn write_lines(path, lines) {
    let content = join_strings(lines, "\n");  // custom recursive join
    file.write(path, content);
    return 0
}
```

### Path utilities

`path.join(a, b)`, `path.basename(path)`, `path.dirname(path)`, `path.extension(path)`, `path.normalize(path)`

---

## JSON Persistence

### Stdlib API

`json.parse(text)`, `json.stringify(value)`

### JSON Store Pattern (see `examples/patterns/json_store.ail`)

```ail
import json;
import file;
import list;
import map;
import string;

fn load_data(filepath) {
    if (!file.exists(filepath)) { return list.new() }
    let content = file.read(filepath);
    if (string.length(content) == 0) { return list.new() }
    return json.parse(content)
}

fn save_data(filepath, data) {
    let text = json.stringify(data);
    file.write(filepath, text);
    return 0
}
```

### Limitations

- No `json.pretty()` or custom indentation
- No streaming parse (JSON Lines)
- Sets are serialized as arrays
- `null` cannot be written or compared in AILang source

---

## Error Decoder

| Error Message | Likely Root Cause | Fix |
|---------------|-------------------|-----|
| `Undefined identifier: X` | Forward reference | Move `X` before its caller |
| `Unexpected token` | `while`/`for` keyword used | Replace with recursion |
| `Expected 2 arguments, got N` | `concat(a, b, c)` with 3+ args | Use `a + b + c` |
| `list index out of range` | Empty list access | Guard with `list.len` |
| `KeyError: X` | `map.get` on missing key | Add `map.has` guard |
| `Expected expression` | `let x;` without initializer | Add `let x = value` |
| `Duplicate declaration: X` | Two functions same name | Remove orphaned duplicate |
| No output / timeout | Infinite recursion | Check base case, reduce recursion depth |
| `Undefined identifier: index_of` | Called nonexistent `string.index_of` | Write custom `find_substring` |
| `Undefined identifier: split` | Called nonexistent `string.split` | Write custom `split_string` |

---

## Anti-patterns

| Anti-pattern | Why It Fails | Remedy |
|-------------|--------------|--------|
| Top-down function ordering | Compiler rejects forward references | Write bottom-up (Level 0 → main) |
| `&&` as short-circuit guard | `&&` is eager — both sides execute | Use nested `if` when right operand depends on left |
| Reusing `i` in multiple functions | `let` shares global scope | Use unique names per function |
| `map.get` without `map.has` check | Crashes at runtime on missing key | Always guard with `map.has` |
| Writing loop constructs | `while`/`for` don't exist | Use recursive helper + wrapper |
| `string.concat(a, b, c)` with 3+ args | Takes exactly 2 args | Use `+` for 3+ strings |
| Blindly calling missing stdlib functions | `split`, `find`, `join`, `sort`, `list.copy` don't exist | Check stdlib table first |
| 100+ functions in a single file | Forward reference ordering becomes error-prone and exhausting beyond ~100 functions | Plan multi-file split when possible; physically sort by dependency level |
| `let` without initializer | Syntax error | `let x = value` always |
| `return` without value | Syntax error | `return expr` always |

---

## Benchmark Lessons

Derived from 10 benchmarks. Each lesson confirmed in ≥2 independent apps before inclusion.

1. **Forward references are the #1 compile failure** (100% of benchmarks). Fix: dependency map before writing.
2. **Missing stdlib functions** (`split`, `find`, `join`, `sort`) cause 60% of first-run failures. Fix: stdlib audit table.
3. **Eager `&&`** causes silent logic errors when right operand depends on left (40% of benchmarks). Fix: nested `if`.
4. **Map key strings** are opaque at compile time — mismatches only surface at runtime (40% of benchmarks). Fix: key name audit.
5. **Variable scoping is global** — `let i` in one function overwrites `i` in another (20% of benchmarks). Fix: unique names.
6. **`string.concat` 2-arg limit** catches 30% of benchmarks. Fix: use `+` for 3+ strings.
7. **100% build+run** is achievable with upfront planning — 10/10 benchmark apps passed after applying this playbook.
8. **Compiler is deterministic** — identical SHA-256 across rebuilds. No flaky failures.
9. **Compile time scales linearly** — 5,000 LOC in ~1.88s, 10,000 LOC stress-tested.
10. **Production readiness (6.0/10)** — suitable for CRUD/data-processing ≤2,000 LOC; not suitable for compute-heavy workloads.
11. **`list.copy` does not exist** — confirmed by Kanban (1012 LOC, 102 functions). Always write a custom recursive `list_copy`.
12. **~100 functions per file is the practical max** — beyond this, forward reference ordering becomes unmanageable without multi-file support. Plan to split early.

---

*This playbook is a living document. Update it when:
- A new lesson appears in ≥2 independent apps
- A new stdlib function ships
- A new anti-pattern is identified
- A new pattern file is added to `examples/patterns/`*
