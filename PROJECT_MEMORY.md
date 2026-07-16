# AILang — Project Memory

Project history, key decisions, and evolution timeline for AI coding assistants.

---

## Project Identity

- **Language:** AILang — AI-first, deterministic, specification-driven
- **Version:** v1.0.8
- **Compiler:** 41 Python source files, ~4,300 LOC
- **Standard Library:** 16 `.ail` modules (extended: `file.listdir`, `list.sum`, `list.find_by_key`, `io.read`; fixed: `convert.to_number`)
- **Test Suite:** 894+ passing tests across 44+ test scripts
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

### M16 — Documentation Architecture Cleanup

| Aspect | Detail |
|--------|--------|
| **What** | Resolved ADR collision (ADR-001/002/003 → ADR-010/011/012). Archived PROJECT_PHASE.md, ROADMAP.md, CURRENT_MILESTONE.md (DEVELOPMENT_STATUS.md now canonical). Archived MASTER_ENGINEERING_PROMPT.md, FOR_FUTURE_AI.md (AGENTS.md canonical). Archived 21 v0.1.0 sprint reports to `docs/archive/v0.1.0/`. Added `generated/` to .gitignore. Created Documentation Ownership Matrix (15 document types with canonical owners). Updated cross-references in RELEASE_PROCESS.md, AI_MODEL_GUIDE.md, PROJECT_MEMORY.md. |
| **Why** | Eliminate documentation duplication and establish clear canonical ownership for every document type before the project scales further. |
| **Result** | Single canonical document per responsibility. Documentation Ownership Matrix prevents future drift. 21 redundant files archived. |
| **Lessons** | Cross-references must be updated as part of any archival to prevent stale links. |
| **Documents** | `DEVELOPMENT_STATUS.md`, `AGENTS.md`, `docs/guides/ARCHITECTURE_DOCUMENTATION_REPORT.md` |

### M17 — Cross-Repository Analysis & Architecture Documentation

| Aspect | Detail |
|--------|--------|
| **What** | Created a comprehensive cross-repository analysis of the entire AiLang codebase as a reference AI repository understanding dataset. Expanded ARCHITECTURE_DECISIONS.md from 9 to 19 ADRs. Created definitive documents: PROJECT_CONSTITUTION.md (governance), VISION_AND_DIFFERENTIATION.md (vision/strategy), ENGINEERING_BENCHMARK_PLAN.md (benchmark methodology). Regenerated all AI benchmark artifacts. |
| **Why** | Needed BEFORE designing benchmarks — understand the architecture's decisions before attempting to measure them. CTO directive: "get the documents right" first. |
| **Result** | 19 ADRs covering all architectural decisions with rationale and evidence. Three new definitive documents. All AI benchmark artifacts updated. |
| **Lessons** | Architecture documentation must precede benchmark design. You cannot measure what you haven't defined. |
| **Documents** | `docs/architecture/ARCHITECTURE_DECISIONS.md`, `docs/governance/PROJECT_CONSTITUTION.md`, `docs/governance/VISION_AND_DIFFERENTIATION.md`, `docs/benchmarks/ENGINEERING_BENCHMARK_PLAN.md` |

### M18 — Engineering Benchmark Program Charter

| Aspect | Detail |
|--------|--------|
| **What** | Structured the entire 7-benchmark Engineering Benchmark Program (B1-B7) with formal charters, acceptance criteria, and evidence collection methodology. Published AILANG_BENCHMARK_WHITEPAPER.md as the canonical synthesis of all benchmark knowledge. |
| **Why** | Needed a single authoritative document describing what the benchmarks measure, how they work, and what results mean — separating methodology from evidence. |
| **Result** | 7 benchmark charters (B1-B7) each with hypothesis, methodology, acceptance criteria, and dataset requirements. Whitepaper replaces scattered benchmark documentation. |
| **Lessons** | Benchmark methodology must be separated from benchmark results. The whitepaper is the permanent synthesis; individual reports are ephemeral. |
| **Documents** | `docs/benchmarks/AILANG_BENCHMARK_WHITEPAPER.md`, `docs/benchmarks/ENGINEERING_BENCHMARK_PLAN.md` |

### M19 — Documentation Canonicalization (v0.5.0)

| Aspect | Detail |
|--------|--------|
| **What** | Consolidated PROJECT_VISION.md + PROJECT_PHILOSOPHY.md into VISION_AND_DIFFERENTIATION.md. Expanded PROJECT_CONSTITUTION.md with Documentation Rule and Canonical First Rule. Created PRODUCT_ROADMAP.md at root as canonical roadmap. Moved benchmark methodology from whitepaper to ENGINEERING_BENCHMARK_PLAN.md. |
| **Why** | 4 documents describing "roadmap" (PROJECT_VISION.md, PROJECT_PHILOSOPHY.md, ROADMAP.md, PRODUCT_ROADMAP.md) created confusion about which was canonical. CTO directed consolidation. |
| **Result** | From 5 documents to 3 canonical sources (VISION_AND_DIFFERENTIATION.md + CONSTITUTION + PRODUCT_ROADMAP.md). Canonical First Rule added to AGENTS.md and Constitution. Eliminated 7 obsolete/archive files. |
| **Lessons** | Before creating a new document, search for an existing canonical first. Extend it rather than creating a new file. |
| **Documents** | `PRODUCT_ROADMAP.md`, `docs/governance/PROJECT_CONSTITUTION.md`, `docs/governance/VISION_AND_DIFFERENTIATION.md` |

### B1 — Engineering Benchmark Framework (v0.6.0)

| Aspect | Detail |
|--------|--------|
| **What** | Implemented the B1 AI Repository Understanding Benchmark: generic measurement framework (runner, metrics, environ, reporting, dataset modules in `benchmarks/framework/`), 3 canonical datasets (small/medium/current_repo), 44 acceptance/regression/smoke tests, automated via `python -m benchmarks {setup,b1,list,test}`. |
| **Why** | B1 is the foundational benchmark measuring the AI repository understanding problem that AILang is designed to solve. Framework must be generic (reusable by B2-B7) before any benchmark execution. |
| **Result** | Framework reusable across all 7 engineering benchmarks. 44/44 tests passing. Deterministic dataset scanning with SHA-256 metadata. Immutable historical results. Summary aggregation across runs. |
| **Lessons** | Framework must be generic and separate from any specific benchmark's methodology. Datasets frozen by SHA-256 metadata. Run IDs are timestamp-based and sortable. |
| **Documents** | `benchmarks/framework/`, `benchmarks/datasets/`, `benchmarks/b1_understanding/`, `benchmarks/tests/` |

### B1.1 — AI Provider Integration & Calibration (v0.6.1)

| Aspect | Detail |
|--------|--------|
| **What** | Built a provider-independent AI benchmark layer: 4 provider implementations (OpenAI, Anthropic, Google, Local) implementing a common `AIProvider` interface with `ProviderResult` data model for all measurements. Created calibration module that runs identical prompts across all providers to validate measurement infrastructure. Extended B1 to use provider abstraction (3 priority modes: provider → manual dict → approximate). Added `python -m benchmarks calibrate` and `list-providers` commands. |
| **Why** | The benchmark framework must be capable of executing identical benchmark scenarios against multiple AI systems using a common interface, without the benchmark framework knowing which provider is executing. This milestone is about measurement infrastructure, not provider comparison. |
| **Result** | Provider abstraction with factory, 4 implementations, calibration module, B1 extended, 37 new tests (81 total in benchmarks/tests/). ProviderResult captures all request/response/timing/cost measurements without estimation. Calibration validates measurement consistency across providers. |
| **Lessons** | Provider implementations must use lazy imports for external packages so the framework works without optional dependencies. Mock-based testing verifies the interface contract without requiring API keys. Cost estimation uses published pricing but is flagged as approximate. |
| **Documents** | `benchmarks/providers/`, `benchmarks/calibration/`, `benchmarks/tests/test_providers.py`, `benchmarks/tests/test_calibration.py` |

### v0.7.0 — Engineering Optimization Program (Evidence-Driven Stdlib Evolution)

| Aspect | Detail |
|--------|--------|
| **What** | Analyzed benchmark evidence (B2–B7) to identify #1 friction source: stdlib gaps causing 42% of feature-implementation errors. Added `file.listdir(path)`, `list.sum(values)`, `list.find_by_key(values, key, value)`. Fixed `convert.to_number` no-op. Created HYPOTHESIS_STATUS.md tracking 7 hypotheses with evidence. |
| **Why** | Benchmark evidence showed AILang requires 1.38× more iterations than Python, with 42% of B2 errors caused by stdlib limitations. Optimization needed before v1.0. |
| **Result** | B2 L2 improved from 3→1 iterations (67%). B2 total from 7→5 (29%). Overall AILang vs Python ratio from 1.38× to 1.23×. All existing tests pass with zero regressions. |
| **Lessons** | Single-error-at-a-time compiler reporting is the next bottleneck (not addressed here, out of scope). Stdlib gaps are the highest-leverage optimization target. The evidence-first methodology (build measure, identify, fix, re-measure) works. |
| **Documents** | `ENGINEERING_EVIDENCE_REPORT.md`, `docs/HYPOTHESIS_STATUS.md`, `stdlib/file.ail`, `stdlib/list.ail`, `stdlib/convert.ail` |

### M20 — Dependency Ordering Assistant (`ail order`)

| Aspect | Detail |
|--------|--------|
| **What** | Implemented `tools/ail_order/` — analyzes .ail files for dependency ordering issues. Detects forward references, circular dependencies, unreachable functions, duplicate declarations. Provides topological ordering recommendations. |
| **Why** | Benchmark evidence (Mini CRM) showed ~1 iteration penalty due to forward reference violations. Provides compiler-generated ordering hints to reduce iteration without changing language semantics. |
| **Result** | Tool analyzes single files and directories. Provides human-readable output and machine-readable JSON. Supports `--fix` mode for automatic reordering. 28 tests (12 acceptance, 8 regression, 8 AI validation) all passing. |
| **Lessons** | Forward reference detection is the primary value — not automatic reordering. The analysis in DEPENDENCY_ORDERING_ANALYSIS.md correctly identified the need for hints over automation. |
| **Documents** | `tools/ail_order/`, `docs/architecture/DEPENDENCY_ORDERING_ANALYSIS.md` |

### B2–B7 — Engineering Benchmark Execution (v0.6.2)

| Aspect | Detail |
|--------|--------|
| **What** | Executed 6 engineering benchmarks (B2–B7) comparing AILang vs Python across feature implementation, bug fixing, refactoring, upgrades, maintenance, and AI context. Generated ENGINEERING_EVIDENCE_REPORT.md with raw measurements, environment, and observations. |
| **Why** | Needed objective, reproducible evidence of AILang's engineering cost relative to Python — the project's primary hypothesis requires measurement before claims. |
| **Result** | AILang: 18 iterations total (B2–B6). Python: 13 iterations total. Ratio: 1.38× more iterations for AILang. All AILang errors are compile-time (zero silent runtime failures). Refactoring/upgrade/maintenance at parity (1.0×). AI structured context saves 3× iterations (B7). Key stdlib gaps identified: no `!=` operator, no `listdir`, `convert.to_number` is no-op. |
| **Lessons** | The compiler's single-error-at-a-time reporting inflates iteration counts. Stdlib gaps are the #1 friction point (42% of B2 errors). Bottom-up ordering is net neutral for refactoring. |
| **Documents** | `ENGINEERING_EVIDENCE_REPORT.md` |

### M21 — Inventory Python Equivalent + Empirical AILang vs Python Comparison

| Aspect | Detail |
|--------|--------|
| **What** | Built a complete Python 3.12 mirror of the AILang Inventory Management System at `apps/inventory_py/` (same function names, same test logic, same PASS/FAIL format). Fixed 9 parallel-agent-generated test failures → 38/38 pass. Created two canonical benchmark docs. |
| **Why** | The INVENTORY_SCALABILITY_BENCHMARK proved AILang scales to 8,515 LOC but was criticized for not proving AI-coding ease, dev speed, quality, maintainability, patching, or security. A head-to-head Python equivalent is required by the Engineering Benchmark Plan (B2–B6). |
| **Result** | **AILang:** 4,009 app + 4,506 test = 8,515 LOC, 407 app functions, 38/38 tests pass, 0.219s full build, 0.173s test run. **Python:** 2,614 app + 3,644 test = 6,258 LOC, 353 app functions, 38/38 tests pass, 0.194s test run. AILang compiles 55× faster cold-start, catches 100% structural errors at compile in 1 pass; Python needs N runtime iterations. AILang is 33% more verbose per function (recursion + unique var names). |
| **Lessons** | AILang's compiler is a batch correctness gate — all import/name errors surface in one compile vs Python's sequential runtime discovery. Both systems exhibited identical data-bleed bugs (fixed identically via storage_clear_all + reseed). AILang eliminates null-pointer, code-injection, and implicit-coercion at the language level. The B2–B6 AI-iteration measurement remains unexecuted (requires provider queries). |
| **Documents** | `docs/benchmarks/INVENTORY_PYTHON_COMPARISON.md`, `docs/benchmarks/INVENTORY_BENCHMARK_HARNESS.md`, `apps/inventory_py/` |

### M27 — Loop Capture Semantics (v0.9.0)

| Aspect | Detail |
|--------|--------|
| **What** | Solved the scope boundary problem for experimental `for-in` loops. Variables from enclosing function scopes referenced in the loop body are now automatically captured via **parameter threading**: free variable detection analyzes the body AST, detected variables become parameters of the generated recursive helper, written variables are returned from the base case and captured back at the call site via `AssignmentIR`. |
| **Why** | The for-loop lowering generated module-level recursive helpers that had no access to the enclosing function's `StackFrame`. Variables like `total` in `for item in items { total = total + item }` were unresolvable — the most common accumulator pattern was broken. |
| **Result** | All 16 loop tests pass (9 existing + 7 new), 226/226 critical tests pass, canonical benchmarks show zero regression. Zero runtime changes — the fix is entirely compile-time in `ir/builder.py` (~100 LOC). Multiple written variables (>1 accumulator) raise a clear `ValueError` suggesting manual recursion. |
| **Lessons** | AILang's architecture constraint (module-level functions only, no closures) can be worked around without violating ADRs by using compile-time transformations. Parameter threading + return-value capture is a general pattern applicable to other scenarios needing closure-like behavior. The investigation report (`docs/architecture/M26_LOOP_CAPTURE_SEMANTICS.md`) analyzed 5 approaches before selecting this one. |
| **Documents** | `docs/architecture/M26_LOOP_CAPTURE_SEMANTICS.md`, `compiler/ir/builder.py`, `tests/test_experimental_loops.py` |

### M25/M26 — Experimental Loop Primitive (v0.9.0)

| Aspect | Detail |
|--------|--------|
| **What** | Added experimental `for item in collection { body }` syntax to AILang, lowering to recursive function calls at IR-build time. Parser recognizes `for` keyword supported by `--experimental-loops` flag. Semantic analyzer rejects it without the flag (PAR012 error). Full evaluation: 12 files modified, 9 new tests, all benchmarks passing. |
| **Why** | Benchmark evidence (B2 L2 sum-even: 67% iteration reduction from `list.sum`) suggested that a loop primitive could further reduce AI iterations and LOC. The v1.0 decision required empirical evaluation. |
| **Result** | LOC reduction: 5-8% (FAIL vs 20% threshold). Determinism: PASS (0 regressions). Compile perf: PASS (<0.1% overhead). AI iteration reduction: pending AI provider validation. The limitation (no capture semantics) was identified as the critical blocker — resolved in M27. |
| **Lessons** | A loop primitive without capture semantics is practically useless (all common patterns write to an accumulator). The evaluation report recommended conditional promotion after checking capture semantics viability. |
| **Documents** | `docs/benchmarks/LOOP_PRIMITIVE_EVALUATION.md`, `docs/architecture/M26_LOOP_CAPTURE_SEMANTICS.md` |

### M38 — Inventory Production Modules (v1.0.0-RC1)

| Aspect | Detail |
|--------|--------|
| **What** | Built all 5 missing production modules from the M35 Production Plan: `login.ail` (auth + sessions), `backup.ail` (combined JSON backup/restore/list, auto-backup on write, corrupted JSON auto-recovery), `validation.ail` (required, positive-number, email, uniqueness), `import_csv.ail` (products/customers/vendors/movements via `csv.parse_header`), `integrity.ail` (JSON parse check, FK refs, negative stock). Modified `storage.ail` (auto-backup before save, recovery from auto-backup on corruption, concurrent access lock via `data/.lock`). Modified `main.ail` (auth guards on mutating commands, new CLI routing for 11 commands). Created `config/users.json` with default admin/staff accounts. Updated test runners for new arg convention. |
| **Why** | The M35 plan identified the system as 80% production-ready with 6 gaps totaling ~375 LOC. These modules fill those gaps, making the system USABLE for a real user — with authentication, data protection, validation, CSV import, and integrity checking. |
| **Result** | ~350 LOC of new AILang code across 5 new files + 2 modified files. 38/38 existing tests pass cleanly (zero warnings). All new CLI commands verified end-to-end via `ail run`. Auth guards correctly prevent mutations without login. Role-based access (admin/staff) works. Backups create verifiable combined JSON files. Integrity check validates all collections. |
| **Files** | `apps/inventory/login.ail` (58 LOC), `apps/inventory/backup.ail` (120 LOC), `apps/inventory/validation.ail` (44 LOC), `apps/inventory/import_csv.ail` (53 LOC), `apps/inventory/integrity.ail` (173 LOC), `apps/inventory/storage.ail` (modified +48 LOC), `apps/inventory/main.ail` (modified +89 LOC), `apps/inventory/config/users.json` |
| **Lessons** | AILang argument handling via `ail run` strips the script path from `environment.args()`, so args[0] = first user arg. This differs from the old test convention which included the script path. Forward reference errors appear when helper functions are defined after callers within the same file — `storage_auto_backup` must appear before `storage_save`. The `csv.parse_header` function directly returns a list of maps keyed by column names — ideal for CSV import without manual mapping. |
| **Documents** | `docs/adoption/INVENTORY_PRODUCTION_PLAN.md`, `apps/inventory/*` |

### M39 — Test Infrastructure & Audit Fixes (v1.0.0-RC2)

| Aspect | Detail |
|--------|--------|
| **What** | Fixed dead-code gaps identified in audit: wired lock into main(), wired validation into import flow, removed unused imports. Added 5 new test files (31 test cases → 43 total). Updated OPERATIONS_RUNBOOK.md, V1_RC1_RELEASE_NOTES.md → RC2, cleaned PLAYBOOK. Verified all 52 inventory files build, all 43 tests pass. |
| **Why** | Audit revealed unused function parameters, unused imports, misaligned documentation, and inactive lock mechanism. These gaps needed fixing before v1 release. |
| **Result** | `import_save_all_rec` now validates CSV rows before saving. `main()` acquires/releases lock on entry/exit. Unused `import validation` removed from main.ail. 38→43 tests (5 new files). All docs updated for RC2. |
| **Files** | `apps/inventory/import_csv.ail`, `apps/inventory/main.ail`, `apps/inventory/stock_aging.ail`, `apps/inventory/tests/test_*.ail`, `docs/deployment/OPERATIONS_RUNBOOK.md`, `docs/releases/V1_RC1_RELEASE_NOTES.md` |

### M40 — Inventory Level 0 Test Fixes

| Aspect | Detail |
|--------|--------|
| **What** | Fixed 2 pre-existing test failures in `tests/test_inventory_level0.py`: (1) `test_helpers_level_0` used `string.to_string()` which doesn't exist in stdlib — replaced with `convert.to_string()` to match the real `helpers.ail`; (2) `test_storage_level_0` had forward-reference errors (`storage_find_first_rec` called before definition, `storage_apply_changes` called before definition) — reordered functions to bottom-up dependency order matching the real `storage.ail`. |
| **Why** | These tests had been inlined with stale code that didn't match the actual app files. The real `helpers.ail` and `storage.ail` apps/inventory/ were updated earlier but the tests were not. |
| **Result** | Both tests pass. 724/724 tests clean across relevant test suites. |
| **Files** | `tests/test_inventory_level0.py` |

### M54 — Package Registry MVP

| Aspect | Detail |
|--------|--------|
| **What** | Implemented `ail publish` + local `ail install` workflow. Created `compiler/package/registry.py` with `publish_local()`, `download_from_local_registry()`. Updated `compiler/cli/main.py` with `cmd_publish()`. Updated `tools/ail_package_manager/{installer,resolver}.py` for registry source support. Added `lib/` directory to compiler search path, package-directory module naming, multi-file package support, always-declare module namespace rule. |
| **Why** | Without a registry every project is copy-paste driven. `ail new` had no `ail install` workflow. |
| **Result** | Full pipeline verified on Windows: `pip install . → ail new mylib → ail publish file:///tmp/reg → ail new consumer → ail install mylib → ail run` — works. Multi-file packages with internal imports verified. 722 tests pass (2 pre-existing inventory_level0 tests now fixed). |
| **Files** | `compiler/package/registry.py`, `compiler/package/__init__.py`, `compiler/cli/main.py`, `compiler/compilation/resolution.py`, `compiler/compilation/session.py`, `tools/ail_package_manager/{installer,resolver}.py`, `docs/releases/FIRST_HOUR_CLOSURE_REPORT.md` |

### M56 — External Adoption Closure (v1.0.0)

| Aspect | Detail |
|--------|--------|
| **What** | Resolved snake-case package naming deadlock (manifest.py regex changed from kebab to snake_case, kebab accepted with deprecation warning). Implemented `ail add`, `ail remove`, `ail update`, `ail list` commands in `tools/ail_package_manager/commands.py`. Updated `ail new` to generate `ail.toml` + `ail.lock` (previously only created `main.ail` + README). Added kebab-to-underscore normalization in `compiler/compilation/resolution.py`. |
| **Why** | Naming deadlock was P0 — manifest.py enforced kebab-case, but AILang lexer tokenizes `-` as MINUS, making `import my-package` a parse error. No package name could satisfy both layers. Without `ail new` generating `ail.toml`, all subsequent package operations broke. |
| **Result** | 12 files changed, 2,090 insertions. 32 new tests (19 naming + 13 commands). Full pipeline: `pip install . → ail new myapp → ail add mylib@1.0.0 → ail list → ail remove mylib` works end-to-end. |
| **Files** | `tools/ail_package_manager/manifest.py`, `tools/ail_package_manager/commands.py`, `tools/ail_package_manager/__main__.py`, `ail_platform/manifest.py`, `compiler/compilation/resolution.py`, `compiler/cli/main.py`, `tests/test_package_naming.py`, `tests/test_package_commands.py`, `docs/PACKAGE_NAMING_POLICY.md`, `docs/QUICKSTART.md`, `docs/PACKAGES.md` |
| **Lessons** | Package naming must be validated at both the manifest layer (Python regex) and the language layer (AILang lexer). Snake_case (`^[a-z][a-z0-9_]*$`) is the only format that satisfies both constraints. Kebab-case can be accepted with deprecation warnings for backward compatibility. |

### M57 — VS Code Extension Hardening (v1.0.0)

| Aspect | Detail |
|--------|--------|
| **What** | Hardened VS Code extension from MVP to production-ready. Synced extension version to v0.2.0. Rewrote code actions to generate actual TextEdit operations (import stdlib module, remove unused variable). Added `for` keyword to TextMate grammar and LSP completions. Created installation and feature documentation. |
| **Why** | Extension existed since Phase 9 but had stub code actions, missing `for` keyword in grammar/completions, and no installation documentation. Needed hardening before external adoption. |
| **Result** | 8 files changed, 597 insertions. 103/103 LSP tests passing, zero regressions. Extension v0.2.0 with full code action support. |
| **Files** | `compiler/lsp/features/code_actions.py`, `compiler/lsp/features/completion.py`, `extensions/vscode-ailang/package.json`, `extensions/vscode-ailang/CHANGELOG.md`, `extensions/vscode-ailang/syntaxes/ailang.tmLanguage.json`, `docs/vscode/INSTALLATION.md`, `docs/vscode/FEATURES.md`, `docs/releases/M57_VSCODE_EXTENSION_REPORT.md` |
| **Lessons** | Code actions must generate TextEdit operations, not just diagnostic messages, for VS Code to apply quick fixes. The `for` keyword was implemented in M25/M26 but not added to the VS Code grammar — extension updates must track language changes. |

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
| String manipulation | ✅ Ready | `string.split`, `string.find`, `string.join` (added v0.7.0) |

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
├── benchmarks/                       ← B1-B7 framework, providers, calibration, datasets, b1_understanding, tests
├── tests/                            ← Existing tests (82 formatter + 44 B1 framework)
├── apps/
│   ├── inventory/                    ← Largest AILang app: 4,046 app + 4,690 test = 8,736 total, 43/43 pass
│   └── inventory_py/                 ← Python 3.12 mirror: 2,614 LOC + 3,644 test = 6,258 total, 38/38 pass
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
├── PRODUCT_ROADMAP.md                ← Canonical product roadmap
└── .github/workflows/ci.yml          ← CI pipeline
```
