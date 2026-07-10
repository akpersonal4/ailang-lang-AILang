# DEVELOPMENT_STATUS.md

## DO NOT START DEVELOPMENT

until this document has been reviewed. Update AGENTS.md reading order after reviewing.

---

## Project Status

| Attribute | Value |
|:----------|:------|
| **Current Version** | v0.8.0 |
| **Current Milestone** | Compiler Diagnostics Improvement Program |
| **Project Phase** | Engineering Optimization |

### Maturity Assessment

| Area | Status |
|------|--------|
| Language | 100% |
| Compiler | 99.9% |
| Runtime | 99% |
| Formatter | 99% |
| Platform Services | 100% |
| Platform Integration | 100% |
| Documentation | 100% |
| Governance | 100% |
| Validation Framework | 100% |
| Engineering Benchmarks | B1 framework active, B1.1 provider integration active, B2–B7 executed — evidence collected, **v0.7.0 optimization complete** |
| AI Provider Abstraction | 4 providers (OpenAI, Anthropic, Google, Local), calibration module, B1 integration |

--------------------------------------

## Completed

### Compiler
- [x] Lexer with full token support
- [x] Parser for all language constructs
- [x] AST builder with error handling
- [x] Semantic analyzer with variable resolution
- [x] Type checker (static analysis)
- [x] IR generation with deterministic SHA-256 output
- [x] Code generation for tree-walking interpreter
- [x] CLI with build/run/fmt commands
- [x] Formatter with --check, --diff, --quiet, --stdin, and directory-wide modes
- [x] Lexer infinite-loop guard (unrecognized characters no longer hang)
- [x] Idempotency verified across 165 valid .ail files (0 failures)
- [x] Comment-aware inline detection (no false positives from `//` inside strings)
- [x] Bug Fix Sprint #001 (6 bugs fixed, 522→624 tests)
- [x] Diagnostics Improvement: `file:line:col` source locations in error messages
- [x] Diagnostics Improvement: spell-check suggestions for undefined identifiers (SEM002)
- [x] Diagnostics Improvement: multi-error reporting (all errors collected before analysis)
- [x] Diagnostics Improvement: JSON diagnostics include `file`, `severity`, `suggestion` fields

### Language
- [x] Core syntax (functions, variables, conditionals)
- [x] Expression evaluation
- [x] Recursion-only iteration model
- [x] Specification frozen (v0.1.x)
- [x] LANGUAGE_SPEC.md canonical specification

### Runtime
- [x] Tree-walking interpreter
- [x] Lexical variable lookup with scoping
- [x] Environment with binding resolution
- [x] Native builtins integration
- [x] Variable Lookup Cache Optimization (RTO-001) ~6× speedup
- [x] **FROZEN** — No further optimizations until community feedback

### Stdlib
- [x] **string** — concat, equals, uppercase, lowercase, length, contains, starts_with, ends_with, trim, substring, find, find_from, split
- [x] **math** — add, sub, mul, div, abs, min, max
- [x] **list** — new, append, len, get, contains, remove, clear, sum, find_by_key
- [x] **array** — new, push, len, get, contains, remove, clear
- [x] **map** — new, set, get, has, delete, keys, clear
- [x] **set** — new, add, contains, len, remove, clear
- [x] **file** — exists, read, write, append, remove, listdir
- [x] **path** — join, basename, dirname, extension, normalize
- [x] **json** — parse, stringify
- [x] **csv** — parse, parse_header, stringify
- [x] **time** — now, timestamp, sleep, format
- [x] **random** — int, float, choice
- [x] **environment** — get, cwd, args
- [x] **convert** — to_string, to_int, to_bool, to_number
- [x] **io** — write, writeln, println
- [x] **system** — exit

### Benchmarks
- [x] B01: Personal Task Manager (255 LOC)
- [x] B02: Sudoku Solver (356 LOC)
- [x] B03: Library Management System (819 LOC)
- [x] B04: Note Taking App (346 LOC)
- [x] B05: Calendar App (492 LOC)
- [x] B06: Markdown → HTML (518 LOC)
- [x] B07: HTTP Request Parser (405 LOC)
- [x] B08: Mini SQL Engine (839 LOC)
- [x] B09: Hotel Management System (1,510 LOC)
- [x] B09b: Spreadsheet Formula Engine (1,325 LOC)
- [x] Inventory System (AILang): 4,009 app + 4,506 test = 8,515 LOC, 38/38 pass, 0.219s build
- [x] Inventory System (Python mirror): 2,614 app + 3,644 test = 6,258 LOC, 38/38 pass
- [x] Inventory Python Empirical Comparison: `docs/benchmarks/INVENTORY_PYTHON_COMPARISON.md`
- [x] Inventory Benchmark Harness (B2–B6 spec): `docs/benchmarks/INVENTORY_BENCHMARK_HARNESS.md`

### Applications
- [x] apps/ — 27 applications validated
- [x] phase11/ — 29 applications validated
- [x] static_analyzer — self-analysis completes (931 lines, 75 functions, 209 calls)
- [x] Total: 66+ applications across CRUD, file processing, text manipulation

### Developer Tools
- [x] VS Code Extension (syntax highlighting, snippets, language config)
- [x] Deterministic formatter (`ail fmt` — --check, --diff, --quiet, dir-wide)
- [x] Lexer stability (no infinite loops on unrecognized characters)
- [x] 82 formatter + CLI tests (50 formatter + 32 CLI)
- [x] 772 tests across 84 test scripts (34 manual + 7 DX tool + 43 generated)
- [x] CI/CD pipeline (GitHub Actions)
- [x] **DX-001** — `ail context` (AI onboarding) — **Complete & Accepted**
- [x] **DX-002** — `ail doctor` (repository health) — **Complete & Accepted**
- [x] **DX-003** — `ail static_analyzer` (code analysis) — **Complete & Accepted**
- [x] **DX-004** — `ail benchmark` (benchmark runner) — **Complete & Accepted**

### Shared Tooling Infrastructure
- [x] `tools/common/` — CLI conventions, filesystem utilities, process execution, reporting helpers

### Documentation
- [x] LANGUAGE_SPEC.md (canonical)
- [x] STDLIB_REFERENCE.md (complete)
- [x] AILANG_DEVELOPMENT_PLAYBOOK.md
- [x] AI_MODEL_GUIDE.md
- [x] ARCHITECTURE_DECISIONS.md (9 ADRs)
- [x] GOVERNANCE.md
- [x] PROJECT_CONSTITUTION.md
- [x] VISION_AND_DIFFERENTIATION.md
- [x] LANGUAGE_EVOLUTION.md
- [x] RELEASE_PROCESS.md
- [x] AI_MODEL_GUIDE.md

--------------------------------------

## Phase Definition

This phase builds the AI-native engineering ecosystem around the stable AILang core.
The language, compiler, runtime, and standard library are frozen — all new
development targets tooling, automation, and developer experience.

### What is Frozen (not modified during this phase)

- Language syntax, grammar, and semantics
- Compiler pipeline (lexer, parser, AST, IR)
- Runtime interpreter and optimization cache
- Standard library API signatures
- Existing benchmark applications
- Existing test suite

### Why This Phase

AILang's differentiation comes from AI-friendly tooling, automation,
and developer experience — not from syntax changes. This phase invests
in the ecosystem that makes AILang productive for both human and AI developers.

---

## Current Work

**DX-009 — Compiler Diagnostics Improvement** ✅

### Status
- **Phase:** Diagnostics Improvement — Complete
- **Runtime:** Frozen
- **v0.8.0 Goal:** Compiler errors show `file:line:col` instead of line number ranges; spell-check suggestions for undefined identifiers; multi-error reporting (collect all errors before stopping); JSON diagnostics include `severity`, `file`, and `suggestion` fields
- **Architecture Design:** ✅ Integrated directly into `Diagnostic`/`DiagnosticFormatter` (no separate doc needed)
- **Implementation:** ✅ Complete

### Key Design Decisions (DX-009)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Source location format | `file:line:col  SEVERITY CODE: message` | Full path + severity + code in standard tool-friendly format |
| Suggestion engine | `difflib.get_close_matches` (cutoff 0.6) | Zero dependencies, works on any identifier collision |
| Multi-error collection | `DiagnosticReporter` threaded through `discover()` path | Lex/parse errors collected before analysis begins |
| Semicolons | Optional (`match` instead of `expect`) | Parser continues after missing semicolon instead of stopping |
| LSP | No changes needed | `from_compiler_diagnostic` already handles new fields via `getattr`; LSP uses URI path, not per-diagnostic file |

### DX-009 Deliverables

| Component | Status | Details |
|-----------|:------:|---------|
| `file_path` in `Diagnostic` | ✅ | Optional field, threaded through all error-reporting paths |
| `suggestion` in `Diagnostic` | ✅ | Populated for SEM002 (undefined identifier) via `difflib` |
| `DiagnosticFormatter.format()` | ✅ | Now outputs `file:line:col  SEVERITY CODE: message` |
| `DiagnosticFormatter.find_suggestion()` | ✅ | Static method, uses `difflib.get_close_matches` |
| SymbolTable suggestion integration | ✅ | `resolve()` collects known names from all scopes; passes suggestion to `_report_error` |
| TypeChecker `file_path` | ✅ | Passed through constructor |
| Lexer `source_path` | ✅ | Passed through constructor |
| TokenStream `source_path` | ✅ | Passed through constructor |
| Parser `source_path` | ✅ | Passed through to TokenStream |
| Reporter threading | ✅ | `discover()` → `_discover_recursive()` → `_compile_all()` → Lexer/Parser |
| CLI error output | ✅ | Uses new `format()` for text; JSON includes `file`, `severity`, `suggestion` |
| Semicolons optional | ✅ | `stream.expect(SEMICOLON)` → `stream.match(SEMICOLON)` at 4 call sites |
| Test suite | ✅ | 308+ tests passing (core + LSP + stdlib) |

**DX-008 — AILang Formatter** ✅

### Status
- **Phase:** Formatter Hardening & Feature Completion
- **Runtime:** Frozen pending new bottleneck evidence
- **v0.5.0 Goal:** Production-ready formatter with --diff, --quiet, directory-wide formatting; verified idempotency across all repo .ail files; corrected lexer stability; lexer no longer hangs on unrecognized characters
- **Architecture Design:** ✅ Complete (FORMATTER_ARCHITECTURE.md)
- **Implementation:** ✅ **Complete** — see details below

### Key Design Decisions (DX-008)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Formatting engine | **AST-based** (parse → validate → reformat) | Preserves structure, allows validation in one pass |
| Configuration | **Zero** — single canonical style | Architecture-first per CTO direction; no config unless ≥2 benchmarks request |
| Comment handling | **Source-line tracking** with string-aware // detection | Preserves comment placement; avoids `//` inside strings (e.g., `https://`) |
| Error recovery | **Skip unrecognized chars with advance** | Lexer must never hang, even on invalid input |
| Semicolons | **Reinserted by formatter**; missing semicolons are not syntax errors | Parser recovers fully; formatter reinserts in output |

### DX-008 Deliverables

| Component | Status | Details |
|-----------|:------:|---------|
| FORMATTER_ARCHITECTURE.md | ✅ | Philosophy, existing architecture, limitations, v0.5 scope, stability release gate |
| SEMICOLON bug fix | ✅ | Filtered `reporter.diagnostics` from error messages; AST builder exception handler also filtered |
| Regression tests (SEMICOLON) | ✅ | Committed before fix per AILang standard |
| `--diff` mode | ✅ | Unified diff output for unformatted files |
| `--quiet` mode | ✅ | Suppresses all output; exit code only |
| Directory-wide formatting | ✅ | Recursive `.ail` discovery; skips hidden/venv/git dirs |
| Comment-only file preservation | ✅ | Files with only comments (no AST) no longer have comments dropped |
| Lexer stability | ✅ | 4 infinite-loop paths fixed (`:`, standalone `&`, standalone `\|`, invalid escape sequences) |
| String-aware inline comments | ✅ | `https://` inside strings no longer treated as comment start |
| Idempotency verification | ✅ | 165 valid `.ail` files pass format + idempotency (0 failures); 3 aspirational examples rejected (invalid map literals `{...}` — correct behavior) |
| Test suite | ✅ | 82 tests (50 formatter + 32 CLI) — all passing |

--------------------------------------

## Next Priority Queue

### v0.6.x — Engineering Benchmark Program

| # | Benchmark | Goal | Priority |
|:-:|-----------|------|:--------:|
| 1 | **B1** (AI Understanding) | ✅ Complete — framework, datasets, 44 tests, automated execution |
| 2 | **B1.1** (Provider Integration) | ✅ Complete — 4 providers, calibration, 37 tests, B1 extended |
| 3 | **B2** (Feature Implementation) | ✅ Complete — 3 levels (sum_even, pipeline, diff) in AILang + Python |
| 4 | **B3** (Bug Fix) | ✅ Complete — 5 bugs (off-by-one, undefined-id, guard, comparison, infinite) |
| 5 | **B4** (Refactoring) | ✅ Complete — rename + extract function, zero regressions |
| 6 | **B5** (Upgrade) | ✅ Complete — signature change, CLI conversion, zero regressions |
| 7 | **B6** (Maintenance) | ✅ Complete — multi-step feature add, edge case handling |
| 8 | **B7** (AI Context) | ✅ Complete — with-guide vs without-guide comparison (3× savings) |

### Maintenance
- 📋 **Documentation website** — Create hosted documentation site
- 📋 **PyPI package** — `pip install ailang`

---

## Forward-Looking Roadmap

> See `PRODUCT_ROADMAP.md` (canonical roadmap) for the complete milestone history and future plans.

| Milestone | Focus | Target |
|-----------|-------|:------:|
| **v0.6.0** | ✅ B1 Engineering Benchmark Framework | Previous |
| **v0.6.1** | ✅ B1.1 AI Provider Integration & Calibration | Current |
| **v0.6.x** | B2–B7 benchmark execution, evidence collection | Next |
| **v1.0** | Language freeze with full backward-compatibility guarantees | Planned |
| **Post-1.0** | Self-hosting, JIT, advanced features (evidence-driven) | Future |

--------------------------------------

## Backlog

### Future Ideas
- Language improvements (pending freeze review)
- IR optimizer (constant folding, DCE)
- Package manager (`ail init`, `ail install`)
- Reduced compile time for >1000 LOC

### Not Approved
- `string.join` — requires 10 LOC recursive implementation
- `list.sort` — requires 20 LOC selection sort
- `list.copy` — requires 15 LOC recursive implementation

*Requires ≥2 benchmarks requesting before consideration per GOVERNANCE.md*

### Waiting
- Wildcard imports (not in spec)

--------------------------------------

## Frozen Components

### Compiler
- IR generation (deterministic)
- Semantic analyzer (optimized)

### Runtime
- **Frozen** — RTO-001 implemented, no further changes until new bottleneck evidence
- v0.2.1 exception: `string_find`, `string_split` Python builtins added (10 LOC, no semantic changes)

### Language Spec
- **Frozen** — v0.1.x specification locked, no new keywords, grammar, or syntax changes

### Stdlib
- **Frozen** — v1.0 complete, additions require ≥2 benchmark requests
- v0.2.1 exception: `string.find`, `string.find_from`, `string.split` added per ADR-003 (evidence: 8+ independent reimplementations)

### Benchmarks
- Canonical suite locked (dice_roller, hangman_game, inventory_mgmt, kanban, static_analyzer)

--------------------------------------

## Recently Completed

| Item | Version | Date |
|------|---------|------|
| **v0.7.0** — Engineering Optimization — `file.listdir`, `convert.to_number` fix, `list.sum`, `list.find_by_key`. B2 L2: 3→1 iterations (67%). HYPOTHESIS_STATUS.md created. | v0.7.0 | 2026-07-07 |
| **v0.8.0** — Compiler Diagnostics Improvement — `file:line:col` source locations, SEM002 suggestions, multi-error reporting, JSON diagnostics enhanced. Semicolons optional. 308+ tests passing. | v0.8.0 | 2026-07-08 |
| **B2–B7** — Engineering Benchmark Evidence — 6 benchmarks (Feature Implementation, Bug Fix, Refactoring, Upgrade, Maintenance, AI Context) executed AILang vs Python — see ENGINEERING_EVIDENCE_REPORT.md | v0.6.2 | 2026-07-07 |
| **B1.1** — AI Provider Integration & Calibration — 4 providers (OpenAI, Anthropic, Google, Local), calibration module, B1 extended with provider abstraction, `python -m benchmarks calibrate` | v0.6.1 | 2026-07-07 |
| **B1** — Engineering Benchmark Framework — measurement infrastructure, 3 datasets, 44 tests, `python -m benchmarks {setup,b1,list,test}` | v0.6.0 | 2026-07-07 |
| **M19** — Documentation Canonicalization (consolidated PROJECT_VISION + PROJECT_PHILOSOPHY → VISION_AND_DIFFERENTIATION + CONSTITUTION; PRODUCT_ROADMAP.md canonical; benchmark methodology/evidence separated) | v0.5.0 | 2026-07-07 |
| **DX-008** — AILang Formatter — architecture, --diff, --quiet, dir-wide, lexer stability, string-aware comments, repo-wide idempotency (82 tests) | v0.5.0 | 2026-07-07 |
| **DX-007** — AILang Language Server — architecture, consolidation, symbol search, code actions (103 tests) | v0.4.0 | 2026-07-07 |
| **M16** — Documentation Architecture Cleanup (ADR fix, status consolidation, AI guidance, archive, .gitignore) | v0.3.1 | 2026-07-07 |
| **DX-006** — AILang Package Manager — implementation complete (manifest, init, install, lock, resolver) | v0.3.1 | 2026-07-07 |
| **M15** — Tooling Architecture & Package Manager Design (TOOLING_ARCHITECTURE.md + PACKAGE_MANAGER_DESIGN.md) | v0.3.1 | 2026-07-07 |
| **DX-005** — Test Generator — **Complete & Accepted** | v0.3.0 | 2026-07-07 |
| **DX-004** — Benchmark Runner — **Complete & Accepted** | v0.3.0 | 2026-07-07 |
| **tools/common/** — shared DX tooling library (+ hashing, discover_apps) | v0.3.0 | 2026-07-07 |
| **v0.3.0 Release Validation Report** | v0.3.0 | 2026-07-07 |
| **DX-003** — Static Analyzer — **Complete & Accepted** | v0.2.1 | 2026-07-07 |
| Stdlib: `string.find`, `string.find_from`, `string.split` (ADR-003) | v0.2.1 | 2026-07-07 |
| Static Analyzer Performance Optimization | v0.2.1 | 2026-07-07 |
| v0.2.1 Release Validation Report | v0.2.1 | 2026-07-07 |
| **DX-002** — `ail doctor` — **Complete & Accepted** | v0.2.1 | 2026-07-07 |
| **DX-001** — `ail context` — **Complete & Accepted** | v0.2.0 | 2026-07-06 |
| Runtime Optimization #001 — Variable Lookup Cache | v0.2.0 | 2026-07-06 |
| Compiler Bug Fix Sprint #001 | v0.1.2 | 2025-XX-XX |
| 10 Documentation guides created | v0.1.0 | 2025-XX-XX |
| Standard Library v1.0 (16 modules) | v0.1.0 | 2025-XX-XX |
| VS Code Extension | v0.1.0 | 2025-XX-XX |
| Official Formatter (`ail fmt`) | v0.1.0 | 2025-XX-XX |
| Language freeze declared (v0.1.x) | v0.1.0 | 2025-XX-XX |

--------------------------------------

## Known Issues

### Non-blocking
- Float literals rejected with LEX004 (intentional design decision)
- (resolved) DX-003 directory analysis timeout — now configurable via `--timeout` (default: 300s)

### Blocking
- None (runtime frozen, all tests passing)

--------------------------------------

## Decisions Waiting

| Decision | Status | Required Review |
|----------|--------|----------------|
| Runtime unfreeze for optimization | Pending | Community feedback on bottlenecks |
| Language unfreeze for improvements | Pending | Evidence from ≥6 benchmarks |
| Stdlib additions (join, sort, list.copy) | Pending | ≥2 independent benchmark requests |

--------------------------------------

## Release Progress

| Version | Status | Target |
|:-------|:-------|:-------|
| **v0.1.0** | ✅ Complete | Initial public release |
| **v0.1.1** | ✅ Complete | Documentation consolidation |
| **v0.1.2** | ✅ Complete | Bug fix sprint |
| **v0.2.0** | ✅ Complete | Runtime optimization |
| **v0.2.1** | ✅ Complete | DX-003 Static Analyzer, stdlib additions |
| **v0.3.0** | ✅ **Complete** | DX-004 Benchmark Runner + DX-005 Test Generator |
| **v0.4.0** | ✅ Complete | DX-007 Language Server |
| **v0.5.0** | ✅ **Complete** | DX-008 AILang Formatter — production-ready |
| **v0.6.0** | ✅ **Complete** | B1 Engineering Benchmark Framework |
| **v0.6.1** | ✅ **Complete** | B1.1 AI Provider Integration & Calibration |
| **v0.6.2** | ✅ **Complete** | B2–B7 Engineering Benchmark Execution — see ENGINEERING_EVIDENCE_REPORT.md |
| **v0.7.0** | ✅ **Complete** | Engineering Optimization Program — `file.listdir`, `convert.to_number` fix, `list.sum`, `list.find_by_key`. B2 L2: 3→1 iterations (67% reduction) |
| **v0.8.0** | ✅ **Complete** | Compiler Diagnostics Improvement Program — `file:line:col` source locations, spell-check suggestions (SEM002), multi-error collection, JSON diagnostics enhanced |
| **v1.0** | 📋 Planned | Full backward compatibility |

--------------------------------------

## Developer Rules

### Before writing code:

1. **DEVELOPMENT_STATUS.md** ← **READ THIS FIRST** (what is happening today)
2. **PROJECT_MEMORY.md** ← Project history (what happened before)
3. **AGENTS.md** ← AI bootstrap (mandatory rules)
4. **AILANG_DEVELOPMENT_PLAYBOOK.md** ← Dependency planning workflow
5. **ARCHITECTURE_DECISIONS.md** ← Why decisions were made
6. **LANGUAGE_SPEC.md** ← Language specification
7. **VISION_AND_DIFFERENTIATION.md** ← Project vision, hypothesis, and differentiation
8. **PROJECT_CONSTITUTION.md** ← Immutable rules
9. **Documentation Ownership Matrix** (below) ← Know where every doc type lives

### Validation Checklist (must pass before merge)

- [ ] Required documents read (§2 of AGENTS.md)
- [ ] Dependency graph created (Level 0 → N)
- [ ] Stdlib audited (no manual reimplementation of existing APIs)
- [ ] Guards verified (`map.has` before `map.get`, `list.len` before `list.get`, `&&` safe)
- [ ] Variable names unique across all functions
- [ ] `string.concat` has ≤2 args (use `+` for 3+)
- [ ] `let` has initializer
- [ ] `return` has value
- [ ] `ail build` passes
- [ ] `ail run` passes with correct output

--------------------------------------

## Flow

```
Current Work → Recently Completed → PROJECT_MEMORY → CHANGELOG
```

Every completed task follows this flow. Nothing gets lost.

--------------------------------------

## Documentation Ownership Matrix

| Topic | Canonical Document |
|-------|-------------------|
| **Vision** | `docs/governance/VISION_AND_DIFFERENTIATION.md` |
| **Constitution** | `docs/governance/PROJECT_CONSTITUTION.md` |
| **Roadmap** | `PRODUCT_ROADMAP.md` |
| **Current Status** | `DEVELOPMENT_STATUS.md` — this file |
| **History / Memory** | `PROJECT_MEMORY.md` |
| **Release History** | `CHANGELOG.md` |
| **Language Specification** | `docs/reference/LANGUAGE_SPEC.md` |
| **Language Tutorial** | `docs/reference/LANGUAGE_TOUR.md` |
| **Getting Started** | `docs/reference/GETTING_STARTED.md` |
| **Stdlib Reference** | `docs/reference/STDLIB_REFERENCE.md` |
| **AI Workflow** | `AGENTS.md` |
| **Development Playbook** | `docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md` |
| **Project Governance** | `docs/governance/GOVERNANCE.md` |
| **Architecture Decisions** | `docs/architecture/ARCHITECTURE_DECISIONS.md` (inline ADRs) + `docs/adr/ADR-*.md` (separate ADRs) |
| **Performance / Runtime** | `docs/performance/runtime_optimization_001/analysis.md` |
| **Tooling Architecture** | `docs/architecture/TOOLING_ARCHITECTURE.md` |
| **Package Manager Design** | `docs/architecture/PACKAGE_MANAGER_DESIGN.md` |
| **LSP Architecture** | `docs/architecture/LSP_ARCHITECTURE.md` |
| **Benchmarks (Methodology)** | `docs/ENGINEERING_BENCHMARK_PLAN.md` |
| **Benchmarks (Results)** | `docs/benchmarks/AILANG_BENCHMARK_WHITEPAPER.md` |
| **Benchmarks (Inventory vs Python)** | `docs/benchmarks/INVENTORY_PYTHON_COMPARISON.md` |
| **Benchmarks (Inventory Harness)** | `docs/benchmarks/INVENTORY_BENCHMARK_HARNESS.md` |

Every document type has exactly one owner. If you need to add information, first check which document owns it. If no document owns it, create a new owner file or add a row to this matrix.

--------------------------------------

## Last Updated

| Field | Value |
|:------|:------|
| **Date** | 2026-07-08 |
| **Version** | v0.8.0 |
| **Milestone** | Compiler Diagnostics Improvement Program |
