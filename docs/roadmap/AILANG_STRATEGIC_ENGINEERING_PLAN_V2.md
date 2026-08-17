# AILang Strategic Engineering Plan — V2 (Post-v1.1.19)

> **Status:** Planning / Governance — NO code, NO test, NO spec, NO version, NO release
> actions are authorized by this document. This document only plans.
>
> **Supersedes:** `AILANG_STRATEGIC_ENGINEERING_PLAN.md` (V1) **where V1 is stale.**
> V1 (2026-08-13) asserts "there is no v1.1.19" and treats P0/P1a/P1b as unshipped.
> v1.1.19 **is published** (commit `837e05c`, tag `v1.1.19`, PyPI `ailang-lang==1.1.19`),
> the P0/P1a/P1b fixes are confirmed shipped and independently verified.
> V1 remains the **master reference / measurement layer** (goal metrics §2, §5B 10k target,
> Gates A–E §13, money decision §11, governance §14, kill criteria §17). V2 is the
> **foundation-hardening execution plan** rebased on v1.1.19 evidence.

---

## PROJECT STATE

```text
PROJECT STATE
Release:        v1.1.19 (published 2026-08-13; commit 837e05c; PyPI ailang-lang==1.1.19)
Phase:          A100 — Active, "recruitment ready" (NOT authorized to start under V2)
Freeze:         Language surface, stdlib API, CLI commands, new tooling, new AI
                integrations, testgen expansion, A100 backlog items (all frozen
                through P1 exit gate)
Strategic Objective: Foundation hardening: make the v1.1.19 artifact meet the
                SIMPLE/FAST/RELIABLE/AI-MAINTAINABLE/EASY-TO-EXTEND contract before
                recruiting real users.
Current Evidence:
  - RELIABLE = FAIL   (exit codes discarded; tests string-scan "FAIL"; float money)
  - FAST     = PARTIAL(linear post-P1b; 1000-rec full-app 2.71s; 10k NOT MEASURED)
  - SIMPLE   = PARTIAL(float arithmetic, 2000-recursion ceiling, spec contradictions)
  - AI-MAINTAINABLE = PASS (toolchain strong; test/testgen are the weak link)
  - EASY-TO-EXTEND  = PASS (coverage 0.88; clean architecture; recursion ceiling
                    blocks large-data extension)
  - Architecture verdict (audit): CONTINUE — no Gate B/C trigger fired.
Requested Work: Author a V2 strategic engineering plan (planning/governance only).
Authorized:     YES — V2 planning document only. NO code/commit/release.
```

---

## 1. Core Question: Is the Audit's Sequence the Best Engineering Strategy?

The v1.1.19 audit recommends `FOUNDATION FREEZE → P0 → P1 → P2 → P3 → A100`.
V2 evaluates each judgment honestly, not reflexively.

### 1.1 Ordering verdict

| Audit decision | V2 evaluation | Ruling |
|---|---|---|
| Exit codes = P0 | Correct. Tiny CLI-contract fix, breaks automation/AI trust, blocks all downstream validation. | ✅ Keep P0 |
| Test verdicts = P0 | Correct. Must come **before** the money fix so tests can verify the money API. | ✅ Keep P0, ordered after exit codes |
| Money safety = P0 | Correct. AILang's reason to exist is business/money apps; silent float corruption violates the mission. Independent of iteration — runs in parallel with P1 research. | ✅ Keep P0 |
| Iteration ADR (Gate F) = P1 | Correct position. Iteration is **both** a language-surface decision (ADR-001/002) and an architecture execution decision (host-stack recursion). | ✅ Keep P1, scope split below |
| Doc contradictions = P1 | Correct. Cheap, reduces AI-agent confusion, gating A100 onboarding. | ✅ Keep P1 |
| 10k measurement = P2 | **Partial.** The 2000-recursion ceiling makes a full 10k *recursive* workload un-runnable today, so full measurement genuinely must follow the iteration decision. BUT a **bounded pre-measurement** (native-stdlib paths, name resolution, compile scaling — all runnable at 10k today) is a Phase-0 deliverable that *informs* Gate F. | ⚠ Split: bounded pre-measure → Phase 0; full canonical-10k → Phase 2 |
| Coverage = P2 | Correct. Not release-blocking; tooling gap, not contract gap. | ✅ Keep P2 |
| Re-evaluate Gates B–E = P3 | Correct. Only after real 10k numbers exist. | ✅ Keep P3 |
| A100 last | Correct. A100 must not start merely because a version is published. | ✅ Keep last |

### 1.2 Iteration: language-design, architecture, or both?

**Both, and the two halves must be de-coupled.**

- **Language surface** (ADR-001 "recursion only", ADR-002 "no loop constructs", ADR-00X
  conditional `for-in`): a product decision about the code AI agents write.
- **Execution model** (tree-walking interpreter calling Python functions through the
  Python host stack): the *reason* the 2000 ceiling exists.
  `sandbox.py:30` sets `max_recursion = 2000`; `interpreter.py:51-53` wires that to
  `_max_call_depth` and `sys.setrecursionlimit(_max_call_depth * 10 + 1000)` — each AILang
  frame consumes ~10 Python frames, so the ceiling is a **host-stack safety limit**, not
  a language rule.

**V2 conclusion:** the 2000 ceiling can be removed **without touching the language at
all** by executing recursion/iteration with an explicit interpreter stack (trampoline)
instead of the Python host stack (Gate F option E below). This preserves ADR-001/002's
language surface exactly while satisfying the 10k depth requirement.

### 1.3 Should 10k be measured before changing the iteration model?

- What **can** be measured today: native-stdlib-dominated workloads at 10k
  (list ops, string, json, csv parse), name resolution, compile time scaling, memory.
- What **cannot**: a 10k *pure-AILang recursive* workload (hits the ceiling at ~2000).
- Ruling: measure the measurable in Phase 0; the trampoline (option E) is
  architecture-internal and low-risk, so it does not need a 10k pre-measurement —
  but its **success** is gated on the Phase-2 canonical measurement.

### 1.4 Can the tree-walking interpreter still meet the strategic target?

Evidence: fixed-tree tests show linear scaling (expense tracker 100→29.6ms,
800→260.1ms). The evaluator's full business app at 1000 records: compile 0.30s +
execute ~2.41s; extrapolated linear at 10k ≈ 24s — **fails §5B's `< 5 s`**.
Python reference was 0.10–0.16s flat (**26–40× gap**).

**Ruling:** the interpreter is capable of *linear* scaling and of any *depth*, but
**linear alone does not guarantee the absolute `< 5 s` @ 10k target** — that depends on
the workload mix (pure-AILang recursion vs native-stdlib) and the per-call constant.
The V2 benchmark protocol (§7) must therefore define a **canonical business workload**
and measure it, and the `< 5 s` target is workload-defined, not assumed.

### 1.5 What objectively triggers a VM (bytecode) transition?

A VM only cuts the **per-node dispatch constant**. It does **not** help algorithmic
scaling, I/O, or stdlib overhead. Gate C fires only when:

1. Canonical 10k workload exceeds the defined runtime target, AND
2. A profiler attributes **≥50% of remaining runtime** to interpreter
   dispatch / function-call overhead (not stdlib, not I/O), AND
3. Gate A/B incremental options (resolve fast paths, call fast paths, iterative
   IR lowering, trampoline tuning) are measured and exhausted.

### 1.6 Risk of endless interpreter patching — how V2 prevents it

Every optimization path gets a **pre-committed decision gate**: date + metric + stop
condition. If a gate's metric is not met by its date, the plan does not "try harder";
it **escalates to the next gate or returns to the decision table**. Concretely:

| Gate | Stop condition if not met |
|---|---|
| Phase 1 trampoline | 10k-depth workload runs with correct output → else revert or fix; escalate |
| Phase 2 canonical 10k | meets workload target → else begin dispatch profiling |
| Phase 2 profiling | ≥50% dispatch overhead + Gate A exhausted → **Gate C (VM spike, time-boxed)** |
| Gate C spike | VM prototype proves ≥2× on canonical workload → else revert, document as permanent limit, re-scope target |

There is no "endless patching" path: each phase either meets its gate or triggers a
**bounded** escalation.

### 1.7 What must be frozen so AI-driven feature creep cannot derail hardening

Hard-freeze (through P1 exit gate): language syntax/semantics, stdlib API signatures,
new CLI commands, new MCP tools, new LSP features, testgen expansion, new AI
integrations, all five A100 backlog proposals (batch diagnostics, stdlib additions,
verbosity/patterns, for-in default, safety-gate visibility). A feature request is NOT
authorization — see §11.

### 1.8 Minimum work for genuine reliability

P0-1 exit codes → P0-2 assert + test verdicts → P0-3 money (integer cents) →
Phase-1 spec/CLI/doc contradiction fixes → deterministic-output + deterministic-build
gates → PyPI-wheel + clean-workspace reproducibility check → **then** the reliability
contract (§8) is signed. Nothing less.

---

## 2. Strategic Objective (unchanged, restated against v1.1.19)

> **AILang exists to make AI agents produce deterministic, low-maintenance, business
> software. Everything else is measured against that.**

| Goal | v1.1.19 status | Failure mode today |
|---|---|---|
| SIMPLE | PARTIAL | `to_number` truncates (12.99→12); float money (24173.85999999999); 2000-recursion ceiling; spec self-contradiction on exit codes |
| FAST | PARTIAL | Linear post-P1b; 10k not measured; recursion ceiling blocks large workloads |
| RELIABLE | **FAIL** | `main`/test return values discarded; tests string-scan `"FAIL"`; money unsafe |
| AI-MAINTAINABLE | PASS | Toolchain strong; test/testgen weakness is the gap |
| EASY-TO-EXTEND | PASS | Coverage 0.88; clean layering; recursion ceiling blocks data-scale extension |

---

## 3. Gate F — Iteration Model Decision (the P1 architecture decision)

### 3.1 Decision frame

Gate F answers: *"What iteration model does AILang use, and how is it executed, so that
the 10k target is achievable without violating determinism, simplicity, or the AI-first
identity?"* Tiebreak rule: **the simplest architecture that satisfies the product
requirements wins** — no sophistication bias.

### 3.2 Options

| Option | Description | Type |
|---|---|---|
| **A** | Keep recursion-only permanently (ADR-001/002) | Language + architecture (status quo) |
| **B** | Native `while`/`for` loops executed directly by the interpreter | Language surface + architecture |
| **C** | Keep the language surface; compile `for-in` to an **efficient IR loop node** (no per-record function call) | Architecture only |
| **D** | Bytecode/VM execution | Architecture only |
| **E** | Keep recursion-only surface; execute calls via an **explicit interpreter stack / trampoline** (removes host-stack ceiling) | Architecture only |

### 3.3 Evaluation (14 axes)

| Axis | A keep recursion | B native loops | C IR loop node | D bytecode VM | **E trampoline** |
|---|---|---|---|---|---|
| Simplicity | High | Low (new surface, break/continue, mutation) | High (surface unchanged) | Medium | High |
| Runtime perf | Ceiling @2000 → FAIL | Good | Good | Best constant | Same constant, no stack thrash |
| Memory | Per-frame on host stack | Good | Good | Medium | Heap frames |
| Recursion depth | **2000 — blocks 10k** | Loops OK; recursion still capped | Loops OK; recursion still capped | Resolved (VM stack) | **Resolved (memory-bound)** |
| Determinism | Preserved | Risk (loop mutation) | Preserved | Risk (semantic drift) | Preserved (same order) |
| AI maintainability | High | Medium (more surface to teach) | High | Medium (two layers) | High |
| Debugging | Good | Medium | Good | Harder | Good (same semantics) |
| Implementation complexity | None | High (grammar/AST/IR/checker/fmt/LSP) | Medium (IR + loop node) | **High** | Low–medium (interpreter-internal) |
| Language complexity | Unchanged | **Increased** | Unchanged | Unchanged | Unchanged |
| Backward compat | Perfect | Good (additive) | Perfect | Requires byte-identical verification | Perfect |
| Testability | High | Medium | High | Medium | High |
| Extensibility | **FAIL at scale** | Good | Good | Good | Good |
| 10k target | FAIL (depth) | Likely met | Likely met | Likely met | Likely met (depth); constant needs measurement |
| Beyond 10k | FAIL | Good | Good | Good | Good |

### 3.4 Recommendation

**Decide: Option E — recursion-only surface, trampolined execution.**

Rationale (evidence-driven):
- The measured failure at 2000 is a **host-stack limit** (`sandbox.py:30`,
  `interpreter.py:51-53`), not a language limit. E removes it with zero surface change.
- E is the **simplest architecture satisfying the product requirements**: no grammar,
  no new semantics, no IR churn, perfect backward compatibility, preserved determinism.
- E keeps ADR-001/002 ("recursion only", "no loop constructs") intact as a *language*
  decision, while the *execution* detail (host stack vs explicit stack) becomes an
  implementation concern where it belongs.
- B is rejected now: it adds the largest complexity for a benefit E already delivers,
  and contradicts the "no loops by default" governance until A100 shows evidence.
- C and D are **not rejected** — they are demoted to gated escalations (§1.5, §1.6):
  C if profiling shows per-record dispatch dominates a canonical 10k workload;
  D only on the Gate C evidence package.

### 3.5 Gate F exit criteria (what P1 must deliver)

1. ADR recording the E decision with this comparison table. **No code.**
2. A trampoline design doc: explicit call stack, `_call_depth` semantics preserved,
   error stack traces preserved (same messages, same ordering), memory-bound depth.
3. Pre-committed Phase-2 trigger table (§1.6) fixed with dates + metrics.
4. `for-in` remains experimental per ADR-00X; the A100 backlog item "for-in default"
   stays frozen.

---

## 4. Architecture Gates (post-Gate-F escalation ladder)

Each gate: metric · measurement method · workload · pass/fail · reason · consequence.
Thresholds are **proposed defaults to be fixed by the Gate F ADR**, not arbitrary.

| Gate | Metric | Method | Workload | Pass/Fail | Reason | Consequence if failed |
|---|---|---|---|---|---|---|
| **Gate A** (incremental interpreter optimization acceptable) | Runtime + depth on canonical workload | Benchmark protocol §7 | Canonical business workload, n=100…10,000 | Pass: runs at all n, correct output, deterministic; fail: depth/ceiling errors | Iteration is the binding constraint; incremental ops first | Fail → Gate B trigger (if depth remains) |
| **Gate B** (deeper interpreter/IR optimization required) | Dispatch overhead share | `cProfile` on canonical 10k | Canonical workload @10k | Pass: ≤50% dispatch; fail: >50% | Dispatch dominance justifies C | Fail → Gate C spike (time-boxed) |
| **Gate C** (bytecode VM justified) | VM spike speedup | Time-boxed spike prototype | Canonical workload @10k | Pass: ≥2× vs current; fail: <2× | VM must pay for itself | Fail → revert, document as permanent limit, re-scope §5B target with evidence |
| **Gate D** (larger redesign) | Mission-contract violation | Any | — | Fires only if product targets change (beyond-10k, concurrency) or multiple contracts irreparably broken | Redesign is a product decision, not an engineering reflex | Triggers a new ADR + Strategic Plan V3 |

**Determinism guard for C/D:** any transition must prove byte-identical output on the
existing app corpus before acceptance; semantic drift is a blocker.

---

## 5. P0 Foundation Contracts

Format per contract: **current behavior** (evidence) · **required behavior** ·
**why it matters** · **regression test** · **acceptance gate** · **what must NOT change**.

### 5.1 Contract P0-1: Process exit codes

| Field | Detail |
|---|---|
| Current | `interpreter.py:79-86` `execute()` **returns** `_call_function(main)`'s value; `main.py:430` `cmd_run` calls `runtime.execute(...)` and **discards the result, returning 0 unconditionally**. `system.exit(code)` exists (`stdlib/system.ail:1`) as an escape hatch. LANGUAGE_SPEC §5.3 (L273): "The return value of `main` is discarded by the CLI." LANGUAGE_SPEC §16 (L900–903): "0 = Success, Non-zero = Error." **The spec contradicts itself.** |
| Required | Non-zero `main` return → non-zero process exit code. `system.exit` keeps precedence. Success (including "0") → exit 0. Compile/runtime errors keep their existing non-zero codes. |
| Why | Automation and AI agents must be able to detect failure. This is the single most damaging contract bug for the AI-first mission. |
| Regression test | CLI harness: `exit_code = run(["ail","run","app.ail"])`; app returns 1 → `exit_code == 1`; returns 0 → `0`; `system.exit(3)` → 3. |
| Acceptance gate | Spec §5.3/§16 contradiction resolved (both sections say the same thing); ALL apps + tests still pass; determinism test (output byte-identical across 3 runs). |
| Must NOT change | `system.exit` semantics; welcome-to-stderr behavior; `ail run`'s own error codes; the interpreter's return-value propagation. |

### 5.2 Contract P0-2: Test assertions and test verdicts

| Field | Detail |
|---|---|
| Current | `main.py:1862-1889` `cmd_test` calls `runtime.call_function(test_name)`, then **string-scans output for `"FAIL"`** (L1874). A test that returns 1 with no output → PASS. There is **no `assert` primitive** (LANGUAGE_SPEC has none). testgen generates compile-only tests. |
| Required | (a) A test's non-zero return → test FAIL. (b) An `assert`-style primitive (e.g., `test.expect(cond, msg)` in stdlib) that surfaces a structured failure. (c) `cmd_test` verdict based on return value + primitive, not string scanning (keep string scan as supplementary display only). |
| Why | `tests can't silently pass` is the reliability floor. Without it, RELIABLE stays FAIL and the whole app corpus is untrustworthy. |
| Regression test | A test that returns 1 with no output → FAIL. A test with a false assertion → FAIL with the message. Existing passing corpus still passes. |
| Acceptance gate | Verdict correctness (no false PASS) on the full test corpus; `test_count` reporting matches actual (fixes the testgen misreport). |
| Must NOT change | Existing test function names/discovery; `ail test` CLI surface; that failing tests produce non-zero overall exit. |

### 5.3 Contract P0-3: Money-safe arithmetic

| Field | Detail |
|---|---|
| Current | Numbers are IEEE floats. `convert.to_int(12.99)` → 12 (truncation, `convert.ail`); `to_number` aliases `to_int`; no `to_float`. Money aggregation yields artifacts like `24173.85999999999`. |
| Required | Integer minor-unit representation exposed via stdlib (e.g., `money.to_cents("12.50") → 1250`, `money.from_cents(1250) → "12.50"`). Documented rule: **money arithmetic happens in integer cents**; float remains for scientific/display use. Rounding behavior defined for ÷. |
| Why | The product is business software. Silent money corruption is a mission-level violation of RELIABLE. |
| Regression test | Add/sub/mul/div/rounding/serialization/comparison on cent values; CSV and JSON persistence round-trips exactly; a money-heavy generated app's output is exact and deterministic. |
| Acceptance gate | All money dimensions in §5.4 pass; spec/stdlib reference updated; no float money artifact in any app output. |
| Must NOT change | Integer semantics; float division semantics; existing `convert.*` names (additive API only); performance of non-money paths. |

### 5.4 Money evaluation dimensions (P0-3 acceptance scope)

decimal correctness · addition · subtraction · multiplication · division · rounding ·
serialization · comparison · CSV persistence · JSON persistence · AI-generated business
applications (expense tracker, ledger, invoice totals).

---

## 6. Documentation / Spec Contradictions (P1)

Prioritized; fixes are doc/spec/CLI-surface only.

### P0-class (block correctness understanding)
- **C-1:** LANGUAGE_SPEC §5.3 (main return discarded) vs §16 (exit codes) — *drives P0-1.*

### P1-class (block AI-maintainability / onboarding)
- **C-2:** `DEVELOPMENT_STATUS.md` stale (says v1.1.18 current, no v1.1.19 row; engineering "frozen").
- **C-3:** `PROJECT_MEMORY.md` stale (v1.1.18; 1217 tests vs 1236 actual).
- **C-4:** `ail fmt`/`ail heal` docs claim reordering; formatter never reorders functions.
- **C-5:** `--experimental-loops` hidden from `ail run --help` (exists, undocumented).
- **C-6:** `ail doctor` scans nested venvs → alarmist health 0/100 scare.
- **C-7:** testgen `test_count` mismatch; generated tests compile-only.
- **C-8:** ADR-016 header "DRAFT / pending approval" though P1b shipped in v1.1.19.

### P2-class (cosmetic/historical)
- **C-9:** `docs/adr/` contains only ADR-010/011/012/016; ADR-001/002 live in
  `docs/architecture/ARCHITECTURE_DECISIONS.md` — cross-reference map needed.
- **C-10:** README/CHANGELOG release cross-links; duplicate error lines in stacktraces.

---

## 7. Performance Validation Protocol (P2)

Reproducible, workload-defined, evidence-only.

- **Sample sizes:** n = 100, 200, 400, 800, 1,000, 2,000, 5,000, 10,000.
- **Workloads:** (a) **canonical business workload** — expense tracker with N
  transactions across load/total/max/category/currency/pending/monthly passes in pure
  AILang recursion; (b) **native-stdlib workload** — N records via list/csv/json ops.
  Both reported separately; the §5B `< 5 s` target is defined against (a).
- **Measurements:** runtime (compile vs execute split), scaling ratio per doubling,
  peak memory, recursion/iteration depth, output correctness, output determinism
  (3 runs byte-identical), process exit code.
- **Python reference:** same workload in Python for the 26–40× baseline (informational,
  not the gate).
- **Overhead decomposition** (must be attributed): algorithmic scaling · interpreter
  dispatch · function-call overhead · name resolution · stdlib overhead · I/O overhead.
- **"FAST enough" definition:** product-defined (canonical workload @10k within target),
  NOT "match Python".
- **Honesty rule:** if a sample cannot run safely under the current model, that is
  recorded as evidence, not glossed over.
- Deliverables: `docs/benchmarks/PERF_SCALING_10K.md` (numbers, environment, Python
  version, wheel vs source) + decision-table update (§1.6).

---

## 8. Reliability Contract (gates P0–P1 must satisfy)

1. **Non-zero exit on failure** — P0-1.
2. **Tests cannot silently pass** — P0-2.
3. **Deterministic output** — 3-run byte-identical on the app corpus.
4. **Deterministic builds** — same source + same toolchain → same artifact/hash
   (extends the publication-matrix hashing to source builds).
5. **Structured diagnostics** — compiler/runtime errors have stable, machine-readable
   shape (existing behavior, now contract-tested).
6. **Sandbox correctness** — sandbox violations still raise `PermissionError` with the
   same message (regression test).
7. **File/CSV/JSON I/O correctness** — round-trip exactness contract-tested.
8. **Money correctness** — P0-3 + §5.4.
9. **CLI correctness** — `run/test/build/check/fmt/context/docs/heal/doctor/explain`
   exit codes and output shape tested.
10. **Regression-test behavior** — full corpus green = the gating condition for any
    change; no "passes but wrong" (P0-2).
11. **PyPI-wheel reproducibility** — fresh venv, `pip install ailang-lang==1.1.19`,
    corpus green (independent verification pattern).
12. **Clean-vs-source import isolation** — `ail` resolves to the intended install
    (wheel OR source tree, never ambiguous).

---

## 9. AI-Maintainability Model

Preserve everything that makes AILang AI-friendly, add a per-change verification loop.

- **Preserved:** `ail context` + `--json`, `ail docs`, `ail heal`, `ail explain`, MCP,
  LSP, deterministic toolchain, clear diagnostics, spec-first documentation.
- **Per-change workflow (mandatory for every accepted change):**
  modify → `ail fmt` → `ail check` → `ail test` → `ail build` → benchmark (if
  performance-relevant) → verify deterministic output (3 runs) → verify no regression →
  update docs/spec → record lesson in Playbook if universal.
- **AI trust gates:** exit codes (P0-1), assert verdicts (P0-2), doc contradictions
  (§6). Until P0 lands, AI agents cannot trust run/test results.

---

## 10. Easy-to-Extend Model

Every future feature (language / stdlib / CLI / tooling / AI-MCP) must complete a
10-field template. A "feature request" does NOT become "feature authorized" until the
template is accepted.

**Template:** Problem · User/AI value · Specification · Architecture impact ·
Test strategy · Performance impact · Determinism impact · Maintenance impact ·
Rollback strategy · Evidence supporting this feature.

Governance: language features require ADR (Q1–Q6); tooling features require maintainer
approval (Q1–Q3) — unchanged from V1 §14.

---

## 11. NOT NOW / OUT OF SCOPE (with justification)

| Item | Justification for exclusion |
|---|---|
| Native `while`/`for` in the language | Gate F option B rejected: largest complexity, E already delivers depth; contradicts "no loops by default" governance until A100 evidence |
| Bytecode/VM | Gate C only; a VM does not fix algorithmic/I/O/scaling; must pay for itself (≥2× spike) |
| A100 recruitment start | A100 success criteria require a hardened artifact; RELIABLE=FAIL blocks it |
| All 5 A100 backlog proposals | Frozen feature set; must not ship before foundation hardening |
| New stdlib modules | Except the P0 money API — no other module has mission evidence |
| Cosmetic CLI/LSP/AI features | No measured pain point; violates mission focus |
| testgen assertion generation | Deferred to P1–P2; P0-2 (assert primitive) lands first |
| Language redesign | No evidence; Gate D is a product decision requiring V3 plan |
| `for-in` promotion to default | Remains experimental per ADR-00X; A100-evidence-gated |

---

## 12. Version / Release Policy

- **No version bump for activity.** A release is justified only by a measurable
  user-facing improvement.
- A candidate release must pass: complete release gate (PUBLICATION_MATRIX-style:
  hashes, fresh-install 12/12, corpus green) **plus** independent verification from the
  PyPI wheel.
- Suggested next release: a P0 hardening release (exit codes + assert verdicts + money)
  on the v1.1.x line, only after all P0 acceptance gates and the §8 contract pass.
- v1.2.0+ is reserved for A100-evidence-driven features (e.g., for-in default, if
  approved).

---

## 13. A100 Readiness Criteria

**A100 must NOT start merely because a version is published.** Recruitment opens only
when the following are **all** true (each item is a measured gate, not an intention).
Every item maps to work defined in §14 (Roadmap) / §5 / §8 / §7 below.

| # | Readiness criterion | Gate | Source requirement |
|---|---|---|---|
| 1 | **Reliability** | §8 contract items 1–4 (exit codes, no false PASS, deterministic output, deterministic builds) all green | RELIABLE no longer FAIL |
| 2 | **Test quality** | Verdict correctness proven (no false PASS on corpus); assert primitive ships with acceptance tests | P0-2 |
| 3 | **Money safety** | All §5.4 dimensions pass on integer-cents API; no float artifact in any app output | P0-3 |
| 4 | **Performance** | Canonical 10k workload measured and within the defined target; scaling documented | Phase 2 + §7 |
| 5 | **Determinism** | 3-run byte-identical output + build on the app corpus | §8.3–8.4 |
| 6 | **Onboarding** | Fresh developer (no prior AILang exposure) completes a greenfield app from spec in one session with zero unresolved questions | A100 four-question progression |
| 7 | **Documentation** | §6 P0- and P1-class contradictions resolved; LANGUAGE_SPEC consistent; `--experimental-loops` documented or removed from surface | Phase 0/1 |
| 8 | **Clean PyPI install** | Fresh venv `pip install ailang-lang` → corpus green with zero source-tree leakage | §8.11 |
| 9 | **Reproducibility** | Same source + same toolchain → same artifact hash; wheel vs source parity | §8.4 + publication matrix |
| 10 | **Maintenance workflow** | §9 AI workflow validated end-to-end by a second AI agent on a real change (modify→check→test→build→verify) with no ambiguity | Phase 3 |

**Decision rule:** any criterion unmet at recruitment time → A100 stays closed and the
gap is routed back into Phases 0–3. A100 readiness is a checkpoint, not a milestone
naming exercise.

---

## 14. Roadmap — PHASE 0–5

Each phase: objective · allowed · forbidden · deliverables · tests · benchmarks ·
acceptance · exit gate · evidence · rollback.

### PHASE 0 — FOUNDATION HARDENING (next)
- Objective: ship P0 contracts (§5) on a frozen surface; establish baselines.
- Allowed: P0-1 exit codes, P0-2 assert/verdicts, P0-3 money stdlib; spec/doc fixes
  for §5.3/§16 (C-1); release-gate verification on v1.1.19.
- Forbidden: iteration model work, new language features, new CLI/tooling, A100,
  version bump.
- Deliverables: P0 contracts implemented + acceptance-gated; §8 items 1–3 green;
  `docs/benchmarks/PERF_SCALING_PRE_ITERATION.md` (bounded pre-measurement, §1.3).
- Tests: new CLI/assert/money regression tests + full corpus green.
- Benchmarks: native-stdlib scaling 100→10k; compile scaling.
- Acceptance / exit gate: all P0 acceptance gates pass; corpus green; deterministic
  output/build verified; doc contradictions P0-class resolved.
- Evidence: acceptance-gate results, corpus run, pre-iteration benchmark doc.
- Rollback: contracts are additive; revert to v1.1.19 tag if a gate is blocked.

### PHASE 1 — ITERATION / ARCHITECTURE DECISION (Gate F)
- Objective: Gate F ADR (Option E recommended) + trampoline design; doc contradiction
  fixes (P1-class).
- Allowed: ADR + design doc (no code); doc/spec fixes C-2…C-8; parallelism with P0 money
  verification.
- Forbidden: implementing the trampoline in this phase; `for-in` promotion; new surface.
- Deliverables: Gate F ADR; trampoline design; contradiction fixes.
- Tests: doc/spec integrity checks (spec §5.3/§16 consistent).
- Benchmarks: none required.
- Acceptance / exit gate: ADR accepted; trigger table (§1.6) committed with dates.
- Evidence: ADR, design doc.
- Rollback: doc-only phase; trivial.

### PHASE 2 — PERFORMANCE + SCALE VALIDATION
- Objective: implement option E trampoline; run canonical 10k measurement; dispatch
  profiling.
- Allowed: interpreter-internal trampoline; benchmark harness; §8 items 4–6.
- Forbidden: language surface changes; VM; new CLI.
- Deliverables: trampoline; `docs/benchmarks/PERF_SCALING_10K.md`; profiling report.
- Tests: full corpus byte-identical (determinism guard); depth workloads to 10k.
- Benchmarks: §7 full protocol.
- Acceptance / exit gate: depth resolved; canonical-10k measured; §1.6 table executed.
- Evidence: benchmark + profiling numbers.
- Rollback: revert trampoline → decision table decides next action (escalate or scope).

### PHASE 3 — TOOLING / DOC HARDENING
- Objective: coverage improvement; testgen asserts behavior; P2-class doc fixes;
  README/CHANGELOG/ADR cross-links.
- Allowed: tooling + docs only.
- Forbidden: language surface; A100.
- Deliverables: coverage report (target: maintain ≥0.88); testgen assertion generation.
- Tests: corpus green; coverage gate.
- Benchmarks: none.
- Acceptance / exit gate: coverage maintained; C-9/C-10 fixed.
- Evidence: coverage + doc reports.

### PHASE 4 — ARCHITECTURE GATE REVIEW
- Objective: apply §1.6 / §4 decision table to the Phase-2 numbers.
- Allowed: ADR for escalation or re-scoping §5B target (evidence-based).
- Forbidden: escalation without the Gate B/C evidence package.
- Deliverables: decision record; updated §5B target (if re-scoped) with evidence.
- Acceptance / exit gate: explicit CONTINUE / OPTIMIZE / VM REQUIRED / REDESIGN ruling.
- Evidence: Phase-2 numbers + decision record.

### PHASE 5 — A100 (only if Phase 4 = CONTINUE/OPTIMIZE with hardened artifact)
- Objective: recruit developers against the hardened artifact.
- Allowed: per A100_COMMUNITY_VALIDATION.md, only after all gates above.
- Forbidden: starting A100 before Phase 4 acceptance.
- Deliverables: participant tracker, four-question progression results.
- Exit gate: A100 evidence (install/build/use-again/choose-over-alternative).
- Rollback: A100 findings feed V3 plan; no silent feature additions.

---

## 15. Final Decision Matrix

| Goal | Current Status | Main Failure | Proposed Fix | Metric | Gate |
|---|---|---|---|---|---|
| SIMPLE | PARTIAL | float money, truncation, 2000 ceiling, spec self-contradiction | P0-3 money API; Gate F option E; C-1…C-8 fixes | Money exact; 10k runnable; spec consistent | P0, Phase 1 |
| FAST | PARTIAL | 10k unmeasured; recursion ceiling | Bounded pre-measure; Gate F E; §7 protocol | Canonical 10k within workload target; linear scaling | Phase 0/1/2 |
| RELIABLE | **FAIL** | exit discarded; string-scan verdicts; float money | P0-1, P0-2, P0-3; §8 contract | Non-zero on failure; no false PASS; money exact | P0, Phase 0 |
| AI-MAINTAINABLE | PASS | test/testgen weak; doc contradictions | P0-2; C-fixes; testgen assertions | Verdict correctness; doc consistency | P0, Phase 3 |
| EASY-TO-EXTEND | PASS | recursion ceiling blocks scale | Gate F option E | 10k workloads run; coverage ≥0.88 | Phase 1/2/3 |

---

## 16. Architecture Verdict

**CONTINUE — with targeted, gated optimization (Gate F option E trampoline).**

- **NOT** VM REQUIRED, **NOT** REDESIGN: no objective evidence justifies either. The
  measured failure is a host-stack ceiling (architecture-internal, option E fixes it
  with the smallest possible change) plus a workload-dependent absolute constant that
  is not yet measured. A VM does not fix scaling/I/O and must first prove ≥2× in a
  time-boxed spike (Gate C).
- CONTINUE is not free: it is conditional on Phase-2 measurement and the §1.6 trigger
  table. If canonical-10k misses the workload target AND dispatch dominates AND Gate A
  options are exhausted, the plan **escalates** — it does not pat the interpreter on
  the back forever.
- This ruling converts "there is no v1.1.19" (V1 premise, stale) into the current
  truth: **v1.1.19 is the baseline to harden, and hardening is measured, not assumed.**

---

## 17. Evidence Sources

- `docs/roadmap/AILANG_STRATEGIC_PLAN_AUDIT_V1_1_19.md` — the v1.1.19 audit (current
  evidence source; this plan supersedes it only in framing, never in facts).
- `C:\Users\aleckhan\Projects\New_Validation3\AILANG_1_1_19_INDEPENDENT_DEVELOPER_EVALUATION.md`
  — independent evaluation of the published PyPI wheel (2.71s@1000, 26–40× vs Python,
  exit-code/verdict/money findings).
- `compiler/runtime/interpreter.py` (L79-86 execute returns main value; L51-53 recursion
  wiring), `compiler/runtime/sandbox.py` (L30 max_recursion=2000),
  `compiler/cli/main.py` (L430 discard; L1874 "FAIL" scan),
  `stdlib/convert.ail`, `stdlib/system.ail` (exit).
- `docs/reference/LANGUAGE_SPEC.md` §5.3 / §16; `docs/architecture/ARCHITECTURE_DECISIONS.md`
  (ADR-001/002), `docs/architecture/ADR_00X_BOUNDED_ITERATION.md`,
  `docs/adr/ADR-016-frame-ever-bound.md`.
- `docs/releases/PUBLICATION_MATRIX_v1_1_19.md`, `docs/releases/PRE_1_1_19_BASELINE.md`,
  `docs/roadmap/A100_COMMUNITY_VALIDATION.md`, `docs/roadmap/A100_FEATURE_BACKLOG.md`.
- `docs/roadmap/AILANG_STRATEGIC_ENGINEERING_PLAN.md` (V1) — goal metrics §2, §5B,
  Gates A–E §13, §11 money, §14 governance, §17 kill criteria remain authoritative.
