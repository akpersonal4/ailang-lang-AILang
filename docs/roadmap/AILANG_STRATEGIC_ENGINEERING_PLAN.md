# AILang — Strategic Engineering Plan

**Status:** DRAFT — planning only. No implementation authorized.
**Version scope:** Current published release is **v1.1.18** (`ailang-lang==1.1.18`). There is **no v1.1.19** on PyPI or GitHub (confirmed by M137 investigation).
**Date:** 2026-08-13
**Type:** Master reference against which future engineering progress is measured.
**Governance:** Preserves the six-question feature governance model (AGENTS.md §8) and the A100 evidence-gated backlog (docs/roadmap/A100_FEATURE_BACKLOG.md). This document does not override them; it adds a measurement layer underneath them.

---

## 1. Executive Summary

AILang is a mature, shipping language (v1.1.18, 31 PyPI releases) whose engineering core is strong but whose **distribution pipeline is leaking**: the most important M136 fixes — the O(n²) interpreter fix (P1b) and the testgen `.ail` output fix (P1a) — exist **only in the uncommitted working tree** and were never shipped. Independent evaluations of the published wheel therefore observe performance and testgen behavior that the project's own reports claim to have fixed. That mismatch, not the underlying engineering, is the largest single credibility problem today.

Against the intended product ("simple, fast, deterministic, AI-first language for small-to-medium business software"), the evidence is mixed:

- **Strong:** determinism (IR SHA-256, 100% compile-time errors, zero silent runtime failures in measured benchmarks), AI onboarding (B7: structured context saves 3× iterations; evaluators rate onboarding/AI docs very strong), maintenance parity (B4/B5/B6 = 1.0× vs Python), stdlib completeness for the target workload, tooling breadth (26 CLI commands, MCP 6 tools, LSP, VS Code extension).
- **Weak / needs verification:** runtime scaling on larger datasets (confirmed O(n²) in the published wheel; linear after the unshipped fix), money/numeric ergonomics (documented int-only conversions; IEEE-754 float artifacts; no Decimal/round), test/testgen coherence (published testgen emits pytest `.py` files `ail test` ignores), recursion limits for larger datasets, and documentation inconsistency (test counts differ across documents).

**Conclusion on direction:** AILang *is* moving toward the intended product, but **not yet there on "fast" and "safe money/data handling," and its release discipline currently undermines "reliable."** The fastest honest progress is: (1) ship the already-written P0/P1a/P1b fixes, (2) measure the true baseline on the shipped artifact, (3) close the numeric/money and testing gaps with evidence, and (4) keep the language core frozen until real external users (A100) provide evidence for any change.

---

## 2. Product Definition

Precise operational meaning of each goal for AILang.

### 2.1 Simple
- **For AI:** an agent given only `AGENTS.md` + Playbook + `ail context` can generate correct code with minimal correction iterations. Measured by B7-style with/without-guide delta and A100 "AI correction iterations."
- **For humans:** a competent programmer reads any `.ail` file and understands data flow without tooling; no hidden evaluation order, no context-sensitive syntax.
- **Minimal:** the language surface (grammar + stdlib) grows only on measured pain (≥2 independent benchmark/app occurrences per ADR-008), never on parity pressure.
- **Anti-definition:** "simple" does not mean fewer keywords at any cost; it means the *total cognitive load of writing, reading, and maintaining* a business app is low.

### 2.2 Fast
- **Build/compile:** linear in source size with a small constant; must stay in the hundreds of milliseconds for the target app size (≤2,000 LOC, verified: 8,515-LOC inventory builds in 0.219 s).
- **Runtime:** "reasonably fast for the intended business-software workload" = CRUD, CSV/JSON data processing, workflows, reports, small APIs on datasets up to ~10⁴ records. Must scale **linearly** (no O(n²) or worse) on these patterns.
- **Measured, not assumed:** every claim carries a benchmark (ADR-007). No architectural change without an objective evidence gate (§13).

### 2.3 Reliable / Deterministic
- Same source + same inputs → same result (already verified: deterministic IR SHA-256).
- All structural errors surface at compile time (verified: 100% of AILang errors in B2–B7 were compile-time).
- **No silent data corruption:** financial calculations must be either exact or documented as approximate with an explicit API for exactness.
- Clear, structured errors with location + suggestion (verified present: RuntimeError diagnostics, error codes, `ail explain`).

### 2.4 Best Maintenance Experience
- AI can add a field, change a business rule, add a workflow, or modify permissions with **fewer correction iterations and fewer regressions than AI-assisted Python** on the same change.
- Existing behavior is protected: regression tests + deterministic build gate.
- **Not measured by LOC.** "AILang uses fewer lines" is neither the goal nor a sufficient signal.

### 2.5 AI-First Development
- AI discovers the language without external coaching: `ail context`, `ail docs`, `ail explain`, `ail heal`, MCP, LSP, diagnostics, `ail check/build/run` pipeline are first-class.
- Machine-readable feedback (JSON diagnostics) so tooling can act on errors.
- Reduce AI correction loops; generated code is easy to validate and maintain.

### 2.6 Appropriate Scope
- Target: business applications — CRUD, data processing, workflows, APIs/backend-style, reporting — at approximately 1–2k LOC per app, datasets to ~10⁴ records.
- Explicitly out of scope: becoming a general-purpose/Python-replacement language; performance-critical numeric/scientific computing; large-scale data engineering; UI frameworks.

---

## 3. Non-Goals

AILang will explicitly NOT:

1. **Python ecosystem replacement.** No PyPI-class package ecosystem, no comprehensive stdlib mirror, no full `pip` semantics beyond the existing minimal package manager.
2. **Feature-count competition.** No features added because Python or another language has them (governance Q6 lens applies to everything).
3. **General-purpose language.** No loops-by-default, generics, async/await, operator overloading, reflection, pattern matching, algebraic types — unless a *measured* business-app pain demands one (each would require ADR + CTO review per governance).
4. **GUI / native framework support.** No GUI toolkit, no native mobile/desktop bindings.
5. **Speculative performance engineering.** No Rust core, bytecode VM, JIT, or compiled backend without passing the evidence gates in §13.
6. **Unbounded stdlib growth.** No `string.replace`/`list.set`-style additions justified only by parity (per A100_FEATURE_BACKLOG §2, these are REJECT until the A100 task forces them).
7. **Optimization without measured evidence.** ADR-007 is binding; no optimization lands without profiler + before/after benchmark.
8. **A "feature backlog disguised as a strategy."** This document is a measurement and gating framework; the A100_FEATURE_BACKLOG remains the only approved feature queue.

---

## 4. Current Baseline

Separates **verified measurements** from **reported/assumed values**. All verified values were re-measured or directly inspected during M137 (2026-08-13) unless noted.

### 4.1 Version / Release State (verified)
| Item | Value | Status |
|---|---|---|
| Latest published release | **v1.1.18** (PyPI + GitHub) | Verified 2026-08-13 |
| v1.1.19 | **Does not exist** (PyPI max 1.1.18; GitHub max v1.1.18; zero docs references) | Verified |
| pyproject.toml version | 1.1.18 | Verified |
| Git HEAD | `7d4e315` "docs: mark v1.1.18 and M136 as published" (branch: main) | Verified |
| Engineering freeze | In effect (restored at v1.1.18; no v1.2 work until A100) | Verified |
| Working tree | 11 modified files + 44+ untracked generated `.ail` tests — contains unshipped M136 P0/P1a/P1b fixes | Verified |

**Critical discrepancy:** the uncommitted working tree contains `_frame_ever_bound` (O(n²)→O(n) fix, `compiler/runtime/interpreter.py`), entry-module single-execution fix (`compiler/cli/main.py`, `_initialize_module(run_body=False)`), and testgen `.ail` output (`tools/ail_testgen/*`). The published wheel contains none of these. M136's "wheel-verified" claims were against a locally-built wheel from the fixed tree, not the PyPI artifact.

### 4.2 Test Baseline
| Source | Count | Verified? |
|---|---|---|
| DEVELOPMENT_STATUS.md | 1217 passing | Reported |
| M136 RC report | 1145 passing / 6 pre-existing failures | Reported |
| EVALUATION_RERUN_V1_1_13.md | 1179 (1098 + 81 benchmark) | Reported |
| tests/ directory | 61 pytest files | Verified (exists) |

**Conflict flagged:** test counts differ across documents (1217 / 1145 / 1179 / 1128). A consistent, reproducible count command must be pinned (Phase 0).

### 4.3 Compiler Architecture (verified by inspection)
- Single-pass pipeline: lexer → parser → AST → semantic analysis → type checker → IR → tree-walking runtime codegen.
- Deterministic compilation: IR SHA-256 identical across runs (documented + claimed verified).
- ~4,000 LOC Python across ~40 files (`compiler/`).
- No forward references; bottom-up ordering required (ADR-004); `ail check` pre-flight catches forward refs/missing imports/ordering before compile.
- Compile time: 5,000 LOC ≈ 1.88 s; 10,000 LOC stress-tested; 8,515-LOC inventory full build = **0.219 s** (verified in repo records; scale linear).
- `--experimental-loops` lowers `for-in` to recursion at IR-build time (compile-time only; not default).

### 4.4 Interpreter Architecture (verified by inspection)
- Tree-walking interpreter; `compiler/runtime/` = 8 files; `interpreter.py` = 645 LOC.
- Lexical scoping; frame stack (`StackFrame`) + `Environment`; positive-only resolve cache (RTO-001, ~6× static-analyzer speedup; negative cache deliberately removed per ADR-006).
- Fresh `Environment` per function call; module/global lookups walk the chain.
- Recursion guard: `max_recursion = 2000` default (policy in `sandbox.py`); clean structured error on depth overflow (verified in v1.1.13+).
- **Published-wheel performance (M137, re-verified):** recursive driver 100→17.8 ms, 200→75.8, 400→376.3, 800→1687.5 (ratios ≈4.0–5.0 → **quadratic**); full Expense Tracker 100→122.7, 800→9997.5 ms; `Environment.resolve` = 74–80% of runtime.
- **With unshipped fix (working tree):** driver 100→3.67, 800→32.79 ms (ratios ≈2.0 → **linear**); Expense Tracker 100→29.6, 800→260.1 ms; **~23× at n=400** (matches M136's "~22×").

### 4.5 Standard Library (verified)
- 16 `.ail` modules: array, convert, csv, environment, file, io, json, list, map, math, path, random, set, string, system, time.
- Extended beyond base with list.sort/sum/sum_by_key/filter/group/collect/take/skip/copy/search, map.values/get_or_default/safe_get, string.join/from_int/from_bool, io.read, file.listdir, convert.to_number.
- Missing (noted, intentionally gated): `string.replace`, `list.set`, JSON pretty/lines, `math.round`, money/formatting APIs.

### 4.6 CLI / Tooling (verified)
26 commands: run, build, check, fmt, new, test, install, add, remove, update, list, publish, lsp, order, rename, watch, version, help, doctor, heal, explain, docs, context, mcp, static-analyzer, benchmark, testgen.
- JSON diagnostics (`file`, `line`, `column`, `code`, `message`, `severity`, `suggestion`) — verified present.
- `ail testgen` (published): emits **pytest `.py`** into `tests/generated/`; `ail test` ignores them ("No tests found", exit 1) — verified. Working-tree fix emits `.ail` that `ail test` executes (1/1 passed).
- `ail test` (published): auto-executes `test_*.ail` files (J-2) — verified with a manual test file.

### 4.7 MCP / LSP (verified by inspection)
- MCP server (`tools/ail_mcp`): 6 tools — get_language_context, get_stdlib, compile_source, explain_diagnostic, get_examples, get_document; JSON-RPC 2.0 over stdio.
- LSP: diagnostics, go-to-definition, rename, hover, code actions, format-on-save, completions; VS Code extension v1.1.0 with 12 commands / 10 settings.

### 4.8 Current Benchmark Results (measured evidence)
| Benchmark | Result | Source |
|---|---|---|
| B2–B7 (vs Python) | AILang **1.38×** more iterations overall; **100% compile-time errors** (zero silent runtime failures); refactor/upgrade/maintenance **parity 1.0×**; B7 structured context saves **3× iterations** | ENGINEERING_EVIDENCE_REPORT |
| Inventory vs Python | AILang 8,515 LOC vs 6,258; **33% more LOC/function** (9.85 vs 7.40); full build 0.219 s; test run 0.173 s vs 0.194 s | INVENTORY_PYTHON_COMPARISON |
| Sudoku (B02) | Performance timeout 30–60 s — algorithmic workloads not viable (out of scope anyway) | PROJECT_MEMORY |
| M137 scaling | Published wheel **quadratic** on recursive patterns; working tree **linear**; CSV parsing linear | M137 report |
| B1/B1.1 | Framework + 4-provider integration, 44 + 37 tests | PROJECT_MEMORY |

### 4.9 Known Limitations (verified)
- Recursion-only iteration (ADR-001/002); practical file ceiling ~100 functions / ~1,000 LOC (Playbook lesson 10).
- Eager `&&`/`||` (ADR-003) — documented trap, nested-`if` idiom.
- No forward references (ADR-004) — 38% of historical AILang correction cycles.
- `string.concat` 2-arg limit; `let` needs initializer; `return` needs value; unique variable names per function.
- `convert.to_number` ≡ `to_int` (integer-only; decimal strings raise at runtime) — documented but surprising.
- `convert.to_int(12.99)` → 12 (silent truncation) — undocumented behavior (docs gap).
- IEEE-754 float arithmetic (e.g., `0.1 + 0.2` = `0.30000000000000004`); no Decimal type, no `round`, no fixed-point money formatting.
- Recursion depth cap 2000 (clean error, but a hard ceiling for very large data).
- `json.parse` returns `false` on malformed input (documented BUG-008).

### 4.10 Known Bugs (confirmed in published artifact)
1. **O(n²) name resolution** in recursive programs (published wheel) — fix exists uncommitted.
2. **`ail testgen` emits `.py` tests the AILang runner ignores** — fix exists uncommitted.
3. **Docs inconsistency:** test counts / version labels differ across documents.
4. `ail doctor` residual findings confined to `docs/archive/` (intentional history, not current drift).

### 4.11 Freeze State
Engineering freeze in effect since v1.1.18. A100 recruitment ready. This plan does **not** lift the freeze; it defines the measurement work (Phase 0) that precedes any unfreeze decision.

---

## 5. Goal Metrics

Each metric has: definition, why it matters, target, and baseline. Where no baseline exists, the target is "measurement required" and Phase 0 establishes it.

### A. Build/compile speed
- **Definition:** wall time `ail build` for a 1,000-LOC single-file app and for the 8,515-LOC inventory suite.
- **Why:** AI correction loops are gated by compile latency; the intended app size must build in well under a second.
- **Target:** 1,000 LOC < 300 ms; 8,515 LOC < 1 s.
- **Baseline:** 0.219 s @8,515 LOC (recorded). **Re-verify on the published wheel.**

### B. Runtime performance
- **Definition:** execution time for canonical business workloads (expense tracker, inventory CRUD, CSV processing) at n = 100 / 1,000 / 10,000 records; scaling ratios must be ≈2× per doubling (linear).
- **Why:** the product promise is linear scaling on business data.
- **Target:** linear scaling ratios (1.8–2.2× per doubling) on published artifact; absolute time for 10,000-record workload < 5 s.
- **Baseline:** published wheel ratios ≈4× (quadratic); fixed tree ≈2×. **Target applies to the shipped artifact, not the working tree.**

### C. Memory usage
- **Definition:** peak RSS for the 10,000-record expense workload and the inventory suite.
- **Why:** small-to-medium business software must run on modest hardware.
- **Target:** < 300 MB peak for the 10,000-record workload.
- **Baseline:** **measurement required** (no recorded memory numbers; add to Phase 0 harness).

### D. AI correction iterations
- **Definition:** number of compile-fix-rerun cycles to reach a working build for a standard task (reuse B2 task spec).
- **Why:** the core differentiator; must be measured against AI-assisted Python under identical conditions (B2–B7 methodology).
- **Target:** ≤ 1.0× Python for greenfield; < 1.0× for maintenance changes (the plan's primary claim to defend).
- **Baseline:** B2–B6 = 1.38× Python; B4/B5/B6 maintenance = 1.0× parity. **Need A100 external confirmation.**

### E. First working program time
- **Definition:** minutes from `pip install ailang-lang` to a working non-trivial program (≥20 LOC, file I/O + data processing), zero tracebacks.
- **Why:** A100 precondition target; first impression.
- **Target:** < 10 minutes (A100 stated target).
- **Baseline:** **measurement required** (M135 fixed the known first-impression crashes; not yet re-timed end-to-end by a stranger).

### F. Maintenance/change success rate
- **Definition:** % of A100 maintenance change requests (M1–M6: add field, tax rule change, new CSV column, permissions, approval workflow) completed with all existing tests green and zero regressions introduced.
- **Why:** maintenance is the primary mission.
- **Target:** 100% of A100 maintenance tasks complete with 0 regressions on the published artifact.
- **Baseline:** internal B4/B5/B6 parity only; **A100 external measurement required.**

### G. Regression rate
- **Definition:** % of changes that break previously passing tests.
- **Why:** maintenance protection is a core promise.
- **Target:** 0% regression on all shipped changes (release gate already enforces this); measured as "regressions found by tests during A100 maintenance phase."
- **Baseline:** release-gate claim (1145/1145 green at M136 gate modulo 6 pre-existing); **re-verify count consistency in Phase 0.**

### H. Test execution
- **Definition:** `ail test` wall time for the canonical suite; ratio of tests that are generated-and-executable vs generated-but-ignored.
- **Why:** test/testgen incoherence was an evaluator finding; the workflow must be one coherent path.
- **Target:** 100% of `ail testgen` output executes under `ail test`; full canonical `ail test` < 30 s.
- **Baseline:** published: 0% (generated `.py` ignored); fixed tree: 100%. **Target = fix + ship P1a.**

### I. Error quality
- **Definition:** % of AI correction iterations resolved by a single compile error message (no "second error discovered only after fixing the first"); structured `file:line:col` + suggestion + code on all errors.
- **Why:** single-error-at-a-time reporting was the #1 recorded iteration driver (B2/B3/B7).
- **Target:** ≥ 70% of compile runs resolve in one iteration with the first message; every error has code + suggestion + location.
- **Baseline:** multi-error collection exists but cross-phase batching incomplete (A100_FEATURE_BACKLOG §1); **measure in A100.**

### J. Application LOC / complexity
- **Definition:** LOC per function and per module for a standardized app (Inventory: AILang 9.85 vs Python 7.40 LOC/fn — 33% tax).
- **Why:** verbosity is a frustration signal but **not** a success metric (§2.4). Tracked to quantify the cost of recursion + naming rules; used only as an input to governance (e.g., whether a pattern library is warranted).
- **Target:** track, do not optimize for. Only act if A100 frustration data implicates verbosity.
- **Baseline:** 9.85 LOC/fn (verified in Inventory comparison).

### K. Determinism
- **Definition:** same source + same inputs → byte-identical output and identical IR SHA-256 across N runs.
- **Why:** the product's central reliability claim.
- **Target:** 100% of canonical apps produce byte-identical output across 10 runs; IR SHA-256 identical across rebuilds.
- **Baseline:** claimed verified; **add an automated determinism gate to Phase 0 harness.**

---

## 6. Performance Strategy

### 6.1 Where is the current runtime spending time? (verified, M137)
- `Environment.resolve` (chain walk) = **74%** of runtime on the recursive driver (208,607 calls @n=200) and **80%** on the full Expense Tracker @n=400 (4,784,466 calls).
- Every non-frame-bound name (module functions like `convert.to_string`, `list.contains`, the recursive function name itself) walks the full parent chain raising `NameError`, then resolves from global/module env. Per-row cost is O(depth); total is O(n²).
- CSV parsing is linear and cheap (~1–1.5 ms @1,000 rows). `list.contains` itself is ~0.000 s in the profiled workload — the evaluator's "`list.contains` is the O(n²) source" attribution is **incorrect**; recursion-driven name resolution is.

### 6.2 Is the interpreter fundamentally sufficient?
**Yes, for the target workload — with the existing fix shipped.** The unshipped `_frame_ever_bound` optimization already restores linear scaling (verified: ratios ≈2.0, 23× @n=400) with ~50 LOC and zero semantic change. No architecture change is justified by current evidence.

### 6.3 Which operations are unexpectedly expensive?
- **Module/global name resolution inside recursion** — the only measured hotspot. Everything else (CSV, list ops, func calls, map ops) scales linearly once resolution is fixed.
- **Absolute overhead:** a single `runtime.execute` of the n=100 driver is ~18 ms published vs ~3.7 ms fixed — the fixed interpreter is competitive for business workloads.

### 6.4 Is O(n²) behavior still present?
- **In the published wheel: yes** (all recursive programs; verified component benchmarks A–F all ratio ≈4).
- **In the working tree: no** (verified linear). The fix is written, tested in RC_VERIFICATION_REPORT.md, and merely unshipped.

### 6.5 What must change to achieve acceptable performance?
1. **Ship the existing fix** (commit + release P1b). Expected: O(n²)→O(n) on all recursive business patterns.
2. **Measure** the real baseline on the published artifact (Phase 0), including the 10,000-record workload, memory, and absolute times.
3. **Re-profile** after shipping; any further work must follow ADR-007 (observe → profile → measure → fix → benchmark).
4. Candidate incremental optimizations *after* profiling (not now): negative-cache for module names if still hot; string/regex fast paths in stdlib; reduce per-call Python overhead in `_call_function`. Each gated on profiler evidence.

### 6.6 When would a bytecode VM / compiled backend / Rust core become justified?
Defined in §13 (Gates B, C, D). The objective triggers are measured ceiling violations — e.g., if a 10,000-record CRUD workload cannot meet target with the shipped interpreter, or if per-call overhead exceeds budget for the target app size. **Rust "because faster" is explicitly not a trigger.** Incremental optimization (Gate A) must be exhausted first because it has near-zero risk and the fix is already written.

---

## 7. Simplicity Strategy

Inventory of current complexity, each evaluated for determinism/AI-reliability/maintainability impact. **Do not remove strictness on request.** Any relaxation requires evidence that the rule costs more AI iterations than it saves.

| Item | Type | Evidence | Proposed action |
|---|---|---|---|
| No forward references (ADR-004) | Rule | #1 historical compile failure (100% of benchmarks); `ail check` auto-fixes | **Keep.** Deterministic, catches errors early. `ail order` already mitigates. |
| Recursion-only iteration (ADR-001/002) | Rule | 33% LOC tax (verified); Sudoku perf timeout (out of scope); no measured business-app failure | **Keep for v1.x.** `for-in` experimental; default-enable only via A100 evidence gate (A100_FEATURE_BACKLOG §4). |
| Eager `&&`/`||` (ADR-003) | Rule | 40% of benchmarks trapped; nested-`if` idiom documented | **Keep, but** ensure `ail check` flags the risky pattern (right operand references left-op-dependent state) as a hint. |
| `string.concat` 2-arg limit | Rule | 30% of benchmarks trapped | **Keep.** Forces explicit intermediates; `+` covers 3+ strings. |
| Unique variable names per function | Rule | Shared-global-scope legacy; name collisions were a benchmark trap | **Revisit for v2 research:** block-scoped shadowing inside a function is the largest remaining "unnecessary rule" candidate; document the risk/benefit. |
| Bottom-up file ceiling (~100 fn / ~1,000 LOC) | Limitation | Playbook lesson 10 | **Keep + document**; multi-file modules are the sanctioned path. |
| Semicolon optionality + formatter reinsertion | Design | DX-008 decision | **Keep.** Formatter normalizes; zero-config. |
| `let` initializer / `return` value requirements | Rule | Missing-initializer crashes were a real bug class | **Keep.** Reduces null states. |
| Mandatory `map.has`/`list.len` guards | Guidance | Guard audits; avoids runtime errors | **Keep** as docs; consider `ail check` hint. |

**Principle:** each simplification must state its effect on (a) determinism, (b) AI reliability, (c) maintainability, (d) readability, and be routed through governance (§14). Candidate simplifications that survive evidence: **batch/multi-error reporting** (tooling, not language), **better `ail check` hints**, and — with strong A100 evidence — **loops default** and **intra-function shadowing**.

---

## 8. Maintenance Strategy (PRIMARY)

### 8.1 Representative maintenance workloads (A100 MAINTENANCE_TASKS.md M1–M6)
1. Add a field (e.g., discount per transaction)
2. Change a business rule (tax rate → per-category)
3. Add validation (required fields, ranges)
4. Change tax logic (GST applied to all → per-category rates)
5. Modify permissions (role-based admin/user)
6. Add a workflow (approval flow)
Plus maintenance-schema changes: add/modify CSV column; change reporting requirements.

### 8.2 Measurement definition (vs Python + AI)
Each change is measured on **both** AILang and AI-assisted Python implementations of the same app:
- **Time to implement** the change (human+AI wall clock)
- **AI correction iterations** (compile/run/review cycles)
- **Regressions** (tests that fail after the change)
- **Bugs introduced** (found by tests or review)
- **Confidence rating** (participant-reported)

**Success is NOT fewer LOC.** Success = "AI can safely change the application with fewer errors, fewer correction loops, and less regression risk than Python + AI."

### 8.3 Baseline evidence
- Internal B4/B5/B6: **parity (1.0×)** for refactor/upgrade/maintenance; deterministic build gate catches all structural errors at compile time.
- Inventory: identical data-bleed bug found in both languages; AILang fixes surface all 9 import/name errors in a single compile vs Python's 3 test-run iterations.
- A100 external measurement is the definitive test; Phase 2 of A100 is the primary deliverable of this strategy.

### 8.4 Strategy components
1. **Protect existing behavior:** generated tests must execute under `ail test` (ship P1a); deterministic build gate on every change.
2. **Make regressions obvious:** `ail test` + `ail benchmark` in CI; regression-count metric (G) tracked per milestone.
3. **Reduce correction loops:** batch diagnostics (metric I); `ail check` hints for guard/pattern violations.
4. **Measure against Python:** fixed A100 protocol (greenfield + maintenance, head-to-head). No self-reported wins.

---

## 9. AI-Native Strategy

Evaluation of each tool against the mission (Q: genuinely differentiated? / needs improvement?):

| Tool | Status | Differentiated? | Improvement needed |
|---|---|---|---|
| `ail context` | Works; AI onboarding strongly rated | **Yes** — single-file structured context; B7 3× savings | Keep current; ensure parity with working-tree fixes (module/version drift risk) |
| `ail docs` | Renders docs; `??` bug fixed (v1.1.13) | Partial | None measured |
| `ail explain` | Error-code explanations; ASCII-safe (v1.1.16) | **Yes** | Batch/compound explanations when multiple errors present |
| `ail heal` | Exists in CLI | Partial | Verify depth/behavior on wheel; document |
| MCP (6 tools) | JSON-RPC stdio; stdlib/context/compile/explain/examples/docs | **Yes** | Version-sync with runtime; add diagnostics-by-code query |
| LSP | diagnostics, go-to-def, rename, hover, code actions, format | **Yes** | Track testgen `.ail` output for quick actions |
| Diagnostics | structured JSON `file/line/col/code/message/severity/suggestion` | **Yes** | Cross-phase batching (metric I) |
| `ail check` | pre-flight ordering/import gate | **Yes** | Add guard-pattern hints (map.has/list.len, eager-&&) |
| `ail build/run` | deterministic, sandboxed | **Yes** | Ensure entry-module single-execution fix ships (P0) |
| `ail testgen` | Published: emits ignored `.py` | **No (currently broken)** | **Ship P1a** (`.ail` output) — highest-priority AI-native fix |
| `ail static-analyzer` | self-analysis, 931-line static_analyzer app | Partial | Verify on wheel after P0 fix |
| `ail benchmark` | regression detection, 20% threshold | Partial | Add memory + scaling modes (Phase 0) |

**Priority:** make the pipeline coherent end-to-end (testgen → test → check → build → run) before adding new AI tools.

---

## 10. Standard Library Strategy

Classify each API family; do not expand blindly.

| Class | Members | Action |
|---|---|---|
| **Essential** | list (new/append/len/get/contains/remove/sum/find_by_key/sort/copy/take/skip/filter/group/collect), map (new/set/get/has/delete/keys/values/get_or_default/safe_get), string (concat/equals/case/length/contains/trim/substring/find/split/join), file (read/write/append/exists/remove/listdir), json (parse/stringify), csv (parse/parse_header/stringify), convert (to_string/to_int/to_bool/to_number), io, math (add/sub/mul/div/abs/min/max), environment, system, time, path, random, set, array | **Maintain, freeze API signatures.** |
| **Useful (gated on evidence)** | JSON pretty/lines, `math.round`, money/format helpers, `string.replace`, `list.set` | Post-A100 candidates; each requires ≥2 independent unprompted reaches (A100_FEATURE_BACKLOG §2). |
| **Dangerous/confusing** | `convert.to_number` ≡ `to_int` (name implies float), `convert.to_int` silent float truncation, `json.parse` returning `false` on malformed input | **Docs fixes** (document truncation + parse-returns-false); consider a `convert.to_float`/`convert.to_decimal` decision under governance — do not add speculatively. |
| **Performance-critical** | list.contains/find/sort on large lists; string.split/find; csv.parse on large files | Benchmark in Phase 0; optimize only with ADR-007 evidence. |
| **Unnecessary** | None identified | Add only via the two-benchmark evidence bar. |

**Minimum stdlib for the target workload:** current 16 modules already cover it; the only true gap is **safe money handling** (§11).

---

## 11. Type / Data / Money Safety

Goal: business applications cannot silently produce incorrect financial results.

### 11.1 Verified current behavior (M137, published wheel)
| Concern | Behavior | Verdict |
|---|---|---|
| Integers | Full support; `+ - *` exact; `/` always float | OK |
| Floats | IEEE-754 double; exists (`3.14`, division results) | OK for measurement, **not for money** |
| Decimal/money representation | **None.** No Decimal type, no fixed-point | **Gap** |
| `convert.to_number` | ≡ `to_int`; integer-only; `"12.50"` raises RuntimeError | Documented, but name is misleading |
| `convert.to_int(12.99)` | → `12` silently | **Docs gap** (behavior undocumented) |
| `0.1 + 0.2` | → `0.30000000000000004` | IEEE-754 artifact; **money hazard** |
| CSV numeric values | All strings; must be converted explicitly | OK if documented |
| JSON values | Numbers parsed as int/float; strings for others | OK |
| Aggregation | `list.sum`/`sum_by_key` coerce preserving float (J-4 shipped) | OK for float; no money semantics |
| Comparisons / arithmetic | Python semantics on int/float | OK within types |

### 11.2 Money handling decision (governance-routed, NOT implemented here)
Options:
1. **Documented "money = integer minor units" convention** (e.g., cents as `int`) with a `convert.to_cents`/`from_cents` helper — minimal, deterministic, exact for ±2⁵³, no float anywhere. **Recommended for v1.x** (smallest surface, zero ambiguity, mission-aligned, AI-learnable).
2. **`convert.to_decimal` returning an exact decimal type** — larger surface; requires runtime type + arithmetic support; defer to v2 research with evidence.
3. **Float + round discipline** — rejected as the status quo silently corrupts money.

**Minimum acceptance (definition of "safe money"):** any money arithmetic path (CSV→sum→report) produces exactly representable results, or explicitly rejects non-integer-minor-unit inputs with a clear error. No silent `0.1+0.2`-style corruption. Phase 1 must deliver: `convert.to_cents`/`from_cents` (or equivalent) + docs + a money-trace test app.

---

## 12. Testing Strategy

One coherent workflow. Desired relationships:

```
write code
   → ail fmt           (normalize)
   → ail check         (structural gate: ordering, imports, patterns)
   → ail build         (deterministic compile)
   → ail testgen       (generate .ail tests that EXECUTE)
   → ail test          (run all test_*.ail; fail on regression)
   → ail benchmark     (perf/regression on canonical apps)
   → ail run           (execute app)
```

### 12.1 Required fixes
1. **testgen must emit `.ail`** (P1a, written) and the generated tests must execute under `ail test` (verified working in the fixed tree). **Non-negotiable** — it is the evaluator-flagged incoherence.
2. **Published wheel must run generated tests end-to-end** (module resolution `import main` must work under `ail test` — flagged in M137 as needing the matching unpublished interpreter).

### 12.2 Rules
- Generated tests: no manual edits (regenerable); they must assert behavior (PASS/FAIL), not just compile.
- Test discovery: single pattern (`test_*.ail` / `*_test.ail`); remove ambiguity with pytest `.py` artifacts (delete the `.py` generator path when P1a ships).
- CI: `ail test` + `ail benchmark` + determinism gate on every PR; regression count is a release gate.
- Static analyzer: advisory (structure), not a test substitute.

### 12.3 Metrics
- H: 100% of generated tests execute; canonical `ail test` < 30 s.
- G: 0 regressions per change.

---

## 13. Architecture Decision Gates

Objective evidence thresholds. Each gate is "pass" only when evidence is produced; no gate is passed on speculation. **Recommendation: pursue Gate A only, now.**

### Gate A — Optimize current interpreter (IN PROGRESS, ~50 LOC)
- **Evidence required:** profiler shows name resolution (or another specific hotspot) dominates; fix benchmarked ≥2× on the targeted workload; zero semantic change; all tests green.
- **Status:** evidence exists (M137: `Environment.resolve` 80%; fix → linear, 23× @n=400; RC_VERIFICATION_REPORT.md verified). **Action: ship it.**
- **Cost:** ~50 LOC + release cycle. **Risk:** low (fix already RC-verified).
- **Next A-gates (incremental, each needs its own profile):** negative module-name cache; `_call_function` overhead; stdlib string/list fast paths; per-run determinism gate.
- **Would NOT justify A:** a small constant-factor improvement on an already-linear workload.

### Gate B — Introduce bytecode VM
- **Trigger:** after shipping A, a 10,000-record canonical business workload cannot meet target (§5B) with the interpreter, AND profiling shows per-node dispatch / per-call overhead is the ceiling, AND Gate A incremental options are exhausted.
- **Evidence required:** profiler showing dispatch/call overhead > 50% of remaining runtime; a spike prototype demonstrating ≥2× on that workload with byte-identical semantics; determinism preserved.
- **Expected benefit:** 2–5× constant factor. **Cost:** substantial (new IR/executor, test migration, regression surface). **Risk:** medium (semantic drift, ADR-005 cache integration).
- **Would NOT justify:** "bytecode is faster" as an argument; Sudoku-class algorithmic workloads (out of scope).

### Gate C — Native / compiled backend
- **Trigger:** business apps need order-of-magnitude runtime beyond B, or target apps exceed the intended size class; and a business-app workload (not toy) shows the need.
- **Evidence required:** measured business-app workload where interpreter + VM cannot meet target; compiled spike with semantic parity on canonical suite; determinism preserved.
- **Expected benefit:** 10–50×. **Cost:** very high (new backend, stdlib native bindings). **Risk:** high (the project's identity is AI-first simplicity; a compiled backend adds enormous surface).
- **Would NOT justify:** wanting Python-like ecosystem performance; startup-time comparisons alone.

### Gate D — Rust implementation / core
- **Trigger:** same as C, AND evidence that Python (the host) is itself the ceiling (e.g., GC pauses, GIL, startup) on measured business workloads; Rust re-implementation offers semantic parity with acceptable effort.
- **Evidence required:** profile attributing ≥50% of remaining runtime to CPython host overhead on a canonical workload; Rust spike with full stdlib parity on canonical tests.
- **Expected benefit:** startup + memory + worst-case throughput. **Cost:** near-total reimplementation of compiler+runtime+stdlib+tooling; years of maintenance. **Risk:** catastrophic to the AI-first/simplicity mission if done for the wrong reasons.
- **Would NOT justify:** "Rust is faster"; community hype; memory safety as a language-level differentiator (AILang already eliminates the relevant bug classes structurally).

### Gate E — Self-hosting
- **Trigger:** AILang has a proven maintenance advantage on itself (A100 evidence) AND the toolchain is stable; self-hosting is a strategic bet on the language, not a performance play.
- **Evidence required:** a substantial internal module (e.g., formatter or static analyzer) reimplemented in AILang meeting parity + the maintenance metrics (§8.2) beating the Python baseline.
- **Expected benefit:** dogfooding + credibility. **Cost:** high (compiler in AILang must compile AILang). **Risk:** high unless phased (start with a non-critical component).
- **Would NOT justify:** "every real language is self-hosted."

**General rule:** any rewrite must first fail Gates A's incremental options with measured data, and must present a determinism-preservation plan. This is deliberately conservative because the mission is simplicity + AI reliability, not raw speed.

---

## 14. Feature Governance

Preserve the existing six-question model (AGENTS.md §8) exactly. This plan adds one rule: **every feature proposal must attach the metric (A–K, §5) it improves and the baseline it moves.** Proposals without a metric or baseline are returned unprocessed.

The six questions (unchanged):
1. Does it serve the mission?
2. Does it improve AI reliability?
3. Does it improve maintainability?
4. Does it preserve determinism?
5. Does it add unacceptable complexity?
6. Would it still be justified without AI hype?

**Routing:**
- Language features → strict Q1–Q6 + ADR + CTO/Architecture review.
- Tooling features → Q1–Q3, maintainer approval.
- Runtime/compiler internals → ADR required.
- Anything that touches money safety or determinism → CTO review regardless of track.

**Input source:** user requests and evaluator feedback *identify problems*; governance *determines solutions*. A100 findings feed the A100_FEATURE_BACKLOG (the only approved feature queue). No unverified evaluator claim becomes a code change (§15 Phase 0 does the verification).

---

## 15. Roadmap

No version numbers assigned. Items classified P0–P3. **Nothing below lifts the freeze.**

### PHASE 0 — Measurement / Baseline (P0)
Goal: pin an honest, reproducible baseline on the **published artifact**.

**Onboarding Verification Protocol (fresh-AI test).** Any "can a new AI developer
work with AILang?" test must follow this flow, which exercises both the **repository
governance** (GitHub) and the **published product** (PyPI) as separate concerns:

```text
Blank folder
    ↓
git clone GitHub repository   (read-only — used ONLY for docs/governance)
    ↓
read AGENTS.md + Strategic Plan + DEVELOPMENT_STATUS + PROJECT_MEMORY
    ↓
identify current release / phase / freeze / evidence gates
    ↓
pip install ailang-lang from PyPI   (published artifact, NOT the source tree)
    ↓
run all tests from a neutral CWD with the source checkout EXCLUDED from the
    Python import path (PYTHONPATH empty; imports must resolve from site-packages)
    ↓
evaluate the published artifact independently and report findings
```

Rules:
- **GitHub source must not be on the import path.** Otherwise the AI (or the
  investigator) silently tests the local checkout and never measures the quality of
  the published PyPI version. This is exactly what happened in M137 (fixed-tree
  A/B comparison via `PYTHONPATH` vs a clean wheel-only venv).
- PyPI alone is not sufficient context: a blank folder has no `AGENTS.md`, no
  Strategic Plan, no roadmap, no history. GitHub provides governance and history;
  PyPI provides the real end-user package. Both are required for a true fresh-AI test.

- [ ] P0 — Commit + release the unshipped M136 P0/P1a/P1b fixes (single-execution entry module, O(n²) fix, testgen `.ail`). (Releases the blocker so the baseline is measured on a correct artifact.)
- [ ] P0 — Pin test-count command and reconcile doc counts (1217/1145/1179/1128 conflict).
- [ ] P0 — Determinism gate: canonical apps ×10 runs, byte-identical output + IR SHA-256.
- [ ] P0 — Performance harness: expense/inventory workloads at n=100/1k/10k (time + memory + scaling ratios) on the shipped artifact.
- [ ] P0 — Money-trace test app: CSV → sum → report with cents, on the shipped artifact.
- [ ] P0 — Record §5 baselines A–K; publish a BASELINE.md.

### PHASE 1 — Critical correctness (P0/P1)
- [ ] P0 — Ship P0/P1a/P1b (carried from Phase 0; a release, not a feature).
- [ ] P0 — Money safety: `convert.to_cents`/`from_cents` (or equivalent) + docs + money-trace test; document `convert.to_int` truncation.
- [ ] P1 — Fix test/testgen coherence on the shipped wheel (generated tests execute under `ail test`).
- [ ] P1 — `ail check` hints for guard patterns (map.has/list.len, eager-`&&` right-op dependency).

### PHASE 2 — Performance (P1)
- [ ] P1 — After baseline, apply incremental Gates A optimizations driven by profiler; re-benchmark each.
- [ ] P1 — Ensure 10,000-record canonical workload meets §5B linear target on shipped artifact.
- [ ] P2 — Memory measurement added to `ail benchmark` (RSS per workload).

### PHASE 3 — Maintenance / DX (P1/P2)
- [ ] P1 — Batch/cross-phase diagnostics (metric I) if A100 baseline confirms the gap.
- [ ] P2 — Playbook/AGENTS updates from any A100 lessons.
- [ ] P2 — Intra-function shadowing research (document, no change without governance).

### PHASE 4 — AI-native tooling (P1/P2)
- [ ] P1 — Pipeline coherence verified end-to-end on the shipped wheel (fmt→check→build→testgen→test→benchmark→run).
- [ ] P2 — MCP/LSP parity with working-tree fixes; diagnostics-by-code query.
- [ ] P2 — `ail heal` verification + documentation.
- [ ] P3 — Safety-guarantee visibility in `ail check`/`ail doctor` (presentation-only subset, per A100_FEATURE_BACKLOG §5).

### PHASE 5 — Architectural decision (P2)
- [ ] P2 — Re-evaluate Gates B–E only if Phase 2 data shows the interpreter cannot meet §5B targets. Otherwise record "Gate A sufficient."

### PHASE 6 — Community validation (P1)
- [ ] P1 — Execute A100 protocol on the shipped artifact (requires Phases 0–1 fixes shipped first, so strangers evaluate a correct artifact).
- [ ] P1 — Publish A100 report with verdict against fixed criteria.
- [ ] P1 — Route all findings through governance (§14).

---

## 16. Definition of Done

Before AILang can honestly claim each property, all conditions must hold **on the published artifact** (not the working tree):

| Claim | DoD |
|---|---|
| **Simple** | New developer/AI achieves first working program < 10 min with zero tracebacks (metric E); AI correction iterations ≤ 1.0× Python greenfield (metric D). |
| **Fast** | 1,000-LOC build < 300 ms; canonical business workload scales linearly (ratios ≈2 per doubling) to 10,000 records; 10k-record workload < 5 s (metrics A, B). |
| **Reliable** | Determinism gate 100% (metric K); 0 release-blocking bugs; all A100 maintenance tasks complete with 0 regressions (metrics F, G); 100% compile-time error capture with structured diagnostics (metric I). |
| **Maintainable** | A100 maintenance changes: fewer correction loops + fewer regressions than Python + AI (metrics D, F, G) — measured externally. |
| **AI-first** | testgen→test→check→build→run is one coherent executable pipeline (metric H = 100%); MCP/LSP/context/docs/explain/heal all function on the published wheel (verified, not assumed). |
| **Money-safe** | No silent financial corruption: money paths use integer minor units (or equivalent exact mechanism) with documented conversions (Phase 1 deliverable). |

Measurable only where a metric exists (A–K); all other claims are explicitly not made.

---

## 17. Kill Criteria / Pivot Criteria

The plan must allow the experiment to fail honestly. These are pre-committed conditions.

| Condition | Trigger | Consequence |
|---|---|---|
| **Interpreter architecture insufficient** | After shipping Gate A fixes, the 10,000-record canonical workload still cannot meet §5B target, profiler attributes ≥50% to host overhead, AND Gate A incremental options are exhausted | Move to Gate B (bytecode) with a spike; if spike fails parity/determinism, pivot runtime strategy. |
| **Language constraints hurt adoption more than help** | A100: ≥2/3 of maintenance-phase completers cite loops or scoping rules as the reason for "would choose = No", or frustration-driven abandonment ≥2 participants | Route ADR for language relaxations with governance; if A100 verdict is negative overall, stop feature work and run an explicit redesign review. |
| **Maintenance advantage not measurable** | A100 maintenance phase shows AILang correction loops or regression rate ≥ Python's, across ≥3 participants (not noise) | Redefine the hypothesis honestly; if the advantage is unmeasurable, pivot mission to "deterministic + safety-first for niche regulated workloads" rather than claiming general maintenance superiority. |
| **Performance target unrealistic** | Published-artifact scaling cannot reach linear at 10k records after all Gate A options | Document the ceiling; restrict the product claim to ≤2,000-record apps; consider Gate B only if business data sizes require more. |
| **Project should pivot architecture or mission** | Any combination of the above triggering ≥2 conditions, OR A100 fixed criteria unmet with 0 release-blocking bugs but negative preference | Pause new work; produce a documented Pivot Proposal with evidence, options, and a decision record — never silently drift. |

---

## 18. Current Recommendation

1. **Do first:** Ship the already-written, already-verified M136 P0/P1a/P1b fixes (single-execution entry module, `_frame_ever_bound` O(n²) fix, testgen `.ail`) as the next release. This is a **release of finished work**, not a new feature, and it is the single highest-leverage action: it converts the current published artifact from "quadratic + broken testgen" to "linear + coherent tests."
2. **Do NOT do yet:** any language feature, any stdlib expansion, any architectural rewrite, any version bump beyond the fix release, any change to the A100 protocol, and any performance work without Phase 0 baseline + ADR-007 profile. Specifically no Rust, no loops-by-default, no Decimal type — none have passed an evidence gate.
3. **Engineering freeze:** **remain frozen for language/architecture.** The freeze's purpose (no v1.2 until A100 evidence) is unchanged. The only unfreeze is the administrative act of **releasing already-approved fixes** — which the freeze was never intended to block, and which the evaluator feedback directly requires. Recommend the freeze continue formally until A100 completes.
4. **Evidence required before implementation begins:**
   - Phase 0 baseline on the shipped artifact (metrics A, B, C, H, K).
   - Reconciliation of the test-count conflict (one command, one number).
   - A100 recruitment + first greenfield/maintenance data (metrics D, F, G, I).
   - Money-trace test result on the shipped artifact (§11.2).
5. **Stop condition for this plan:** review this document after Phase 0 and after A100; update baselines, and only then open the language-feature track.

---

*End of plan. This document is the master reference for future engineering progress. No implementation occurs until this document is reviewed and explicitly approved.*
