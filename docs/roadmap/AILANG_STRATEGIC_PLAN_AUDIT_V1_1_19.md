# AILang Strategic Plan Audit — v1.1.19

> **Audit date:** 2026-08-14
> **Version audited:** v1.1.19 (published artifact `ailang-lang==1.1.19`, commit `837e05c`)
> **Auditor classification scheme:** Every conclusion below is tagged
> **A.** VERIFIED FACT · **B.** EXISTING PROJECT DECISION · **C.** ENGINEERING INFERENCE · **D.** PROPOSED FUTURE DECISION.
> Any value not measured is explicitly labeled `NOT MEASURED — requires evidence.`
> **Read-only audit.** No code, spec, version, release, or repository changes were made.

---

## 1. Executive Summary

AILang v1.1.19 is a **published, installable release** (`ailang-lang==1.1.19`, commit `837e05c`,
2026-08-13). The three fixes the Strategic Plan marked as "unshipped" — **P0** single-execution
entry, **P1a** testgen emitting `.ail`, **P1b** `_frame_ever_bound` O(n²)→O(n) — **are shipped and
independently confirmed working** on the published artifact: the previously reported O(n²) scaling is
gone (growth is now roughly linear), testgen produces an executable `.ail` test that `ail test`
round-trips, and the independent evaluator achieved **8/8 maintenance edits that compile on first
try** and **10/10 byte-identical deterministic runs** (A).

The plan's own "weak / needs verification" list (runtime scaling, money/numeric ergonomics,
test/testgen coherence, recursion limits, documentation consistency) is confirmed accurate and is
now **fully re-verified against the published artifact** by an independent developer with **no
source access** (A).

**What the audit changes:** the plan's stated Phase-2 premise ("v1.1.19 does not exist", plan dated
2026-08-13) is **stale** (A); it must be rebased onto the published v1.1.19. The architecture itself
is **not the binding constraint** — the binding problems are (1) exit-code semantics, (2) string-scan
test verdicts, (3) the 2000-record recursion ceiling vs the 10,000-record §5B target, and (4) the
money/numeric model. Each is fixable without a rewrite (C).

**Architecture verdict: CONTINUE with a focused hardening phase.** No trigger for Gate B (bytecode
VM), Gate C (Rust core), or Gate D (JIT) has fired, because the 10,000-record workload **cannot even
be measured** under the current recursion ceiling (A, C). The evidence mandates an **ADR-level
decision on the iteration model** before the plan's Phase-2 gates can be evaluated (D).

**Final verdict: The Strategic Plan remains directionally sound; it requires (a) a v1.1.19 evidence
rebase, (b) a P0–P3 foundation-hardening milestone executed under feature freeze, and (c) a measured
10,000-record benchmark on the published artifact before any deeper architectural decision.** (C, D)

---

## 2. PROJECT STATE

```text
PROJECT STATE
Release: v1.1.19 — published 2026-08-13 (commit 837e05c; tag v1.1.19; PyPI ailang-lang==1.1.19)
Phase: A100 Community Validation (public release done; engineering freeze in effect)
Freeze: Language, compiler pipeline, runtime, stdlib, benchmark suite, feature backlog — frozen
        pending A100 evidence
Strategic Objective: AI-assisted, deterministic, low-maintenance business software development
Current Architecture: single-pass lexer → parser → CST/AST → semantic analysis → type check →
        IR → tree-walking interpreter in Python (~4,000 LOC core); recursion-only iteration;
        16-module stdlib; 26-command CLI; MCP server; LSP server; VS Code extension; local-first
        package manager
Current Evidence:
  - v1.1.19 shipped P0/P1a/P1b; independent evaluation confirms: O(n²) fixed (linear growth),
    testgen round-trip 1/1 PASS, 8/8 first-try compiles after maintenance, 10/10 byte-identical
    determinism (A)
  - Release gate: 1236 passed / 6 pre-existing env failures / 12 M136 regressions pass (A)
  - Canonical build (wheel): static_analyzer build min 244 ms (was 713 ms in 1.1.18) (A)
  - Baseline (PRE_1_1_19): 1.1.18 published wheel was O(n²); testgen emitted pytest .py that
    `ail test` ignored; testgen round-trip 0% (A)
Current Problems (verified on published artifact):
  - P0: main()/test return values discarded — process exit always 0 (A)
  - P1: test pass/fail is a string scan for "FAIL"; return-1-with-no-output reported PASS (A)
  - P2: hard recursion cap = 2000 records; for-in lowers to recursion (same wall) (A)
  - P3: IEEE-754 float money artifacts (24173.85999999999); no to_float; to_int truncates (A)
  - P4: ~26–40× slower than Python at useful sizes; linear but large constant (A)
  - Doc contradictions: fmt/heal reorder claims, hidden --experimental-loops, doctor venv scan (A)
Requested Review: Strategic plan + architecture audit against published v1.1.19 (read-only)
Authorized: YES — audit report only; no implementation, no version/release/commit changes
```

---

## 3. Purpose

This audit answers a single question for the AILang project leadership:

> **Given what the independent evaluator measured against the published v1.1.19 artifact, does the
> Strategic Engineering Plan's architecture and roadmap still achieve the five product goals
> (SIMPLE, FAST, RELIABLE, AI-MAINTAINABLE, EASY TO EXTEND)? And if not, what must change first?**

It is strictly read-only: no code, spec, pyproject, version, release, or commit changes were made.
The evaluation document at `New_Validation3\AILANG_1_1_19_INDEPENDENT_DEVELOPER_EVALUATION.md` is
treated as **evidence**, not as the roadmap. This report flags where the plan's claims are now stale,
where they are confirmed, and where they remain `NOT MEASURED`.

---

## 4. Part 1 — Goal Audit

Each goal is rated **PASS / PARTIAL / FAIL / NOT MEASURED** against v1.1.19 measured evidence.

### 4.1 SIMPLE — **PARTIAL (leaning FAIL for business use)**

| Evidence | Classification |
|---|---|
| Recursion-only iteration with a hard 2000-frame cap; any realistic dataset app hits it | A |
| `for-in` exists but is hidden behind `--experimental-loops`, not in `ail run --help`, syntax inconsistent (`for n in nums { }` vs `if (cond) { }`) | A |
| No `assert` primitive; tests are "functions that don't print FAIL" | A |
| No `to_float`, no Decimal; money requires hand-rolled parsing | A |
| Bottom-up ordering is a real mental tax (2× SEM002 in first app) but is learnable and checked pre-flight | A |
| Plan §2.4: "simplicity" is about first-compile success, not LOC | B |

**Conclusion:** The simple-to-compile story holds (first-try compiles are real), but *simple to do
business* does not: money, large datasets, and reliable tests are all three structurally hard (C).

### 4.2 FAST — **PARTIAL**

| Evidence | Classification |
|---|---|
| O(n²) fixed: 400→800 records took 1.53× (linear-ish growth) on published wheel | A |
| ~26–40× slower than Python; 1000 records = 2.71 s vs 0.10 s | A |
| Compile 0.30 s constant; 990-LOC build 244 ms on wheel | A |
| 10,000-record workload §5B target (< 5 s) — `NOT MEASURED` (cannot run >2000) | NOT MEASURED |
| Memory < 300 MB @10k — `NOT MEASURED` | NOT MEASURED |
| Gate B/C triggers (cannot meet target at 10k + profiler attribution) — **cannot be evaluated** until 10k runs | NOT MEASURED |

**Conclusion:** Linear scaling target is met; absolute-time target is unmeasurable today (C). The
2000-record ceiling must be resolved before any performance verdict can be final.

### 4.3 RELIABLE — **FAIL**

| Evidence | Classification |
|---|---|
| Determinism: 10/10 byte-identical outputs, 5/5 identical builds | A |
| Exit code always 0 — a missing-CSV error path silently "succeeded" (exit 0) | A |
| Test runner false-PASS on return-1-no-output and on `main` returning 1 | A |
| Float money artifacts in a finance domain (24173.85999999999) | A |
| Plan goal: "zero correctness bugs per release" | B |

**Conclusion:** The single most important goal FAILS. A reliability-first language cannot ship exit
code 0 on failure or green-light failing tests. These are contract bugs, not design trade-offs (C).

### 4.4 AI-MAINTAINABLE — **PASS** (strongest pillar)

| Evidence | Classification |
|---|---|
| 8/8 maintenance edits compiled first-try; dead code caught by two tools | A |
| `context --json`, offline `docs`, `explain`, `rename` w/ rollback rated 5/5 | A |
| `test`/`testgen` rated 2/5 (verdicts unreliable, compile-only generation) | A |
| fmt/heal overpromise reordering (doc contradiction) | A |

**Conclusion:** Tooling excellence is real and independently confirmed. The single weak point is the
same P0/P1 pair (exit codes + test verdicts) — tools that **lie to the AI** in the two steps that
matter most (verification). Fix those and this goal is near-total (C).

### 4.5 EASY TO EXTEND — **PASS** (with a documented wall)

| Evidence | Classification |
|---|---|
| v1.1.19 shipped 22 files / 1268 insertions; MCP, LSP, package manager, testgen, rename, loops all landed | A |
| Single-pass tree-walking design is ~4,000 LOC and has absorbed all of the above | C |
| ADR-004: files beyond ~100 functions / ~1000 LOC become hard to order; modules mitigate | B |
| Recursion ceiling is a hard wall for extending *data scale* (not code scale) | A |

**Conclusion:** The architecture demonstrably absorbs new tools and modules. Its extension wall is
the iteration model, not the codebase shape (C).

---

## 5. Part 2 — v1.1.19 Findings Audit (P0–P4)

Each finding is re-audited against the plan's own goals and governance. **No release-blocking
dispute:** the evaluator's findings reproduce on the published artifact (A).

### 5.1 P0 — Exit-code semantics: CONFIRMED, contract contradiction (A)

- **Facts:** `cmd_run` (main.py) returns 0 unconditionally after `runtime.execute(...)`; the
  interpreter's returned value from `main()` is not propagated to `sys.exit`. `LANGUAGE_SPEC.md`
  §5.3 explicitly documents "The return value of `main` is discarded by the CLI (use `print()` for
  output)", while §16 documents the exit-code contract "0 = Success / Non-zero = Error occurred".
  `system.exit(code)` exists in the stdlib. (A)
- **Audit classification:** the *language spec* deliberately discards the value (B — existing
  project decision) but the *CLI/spec contract* (B) contradicts it. The reliability goal demands
  non-zero exits on failure. The plan's own governance (Q4/Q5, §7 checklist) rates this a
  **release-blocking reliability defect** (C).
- **Not a language feature request** — it is a tooling/CLI contract fix: propagate the interpreter
  result to the process exit code in `cmd_run`/`cmd_test`. Small, low-risk, no language change (C).

### 5.2 P1 — Test verdicts: CONFIRMED, false-negative path proven (A)

- **Facts:** `cmd_test` (main.py ~1571; "FAIL" scan ~1874) treats a test as PASS if output contains
  no `FAIL`. A test returning 1 with no output → **PASS**. `test_main_return_fail.ail` → PASS.
  No `assert` primitive; coverage NOT IMPLEMENTED; testgen generates only
  `fn test_app_compiles() { return 0 }` (compilation-only) and its report claims `test_count: 2`
  for a file containing 1 test. (A)
- **Audit classification:** testing is the weakest pillar (C). The plan's Phase-2 premise
  ("testgen emits pytest `.py` that `ail test` ignores") is **fixed** in v1.1.19 (A), but the
  deeper semantics remain. Reliability goal: **FAIL**. Requires an `assert`-based verdict (C, D).
- `test_count` reporting inconsistency is a small, clear bug (A).

### 5.3 P2 — Recursion ceiling: CONFIRMED; the biggest strategic tension (A)

- **Facts:** `sandbox.py` `max_recursion: int = 2000`; interpreter `_max_call_depth`; clean
  structured error `Recursion depth exceeded (limit: 2000)`. `--experimental-loops` lowers to
  recursion — same wall (ADR_00X_BOUNDED_ITERATION). Native stdlib ops (list.sum, json, csv) scale
  flat because they run in Python (A).
- **Audit classification:** ADR-001/002 made recursion-only iteration **permanent** (B). This is
  the single architectural decision that conflicts with the plan's own §5B 10,000-record target (C).
  The plan's "restrict claim to ≤2000-record apps" fallback (§13, performance target unrealistic) is
  a **documented contingency**, but it materially narrows the business-applications promise (C).
- **Decision required (D):** lift the ceiling with evidence (e.g., verified trampoline/iterative
  lowering of tail recursion), add a native iterative path for the data passes business apps use,
  or formally adopt the ≤2000-record claim. This is an ADR-level decision, **not** a Gate B trigger
  (C).

### 5.4 P3 — Money/numeric model: CONFIRMED (A)

- **Facts:** `24173.85999999999` vs Decimal `24173.86`; `convert.to_int("12.34")` raises; no
  `to_float`; `convert.to_int`/`to_number` = `__native_to_int` (silent truncation). The evaluator
  had to hand-roll decimal parsing with `pow10` recursion. (A)
- **Audit classification:** plan already lists this as "needs verification" and recommends integer
  minor-units (cents) conversion (B). The **fix is stdlib + docs**, not a runtime type-system change
  (C): add `to_cents`/`from_cents` (exact string parsing) and a documented money convention, plus
  decide truncation semantics of `to_int` (D). No Decimal type is required for v1.x money safety
  (C, D).

### 5.5 P4 — Performance: CONFIRMED; linear now, constant large (A)

- **Facts:** growth is roughly linear (400→800 = 1.53×); absolute is 26–40× slower than Python;
  10000 records in Python = 0.16 s flat. Compile is ~11% of a 1000-record run; interpreter
  recursion dominates. (A)
- **Audit classification:** Gate A (interpreter optimization) evidence is **produced** (P1b) and
  confirmed (A). Gate B trigger is **NOT satisfied**: the 10k workload cannot be measured, so "cannot
  meet target" is unproven; per-call dispatch overhead at scale is `NOT MEASURED`. Holding Gates B–D
  is correct and plan-compliant (C).

### 5.6 Doc contradictions: CONFIRMED, three instances (A)

1. `ail context --json` and `ail heal forward_reference` promise that `ail fmt` reorders functions;
   `ail fmt` never reorders (FORMATTER_ARCHITECTURE.md is explicit). (A)
2. `--experimental-loops` is undocumented in `ail run --help` / `ail help`. (A)
3. `ail doctor` recursively scans CWD including a nested venv's site-packages → health 0/100 next to
   a venv. (A)

These are documentation/tooling defects, cheap to fix, and they **break AI trust** in a
toolchain whose selling point is AI trust (C).

---

## 6. Part 3 — Architecture Fitness

Per-component verdict against the five goals (GREEN = fit; YELLOW = fit with known friction;
ORANGE = structural constraint; RED = contract broken).

| Component | Verdict | Evidence basis |
|---|---|---|
| Lexer / Parser / CST / AST | GREEN | stable, deterministic, no hangs (A) |
| Semantic analysis + `ail check` | GREEN | SEM002/WHILE001 pre-execution; catches forward refs (A) |
| Type checker | YELLOW | TYP005 stricter than runtime (to_string-of-unknown); confusing (A) |
| Tree-walking interpreter | YELLOW | linear after P1b, deterministic; 26–40× constant (A) |
| Iteration model (recursion-only) | ORANGE | 2000 cap vs 10k §5B target; ADR-001/002 permanent (A, B) |
| Numeric model (float-only) | ORANGE | money artifacts; silent truncation; no exact path (A, C) |
| Testing model (`ail test`) | RED | string-scan verdicts; false PASS; no assert; no coverage (A) |
| CLI exit-code contract | RED | always 0 on failure (A) |
| Stdlib | GREEN-YELLOW | complete for target workloads except money/float; native ops scale flat (A) |
| Static analyzer | GREEN | dead-code detection real; self-analyzed (A) |
| Formatter | GREEN | works as formatter; docs overpromise reorder (A) |
| MCP / LSP / package manager | GREEN | 6 MCP tools work; LSP resolves modules; local-first packages (A) |
| Build / deployment | YELLOW | `ail build` = compile check only, no artifact; ship source + runtime (A, B) |

**Overall:** The core architecture is **fit for the product's current scale** and is **not the
binding constraint**. The binding constraints are contracts (exit codes, test verdicts), the
iteration model ceiling, and the numeric model (C). No architectural rewrite is justified by current
evidence (C).

---

## 7. Part 4 — Feature-Creep Audit & Foundation Freeze

The project has shipped **26 CLI commands, MCP, LSP, VS Code extension, a package manager, a renamer,
an experimental loop lowering, a test generator, a benchmark tool, a static analyzer, and 16 stdlib
modules** — while the foundational contract problems (exit codes, test verdicts, money, recursion)
persist into v1.1.19 (A). This is the classic "tools ahead of foundation" pattern (C).

**Verdict: FOUNDATION FREEZE.** Freeze all new language features, new stdlib modules, new CLI
commands, new AI integrations, and new tooling until the P0–P3 foundation items (§11) are shipped
and re-verified on the published artifact (D). The A100 community-validation milestone is the
correct venue for the *measurement* work — but it must run against a hardened artifact, not the
current one (C).

---

## 8. Part 5 — AI-Maintenance 12-Step Loop

The evaluator applied 8 maintenance edits (M1–M6, U1–U2) to both AILang and Python apps; all 8
passed `ail check`/`build` **first try** — the strongest measured result in the entire audit (A).

| Step | Tool | Verified on v1.1.19 | Rating |
|---|---|---|---|
| 1. Discover project | `ail context --json` | accurate, complete rules | 5/5 |
| 2. Read rules | `ail docs` (offline) | works, no network | 5/5 |
| 3. Understand errors | `ail explain <CODE>` | clear, actionable | 5/5 |
| 4. Order dependencies | `ail order` | flags unreachable fns; L0 levels not meaningful | 4/5 |
| 5. Analyze | `ail static-analyzer` | dead code found | 4/5 |
| 6. Rename | `ail rename` | dry-run, diff, rollback bundle, verify | 5/5 |
| 7. Format | `ail fmt` | works as formatter | 3/5 (docs overpromise) |
| 8. Heal | `ail heal` | 7 topics work; SEM002 unknown; reorder claim false | 3/5 |
| 9. Check/build | `ail check` / `ail build` | 0.30 s, reliable, caught TYP005 | 5/5 |
| 10. Test | `ail test` / `ail testgen` | **false PASS; compile-only** | 2/5 |
| 11. Run + exit codes | `ail run` | **exit always 0** | 1/5 |
| 12. Doctor | `ail doctor` | alarmist near venvs | 3/5 |

**Conclusion:** 9 of 12 loop steps are strong or excellent; the two **verification steps that an AI
relies on to know "is it correct?"** — Test (10) and Run/exit (11) — are the ones that lie (A, C).
An AI-maintainable language whose verification signals are unreliable cannot claim the goal (C).
Fix order: exit codes → assert verdicts → docs contradictions → doctor venv exclusion (D).

---

## 9. Part 6 — Acceptance Criteria

Measurable, plan-aligned criteria. `Target` taken from the Strategic Plan where defined; otherwise
proposed with `(D)`.

| # | Goal | Metric | Current (v1.1.19) | Target | Evidence Required | Gate |
|---|---|---|---|---|---|---|
| 1 | RELIABLE | Non-zero exit on failure | FAIL (always 0) | `main`/test non-zero → process non-zero | reproduce + test on wheel | Release-blocking |
| 2 | RELIABLE | Test verdict truthfulness | FAIL (false PASS) | 100% of failing probes reported FAIL | probe suite on wheel | Release-blocking |
| 3 | RELIABLE | Money accuracy | FAIL (float artifacts) | exact cents path; documented truncation | 1000-record money app on wheel | Release-blocking |
| 4 | RELIABLE | Determinism | PASS (10/10 byte-identical) | maintained | automated gate | Release |
| 5 | FAST | Scaling | PASS (≈linear; 400→800 1.53×) | 1.8–2.2× per doubling | benchmark on wheel | Gate A |
| 6 | FAST | 10k-record workload | NOT MEASURED (ceiling 2000) | < 5 s (§5B) | post-iteration-decision run | Gate B eval |
| 7 | FAST | 1000-LOC build | PASS (244 ms wheel) | < 300 ms | wheel measurement | Release |
| 8 | AI-MAINTAIN | First-try compile after edit | PASS (8/8) | ≥ 8/8 | maintenance probe suite | Release |
| 9 | SIMPLE | Time to working app | NOT MEASURED (fresh-dev) | < 10 min, no tracebacks (D) | A100 onboarding | A100 |
| 10 | EASY-TO-EXTEND | New stdlib/tool landed | PASS (22 files in v1.1.19) | no architecture change needed | ADR-review log | Continuous |

---

## 10. Part 7 — Decision Gates

| Gate | Plan Definition | Status at v1.1.19 | Action |
|---|---|---|---|
| Gate A — optimize interpreter | ~50-LOC incremental, zero-risk fix | **DELIVERED** (P1b in v1.1.19; O(n²) gone, confirmed) | Record as passed; proceed to measurement |
| Gate B — bytecode VM | 10k workload can't meet §5B **AND** dispatch overhead ≥50% **AND** Gate A exhausted | **NOT FIRED** — 10k workload unmeasurable under ceiling | Resolve iteration model first; re-evaluate with data |
| Gate C — Rust core | explicit §6.6 trigger | NOT FIRED | Hold; "faster because Rust" is explicitly not a trigger |
| Gate D — JIT / speculative | explicit trigger only | NOT FIRED | Hold |
| Gate E — self-hosting | later phase | NOT FIRED | Hold |
| **New Gate F (D)** | Iteration-model decision: lift ceiling with evidence / native iterative path / documented ≤2000 claim | NO DECISION EXISTS | ADR required before Phase-2 gates can be evaluated |

**Audit position:** Gates B–E are correctly on hold; the missing piece is an **ADR on the iteration
model** (Gate F), because the plan's own gate logic cannot advance without a runnable 10k workload
(C, D).

---

## 11. Part 8 — Architecture Verdict

**CONTINUE — with a focused, evidence-gated hardening phase.** The architecture has been
independently confirmed to be: deterministic, linear after the shipped fix, strong on compile-time
checking, and extensible (tools, MCP, LSP, package manager all landed). The binding constraints are
**contract-level, not architectural**: exit codes, test verdicts, the numeric model, and one genuine
architectural decision — the recursion-only iteration ceiling vs the 10k target (C).

A pivot (Gate B/C) would be justified **only if**, after the iteration-model decision, a measured
10,000-record canonical workload exceeds §5B by >2× with ≥50% of time attributed to host dispatch
overhead and Gate A exhausted (D). None of that evidence exists yet (C).

---

## 12. Part 9 — Ranked Next Phase (P0–P3)

Deliverables under the foundation freeze, in order. Each must be verified against the **published**
artifact by an independent probe, not the source tree (D).

**P0 (release-blocking, small, contract fixes):**
- P0-1 Propagate `main()`/test return values to the process exit code (`cmd_run`, `cmd_test`);
  align `LANGUAGE_SPEC.md` §5.3 with §16. (C, D)
- P0-2 Assert-based test verdicts: add `assert` (or `test.expect`) primitive; a failing assertion
  must fail the test regardless of printed text; remove string-scan semantics. Fix `testgen`'s
  `test_count` reporting. (C, D)
- P0-3 Money: add exact `to_cents`/`from_cents` (string-based), document `to_int` truncation, add
  `to_float`; a documented money convention. No Decimal runtime type. (D)

**P1 (target-meeting, ADR-gated):**
- P1-1 Iteration model ADR (Gate F): lift 2000 ceiling with measured evidence (trampoline or
  iterative lowering of the recursive data passes business apps use), or formally adopt the
  ≤2000-record product claim. (D)
- P1-2 Fix doc contradictions: fmt/heal reorder claims, document `--experimental-loops`, exclude
  venvs from `ail doctor`. (D)

**P2 (measurement):**
- P2-1 Run the 10,000-record canonical workload + memory on the hardened published artifact;
  publish numbers to decide Gate B (D).
- P2-2 Test coverage support in `ail test` (D).

**P3 (governance):**
- P3-1 Re-evaluate Gates B–E with the §11 data; record "Gate A sufficient" or move to a Gate B
  spike (D).
- P3-2 Launch A100 community validation **against the hardened artifact** (D).

---

## 13. Part 10 — What NOT to Build

| Item | Why not | Classification |
|---|---|---|
| Bytecode VM / Rust core / JIT | No §6.6/§13 trigger fired; "faster" alone is not a trigger | C, B |
| Default loops / for-in promotion | ADR-00X experimental; A100 backlog restricts; recursion ceiling is the real issue | B |
| New stdlib modules (string.replace, list.set, JSON pretty, etc.) | A100 backlog explicitly defers; money path (P0-3) is the only justified addition | B |
| Decimal/rich numeric types in the runtime | Not needed for v1.x money safety; stdlib cents path suffices | C, D |
| New CLI commands / MCP tools / LSP features / AI integrations | Foundation freeze §7; tooling is already over-built vs foundation | D |
| Standalone executable / packaging build-out | `ail build` is compile-check by design; deployment = ship source + runtime works | B |
| Auto-reordering of functions (compiler topological sort) | Rejected in DEPENDENCY_ORDERING_ANALYSIS on determinism/AI-clarity grounds | B |
| Self-hosting (Gate E) | Not before Phase 2/3 data | B |
| Marketing/benchmark apps for hype | Evidence first; benchmarks already exist (8,515-LOC inventory) | C |

---

## 14. Part 11 — Final Strategic Verdict

**The Strategic Engineering Plan is directionally sound and its risk assessment was accurate.**
Every item it flagged as "weak / needs verification" was independently confirmed on the published
artifact; every fix it claimed was unshipped is now shipped and confirmed (A). The plan does **not**
need a rewrite — it needs **an evidence rebase onto v1.1.19** (the "v1.1.19 does not exist" premise
is stale) and **a P0–P3 foundation-hardening milestone executed under feature freeze**, before the
Phase-2 gates (B–E) can be honestly evaluated (C, D).

**The one strategic decision that cannot be deferred: the iteration model.** The recursion-only
design (ADR-001/002, permanent) caps business apps at ~2000 records, which conflicts with the plan's
own §5B 10,000-record target. Everything else binding (exit codes, test verdicts, money) is a
small, contract-level fix. Resolve the iteration model by ADR, harden the P0–P3 items, re-measure
against the published artifact, then launch A100 (D).

If those four items ship and verify, AILang's independently confirmed strengths — first-try
compiles, perfect determinism, best-in-class AI tooling — become the foundation of a defensible
production claim. If the iteration model is not resolved, the product claim must be narrowed to
"AI-assisted apps up to ~2000 records," which the plan already contemplated (B).

---

## 15. Evidence Sources

1. `docs/roadmap/AILANG_STRATEGIC_ENGINEERING_PLAN.md` — goals, §5 targets, §13 gates, Phase-2 premise.
2. `docs/roadmap/PRODUCT_ROADMAP.md` — milestones, Phase 5B, A100.
3. `DEVELOPMENT_STATUS.md` — current phase/freeze.
4. `PROJECT_MEMORY.md` — cross-milestone notes.
5. `CHANGELOG.md` — v1.1.19 entry.
6. `docs/releases/PUBLICATION_MATRIX_v1_1_19.md` — release gate, hashes, wheel SHA-256, build numbers.
7. `docs/releases/PRE_1_1_19_BASELINE.md` — 1.1.18 baseline, 1242 collected tests, testgen 0% baseline.
8. `M137_RELEASE_AND_PERFORMANCE_INVESTIGATION.md` — O(n²) attribution (Environment.resolve frame-chain walk, 74–80% runtime), not `list.contains`.
9. `docs/adr/ADR-016-frame-ever-bound.md` — P1b root cause (previously working-tree-only; now shipped).
10. `docs/architecture/ARCHITECTURE_DECISIONS.md` (ADR-001/002 recursion-only), `docs/architecture/ADR_00X_BOUNDED_ITERATION.md` (experimental for-in), `docs/architecture/DEPENDENCY_ORDERING_ANALYSIS.md` (auto-reorder rejected), `docs/architecture/FORMATTER_ARCHITECTURE.md` (never reorders).
11. `docs/runtime/optimizations.md` (RTO-001 lookup cache).
12. `C:\Users\aleckhan\Projects\New_Validation3\AILANG_1_1_19_INDEPENDENT_DEVELOPER_EVALUATION.md` — primary v1.1.19 evidence (independent developer, published PyPI artifact only, fresh venv, no source access).
13. Source inspection: `compiler/cli/main.py` (cmd_run, cmd_test FAIL-scan, cmd_testgen), `compiler/runtime/interpreter.py`, `compiler/runtime/sandbox.py` (max_recursion=2000), `compiler/runtime/environment.py`, `stdlib/convert.ail`, `docs/reference/LANGUAGE_SPEC.md` (§5.3, §16), `compiler/docs/LANGUAGE_SPEC.md`.
14. Git state: HEAD `837e05c` "release: v1.1.19"; tag `v1.1.19`; `pyproject.toml` version 1.1.19; working tree dirty (AGENTS.md, reports/dependency_ordering.json, removed generated tests, untracked generated `.ail` files).
