# Benchmark 009 — Spreadsheet Formula Engine

**Date:** 2026-07-05  
**Benchmark:** #009 — Spreadsheet Formula Engine  
**Language:** AILang v0.1.2  
**Evaluator:** Independent Senior Software Engineer

---

## Application Summary

| Metric | Value |
|--------|-------|
| **Lines of Code** | 1325 |
| **Code Lines (non-empty, non-comment)** | 1087 |
| **Functions** | 85 |
| **Modules Used** | 6 (`string`, `list`, `map`, `convert`, `json`, `io`) |
| **Algorithm** | Recursive-descent expression parser + dependency graph with DFS cycle detection + topological sort |
| **Recursion Depth** | ≤ token count per formula (typically 3-10) |
| **Test Coverage** | 31 test cases across 10 test suites |
| **Execution Time** | ~2-5 seconds |

### Features Implemented

- Tokenizer: numbers, operators, cell references (A1–ZZ999), string literals, parentheses, colon ranges, comma separators, function names
- Recursive-descent expression parser with operator precedence (PEMDAS), parentheses, function calls, unary minus
- Reference resolver: cell reference → row/col coordinates, range parsing for SUM/AVG/MIN/MAX/COUNT
- Dependency graph: extracts all cell references from formula tokens, builds adjacency list
- Cycle detection: DFS-based with 3-color marking (white/gray/black), detects circular dependencies
- Topological sort: produces dependency-ordered evaluation sequence
- Formula evaluation: ordered evaluation of all formula cells
- Function library: SUM, AVG, MIN, MAX, COUNT, IF
- Comparisons: `==`, `!=`, `<`, `>`, `<=`, `>=` (produce integer 0/1)
- Error propagation: `#DIV/0!`, `#REF!`, `#CIRC!`, `#VALUE!` propagate through dependent formulas
- Workbook: 2D grid (list of maps), cell metadata (type, value, formula text)

---

## Development Metrics

| Event | Result |
|-------|--------|
| **First Compile** | **FAIL** — 8 language compatibility issues |
| **Final Compile** | **PASS** (revision 2) |
| **First Runtime** | **FAIL** — "list index out of range" (typo `i - 1` → `i + 1`) |
| **Final Runtime** | **PASS** (revision 3) |
| **Total Revisions** | 3 |
| **Development Time** | ~90 minutes |

### Revision Breakdown

| Iteration | Type | Result | Description |
|:---------:|------|--------|-------------|
| R1 | Compile | FAIL | 8 issues: no `while` loops (replaced with recursion), no mutual recursion in DFS (merged into single self-recursive function), no `string.index_of` (implemented custom `find_in_string`), `map.get` on missing key raises error (added `map.has` guards), `let` needs initializer (added default values), `string.concat` 2-arg limit (used `+`), negative number tokenization hack (handled unary minus in evaluator), semicolons required by formatter (added) |
| R2 | Compile | PASS | All fixes applied; runtime fails with "list index out of range" in chained formulas test |
| R3 | Runtime | PASS | Fixed `i - 1` → `i + 1` typo in `eval_topo_order`; all 31 tests pass |

---

## Revision Analysis

### R1 — Language Compatibility Issues

**8 issues discovered during first compile attempt:**

1. **No `while` loops.** AILang does not support `while` or `for` loops. All iteration must use recursion. Initial implementation used `while` for tokenizer loops and formula parsing. **Fix:** Replaced every `while` with a tail-recursive helper function.

2. **No mutual recursion.** DFS cycle detection naturally uses two mutually recursive functions (`dfs_visit_node` and `dfs_visit_deps`). AILang's no-forward-reference rule prevents mutual recursion. **Fix:** Merged into a single `dfs_visit(node, graph, state, order, node_set, dep_idx, deps_list)` function where `dep_idx < 0` means "visit a new node" and `dep_idx >= 0` means "continue iterating the current node's dependency list."

3. **`string.index_of` does not exist.** The standard library lacks `index_of` or `find` for strings. **Fix:** Implemented `find_in_string(s, needle, start)` via recursive character-by-character search using `string.substring`.

4. **`map.get` on missing key raises runtime error.** Unlike `map.get` in most languages that returns `None`/`null` for missing keys, AILang's `map.get` raises an error. **Fix:** Added `map.has(map, key)` guards before all `map.get` calls (e.g., `map.has(cell, "v")`, `map.has(r, "error")`).

5. **`let` requires an initializer.** `let x;` is not valid; every `let` declaration must include an expression. **Fix:** Added initial values (e.g., `let col = 0`, `let row_str = ""`).

6. **`string.concat(a, b, c)` with 3 arguments.** `string.concat` takes exactly 2 arguments. **Fix:** Used `+` operator: `"a" + "b" + "c"`.

7. **Negative number tokenization.** Initial approach tokenized `-5` as a single NUMBER token with value -5, which conflicted with the subtraction operator. **Fix:** `-` is always tokenized as OPERATOR(`-`); unary minus is handled in the evaluator (`eval_full` checks for `-` at the start of an expression or after an operator/left-paren).

8. **Semicolons required by formatter.** `ail fmt --check` requires semicolons after all expression statements. **Fix:** Added semicolons throughout.

### R2 — First Successful Compile

All 8 issues resolved. File compiles successfully.

### R3 — Runtime Error: "list index out of range"

**Error:** `Runtime error: list index out of range` during `test_chained_formulas`.

**Debugging:** Added `print` debug statements revealed that the `eval_topo_order` recursion index was decreasing instead of increasing:
```
eval_topo_order i=0  → processes "0,1"
eval_topo_order i=-1 → processes "0,2"
eval_topo_order i=-2 → processes "0,1" again (infinite loop)
eval_topo_order i=-3 → crash
```

**Root Cause:** Typo on line 910:
```ail
return eval_topo_order(topo_result, i - 1, workbook)  // BUG: should be i + 1
```

Since AILang supports negative list indexing (`list.get(list, -1)` returns the last element), the decreasing index wrapped around and re-processed cells indefinitely until the recursion stack/list index went out of range.

**Fix:** Changed `i - 1` to `i + 1`.

---

## Language Evaluation

| Category | Rating (1–10) | Notes |
|----------|:-------------:|-------|
| **Documentation** | 6 | LANGUAGE_SPEC.md and STDLIB_REFERENCE.md are generally clear but missing critical details: no mention that `map.get` raises on missing key, no mention of `while`/`for` loop absence in the syntax reference, no mention of the `let` initializer requirement, no mention of semicolon requirements for the formatter. These were all discovered through trial and error. |
| **Compiler** | 7 | Fast compilation, clear error messages for missing identifiers. However, `ail fmt` rejects valid code (compiles and runs correctly) due to strict semicolon requirements. |
| **Runtime** | 7 | Correct execution for all 31 test cases. Numeric operations are accurate. The global variable scoping (shared `i` variable between functions) is a concerning design choice that could cause subtle bugs. |
| **Standard Library** | 6 | `list`, `map`, `convert`, `string`, `json`, `io` all work. Major gaps: no `string.index_of`, no `string.split`, no `list.set`, no safe `map.get` with default, no `while`/`for` in the language spec. The `string.substring` start/end semantics are correct. |
| **Formula Engine Implementation** | 7 | Feasible and produces correct results. The no-loop constraint adds significant boilerplate (85 functions for a formula engine that would be ~300-400 LOC in Python). The global variable scoping is the most concerning issue — naming collisions between function parameters and `let` bindings across different functions could produce hard-to-debug bugs. |
| **AI Friendliness** | 6 | Syntax is simple and predictable. However, the many implicit rules (no `while`, no mutual recursion, `map.get` raises, `let` needs initializer, semicolons for formatter) make it difficult to produce correct code on the first attempt. Multiple iteration rounds are expected. |

### Overall: 6.5 / 10

---

## Comparison with Previous Benchmarks

| Application | LOC | Functions | Modules | Compile Iterations | Runtime Iterations | Total Revisions | Dev Time |
|-------------|:---:|:---------:|:-------:|:------------------:|:-----------------:|:---------------:|:--------:|
| Library Management (B1) | 819 | 107 | 9 | 3 | 1 | 3 | ~45 min |
| Note Taking (B2) | 346 | 39 | 7 | 1 | 1 | 1 | — |
| Calendar (B3) | 492 | 59 | 7 | 3 | 1 | — | — |
| Markdown Parser (B4) | 518 | 38 | 5 | 4 | 2 | 6 | ~40 min |
| HTTP Request Parser (B5) | 405 | 38 | 4 | 5 | 2 | 7 | ~36 min |
| Mini SQL Engine (B6) | 839 | 67 | 8 | 3 | 6 | 9 | ~48 min |
| Hotel Management (B7) | — | — | — | — | — | — | — |
| Sudoku Solver (B8) | 356 | 45 | 5 | 2 | 2 | 4 | ~60 min |
| **Spreadsheet Engine (B9)** | **1325** | **85** | **6** | **2** | **2** | **3** | **~90 min** |

### Key Findings

#### New Findings (B9 — Spreadsheet Formula Engine)

1. **`map.get` on missing key raises an error.** This is different from most languages where `map.get` returns `None`/`null`/`undefined` for missing keys. AILang raises a runtime error. **Workaround:** Always use `map.has(map, key)` before `map.get`.

2. **Global variable scoping for `let` bindings.** Variables declared with `let` appear to share a single global scope. A variable named `i` in one function can be overwritten by a `let i` in another function. This means naming collisions between functions can cause incorrect behavior. **Workaround:** Use unique variable names across all functions, or avoid reusing common names like `i` for loop indices.

3. **`string.index_of` is missing from the standard library.** While the existence of `string.indexOf` was assumed based on the naming convention of other standard library functions, it does not exist. **Workaround:** Implement custom substring search via recursion and `string.substring`.

4. **Tokenizer numeric literal sensitivity.** AILang's tokenizer treats `-` followed by a digit as an operator followed by a positive number, not as a negative number literal. This is correct behavior for expression parsing but requires the evaluator to handle unary minus explicitly.

5. **Largest benchmark to date.** At 1325 LOC and 85 functions, this is the most complex AILang application built so far. It validates that AILang can handle multi-module, algorithmically complex applications.

#### Previously Confirmed Findings (Replicated by B9)

| Finding | Previously | B9 Confirms |
|---------|:----------:|:-----------:|
| No forward references — functions in dependency order | 7/7 benchmarks | ✅ (R1 fixes) |
| No loops — recursion only | 7/7 benchmarks | ✅ (all iteration via recursion) |
| `string.concat` 2-arg limit | 2/7 benchmarks | ✅ (used `+` for chaining) |
| `print()` always adds newline | 4/7 benchmarks | ✅ (built strings for display) |
| Poor diagnostics (no line numbers on runtime errors) | 5/7 benchmarks | ✅ (error had no line number) |

#### Regressions

No regressions observed.

---

## Cumulative Evidence Table

| Issue | Category | Evidence | B1 | B2 | B3 | B4 | B5 | B6 | B8 | B9 |
|-------|----------|:--------:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **No forward references** | Language Characteristic | **8/8** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **No loops (recursion-only)** | Language Characteristic | **8/8** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Formatter bug (`ail fmt` SEMICOLON)** | **Formatter Bug** | 6/8 | ✅ | ✅ | ✅ | ✅ | ✅ | — | — | ✅ |
| **Poor diagnostics (no line numbers)** | Poor Diagnostic | 5/8 | ✅ | ✅ | — | ✅ | — | ✅ | — | ✅ |
| **No sort in stdlib** | Stdlib Gap | 3/8 | — | — | ✅ | ✅ | — | ✅ | — | — |
| **`print()` always adds newline** | Language Characteristic | **5/8** | — | ✅ | ✅ | ✅ | — | — | ✅ | ✅ |
| **`string.split()` missing** | Stdlib Gap | 2/8 | — | — | — | ✅ | — | ✅ | — | — |
| **`string.find()` / `string.index_of` missing** | Stdlib Gap | **3/8** | — | — | — | ✅ | — | ✅ | — | ✅ |
| **`string.join()` missing** | Stdlib Gap | 2/8 | — | — | ✅ | ✅ | — | — | — | — |
| **No short-circuit `&&`/`\|\|`** | Language Characteristic | 3/8 | — | — | — | — | — | ✅ | ✅ | ✅ |
| **`string.concat` 2-arg limit** | Language Characteristic | **3/8** | — | — | — | ✅ | — | ✅ | — | ✅ |
| **Variable scoping bug (`let` leaks)** | **Runtime Bug** | **2/8** | — | — | — | — | ✅ | — | — | ✅ |
| **No `None`/`null` literal** | Stdlib Gap | 1/8 | — | — | — | — | — | ✅ | — | — |
| **No `try`/`catch`** | Language Characteristic | 1/8 | — | — | — | — | — | ✅ | — | — |
| **No mutual recursion support** | Language Characteristic | 2/8 | — | — | — | — | — | — | ✅ | ✅ |
| **No `list.set()` for in-place mutation** | Stdlib Gap | 1/8 | — | — | — | — | — | — | ✅ | — |
| **Poor algorithmic performance** | Runtime Characteristic | 1/8 | — | — | — | — | — | — | ✅ | — |
| **`map.get` raises on missing key** | **Runtime Characteristic** | **1/8 (NEW)** | — | — | — | — | — | — | — | ✅ |

### Legend

- ✅ = Issue confirmed for this benchmark
- — = Not applicable / not tested / not encountered

---

## Developer Error vs. Language Limitation Analysis

| Issue | Classification |
|-------|---------------|
| `i - 1` typo in `eval_topo_order` | Developer Error (simple typo) |
| No `while` loops | Language Characteristic |
| No mutual recursion | Language Characteristic |
| `map.get` raises on missing key | Language Characteristic (dangerous default) |
| `string.index_of` missing | Stdlib Gap |
| `string.concat` 2-arg limit | Language Characteristic |
| `let` requires initializer | Language Characteristic |
| Shared global variable scope | Runtime Characteristic (dangerous) |
| Semicolons required by formatter | Formatter Limitation |

- **Total Developer Errors:** 1 (R3 — `i - 1` typo)
- **Total Language Limitations:** 6 (no while, no mutual recursion, `map.get` raises, `string.concat` limit, `let` needs initializer, global scope)
- **Total Stdlib Gaps:** 1 (no `string.index_of`)
- **Total Formatter Limitations:** 1 (semicolons required)
- **Total Compiler Bugs:** 0
- **Total Runtime Bugs:** 1 (global variable scoping — `let` bindings leak across functions)

---

## Conclusion

**"Can AILang reliably implement a spreadsheet formula engine suitable for production software?"**

### Answer: YES — With caveats.

### Reasons

1. **The engine is correct.** All 31 test cases pass, covering arithmetic, cell references, chained formulas, range functions (SUM/AVG/MIN/MAX/COUNT), conditional logic (IF), comparisons, circular dependency detection, error propagation, and nested expressions.

2. **Performance is adequate for typical spreadsheet workloads.** Unlike algorithmic workloads (Sudoku solver ~30-60s), formula evaluation uses shallow recursion (3-10 frames per formula) and completes in seconds for moderate-sized workbooks.

3. **The global variable scoping is a real risk.** Sharing variable names between function parameters and `let` bindings across different functions can cause incorrect behavior. This is the most concerning issue discovered — it's not just a documentation gap but a runtime behavior that could produce hard-to-debug bugs in larger codebases.

4. **`map.get` on missing keys is error-prone.** Every `map.get` call must be guarded by `map.has`, adding verbosity and opportunities for runtime crashes if a guard is missed.

5. **No sort in stdlib is not a problem here** (topological sort was implemented manually via DFS), but `string.index_of` being missing forced a custom implementation.

### What Works Well

- Recursive-descent parsing works naturally with AILang's recursion-only approach
- Map/list data structures are suitable for spreadsheet cell storage
- The dependency graph and cycle detection work correctly
- Formula ordering via topological sort is correct
- Error propagation cascades properly through the evaluation chain

### Final Verdict

AILang can **correctly** implement a spreadsheet formula engine. The 85-function, 1325-line implementation passes all 31 tests. The main concerns are: (1) the global variable scoping issue (`let` bindings leak across functions) which could produce subtle bugs, and (2) the `map.get`-on-missing-key behavior which requires defensive guards.

**Rating for formula engine implementation: 7/10** (correct but verbose; global scoping is a concern)
**Rating for business applications: 7/10** (adequate for similar data-processing workloads)
