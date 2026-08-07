# PRODUCT_ROADMAP

> **Canonical roadmap document.** One source of truth for what has been done,
> what is being done, and what is planned. No philosophy, no design principles,
> no historical narrative — only milestones and versions.

## Roadmap Policy

Engineering milestones are planned internally.

Major feature milestones after v1.1.x are driven by evidence gathered during
A100 Community Validation rather than speculation.

> We do not invent features first. We validate needs first.

---

## Roadmap Summary

```
Completed
-----------
Language implementation
Tooling
Governance
Release engineering
Maintenance (v1.1.x)

Current
--------
A100 — Community Validation

Future
-------
v1.2.x (determined by community validation results)
```

---

## Completed

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
- `Environment.resolve()` caching — ~6x speedup on static analyzer

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

### v1.0.0-M56 — External Adoption Closure ✓
- **M56** — Snake-case package naming deadlock resolved, `ail add/remove/update/list` implemented, `ail new` generates `ail.toml` + `ail.lock`, kebab-to-underscore normalization in resolver

### v1.0.0-M57 — VS Code Extension Hardening ✓
- **M57** — Extension v0.2.0, code action TextEdits, `for` keyword in grammar and LSP, installation/feature documentation

### v1.0.5 — MCP Server + VS Code Integration ✓
- **M71** — MCP Server (5 tools, JSON-RPC 2.0 over stdio, AI tool integration)
- **M72** — VS Code Extension v0.3.0 (LSP + MCP dual-server, 7 commands, status bar, auto-launch)
- **M73** — 8 Reference Applications (todo, expense, inventory, employee, log_analyzer, csv_etl, json_transformer, invoice)

### v1.1.x — Maintenance & Verification Series ✓

Maintenance and external-review milestones culminating in the current release:

- **M127** — Runtime Diagnostics & Package Validation (structured diagnostics, type guards, new exit codes, wheel packaging verified)
- **M132** — Maintenance Verification (v1.1.14) — regression hardening across stdlib and type checker
- **M133** — Independent Engineering Response (v1.1.15) — response to external evaluation of v1.1.14
- **M134** — External Review Verification (v1.1.16) — SEM005/TYP001 fixes, ASCII diagnostics, version consistency
- **M135** — A100 Preconditions (v1.1.17) — wheel-install tooling fixes, bundled canonical apps, release gate + post-publication verification

**v1.1.16 (RC1) published** — 1128 tests passing, canonical benchmark 5/5 apps,
wheel + sdist built and verified from a fresh virtual environment, external
review verdict GO, released to PyPI and GitHub with assets SHA256-matched.

**v1.1.17 published** — 1217 tests passing, canonical benchmark 5/5 apps,
all four A100 wheel-install preconditions fixed and bundled apps shipped in the
wheel, `twine check` PASSED, fresh wheel-only venv verified (8/8 CLI checks),
released to PyPI + GitHub, post-publication verification from PyPI green.
A100 recruitment is now unblocked.

---

## Current

### A100 — Community Validation

First non-engineering milestone. Evaluates whether AILang's design produces
measurable advantages for AI-assisted business software development under real
usage conditions.

- **Preconditions:** first-impression fixes shipped (wheel-only `ail testgen`
  crash, `ail benchmark`/`ail static-analyzer` source-checkout requirement,
  `ail doctor` health score on wheel installs)
- **Protocol:** two-phase head-to-head (greenfield build + maintenance changes)
  against AI-assisted Python; "easier" and "would choose" recorded separately
- **Success criteria fixed before recruitment:** >= 5 participants, >= 5 useful
  apps, >= 3 maintenance phase, >= 3 would choose AILang again, 0
  release-blocking bugs
- **Governance:** community feedback identifies problems; governance determines
  solutions

Details: `docs/roadmap/A100_COMMUNITY_VALIDATION.md`.

---

## Future

- **v1.2.x** — determined by the results of A100 Community Validation, not by
  internal brainstorming. No major feature milestone is committed until
  evidence from real usage exists.
- Previously-listed post-1.0 items (self-hosting, JIT, advanced features)
  remain gated on the evidence bar below.

---

## Frozen Components

| Component | Freeze Status | Unfreeze Condition |
|-----------|---------------|-------------------|
| Language spec (v0.1.x) | Frozen — no syntax, grammar, or semantics changes | Evidence from >= 6 independent benchmarks |
| Compiler pipeline | Frozen | Evidence from >= 6 independent benchmarks |
| Runtime interpreter | Frozen | Evidence of new bottleneck |
| Standard library | Frozen — v1.0 complete | Evidence from >= 2 independent benchmarks |
| Benchmark suite | Frozen — canonical set locked | Project lead discretion |

---

## Related Documents

- [Development Status](../../DEVELOPMENT_STATUS.md) — Detailed current work and known issues
- [Governance](../governance/GOVERNANCE.md) — Proposal process and evidence bars
- [Language Evolution](../governance/LANGUAGE_EVOLUTION.md) — Feature request log
- [Changelog](../../CHANGELOG.md) — Release-by-release changes
- [A100 Community Validation](A100_COMMUNITY_VALIDATION.md) — Current milestone
