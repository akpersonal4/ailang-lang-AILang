# Cumulative Evidence Matrix

A cross-benchmark summary of all issues discovered across 5 AILang benchmarks.

## Legend

| Category | Description |
|----------|-------------|
| Compiler Bug | Defect in the compiler that produces incorrect code or crashes |
| Runtime Bug | Defect in the interpreter/runtime that produces incorrect behavior |
| Language Limitation | Deliberate design choice that limits expressiveness |
| Missing Stdlib | Functionality that should exist in standard library |
| Documentation Gap | Missing, inaccurate, or misleading documentation |
| Poor Diagnostic | Error message that is unclear, misleading, or lacks location info |
| User Error | Mistake made by the developer (not a language defect) |

---

## Matrix

| Benchmark | Compiler Bugs | Runtime Bugs | Language Limitations | Missing Stdlib | Documentation Gaps | Poor Diagnostics | User Errors | Total |
|-----------|:-------------:|:------------:|:--------------------:|:--------------:|:------------------:|:----------------:|:-----------:|:-----:|
| B1 — Library Management | 0 | 0 | 1 | 0 | 1 | 0 | 0 | **2** |
| B2 — Note Taking | 0 | 1 | 0 | 1 | 0 | 0 | 0 | **2** |
| B3 — Calendar Application | 1 | 0 | 1 | 1 | 0 | 0 | 0 | **3** |
| B4 — Markdown Parser | 0 | 0 | 2 | 1 | 0 | 1 | 1 | **5** |
| B5 — HTTP Request Parser | 0 | 1 | 2 | 0 | 0 | 0 | 1 | **4** |
| **TOTAL** | **1** | **2** | **6** | **3** | **1** | **1** | **2** | **16** |

---

## Issue Details

### B1 — Library Management (943 LOC)
- **Language Limitation**: No structs/classes — maps used as records throughout
- **Documentation Gap**: Missing documentation for map-as-record pattern

### B2 — Note Taking (346 LOC)
- **Runtime Bug**: `list.len` on non-list types crashes (note update returning bool instead of list)
- **Missing Stdlib**: No UUID generation

### B3 — Calendar Application (492 LOC)
- **Compiler Bug**: Parser crashes on nested if statements
- **Language Limitation**: No loops (while/for)
- **Missing Stdlib**: No date/time math operations

### B4 — Markdown Parser (518 LOC)
- **Language Limitation**: No forward references
- **Language Limitation**: No string indexing (`s[i]`)
- **Missing Stdlib**: No `string.find`, `string.split`, `string.replace` (3 individual gaps, counted as 1 category)
- **Poor Diagnostic**: No source line numbers in error messages
- **User Error**: Infinite recursion from missing base case

### B5 — HTTP Request Parser (405 LOC)
- **Runtime Bug**: `_set_local` uses `assign` instead of `define` — `let` declarations leak to global scope, affecting ALL programs
- **Language Limitation**: No forward references (5 compiler iterations caused by this)
- **Language Limitation**: No loops (recursive helpers for all iteration)
- **User Error**: Orphaned duplicate code from edit tool (3 cleanup passes)

---

## Category Totals

```
Compiler Bugs        ██    1
Runtime Bugs         ████  2
Language Limitations ████████████  6
Missing Stdlib       ██████  3
Documentation Gaps   ██    1
Poor Diagnostics     ██    1
User Errors          ████  2
```

**Total issues across all benchmarks: 16**

---

## Per-Benchmark Trend

```
B1  ████   2
B2  ████   2
B3  ██████  3
B4  ██████████  5
B5  ████████  4
```

**Observation**: Benchmark complexity (in terms of issues found) has increased over time, with B4 (Markdown Parser) being the most issue-dense. B5 returned to a moderate level but discovered the most impactful runtime bug yet.

---

## Recurring Issues (present in 2+ benchmarks)

| Issue | B1 | B2 | B3 | B4 | B5 | Count |
|-------|:--:|:--:|:--:|:--:|:--:|:-----:|
| No forward references | ✅ | ✅ | ✅ | ✅ | ✅ | **5/5** |
| No loops (while/for) | ✅ | ✅ | ✅ | ✅ | ✅ | **5/5** |
| `print()` always adds newline | — | ✅ | ✅ | ✅ | — | **3/5** |
| Poor diagnostics (no line numbers) | ✅ | ✅ | — | ✅ | — | **3/5** |
| No string split in stdlib | — | — | — | ✅ | ✅ | **2/5** |
| No sort in stdlib | — | — | ✅ | ✅ | — | **2/5** |
| Orphaned code from edits | — | — | — | ✅ | ✅ | **2/5** |
