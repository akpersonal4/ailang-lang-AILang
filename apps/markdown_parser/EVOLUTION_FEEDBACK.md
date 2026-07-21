# Evolution Feedback — Cross-Benchmark Comparison

## Benchmarks Compared

| # | Application | Lines | Functions | Domain |
|---|-------------|-------|-----------|--------|
| B1 | Library Management (existing) | 943 | — | Data management |
| B2 | Note Taking Application | 346 | 39 | Data management |
| B3 | Calendar Application | 492 | 59 | Scheduling |
| B4 | Markdown to HTML Converter (this) | 518 | 38 | Text processing |

---

## Cross-Benchmark Issue Count

### Issues Reported in 4 of 4 Benchmarks

| Issue | B1 | B2 | B3 | B4 | Count |
|-------|:--:|:--:|:--:|:--:|:-----:|
| **Formatter bug**: `ail fmt` reports "Expected SEMICOLON" on valid code | ✅ | ✅ | ✅ | ✅ | **4/4** |
| **No loops**: recursion-only iteration adds boilerplate | ✅ | ✅ | ✅ | ✅ | **4/4** |
| **No forward references**: functions must be in dependency order | ✅ | ✅ | ✅ | ✅ | **4/4** |

### Issues Reported in 3 of 4 Benchmarks

| Issue | B1 | B2 | B3 | B4 | Count |
|-------|:--:|:--:|:--:|:--:|:-----:|
| **`print()` always adds newline**: formatted inline output impossible | — | ✅ | ✅ | ✅ | **3/4** |
| **No sort in stdlib**: manual sort implementation needed | — | — | ✅ | ✅ | **2/4** |

### Issues Reported in 2 of 4 Benchmarks

| Issue | B1 | B2 | B3 | B4 | Count |
|-------|:--:|:--:|:--:|:--:|:-----:|
| **No string split in stdlib**: manual split needed | — | — | — | ✅ | **1/4** |
| **No string find in stdlib**: character scanning manual | — | — | — | ✅ | **1/4** |
| **Poor diagnostics**: no line numbers in errors | ✅ | ✅ | — | ✅ | **3/4** |
| **Missing list.sort**: manual sort required | — | — | ✅ | — | **1/4** |

### Issues Unique to Individual Benchmarks

| Issue | Found In | Evidence |
|-------|----------|----------|
| **`string.concat` only accepts 2 args** | B4 | Runtime error in `process_inline_helper` at `main.ail:252` |
| **Inline parsing requires character recursion** | B4 | `process_inline_helper` at `main.ail:223` — 104 lines of nested pattern matching |
| **No regex for pattern matching** | B4 | Manual `find_substring` at `main.ail:14` for all pattern detection |
| **Node count / list.len on non-list types** | B2 | Runtime error when `demo_update_note` returned bool instead of list |

---

## Newly Discovered Issues in Benchmark #4

1. **`string.concat` arity confusion** — The function accepts exactly 2 arguments. When building complex HTML strings, it's easy to accidentally pass 3+ arguments. The error message is clear (`Function concat expected 2 arguments, got 3`) but the pattern of deeply nested calls (`string.concat(string.concat(a, string.concat(b, c)), d)`) is hard to read and maintain.

2. **Character-by-character parsing is extremely verbose** — Processing a string character by character in AILang requires:
   - A recursive helper function with `text`, `i`, and `result` parameters
   - Every character check: `string.substring(text, i, i + 1)` instead of `text[i]`
   - Every pattern check: `string.starts_with(string.substring(text, i), "**")` instead of `text[i:i+2] == "**"`
   - The `process_inline_helper` function at `main.ail:223` required 104 lines to handle 7 inline patterns

3. **No `string.find` forces O(n*m) scanning** — The `find_substring` implementation at `main.ail:14` is linear scan character-by-character. Combined with the recursion-only constraint, pattern searching in long strings is both verbose and algorithmically suboptimal.

4. **Editing large files with no forward references is error-prone** — Reordering a 518-line file with 38 functions into strict dependency order required 6 revision iterations. Each edit introduced risk of orphaned code (as happened in iterations 2–3).

---

## Recurring Standard Library Gaps

| Missing Function | Used Instead | Affected Benchmarks |
|-----------------|-------------|-------------------|
| `string.split(text, sep)` | `split_lines` (manual) | B4 |
| `string.find(text, pattern)` | `find_substring` (manual) | B4 |
| `string.replace(text, from, to)` | Manual character scan | B4 |
| `list.sort(list, comparator)` | Manual insertion sort | B3 |
| `string.join(list, sep)` | Manual list iteration | B3, B4 |
| `print_no_newline(value)` | Workaround impossible | B2, B3, B4 |

---

## Recurring Documentation Gaps

| Gap | First Reported | Still Present |
|-----|----------------|---------------|
| `print()` newline behavior not highlighted as limitation | B2 | ✅ |
| No examples of string-based pattern matching without regex | — | ✅ (B4) |
| No clear guidance on function ordering for complex files | B2 | ✅ (B4) |

---

## Summary

**Most impactful issue across all benchmarks:** The combination of `no loops + no forward references + no string indexing` makes text processing (Benchmark #4) significantly harder than data management (Benchmarks #1–3). The Markdown parser required 40 minutes and 6 iterations — the most of any benchmark — despite being the third-smallest by line count (518 lines vs 943 for Library Management).

**Most common bug pattern:** Forward reference errors caused by function ordering. This accounted for 3 of 6 iterations in B4 and was the only type of compile error encountered.

**Standard library gap with widest impact:** No `string.find` / `string.split` / `string.replace`. These are fundamental for any text processing task. Without them, every AILang text processor must reimplement basic string scanning.
