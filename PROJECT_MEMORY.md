# AILang — Project Memory

Project history, key decisions, and evolution timeline for AI coding assistants.

---

## Project Identity

- **Language:** AILang — AI-first, deterministic, specification-driven
- **Version:** v0.2.0
- **Compiler:** 40 Python source files, ~4,000 LOC
- **Standard Library:** 16 `.ail` modules
- **Test Suite:** 624 passing tests across 28 test files
- **Applications:** 66+ across `apps/`, `ai_benchmarks/`, `examples/patterns/`

---

## Timeline

### Foundation
- Compiler pipeline designed with deterministic compilation guarantee (IR SHA-256 identical across runs)
- 16-module stdlib covering string, math, list, map, set, file, path, json, csv, time, random, environment, convert, io, system

### Benchmark Program (13 months simulated)

10 benchmarks totaling ~6,610 LOC of AILang:

| Phase | Scope | Key Finding |
|-------|-------|-------------|
| B01 | Personal Task Manager (255 LOC) | Only benchmark to pass first runtime — 9.5/10 |
| B02 | Sudoku Solver (356 LOC) | Performance timeout at 30–60s — algorithmic workloads not viable |
| B1 | Library Management System (819 LOC) | 3 total revisions — CRUD apps are AILang's sweet spot |
| B2 | Note Taking App (346 LOC) | 1 compile iteration only — learned from previous |
| B3 | Calendar App (492 LOC) | 3 compile iterations — map key mismatch pattern |
| B4 | Markdown → HTML (518 LOC) | `string.concat` 3-arg bug — 6 total revisions |
| B5 | HTTP Request Parser (405 LOC) | Variable scoping compiler bug found — 7 revisions |
| B6 | Mini SQL Engine (839 LOC) | Eager `&&` caused cascading failures — 9 revisions (worst) |
| B7 | Hotel Management System (1,510 LOC) | Largest app — 6 revisions in only 17 min dev time |
| B09 | Spreadsheet Formula Engine (1,325 LOC) | Second largest — mutual recursion challenge |

### Key Milestones

- **Compiler determinism validated** — SHA-256 identical across rebuilds
- **9 compiler bugs fixed** — zero regressions
- **5,000 LOC in 1.88s** compile time benchmark
- **10,000 LOC stress test** passed
- **100% build+run** achieved for all 10 benchmarks after applying playbook methodology
- **10 engineering patterns** created (`examples/patterns/`) — all build+run verified

---

## Architecture Decisions

### Intentional (Do Not Propose Changes)

| Decision | Rationale | Evidence |
|----------|-----------|----------|
| No forward references | No static analysis to resolve call order | 10/10 benchmarks |
| Recursion-only iteration | Simpler compiler, no loop semantics | 10/10 benchmarks |
| No mutual recursion | Requires multi-pass resolution | 2/10 benchmarks |
| Eager `&&`/`\|\|` | Simpler evaluation model | 3/10 benchmarks |
| `string.concat` 2-arg limit | Forces explicit intermediate steps | 3/10 benchmarks |
| Shared global scope for `let` | Simpler variable resolution | 2/10 benchmarks |

### Runtime Optimization #001 — Lexical Variable Lookup Cache (v0.2.0)

Feature added to `Environment.resolve()` to cache binding locations
per-environment after the first successful resolution.

| Aspect | Detail |
|--------|--------|
| **Reason** | `Environment.resolve` consumed 85.4% of wall-clock time (1.6M calls, 230M chain walks) in the static analyzer — the primary bottleneck workload |
| **Solution** | `_resolve_cache: dict[str, Environment]` on each Environment. `resolve()` checks own cache → own values → parent cache shortcut → chain walk. Cache populated with the binding `Environment` pointer on first successful resolution |
| **Negative caching removed** | Initial implementation cached NameError sentinels, but `assign` can create new bindings in ancestor environments, making negative cache entries stale. Only positive results are cached |
| **Impact** | Static Analyzer improved ~6× (373s→19.5s without cProfile). Cache hit rate 52–64% across 5 benchmark apps. Memory overhead ~11 KB |
| **Tests** | 102 new regression tests + 522 existing tests = 624 passing |
| **Instrumentation** | `_CacheStats` counters (hits/misses/negative_hits) per Environment for profiling; `get_cache_info()` introspection hook; `Runtime.get_cache_info()` aggregation |

### Known Gaps (Consider Feature Requests)

| Gap | Impact | Evidence |
|-----|--------|----------|
| `string.split` missing | Requires 15–20 LOC recursive impl | 2/10 benchmarks |
| `string.find`/`index_of` missing | Requires 15 LOC recursive impl | 3/10 benchmarks |
| `string.join` missing | Requires 10 LOC recursive impl | 2/10 benchmarks |
| `list.sort` missing | Requires 20 LOC selection sort | 3/10 benchmarks |
| No source line numbers in errors | Poor DX — must search 500+ LOC files | 5/10 benchmarks |
| `ail fmt` spurious SEMICOLON error | Formatter unusable on valid code | 6/10 benchmarks |

### Governance

- **Benchmark Feedback Loop:** Single-app findings stay in benchmark reports. Only ≥2 independent apps promote lessons to Playbook/AGENTS.md.
- **Stdlib additions:** Require ≥2 benchmarks requesting the same function.
- **Core language changes:** Require ≥6 benchmarks demonstrating the issue.

---

## Production Readiness

| Domain | Verdict | Constraint |
|--------|---------|------------|
| CRUD / data processing ≤2,000 LOC | ✅ Ready | Use playbook methodology |
| Algorithmic / compute workloads | ❌ Not suitable | 30–60s Sudoku solver evidence |
| JSON persistence | ✅ Ready | `json.parse` / `json.stringify` + `file` module |
| CSV processing | ✅ Ready | `csv.parse` / `csv.stringify` |
| String manipulation | ⚠️ Partial | Missing split/find/join — must write custom |

**Overall score:** 6.0/10

---

## Repository Map

```
Root
├── AGENTS.md                         ← AI bootstrap (read first)
├── PROJECT_MEMORY.md                 ← Project history (read second)
├── LANGUAGE_SPEC.md                  ← Source of truth
├── README.md
│
├── docs/
│   ├── MASTER_ENGINEERING_PROMPT.md   ← Orchestration
│   ├── AILANG_DEVELOPMENT_PLAYBOOK.md ← Engineering process
│   ├── STDLIB_REFERENCE.md           ← API reference
│   ├── LANGUAGE_TOUR.md              ← Feature tour
│   ├── AI_MODEL_GUIDE.md             ← Per-tool AI setup
│   └── (40+ other documents)
│
├── compiler/                         ← 39 Python files
├── tests/                            ← 522 tests
├── apps/                             ← ~60 applications
├── ai_benchmarks/                    ← 3 large benchmarks
├── examples/patterns/                ← 10 pattern files
└── .github/workflows/ci.yml          ← CI pipeline
```
