# DEVELOPMENT_STATUS.md

## DO NOT START DEVELOPMENT

until this document has been reviewed. Update AGENTS.md reading order after reviewing.

---

## Project Status

| Attribute | Value |
|:----------|:------|
| **Current Version** | v1.1.2 |
| **Current Milestone** | M83C — VS Code Extension Release |
| **Project Phase** | Public Beta |

### Maturity Assessment

| Area | Status |
|------|--------|
| Language | 100% |
| Compiler | 99.9% |
| Runtime | 99% |
| Formatter | 99% |
| Platform Services | 100% |
| Platform Integration | 100% |
| VS Code Extension | v1.1.0 — syntax highlighting, LSP, MCP integration, formatting, 12 commands, 10 settings |
| MCP Server | v1.2.0 — 6 tools, JSON-RPC 2.0 over stdio, 12 example categories |
| Documentation | 100% |
| Governance | 100% |
| Validation Framework | 100% |
| Reference Applications | 8 apps (todo, expense, inventory, employee, log_analyzer, csv_etl, json_transformer, invoice) |
| Test Suite | 1079 tests passing |

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

### MCP Server (M71)
- [x] `ail mcp` CLI command
- [x] JSON-RPC 2.0 over stdio transport
- [x] `get_language_context` tool — language rules, workflow, diagnostics
- [x] `get_stdlib` tool — module functions and signatures
- [x] `compile_source` tool — compile source, return diagnostics
- [x] `explain_diagnostic` tool — detailed error explanations
- [x] `get_examples` tool — canonical code examples
- [x] 14 MCP tests, all passing
- [x] Documentation: MCP_SERVER.md, MCP_QUICKSTART.md

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
- [x] **io** — write, writeln, println, read
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
- [x] VS Code Extension (syntax highlighting, diagnostics, go-to-definition, rename, hover, code actions, `for` keyword)
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

### Inventory Production Modules (M38)
- [x] **login.ail** — User authentication (plaintext passwords, session management, role-based guards)
- [x] **backup.ail** — Backup/restore (combined JSON backup, auto-backup before every write, backup listing)
- [x] **validation.ail** — Input validation (required fields, positive numbers, email format, uniqueness)
- [x] **import_csv.ail** — CSV import (products, customers, vendors, movements via `csv.parse_header`)
- [x] **integrity.ail** — Data integrity checking (JSON parse check, foreign key refs, negative stock detection)
- [x] **storage.ail** — Modified (auto-backup on save, corrupted JSON recovery, concurrent access lock)
- [x] **main.ail** — Modified (login/logout/backup/restore/backs/import/check commands + auth guards)
- [x] **config/users.json** — Default admin and staff accounts
- [x] **Test updates** — test_compile.py + tests/runner.py updated for new arg convention + auth flow
- [x] Build: ✅ | Test: 38/38 passing | E2E: All CLI commands verified

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

**M56/M57 — External Adoption Closure** ✅ Complete

### Status
- **Phase:** Package naming deadlock resolved + VS Code extension hardened
- **M56:** Snake-case package naming, `ail add/remove/update/list`, `ail new` generates `ail.toml`
- **M57:** VS Code extension v0.2.0, code action TextEdits, `for` keyword support
- **Test Results:** 176/176 tests passing (103 LSP + 19 naming + 13 commands + 41 CLI)
- **Commits:** `7cba4ef` (M56), `b38cd7e` (M57) — both on `develop` branch

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

## Next Priority

| Priority | Area | Key Deliverables |
|:--------:|------|------------------|
| **P0** | **M56 — Package Naming + Commands** | ✅ Snake-case naming, `ail add/remove/update/list`, `ail new` generates `ail.toml` — see "Recently Completed" |
| **P1** | **M57 — VS Code Extension** | ✅ Extension v0.2.0, code actions, `for` keyword support — see "Recently Completed" |
| **P2** | 90‑Day Production Validation (M40) | Continuous inventory run, collect bugs/fixes/incidents |
| **P3** | Official Examples Repository | 5 polished examples (Inventory, CRM, Ticket Management, HRMS, Legal Case Tracker) |

> Rationale: Package naming deadlock and VS Code extension hardening are complete. Next focus is production validation and example repositories.

## Forward-Looking Roadmap

> See `PRODUCT_ROADMAP.md` (canonical roadmap) for the complete milestone history and future plans.

| Milestone | Focus | Target |
|-----------|-------|:------:|
| **v1.0.0** | ✅ Release — benchmarks, daemon, language freeze, documentation | Current |
| **M54** | Package Registry MVP — `ail publish`, remote `ail install` | Next |
| **P1** | VS Code Extension — highlighting, diagnostics, LSP features | Future |
| **P2** | 90-Day Production Validation — continuous inventory run | Future |
| **P3** | Official Examples — 5 polished repos | Future |

--------------------------------------

## Backlog

### Future Ideas
- Language improvements (pending freeze review)
- IR optimizer (constant folding, DCE)
- Reduced compile time for >1000 LOC

### Not Approved
- ~~`string.join` — requires 10 LOC recursive implementation~~ ✅ Implemented (v0.7.0+)
- ~~`list.sort` — requires 20 LOC selection sort~~ ✅ Implemented (v0.7.0+)
- ~~`list.copy` — requires 15 LOC recursive implementation~~ ✅ Implemented (v0.7.0+)

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
| **M83C — VS Code Extension Public Release** — Packaged VSIX (19.73 KB), created GitHub Release v1.1.0-vscode, uploaded VSIX asset. Extension 1.1.0, LSP 1.1.0, VSIX 1.1.0. 13 files in package. | v1.1.0 | 2026-07-20 |
| **M83B — VS Code Extension MVP** — Wired formatter to LSP (formatting handlers, v1.1.0). Added format-on-save, 5 CLI commands (build/run/check/version/format), MVP settings. 5 new tests (108 total). | v1.1.0 | 2026-07-20 |
| **M83A — VS Code Extension Architecture** — Created `VSCODE_EXTENSION_ARCHITECTURE.md` (682 lines). Two-server design: LSP (deterministic IDE) + MCP (AI-assisted tools). 31 error codes mapped. Feature roadmap: MVP, Phase 2, Phase 3. | v1.1.0 | 2026-07-20 |
| **M82 — Developer Experience & Onboarding** — Created Quick Start guide (`docs/getting-started/QUICK_START.md`) and Onboarding Checklist (`docs/getting-started/ONBOARDING_CHECKLIST.md`). Fixed stale documentation across README.md, DEVELOPMENT_STATUS.md, PROJECT_MEMORY.md, and GETTING_STARTED.md. Updated test counts (894→1074), version badges (v1.0.11→v1.1.0), CLI command references (`ail hello.ail`→`ail run hello.ail`). | v1.1.0 | 2026-07-20 |
| **M81 — Formatting & Auto-fix Lint Baseline** — `black .` reformatted 248 files (270 total with M81.2). `ruff check --fix` fixed 562 violations (263 targeted rules): 239 unused imports, 86 f-string, 170 unnecessary parens, 56 trailing whitespace, 11 type annotations. Restored `find_manifest` re-export (false positive). 377 files black-clean, 377 ruff-clean for targeted rules. | v1.1.0 | 2026-07-20 |
| **M80 — Technical Debt Roadmap** — Created `docs/architecture/M80_TECHNICAL_DEBT_ROADMAP.md` (382 lines). Cataloged 7 debt categories, 4 milestone plan (M81–M84). Established formatting/lint baseline as prerequisite for all future work. | v1.1.0 | 2026-07-20 |
| **M79.3C — Version & Release** — Released v1.1.0 on GitHub and PyPI. Published `ailang-lang` package to PyPI. | v1.1.0 | 2026-07-20 |
| **M64 — AI-First Development Process Integration** — Integrated `ail check` into `ail run` and `ail test` as mandatory pre-flight step. `ail run` now auto-detects forward references before compilation; `ail test` auto-detects ordering violations before test execution. Both commands support `--no-check` flag for rare bypass. Updated documentation: DEVELOPMENT_PLAYBOOK.md, AGENTS.md, CONTRIBUTING.md, VISION_AND_DIFFERENTIATION.md. Official pipeline: write → fmt → check → build → test → run. | v1.0.0 | 2026-07-14 |
| **M63 — Pre-Flight Ordering Check Validation** — Implemented `ail check` command (350 LOC) that detects forward references, missing imports, and ordering violations. Tested against 173 files: 0% false positive rate, ~15ms per file. M59 replay: AILang correction cycles dropped from 8 to 5 (-37.5%), now 29% fewer than Python (5 vs 7). AILang/Python ratio: 1.14× → 0.71×. | v1.0.0 | 2026-07-14 |
| **M62 — AI Correction Cycle Root Cause Analysis** — Classified all 49 correction cycles (AILang 26, Python 23) across 7 benchmarks into 12 AICC categories. Key finding: forward references account for 38% of AILang cycles; 62% of AILang cycles are predictable/mechanical vs Python's 9% Recommended: `ail check` pre-flight ordering tool (200 LOC, eliminates 38% of cycles). After implementation, AILang drops to 0.70× Python's cycle count. | v1.0.0 | 2026-07-14 |
| **M60 — Security & Maintenance Olympics** — 10 security test cases + 8 maintenance operations across Ticket, Workflow, Inventory. Security: AILang 18/30 vs Python 18/30 (tie). Maintenance: AILang 26/40 vs Python 24/40 (AILang slight edge). AILang wins: SEC-005 (arity compile-time), SEC-008 (circular import compile-time). Python wins: SEC-001 (explicit KeyError), SEC-006 (len on string). | v1.0.0 | 2026-07-14 |
| **M59 — Large Application Validation** — Ticket System (1,371 AILang LOC, 44 tests) + Workflow Engine (1,262 AILang LOC, 38 tests). Full feature parity with Python (18/18 Ticket, 20/20 Workflow). 100% build + test pass. AILang correction cycles: 8 total vs Python 7 (1.14×). | v1.0.0 | 2026-07-13 |
| **P0 — Boilerplate Reduction** — `ail test` CLI (BRE 2.1×), safe `json.parse`, `list.filter_by_contains` (BRE 6.5×), `list.collect_key` (BRE 9.8×). Measured cumulative BRE: 2.7×. ~124 LOC added to compiler/stdlib, ~337 LOC removable from apps. | v1.0.0 | 2026-07-14 |
| **M57 — VS Code Extension Hardening** — Extension version synced to v0.2.0. Code action edits implemented (TextEdit operations for import stdlib, remove unused variable). `for` keyword added to grammar and LSP completions. Documentation: INSTALLATION.md, FEATURES.md, M57 report. 103/103 LSP tests passing. | v1.0.0 | 2026-07-13 |
| **M56 — External Adoption Closure** — Resolved snake-case package naming deadlock (kebab accepted with deprecation warning). Implemented `ail add/remove/update/list` commands. `ail new` now generates `ail.toml` + `ail.lock`. Added kebab-to-underscore normalization in resolver. 32 new tests (naming + commands), all passing. Documentation: QUICKSTART, PACKAGES, NAMING_POLICY. | v1.0.0 | 2026-07-13 |
| **M27 — Loop Capture Semantics** — Free variable detection + parameter threading + return-value capture for experimental `for-in` loops. 7 new tests, zero runtime changes. All canonical benchmarks pass. | v0.9.0 | 2026-07-10 |
| **M38 — Inventory Production Modules** — Built 5 missing production modules (login.ail, backup.ail, validation.ail, import_csv.ail, integrity.ail) totaling ~350 LOC of AILang. Modified storage.ail (auto-backup, recovery, lock) and main.ail (auth guards, command routing, new CLI commands). Created config/users.json. All 38/38 existing tests pass, all CLI commands verified end-to-end. The inventory system is now fully USABLE per M35 Production Plan. | v1.0.0-RC1 | 2026-07-10 |
| **M54 — Package Registry MVP** — `ail publish`, local `file://` registry, `ail install` (via `ail_package_manager`), transitive dependency resolution. Added `lib/` directory search path, package-directory module naming, multi-file package support. Full `pip install` → `ail new` → `ail publish` → `ail install` → `ail run` pipeline verified end-to-end. | v1.0.0 | 2026-07-13 |
| **Test Fix — inventory_level0** — Fixed 2 pre-existing test failures: replaced `string.to_string` → `convert.to_string` in helpers test; reordered functions in storage test to eliminate forward reference errors (`storage_find_first_rec`/`storage_apply_changes` before their callers). Both now pass. 724/724 tests clean. | v1.0.0 | 2026-07-13 |
| **M25/M26 — Experimental Loop Primitive** — `for item in collection { body }` lowered to recursive `__for_fn_N`; 12 files changed, 9 tests, `--experimental-loops` flag, full evaluation report. | v0.9.0 | 2026-07-09 |
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
- (resolved) Float literals now supported
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
| **v0.9.0** | ✅ **Complete** | Experimental Loop Primitive — `for-in` syntax, recursive lowering, variable capture semantics, evaluation report |
| **v1.0.0** | 📋 Planned | Full backward compatibility |
| **v1.0.0-M56** | ✅ Complete | External Adoption Closure — package naming, `ail add/remove/update/list` |
| **v1.0.0-M57** | ✅ Complete | VS Code Extension Hardening — v0.2.0, code actions, `for` keyword |

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
| **Date** | 2026-07-20 |
| **Version** | v1.1.2 |
| **Milestone** | M83C — VS Code Extension Release |
