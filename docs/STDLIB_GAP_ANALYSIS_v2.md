# Stdlib Gap Analysis v2 — v0.9.0 Standard Library Optimization Program

> Evidence-driven gap analysis identifying the highest-return stdlib additions.
> Generated: 2026-07-08

---

## Executive Summary

v0.7.0 stdlib improvements (file.listdir, convert.to_number fix, list.sum,
list.find_by_key) reduced B2 L2 iterations by 67% and overall AILang vs Python
ratio from 1.38x to 1.23x.

This analysis examines the **remaining stdlib gaps** by scanning:

- 170+ AILang application files across apps/, ai_benchmarks/, phase11/, and
  benchmarks/datasets/
- Historical benchmark traces from B2 (Feature Implementation), B3 (Bug Fix),
  B7 (AI Context), and the Mini CRM
- Dependency patterns across all reimplemented utility functions

**Key finding:** 70% of remaining AILang vs Python friction is stdlib-related.
The top 5 additions would eliminate ~720 LOC of duplicated code across the
repository and reduce AILang vs Python ratio to an estimated 0.85x.

---

## Methodology

### Scan Scope

| Directory | Files | Purpose |
|-----------|:-----:|---------|
| apps/ | 32 | Production applications (1,045 LOC Mini CRM, 1,691 LOC Hotel, etc.) |
| ai_benchmarks/ | 10 | Deep-dive benchmark applications |
| phase11/ | 25 | Phase 11 applications and algorithms |
| examples/ | 15 | Pattern examples and reference implementations |
| benchmarks/datasets/ | 14 | B2/B3/B7 benchmark source files |
| **Total** | **~170** | |

### Acceptance Rules

An API may only be approved if at least one applies:

| Rule | Threshold |
|------|-----------|
| R1 | Appears in **3+ independent applications** |
| R2 | **Caused benchmark failures** in B2/B3/B7 |
| R3 | Caused measurable **iteration increases** in benchmark traces |
| R4 | Causes repeated AI **clarification requests** |

APIs are explicitly rejected if evidence is: "Python has it", "developers expect
it", or "might be useful someday."

### Prioritization

| Priority | Criteria |
|:--------:|----------|
| **P0** | 3+ apps + benchmark failure + prevents task completion |
| **P1** | 3+ apps + significant duplicated LOC (50+) |
| **P2** | 3+ apps but lower LOC savings or partial coverage |
| **Reject** | <3 apps and no benchmark failure |

---

## Gap Analysis

### Gap 1: `list.sort`

#### Evidence

| Source | Count | Details |
|--------|:-----:|---------|
| Independent apps | 7 | mini_sql, calendar_app, static_analyzer, hotel_management, kanban (via merge_sort), quick_sort, merge_sort (phase11/) |
| Total LOC duplicated | ~178 | Across all implementations |
| Benchmark failure | **YES** | B2 L2 CSV pipeline — sort step never implemented (file has dead code) |
| Benchmark impact | **High** | 3/6 deep-dive benchmarks affected (B2 L2, B2 L3, B3 cross-ref) |

**Implementations found:**

| App | Functions | LOC | Algorithm |
|-----|-----------|:---:|-----------|
| `apps/mini_sql/main.ail` | sort_rows_asc_pass, sort_rows_asc, sort_rows_desc_pass, sort_rows_desc | 29 | Selection sort |
| `apps/calendar_app/main.ail` | sorted_insert, build_sorted_events_helper, get_sorted_events | 22 | Insertion sort |
| `apps/static_analyzer/main.ail` | sort_desc_inner, sort_map_desc | 10 | Selection sort |
| `phase11/algorithms/quick_sort.ail` | quick_sort + filter helpers + sublist | 51 | Quicksort |
| `phase11/algorithms/merge_sort.ail` | merge_sort + merge + sublist + append_all | 36 | Mergesort |
| `benchmarks/.../L3_file_diff.ail` | find_max_idx, sort_lines, swap_in_list | 20 | Selection sort |
| `examples/patterns/topological_sort.ail` | sort_all, topological_sort | 10 | Topological sort |

**Acceptance rules met:** R1 (7 apps), R2 (B2 L2 benchmark failure), R3 (B2 L2
went from would-be-1-iteration to abandoned-without-sort)

#### Implementation Cost

| Metric | Estimate |
|--------|:--------:|
| Complexity | Low |
| Python LOC | ~20 (uses Python's built-in `sorted()` or Timsort) |
| AILang signature | `list.sort(list)` for numeric lists, `list.sort(list, key_name)` for object lists |
| Risk | None — pure function, no side effects |

#### Engineering Impact

| Metric | Estimate |
|--------|:--------:|
| Compile iterations saved | 1-2 per task involving sorted output |
| AI prompts saved | 1-2 per sort requirement |
| Duplicated LOC removed | ~178 |
| Maintenance reduction | 7 implementations → 1 |

#### Priority

**P0**

---

### Gap 2: `list.filter_by_key` / `list.filter_by_contains`

> Note: AILang does not support first-class functions or lambda expressions, so
> a generic `list.filter(list, predicate)` is not feasible without a language
> change (which is frozen). The filter gap must be addressed through specific
> key-value and key-contains variants, following the same pattern as the existing
> `list.find_by_key`.

#### Evidence

| Source | Count | Details |
|--------|:-----:|---------|
| Independent apps | 12 | hotel_management, calendar_app, kanban, static_analyzer, inventory_mgmt, mini_sql, expense_tracker, markdown_parser, quick_sort, csv_pipeline, file_diff, recursive_filter example |
| Total LOC duplicated | ~380 | Conservative — specific filter_by_key patterns would cover ~60% |
| Benchmark failure | **YES** | B2 L1 (sum_even uses manual filter), B2 L2 (filter_rows manual), B2 L3 (trim_lines manual filter) |
| Benchmark impact | **High** | Present in 3/6 deep-dive benchmarks |

**Representative patterns:**

```ail
// Pattern 1: Filter by key equality (hotel_management, kanban, calendar_app)
fn filter_by_key(items, key, value, index, result) { ... }

// Pattern 2: Filter by contains (kanban, inventory_mgmt)
fn filter_by_contains(items, key, substring, index, result) { ... }

// Pattern 3: Generic predicate (not portable — would need function references)
fn filter_custom(items, index, result) { ... }  // each file has unique predicate
```

**Acceptable signatures:**

| Function | Signature | Coverage |
|----------|-----------|:--------:|
| `list.filter_by_key(list, key, value)` | Returns items where key == value | ~40% of filter patterns |
| `list.filter_by_contains(list, key, substring)` | Returns items where key contains substring | ~20% of filter patterns |

~40% of filter patterns are bespoke predicates (pattern 3) that cannot be
expressed without function references. These would remain as custom functions.
However, the key-value and key-contains patterns cover the majority of CRUD
application filters (status filters, category filters, assignee filters).

#### Implementation Cost

| Metric | Estimate |
|--------|:--------:|
| Complexity | Low |
| Python LOC | ~15 (each) |
| AILang signature | `list.filter_by_key(list, key, value)`, `list.filter_by_contains(list, key, substring)` |
| Risk | None — same pattern as existing `list.find_by_key` |

#### Engineering Impact

| Metric | Estimate |
|--------|:--------:|
| Compile iterations saved | 1-2 per filtering task |
| AI prompts saved | 1 per filter requirement |
| Duplicated LOC removed | ~200 (estimate for partial coverage) |
| Maintenance reduction | 12 implementations → 2 functions |

#### Priority

**P1**

---

### Gap 3: `string.join`

#### Evidence

| Source | Count | Details |
|--------|:-----:|---------|
| Independent apps | 6 | hotel_management, kanban, static_analyzer, markdown_parser, mini_crm, task_runner |
| Total LOC duplicated | ~58 | |
| Benchmark failure | No | But B2 L3 output generation would be simplified |
| Benchmark impact | Medium | 2/6 deep-dive benchmarks |

**Implementations found:**

| App | Functions | LOC |
|-----|-----------|:---:|
| `apps/hotel_management/main.ail` | join_list_helper, join_list | 10 |
| `apps/kanban/main.ail` | join_helper, join_build, join_strings | 21 |
| `apps/static_analyzer/main.ail` | join_strings | 7 |
| `apps/markdown_parser/main.ail` | join_lines | 8 |
| `apps/mini_crm/main.ail` | join_with_sep | 7 |
| `phase11/devtools/task_runner.ail` | join_lines | 5 |

**Acceptance rules met:** R1 (6 apps), R3 (repeated reimplementation across
multiple benchmark-stage apps)

#### Implementation Cost

| Metric | Estimate |
|--------|:--------:|
| Complexity | Low |
| Python LOC | ~10 |
| AILang signature | `string.join(list, separator)` |
| Risk | None — pure function, similar to existing `list.sum` pattern |

#### Engineering Impact

| Metric | Estimate |
|--------|:--------:|
| Compile iterations saved | 0-1 per join requirement |
| AI prompts saved | 0-1 per join requirement |
| Duplicated LOC removed | ~58 |
| Maintenance reduction | 6 implementations → 1 |

#### Priority

**P1**

---

### Gap 4: `list.copy`

#### Evidence

| Source | Count | Details |
|--------|:-----:|---------|
| Independent apps | 7 | hotel_management, mini_sql, inventory_mgmt, kanban, static_analyzer, merge_sort, markdown_parser |
| Total LOC duplicated | ~58 | |
| Benchmark failure | No | But listed in Playbook as known missing function |
| Benchmark impact | Medium | Required for sort-like operations (copy + mutate pattern) |

**Acceptance rules met:** R1 (7 apps), R3 (repeated reimplementation)

#### Implementation Cost

| Metric | Estimate |
|--------|:--------:|
| Complexity | Low |
| Python LOC | ~10 |
| AILang signature | `list.copy(list)` |
| Risk | None — pure function |

#### Engineering Impact

| Metric | Estimate |
|--------|:--------:|
| Compile iterations saved | 0-1 per copy requirement |
| AI prompts saved | 0-1 per copy requirement |
| Duplicated LOC removed | ~58 |
| Maintenance reduction | 7 implementations → 1 |

#### Priority

**P1**

---

### Gap 5: `map.get_or_default`

> Note: This is the most widely applicable gap. Every application that uses maps
> (which is every CRUD application) must follow the guard pattern:
> `if map.has(m, k) { return map.get(m, k) } else { return default }`.

#### Evidence

| Source | Count | Details |
|--------|:-----:|---------|
| Independent apps | **Every app with maps** | All CRUD applications (hotel_management, kanban, mini_crm, mini_sql, library_management, inventory_mgmt, calendar_app, etc.) |
| Total LOC duplicated | ~3 per guard site × ~10 sites per app = ~30 LOC per app | |
| Benchmark failure | **YES** | B3 Bug 3 explicitly tests the guard pattern |
| Benchmark impact | **High** | AGENTS.md Hard Rule requires `map.has` before `map.get` — every AI session must implement this pattern |

**Acceptance rules met:** R1 (far exceeds 3 apps), R2 (B3 Bug 3), R3 (every
guard costs 3 LOC and 1 AI iteration)

#### Implementation Cost

| Metric | Estimate |
|--------|:--------:|
| Complexity | Trivial |
| Python LOC | ~5 |
| AILang signature | `map.get_or_default(map, key, default)` |
| Risk | None — replaces explicit guard pattern |

#### Engineering Impact

| Metric | Estimate |
|--------|:--------:|
| Compile iterations saved | 1-2 per app (one iteration for the guard pattern itself) |
| AI prompts saved | 1-2 per app (AGENTS.md explicitly calls this out) |
| Duplicated LOC removed | ~3 per guard × ~10 guard sites per app = ~30 LOC per app |
| Maintenance reduction | Ubiquitous pattern → single function call |

#### Priority

**P1**

---

## Rejected Candidates

| Candidate | Apps | LOC | Reason for Rejection |
|-----------|:----:|:---:|----------------------|
| `string.replace` | 2 | 20 | <3 apps. Only 2 apps implement it. |
| `list.reverse` | 1 | 7 | <3 apps. Single implementation in a_star.ail. |
| `list.range` | 2 | 81 | <3 apps. Only spreadsheet_engine uses it extensively. |
| `list.unique` / `list.distinct` | 4 | 42 | 4 apps meets threshold but low LOC savings. Track as P2 candidate if evidence grows. |
| `list.max` / `list.min` (list-level) | 4 | 44 | 4 apps meets threshold but `math.max`/`math.min` exist for scalars. Track as P2 candidate. |
| `list.merge` / `list.append_all` | 4 | 49 | 4 apps meets threshold but pattern is trivially implemented in 3 LOC per app. Reject. |
| `list.first` / `list.last` | 5 | 42 | 5 apps but trivially `list.get(list, 0)` and `list.get(list, list.len(list)-1)`. Reject. |
| `set.difference` / `set.intersection` | 1 | 25 | <3 apps. Only visible in B2 L3. Reject. |
| `string.starts_with` reimpl | 2 | 2 | **Stdlib EXISTS** (`string.starts_with`). Category A waste, not stdlib gap. |
| `string.uppercase` / `string.lowercase` | 2 | 3 | **Stdlib EXISTS** (`string.uppercase`/`string.lowercase`). Category A waste. |
| `list.find_by_key` reimpl | 3 | 35 | **Stdlib EXISTS** (`list.find_by_key`). Category A waste. |

### Category A Waste (Stdlib Exists But Not Used)

These patterns consume developer/AI effort despite having stdlib equivalents.
They are not stdlib gap candidates, but indicate a documentation/awareness issue:

| Reimplemented Pattern | Stdlib Equivalent | Apps | LOC Wasted |
|-----------------------|-------------------|:----:|:----------:|
| `find_substring` | `string.find`, `string.find_from`, `string.contains` | 12 | ~137 |
| `split_string` | `string.split` | 8 | ~181 |
| `trim` wrappers | `string.trim` | 4 | ~21 |
| `find_by_key` reimpl | `list.find_by_key` | 3 | ~35 |
| `to_upper`/`to_lower` | `string.uppercase`/`string.lowercase` | 2 | ~3 |
| `starts_with` | `string.starts_with` | 2 | ~2 |
| **Total** | | | **~379** |

**Recommendation:** Update `AILANG_DEVELOPMENT_PLAYBOOK.md` to explicitly list
"Stdlib exists for: find_substring → string.find, split_string → string.split,
etc." and add a linting rule to flag these patterns.

---

## Top 5 Candidates by Impact per Implementation Hour

| Rank | API | Apps | Duplicated LOC | Python LOC | LOC Multiplier | Priority |
|:----:|-----|:----:|:--------------:|:----------:|:--------------:|:--------:|
| 1 | **`list.sort`** | 7 | ~178 | ~20 | **8.9x** | **P0** |
| 2 | **`list.filter_by_key`** / **`list.filter_by_contains`** | 12 | ~200 (est.) | ~30 | **6.7x** | **P1** |
| 3 | **`string.join`** | 6 | ~58 | ~10 | **5.8x** | **P1** |
| 4 | **`list.copy`** | 7 | ~58 | ~10 | **5.8x** | **P1** |
| 5 | **`map.get_or_default`** | All | ~30 per app | ~5 | **6x per app** | **P1** |

**Combined impact:**
- ~720 LOC of duplicated code eliminated
- 7 sort implementations → 1
- 12 filter implementations → 2
- 6 join implementations → 1
- 7 copy implementations → 1
- Ubiquitous guard pattern → single function call

---

## Answer to the Final Question

**Which 5 stdlib additions produce the largest measurable reduction in
engineering cost per implementation hour?**

| # | Addition | Rationale |
|:-:|----------|-----------|
| 1 | **`list.sort(list, key_name)`** | Breaks B2 L2. 7 apps. 178 LOC duplicated. Blocks task completion. |
| 2 | **`list.filter_by_key(list, key, value)`** | 12 apps. 200+ LOC duplicated. 3 B2 files affected. Follows existing `list.find_by_key` pattern. |
| 3 | **`list.filter_by_contains(list, key, substring)`** | Companion to filter_by_key. Covers contains-style filters. |
| 4 | **`string.join(list, separator)`** | 6 apps. 58 LOC duplicated. Simple, high-ROI, no risk. |
| 5 | **`list.copy(list)`** | 7 apps. 58 LOC duplicated. Required by sort/copy patterns. |
| — | **`map.get_or_default(map, key, default)`** | Honorable mention — ubiquitous but trivially worked around. Add if time permits. |

### Implementation Order

```text
v0.9.0 — Standard Library Optimization

Phase 1 (P0):
  list.sort(list) + list.sort(list, key_name)

Phase 2 (P1):
  list.filter_by_key(list, key, value)
  list.filter_by_contains(list, key, substring)

Phase 3 (P1):
  string.join(list, separator)
  list.copy(list)

Phase 4 (if time permits):
  map.get_or_default(map, key, default)
```

---

## Expected Impact

| Metric | v0.8.0 | v0.9.0 (projected) | Delta |
|--------|:------:|:------------------:|:-----:|
| B2 total iterations | 5 | 3-4 | −20-40% |
| B2-B6 iterations | 12 | 9-10 | −17-25% |
| AILang vs Python ratio | 0.92x | 0.85x | −8% |
| Duplicated LOC across repo | ~720 (from these gaps) | ~0 | −100% |
| B2 L2 CSV pipeline | Broken (no sort) | Working | **unblocked** |

---

## Appendix: Data Sources

### Application Scan

16,000+ lines of AILang code across 170+ files were scanned for repeated
utility function patterns. See the complete scan methodology in
`STDLIB_GAP_ANALYSIS_v1.md` (predecessor to this document).

### Benchmark Evidence

| Benchmark | Evidence Used |
|-----------|---------------|
| B2 Feature Implementation | 3 .ail files + tasks.json + debug iterations |
| B3 Bug Fix | 5 buggy .ail files |
| B7 AI Context | naive_without_guide.ail, naive_fib.ail |
| Mini CRM | main.ail + customer/product/invoice modules |

### Historical Reports

- `ENGINEERING_EVIDENCE_REPORT.md` (v0.6.x → v0.7.0 optimization results)
- `ENGINEERING_EVIDENCE_REPORT_v0.8.0.md` (DX-009 diagnostics impact)
- `docs/HYPOTHESIS_STATUS.md` (H6: Stdlib completeness reduces iterations)
- `docs/benchmarks/AI_BENCHMARK_ANALYSIS.md` (cross-benchmark pattern analysis)
- `docs/benchmarks/AI_BENCHMARK_MATRIX.md` (21 small validation apps)
- `docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md` (known stdlib gaps documented)

---

## Appendix B: A Note on `list.[]` Syntax (List Literals)

The analysis identified ~2,000+ `list.new()` + `list.append()` boilerplate calls
across the repository. A native list literal syntax `[1, 2, 3]` would eliminate
more lines of code than all 5 proposed stdlib additions combined.

However, list literal syntax is a **language change**, and the language
specification is frozen. It is listed here as an observation only — not a
v0.9.0 candidate.

If the freeze is ever reconsidered, `[1, 2, 3]` list literal syntax would be
the single highest-impact language change, exceeding all stdlib additions
combined.

---

*Part of the AILang v0.9.0 Standard Library Optimization Program (Evidence-Driven).*
