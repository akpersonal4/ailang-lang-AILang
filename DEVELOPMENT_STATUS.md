# DEVELOPMENT_STATUS.md

## DO NOT START DEVELOPMENT

until this document has been reviewed. Update AGENTS.md reading order after reviewing.

---

## Project Status

| Attribute | Value |
|:----------|:------|
| **Current Version** | v0.3.0 |
| **Current Milestone** | v0.3.1 — DX-006 Package Manager (Architecture Design Complete) |
| **Project Phase** | Platform & Developer Experience Engineering |

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
- [x] Formatter with --check and --stdin modes
- [x] Bug Fix Sprint #001 (6 bugs fixed, 522→624 tests)

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
- [x] **list** — new, append, len, get, contains, remove, clear
- [x] **array** — new, push, len, get, contains, remove, clear
- [x] **map** — new, set, get, has, delete, keys, clear
- [x] **set** — new, add, contains, len, remove, clear
- [x] **file** — exists, read, write, append, remove
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

### Applications
- [x] apps/ — 27 applications validated
- [x] phase11/ — 29 applications validated
- [x] static_analyzer — self-analysis completes (931 lines, 75 functions, 209 calls)
- [x] Total: 66+ applications across CRUD, file processing, text manipulation

### Developer Tools
- [x] VS Code Extension (syntax highlighting, snippets, language config)
- [x] Deterministic formatter (`ail fmt`)
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
- [x] PROJECT_PHILOSOPHY.md
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

**DX-006 — Package Manager — Architecture Design Phase** 📋

### Status
- **Phase:** Tooling Architecture & Package Manager Design
- **Runtime:** Frozen pending new bottleneck evidence
- **v0.3.1 Goal:** Complete DX-006 (Package Manager) design and implementation
- **Architecture Design:** ✅ Complete & Accepted
- **Implementation:** 📋 Not started

### Architecture Milestone (M15) — Tooling Architecture & Package Manager Design

Before writing implementation code for DX-006, two architecture documents were created:

| Document | Purpose | Status |
|----------|---------|--------|
| `docs/architecture/TOOLING_ARCHITECTURE.md` | Architecture contract for all DX tools — CLI conventions, exit codes, JSON/MD report conventions, generated file policy, `tools/common/` responsibilities, testing strategy | ✅ Complete |
| `docs/architecture/PACKAGE_MANAGER_DESIGN.md` | Specification-first design — `ail.toml` manifest schema, dependency resolution algorithm, CLI commands, lock file, caching, checksum verification, integration with other DX tools | ✅ Complete |

### Key Design Decisions (DX-006)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Manifest format | **TOML** (`ail.toml`) | Python stdlib `tomllib`, human-readable, supports comments |
| Package sources | Local paths + Git repos (v1); official registry (future) | Minimal viable scope; registry requires infrastructure |
| Lock file | **TOML** (`ail.lock`), committed to VCS | Reproducible builds, fast install replay |
| Dependency resolution | **Backtracking**, semver ranges, highest-version preference | Consistent with Cargo/npm |
| Exit codes | 0=success, 1=failure, 3=internal error | Per TOOLING_ARCHITECTURE.md conventions |
| Cache | Project-local `.ail/cache/` (v1); global `~/.cache/ail/` (future) | Simple v1, no concurrency concerns |

### v0.3.1 Deliverables (Tooling Architecture + Package Manager Design)

- **Tooling Architecture Contract** (`docs/architecture/TOOLING_ARCHITECTURE.md`):
  12 sections covering tool layers, lifecycle, CLI conventions, exit code policy, JSON report conventions, generated file conventions, `tools/common/` responsibilities, shared utilities, discovery patterns, plugin/extension points, versioning policy, testing strategy
- **Package Manager Design Spec** (`docs/architecture/PACKAGE_MANAGER_DESIGN.md`):
  13 sections covering motivation, project manifest, package repository, dependency resolution, CLI commands (6: init, add, remove, install, update, list), lock file, cache, checksum verification, DX tool integration
- **10 Open Questions**: See `docs/architecture/PACKAGE_MANAGER_DESIGN.md §13` — must be resolved before implementation

### M16 — Documentation Architecture Cleanup (Current)

Before beginning DX-006 implementation, a documentation cleanup milestone was introduced:
- ADR numbering collision resolved (ADR-001→ADR-010, etc.)
- Status documents consolidated (PROJECT_PHASE.md, ROADMAP.md, CURRENT_MILESTONE.md → archived)
- AI guidance consolidated (see AGENTS.md)
- v0.1.0 sprint reports archived
- Generated files policy established (generated/ added to .gitignore)
- Performance data centralized
- Documentation Ownership Matrix created

--------------------------------------

## Next Priority Queue

### v0.3.1 — DX-006 Package Manager Implementation

 | # | Tool | Goal | Priority |
|:-:|------|------|:--------:|
| 1 | **DX-006** | Package Manager — `ail init`, `ail install`, dependency resolution | **Highest** |
| 2 | **DX-007** | LSP (Language Server Protocol) — editor intelligence | High |
| 3 | **DX-008** | Code Formatter (`ail fmt`) — formalize and harden | Medium |

### Maintenance
- 📋 **Community feedback collection** — Gather real-world usage data
- 📋 **Documentation website** — Create hosted documentation site
- 📋 **PyPI package** — `pip install ailang`

---

## Forward-Looking Roadmap

| Milestone | Focus | Target |
|-----------|-------|:------:|
| **v0.3.1** | DX-006 Package Manager — implementation | Current |
| **v0.5.x** | Ecosystem maturity — full tooling suite, docs site, community | Next |
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
- Source line numbers in errors (poor DX for large files)
- `ail fmt` spurious SEMICOLON error (formatter unusable on valid code)
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
| **M16** — Documentation Architecture Cleanup (ADR fix, status consolidation, AI guidance, archive, .gitignore) | v0.3.1 | 2026-07-07 |
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
- Source line numbers not included in error messages
- `ail fmt` false positive on SEMICOLON token in some edge cases
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
| **v0.3.1** | 📋 Architecture Design Complete | DX-006 Package Manager (Tooling Architecture + Package Manager Design docs) |
| **v0.5.x** | 📋 Planned | Ecosystem maturity |
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

## Last Updated

| Field | Value |
|:------|:------|
| **Date** | 2026-07-07 |
| **Version** | v0.3.1 |
| **Milestone** | M16 — Documentation Architecture Cleanup |
