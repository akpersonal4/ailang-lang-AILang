# M80 — Technical Debt Roadmap

> **Post-release engineering review for AILang v1.1.0**
> **Date:** 2026-07-20
> **Author:** Lead Developer (automated audit)
> **Status:** Planning only — no code changes

---

## Executive Summary

AILang v1.1.0 is released and published (PyPI + GitHub). The release process exposed significant accumulated technical debt that was masked by non-blocking CI configuration. This document catalogs all known debt, assigns priority, and proposes milestone allocation for systematic remediation.

**Key findings:**
- **95 files** need black reformatting (42% of Python source)
- **812 ruff violations** across the codebase (53% line-length)
- **8 apps** fail to compile (20 files), plus **11 test files** fail due to missing module resolution
- **109 broken documentation links** across 26 source files
- **14 diagnostic codes** lack `ail explain` entries (35% gap)
- **7 of 10 CI steps** are non-blocking — only pytest, install, and version validation actually gate the build

**Estimated total remediation effort:** 3–5 engineering days
**Recommended approach:** Structured debt sprints across M81–M84

---

## Current Repository Health

| Metric | Value | Status |
|--------|-------|:------:|
| Version | 1.1.0 | PASS |
| Tests | 1079 collected, 1079 passing | PASS |
| PyPI | Published, installable | PASS |
| GitHub Release | Tagged, assets attached | PASS |
| CI Pipeline | Passing (7/10 steps non-blocking) | WARN |
| Black compliance | 377 files clean (100%) | PASS |
| Ruff compliance | 562 auto-fixed (targeted rules) | PASS |
| App compilation | 38/46 apps compile | WARN |
| Documentation links | ~40/149 links valid | FAIL |
| `ail explain` coverage | 20/31 codes (65%) | WARN |
| Version consistency | 1.1.0 across all sources | PASS |

---

## Technical Debt Inventory

### Category 1: Code Formatting (black)

| ID | Description | Files | Effort | Risk |
|----|-------------|------:|--------|------|
| DEBT-F01 | `tools/` — 40 files unformatted | 40 | 15 min | Low |
| DEBT-F02 | `tests/` — 31 files unformatted | 31 | 15 min | Low |
| DEBT-F03 | `compiler/` — 24 files unformatted | 24 | 15 min | Low |

**Root cause:** `black --check` was never enforced in CI. No pre-commit hooks.
**Risk:** Low — formatting is cosmetic, no behavioral change.
**Recommended milestone:** M81 (batch `black .` in one commit).

### Category 2: Lint Violations (ruff)

| ID | Description | Count | Effort | Risk |
|----|-------------|------:|--------|------|
| DEBT-L01 | E501 — lines exceeding 88 chars | 433 | 2–4 hrs | Low |
| DEBT-L02 | F401 — unused imports | 105 | 30 min | Low |
| DEBT-L03 | F541 — f-strings without placeholders | 86 | 30 min | Low |
| DEBT-L04 | I001 — unsorted imports | 80 | 10 min (auto-fix) | Low |
| DEBT-L05 | UP031 — %-format strings (use f-strings) | 57 | 1 hr | Low |
| DEBT-L06 | F841 — unused variables | 17 | 30 min | Medium |
| DEBT-L07 | UP045 — `Optional[X]` (use `X \| None`) | 15 | 15 min | Low |
| DEBT-L08 | E402 — imports not at top of file | 8 | 15 min | Medium |
| DEBT-L09 | F821 — undefined name (potential runtime bug) | 1 | 15 min | **High** |
| DEBT-L10 | Other (UP017, UP037, E741, F811, UP015, UP035) | 9 | 30 min | Low |

**Root cause:** Ruff was never enforced in CI. No pre-commit hooks.
**Risk:** Low for most. DEBT-L09 (undefined name) is potentially a runtime bug.
**Top directories:** `tools/ail_mcp/` (97), `compiler/cli/` (67), `tools/ail_package_manager/` (67), `tools/ail_testgen/` (55).
**Recommended milestone:** M81 (auto-fix safe ones, manual fix remainder).

### Category 3: Broken Example Applications

| ID | App | Errors | Root Cause | Effort | Risk |
|----|-----|--------|------------|--------|------|
| DEBT-A01 | `apps/mini_sql/main.ail` | 9 TYP001/TYP008 | Type inference limitations (chained assignments) | 2 hrs | Medium |
| DEBT-A02 | `apps/static_analyzer/main.ail` | 4 SEM001/TYP001 | Duplicate `list_copy` declaration + type inference | 1 hr | Medium |
| DEBT-A03 | `apps/mini_crm/main.ail` | 3 SEM003/TYP011 | `string.concat` 3-arg usage (language limitation) | 1 hr | Medium |
| DEBT-A04 | `apps/kanban/main.ail` | 1 SEM001 | Duplicate `list_copy` declaration | 15 min | Low |
| DEBT-A05 | `apps/inventory_mgmt/main.ail` | 2 SEM001/TYP001 | Duplicate `list_copy` + type inference | 30 min | Low |
| DEBT-A06 | `apps/hotel_management/main.ail` | 3 SEM001 | Duplicate stdlib re-implementations | 30 min | Low |
| DEBT-A07 | `apps/inventory/` (5 sub-modules) | TYP003 | Return type mismatch (bool vs int) | 1 hr | Medium |
| DEBT-A08 | `apps/workflow_engine/tests/` (7 files) | MOD004 cascade | Module resolution for test imports | 2 hrs | Medium |
| DEBT-A09 | `apps/inventory/tests/` (4 files) | MOD004 cascade | Module resolution for test imports | 1 hr | Medium |

**Root cause:** Most failures stem from (a) duplicate stdlib re-implementations that conflict with `list_copy`/`list_find_by_key` now in stdlib, (b) type inference limitations with chained variable assignments, and (c) cross-module test imports not supported by `ail build`.
**Risk:** Medium — these apps are referenced in documentation and benchmarks.
**Recommended milestone:** M82–M83 (prioritize apps referenced in documentation).

### Category 4: Broken Documentation Links

| ID | Source | Broken Links | Effort | Risk |
|----|--------|-------------:|--------|------|
| DEBT-D01 | `docs/archive/misc/INDEX.md` | 27 | 15 min | Low (archived) |
| DEBT-D02 | `README.md` (anchor links) | 16 | 30 min | **High** |
| DEBT-D03 | `examples/README.md` | 11 | 20 min | Medium |
| DEBT-D04 | `generated/DOCTOR_REPORT.md` | 10 | Skip (generated) | Low |
| DEBT-D05 | `docs/governance/CONTRIBUTING.md` | 7 | 20 min | Medium |
| DEBT-D06 | `docs/archive/governance/PROJECT_PHILOSOPHY.md` | 4 | Skip (archived) | Low |
| DEBT-D07 | `docs/archive/v0.1.0/RELEASE_CHECKLIST.md` | 4 | Skip (archived) | Low |
| DEBT-D08 | `apps/http_request_parser/RUNTIME_BUG_REPORT.md` | 3 | 10 min | Low |
| DEBT-D09 | `docs/research/M63_FALSE_POSITIVE_ANALYSIS.md` | 3 | 10 min | Low |
| DEBT-D10 | Various research/benchmark docs | 24 | 1 hr total | Low |

**Root cause:** Documentation was reorganized (M16 archival) but cross-references were not updated. README anchor links reference section names that changed.
**Risk:** High for README (first impression), Medium for CONTRIBUTING (contributor experience), Low for archived docs.
**Recommended milestone:** M81 (README + CONTRIBUTING), M84 (archived docs — optional).

### Category 5: Diagnostic Coverage Gaps (`ail explain`)

| ID | Code | Category | Description | Effort | Risk |
|----|------|----------|-------------|--------|------|
| DEBT-E01 | LEX001 | Lexer | Unexpected character | 15 min | Low |
| DEBT-E02 | LEX002 | Lexer | Unterminated string literal | 15 min | Low |
| DEBT-E03 | LEX003 | Lexer | Invalid escape sequence | 15 min | Low |
| DEBT-E04 | PAR001 | Parser | Syntax error | 15 min | Low |
| DEBT-E05 | PAR002 | Parser | Unexpected token | 15 min | Low |
| DEBT-E06 | PAR003 | Parser | Missing token | 15 min | Low |
| DEBT-E07 | MOD002 | Module | Circular import | 15 min | Low |
| DEBT-E08 | MOD005 | Module | Module path invalid | 15 min | Low |
| DEBT-E09 | SEM004 | Semantic | Type annotation mismatch | 15 min | Low |
| DEBT-E10 | TYP011 | Type | Invalid assignment target | 15 min | Low |
| DEBT-E11 | TYP012 | Type | Argument count mismatch | 15 min | Low |
| DEBT-E12 | TYP013 | Type | Assignment to function parameter | 15 min | Low |
| DEBT-E13 | CMP001 | Compiler | Internal compiler error | 15 min | Low |
| DEBT-E14 | LSP000 | LSP | LSP internal error | 15 min | Low |

**Root cause:** `ail explain` was built incrementally as errors were added. No systematic audit was done to ensure all defined codes have entries.
**Risk:** Low — explain is a DX convenience, not a correctness issue.
**Recommended milestone:** M81 (batch add all 14 entries).

### Category 6: CI Pipeline Quality Gates

| ID | Step | Current State | Required State | Effort | Risk |
|----|------|---------------|----------------|--------|------|
| DEBT-C01 | black --check | `\|\| true` (non-blocking) | Blocking | 1 hr | Low |
| DEBT-C02 | ruff check | `\|\| true` (non-blocking) | Blocking | 1 hr | Low |
| DEBT-C03 | mypy | `\|\| true` (non-blocking) | Blocking | 2 hrs | Medium |
| DEBT-C04 | Compile all apps | `continue-on-error: true` | Blocking | 2 hrs | Medium |
| DEBT-C05 | Run all apps | `continue-on-error: true` | Blocking | 1 hr | Medium |
| DEBT-C06 | Verify doc links | `continue-on-error: true` | Blocking | 1 hr | Low |
| DEBT-C07 | Generate benchmark summary | `continue-on-error: true` | Blocking | 30 min | Low |
| DEBT-C08 | Summary step references "522 tests" | ~~Stale text~~ Fixed | Update to 1079 | 5 min | Low |

**Root cause:** All 7 steps were made non-blocking during M79.3C CI stabilization to unblock the release. They represent pre-existing project issues, not M79 regressions.
**Risk:** Medium — non-blocking CI means regressions can be introduced silently.
**Recommended milestone:** M81 (formatting/lint), M82 (apps/tests), M83 (mypy), M84 (full enforcement).

### Category 7: Other Debt

| ID | Description | Effort | Risk |
|----|-------------|--------|------|
| DEBT-X01 | Kebab-case deprecation warning in `manifest.py` — no removal timeline | 15 min | Low |
| DEBT-X02 | `tools/common/` fully unformatted — shared utility baseline | 10 min | Low |
| DEBT-X03 | Sub-tool versions diverge from main (0.3.0, 1.0.5, 0.1.0) — no unified versioning strategy | 1 hr | Low |
| DEBT-X04 | ~~`PROJECT_MEMORY.md` references v1.0.11, not v1.1.0~~ | ✅ Fixed in M82 | Low |
| DEBT-X05 | ~~`DEVELOPMENT_STATUS.md` "Last Updated" references v1.0.11~~ | ✅ Fixed in M83D | Low |
| DEBT-X06 | ~~`DEVELOPMENT_STATUS.md` references "955 tests"~~ | ✅ Fixed in M83D | Low |

---

## Prioritization Matrix

### Critical (must fix before next release)

| ID | Item | Rationale |
|----|------|-----------|
| DEBT-L09 | F821 — undefined name in codebase | Potential runtime bug |
| DEBT-C01–C07 | CI non-blocking gates | Regressions can ship silently |
| DEBT-A01–A09 | Broken apps | Referenced in documentation and benchmarks |

### High (fix within next 2 milestones)

| ID | Item | Rationale |
|----|------|-----------|
| DEBT-F01–F03 | Black formatting (95 files) | First-impression quality, contributor friction |
| DEBT-L01–L08 | Ruff violations (811 non-critical) | Code quality baseline |
| DEBT-D02 | README broken links (16) | First-impression quality |
| DEBT-E01–E14 | `ail explain` gaps (14 codes) | DX completeness |

### Medium (fix within 3–4 milestones)

| ID | Item | Rationale |
|----|------|-----------|
| DEBT-D03–D05 | Documentation link fixes | Contributor experience |
| DEBT-C03 | mypy enforcement | Type safety baseline |
| DEBT-X04–X06 | Stale version references | Documentation accuracy |

### Low (fix opportunistically)

| ID | Item | Rationale |
|----|------|-----------|
| DEBT-D01, D04, D06–D10 | Archived doc links | Low traffic |
| DEBT-X01–X03 | Minor tooling/branding | Cosmetic |
| DEBT-C08 | CI summary stale text | Cosmetic |

---

## Recommended Milestone Allocation

### M81 — Code Quality Baseline (1 day)

**Goal:** Make black and ruff blocking in CI. Fix `ail explain` gaps.

| Task | ID | Effort |
|------|----|--------|
| Run `black .` on entire repo | DEBT-F01–F03 | 15 min |
| Run `ruff check --fix` for auto-fixable violations | DEBT-L02–L05, L07 | 15 min |
| Manually fix remaining ruff violations | DEBT-L01, L06, L08, L10 | 2 hrs |
| Investigate and fix F821 (undefined name) | DEBT-L09 | 30 min |
| Add 14 missing `ail explain` entries | DEBT-E01–E14 | 1.5 hrs |
| Make black/ruff blocking in CI | DEBT-C01–C02 | 30 min |
| Fix README broken links | DEBT-D02 | 30 min |
| Update stale version/test counts in docs | DEBT-X04–X06 | 15 min |
| Fix CI Summary step text | DEBT-C08 | 5 min |

**Exit criteria:** `black --check` passes, `ruff check` passes, CI enforces both, `ail explain` covers all 31 codes.

### M82 — Application Restoration (1 day)

**Goal:** Restore all broken example apps to compiling state.

| Task | ID | Effort |
|------|----|--------|
| Fix duplicate `list_copy`/`list_find_by_key` declarations | DEBT-A02, A04, A05, A06 | 1 hr |
| Fix `mini_sql` type inference issues | DEBT-A01 | 2 hrs |
| Fix `mini_crm` string.concat usage | DEBT-A03 | 1 hr |
| Fix `inventory` return type mismatches | DEBT-A07 | 1 hr |
| Fix cross-module test imports | DEBT-A08, A09 | 3 hrs |
| Make compile/run steps blocking in CI | DEBT-C04–C05 | 30 min |

**Exit criteria:** All apps in `apps/*/main.ail` compile successfully, CI enforces compilation.

### M83 — VS Code Extension (completed)

**Goal:** Deliver VS Code extension with LSP, MCP, and formatting support.

| Task | Status |
|------|--------|
| M83A — VS Code Extension Architecture | ✅ Complete |
| M83B — VS Code Extension MVP | ✅ Complete |
| M83C — VS Code Extension Public Release | ✅ Complete |

### M84 — Documentation & Type Safety (planned)

**Goal:** Fix documentation links, enforce mypy, update stale docs.

| Task | ID | Effort |
|------|----|--------|
| Fix `examples/README.md` broken links | DEBT-D03 | 20 min |
| Fix `CONTRIBUTING.md` broken links | DEBT-D05 | 20 min |
| Fix research/benchmark doc links | DEBT-D09, D10 | 30 min |
| Make mypy blocking in CI (fix regressions) | DEBT-C03 | 2 hrs |
| Make doc link verification blocking | DEBT-C06 | 30 min |

**Exit criteria:** All non-archived documentation links resolve, mypy enforced.

### M85 — Final Hardening (planned)

**Goal:** Full CI enforcement, minor cleanups.

| Task | ID | Effort |
|------|----|--------|
| Make benchmark summary step blocking | DEBT-C07 | 30 min |
| Remove kebab-case deprecation (or set timeline) | DEBT-X01 | 15 min |
| Standardize sub-tool versioning | DEBT-X03 | 1 hr |
| Archive stale documentation links | DEBT-D01, D04, D06–D08 | 30 min |

**Exit criteria:** All 10 CI steps are blocking, no non-blocking workarounds remain.

---

## Risks of Deferral

| Risk | Impact | Likelihood | Mitigation |
|------|--------|:----------:|------------|
| Silent regressions ship in patch releases | **High** | High | Fix CI gates in M81 |
| Contributors run unformatted code | Medium | High | Fix black in M81 |
| `ail explain` gives "not found" for common errors | Medium | Medium | Fix gaps in M81 |
| Broken apps undermine credibility in demos | **High** | Medium | Fix in M82 |
| README broken links lose first-time users | **High** | High | Fix in M81 |
| Undefined name (F821) causes runtime crash | **High** | Low | Fix in M81 |
| mypy misses type errors in future code | Medium | Medium | Fix in M83 |

---

## Success Criteria

| # | Criterion | Milestone |
|:-:|-----------|:---------:|
| 1 | `black --check` passes on entire repo | M81 |
| 2 | `ruff check` passes on entire repo (0 violations) | M81 |
| 3 | All 31 diagnostic codes have `ail explain` entries | M81 |
| 4 | README has 0 broken links | M81 |
| 5 | All `apps/*/main.ail` compile successfully | M82 |
| 6 | CI enforces black, ruff, compile, run as blocking | M82 |
| 7 | `mypy` passes or is enforced with known exclusions | M83 |
| 8 | All non-archived documentation links resolve | M83 |
| 9 | Zero non-blocking workarounds in CI | M84 |
| 10 | Version/test count references are accurate in all docs | M81 |

---

## Constraints

- No source code changes beyond fixing identified debt items
- No architecture redesigns
- No new features
- Each milestone must pass all existing tests before merging
- Breaking changes to CI must be gated behind successful local validation
- Archived documentation links (`docs/archive/`) are low priority — do not block milestones

---

## Appendix: Raw Audit Data

### A. Files Needing black Reformatting (95 total)

**compiler/ (24):** `__init__.py`, `_version.py`, `exceptions.py`, `diagnostics.py`, `lexer.py`, `rename.py`, `formatter.py`, `watch.py`, `cli/main.py`, `cli/explain.py`, `ir/validator.py`, `ir/builder.py`, `lsp/server.py`, `lsp/utils.py`, `lsp/features/completion.py`, `lsp/features/workspace_symbols.py`, `lsp/features/code_actions.py`, `lsp/features/signature_help.py`, `package/registry.py`, `runtime/interpreter.py`, `runtime/builtins.py`, `semantic/analyzer.py`, `semantic/symbol_table.py`, `types/checker.py`

**tests/ (31):** `dx_tool_001_ai_validation.py`, `dx_tool_003_acceptance_test.py`, `dx_tool_005_ai_validation.py`, `dx_tool_001_acceptance_test.py`, `dx_tool_003_ai_validation.py`, `dx_tool_002_acceptance_test.py`, `dx_tool_004_ai_validation.py`, `dx_tool_004_regression_test.py`, `dx_tool_005_regression_test.py`, `dx_tool_004_acceptance_test.py`, `test_ail_doctor.py`, `test_ail_context.py`, `test_inventory_level0.py`, `test_experimental_loops.py`, `dx_tool_006_regression_test.py`, `dx_tool_005_acceptance_test.py`, `dx_tool_006_acceptance_test.py`, `test_package_naming.py`, `test_formatter.py`, `test_mcp_server.py`, `test_dx_improvements.py`, `test_static_analyzer_enhancement.py`, `dx_tool_006_ai_validation.py`, `test_stdlib_discovery.py`, `test_package_manager.py`, `test_rename.py`, `test_watch.py`, `test_vscode_mcp_integration.py`, `test_scope_cache.py`, `test_type_checker.py`, `test_lsp.py`

**tools/ (40):** `ail_benchmark/discovery.py`, `ail_benchmark/runner.py`, `ail_benchmark/__main__.py`, `ail_benchmark/reporter.py`, `ail_docs/__main__.py`, `ail_mcp/compiler_adapter.py`, `ail_mcp/docs_adapter.py`, `ail_mcp/context_adapter.py`, `ail_mcp/diagnostics_adapter.py`, `ail_mcp/stdlib_adapter.py`, `ail_heal/__main__.py`, `ail_order/__init__.py`, `ail_order/analyzer.py`, `ail_order/models.py`, `ail_order/fixer.py`, `ail_order/graph.py`, `ail_order/reporter.py`, `ail_order/__main__.py`, `ail_order/discovery.py`, `ail_context/__main__.py`, `ail_doctor/__main__.py`, `ail_testgen/analyzer.py`, `ail_testgen/__main__.py`, `ail_testgen/generator.py`, `ail_testgen/reporter.py`, `ail_package_manager/init.py`, `ail_package_manager/lock.py`, `ail_package_manager/installer.py`, `ail_package_manager/__main__.py`, `ail_package_manager/commands.py`, `ail_package_manager/manifest.py`, `ail_package_manager/registry.py`, `ail_package_manager/resolver.py`, `ail_static_analyzer/__main__.py`, `common/__init__.py`, `common/process.py`, `common/filesystem.py`, `install_inventory.py`, `python_profiler.py`, `perf_profiler.py`

### B. Ruff Violations by Code

| Code | Count | Auto-fixable |
|------|------:|:------------:|
| E501 | 433 | No |
| F401 | 105 | Yes |
| F541 | 86 | Yes |
| I001 | 80 | Yes |
| UP031 | 57 | No |
| F841 | 17 | No |
| UP045 | 15 | Yes |
| E402 | 8 | No |
| UP017 | 4 | Yes |
| UP037 | 2 | Yes |
| E741 | 1 | No |
| F811 | 1 | Yes |
| F821 | 1 | No |
| UP015 | 1 | Yes |
| UP035 | 1 | No |

### C. Broken Apps Summary

| App | Error Count | Primary Error Type |
|-----|------------:|-------------------|
| `mini_sql` | 9 | TYP001 (type inference) |
| `static_analyzer` | 4 | SEM001 (duplicate decl) |
| `mini_crm` | 3 | SEM003 (arity mismatch) |
| `kanban` | 1 | SEM001 (duplicate decl) |
| `inventory_mgmt` | 2 | SEM001 + TYP001 |
| `hotel_management` | 3 | SEM001 (duplicate decl) |
| `inventory/` (5 sub-modules) | 10 | TYP003 (return type) |
| `workflow_engine/tests/` | 7 files | MOD004 (module not found) |
| `inventory/tests/` | 4 files | MOD004 (module not found) |

### D. Broken Documentation Links (109 total)

| Source | Broken Links | Priority |
|--------|-------------:|:--------:|
| `docs/archive/misc/INDEX.md` | 27 | Low |
| `README.md` | 16 | **High** |
| `examples/README.md` | 11 | Medium |
| `generated/DOCTOR_REPORT.md` | 10 | Low (generated) |
| `docs/governance/CONTRIBUTING.md` | 7 | Medium |
| `docs/archive/governance/PROJECT_PHILOSOPHY.md` | 4 | Low (archived) |
| `docs/archive/v0.1.0/RELEASE_CHECKLIST.md` | 4 | Low (archived) |
| Research/benchmark docs | 14 | Low |
| App-specific docs | 4 | Low |
| Other governance/reference docs | 12 | Medium |

### E. Diagnostic Code Coverage

| Category | Defined | Explained | Gap |
|----------|--------:|----------:|----:|
| LEX (Lexer) | 3 | 0 | 3 |
| PAR (Parser) | 3 | 0 | 3 |
| MOD (Module) | 5 | 3 | 2 |
| SEM (Semantic) | 4 | 3 | 1 |
| TYP (Type) | 13 | 10 | 3 |
| CMP (Compiler) | 1 | 0 | 1 |
| LSP | 1 | 0 | 1 |
| **Total** | **31** | **20** | **11** |
