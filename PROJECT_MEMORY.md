# AILang — Project Memory

Project history, key decisions, and evolution timeline for AI coding assistants.

---

## Project Identity

- **Language:** AILang — AI-first, deterministic, specification-driven
- **Version:** v0.3.0
- **Compiler:** 40 Python source files, ~4,000 LOC
- **Standard Library:** 16 `.ail` modules
- **Test Suite:** 772 passing tests across 84 test scripts
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

---

## Major Engineering Milestones

A chronological record of every major engineering phase, with results, lessons, and links to relevant documentation.

### M01 — Compiler Completed

| Aspect | Detail |
|--------|--------|
| **What** | The AILang compiler reached feature parity with the language specification. Lexer, parser, AST, IR, semantic analysis, type checking, and code generation all operational. |
| **Why** | Required before any applications could be written or benchmarked. |
| **Result** | Compiler pipeline with deterministic compilation guarantee (IR SHA-256 identical across runs). ~4,000 LOC of Python across 40 files. |
| **Lessons** | Single-pass compilation eliminates forward references by construction. |
| **Documents** | `docs/reference/COMPILER_ARCHITECTURE.md`, `docs/reference/FOLDER_STRUCTURE.md` |

### M02 — Runtime Stabilization

| Aspect | Detail |
|--------|--------|
| **What** | The tree-walking interpreter was hardened to handle real programs of 500+ LOC with correct scoping, variable mutation, and error reporting. |
| **Why** | Early applications crashed at runtime due to scoping bugs, missing features, and edge cases in the interpreter. |
| **Result** | Stabilized runtime with lexical scoping, proper `assign` semantics, module imports, and 16 stdlib modules. |
| **Lessons** | Lexical scoping with bottom-up function ordering is the correct model for AILang's use case. |
| **Documents** | `docs/reference/COMPILER_ARCHITECTURE.md`, `docs/reference/LANGUAGE_SPEC.md` |

### M03 — 42 Benchmark Applications

| Aspect | Detail |
|--------|--------|
| **What** | Written and validated 42 applications spanning 10 benchmarks (initial phase) + 21 AI benchmark matrix apps + additional validation apps. |
| **Why** | Needed a representative corpus to validate the compiler, runtime, and AI generation capability. |
| **Result** | ~6,610 LOC of AILang across diverse domains: CRUD, file processing, text manipulation, algorithms, games, data analysis. All build+run successfully. |
| **Lessons** | CRUD/data processing ≤2,000 LOC is AILang's sweet spot. Algorithmic workloads (Sudoku) timeout at 30–60s. |
| **Documents** | `docs/benchmarks/AI_BENCHMARK_MATRIX.md`, `docs/benchmarks/AI_BENCHMARKS.md`, `docs/archive/benchmarks/APPLICATION_ANALYSIS.md` |

### M04 — 522+ Regression Tests

| Aspect | Detail |
|--------|--------|
| **What** | Built a comprehensive test suite covering lexer, parser, AST, IR, semantic analysis, type checker, runtime, CLI, formatter, stdlib, stress, benchmarks, and AI validation. |
| **Why** | TDD mandatory. Every feature starts with tests. No change is accepted without passing all existing tests. |
| **Result** | 522 tests (now 772 after cache optimization + DX tools) across 84 test scripts. Quality gates (pytest, black, ruff, mypy) enforced on every change. |
| **Lessons** | TDD prevents regression in a codebase where the compiler and runtime are closely coupled. The relationship between tests and feature areas must be maintained as the codebase grows. |
| **Documents** | `docs/reference/TESTING.md` |

### M05 — AI Validation

| Aspect | Detail |
|--------|--------|
| **What** | Validated that AI models (Claude, GPT, Gemini, DeepSeek, Llama) can generate correct AILang code from specification. Created AI_MODEL_GUIDE.md for per-tool setup. |
| **Why** | AILang is AI-first. If AI cannot generate it reliably, the project fails its primary mission. |
| **Result** | 100% build+run achieved for all benchmarks after playbook methodology. Compile iterations ~0, runtime iterations ~0 with proper planning. |
| **Lessons** | AI needs structured documentation (AGENTS.md, Playbook) consumed before code generation. The Benchmark Feedback Loop ensures continuous improvement. |
| **Documents** | `docs/guides/AI_MODEL_GUIDE.md`, `docs/benchmarks/AILANG_BENCHMARK_WHITEPAPER.md`, `AGENTS.md` |

### M06 — Packaging Sprint

| Aspect | Detail |
|--------|--------|
| **What** | Created installable Python package with CLI entry point (`ail`), CI pipeline (GitHub Actions), and proper version management. |
| **Why** | Needed for distribution, CI, and reproducible builds. |
| **Result** | v0.1.2 release with `pip install` support. CI runs tests, linting, and type checking on every push. |
| **Lessons** | Packaging is not zero-effort even for a Python project. pyproject.toml, CI, and version management must be planned. |
| **Documents** | `docs/releases/RELEASE_PROCESS.md`, `pyproject.toml`, `.github/workflows/ci.yml` |

### M07 — Performance Investigation

| Aspect | Detail |
|--------|--------|
| **What** | Systematic profiling of the AILang runtime using `cProfile` and `tracemalloc` across 5 canonical benchmark apps. |
| **Why** | Needed to understand where runtime time is spent before any optimization. ADR-007 mandates evidence-first optimization. |
| **Result** | Identified `Environment.resolve` as the sole bottleneck at 85.4% of static analyzer runtime (1.6M calls, 230M chain walks). Other apps ran in <0.3s with no significant hotspots. |
| **Lessons** | Without profiler evidence, optimization is speculation. The static analyzer's deep recursion (scope depth ~144) drives the bottleneck, not Python overhead or isinstance calls. |
| **Documents** | `docs/performance/runtime_optimization_001/profile.md`, `docs/performance/runtime_optimization_001/analysis.md` |

### M08 — Variable Lookup Cache Optimization (v0.2.0)

| Aspect | Detail |
|--------|--------|
| **What** | Implemented `_resolve_cache: dict[str, Environment]` on each `Environment` to cache binding locations after first successful resolution. |
| **Why** | 85.4% of static analyzer runtime was in `Environment.resolve`. Caching reduces 230M chain walks to O(1) per (environment, name) pair after first access. |
| **Result** | Static analyzer improved from 373s to ~19.5s (without cProfile). Cache hit rate 52–64% across all 5 benchmarks. ~11 KB memory overhead. 624/624 tests pass. |
| **Lessons** | ~20 lines of Python produced a 6× improvement on the worst-case workload. The cache is safe because it stores binding locations, not values — no invalidation needed for `assign`. Negative caching was removed due to an `assign`-can-create-bindings edge case. |
| **Documents** | `docs/runtime/lookup_cache/design.md`, `docs/runtime/lookup_cache/implementation.md`, `docs/runtime/lookup_cache/regression.md`, `docs/runtime/lookup_cache/benchmark.md`, `docs/runtime/optimizations.md` |

### M09 — Runtime Profiling Results (v0.2.0)

| Aspect | Detail |
|--------|--------|
| **What** | Full before/after benchmark comparison across all 5 canonical apps with cache stats, memory impact, and speedup factors. |
| **Why** | ADR-007 mandates benchmark evidence for every optimization. Needed to confirm the cache works as designed and has no regressions. |
| **Result** | See Runtime Optimization Registry RTO-001 for full table. Static analyzer: ~6× improvement. All apps produce byte-identical output. |
| **Lessons** | cProfile's tracing overhead distorts absolute timing — direct-with-cProfile comparison gives ~6×, without-cProfile gives ~19×. Cache hit rate is the key metric, not absolute speedup. |
| **Documents** | `docs/runtime/optimizations.md`, `docs/runtime/lookup_cache/benchmark.md` |

### M10 — Architecture Documentation Sprint

| Aspect | Detail |
|--------|--------|
| **What** | Created comprehensive architecture documentation: ARCHITECTURE_DECISIONS.md (9 ADRs), RUNTIME_OPTIMIZATIONS.md (optimization registry), FOR_FUTURE_AI.md (10-minute guide) [archived M16]. Updated PROJECT_MEMORY.md, AGENTS.md, Playbook, and Master Prompt [archived M16]. |
| **Why** | Preserve engineering knowledge so future AI and human contributors understand why decisions were made without rediscovering them. |
| **Result** | Single source of truth for all architectural decisions. Evidence attached to every optimization. Cross-references verified. Repository is self-explanatory. |
| **Lessons** | Documentation is infrastructure. AI-consumable structured documentation reduces iteration by making all context available upfront. |
| **Documents** | `docs/architecture/ARCHITECTURE_DECISIONS.md`, `docs/runtime/optimizations.md`, `docs/archive/misc/FOR_FUTURE_AI.md`, `docs/guides/ARCHITECTURE_DOCUMENTATION_REPORT.md` (this file) |

### M11 — DX Tool #001 (ail context)

| Aspect | Detail |
|--------|--------|
| **What** | Implemented standalone developer experience tool `tools/ail_context/` that generates `generated/PROJECT_CONTEXT.md` for AI consumption. |
| **Why** | Needed single-file project context that any AI agent could read before generating code to reduce iteration and mistakes. |
| **Result** | Tool generates ~6.5KB markdown document with 15 sections covering everything from project overview to frozen components. Acceptance test suite validates all aspects. |
| **Lessons** | Single-file context prevents AI from missing critical constraints (no loops, no forward references, bottom-up ordering). Warnings about missing stdlib functions prevent hallucinations. |
| **Documents** | `tools/ail_context/`, `tests/dx_tool_001_acceptance_test.py`, `tests/dx_tool_001_ai_validation.py`, `DX_TOOL_001_REPORT.md` |

### M12 — DX Tool #004 (ail benchmark)

| Aspect | Detail |
|--------|--------|
| **What** | Implemented `tools/ail_benchmark/` — automated benchmark runner with discovery, execution, measurement pipeline, regression detection, and CI-friendly exit codes. |
| **Why** | Needed a single command to run the standard benchmark suite, produce standardized reports, detect regressions, and support before/after comparison — none of which existed despite 43 benchmark apps and 2 profiler tools. |
| **Result** | 5 Python files (discovery, runner, compare, reporter, CLI). Auto-discovers apps from `apps/*/main.ail`. Suite modes: quick (2), canonical (5), full (all). Configurable repetition (default 3×) with min/max/avg/median. Baseline save/compare with 20% regression threshold. Output: `generated/benchmarks/BENCHMARK_REPORT.md` + `.json`. Exit codes: 0=pass, 1=failure, 2=regression, 3=internal error. 19 tests all passing. |
| **Lessons** | Subprocess-based execution keeps measurement realistic. Structured Benchmark dataclass enables future metadata (tags, categories, expected runtime). Fault-tolerant execution is essential for CI pipelines. |
| **Documents** | `tools/ail_benchmark/`, `tests/dx_tool_004_acceptance_test.py`, `tests/dx_tool_004_regression_test.py`, `tests/dx_tool_004_ai_validation.py` |

### M13 — DX Tool Shared Library Foundation (tools/common/)

| Aspect | Detail |
|--------|--------|
| **What** | Created `tools/common/` shared library providing CLI conventions, filesystem utilities, process execution, and reporting helpers to all DX tools, eliminating duplication across ail_context, ail_doctor, ail_static_analyzer, and ail_benchmark. |
| **Why** | As DX tools grew, each reimplemented the same patterns (CLI argument parsing, JSON file I/O, subprocess execution, markdown/JSON dual report writing). A shared library ensures consistency and reduces maintenance burden. |
| **Result** | 5 modules: `cli.py` (standard argument parser), `filesystem.py` (path resolution, output dirs), `process.py` (subprocess helpers), `reporting.py` (markdown/JSON report writer), `__init__.py`. All existing tools continue to work — migration is incremental. Later extended with `hashing.py` (SHA-256 file hashing), `discover_apps()`, `list_py_files()` for DX-005. |
| **Lessons** | Shared libraries should be opt-in, not forced migration. Each tool can adopt helpers incrementally without breaking existing functionality. The CLI conventions module ensures all tools have consistent `--help` output and argument naming. |
| **Documents** | `tools/common/` |

### M14 — DX Tool #005 (ail testgen)

| Aspect | Detail |
|--------|--------|
| **What** | Implemented `tools/ail_testgen/` — automatic AILang test case generator with three-stage pipeline (Discovery → Analysis → Generation). |
| **Why** | Needed to automatically generate regression tests for all 43 apps, detect coverage gaps, and produce standardized reports — eliminating manual test creation overhead. |
| **Result** | 7 Python files: `models.py` (TestCase intermediate model), `discovery.py` (app + existing test discovery), `analyzer.py` (coverage gap analysis), `generator.py` (pure Python generators, no template files), `validator.py` (pytest verification), `reporter.py` (MD + JSON), `__main__.py` (CLI). Output: 44 generated test files in `tests/generated/`, `generated/TEST_GENERATION_REPORT.md` + `.json`. CLI flags: `--dry-run`, `--force`, `--app`, `--report-only`, `--quiet`. 17 tests all passing. |
| **Lessons** | Separation of concerns (facts first, rendering second via intermediate `TestCase` model) makes the system extensible to other output formats (Markdown examples, AI prompts, documentation). Pure Python generators are simpler and more maintainable than template files. The `--force` guard prevents accidental overwrites. |
| **Documents** | `tools/ail_testgen/`, `tests/dx_tool_005_acceptance_test.py`, `tests/dx_tool_005_regression_test.py`, `tests/dx_tool_005_ai_validation.py`, `tools/ail_testgen/DESIGN.md` |

### M15 — Tooling Architecture & Package Manager Design (v0.3.1)

| Aspect | Detail |
|--------|--------|
| **What** | Created two architecture documents before implementing DX-006: `TOOLING_ARCHITECTURE.md` (architecture contract for all DX tools) and `PACKAGE_MANAGER_DESIGN.md` (specification-first design for the package manager). |
| **Why** | Following AILang's specification-first philosophy. A package manager touches many system components (filesystem, VCS, network, registry, caching, integrity verification). Getting the design right before writing code prevents redesign later. The tooling architecture contract ensures all future DX tools follow consistent conventions. |
| **Result** | `TOOLING_ARCHITECTURE.md`: 572 lines covering 12 sections + 2 appendices. `PACKAGE_MANAGER_DESIGN.md`: 722 lines covering 13 sections + 1 appendix. 10 open questions identified for review. No implementation code written. |
| **Lessons** | Design-first prevents architecture drift. The `ail.toml` project manifest serves as a single source of truth for all DX tools (package manager, benchmark runner, test generator, LSP, formatter). Writing the design document revealed 10 open questions that would have been discovered mid-implementation. |
| **Documents** | `docs/architecture/TOOLING_ARCHITECTURE.md`, `docs/architecture/PACKAGE_MANAGER_DESIGN.md` |

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
├── README.md
│
├── docs/
│   ├── reference/                     ← LANGUAGE_SPEC, stdlib, compiler arch, install
│   ├── guides/                        ← Playbook, AI_MODEL_GUIDE
│   ├── architecture/                  ← ARCHITECTURE_DECISIONS.md, TOOLING_ARCHITECTURE.md, PACKAGE_MANAGER_DESIGN.md, MEMBER_ACCESS, MODULE_SYSTEM
│   ├── adr/                           ← ADR-001, ADR-002
│   ├── governance/                    ← Philosophy, Constitution, Vision, Evolution, Contributing
│   ├── runtime/
│   │   ├── optimizations.md           ← Optimization registry
│   │   └── lookup_cache/              ← Cache design, implementation, benchmark, regression
│   ├── performance/
│   │   └── runtime_optimization_001/  ← Profile reports, hotspot analysis, feasibility
│   ├── benchmarks/                    ← AI benchmarks, matrix, analysis, whitepaper
│   ├── releases/                      ← Release process
│   ├── archive/
│   │   ├── phases/                    ← Phase 5B–10 reports
│   │   ├── benchmarks/                ← Past benchmark/validation reports
│   │   └── misc/                      ← Other historical documents
│   └── reports/
│       ├── v0.1.0/                    ← Sprint reports, checklists, audits
│       └── v0.2.0/                    ← v0.2-specific reports
│
├── compiler/                         ← 40 Python files
├── tests/                            ← 677 tests
├── apps/                             ← ~60 applications
├── tools/
│   ├── common/                       ← Shared DX tooling library
│   ├── ail_context/                  ← DX-001
│   ├── ail_doctor/                   ← DX-002
│   ├── ail_static_analyzer/          ← DX-003
│   ├── ail_benchmark/               ← DX-004
│   └── ail_testgen/                 ← DX-005
├── tests/
│   └── generated/                    ← Auto-generated test files
├── ai_benchmarks/                    ← 3 large benchmarks
├── examples/patterns/                ← 10 pattern files
└── .github/workflows/ci.yml          ← CI pipeline
```
