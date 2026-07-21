# Development Log — Mini SQL Engine

## Application

- Name: Mini SQL Engine
- Location: `apps/mini_sql/main.ail`
- Lines of Code: 839
- Functions: 67
- Modules Used: 8 (`string`, `list`, `map`, `convert`, `csv`, `file`, `io`, `json`)

---

## Iteration Log

### Iteration 1 — First Compile (forward reference failure)

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Unexpected character: :`, `Return statement requires an expression`, `Undefined identifier: tokenize_helper` (and ~30 others) |
| Cause | Three issues: (1) label syntax `while_dummy:` not supported, (2) empty `return;` statements need a value, (3) mutual recursion between `tokenize_helper` and token-type functions (string/number/identifier) violated callee-before-caller requirement |
| Fix | Removed labels, replaced `return;` with `return 0`, rewrote tokenizer to avoid mutual recursion |
| Time | 8 min |
| Classification | Language Limitation |

### Iteration 2 — Second Compile (while/continue not supported)

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Undefined identifier: while` (and ~12 `continue` errors) |
| Cause | Replaced mutual recursion with `while` loops and `continue`, but AILang has no loop keywords |
| Fix | Rewrote tokenizer using pure recursion: `tokenize_step` dispatches by character, `collect_digits`/`collect_alphanum` are pure recursive collectors that don't call back to the main loop |
| Time | 5 min |
| Classification | Language Limitation |

### Iteration 3 — Third Compile

| Field | Value |
|-------|-------|
| Status | **PASS** |
| Error | (none) |
| Cause | — |
| Fix | — |
| Time | 0 min |
| Classification | — |

### Iteration 4 — First Runtime (column key mismatch)

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Runtime error: 'columns'` |
| Cause | `parse_column_list_helper` returned via `make_result` which stores under key `"query"`, but `parse_select` read key `"columns"`. AILang `map.get` throws `KeyError` on missing key. |
| Fix | Added `make_col_result` function that stores under key `"columns"` |
| Time | 2 min |
| Classification | Developer Error |

### Iteration 5 — Second Runtime (file path handling)

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | Runtime error from `list.get(args, 1)` with off-by-one arg indexing |
| Cause | Main function used `args[1]` as the first argument instead of `args[0]` |
| Fix | Changed to `args[0]` for first arg, `args[1]` for second arg |
| Time | 1 min |
| Classification | Developer Error |

### Iteration 6 — Third Runtime (SELECT * expansion)

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | Displayed `*` as header and `NULL` for all rows; then `string.concat` error with 3 args |
| Cause | Two issues: (1) `sel_cols = ["*"]` was not expanded to actual table columns before projection, (2) `string.concat("(", count, ")")` passed 3 arguments but `concat` only takes 2 |
| Fix | Added `resolve_columns` to expand `*` to uppercase table columns; nested `concat("(", concat(count, " rows)"))` |
| Time | 3 min |
| Classification | Developer Error |

### Iteration 7 — Fourth Runtime (ORDER BY column case)

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `Runtime error: 'age'` — map key not found |
| Cause | `order_by` column name was stored in original query casing (lowercase) but table columns are uppercase |
| Fix | Normalized `order_by` to uppercase via `to_upper` in `parse_select`; also normalized projected column names to uppercase in `project_row` and `resolve_columns` |
| Time | 2 min |
| Classification | Developer Error |

### Iteration 8 — Fifth Runtime (DISTINCT ordering)

| Field | Value |
|-------|-------|
| Status | **PASS after fix** |
| Error | `SELECT DISTINCT city` returned 8 rows (not deduplicated) |
| Cause | DISTINCT was applied BEFORE column projection, so it operated on full rows where every row was unique |
| Fix | Moved projection before DISTINCT in `execute_query` so DISTINCT sees only the selected columns |
| Time | 2 min |
| Classification | Developer Error |

### Iteration 9 — Sixth Runtime (COUNT with WHERE)

| Field | Value |
|-------|-------|
| Status | **FAIL** |
| Error | `list index out of range` during `resolve_columns` with empty `sel_cols` |
| Cause | `if (list.len(sel_cols) == 1 && string.equals(list.get(sel_cols, 0), "*"))` crashed because AILang's `&&` does NOT short-circuit — both operands are always evaluated, so `list.get([], 0)` threw out-of-range |
| Fix | Replaced `&&` with nested `if` statements throughout the codebase (5 locations) |
| Time | 10 min |
| Classification | Language Quirk |

---

## Summary

| Metric | Result |
|--------|--------|
| Iterations to first compile | 3 |
| Iterations to first working output | 9 |
| Total revisions | 9 |
| Language limitations encountered | 3 (no loops, no forward references, no short-circuit `&&`) |
| Developer errors | 5 (key naming, arg indexing, column expansion, case, ordering) |
