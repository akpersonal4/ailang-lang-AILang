# Evolution Feedback — Cross-Benchmark Comparison

## Benchmarks Compared

| # | Application | Lines | Functions | Domain |
|---|-------------|-------|-----------|--------|
| B1 | Library Management | 943 | — | Data management |
| B2 | Note Taking Application | 346 | 39 | Data management |
| B3 | Calendar Application | 492 | 59 | Scheduling |
| B4 | Markdown to HTML Converter | 518 | 38 | Text processing |
| B5 | HTTP Request Parser | 405 | 38 | Text / protocol parsing |
| B6 | Mini SQL Engine (this) | 839 | 67 | SQL / data querying |

---

## Cross-Benchmark Issue Count

### Issues Reported in 6 of 6 Benchmarks

| Issue | B1 | B2 | B3 | B4 | B5 | B6 | Count |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:-----:|
| **No forward references**: functions must be in dependency order | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **6/6** |
| **No loops**: recursion-only iteration adds boilerplate | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | **6/6** |

### Issues Reported in 5 of 6 Benchmarks

| Issue | B1 | B2 | B3 | B4 | B5 | B6 | Count |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:-----:|
| **Formatter bug**: `ail fmt` reports "Expected SEMICOLON" on valid code | ✅ | ✅ | ✅ | ✅ | ✅ | — | **5/6** |
| **No short-circuit &&**: both operands evaluated even when left side is false | — | — | — | — | — | ✅ | **1/6** |

### Issues Reported in 3 of 6 Benchmarks

| Issue | B1 | B2 | B3 | B4 | B5 | B6 | Count |
|-------|:--:|:--:|:--:|:--:|:--:|:--:|:-----:|
| **Poor diagnostics**: no line numbers in errors | ✅ | ✅ | — | ✅ | — | ✅ | **4/6** |
| **No sort in stdlib** | — | — | ✅ | ✅ | — | ✅ | **3/6** |

---

## What Got Better / Worse

### What Got Better

| Improvement | Impact | Since Benchmark |
|-------------|--------|-----------------|
| `csv.parse_header` available | Avoided custom CSV parser | B5 (hand-rolled) |
| `string.starts_with` available | Clean arg detection | B5 (used `find_substring` hack) |
| `json.parse("null")` as null literal | Clean missing-value handling | — |

### What Got Worse / Newly Discovered

| Regression / Discovery | Impact | Details |
|------------------------|--------|---------|
| **No short-circuit `&&`** | **High** | `if (cond_a && depends_on_a)` always evaluates `depends_on_a` even when `cond_a` is false. Causes crashes when `depends_on_a` accesses list/map items. Requires nested `if` everywhere. |
| `convert.to_string(list)` crashes | Medium | `string.concat("cols: ", keys)` fails because `convert.to_string` on a list throws. Manual iteration needed. |

---

## Per-Impact Issue Summary

### Critical (Blocking)

| Issue | Workaround | Cost |
|-------|-----------|------|
| **No loops** | Recursion with accumulator params | +2-3× LOC for iterative operations |
| **No forward references** | Dependency-ordered definition levels | Requires planning; circular deps impossible |
| **No short-circuit `&&`** | Nested `if` statements | +1 nesting level per guarded access; easy to forget |

### High (Slows Development)

| Issue | Workaround | Cost |
|-------|-----------|------|
| No try/catch | Pre-check with `map.has` | Verbose, easy to miss |
| No regex | Character-by-character parsing | +5-10× parsing code |
| No string.split | Custom split via `find_substring` | Boilerplate for every delimiter |

### Medium (Annoying)

| Issue | Workaround | Cost |
|-------|-----------|------|
| Poor error diagnostics | Add manual prints | Slows debugging |
| No sort in stdlib | Implement recursive selection sort | +20 LOC |
| No string.join | No way to join lists into strings | Manual iteration required |

---

## Recommendations

1. **Add short-circuit evaluation** to `&&` and `||`. This is the single most impactful fix — it would prevent crashes in guarded list/map access patterns.

2. **Improve error messages** with file names and line numbers. Currently all runtime errors only show the error string and the top-level CLI command, making it very difficult to locate the source.

3. **Add `string.join`** for joining lists with a separator. This would eliminate a common pattern of manual iteration.

4. **Add `None`/`null` literal** instead of requiring `json.parse("null")` for missing values.
