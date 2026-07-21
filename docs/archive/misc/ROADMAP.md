# AILang Roadmap

**Current status and forward-looking plans for AILang development.**

> This roadmap is subject to the governance process in [GOVERNANCE.md](GOVERNANCE.md).
> The v0.1.x language specification is **frozen** — no new keywords, grammar changes,
> syntax changes, semantic changes, or breaking changes are accepted during this phase.

---

## Current Status (v0.3.0 — Developer Experience Automation)

| Area | Status |
|------|:------:|
| Compiler pipeline | **Complete and frozen** |
| Standard Library v1.0 | **Complete** (16 modules, 63+ functions) |
| Validation | **Complete** (772 tests, all quality gates passing) |
| Documentation | **Complete** (canonical spec, full ecosystem guides, governance) |
| Language freeze | **Active** (v0.1.x — no syntax/grammar/semantic changes) |
| Developer Experience | **DX-001 through DX-005 complete** — Context, Doctor, Analyzer, Benchmark, Test Generator |
| Project Phase | **Platform & Developer Experience Engineering** |

---

## v0.3.1 — Developer Experience Automation (DX-006)

Focus: Package management for the AILang ecosystem.

| # | Tool | Goal | Priority |
|:-:|------|------|:--------:|
| 1 | **DX-006** | Package Manager — `ail init`, `ail install`, dependency resolution | **Highest** |
| 2 | **DX-007** | LSP (Language Server Protocol) — editor intelligence | High |
| 3 | **DX-008** | Code Formatter (`ail fmt`) — formalize and harden | Medium |

---

## v0.3.0 — Developer Experience Automation ✅ Completed

| # | Tool | Status |
|:-:|------|:------:|
| 1 | **DX-004** | Benchmark Runner — **Complete & Accepted** |
| 2 | **DX-005** | Test Generator — **Complete & Accepted** |

---

## Medium-Term (v0.5.x — Ecosystem Maturity)

| Milestone | Goal |
|-----------|------|
| v0.5.x | Ecosystem maturity — full tooling suite, documentation site, community |
| v1.0 | Language freeze with full backward-compatibility guarantees |
| Post-1.0 | Self-hosting, JIT, advanced features (evidence-driven) |

---

## Completed Milestones

### Phase 1 — Core Compiler ✓

- [x] Repository structure, source model, diagnostics system
- [x] Lexer, parser, CST, AST
- [x] Semantic analysis, type checker, runtime interpreter, CLI

### Phase 2 — Standard Library v1.0 ✓

- [x] 16 modules: string, math, list, array, map, set, file, path, json, csv, time, random, environment, convert, io, system

### Phase 3 — App Validation ✓

- [x] 27 AILang application programs, all compile and run

### Phase 4 — Validation Sprint 1 ✓

- [x] 10 compiler validation examples, CLI auto-print bug fixed

### Phase 5 — Stdlib JSON/CSV ✓

- [x] JSON and CSV modules with parse/stringify

### Phase 5B — Performance, Memory & AI Validation ✓

- [x] Compile-time benchmarks (100–5000 LOC)
- [x] Memory benchmarks (<500MB at 5000 LOC)
- [x] Deterministic IR verification (SHA-256)
- [x] Stress tests (5000 LOC, 10000 LOC, 100 modules)
- [x] AI validation (23 programs, 100% first-pass)
- [x] Bug: `convert.to_string` no-op fixed

### Phase 6 — Developer Ecosystem Foundation ✓

- [x] 10 documentation guides, README with badges and stdlib table

### Phase 7 — Documentation Consolidation ✓

- [x] Canonical `LANGUAGE_SPEC.md`, 9 obsolete specs archived, doc fixes

### Phase 8 — Validation & Ecosystem Audit ✓

- [x] 144 code examples validated, all 16 stdlib modules tested, 5 apps validated, 28 stress tests, 25 benchmarks, 23 AI programs
- [x] 5 defects fixed (AST builder crash, CLI crash, doc errors)

### Phase 9 — VS Code Extension ✓

- [x] Extension with TextMate grammar, 9 snippets, language configuration

### Phase 10 — Official Formatter ✓

- [x] `ail fmt` with --check and --stdin, 27 formatter tests, 7 CLI tests

### Phase 11 — Dogfooding & Real-World Validation ✓

- [x] 56 AILang applications, `string.substring` stdlib addition, `env_args` fix
- [x] Language freeze declared, governance documents created

### Phase 12 — Public Release & Ecosystem Preparation ✓

- [x] Repository audit, GitHub readiness, release checklist
- [x] Documentation audit, example validation, installation validation
- [x] VS Code extension verification, CI/CD verification

### RTO-001 — Variable Lookup Cache ✓

- [x] `Environment.resolve()` caching — ~6× speedup on static analyzer
- [x] 102 regression tests, 624 total tests
- [x] Runtime frozen after optimization

### DX Foundation — Developer Experience Tools ✓

- [x] **DX-001** — `ail context` (AI onboarding context generator)
- [x] **DX-002** — `ail doctor` (repository health checker)
- [x] **DX-003** — `ail static_analyzer` (multi-file analysis, JSON/Markdown reports, self-analysis)
- [x] Stdlib additions: `string.find`, `string.find_from`, `string.split` (ADR-003)
- [x] 658 tests passing (up from 624)
- [x] v0.2.1 Release Validation Report completed

### v0.3.0 — Automation Milestone ✓

- [x] **DX-004** — `ail benchmark` (auto-discovery, suite modes, regression detection, CI-friendly exit codes)
- [x] **DX-005** — `ail testgen` (three-stage pipeline, intermediate TestCase model, 44 auto-generated test files)
- [x] `tools/common/` — shared DX tooling library (hashing, discover_apps, list_py_files, process, reporting)
- [x] 772 tests passing (up from 658)
- [x] v0.3.0 Release Validation Report completed
