# Development Log — Spreadsheet Formula Engine

**Benchmark:** #009 — Spreadsheet Formula Engine  
**Language:** AILang v0.1.2  
**Date:** 2026-07-05

---

## Revision History

| Revision | Type | Result | Description |
|:--------:|------|--------|-------------|
| R1 | Compile | FAIL | Multiple language compatibility issues: no `while` loops, no mutual recursion, no `string.index_of`, `map.get` on missing key raises error, `let` needs initializer, `string.concat` takes only 2 args, `-` tokenized as negative number literal |
| R2 | Compile | PASS | All compatibility fixes applied; runtime fails with "list index out of range" in chained formulas test |
| R3 | Runtime | PASS | Fixed `i - 1` typo → `i + 1` in `eval_topo_order`; all 31 tests pass |

---

## R1 — Initial Compile (FAIL)

### Issues Found (Batch)

| # | Issue | Error | Fix |
|---|-------|-------|-----|
| 1 | `while` loops not supported | `Error: Unexpected token` | Replaced all `while` loops with recursion |
| 2 | Mutual recursion in DFS | `Error: Undefined identifier` | Merged `dfs_visit_node` and `dfs_visit_deps` into single self-recursive `dfs_visit(node, ..., dep_idx, ...)` — `dep_idx < 0` means "visit new node", `>= 0` means "continue iterating deps" |
| 3 | `string.index_of` does not exist | `Error: Undefined identifier: index_of` | Implemented custom `find_in_string(s, needle, start)` via recursive character-by-character search |
| 4 | `map.get(map, key)` on missing key raises runtime error | Runtime crash | Added `map.has(cell, "v")` / `map.has(r, "error")` guards before all `map.get` calls |
| 5 | `let x;` without initializer | `Error: Expected expression` | All `let` declarations given initial values (e.g., `let x = 0`) |
| 6 | `string.concat(a, b, c)` with 3 args | `Error: Expected 2 arguments` | Changed to `a + b + c` using `+` operator for string concatenation |
| 7 | `-5` tokenized as negative number literal (confuses parser) | Wrong evaluation | Removed negative-number tokenizer hack; handle unary minus in evaluator |
| 8 | Semicolons required by formatter | `ail fmt --check` errors | Added semicolons to all expression statements |

### Root Cause Summary

All issues are **language characteristics** of AILang v0.1.2, not compiler bugs:
- No `while`/`for` loops — AILang is recursion-only
- No forward references — functions must be defined before use
- `map.get` on missing key raises an error (no safe-get pattern)
- `string.concat` takes exactly 2 arguments
- `string.index_of` is not in the standard library
- `let` requires an initializer expression

---

## R2 — First Successful Compile (RUNTIME FAIL)

### Runtime Error: "list index out of range"

**Symptoms:** All simple arithmetic tests, cell reference tests, and comparison tests pass. Chained formulas test crashes.

**Root Cause:** Typo `i - 1` instead of `i + 1` in `eval_topo_order`:
```ail
return eval_topo_order(topo_result, i - 1, workbook)  // wrong
```
Since AILang supports negative list indexing, `i` became negative and wrapped around, creating an infinite loop that eventually exceeded the list bounds.

**Debugging approach:** Added `print` debug statements at key points revealed the decreasing `i` pattern (`0 → -1 → -2 → -3`), confirming the typo.

---

## R3 — All Tests Pass (RUNTIME PASS)

**Fix:** Changed `i - 1` to `i + 1` on line 910 of `eval_topo_order`.

**Result:** All 31 tests pass, demo workbook displays correctly.

---

## Key Constraints Discovered

| Constraint | Impact | Workaround |
|-----------|--------|------------|
| No `while`/`for` loops | All iteration must be recursive | Every loop becomes a tail-recursive helper function |
| No forward references | Functions in dependency order | Define callees before callers; merge mutual recursion into single function |
| No mutual recursion | DFS cycle detection cannot use two-function pattern | Single `dfs_visit` with mode-flag parameter (`dep_idx`) |
| `map.get` on missing key raises error | Must check existence first | `map.has(map, key)` before every `map.get` |
| `string.index_of` missing | Cannot find substring position | Custom `find_in_string` via recursive char-by-char |
| `string.concat` takes only 2 args | Cannot concatenate 3+ strings in one call | Use `+` operator: `"a" + "b" + "c"` |
| `let` needs initializer | Cannot declare uninitialized variable | Always provide initial value (e.g., `let x = 0`) |
| Shared global scope for all named variables | Naming collisions between functions | Use unique names for loop indices and accumulators across all functions |
| Negative list indexing supported | `list.get(list, -1)` returns last element | Not a bug but unexpected for index variables; must ensure indices are always non-negative |

---

## Metrics

| Metric | Value |
|--------|-------|
| Total Lines | 1325 |
| Code Lines (non-empty, non-comment) | 1087 |
| Functions | 85 |
| Test Functions | 10 |
| Test Cases | 31 |
| Modules Used | 6 (`string`, `list`, `map`, `convert`, `json`, `io`) |
| Compile Iterations | 2 |
| Runtime Iterations | 2 |
| Total Revisions | 3 |
| Development Time | ~90 minutes |

---

## Cumulative Issue Registry

| Issue | Classification |
|-------|---------------|
| No `while` loops | Language Characteristic |
| No forward references | Language Characteristic |
| No mutual recursion | Language Characteristic |
| `map.get` raises on missing key | Language Characteristic |
| `string.index_of` missing | Stdlib Gap |
| `string.concat` 2-arg limit | Language Characteristic |
| `let` requires initializer | Language Characteristic |
| Semicolons required by formatter | Formatter Requirement |
| Shared global variable scope | Language Characteristic |
| `i - 1` typo | Developer Error |
