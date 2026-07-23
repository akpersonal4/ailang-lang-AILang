# M84R.2 — Reproduction Report

**Date:** 2026-07-22
**Environment:** Windows, Python 3.11.15, ailang-lang v1.1.1 (editable install)

---

## P0 — MOD003: Module not found after `ail new demo`

### Claim

Every project created using `ail new demo` fails immediately with `MOD003: Module not found` because the ModuleResolver cannot locate the pip-installed standard library.

### Reproduction Attempt

```bash
ail new verify_demo
cd verify_demo
ail run main.ail
```

### Result: NOT REPRODUCED (as stated)

The generated `main.ail` template contains only `print("Hello, AILang!")` which uses a builtin function, not an import. The project builds and runs successfully.

### Underlying Issue: CONFIRMED

When running from a directory outside the source repository (e.g., a user's home directory after `pip install`), any AILang program that imports stdlib modules fails:

```bash
# From C:\Users\aleckhan\AppData\Local\Temp\ail_verify\
import math;
let x = math.add(10, 20);
io.writeln(convert.to_string(x))
```

Output: `ERROR MOD003: Module not found: math`

**Root Cause:** `_candidate_roots()` in `resolution.py` walks up from the source file's parent directory looking for `stdlib/` subdirectories. In a pip-installed (non-editable) environment, the stdlib is inside the Python site-packages, not relative to the user's project directory.

### Severity

**Medium.** The default `ail new` template works. Only projects that import stdlib modules are affected. This impacts all real-world usage outside the development environment.

---

## P1 — list.sum floating-point truncation

### Claim

`list.sum(list.collect_key(...))` returns incorrect floating-point totals. Example: `15.5 + 2.5 + 4.0` returns `21` instead of `22.0`.

### Reproduction

```ailang
import json;
import list;

fn main() {
    let items0 = json.parse("[{\"val\": 15.5}, {\"val\": 2.5}, {\"val\": 4.0}]");
    let vals = list.collect_key(items0, "val");
    let total = list.sum(vals);
    io.writeln(convert.to_string(total));
    return 0
}
```

### Result: CONFIRMED

Output: `21` (expected: `22.0`)

**Root Cause:** `list_sum()` in `builtins.py` uses `int(item)` which truncates floats to integers before summing. The accumulator is initialized as `0` (int), and all items are cast via `int()`.

---

## P2 — list.sort_by_key incorrect implementation

### Claim

`list.sort_by_key()` calls `list_sort()` instead of `list_sort_by_key()`, making the function incorrect.

### Reproduction

```ailang
import json;
import list;

fn main() {
    let items0 = json.parse("[{\"name\": \"Charlie\", \"age\": 30}, {\"name\": \"Alice\", \"age\": 25}, {\"name\": \"Bob\", \"age\": 35}]");
    let sorted0 = list.sort_by_key(items0, "name");
    # Verify order: Alice, Bob, Charlie
    let sorted1 = list.sort_by_key(items0, "age");
    # Verify order: 25, 30, 35
    return 0
}
```

### Result: NOT REPRODUCED

Output:
```
sort_by_key(name): Alice Bob Charlie
sort_by_key(age): 25 30 35
```

Both sort-by-key operations work correctly. `list.sort_by_key` in the stdlib calls `list_sort(values, key)` which is a polymorphic native function that handles both plain sorting and key-based sorting based on argument count. There is no separate `list_sort_by_key` native function — the design is intentionally polymorphic.

---

## Version Issue

### Claim

Package version: v1.1.1, CLI version: v1.1.0 — mismatch.

### Result: CONFIRMED (but different than claimed)

```
CLI:   v1.1.1
PyPI:  v1.1.0 (installed package metadata)
```

The `pyproject.toml` and `compiler/_version.py` both say `1.1.1`, but `pip show ailang-lang` reports `1.1.0`. This is because the installed package metadata reflects the version at the time of the last `pip install` from PyPI. The source code has been updated to v1.1.1 but the installed package hasn't been rebuilt.

---

## Summary

| Issue | Claimed | Reproduced | Notes |
|-------|---------|------------|-------|
| P0: MOD003 on `ail new` | Every project fails | No (default template works) | Underlying stdlib resolution bug confirmed |
| P1: list.sum float truncation | Returns 21 instead of 22.0 | Yes | `int()` truncation in `list_sum` |
| P2: sort_by_key wrong impl | Calls wrong native function | No | Polymorphic design is correct |
| Version mismatch | Package ≠ CLI | Yes (but reversed) | Installed metadata outdated |
