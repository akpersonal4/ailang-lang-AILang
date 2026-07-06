# AILang Roadmap

**Current status and forward-looking plans for AILang development.**

> This roadmap is subject to the governance process in [GOVERNANCE.md](GOVERNANCE.md).
> The v0.1.x language specification is **frozen** — no new keywords, grammar changes,
> syntax changes, semantic changes, or breaking changes are accepted during this phase.

---

## Current Status (v0.1.2 — Bug Fix Release)

- Compiler pipeline: **Complete and validated**
- Standard Library v1.0: **Complete** (16 modules, 60+ functions)
- Validation: **Complete** (522 tests, all quality gates passing)
- Documentation: **Complete** (canonical spec, full ecosystem guides, governance)
- VS Code extension: **Complete** (syntax highlighting, snippets, language config)
- Formatter: **Complete** (`ail fmt` — deterministic, idempotent, single canonical style)
- Language freeze: **Active** (v0.1.x — no syntax/grammar/semantic changes)
- Governance: **Complete** (GOVERNANCE.md, LANGUAGE_EVOLUTION.md, PROJECT_PHILOSOPHY.md)
- Real-world validation: **Complete** (56 AILang applications, all compile and run)
- Public release: **Current phase** (repository polish, GitHub readiness, release engineering)

---

## Short-Term (v0.1.x — Ecosystem & Tooling)

Focus: ecosystem growth, community building, tooling maturity.
Language remains frozen.

| Area | Priority | Status |
|------|----------|--------|
| Public GitHub release (v0.1.2) | Critical | ✅ Complete |
| Documentation website | High | 📋 Planned |
| LSP (Language Server Protocol) | High | 📋 Planned |
| Interactive REPL | Medium | 📋 Planned |
| PyPI package (`pip install ailang`) | Medium | 📋 Planned |
| Pre-built binaries (Windows, Linux, macOS) | Low | 📋 Planned |
| CI/CD pipeline with GitHub Actions | High | 📋 Planned |
| Community feedback collection | High | 📋 Planned |

---

## Medium-Term (v0.2.x — Evidence-Based Improvements)

After substantial real-world usage and community feedback.
Language may be unfrozen with evidence from actual users.

| Area | Priority | Status |
|------|----------|--------|
| Evidence-based language improvements | High | 📋 Pending freeze review |
| IR optimizer (constant folding, DCE) | Medium | 📋 Planned |
| Compiler performance profiling | Medium | 📋 Planned |
| Package manager (`ail init`, `ail install`) | Medium | 📋 Planned |
| Reduced compile time for >1000 LOC | Medium | 📋 Planned |

---

## Long-Term (v0.5.x → v1.0 — Ecosystem Maturity)

| Milestone | Goal |
|-----------|------|
| v0.5.x | Ecosystem maturity — LSP, package manager, REPL, documentation site, community |
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

### Compiler QA — Bug Fix Sprint #001 ✓

- [x] BUG-001: Empty return statement crash fixed
- [x] BUG-002: Missing initializer crash fixed
- [x] BUG-003: Module bare-name resolution fixed
- [x] BUG-004: Float literal LEX004 diagnostic added
- [x] BUG-005: Block scope shadowing fixed
- [x] BUG-006: Recursion limit increased
- [x] 522 tests passing (up from 521)
