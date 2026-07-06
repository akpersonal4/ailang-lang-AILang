# Evolution Feedback — Cross-Benchmark Comparison

## Benchmarks Compared

| # | Application | Lines | Functions | Domain |
|---|-------------|-------|-----------|--------|
| B1 | Library Management | 943 | — | Data management |
| B2 | Note Taking Application | 346 | 39 | Data management |
| B3 | Calendar Application | 492 | 59 | Scheduling |
| B4 | Markdown to HTML Converter | 518 | 38 | Text processing |
| B5 | HTTP Request Parser (this) | 405 | 38 | Text / protocol parsing |

---

## Cross-Benchmark Issue Count

### Issues Reported in 5 of 5 Benchmarks

| Issue | B1 | B2 | B3 | B4 | B5 | Count |
|-------|:--:|:--:|:--:|:--:|:--:|:-----:|
| **No forward references**: functions must be in dependency order | ✅ | ✅ | ✅ | ✅ | ✅ | **5/5** |
| **No loops**: recursion-only iteration adds boilerplate | ✅ | ✅ | ✅ | ✅ | ✅ | **5/5** |

### Issues Reported in 4 of 5 Benchmarks

| Issue | B1 | B2 | B3 | B4 | B5 | Count |
|-------|:--:|:--:|:--:|:--:|:--:|:-----:|
| **Formatter bug**: `ail fmt` reports "Expected SEMICOLON" on valid code | ✅ | ✅ | ✅ | ✅ | — | **4/5** |
| **`print()` always adds newline**: formatted inline output impossible | — | ✅ | ✅ | ✅ | — | **3/5** |

### Issues Reported in 3 of 5 Benchmarks

| Issue | B1 | B2 | B3 | B4 | B5 | Count |
|-------|:--:|:--:|:--:|:--:|:--:|:-----:|
| **Poor diagnostics**: no line numbers in errors | ✅ | ✅ | — | ✅ | — | **3/5** |
| **No sort in stdlib** | — | — | ✅ | ✅ | — | **2/5** |

---

## What Got Better / Worse

### What Got Better

1. **Standard library coverage**: No missing stdlib functions were encountered in this benchmark. The `string`, `list`, `map`, and `convert` modules covered all HTTP parsing needs. This is an improvement over B4 (Markdown), which needed 5 missing stdlib functions.

2. **Compiler diagnostic quality**: Error messages for "Undefined identifier" were clear and consistent. While still lacking line numbers, the error text was precise enough to identify the offending function.

3. **No formatter bug encountered**: The `ail fmt` "Expected SEMICOLON" issue was not triggered during this benchmark (the HTTP parser's syntax is simpler than Markdown's deeply nested conditionals).

### What Got Worse

1. **Most severe runtime bug discovered yet**: The variable scoping bug in `_set_local` is more fundamental than any previously discovered runtime bug. In B2 (Note Taking), the runtime bug was a type mismatch (`list.len` on a bool). In B5, the bug is in the interpreter's variable scoping mechanism itself — it affects every AILang program that uses `let` with the same variable name across different functions.

2. **User error frequency**: B5 had 1 user error (orphaned code from edit tool). B4 also had 1 user error. This is a pattern — the no-forward-references constraint combined with iterative editing creates cleanup problems.

3. **Compiler iterations increased**: B5 required 5 compiler iterations (up from 4 in B4, 3 in B3). All were caused by forward reference errors or cleanup of orphaned code. While the core issue (no forward references) is unchanged, the edit tool's behavior added extra iterations.

---

## New Issues Discovered in Benchmark #5

1. **Runtime bug: `_set_local` uses `assign` instead of `define`** — The interpreter's `_set_local` method calls `environment.assign()` for `let` variable declarations. This traverses the parent scope chain and can overwrite variables in enclosing scopes (including global scope). When different functions use `let` with the same variable name (e.g., `result`), the second function's `let` declaration overwrites the first function's variable in global scope, causing type errors when the overwritten variable changes type (e.g., from map to list).

2. **Orphaned code from edit tool** — Multiple edit passes in this benchmark left duplicate function bodies that the compiler rejected. This highlights a workflow problem: when the edit tool rewrites large files, it can leave remnants of old code. Three cleanup passes were needed to fully resolve.

---

## Trends in Issue Categories

| Category | B1 | B2 | B3 | B4 | B5 | Trend |
|----------|:--:|:--:|:--:|:--:|:--:|-------|
| Compiler Bug | 0 | 0 | 1 | 0 | 0 | Stable — only 1 ever found (B3 parser crash on nested if) |
| Runtime Bug | 0 | 1 | 0 | 0 | 1 | Recurring — 2 out of 5 benchmarks have runtime bugs |
| Language Limitation | 1 | 0 | 1 | 2 | 2 | Increasing — text processing reveals more limitations |
| Missing Stdlib | 0 | 1 | 1 | 1 | 0 | Variable — depends on domain |
| Documentation Gap | 1 | 0 | 0 | 0 | 0 | Only B1 had documentation issues |
| Poor Diagnostic | 0 | 0 | 0 | 1 | 0 | Rare — only B4 found poor diagnostics |
| User Error | 0 | 0 | 0 | 1 | 1 | Emerging pattern — edit tool workflow issues |

**Observation**: Language Limitations are the most common and most persistent issue category (5 total across all benchmarks). Runtime Bugs and User Errors are tied for second (2 each). The increasing Language Limitation count reflects that text processing domains (B4, B5) stress the language more than data management (B1, B2).

---

## Recommendations for Language Improvement

### Priority 1: Fix the variable scoping bug in `_set_local`

**Severity: Critical** — This bug affects every AILang program.

The `_set_local` method in `compiler/runtime/interpreter.py` must be split into two operations:
- **`_define_local`** — called for `let` declarations; uses `environment.define()` to create a new variable in the current scope
- **`_assign_local`** — called for `=` reassignments; uses `environment.assign()` to traverse the scope chain and update an existing variable

Without this fix, any AILang program that uses the same variable name across different functions will silently corrupt its global scope, leading to unpredictable type errors.

### Priority 2: Add forward reference support

**Severity: High** — Forward reference errors caused 5 of 5 compiler iterations in this benchmark.

Options:
- **Multi-pass compilation**: Allow functions to reference functions defined later in the file
- **Module-level dependency ordering**: Provide a mechanism to declare dependency order explicitly (e.g., `// @level: 0` annotations)
- **Auto-ordering**: Have the compiler resolve the call graph and reorder functions automatically

The current approach of manual dependency ordering is error-prone and wastes developer time on structural reorganization rather than logic.

### Priority 3: Add loop constructs

**Severity: Medium** — Every benchmark has requested this.

While recursion is functional, string/text processing would benefit significantly from:
- `while` loops for character-by-character scanning
- `for` loops for iterating over lists/maps

This would eliminate the "recursive helper + wrapper" pattern that adds ~30% boilerplate to every iteration-heavy function.

### Priority 4: Improve edit tool reliability

**Severity: Low-Medium** — Two consecutive benchmarks had user errors from orphaned code.

When the edit tool rewrites large functions, it should ensure old function bodies are fully replaced, not partially duplicated. Consider a diff-based approach that verifies no duplicate declarations remain after edits.

---

## Impact of the Runtime Bug Discovery

The `_set_local` bug is the most significant issue found across all 5 benchmarks because:

1. **It is a language implementation defect, not a missing feature** — Previous issues were about what AILang lacks (no loops, no forward refs, no regex). This bug is about something that is documented as working (`let` declarations) but actually behaves incorrectly.

2. **It affects ALL programs** — Any AILang program using `let` with common variable names across functions is vulnerable. This includes the 21 existing benchmark apps in `AI_BENCHMARK_MATRIX.md`.

3. **It produces confusing error messages** — The symptom (`map.set` on a list) does not point to the root cause. The error happens far from the actual bug (in a different function's `let` declaration), making debugging extremely difficult.

4. **The fix is straightforward** — Splitting `_set_local` into `_define_local` and `_assign_local` is a simple change with no regressions (all 512 tests pass after the fix).

5. **Urgency** — Before this benchmark, AILang's runtime could be considered stable. This bug undermines that confidence and should be fixed before any production use.
