# Log Analyzer — AI Usage Guide

## Overview

Demonstrates file I/O, string parsing, and map-based aggregation in AILang.

## Key Patterns

### File Reading and Line Splitting

```
let raw_content = file.read(filename);
let raw_lines = string.split(raw_content, "\n");
```

### String Parsing with Split

Log lines are split by space to extract structured fields:

```
let toks = string.split(line, " ");
let level = list.get(toks, 2);
```

### Substring Extraction

`string.substring(str, start, end)` uses Python-style slicing (end exclusive).
Wrap arithmetic on stdlib calls with `convert.to_int` to satisfy the type checker:

```
let pfx = convert.to_int(string.length(dt) + string.length(tm) + string.length(lvl) + 3);
let msg = string.substring(line, pfx, string.length(line));
```

### Recursive Counting Pattern

Use a helper with an accumulator index to count matching entries.
Return `0` for base cases (function return type defaults to `INT_TYPE`):

```
fn count_errors_helper(entries, idx) {
    if (idx >= list.len(entries)) { return 0 }
    let item = list.get(entries, idx);
    let lvl = map.get(item, "level");
    if (lvl == "ERROR") {
        return 1 + count_errors_helper(entries, idx + 1)
    }
    count_errors_helper(entries, idx + 1)
}
```

### Map-Based Aggregation

Initialize a report map with expected keys, then increment counts recursively:

```
let report = map.new();
map.set(report, "INFO", 0);
map.set(report, "ERROR", 0);
// recursive helper increments counts via map.get + map.set
```

## AI Notes

- AILang functions default to `INT_TYPE` return — use `return 0`, not `return true`
- `if` conditions must be `BOOL_TYPE` — use comparisons (`==`, `!=`) directly
- Wrap arithmetic on stdlib function results with `convert.to_int` to avoid TYP001
- `list.append` mutates in place and returns the modified list
- Always initialize map keys before aggregation to avoid missing-key errors
