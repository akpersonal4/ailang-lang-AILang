# Documentation Audit Report

**Audit of all Markdown documentation in the AILang repository.**

---

## 1. Documentation Inventory

Total Markdown files: **173** (excluding `node_modules/`, `.git/`, `.venv*/`, `__pycache__/`, `mypy_cache/`, `pytest_cache/`, `ruff_cache/`, `egg-info/`)

### 1.1 Root Project Documentation (10 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `README.md` | Project overview, quick start, stdlib table, badges | 6.2 KB | Primary entry point |
| `AGENTS.md` | AI agent bootstrap — mandatory reading order, hard rules, validation checklist | 4.3 KB | AI-consumable |
| `DEVELOPMENT_STATUS.md` | Operational status — completed items, current work, next priorities | 12.8 KB | **Stale: §Current Milestone still says v0.3.0/DX-005** |
| `PROJECT_MEMORY.md` | Institutional memory — milestones, ADRs, timeline, engineering history | 22.8 KB | Comprehensive |
| `CHANGELOG.md` | Release changelog (v0.1.0 → v0.3.0) | 13.8 KB | Well-maintained |
| `AUTHORS.md` | Project authors | 0.2 KB | Minimal |
| `CODE_OF_CONDUCT.md` | Contributor covenant | 2.3 KB | Standard template |
| `SECURITY.md` | Security policy | 1.0 KB | Standard template |
| `SUPPORT.md` | Support channels | 1.0 KB | Standard template |
| `IMPLEMENTATION_PLAN.md` | Root-level implementation plan | 2.2 KB | Orphaned — no cross-references |

### 1.2 Root-Level Transient Reports (2 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `DX_TOOL_001_REPORT.md` | DX-001 (ail context) acceptance report | 4.7 KB | Historical — should be archived |
| `DX_TOOL_002_REPORT.md` | DX-002 (ail doctor) acceptance report | 3.9 KB | Historical — should be archived |

### 1.3 Project Status Documents — `docs/` top-level (3 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `docs/CURRENT_MILESTONE.md` | Current milestone detail (v0.3.1 design phase) | 2.5 KB | Well-maintained, recently updated |
| `docs/PROJECT_PHASE.md` | Current project phase definition | 2.1 KB | Overlaps with DEVELOPMENT_STATUS.md |
| `docs/ROADMAP.md` | Forward-looking roadmap (v0.3.1 → v1.0) | 5.5 KB | Overlaps with DEVELOPMENT_STATUS.md §Next Priority Queue |

### 1.4 Architecture Documents — `docs/architecture/` (5 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `ARCHITECTURE_DECISIONS.md` | All 9 ADRs (ADR-001 through ADR-009) | 11.8 KB | **Canonical ADR source** |
| `MEMBER_ACCESS.md` | Member access syntax/grammar spec | 0.8 KB | Technical spec — distinct from ADR-001-member-access.md |
| `MODULE_SYSTEM.md` | Module system spec | 4.0 KB | Technical spec — distinct from ADR-002-module-system.md |
| `TOOLING_ARCHITECTURE.md` | DX tool architecture contract | 19.7 KB | New (this session) |
| `PACKAGE_MANAGER_DESIGN.md` | DX-006 package manager design spec | 22.4 KB | New (this session) |

### 1.5 ADR Documents — `docs/adr/` (3 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `ADR-010-member-access.md` | Decision: Member access precedes module system | 0.1 KB | Renamed from ADR-001 (collision resolved) |
| `ADR-011-module-system.md` | Decision: Module system architecture | 0.1 KB | Renamed from ADR-002 (collision resolved) |
| `ADR-012-string-find-split.md` | Decision: Add string.find/split to stdlib | 0.6 KB | Renamed from ADR-003 (collision resolved) |

### 1.6 Governance Documents — `docs/governance/` (6 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `GOVERNANCE.md` | Formal change proposal and review process | 12.1 KB | Canonical governance process |
| `PROJECT_PHILOSOPHY.md` | Design manifesto — why AILang exists, what it values | 9.5 KB | Distinct from GOVERNANCE — "why" vs "how" |
| `PROJECT_VISION.md` | High-level vision, mission, 3-phase roadmap | 2.8 KB | Overlaps with PROJECT_PHILOSOPHY.md (core principles) |
| `PROJECT_CONSTITUTION.md` | Immutable rules (10 hard rules) | 0.7 KB | **Overlaps with PROJECT_VISION.md "Core Principles"** |
| `LANGUAGE_EVOLUTION.md` | Feature request log (25+ entries) | 9.9 KB | Canonical decision record |
| `CONTRIBUTING.md` | Contributor onboarding and workflow | 5.1 KB | Practical setup instructions |

### 1.7 Guide Documents — `docs/guides/` (4 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `AILANG_DEVELOPMENT_PLAYBOOK.md` | Dependency planning, recursion patterns, error decoder | 14.9 KB | Canonical AI coding guide |
| `MASTER_ENGINEERING_PROMPT.md` | Complete engineering prompt for AI | 34.9 KB | Largest docs file — overlaps with Playbook |
| `FOR_FUTURE_AI.md` | 10-minute AI onboarding — all project knowledge | 7.2 KB | **Overlaps with PROJECT_MEMORY.md, AGENTS.md, Playbook** |
| `AI_MODEL_GUIDE.md` | Per-tool setup for Claude, GPT, Gemini, etc. | 3.3 KB | Unique — no other file covers this |

### 1.8 Reference Documents — `docs/reference/` (9 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `LANGUAGE_SPEC.md` | **Canonical language specification** | 26.9 KB | Single source of truth |
| `LANGUAGE_TOUR.md` | Tutorial-style language walkthrough | 11.1 KB | Overlaps with LANGUAGE_SPEC.md + GETTING_STARTED.md |
| `STDLIB_REFERENCE.md` | **Canonical stdlib API reference** | 11.7 KB | Single source of truth |
| `STDLIB_GAP_ANALYSIS.md` | Analysis of missing stdlib functions | 7.4 KB | Complementary to STDLIB_REFERENCE.md |
| `COMPILER_ARCHITECTURE.md` | Compiler pipeline and internal structure | 8.6 KB | Overlaps with LANGUAGE_SPEC.md §1.2 (pipeline diagram) |
| `FOLDER_STRUCTURE.md` | Project directory layout | 4.1 KB | Recently updated? |
| `GETTING_STARTED.md` | Beginner tutorial (Hello World → functions) | 6.7 KB | **Overlaps with LANGUAGE_TOUR.md** |
| `INSTALLATION.md` | Installation guide | 2.7 KB | Unique |
| `TESTING.md` | Test running guide and test directory overview | 7.5 KB | Unique |

### 1.9 Runtime Documents — `docs/runtime/` (5 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `optimizations.md` | **Master optimization registry** (RTO-001) | 6.8 KB | Canonical |
| `lookup_cache/design.md` | Variable lookup cache design | 7.3 KB | Overlaps with performance/ problem statements |
| `lookup_cache/implementation.md` | Cache implementation details | 5.4 KB | Unique implementation guide |
| `lookup_cache/benchmark.md` | Cache benchmark protocol and results | 7.3 KB | Overlaps with performance/ data |
| `lookup_cache/regression.md` | Cache regression test specification | 1.5 KB | Unique test spec |

### 1.10 Performance Investigation — `docs/performance/` (5 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `runtime_optimization_001/profile.md` | Raw cProfile data and methodology | 3.9 KB | **Problem stats duplicated in runtime/ 5+ times** |
| `runtime_optimization_001/analysis.md` | Root cause analysis | 6.8 KB | Unique analysis |
| `runtime_optimization_001/hotspots.md` | Hotspot ranking table | 5.2 KB | Unique ranked table |
| `runtime_optimization_001/feasibility.md` | Multi-option feasibility scoring | 1.0 KB | Unique |
| `runtime_optimization_001/recommendation.md` | Final recommendation | 6.2 KB | Unique |

### 1.11 Benchmark Documents — `docs/benchmarks/` (4 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `AI_BENCHMARK_ANALYSIS.md` | Cross-benchmark analysis | 17.2 KB | Comprehensive analysis |
| `AI_BENCHMARK_MATRIX.md` | Benchmark coverage matrix | 6.7 KB | Reference matrix |
| `AI_BENCHMARKS.md` | Individual benchmark results | 7.1 KB | Overlaps with matrix + analysis |
| `AILANG_BENCHMARK_WHITEPAPER.md` | Formal benchmark whitepaper | 39.4 KB | **Synthesizes all benchmark docs** |

### 1.12 Release Documents — `docs/releases/` (3 files)

| File | Purpose | Size | Notes |
|------|---------|:----:|-------|
| `RELEASE_PROCESS.md` | Formal release process | 4.8 KB | Canonical |
| `v0.2.1/RELEASE_VALIDATION.md` | v0.2.1 release validation report | 8.4 KB | Historical |
| `v0.3.0/RELEASE_VALIDATION.md` | v0.3.0 release validation report | 6.3 KB | Current release |

### 1.13 v0.1.0 Report Documents — `docs/archive/v0.1.0/` (21 files, archived M16)

| File | Purpose | Size |
|------|---------|:----:|
| `BACKWARD_COMPATIBILITY_REPORT.md` | Backward compatibility analysis | 6.6 KB |
| `BENCHMARK_VALIDATION_REPORT.md` | Benchmark validation | 3.1 KB |
| `CI_VALIDATION_REPORT.md` | CI/CD validation | 1.5 KB |
| `DIAGNOSTIC_AUDIT.md` | Diagnostic system audit | 5.0 KB |
| `DIAGNOSTICS_IMPROVEMENT_REPORT.md` | Diagnostics improvement plan | 2.2 KB |
| `DISTRIBUTION_CHECKLIST.md` | Distribution readiness checklist | 2.6 KB |
| `FINAL_ASSESSMENT.md` | Final v0.1.0 assessment | 2.1 KB |
| `FINAL_RELEASE_CHECKLIST.md` | Final release checklist | 2.7 KB |
| `FINAL_VALIDATION_REPORT.md` | Final validation report | 6.1 KB |
| `FORMATTER_FIX_REPORT.md` | Formatter bug fix report | 2.5 KB |
| `INSTALLATION_VALIDATION.md` | Installation testing results | 1.5 KB |
| `OPEN_SOURCE_READINESS.md` | Open source readiness audit | 3.7 KB |
| `PACKAGING_REPORT.md` | Packaging report | 3.1 KB |
| `PROJECT_AUDIT.md` | Full project audit | 8.0 KB |
| `PROJECT_CLEANUP_REPORT.md` | Cleanup report | 1.8 KB |
| `RELEASE_AUDIT_REPORT.md` | Release audit | 3.5 KB |
| `RELEASE_CHECKLIST.md` | Release checklist | 3.0 KB |
| `RELEASE_PACKAGING_AUDIT.md` | Packaging audit | 1.0 KB |
| `RELEASE_READINESS_v0.1.3.md` | v0.1.3 readiness assessment | 3.6 KB |
| `RELEASE_REPORT.md` | Release report | 6.6 KB |
| `RUNTIME_CHANGE_SUMMARY.md` | Runtime change summary | 5.4 KB |

**Verdict:** All 21 files are **historical sprint artifacts** from the v0.1.0 release sprint. They contain information that has been consolidated into permanent docs (DEVELOPMENT_STATUS.md, CHANGELOG.md, PROJECT_MEMORY.md).

### 1.14 Archive — `docs/archive/benchmarks/` (6 files)

| File | Purpose |
|------|---------|
| `APPLICATION_ANALYSIS.md` | Legacy application analysis |
| `APPLICATION_VALIDATION.md` | Legacy application validation |
| `CONSISTENCY_REVIEW.md` | Legacy consistency review |
| `DOCUMENTATION_AUDIT.md` | Legacy documentation audit |
| `LIBRARY_MANAGEMENT_BENCHMARK.md` | Legacy library management benchmark |
| `PUBLIC_API_AUDIT.md` | Legacy public API audit |

### 1.15 Archive — `docs/archive/misc/` (7 files)

| File | Purpose |
|------|---------|
| `ARCHITECTURE_DOCUMENTATION_REPORT.md` | Architecture documentation report |
| `DIAGNOSTICS_REVIEW.md` | Diagnostics review |
| `INDEX.md` | Obsolete documentation index |
| `POST_RELEASE_PLAN.md` | Post-release planning |
| `PRODUCT_ROADMAP.md` | Obsolete product roadmap |
| `PROJECT_CONCLUSION.md` | Project conclusion (from earlier phase) |
| `PYTEST_ENVIRONMENT_NOTE.md` | Pytest environment note |

### 1.16 Archive — `docs/archive/phases/` (7 files)

| File | Purpose |
|------|---------|
| `PHASE_5B_REPORT.md` | Phase 5B completion report |
| `PHASE_6_REPORT.md` | Phase 6 completion report |
| `PHASE_7_REPORT.md` | Phase 7 completion report |
| `PHASE_7B_REPORT.md` | Phase 7B completion report |
| `PHASE_8_REPORT.md` | Phase 8 completion report |
| `PHASE_9_REPORT.md` | Phase 9 completion report |
| `PHASE_10_REPORT.md` | Phase 10 completion report |

### 1.17 Archived Specifications — `archived/specifications/` (10 files)

| File | Purpose |
|------|---------|
| `ARCHIVED_README.md` | Explains this directory |
| `ir/IR_SPEC.md` | Obsolete IR specification |
| `language/LANGUAGE_SPEC.md` | Obsolete language spec (pre-canonical) |
| `lexer/LEXER_SPEC.md` | Obsolete lexer spec |
| `lexer_specification.md` | Duplicate lexer spec (root level) |
| `parser/AST_SPEC.md` | Obsolete AST spec |
| `parser/CST_SPEC.md` | Obsolete CST spec |
| `parser/GRAMMAR.md` | Obsolete grammar |
| `parser/PARSER_SPEC.md` | Obsolete parser spec |
| `stdlib_v1_final.md` | Obsolete stdlib design |

### 1.18 Application Documentation — `apps/*/` (27 files across 6 apps)

Only 6 of 43 apps have Markdown documentation:
- **hotel_management**: BENCHMARK_REPORT.md, DEVELOPMENT_LOG.md, EVOLUTION_FEEDBACK.md, IMPLEMENTATION_PLAN.md, README.md (5 files)
- **http_request_parser**: BENCHMARK_REPORT.md, DEVELOPMENT_LOG.md, EVOLUTION_FEEDBACK.md, PATCH_SUMMARY.md, RUNTIME_BUG_REPORT.md, UPDATED_EVIDENCE_MATRIX.md (6 files)
- **inventory_mgmt**: AI_EXPERIENCE_VALIDATION_REPORT.md, IMPLEMENTATION_PLAN.md (2 files)
- **kanban**: BENCHMARK_REPORT.md, DEVELOPMENT_LOG.md, DOCUMENTATION_REVIEW.md, FINAL_METRICS.md, IMPLEMENTATION_PLAN.md, PLAYBOOK_VALIDATION.md (6 files)
- **markdown_parser**: BENCHMARK_REPORT.md, DEVELOPMENT_LOG.md, EVOLUTION_FEEDBACK.md (3 files)
- **mini_sql**: BENCHMARK_REPORT.md, DEVELOPMENT_LOG.md, EVOLUTION_FEEDBACK.md, IMPLEMENTATION_PLAN.md (4 files)
- **static_analyzer**: IMPLEMENTATION_PLAN.md (1 file)

### 1.19 AI Benchmark Documentation — `ai_benchmarks/*/` (8 files across 3 benchmarks)

- **benchmark01_task_manager**: EXPECTED_OUTPUT.md, INPUT.md, README.md, RESULT.md (4 files)
- **benchmark02_sudoku_solver**: BENCHMARK_REPORT.md (1 file)
- **benchmark09_spreadsheet_engine**: BENCHMARK_REPORT.md, DEVELOPMENT_LOG.md, IMPLEMENTATION_PLAN.md (3 files)

### 1.20 Tool Documentation — `tools/` (3 files)

| File | Purpose |
|------|---------|
| `tools/ail_context/README.md` | Context tool README |
| `tools/ail_doctor/README.md` | Doctor tool README |
| `tools/ail_testgen/DESIGN.md` | Test generator design doc |

### 1.21 QA Test Documentation — `qa_tests/` (3 files)

| File | Purpose |
|------|---------|
| `BUG_REPORT.md` | Bug report for QA |
| `IMPACT_ANALYSIS.md` | Impact analysis |
| `REGRESSION_TEST.md` | Regression test results |

### 1.22 Generated Documentation — `generated/` (8 files + 1 JSON)

| File | Tool | Status |
|------|------|--------|
| `PROJECT_CONTEXT.md` | ail context (DX-001) | Regeneratable |
| `DOCTOR_REPORT.md` | ail doctor (DX-002) | Regeneratable |
| `STATIC_ANALYZER_REPORT.md` | ail static_analyzer (DX-003) | Regeneratable |
| `STATIC_ANALYZER_REPORT.json` | ail static_analyzer (DX-003) | Regeneratable |
| `TEST_GENERATION_REPORT.md` | ail testgen (DX-005) | Regeneratable |
| `TEST_GENERATION_REPORT.json` | ail testgen (DX-005) | Regeneratable |
| `benchmarks/BENCHMARK_REPORT.md` | ail benchmark (DX-004) | Regeneratable |
| `benchmarks/BENCHMARK_REPORT.json` | ail benchmark (DX-004) | Regeneratable |
| `regression_check.txt` | (not .md) | Regeneratable |

### 1.23 VS Code Extension — `extensions/vscode-ailang/` (2 files, excluding node_modules)

| File | Purpose |
|------|---------|
| `README.md` | Extension README |
| `CHANGELOG.md` | Extension changelog |

---

## 2. Statistics

| Category | Count | Notes |
|----------|:-----:|-------|
| **Total .md files** | **173** | Excluding node_modules, .git, venvs, caches, egg-info |
| Permanent project docs (root) | 10 | README, AGENTS, STATUS, MEMORY, CHANGELOG, etc. |
| Transient root reports | 2 | DX_TOOL_001_REPORT, DX_TOOL_002_REPORT |
| Status/roadmap (docs/ top-level) | 3 | CURRENT_MILESTONE, PROJECT_PHASE, ROADMAP |
| Architecture documents | 5 | Includes 2 new (this session) |
| ADR files (separate) | 3 | **Numbering collision with ARCHITECTURE_DECISIONS.md** |
| Governance documents | 6 | Constitution, Vision, Philosophy, Governance, Evolution, Contributing |
| Guide documents | 4 | Playbook, Master Prompt, FOR_FUTURE_AI, AI Model Guide |
| Reference documents | 9 | Language spec/tour, stdlib, compiler arch, folder structure, etc. |
| Runtime documents | 5 | Optimization registry + lookup_cache/ subdir |
| Performance investigation | 5 | runtime_optimization_001/ |
| Benchmark documents | 4 | Analysis, Matrix, Results, Whitepaper |
| Release documents | 3 | Process + validation reports |
| v0.1.0 sprint reports | 21 | **Largest single category of historical artifacts** |
| Archive (benchmarks) | 6 | Historical |
| Archive (misc) | 7 | Historical |
| Archive (phases) | 7 | Historical |
| Archived specifications | 10 | Obsolete pre-canonical specs |
| App-specific docs | 27 | Only 6 of 43 apps have docs |
| AI benchmark docs | 8 | Only 3 of 10 benchmarks have docs |
| Tool documentation | 3 | README + DESIGN.md |
| QA test documentation | 3 | Bug report, impact analysis, regression test |
| Generated docs (regeneratable) | 8 | All in `generated/` |
| VS Code extension | 2 | Extension README + changelog |
| **Permanent (non-historical, non-generated) .md** | **~74** | All docs/* files except archive/, reports/v0.1.0/ |

---

## 3. Source of Truth Matrix

| Topic | Authoritative Document | Also Found In | Duplication Issue |
|-------|----------------------|---------------|-------------------|
| **Language specification** | `docs/reference/LANGUAGE_SPEC.md` | LANGUAGE_TOUR.md, GETTING_STARTED.md, archived/specifications/language/LANGUAGE_SPEC.md | LANGUAGE_TOUR and GETTING_STARTED re-explain the same constructs at different detail levels |
| **Language tour / tutorial** | `docs/reference/LANGUAGE_TOUR.md` | GETTING_STARTED.md | GETTING_STARTED is a subset of LANGUAGE_TOUR |
| **Stdlib reference** | `docs/reference/STDLIB_REFERENCE.md` | DEVELOPMENT_STATUS.md (§Stdlib list) | STATUS reproduces the full module list verbatim |
| **Stdlib gap analysis** | `docs/reference/STDLIB_GAP_ANALYSIS.md` | PROJECT_MEMORY.md (§Known Gaps) | Overlap — both list missing functions |
| **Compiler architecture** | `docs/reference/COMPILER_ARCHITECTURE.md` | LANGUAGE_SPEC.md §1.2 | Pipeline diagram repeated |
| **Project folder structure** | `docs/reference/FOLDER_STRUCTURE.md` | None | Unique |
| **Installation** | `docs/reference/INSTALLATION.md` | CONTRIBUTING.md (§Setup) | CONTRIBUTING duplicates install steps |
| **Testing guide** | `docs/reference/TESTING.md` | None | Unique |
| **Current project status** | `DEVELOPMENT_STATUS.md` | PROJECT_PHASE.md, ROADMAP.md, CURRENT_MILESTONE.md | **Quadruple overlap** — all 4 track version, milestones, and DX tool status with potential staleness |
| **Project history** | `PROJECT_MEMORY.md` | CHANGELOG.md | Different level of detail (narrative vs changelog) — acceptable |
| **Architecture decisions** | `docs/architecture/ARCHITECTURE_DECISIONS.md` | docs/adr/ADR-001, ADR-002, ADR-003 | **Numbering collision** — separate ADR files use same numbers for different decisions |
| **Member access (technical)** | `docs/architecture/MEMBER_ACCESS.md` | docs/adr/ADR-010-member-access.md | Complementary (spec vs decision record) |
| **Module system (technical)** | `docs/architecture/MODULE_SYSTEM.md` | docs/adr/ADR-011-module-system.md | Complementary (spec vs decision record) |
| **Tooling architecture** | `docs/architecture/TOOLING_ARCHITECTURE.md` | (New) | Unique |
| **Package manager design** | `docs/architecture/PACKAGE_MANAGER_DESIGN.md` | (New) | Unique |
| **Governance process** | `docs/governance/GOVERNANCE.md` | PROJECT_CONSTITUTION.md, PROJECT_VISION.md | Constitution and Vision restate governance rules |
| **Project philosophy** | `docs/governance/PROJECT_PHILOSOPHY.md` | PROJECT_VISION.md | Vision overlaps on core principles |
| **Feature request log** | `docs/governance/LANGUAGE_EVOLUTION.md` | None | Unique |
| **Release history** | `CHANGELOG.md` | docs/releases/v0.2.1/RELEASE_VALIDATION.md, docs/releases/v0.3.0/RELEASE_VALIDATION.md | Release validation reports contain unique data (test counts, benchmarks), not pure duplication |
| **Release process** | `docs/releases/RELEASE_PROCESS.md` | None | Unique |
| **AI coding guide** | `docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md` | MASTER_ENGINEERING_PROMPT.md, FOR_FUTURE_AI.md, AGENTS.md | **Quadruple overlap** — all 4 contain similar "how to write AILang" instructions |
| **AI model setup** | `docs/guides/AI_MODEL_GUIDE.md` | None | Unique |
| **Runtime optimization registry** | `docs/runtime/optimizations.md` | lookup_cache/*, performance/* | **Problem statistics repeated 6+ times** across runtime/ and performance/ |
| **Roadmap** | `docs/ROADMAP.md` | DEVELOPMENT_STATUS.md (§Next Priority Queue), PROJECT_VISION.md (3-phase roadmap) | Triple overlap on future plans |

---

## 4. Benchmark Documentation

### 4.1 Benchmark Applications

| Count | Location | Description |
|:-----:|----------|-------------|
| **43** | `apps/*/main.ail` | Standard benchmark apps |
| **10** | `ai_benchmarks/*/main.ail` | AI benchmark suite |
| **3** | `ai_validation/*/main.ail` | Validation apps |
| **3** | `qa_tests/*.ail` | QA test apps |
| **Total: ~59** | | All compile and run |

### 4.2 Benchmark Reports (Permanent)

| File | Type | Notes |
|------|------|-------|
| `docs/benchmarks/AI_BENCHMARK_ANALYSIS.md` | Cross-app analysis | Permanent |
| `docs/benchmarks/AI_BENCHMARK_MATRIX.md` | Coverage matrix | Permanent |
| `docs/benchmarks/AI_BENCHMARKS.md` | Individual results | Permanent |
| `docs/benchmarks/AILANG_BENCHMARK_WHITEPAPER.md` | Formal whitepaper | Permanent — **synthesizes the other 3** |
| `docs/archive/benchmarks/CONSISTENCY_REVIEW.md` | Historical | Archived |
| `docs/archive/benchmarks/APPLICATION_ANALYSIS.md` | Historical | Archived |
| `docs/archive/benchmarks/APPLICATION_VALIDATION.md` | Historical | Archived |
| `docs/archive/benchmarks/DOCUMENTATION_AUDIT.md` | Historical | Archived |
| `docs/archive/benchmarks/LIBRARY_MANAGEMENT_BENCHMARK.md` | Historical | Archived |
| `docs/archive/benchmarks/PUBLIC_API_AUDIT.md` | Historical | Archived |

### 4.3 App-Specific Benchmark Reports (Historical)

6 apps have BENCHMARK_REPORT.md files embedded in the app directory:
- `apps/hotel_management/BENCHMARK_REPORT.md`
- `apps/http_request_parser/BENCHMARK_REPORT.md`
- `apps/kanban/BENCHMARK_REPORT.md`
- `apps/markdown_parser/BENCHMARK_REPORT.md`
- `apps/mini_sql/BENCHMARK_REPORT.md`
- `ai_benchmarks/benchmark02_sudoku_solver/BENCHMARK_REPORT.md`
- `ai_benchmarks/benchmark09_spreadsheet_engine/BENCHMARK_REPORT.md`

These are per-app historical artifacts. They are **not referenced** by any permanent document.

### 4.4 Generated Benchmark Artifacts

| File | Tool | Status |
|------|------|--------|
| `generated/benchmarks/BENCHMARK_REPORT.md` | ail benchmark (DX-004) | Regeneratable |
| `generated/benchmarks/BENCHMARK_REPORT.json` | ail benchmark (DX-004) | Regeneratable |

### 4.5 Baseline Files

No baseline files found. The benchmark runner's `--baseline` flag saves baselines to `generated/benchmarks/` but no baselines are committed.

---

## 5. Generated Documentation

| File | Tool | Should Be | Rationale |
|------|------|:---------:|-----------|
| `generated/PROJECT_CONTEXT.md` | ail context (DX-001) | **Regenerated on demand** | Snapshot of current project — stale when project changes |
| `generated/DOCTOR_REPORT.md` | ail doctor (DX-002) | **Regenerated on demand** | Per-run diagnostic output |
| `generated/STATIC_ANALYZER_REPORT.md` | ail static_analyzer (DX-003) | **Regenerated on demand** | Per-run analysis output |
| `generated/STATIC_ANALYZER_REPORT.json` | ail static_analyzer (DX-003) | **Regenerated on demand** | Per-run analysis output |
| `generated/TEST_GENERATION_REPORT.md` | ail testgen (DX-005) | **Regenerated on demand** | Per-run generation output |
| `generated/TEST_GENERATION_REPORT.json` | ail testgen (DX-005) | **Regenerated on demand** | Per-run generation output |
| `generated/benchmarks/BENCHMARK_REPORT.md` | ail benchmark (DX-004) | **Regenerated on demand** | Per-run benchmark output |
| `generated/benchmarks/BENCHMARK_REPORT.json` | ail benchmark (DX-004) | **Regenerated on demand** | Per-run benchmark output |
| `generated/regression_check.txt` | (manual) | **Regenerated on demand** | Per-run regression output |

**Recommendation:** Add `generated/` to `.gitignore`. None of these files should be version-controlled — they are regeneratable by running the respective tools.

---

## 6. Recommendations

### R1: Resolve ADR Numbering Collision ✅

**Problem:** `docs/adr/ADR-001-member-access.md`, `ADR-002-module-system.md`, `ADR-003-string-find-split.md` used numbers that collided with ADR-001 through ADR-003 inside `docs/architecture/ARCHITECTURE_DECISIONS.md`.

**Resolution:** Renamed to ADR-010, ADR-011, ADR-012 (the inline set stops at ADR-009). Updated cross-references in `docs/releases/v0.2.1/RELEASE_VALIDATION.md` and `AUDIT_REPORT.md`.

---

### R2: Consolidate Status Documents

**Problem:** Four documents track overlapping status information with staleness risk:
- `DEVELOPMENT_STATUS.md`
- `docs/PROJECT_PHASE.md`
- `docs/ROADMAP.md`
- `docs/CURRENT_MILESTONE.md`

**Recommendation:** Merge into two documents:
1. **`DEVELOPMENT_STATUS.md`** — Keep as the canonical status document. Move PROJECT_PHASE.md content here.
2. **`docs/ROADMAP.md`** — Keep as the forward-looking roadmap. CURRENT_MILESTONE.md content becomes a section of this.
3. Archive `docs/PROJECT_PHASE.md` and `docs/CURRENT_MILESTONE.md`.

**Benefits:** One place to update status. No staleness conflicts. 50% reduction in documents to maintain.
**Risk:** Low — all content already exists.
**Impact:** 4→2 files. ~100-line merge.

---

### R3: Consolidate AI Coding Guides

**Problem:** Four documents contain similar "how to write AILang code" instructions:
- `AGENTS.md`
- `docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md`
- `docs/guides/MASTER_ENGINEERING_PROMPT.md`
- `docs/guides/FOR_FUTURE_AI.md`

**Recommendation:** Keep the canonical content in two places:
1. **`AGENTS.md`** — AI bootstrap (hard rules, reading order, validation checklist). This is the entry point for every AI agent.
2. **`docs/guides/AILANG_DEVELOPMENT_PLAYBOOK.md`** — Detailed development guidance (dependency planning, recursion patterns, error decoder, performance engineering workflow).
3. Archive `MASTER_ENGINEERING_PROMPT.md` (it's a synthesis of the other docs) and `FOR_FUTURE_AI.md` (it's a subset of PROJECT_MEMORY.md + Playbook).

**Benefits:** Eliminates 4-way duplication. AI agents read AGENTS.md → Playbook. One canonical path.
**Risk:** Medium — MASTER_ENGINEERING_PROMPT.md is the largest guide (35KB) and may contain unique content. Audit needed before archiving.
**Impact:** 4→2 files. Requires content audit of MASTER_ENGINEERING_PROMPT.md.

---

### R4: Archive v0.1.0 Sprint Reports

**Problem:** 21 files in `docs/reports/v0.1.0/` were historical sprint artifacts from the v0.1.0 release. Their information has been consolidated into `DEVELOPMENT_STATUS.md`, `CHANGELOG.md`, and `PROJECT_MEMORY.md`.

**Resolution:** Moved to `docs/archive/v0.1.0/`. Files remain available for historical reference but no longer clutter the active documentation tree.

**Benefits:** Permanent docs directory shrinks by 21 files (26%). Reduces noise for readers.
**Risk:** Low — no permanent documents reference these files.
**Impact:** Move 21 files. Add one ARCHIVED_README.md. No content changes.

---

### R5: Add `generated/` to `.gitignore`

**Problem:** All files in `generated/` are regeneratable by DX tools but are not in `.gitignore`. They appear as untracked files in `git status`.

**Recommendation:** Add `generated/` to `.gitignore`.

**Benefits:** Clean `git status`. No risk of stale generated files being accidentally committed.
**Risk:** Low — all generated files are regeneratable. If a reference baseline is needed, commit it to `tests/baselines/` instead.
**Impact:** 1 line in `.gitignore`.

---

### R6: Consolidate Language Tutorials

**Problem:** `LANGUAGE_SPEC.md` (canonical spec), `LANGUAGE_TOUR.md` (tutorial), and `GETTING_STARTED.md` (beginner intro) all cover the same language features at different depths. Any grammar change requires updates to 3 files.

**Recommendation:** 
- Keep `LANGUAGE_SPEC.md` as the canonical spec (no change).
- Update `LANGUAGE_TOUR.md` to reference `LANGUAGE_SPEC.md` for formal definitions instead of re-explaining them.
- Consider archiving `GETTING_STARTED.md` if `LANGUAGE_TOUR.md` can serve both audiences, or retargeting it as a 5-minute quickstart that references the tour for details.

**Benefits:** Reduces spec drift risk. One grammar change = one file update.
**Risk:** Low — LANGUAGE_TOUR.md already references LANGUAGE_SPEC.md as the canonical source.
**Impact:** Moderate — LANGUAGE_TOUR.md would need trimming; GETTING_STARTED.md may be archived.

---

### R7: Consolidate Performance/Runtime Documentation

**Problem:** The same profiling statistics (85.4%, 1.6M calls, 144 depth, 230M steps) are repeated in 6+ files across `docs/runtime/` and `docs/performance/`. The `performance/` directory is the original investigation; `runtime/` is the implementation registry. Neither references the other.

**Recommendation:**
- In `docs/runtime/optimizations.md` and `docs/runtime/lookup_cache/design.md`, replace the inline problem statement with a cross-reference: "See `docs/performance/runtime_optimization_001/analysis.md` for the full profiling data."
- Keep the `performance/` directory as-is (it's an investigation archive).
- Keep summary numbers in the runtime docs for readability, but reduce to 1-2 sentences.

**Benefits:** Eliminates 5-way duplication. Single source of truth for profiling data.
**Risk:** Low — no content removed, only refactored.
**Impact:** Edit 2 files in `docs/runtime/` to add cross-references.

---

### R8: Archive App-Specific Benchmark Reports

**Problem:** 7 apps have `BENCHMARK_REPORT.md` or equivalent files embedded in their directories. These are historical artifacts from the benchmark development process and are not referenced by any permanent documentation.

**Recommendation:** Move app-specific benchmark reports to a centralized archive location, or remove them entirely if their content is captured in `docs/benchmarks/AILANG_BENCHMARK_WHITEPAPER.md`.

**Benefits:** Cleaner app directories. Less noise for new developers reading app code.
**Risk:** Low — 7 files, no cross-references.
**Impact:** Move or delete 7+ files.

---

### R9: Resolve Stale Version Reference in DEVELOPMENT_STATUS.md

**Problem:** `DEVELOPMENT_STATUS.md` line 14 still reads: *"Current Milestone: v0.3.0 — DX-005 Test Generator (Next)"* — but DX-005 is complete and CURRENT_MILESTONE.md says v0.3.1/design phase.

**Recommendation:** Update line 14 to: *"Current Milestone: v0.3.1 — DX-006 Package Manager (Design Phase)"*

**Benefits:** Corrects misinformation for readers. Consistent with CURRENT_MILESTONE.md.
**Risk:** None.
**Impact:** 1 line edit.

---

### R10: Consolidate Governance Overlap (Project Constitution vs Vision)

**Problem:** `PROJECT_CONSTITUTION.md` (10 immutable rules) and `PROJECT_VISION.md` (core principles) cover nearly identical ground with different language. The Constitution is authoritative but the Vision duplicates 80% of its content.

**Recommendation:**
- Make `PROJECT_CONSTITUTION.md` the single source of truth for immutable rules.
- In `PROJECT_VISION.md`, replace the "Core Principles" section with a reference: "See `PROJECT_CONSTITUTION.md` for the immutable rules that govern this project."

**Benefits:** One place to update project rules.
**Risk:** Low.
**Impact:** Edit PROJECT_VISION.md to remove/trim duplicated section.

---

## Summary of Recommendations

| # | Recommendation | Effort | Risk | Benefit |
|:-:|---------------|:------:|:----:|:--------|
| R1 | Resolve ADR numbering collision | 3 files | Low | Eliminates ambiguity |
| R2 | Consolidate status documents (4→2) | 4 files | Low | Single source of truth for status |
| R3 | Consolidate AI coding guides (4→2) | 4 files | Medium | Eliminates quadruple duplication |
| R4 | Archive v0.1.0 sprint reports | 21 files | Low | Reduces permanent doc count by 26% |
| R5 | Add `generated/` to `.gitignore` | 1 line | Low | Clean git status |
| R6 | Consolidate language tutorials | 3 files | Low | Reduces spec drift risk |
| R7 | Cross-reference performance/runtime docs | 2 files | Low | Single source for profiling data |
| R8 | Archive app-specific benchmark reports | 7 files | Low | Cleaner app directories |
| R9 | Fix stale version in DEVELOPMENT_STATUS.md | 1 line | None | Corrects misinformation |
| R10 | Consolidate governance overlap | 2 files | Low | Single source for rules |

**Total files affected:** ~48 moves + ~17 edits (estimate)  
**Total risk:** Low (all changes are moves, cross-references, or trims — no content deletion without archival)

---

*This report is an audit only. No files were created, renamed, moved, merged, or deleted.*
