# PRODUCT_ROADMAP

> **Canonical roadmap document.** One source of truth for what has been done,
> what is being done, and what is planned. No philosophy, no design principles,
> no historical narrative — only milestones and versions.

---

## Past: Completed Milestones

### Phase 1 — Core Compiler ✓
- Repository structure, source model, diagnostics system
- Lexer, parser, CST, AST
- Semantic analysis, type checker, runtime interpreter, CLI

### Phase 2 — Standard Library v1.0 ✓
- 16 modules: string, math, list, array, map, set, file, path, json, csv, time, random, environment, convert, io, system

### Phase 3 — App Validation ✓
- 27 AILang application programs, all compile and run

### Phase 4 — Validation Sprint 1 ✓
- 10 compiler validation examples, CLI auto-print bug fixed

### Phase 5 — Stdlib JSON/CSV ✓
- JSON and CSV modules with parse/stringify

### Phase 5B — Performance, Memory & AI Validation ✓
- Compile-time benchmarks (100–5000 LOC)
- Memory benchmarks (<500MB at 5000 LOC)
- Deterministic IR verification (SHA-256)
- Stress tests (5000 LOC, 10000 LOC, 100 modules)
- AI validation (23 programs, 100% first-pass)

### Phase 6 — Developer Ecosystem Foundation ✓
- 10 documentation guides, README with badges and stdlib table

### Phase 7 — Documentation Consolidation ✓
- Canonical `LANGUAGE_SPEC.md`, 9 obsolete specs archived, doc fixes

### Phase 8 — Validation & Ecosystem Audit ✓
- 144 code examples validated, all 16 stdlib modules tested

### Phase 9 — VS Code Extension ✓
- Extension with TextMate grammar, 9 snippets, language configuration

### Phase 10 — Official Formatter ✓
- `ail fmt` with --check and --stdin, 27 formatter tests, 7 CLI tests

### Phase 11 — Dogfooding & Real-World Validation ✓
- 56 AILang applications, `string.substring` stdlib addition, `env_args` fix
- Language freeze declared, governance documents created

### Phase 12 — Public Release & Ecosystem Preparation ✓
- Repository audit, GitHub readiness, release checklist
- Documentation audit, example validation, installation validation

### RTO-001 — Variable Lookup Cache ✓
- `Environment.resolve()` caching — ~6× speedup on static analyzer

### DX Foundation — Developer Experience Tools ✓
- **DX-001** — `ail context` (AI onboarding context generator)
- **DX-002** — `ail doctor` (repository health checker)
- **DX-003** — `ail static_analyzer` (static analysis, multi-file)

### v0.3.0 — Automation Milestone ✓
- **DX-004** — `ail benchmark` (benchmark runner)
- **DX-005** — `ail testgen` (test generator)
- `tools/common/` — shared DX tooling library

### v0.3.1 — Tooling & Docs ✓
- **DX-006** — AILang Package Manager (manifest, init, install, lock, resolver)
- **M15** — Tooling Architecture & Package Manager Design
- **M16** — Documentation Architecture Cleanup

### v0.4.0 — Language Server ✓
- **DX-007** — AILang LSP (Go to Definition, Hover, Completion, Diagnostics, References, Rename, Symbols, Code Actions) — 103 tests

### v0.5.0 — Production Formatter ✓
- **DX-008** — AILang Formatter (--diff, --quiet, directory-wide, lexer stability, string-aware comments, repo-wide idempotency) — 82 tests
- **M17** — Vision and Differentiation (evidence-driven strategic document)
- **M18** — Engineering Benchmark Plan (design-only methodology)
- **M19** — Documentation Canonicalization (this consolidation)

---

## Current: Active Work

**v0.5.0 (complete)** — DX-008 Formatter hardened and finalized.
**Next:** v0.6.x — Ecosystem Maturity.

---

## Future: Planned Milestones

| Milestone | Focus | Target |
|-----------|-------|:------:|
| **v0.6.x** | Ecosystem maturity — documentation site, PyPI package, community | Next |
| **v1.0** | Language freeze with full backward-compatibility guarantees | Planned |
| **Post-1.0** | Self-hosting, JIT, advanced features (evidence-driven) | Future |

### v0.6.x — Ecosystem Maturity
- Documentation website (hosted)
- PyPI package (`pip install ailang`)
- Community feedback collection
- Potential: LSP improvements, formatter CI integration

### v1.0 — Language Guarantee
- Full backward-compatibility guarantees
- Language specification frozen with no further changes without governance vote

### Post-1.0 — Advanced (Evidence-Driven)
- Self-hosting compiler
- JIT compilation
- Advanced features only if evidence from ≥6 benchmarks demands them

---

## Frozen Components

| Component | Freeze Status | Unfreeze Condition |
|-----------|---------------|-------------------|
| Language spec (v0.1.x) | Frozen — no syntax, grammar, or semantics changes | Evidence from ≥6 independent benchmarks |
| Compiler pipeline | Frozen | Evidence from ≥6 independent benchmarks |
| Runtime interpreter | Frozen | Evidence of new bottleneck |
| Standard library | Frozen — v1.0 complete | Evidence from ≥2 independent benchmarks |
| Benchmark suite | Frozen — canonical set locked | Project lead discretion |

---

## Related Documents

- [Development Status](DEVELOPMENT_STATUS.md) — Detailed current work and known issues
- [Governance](docs/governance/GOVERNANCE.md) — Proposal process and evidence bars
- [Language Evolution](docs/governance/LANGUAGE_EVOLUTION.md) — Feature request log
- [Changelog](CHANGELOG.md) — Release-by-release changes
