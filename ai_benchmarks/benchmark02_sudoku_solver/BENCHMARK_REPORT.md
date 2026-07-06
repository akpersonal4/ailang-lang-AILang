# Benchmark 008 — Sudoku Solver

**Date:** 2026-07-05  
**Benchmark:** #008 — Sudoku Solver  
**Language:** AILang v0.1.2  
**Evaluator:** Independent Senior Software Engineer

---

## Application Summary

| Metric | Value |
|--------|-------|
| **Lines of Code** | 356 |
| **Functions** | 45 |
| **Modules Used** | 5 (`list`, `map`, `convert`, `set`, `json`) |
| **Algorithm** | Recursive Backtracking with Constraint Checking |
| **Recursion Depth** | ≤ 81 (one frame per cell) + backtracking |
| **Maximum Backtracking Steps** | Thousands (puzzle-dependent, bounded by 9^81) |
| **Execution Time** | ~30-60 seconds for standard Wikipedia puzzle |

### Features Implemented

- 9x9 board creation (list of 9 maps with integer keys)
- Puzzle loading from JSON strings
- Puzzle validation (detect duplicate givens)
- Recursive backtracking solver
- Unsolvable puzzle detection
- Pretty-printing (standard Sudoku grid format)
- Final solution verification (rows, columns, boxes contain 1-9)

---

## Development Metrics

| Event | Result |
|-------|--------|
| **First Compile** | **FAIL** — forward reference errors |
| **Final Compile** | **PASS** (revision 2) |
| **First Runtime** | **FAIL** — timeout (map string-key overhead) |
| **Final Runtime** | **PASS** (revision 4) |
| **Total Revisions** | 4 |
| **Development Time** | ~60 minutes |

### Revision Breakdown

| Iteration | Type | Result | Description |
|:---------:|------|--------|-------------|
| R1 | Compile | FAIL | Forward references: `init_board` called before definition; mutual recursion between `solve` and `try_number` |
| R2 | Compile | PASS | Reordered `init_board` before `create_board`; merged `solve`/`try_number` into single `solve_recursive` function |
| R3 | Runtime | FAIL | Timeout: map with string keys (`convert.to_string(row) + "," + convert.to_string(col)`) caused extreme overhead for 27 cell accesses per constraint check |
| R4 | Runtime | PASS | Changed board from flat map to list-of-maps with integer keys; removed all `convert.to_string` calls; added `validate_puzzle`, fixed unsolvable test data |

---

## Revision Analysis

### R1 — Forward Reference Errors

**Error:** `Error: Undefined identifier: init_board`, `Error: Undefined identifier: solve`

**Root Cause:** AILang requires functions to be defined before they are called (no forward references). Two issues:
1. `create_board()` called `init_board()` which was defined later
2. `solve()` and `try_number()` had mutual recursion — neither could be defined before the other

**Fix:**
1. Reordered `init_board` before `create_board`
2. Eliminated mutual recursion by merging `solve()` and `try_number()` into a single recursive function `solve_recursive(board, pos, num)` that handles both "find next empty cell" and "try numbers 1-9" in one recursion

**Classification:** Language Characteristic (no forward references; no mutual recursion support)

---

### R2 — First Successful Compile

No errors. All functions defined in dependency order. Single recursion avoids mutual dependency.

**Classification:** N/A (success)

---

### R3 — Runtime Timeout

**Error:** Program timed out after 120 seconds with no output.

**Root Cause:** The initial board used a flat `map` with string keys like `"0,0"`, `"0,1"` built via `convert.to_string(row) + "," + convert.to_string(col)`. Each `get_cell` required:
1. Two `convert.to_string()` Python calls
2. Two string concatenations via `+`
3. One `map.get()` call

Each `is_valid()` call performed 27 `get_cell` calls (9 for row + 9 for col + 9 for box). With 51 empty cells in the standard puzzle, backtracking required millions of constraint checks, each with expensive string key construction.

**Fix:** Changed board representation from a flat map to `list` of 9 `map`s, each map using **integer keys** (0-8). This eliminated all string operations from the hot path:
- `get_cell`: `map.get(list.get(board, row), col)` — just two index operations, no strings
- `set_cell`: `map.set(list.get(board, row), col, val)` — modifies inner map in-place

**Classification:** Developer Error (poor data structure choice) / Language Characteristic (no list element mutation — must use map for in-place modification)

---

### R4 — Final Successful Runtime

**Changes from R3:**
- Optimized board storage from string-keyed flat map to integer-keyed list-of-maps
- Added `validate_puzzle()` function to check initial givens for duplicates before solving
- Added proper test data: truly unsolvable puzzle (cell with no valid placement), invalid puzzle (duplicate givens)
- All three test cases pass correctly

**Classification:** N/A (success)

---

## Language Evaluation

| Category | Rating (1–10) | Notes |
|----------|:-------------:|-------|
| **Documentation** | 8 | LANGUAGE_SPEC.md, STDLIB_REFERENCE.md, and LANGUAGE_TOUR.md are clear and consistent. Missing: examples of list-of-maps pattern (discovered through reading app code), no mention of mutual recursion limitation. |
| **Compiler** | 8 | Clear error messages, fast compilation. No bugs encountered. Forward reference error was clear and easy to fix. |
| **Runtime** | 6 | Correct execution but very slow for algorithmic workloads. No JIT, no optimization. Python-backed interpreter adds overhead. Map/list operations are O(1) but have Python call overhead. |
| **Standard Library** | 7 | `list`, `map`, `set`, `convert`, `json` all worked as documented. Missing: `list.set(index, value)` for in-place mutation (forced map-based approach). `convert.to_int` works correctly but adds overhead. |
| **Algorithm Implementation** | 5 | **Feasible but constrained.** The no-forward-reference rule forced unnatural restructuring of the solver from mutual recursion (standard backtracking pattern) to a single recursion. The no-loop constraint is manageable but adds verbosity. Performance is unacceptable for production use — solving a standard Sudoku takes ~30-60 seconds vs. milliseconds in any mainstream language. |
| **AI Friendliness** | 7 | Syntax is simple and predictable. The function ordering constraint is the main challenge — AI models must generate code in bottom-up order, which is non-intuitive. The single-recursion workaround for backtracking is non-obvious. |

### Overall: 6.8 / 10

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
| **Sudoku Solver (B8)** | **356** | **45** | **5** | **2** | **2** | **4** | **~60 min** |

### Benchmark Matrix Update

| Application | Category | LOC | Features | Difficulty | First-pass Compile | First-pass Run | Compile Iterations | Runtime Iterations | Final Rating |
|-------------|----------|:---:|----------|:----------:|:------------------:|:--------------:|:------------------:|:------------------:|:------------:|
| banking_ledger | Data Management | 56 | list, map, time, recursion | M | ✅ | ✅ | 1 | 1 | — |
| bmi_calculator | Utilities | 20 | arithmetic, conditionals | L | ✅ | ✅ | 1 | 1 | — |
| calculator | Utilities | 14 | arithmetic | L | ✅ | ✅ | 1 | 1 | — |
| config_reader | File Processing | 23 | file, string | M | ✅ | ✅ | 1 | 1 | — |
| contact_book | Data Management | 50 | list, map, recursion, search | M | ✅ | ✅ | 1 | 1 | — |
| csv_analyzer | Data Processing | 28 | csv, list, map, convert | M | ✅ | ✅ | 1 | 1 | — |
| employee_management | Business Logic | 43 | list, map, arithmetic | M | ✅ | ✅ | 1 | 1 | — |
| expense_tracker | Data Management | 47 | list, map, time, aggregation | M | ✅ | ✅ | 1 | 1 | — |
| file_copy | File Processing | 27 | file, path, comparison | M | ✅ | ✅ | 1 | 1 | — |
| file_search | File Processing | 28 | file, string | M | ✅ | ✅ | 1 | 1 | — |
| grade_calculator | Utilities | 18 | conditionals | L | ✅ | ✅ | 1 | 1 | — |
| inventory | Data Management | 44 | list, map, multiplication | M | ✅ | ✅ | 1 | 1 | — |
| invoice_generator | Business Logic | 48 | list, map, time, arithmetic | M | ✅ | ✅ | 1 | 1 | — |
| json_formatter | Data Processing | 20 | json, file, path | M | ✅ | ✅ | 1 | 1 | — |
| log_analyzer | File Processing | 10 | file, string | L | ✅ | ✅ | 1 | 1 | — |
| markdown_stats | Text Processing | 21 | string | M | ✅ | ✅ | 1 | 1 | — |
| number_base | Utilities | 59 | convert, recursion, arithmetic | H | ✅ | ✅ | 1 | 1 | — |
| password_generator | Security | 45 | random, list, string | M | ✅ | ✅ | 1 | 1 | — |
| random_data_generator | Utilities | 40 | random, list | M | ✅ | ✅ | 1 | 1 | — |
| scientific_calculator | Utilities | 39 | recursion, math | H | ✅ | ✅ | 1 | 1 | — |
| simple_quiz | Education | 27 | random, conditionals | M | ✅ | ✅ | 1 | 1 | — |
| student_management | Education | 53 | list, map, arithmetic | M | ✅ | ✅ | 1 | 1 | — |
| temperature_converter | Utilities | 15 | arithmetic | L | ✅ | ✅ | 1 | 1 | — |
| text_search | Text Processing | 20 | string | M | ✅ | ✅ | 1 | 1 | — |
| todo_manager | Productivity | 45 | list, map, booleans | M | ✅ | ✅ | 1 | 1 | — |
| unit_converter | Utilities | 14 | arithmetic | L | ✅ | ✅ | 1 | 1 | — |
| word_counter | Text Processing | 12 | string | L | ✅ | ✅ | 1 | 1 | — |
| **sudoku_solver** | **Algorithms** | **356** | **list, map, convert, set, json, recursion, backtracking** | **H** | ❌ | ❌ | **2** | **2** | — |

### Key Findings

#### New Findings (B8 — Sudoku Solver)

1. **Mutual recursion is not supported.** Standard backtracking algorithms use mutual recursion between a "find empty cell" function and a "try numbers" function. AILang's no-forward-reference rule means all functions must be defined before they are called, making mutual recursion impossible. **Workaround:** Merge both functions into a single recursive function that handles both concerns through its parameter list. This is non-obvious and requires restructuring the algorithm significantly.

2. **Performance is a critical limitation for algorithmic workloads.** The Sudoku solver uses 27 `get_cell` operations per constraint check. Initial implementation using string keys (`convert.to_string(row) + "," + convert.to_string(col)`) caused 120-second timeout. Optimization to integer-keyed list-of-maps reduced runtime to ~30-60 seconds, still orders of magnitude slower than any mainstream language. The lack of a JIT compiler or optimized runtime makes AILang unsuitable for compute-intensive algorithms.

3. **`list.set()` is missing from the standard library.** Since lists cannot be modified in-place at arbitrary indices, the solver must wrap each row in a `map` and use `map.set()` for mutation. This adds an extra layer of indirection (and function call overhead) vs. a simple 2D array.

4. **Validator/verifier pattern is verbose.** All row/col/box iteration requires recursive helper functions. Pattern is consistent but adds ~200 LOC of boilerplate validation code.

#### Previously Confirmed Findings (Replicated by B8)

| Finding | Previously | B8 Confirms |
|---------|:----------:|:-----------:|
| No forward references — functions in dependency order | 6/6 benchmarks | ✅ (R1 failure) |
| No loops — recursion only | 6/6 benchmarks | ✅ (45 functions, all recursion) |
| No short-circuit `&&` — use nested `if` | 1/6 benchmarks | ✅ (not triggered but pattern known) |
| No `list.set()` for in-place mutation | — | ✅ (forced map-based storage) |
| `print()` always adds newline | 3/6 benchmarks | ✅ (built string for row printing) |
| Poor diagnostics (no line numbers on runtime errors) | 4/6 benchmarks | ⚠️ Not triggered (no runtime errors) |

#### Regressions

No regressions observed. The compiler and runtime are stable at v0.1.2.

---

## Cumulative Evidence Table

| Issue | Category | Evidence | B1 | B2 | B3 | B4 | B5 | B6 | B8 |
|-------|----------|:--------:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **No forward references** | Language Characteristic | **7/7** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **No loops (recursion-only)** | Language Characteristic | **7/7** | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Formatter bug (`ail fmt` SEMICOLON)** | **Formatter Bug** | 5/7 | ✅ | ✅ | ✅ | ✅ | ✅ | — | — |
| **Poor diagnostics (no line numbers)** | Poor Diagnostic | 4/7 | ✅ | ✅ | — | ✅ | — | ✅ | — |
| **No sort in stdlib** | Stdlib Gap | 3/7 | — | — | ✅ | ✅ | — | ✅ | — |
| **`print()` always adds newline** | Language Characteristic | **4/7** | — | ✅ | ✅ | ✅ | — | — | ✅ |
| **`string.split()` missing** | Stdlib Gap | 2/7 | — | — | — | ✅ | — | ✅ | — |
| **`string.find()` missing** | Stdlib Gap | 2/7 | — | — | — | ✅ | — | ✅ | — |
| **`string.join()` missing** | Stdlib Gap | 2/7 | — | — | ✅ | ✅ | — | — | — |
| **No short-circuit `&&`/`\|\|`** | Language Characteristic | 2/7 | — | — | — | — | — | ✅ | ✅ (known) |
| **Variable scoping bug (`let` leaks)** | **Runtime Bug** | 1/7 | — | — | — | — | ✅ | — | — |
| **No `None`/`null` literal** | Stdlib Gap | 1/7 | — | — | — | — | — | ✅ | — |
| **No `try`/`catch`** | Language Characteristic | 1/7 | — | — | — | — | — | ✅ | — |
| **`string.concat` 2-arg limit** | Language Characteristic | 2/7 | — | — | — | ✅ | — | ✅ | — |
| **No mutual recursion support** | Language Characteristic | **1/7 (NEW)** | — | — | — | — | — | — | ✅ |
| **No `list.set()` for in-place mutation** | Stdlib Gap | **1/7 (NEW)** | — | — | — | — | — | — | ✅ |
| **Poor algorithmic performance** | Runtime Characteristic | **1/7 (NEW)** | — | — | — | — | — | — | ✅ |

### Legend

- ✅ = Issue confirmed for this benchmark
- — = Not applicable / not tested / not encountered

---

## Algorithmic Programming vs. Business Applications

**Finding: AILang handles business applications significantly better than algorithmic programming.**

| Dimension | Business Apps (B1-B7) | Algorithmic (B8 - Sudoku) |
|-----------|----------------------|--------------------------|
| Data modeling | Natural via `map` + `list` | Same but forced map-based 2D array adds overhead |
| CRUD operations | Well-supported by stdlib | N/A |
| File/JSON/CSV I/O | Excellent | N/A (not needed) |
| Recursion depth | Shallow (10-50 frames) | Deep (81+ frames) |
| Performance | Adequate | **Poor** (~60s for standard puzzle) |
| Algorithm structure | Linear/sequential | Requires backtracking — structure impacted by no-forward-ref constraint |
| Code organization | Natural top-down | Must use bottom-up ordering (unnatural for algorithmic logic) |

**The no-forward-reference rule and no-mutual-recursion limitation significantly affect algorithmic programming**, where recursive backtracking is a standard pattern. The single-recursion workaround works but is non-obvious and requires restructuring the algorithm.

**Performance is the critical blocker.** A Sudoku solver that takes 30-60 seconds in AILang would take <10ms in Python, JavaScript, or any compiled language. For production software requiring complex algorithms, AILang's runtime is not competitive.

---

## Classified Issue Registry (B8 Only)

| Issue | Classification |
|-------|---------------|
| Forward reference errors (R1) | Language Characteristic (no forward references) |
| Mutual recursion impossible (R1) | Language Characteristic (no forward references ⇒ no mutual recursion) |
| Map string-key overhead timeout (R3) | Developer Error (poor data structure choice) mitigated by Language Characteristic (no `list.set()`) |
| Slow performance (final) | Runtime Characteristic (interpreted, Python-backed, no JIT) |

- **Total Developer Errors:** 1 (R3 — poor initial data structure)
- **Total Language Limitations:** 2 (no forward references, no `list.set()`)
- **Total Compiler Bugs:** 0
- **Total Runtime Bugs:** 0

---

## Conclusion

**"Can AILang reliably implement recursive backtracking algorithms suitable for production software?"**

### Answer: NO — Not for production use.

### Reasons

1. **Mutual recursion is impossible.** The standard Sudoku solver pattern (mutual recursion between "find empty" and "try numbers") cannot be expressed in AILang due to the no-forward-reference constraint. A single-recursion workaround exists but is non-obvious and requires significant restructuring.

2. **Performance is unacceptable.** ~30-60 seconds for a standard 9x9 Sudoku puzzle. In production, this would be a dealbreaker. The interpreted runtime with Python-backed operations adds too much overhead for compute-intensive algorithmic workloads.

3. **Missing `list.set()` forces contortions.** The board must use a list-of-maps structure (instead of a simple 2D list) because lists cannot be modified in-place at arbitrary indices. This adds indirection and cognitive overhead.

4. **Verbosity is high.** 356 LOC and 45 functions for a problem that would be ~50-100 LOC in a mainstream language. Pure recursion for all iteration adds significant boilerplate.

### What Works

- The algorithm is **correct** — all three test cases pass (solvable, invalid, unsolvable).
- The solution **verification** works correctly (rows, columns, boxes all validated).
- The **constraint checking** is correct (no false positives/negatives).
- The **pretty printing** produces a clean standard Sudoku grid.

### Final Verdict

AILang can **correctly** implement recursive backtracking algorithms, but it **cannot implement them efficiently enough for production use**. The language's design constraints (no forward references, recusion-only iteration, missing `list.set()`) and slow interpreted runtime make it unsuitable for real-world algorithmic software.

**Rating for algorithmic programming: 4/10** (correct but impractical)  
**Rating for business applications: 7/10** (adequate for CRUD, file I/O, data processing)
