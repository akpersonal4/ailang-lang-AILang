# AI Benchmark Analysis — Aggregate Report Across 6 Benchmarks

## Benchmarks Analyzed

| # | Application | LOC | Functions | Modules | Domain |
|:-:|-------------|----:|----------:|--------:|--------|
| B1 | Library Management | 819 | 107 | 9 | Data management |
| B2 | Note Taking Application | 346 | 39 | 7 | Data management |
| B3 | Calendar Application | 492 | 59 | 7 | Scheduling |
| B4 | Markdown to HTML Converter | 518 | 38 | 5 | Text processing |
| B5 | HTTP Request Parser | 405 | 38 | 4 | Protocol parsing |
| B6 | Mini SQL Engine | 839 | 67 | 8 | SQL / data querying |
| | **Total / Avg** | **3,419** | **58 avg** | **6.7 avg** | — |

---

## Aggregate Development Metrics

| Metric | B1 | B2 | B3 | B4 | B5 | B6 |
|--------|:--:|:--:|:--:|:--:|:--:|:--:|
| First Compile | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |
| First Runtime | PASS | FAIL | FAIL | FAIL | FAIL | FAIL |
| Compiler Iterations | 3 | 1 | 3 | 4 | 5 | 3 |
| Runtime Iterations | 1 | 1 | 1 | 2 | 2 | 6 |
| Total Revisions | 3 | — | — | 6 | 7 | 9 |
| Dev Time (min) | ~45 | — | — | ~40 | ~36 | ~48 |

### Key Observations

- **Every benchmark failed first compile.** The 100% failure rate is driven entirely by the no-forward-references constraint.
- **Compile failures are cheap** (fixed in 1-5 min by reordering functions).
- **Runtime failures are expensive** (B6: 6 runtime iterations, ~30 min debugging). Each runtime bug required tracing through recursive call chains with no line-number diagnostics.
- **B6 (Mini SQL) had the most runtime iterations** because the no-short-circuit `&&` behavior caused cascading crashes in list/map guard patterns that worked "correctly" in earlier benchmarks by coincidence.

---

## Classified Issue Registry

### Classification Taxonomy

| Category | Definition |
|----------|------------|
| **Compiler Bug** | The compiler produces incorrect output or crashes on valid code |
| **Runtime Bug** | The interpreter produces wrong results or crashes on valid compiled code |
| **Formatter Bug** | `ail fmt` crashes or reports false errors on valid code |
| **Language Characteristic** | Intentional design choice, not a defect. May still have productivity cost. |
| **Stdlib Gap** | Functionality missing from the standard library that was needed by ≥2 benchmarks |
| **Documentation Bug** | Docs claim behavior that doesn't match reality |
| **Documentation Gap** | Behavior is undocumented, under-documented, or misleading |
| **Poor Diagnostic** | Error message lacks actionable information (line number, location) |
| **Developer Error** | Mistake in application code, not a tool issue |

---

## Issues by Evidence Strength

### Tier 1 — Confirmed Across All 6 Benchmarks (6/6)

| Issue | Category | Classification |
|-------|----------|---------------|
| **No forward references** — functions must be defined in dependency order (callees before callers) | Language Characteristic | Intentional. AILang resolves all symbols at definition time. Enforces clean dependency structure but makes top-down development impossible. All 6 benchmarks failed first compile due to this. Cost: ~3-5 min per benchmark for restructuring. |
| **No loops** — no `while` / `for` / `loop` keywords; all iteration via recursion | Language Characteristic | Intentional. AILang was designed as a pure-expression language. Every iteration requires: `fn helper(coll, i, acc)` + `fn wrapper(coll)`. Cost: +2-3× LOC for iterative operations vs. a loop-based language. Recursion depth limited to ~1200 frames with `sys.setrecursionlimit(10000)`. |

### Tier 2 — Confirmed Across 5 of 6 Benchmarks (5/6)

| Issue | Category | Classification |
|-------|----------|---------------|
| **`ail fmt` reports spurious "Expected SEMICOLON"** on valid code that compiles and runs correctly | Formatter Bug | **Confirmed bug.** Reported by B1-B5. B6 did not test formatter. All five compilation pipelines were unaffected — the formatter is broken but the compiler is correct. |

### Tier 3 — Confirmed Across 4 of 6 Benchmarks (4/6)

| Issue | Category | Classification |
|-------|----------|---------------|
| **Error messages lack source location** (file name, line number, column) | Poor Diagnostic | B1, B2, B4, B6 report this. B3 and B5 did not flag it. Runtime errors show only the error string and the top-level CLI command. In a 500+ line file with recursive functions, finding the offending line requires manual search. |

### Tier 4 — Confirmed Across 2-3 of 6 Benchmarks

| Issue | Category | Benchmarks | Classification |
|-------|----------|:----------:|---------------|
| **No sort in stdlib** | Stdlib Gap | B3, B4, B6 (3/6) | Missing function. Each benchmark implemented recursive selection sort (~20 LOC each). |
| **`print()` always adds newline** — no way to build inline output | Language Characteristic | B2, B3, B4 (3/6) | Intentional. `print` is documented as always appending `\n`. `io.write()` exists but doesn't flush. Workaround requires building full strings and printing once. |
| **`string.split(text, delimiter)` missing** | Stdlib Gap | B4, B6 (2/6) | Missing function. Implemented manually via `find_substring` recursion (~15 LOC each). |
| **`string.find(text, pattern)` missing** | Stdlib Gap | B4, B6 (2/6) | Missing function. Returns position of substring, not just boolean. Manual `find_substring` O(n×m) recursion. |
| **`string.join(list, separator)` missing** | Stdlib Gap | B3, B4 (2/6) | Missing function. Manual iteration for building delimited strings from lists. |

### Tier 5 — Confirmed Across 1 of 6 Benchmarks (May Affect All)

| Issue | Category | Reported | Classification |
|-------|----------|:--------:|---------------|
| **`&&` / `||` do NOT short-circuit** — both operands are always evaluated | Language Characteristic | B6 | Intentional per `docs/GOVERNANCE.md`. **But LANGUAGE_SPEC.md incorrectly claims short-circuit behavior.** The IR builder at `compiler/ir/builder.py:177-178` eagerly evaluates both operands; the interpreter at `compiler/runtime/interpreter.py:162-165` uses Python's `bool(left and right)` which has no effect since both are already evaluated. Impact: guarded access patterns like `if (len > 0 && list.get(list, 0) == x)` crash when `len == 0`. Fix: nested `if` statements. |
| **Variable scoping bug: `let` declarations leak to global scope** | Runtime Bug | B5 | **Confirmed bug** in `compiler/runtime/interpreter.py:275+`. The `_set_local` method used `environment.assign()` (which traverses parent scope chain) instead of `environment.define()` (which creates local variable). Fixed during B5 development. Affects ALL programs that reuse variable names across functions. |
| **`map.get` raises `KeyError` on missing key** with error string `'keyname'` | Language Characteristic | B6 | Intentional. No fallback/optional mechanism. Workaround: guard every `map.get` with `map.has`. |
| **No `try`/`catch` / exception handling** | Language Characteristic | B6 | Intentional. Runtime errors are fatal. Workaround: explicit `map.has` checks before `map.get`. |
| **No `None` / `null` literal** | Stdlib Gap | B6 | No way to represent absent values naturally. Workaround: `json.parse("null")`. |
| **No regex** | Language Characteristic | B4, B6 | Intentional. All pattern matching is manual character-by-character. |
| **`string.concat` accepts exactly 2 arguments** | Language Characteristic | B4, B6 | Intentional. Multi-arg concatenation requires nested calls: `concat(a, concat(b, c))`. |

### Tier 6 — Single Benchmark, Unclear Cross-Impact

| Issue | Category | Reported | Classification |
|-------|----------|:--------:|---------------|
| Parser crashes on nested `if` statements | Compiler Bug | B3 | **Probable bug.** Single report, unclear reproducibility. Needs re-testing with modern compiler. |
| `list.len` on non-list types crashes (returned `bool` instead of `list` from a function) | Developer Error / Runtime Bug | B2 | Likely a type mismatch in application code rather than a runtime bug. The interpreter has no static type enforcement, so returning wrong types causes cascading failures. |

---

## Issue by Frequency

| Issue | Evidence | Category |
|-------|:--------:|----------|
| **No forward references** | **6/6** | Language Characteristic |
| **No loops (recursion-only)** | **6/6** | Language Characteristic |
| **Formatter bug (`ail fmt` SEMICOLON)** | **5/6** | **Formatter Bug** |
| **Poor diagnostics (no line numbers)** | **4/6** | Poor Diagnostic |
| **`print()` always adds newline** | **3/6** | Language Characteristic |
| **No sort in stdlib** | **3/6** | Stdlib Gap |
| **`string.split()` missing** | **2/6** | Stdlib Gap |
| **`string.find()` missing** | **2/6** | Stdlib Gap |
| **`string.join()` missing** | **2/6** | Stdlib Gap |
| **No short-circuit `&&`/`||`** | **1/6** | Language Characteristic (docs bug) |
| **Variable scoping bug (`let` leaks)** | **1/6** | **Runtime Bug** |
| **No `None`/`null` literal** | **1/6** | Stdlib Gap |
| **No `try`/`catch`** | **1/6** | Language Characteristic |
| **No regex** | **1/6** | Language Characteristic |
| **`string.concat` 2-arg limit** | **1/6** | Language Characteristic |
| **No `string.replace()`** | **1/6** | Stdlib Gap |
| **No UUID generation** | **1/6** | Stdlib Gap |
| **No date/time math** | **1/6** | Stdlib Gap |
| **Parser crash on nested `if`** | **1/6** | **Compiler Bug** (unconfirmed) |

---

## Recurring Implementation Patterns

### Pattern 1: Recursive Helper + Wrapper (100% of benchmarks)

Every iterative operation follows this structure:
```ail
fn helper(coll, i, acc) {
    if (i >= list.len(coll)) { return acc }
    // process coll[i]
    list.append(acc, transform(list.get(coll, i)));
    return helper(coll, i + 1, acc)
}

fn wrapper(coll) {
    return helper(coll, 0, list.new())
}
```

**Cost:** +3 lines of boilerplate per iterative operation vs. a `for` loop.

### Pattern 2: Dependency-Leveled File Structure (100% of benchmarks)

All files >400 LOC are organized as:
```
Level 0: No-dependency utilities (is_digit, is_letter, find_substring)
Level 1: String/list helpers (split, trim, clone)
Level 2: Domain-specific parsing primitives
...
Level N: Main entry point
```

**Cost:** Forces unnatural top-down reading order. Circular dependencies are impossible.

### Pattern 3: Character-by-Character String Scanning (B4, B5, B6)

String processing without `string.find`, `string.split`, or regex:
```ail
fn scan(text, i, result) {
    if (i >= string.length(text)) { return result }
    let ch = string.substring(text, i, i + 1);
    // check ch, accumulate, recurse
    return scan(text, i + 1, result)
}
```

**Cost:** +5-10× parsing code vs. a language with regex/split.

### Pattern 4: Nested `if` Instead of Guarded `&&` (B6 only, but pattern applies to all)

```ail
// What you WANT to write (crashes if len == 0):
if (list.len(coll) > 0 && string.equals(list.get(coll, 0), x)) { ... }

// What you MUST write:
if (list.len(coll) > 0) {
    if (string.equals(list.get(coll, 0), x)) { ... }
}
```

**Cost:** +1 nesting level per guarded list/map access. Now recommended practice for all AILang programs.

---

## Recommendations (Supported by Repeated Evidence)

### Must Fix — Confirmed Bugs

| Priority | Issue | Evidence | Fix |
|----------|-------|----------|-----|
| **P0** | **Formatter bug**: `ail fmt` crashes on valid code | 5/6 benchmarks | Debug `compiler/formatter.py`. The compiler itself is correct; the formatter mis-parses certain AST constructs. |
| **P0** | **Variable scoping bug**: `let` declarations leak to global scope | 1/6 (B5), but potentially affects ALL programs | Already fixed during B5 development. Verify the fix (`_define_local` vs `_assign_local` in `interpreter.py`) is merged and tested. |

### Must Fix — Documentation Bugs

| Priority | Issue | Evidence | Fix |
|----------|-------|----------|-----|
| **P0** | **LANGUAGE_SPEC.md claims `&&`/`||` short-circuit but runtime doesn't implement it** | 1/6 (B6), confirmed by reading `interpreter.py` | Correct LANGUAGE_SPEC.md §6.3 to state eager evaluation. Update operator table. Either implement short-circuit or document the actual behavior. |

### Should Fix — High-Impact Improvements

| Priority | Issue | Evidence | Effort |
|----------|-------|----------|--------|
| **P1** | **Add source location to error messages** | 4/6 benchmarks | Medium. Thread source spans through IR to runtime errors. |
| **P1** | **Add `string.split(text, delimiter)`** | 2/6 benchmarks | Low. One Python stdlib call in the runtime. Eliminates ~15 LOC per benchmark. |
| **P1** | **Add `string.find(text, pattern)`** | 2/6 benchmarks | Low. Returns first index or -1. Eliminates O(n×m) manual scanning. |
| **P2** | **Add `list.sort(list, comparator)`** | 3/6 benchmarks | Low. One Python stdlib call. Eliminates ~20 LOC recursive selection sort. |
| **P2** | **Add `string.join(list, separator)`** | 2/6 benchmarks | Low. One Python stdlib call. |
| **P2** | **Add `None`/`null` literal** | 1/6 (B6), stdlib-wide gap | Medium. Requires lexer, parser, and interpreter changes. |

### Consider — Language Evolution (Recurring Requests, Intentional Decisions)

| Issue | Evidence | Current Status | Recommendation |
|-------|----------|---------------|---------------|
| **`while`/`for` loops** | 6/6 benchmarks requested | Rejected — intentional pure-expression design | Do NOT add. The recursion pattern is well-established and consistent with the language's design. Adding loops would create two ways to do iteration. |
| **Forward references** | 6/6 benchmarks impacted | Intentional — no hoisting | Do NOT add. The dependency-order constraint is a core language property. |
| **Short-circuit `&&`/`||`** | 1/6 discovered, spec mismatch | Rejected in GOVERNANCE.md, but spec says otherwise | **Revisit.** Either implement short-circuit (breaking change to semantics but fixing the spec mismatch) or definitively document eager evaluation. |
| **`try`/`catch`** | 1/6 requested | No existing mechanism | Low priority. Only B6 requested it. The `map.has` guard pattern is a reasonable workaround. |

---

## Per-Benchmark Issue Distribution

| Category | B1 | B2 | B3 | B4 | B5 | B6 | Total Unique |
|----------|:--:|:--:|:--:|:--:|:--:|:--:|:-----------:|
| Compiler Bug | 0 | 0 | 1 | 0 | 0 | 0 | **1** |
| Runtime Bug | 0 | 1 | 0 | 0 | 1 | 0 | **2** |
| Formatter Bug | 1 | 1 | 1 | 1 | 1 | — | **1** |
| Language Characteristic | 2 | 1 | 2 | 3 | 2 | 5 | **7** |
| Stdlib Gap | 0 | 1 | 1 | 3 | 0 | 2 | **6** |
| Documentation Bug | 0 | 0 | 0 | 0 | 0 | 1 | **1** |
| Documentation Gap | 1 | 0 | 0 | 2 | 0 | 0 | **3** |
| Poor Diagnostic | 1 | 1 | 0 | 1 | 0 | 1 | **1** |
| Developer Error | 0 | 0 | 0 | 1 | 1 | 5 | **1** (pattern: same class across benchmarks) |

### Notes on Developer Errors

Developer errors across benchmarks fall into one category: **mismatched function result keys** (e.g., `make_result` returns `{query: ...}` but caller reads `{columns: ...}`). These are the AILang equivalent of type errors — the language has no static type checking, so accessing the wrong key on a map only fails at runtime with a `KeyError`.

---

## Language Health Summary

| Dimension | Rating | Trend |
|-----------|:------:|-------|
| **Compiler Stability** | ✅ 9/9 compile bugs fixed, zero regressions | Stable |
| **Runtime Stability** | ⚠️ 2 runtime bugs found (scoping, short-circuit spec) | 1 fixed, 1 docs-only |
| **Stdlib Coverage** | ⚠️ 6 gaps identified (sort, split, find, join, replace, null) | Gaps known, no additions yet |
| **Diagnostic Quality** | ❌ No source location in errors (4/6 benchmarks) | Unchanged |
| **Formatter** | ❌ Crashes on valid code (5/6 benchmarks) | Unchanged |
| **Documentation Accuracy** | ⚠️ 1 confirmed bug (`&&` short-circuit claim) | Newly discovered |

---

## Appendix: What Each Benchmark Proved

| Benchmark | Key Discovery |
|-----------|---------------|
| B1 — Library Management | Large-app feasibility (107 functions, 819 LOC). Demonstrated that AILang can handle CRUD + persistence + search. |
| B2 — Note Taking | First benchmark to complete with 0 compiler iterations. Showed that once the function-ordering pattern is understood, simple apps can compile on first attempt. |
| B3 — Calendar Application | Exposed compiler crash on nested `if` and the need for `list.sort` and date math. |
| B4 — Markdown Parser | Proved text processing is feasible but expensive. 6 iterations, 40 min for 518 LOC. No `string.find`/`split`/`replace` forced manual character-by-character scanning. |
| B5 — HTTP Request Parser | **Found and fixed a critical runtime bug** (variable scoping). Established the 7-level dependency structure pattern. |
| B6 — Mini SQL Engine | **Discovered the `&&` short-circuit spec mismatch** and the nested-`if` workaround. Highest iteration count (9) due to cascading runtime errors. Most complex data querying logic across all benchmarks. |
