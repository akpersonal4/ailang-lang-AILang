# Changelog

## 0.8.0

### DX-006 — AILang Dependency Ordering Assistant (`ail order`)

- **Tool implementation**: `tools/ail_order/` — analyzes .ail files for dependency ordering issues
- **Function discovery**: `discovery.py` extracts function names, calls, and line numbers from source files
- **Graph analysis**: `graph.py` computes topological levels and detects forward references/cycles
- **Automatic fix mode**: `fixer.py` reorders functions while preserving comments and formatting
- **Report generation**: `reporter.py` produces Markdown and JSON reports for CI/LSP integration
- **CLI integration**: `ail order` command added to compiler CLI with `--json`, `--fix`, `--quiet`, `--stdout` flags
- **Detection capabilities**: 
  - Forward reference violations (function called before definition)
  - Circular function dependencies
  - Unreachable functions (not reachable from main)
  - Duplicate function declarations
- **Project analysis**: Full directory analysis with cross-file insights and report generation
- **12 acceptance tests**, 8 regression tests, 8 AI validation tests — all passing

## 0.4.0

### DX-007 — AILang Language Server

- **Architecture document**: `docs/architecture/LSP_ARCHITECTURE.md` — JSON-RPC, workspace model, document lifecycle, diagnostics pipeline, feature modules, performance goals, testing strategy
- **Shared AST utilities**: New `compiler/lsp/utils.py` consolidating 5× duplicated helpers (`walk_ast`, `find_node_at_offset`, `position_to_offset`, `node_range`, `find_references`, `find_enclosing_call`, `callee_name`, `member_access_name`, `find_definition_target`) into a single source of truth
- **Code duplication eliminated**: `definition.py`, `hover.py`, `references.py`, `rename.py`, `signature_help.py` all refactored to import from `utils.py` — 300+ lines of duplicated code removed
- **Workspace Symbol Search**: `workspace/symbol` implemented — cross-file symbol search with case-insensitive query matching across functions, variables, and imports
- **Code Actions foundation**: `textDocument/codeAction` — quick fix scaffolding for import errors, undefined stdlib references, and unused variable warnings
- **Server capabilities extended**: `workspaceSymbolProvider: true` and `codeActionProvider: true` added to initialize response
- **103 tests**, all passing (up from 99) — 4 new tests for workspace symbols and code actions

## 0.5.0

### DX-008 — AILang Formatter

- **Architecture document**: `docs/architecture/FORMATTER_ARCHITECTURE.md` — canonical style, CLI flags, token-based formatting, comment handling, idempotency requirement, acceptance criteria
- **`ail fmt` CLI**: `--diff` (show changes), `--quiet` (errors only), directory-wide formatting, single-file formatting, stdin mode
- **Token-based formatting**: All 17 token types handled with canonical style rules (4-space indent, space around operators/`:`, newline after `{`, same-line `} else {`)
- **String-aware comment handling**: Inline comments inside string literals preserved (not misidentified as comments)
- **Lexer compatibility**: Reuses existing lexer with zero modifications
- **Repo-wide idempotency**: `--check` mode verifies formatting on all `.ail` files; verified idempotent across the entire repository
- **82 tests**: 71 formatter tests + 11 CLI tests, all passing
- **Zero semantic changes**: no modifications to compiler, runtime, or language specification

### M19 — Documentation Canonicalization

- **Consolidated PROJECT_VISION.md + PROJECT_PHILOSOPHY.md** into `VISION_AND_DIFFERENTIATION.md`
- **Expanded PROJECT_CONSTITUTION.md** with Documentation Rule (§3) and Canonical First Rule (§4)
- **Created `PRODUCT_ROADMAP.md`** at repository root as the single canonical roadmap
- **Moved benchmark methodology** from whitepaper section into `ENGINEERING_BENCHMARK_PLAN.md`
- **Eliminated 7 obsolete/archive files** — ROADMAP.md, PRODUCT_ROADMAP.md (old), etc.
- **Canonical First Rule** added to AGENTS.md workflow and Constitution
- **Cross-references updated** across all affected documents

### Quality Gates

- **854 tests**, all passing (772 existing + 82 new formatter)
- DX-008 (ail fmt): PASS — 82 tests
- Documentation canonicalization: PASS — no broken links

## 0.7.0

### Engineering Optimization Program (Evidence-Driven Stdlib Evolution)

- **Evidence Analysis**: Reviewed B2–B7 benchmark data. Identified stdlib gaps as #1 friction source (42% of B2 errors).
- **`file.listdir(path)`**: New stdlib API returning sorted directory entries. Python `os.listdir()` backend. Available via `import file; file.listdir(path)`.
- **`list.sum(values)`**: New stdlib API returning sum of numeric list items. 3+ independent app pattern threshold met (STDLIB_GAP_ANALYSIS.md).
- **`list.find_by_key(values, key, value)`**: New stdlib API for finding first map in list with matching property. 3+ app threshold met.
- **`convert.to_number(value)`**: Fixed — was a no-op identity function. Now correctly converts string/int to integer (same semantics as `to_int`).
- **`docs/HYPOTHESIS_STATUS.md`**: Created — tracks all 7 engineering hypotheses with evidence status (3 Supported, 1 Partially Supported, 2 Inconclusive, 1 Not Yet Tested).
- **AGENTS.md updated**: Removed `convert.to_number` no-op pitfall. Updated missing stdlib list to reflect available APIs.
- **STDLIB_REFERENCE.md updated**: Added documentation for all 4 new/changed APIs. Updated "Known Missing Operations" section.

### Measured Improvement

| Metric | Before (v0.6.x) | After (v0.7.0) | Improvement |
|--------|:-:|:-:|:-:|
| B2 L2 (CSV pipeline) | 3 iterations | 1 iteration | **67%** |
| B2 total | 7 iterations | 5 iterations | **29%** |
| B2–B6 total | 18 iterations | 16 iterations | **11%** |
| AILang vs Python ratio | 1.38× | 1.23× | **11% closer** |

### Quality Gates

- All new APIs verified: `file.listdir`, `list.sum`, `list.find_by_key`, `convert.to_number` — build+run confirmed
- Existing test suite: 18 stdlib tests pass, zero regressions
- ENGINEERING_EVIDENCE_REPORT.md: updated with before/after comparison
- HYPOTHESIS_STATUS.md: created with evidence references
- All P0 APIs implemented (no scope changes)

## 0.6.2

### B2–B7 — Engineering Benchmark Execution

- **B2 Feature Implementation**: 3 levels (sum_even, CSV pipeline, file diff) in AILang + Python — AILang 2.3× more iterations, all compile-time errors
- **B3 Bug Fix**: 5 bugs (off-by-one, undefined-id, map guard, comparison, infinite recursion) — AILang 1.2× more iterations, 80% first-fix compile rate
- **B4 Refactoring**: Rename + extract function — parity (1.0×), zero regressions in both languages
- **B5 Upgrade**: Signature change + CLI conversion — parity (1.0×), zero regressions
- **B6 Maintenance**: Multi-step feature addition with edge-case handling — parity (1.0×)
- **B7 AI Context**: Structured guide (AGENTS.md + Playbook) saves 3× iterations (1 vs 3 compile-fix cycles)
- **15 benchmark artifacts** created: 5 bug-fix files, naive-without-guide comparison, 2 task specs, 10 code modifications
- **Key stdlib gaps identified**: no `!=` operator, no `listdir`, `convert.to_number` is no-op
- **Evidence published**: `ENGINEERING_EVIDENCE_REPORT.md` with method, datasets, raw results, summary table, and cost model

### Quality Gates

- **ENGINEERING_EVIDENCE_REPORT.md**: PASS — all 6 benchmarks documented with measurements
- B2–B7 artifacts: PASS — all build+run verified

## 0.6.1

### B1.1 — AI Provider Integration & Calibration

- **Provider abstraction**: `benchmarks/providers/base.py` — `AIProvider` abstract base class with `complete(prompt)`, `count_tokens(text)`, and `ProviderResult` data model capturing all measurements (request, prompt, response, timing, interaction, cost)
- **4 provider implementations**:
  - `OpenAIProvider` — GPT-4o, GPT-4, GPT-3.5 (requires `openai` + `tiktoken`)
  - `AnthropicProvider` — Claude 3, Claude 3.5 (requires `anthropic`)
  - `GoogleProvider` — Gemini 1.5, Gemini 2.0 (requires `google-generativeai`)
  - `LocalProvider` — Ollama, vLLM, llama.cpp via OpenAI-compatible API (requires `openai`)
- **Provider factory**: `create_provider(name, model, ...)` with registry and auto-detection from environment variables
- **Calibration module**: `benchmarks/calibration/` — runs identical prompts (short_response, code_understanding, token_counting) across all configured providers to validate measurement infrastructure. Generates immutable calibration reports.
- **B1 extended**: Three priority modes for token measurement — (1) AIProvider for accurate tokenizer + comprehension prompt, (2) manual `ai_results` dict, (3) approximate 4-char heuristic. B1 version bumped to 0.2.0.
- **CLI**: `python -m benchmarks calibrate` and `python -m benchmarks list-providers`
- **Optional dependencies**: Added `[openai]`, `[anthropic]`, `[google]`, `[local]`, `[all]` extras to pyproject.toml
- **37 new tests**: ProviderResult serialization, interface contract, factory, mocked provider implementations (all 4), token estimation, cost estimation, B1 provider integration, calibration execution, schema stability
- **81 tests total** in benchmarks/tests/ (44 existing + 37 new)

### Quality Gates

- **935 tests**, all passing (898 existing + 37 new provider/calibration)
- Provider interface: PASS — all ABC methods implemented, serialization roundtrip verified
- Calibration: PASS — runs against mock providers, reports errors correctly, serializable output

## 0.6.0

### B1 — Engineering Benchmark Framework

- **Generic measurement framework**: `benchmarks/framework/` — runner, metrics, environ, reporting, dataset modules — reusable by B2-B7
- **3 canonical datasets**: small (compiler only), medium (stdlib + docs), current_repo (full repository)
- **Dataset scanning**: Deterministic metadata generation with SHA-256 content hash and repeatability hash
- **Repository metrics**: Full structural analysis (files, LOC, function count, variable count, import count, dependency depth, symbol density, comment ratio, nesting depth, cyclomatic complexity)
- **AI comprehension metrics**: Token estimate, context window utilization, comprehension accuracy (placeholder for future AI integration)
- **Immutable historical results**: Each run stored in `benchmarks/results/<benchmark>/run_<timestamp>/` with measurements, environment snapshot, and human-readable report
- **Summary aggregation**: `benchmarks/results/summary.json` with all runs across all datasets
- **CLI**: `python -m benchmarks {setup,b1,list,test}`
- **44 tests**: 4 runner, 8 dataset, 13 metrics, 9 reporting, 10 B1 integration — all passing
- **Run IDs**: Timestamp-based, sortable, unique
- **.gitignore**: `benchmarks/results/` excluded (runtime artifacts); datasets remain version-controlled

### Quality Gates

- **898 tests**, all passing (854 existing + 44 new B1 framework)
- B1 smoke test: PASS against small, medium, current_repo datasets
- All 3 datasets scan, validate, and produce metrics

## 0.3.1

### DX-006 — AILang Package Manager

- **Manifest parser**: `ail.toml` parsing via `tomllib` with full validation (package name, semver, dependency format)
- **`ail init`**: Project initialization — creates `ail.toml`, `main.ail` stub, and `ail.lock`
- **Local package support**: `path=` dependencies resolved, copied to `lib/<name>/`, full transitive dependency support
- **Git package support**: `git=` dependencies shallow-cloned, tag/branch/rev checkout, transitive support
- **Dependency resolver**: Recursive resolution with topological sort and circular dependency detection
- **Lock file**: `ail.lock` with TOML format, versioned schema, `input_hash` staleness detection, fast replay
- **Checksum verification**: SHA-256 integrity hashing for all installed packages
- **Installation engine**: Full orchestration with `--no-lock`, `--offline`, `--frozen-lockfile` flags
- **Exit codes**: Per TOOLING_ARCHITECTURE.md conventions (0=success, 1=failure, 3=internal error)
- **Acceptance tests**: 8/8 tests passing covering init, parse, install, and lock file generation
- **Documentation**: PACKAGE_MANAGER_DESIGN.md approved, tool README created

### M16 — Documentation Architecture Cleanup

- **ADR collision resolved**: Separate ADR files renumbered ADR-001/002/003 → ADR-010/011/012
- **Status duplication eliminated**: PROJECT_PHASE.md, ROADMAP.md, CURRENT_MILESTONE.md archived; DEVELOPMENT_STATUS.md now canonical
- **AI guidance consolidated**: MASTER_ENGINEERING_PROMPT.md, FOR_FUTURE_AI.md archived; AGENTS.md canonical
- **v0.1.0 sprint reports archived**: 21 files moved to `docs/archive/v0.1.0/`
- **`generated/` added to `.gitignore`**: 9 tracked generated files removed from git tracking
- **Documentation Ownership Matrix created**: 15 document types with canonical owners
- **Cross-references updated**: RELEASE_PROCESS.md, AI_MODEL_GUIDE.md, PROJECT_MEMORY.md

## 0.1.0

### Standard Library v1.0

- **json** — `parse(text)`, `stringify(value)` using Python `json` backend
- **csv** — `parse(text)`, `parse_header(text)`, `stringify(rows)` using Python `csv` backend
- **time** — `now()`, `timestamp()`, `sleep(ms)`, `format(ts)`
- **environment** — `get(name)`, `cwd()`, `args()`
- **random** — `int(min, max)`, `float()`, `choice(collection)`
- **file** — `exists(path)`, `read(path)`, `write(path, content)`, `append(path, content)`, `remove(path)`
- **path** — `join(a, b)`, `basename(path)`, `dirname(path)`, `extension(path)`, `normalize(path)`
- **collections** — `array`, `list`, `map`, `set` with `new`, `get`, `set`, `add`, `contains`, `remove`, `clear`, `keys`, `len`
- **string** — `concat`, `equals`, `uppercase`, `lowercase`, `length`, `contains`, `starts_with`, `ends_with`, `trim`
- **math** — `add`, `sub`, `mul`, `div`, `abs`, `min`, `max`
- **io** — `write`, `writeln`, `println`
- **convert** — `to_string`, `to_int`, `to_bool`, `to_number`
- **system** — `exit`

### Performance, Memory & AI Validation (Phase 5B)

- **Stress tests**: 5000 LOC, 10000 LOC, 50 modules, 100 modules
- **Compile-time benchmarks**: 100/500/1000/5000 LOC with <60s thresholds
- **Memory benchmarks**: LOC-based with <500MB threshold at 5000 LOC
- **Determinism**: IR SHA-256 hash verification across 3 compiles
- **AI validation**: 23 programs generated from public docs, 100% first-pass success
- **Defect fix**: `convert.to_string` was a no-op; added `__native_to_string` builtin

### Developer Ecosystem Foundation (Phase 6)

- **10 documentation guides** created: Installation, Getting Started, Language Tour, Stdlib Reference, Compiler Architecture, Contributor Guide, Testing Guide, Release Process, Roadmap, Documentation Index
- **README rewritten** with badges, quick start, full stdlib table, project status
- **CURRENT_MILESTONE.md** updated to reflect Phase 6 completion

### Quality Gates

- 360 tests, all passing
- black, ruff, mypy all clean

## 0.1.1

### Documentation Consolidation (Phase 7)

- **Canonical specification**: Created `LANGUAGE_SPEC.md` at repository root — single source of truth (860 lines, 16 sections)
- **Fixed LANGUAGE_TOUR.md**: Corrected `else` keyword documentation, removed false "no reassignment" claim, removed wildcard import docs, removed `import "string"` path syntax, updated grammar section to reference canonical spec
- **Archived specifications**: Moved all 9 obsolete design specification files to `archived/specifications/` with ARCHIVED_README.md
- **Updated cross-references**: INDEX.md, CONTRIBUTING.md, PHASE_5B_REPORT.md, PHASE_6_REPORT.md, MASTER_ENGINEERING_PROMPT.md all now point to canonical spec
- **CLI improvements**: Fixed PHASE_6_REPORT.md to reference `ail` CLI instead of `python -m compiler`
- **All quality gates pass**: 374 tests (up from 360), black/ruff/mypy clean

### Validation & Ecosystem Audit (Phase 8)

- **Documentation validation**: 144 code examples tested across 4 documents; all compile and run correctly
- **Standard Library validation**: All 16 modules tested with edge cases and invalid inputs
- **Application validation**: 5/5 large applications compile and execute (Expense Tracker, Inventory, Contact Manager, Banking Ledger, Student Management)
- **Stress validation**: 28/28 tests pass (large LOC, deep nesting, multi-module, determinism)
- **Benchmark validation**: 25/25 tests pass (determinism, compile time, memory, IR hash)
- **AI validation**: 23/23 AI-generated programs compile on first pass (100%)
- **Defect fixes**: Fixed AssertionError crash in AST builder, CLI crash on malformed input, invalid list literal in STDLIB_REFERENCE.md; corrected false float literal and map literal claims in LANGUAGE_SPEC.md
- **408 tests** (up from 374)

### VS Code Extension (Phase 9)

- **Extension structure**: `extensions/vscode-ailang/` with `package.json`, TextMate grammar, snippets, language configuration
- **Syntax highlighting**: 15+ token categories (keywords, builtins, stdlib modules, strings, numbers, operators, comments, functions)
- **Language configuration**: Bracket matching, auto-closing pairs, auto-indentation, folding markers, comment toggling
- **9 snippets**: `main`, `fn`, `if`, `ifelse`, `import`, `return`, `recur`, `let`, `comment`
- **Validation**: 12 test `.ail` files covering all syntax features

### Official Formatter (Phase 10)

- **`ail fmt` command**: Format files in-place, `--check` for CI, `--stdin` for pipelines
- **Single canonical style**: 4-space indentation, same-line braces, spaces around operators, preserved comments
- **Deterministic and idempotent**: Formatting is stable across multiple runs
- **27 formatter tests** + 7 CLI tests
- **Operator precedence parenthesization**: Automatic for correct precedence rendering

### Dogfooding & Real-World Validation (Phase 11)

- **56 AILang applications**: 27 in `apps/`, 29 in `phase11/` — all compile and run
- **Stdlib addition**: `string.substring(value, start, end)` added
- **`env_args` fix**: Now returns user args only (strips CLI plumbing)
- **23 phase11 apps fixed**: Arg index bugs corrected for new `env_args` contract
- **6 new apps built**: find, payroll, library_mgmt, a_star, expr_eval, markdown_parser
- **Linter de-chaining**: Fixed chained member-access-on-call patterns in linter
- **Language freeze declared**: v0.1.x specification frozen — no new keywords, grammar, or syntax changes

### Governance & Philosophy (Phase 11/12)

- **`GOVERNANCE.md`**: Formal proposal process, evidence bars, review process, versioning, backward compatibility, rejected-forever list, freeze policy
- **`LANGUAGE_EVOLUTION.md`**: Permanent record of all 28 feature requests with dispositions
- **`PROJECT_CONSTITUTION.md`**: Immutable rules for development
- **`VISION_AND_DIFFERENTIATION.md`**: Evidence-driven vision, engineering hypothesis, differentiation strategy

### Public Release Preparation (Phase 12)

- **Repository audit**: Removed 9 obsolete/temporary artifacts
- **GitHub readiness**: LICENSE (MIT), SECURITY.md, CODE_OF_CONDUCT.md, SUPPORT.md, issue templates, PR template
- **`RELEASE_CHECKLIST.md`**: Formal release checklist for v0.1.1
- **Documentation audit**: All docs reviewed for broken links, stale examples, version consistency
- **Example validation**: All examples build, run, and produce documented output
- **Installation validation**: Verified from clean environment on Windows
- **VS Code extension**: Verified installation, highlighting, snippets
- **CI/CD**: All workflows verified

### RC1 Fixes

- **`system.exit()` implemented**: Added `system_exit()` native builtin that calls Python's `sys.exit(code)` to properly terminate the process
- **`string.substring` documented**: Added to STDLIB_REFERENCE.md and stdlib tables in README.md and LANGUAGE_SPEC.md
- **Documentation synchronized**: Updated LANGUAGE_TOUR.md to include string module examples and substring workaround
- **Error code constants**: Centralized PAR001, PAR002, PAR003, LEX001, LEX002, LEX003 constants in diagnostics.py
- **Test count corrected**: Updated README.md to show 507 passing tests

## 0.3.0

### Developer Experience

- **DX-004 — Benchmark Runner** completed and accepted (auto-discovery, suite modes, configurable repetition, baseline save/compare, regression detection, CI-friendly exit codes, fault-tolerant execution)
- **DX-005 — Test Generator** completed and accepted (auto-discovery, coverage analysis, three-stage pipeline, intermediate TestCase model, pure Python generators, `--force`/`--dry-run`/`--app` flags, `tests/generated/` separation, dual MD+JSON reports)
- **tools/common/ — extensions**: Added `hashing.py` (SHA-256 file hashing), `discover_apps()`, `list_py_files()`; `run_ail_build()`/`run_ail_run()` already present

### Quality Gates

- **772 tests**, all passing (up from 658)
- DX-004 (ail benchmark): PASS — 11 acceptance + 4 regression + 4 AI validation
- DX-005 (ail testgen): PASS — 9 acceptance + 4 regression + 4 AI validation

## 0.2.1

### Static Analyzer Performance Optimization

- **Replaced 4-pass scan** with single `scan_lines` pass, eliminating redundant function-end detection
- **Replaced character-by-character** `scan_line_calls_inner` with `collect_calls_inner` using `find_substring` builtin
- **Replaced `count_calls_file`** (character-by-character scan of all lines) with `build_calls_from_cache` (derives call statistics from per-function cache)
- **Result:** 3× speedup on hotel_management (252s → 84s), 3× on self-analysis (71s → 24s); self-analysis and large-file analysis now complete (previously never finished)

### Standard Library Additions (ADR-003)

- **`string.find(value, needle)`** — substring search, returns position index or -1
- **`string.find_from(value, needle, start_pos)`** — substring search with start offset
- **`string.split(value, delim)`** — split string into list by delimiter
- Evidence: 8+ independent reimplementations across the app ecosystem satisfied ADR-008 threshold

### Documentation

- **ADR-003** — Decision record for `string.find`/`string.split` stdlib additions
- **v0.2.1 Release Validation Report** — formal checkpoint with 658 tests, benchmark validation, DX acceptance, before/after performance
- **PROJECT_PHASE.md** — documents Platform & Developer Experience Engineering phase
- **PROJECT_CONTEXT.md** regenerated — reflects new stdlib APIs, updated version and test counts

### Quality Gates

- **658 tests**, all passing (up from 624)
- DX-001 (ail context): PASS — 8 acceptance tests, AI validation
- DX-002 (ail doctor): PASS — 9 acceptance tests
- DX-003 (ail static_analyzer): PASS — 8/8 acceptance tests (directory analysis timeout resolved with configurable `--timeout`)

## 0.2.0

### DX Tool #001 — ail context Developer Experience Tool

- **Standalone tool**: `tools/ail_context/` generates `generated/PROJECT_CONTEXT.md` for AI consumption
- **Single-file context**: All project knowledge consolidated into one LLM-optimized document (~6.5KB)
- **15 sections**: Project overview, philosophy, architecture, constraints, milestone, ADRs, stdlib, benchmarks, testing, frozen components
- **Acceptance tested**: 9 functional tests, 6 performance tests, 6 content validation tests, 3 AI validation tests
- **Zero changes**: No modifications to compiler, runtime, or language specification

### Runtime Optimization #001 — Lexical Variable Lookup Cache

- **`Environment.resolve()`** now caches binding locations per-environment in `_resolve_cache: dict[str, Environment]`, eliminating recursive chain walks on repeated variable lookups
- **~6× speedup** on the static analyzer benchmark (373s → 19.5s, the primary bottleneck workload identified by Python profiling)
- **52–64% cache hit rate** across all 5 benchmark apps (dice_roller, hangman_game, inventory_mgmt, kanban, static_analyzer)
- **Negative caching removed**: initial design cached `NameError` sentinels, but `assign` can create new bindings in ancestor environments, making negative entries stale. Only positive results are cached
- **`get_cache_info()` introspection** added to `Environment` and `Runtime` for testing
- **`_CacheStats` instrumentation** added to `Environment` (hits/misses/negative_hits counters) — no semantic effect, used exclusively for profiling
- **102 regression tests** in `tests/test_scope_cache.py` covering basic resolution, shadowing, recursion, reassignment, modules, edge cases, cache introspection, stress, and correctness invariants
- **624 tests total** (522 existing + 102 new), all passing
- **Memory overhead**: ~11 KB for the static analyzer workload (98 cache entries across 18 environments)
- **No semantic changes** — all existing AILang programs remain fully compatible
- **Runtime frozen** after this release. No further optimizations planned until community feedback identifies new bottlenecks

## 0.1.2

### Compiler QA — Bug Fix Sprint #001

- **BUG-001 fixed**: Empty `return;` no longer crashes with `AssertionError` — produces "Return statement requires an expression" diagnostic instead
- **BUG-002 fixed**: Missing initializer `let x = ;` no longer crashes with `AssertionError` — produces "Variable declaration requires an initializer expression" diagnostic instead
- **BUG-003 fixed**: Module name resolution for bare identifiers (`map.set` as a value, not just in call position)
  - `_resolve_name` now checks `self._modules` for bare module names before falling through to `NameError`
  - Module functions are now registered in module environments at initialization time
- **BUG-004 fixed**: Float literal `3.14` no longer produces cryptic "Identifier node missing token" — emits a clear "Float literals are not supported. Use integer division, e.g. 22 / 7" diagnostic at the lexer level (LEX004)
- **Regression tests added**: `test_ast_rejects_empty_return`, `test_ast_rejects_missing_initializer` in `test_ast_builder.py`; `test_regression_module_function_as_value` in `test_validation.py`; `test_lexer_rejects_float_literal` in `test_lexer.py`
- **BUG-005 fixed**: Block-level variable shadowing now works — `_execute_block` creates a new `StackFrame` for each block scope, so `let x` inside an `if`/`else` block properly scopes to that block instead of leaking to the enclosing function
- **BUG-006 fixed**: Deep recursion `count(1000)` no longer crashes — `Runtime.__init__` raises Python's recursion limit from 1000 to 10000 to accommodate AILang function call overhead

### Quality Gates

- **522 tests**, all passing (up from 521)
