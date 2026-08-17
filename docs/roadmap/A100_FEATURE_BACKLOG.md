# A100 Evidence-Gated Feature Backlog

**Status:** Engineering freeze (v1.1.17). Analysis only — no implementation.
**Purpose:** Gate every proposed feature on evidence the A100 protocol can actually
produce, and assign a classification + trigger for each.
**Scope:** Five proposals only (batch diagnostics, stdlib additions, verbosity/patterns,
for-in default, safety-gate visibility).

---

## 0. Verified Facts (checked against current tree)

| Claim | Verdict |
|-------|---------|
| `string.replace` missing from `stdlib/string.ail` | ✅ Confirmed absent |
| `list.set` missing from `stdlib/list.ail` | ✅ Confirmed absent |
| `json` has only `parse` + `stringify` (no pretty / no lines streaming) | ✅ Confirmed |
| `csv.parse` + `csv.parse_header` exist | ✅ Confirmed present (relevant to A100 task) |
| Error reporter collects a list; CLI prints *all* diagnostics in one run | ✅ Confirmed (`DiagnosticReporter.diagnostics`, `for diagnostic in reporter.diagnostics`) |
| Analyzer has cascade suppression for follow-on errors | ✅ Confirmed (MOD004/LANG002/LANG003) |
| `for-in` requires `--experimental-loops`; bare `for` → PAR012 | ✅ Confirmed in spec |
| A100 Phase-1 task = expense tracker: CSV import, categories, summary report | ✅ Per `A100_COMMUNITY_VALIDATION.md` |

---

## 1. Batch / Multi-Error Compiler Reporting

**A. Supporting evidence:**
- Playbook §Benchmark Lessons: "AILang reports errors one at a time; batch
  reporting would reduce iterations" (B7 observation).
- `ENGINEERING_EVIDENCE_REPORT.md`: B2/B3 iterations were driven by
  single-error discovery ("1 compile → all fixed" is listed as a *desirable*
  property, not current behavior).

**B. Evidence type:** Historical benchmark data (v0.6.x–v0.7.x). Also partially
**stale**: the reporter already collects and prints multiple diagnostics today.
The "one at a time" gap is narrower than the playbook implies — it persists mainly
across *phases* (discovery → analyze → type-check) and via cascade suppression.

**C. Can A100 measure it?** **Yes, with zero baseline change.** The protocol already
counts "AI correction iterations" and "compiler/runtime errors." An `ail check`
run that surfaces N errors in one invocation vs N invocations is directly
observable in the iteration metric without modifying the protocol.

**D. A100 metric:** AI correction iterations; error count; time to first working
version (secondary).

**E. Governance (Q1–Q6):**
- Q1 (mission): supports AI-assisted, deterministic dev. ✅
- Q2 (measured pain): the playbook's own recorded pain. ✅
- Q3 (existing tooling): partial — multi-error display already exists; the
  remaining work is cross-phase batching. ⚠ Partially solved already.
- Q4 (expressiveness): no change. ❌ (not the point)
- Q5 (determinism): neutral — reporting only. ✅
- Q6 (AI-first?): diagnostics UX; Python ecosystems do this well too. ⚠
- **Net:** low-risk tooling improvement, but the magnitude of remaining benefit
  is unproven *today* because a large part already shipped.

**F. Classification:** **A100 EXPERIMENTAL HYPOTHESIS** (measure first; likely
cheap enough to ship during A100 without changing the baseline).

**G. Trigger to ship:** A100 participants hitting ≥1 correction iteration purely
due to discovering a second error only after fixing the first (≥2 independent
participants).

---

## 2. A100-Domain Stdlib Additions (`string.replace`, `list.set`, JSON pretty/lines)

**A. Supporting evidence:**
- Playbook Stdlib Existence Table lists `string.replace` and `list.set` as ❌ with
  manual fallbacks.
- B2 measured stdlib gaps as the **#1 friction point** (42% of B2 errors).
- Prior stdlib additions (`file.listdir`, `convert.to_number` fix) measurably cut
  B2 L2 from 3→1 iterations (67%).

**B. Evidence type:** Historical benchmark data + engineering review. **Not**
external-user evidence. The A100 task (expense tracker: CSV import, categories,
summary report) is served by `csv.parse` (exists) and `string.split` (exists);
**none of the three proposed APIs is demonstrably required by the A100 task.**

**C. Can A100 measure it?** **No cleanly.** The A100 task as written does not force
use of `string.replace`, `list.set`, or JSON pretty/lines. Adding them would be
shipping APIs the baseline cannot exercise — exactly the "Python parity" trap.

**D. A100 metric:** Would target AI correction iterations / frustration — but only
if participants actually need them, which the current task does not require.

**E. Governance (Q1–Q6):**
- Q1: mission-aligned only if needed by real tasks. ⚠
- Q2: measured pain yes (historically), but not tied to the A100 workload. ⚠
- Q3: fallbacks exist (character-by-character, map wrappers). ✅ covered.
- Q4: expressiveness increase. ✅
- Q5: determinism neutral. ✅
- Q6: these are generic language features every language has. ❌
- **Net:** NOT justified by the A100 baseline. Adding them now is parity-driven.

**F. Classification:** **POST-A100 CANDIDATE** (JSON pretty/lines) and
**REJECT / NOT JUSTIFIED** for `string.replace`/`list.set` *unless* the A100 task
is extended to force them.

**G. Trigger to ship:** A participant reaches for `string.replace` or `list.set`
(or needs readable/streaming JSON) during the A100 task **without being prompted**
(≥2 independent occurrences), or the A100 task specification is amended to include
a transformation/substitution requirement.

---

## 3. Verbosity Reduction / Standard Pattern Library

**A. Supporting evidence:**
- `INVENTORY_PYTHON_COMPARISON.md`: AILang is 33% more LOC per function (9.85 vs
  7.40) due to recursion + unique names + mandatory initializers/returns.
- Playbook: hand-written recursive filter/map/reduce/search wrappers are the
  standard idiom; `examples/patterns/` codifies them.

**B. Evidence type:** Historical benchmark data + engineering review. The 33% LOC
tax is well measured; whether it translates to *perceived frustration* for a
stranger is not.

**C. Can A100 measure it?** **Yes, partially.** A100 records "frustration rating"
and "which was easier to build." LOC/verbosity itself is not a metric, but its
effect on frustration and time-to-first-working-version is.

**D. A100 metric:** Frustration; time to first working version; "easier to build."

**E. Governance (Q1–Q6):**
- Q1: reduces AI iteration cost — core mission. ✅
- Q2: measured pain (33% tax). ✅
- Q3: partial mitigation exists (playbook + `list.filter/sum/map` already in stdlib). ⚠
- Q4: a stdlib pattern library increases expressiveness. ✅
- Q5: pure additive stdlib — deterministic. ✅
- Q6: every language has stdlib conveniences. ⚠
- **Net:** genuinely aligned, but overlaps with existing `list.*` helpers; the
  *residual* need is unmeasured.

**F. Classification:** **POST-A100 CANDIDATE** — do not pre-build a pattern library
the baseline doesn't prove people need.

**G. Trigger to ship:** ≥2 participants independently re-implement the same
recursive filter/map/reduce/search helper during the A100 task (recorded in the
study's first-impression bug/notes log).

---

## 4. Make Experimental `for-in` Loops the Default

**A. Supporting evidence:**
- Spec: `for-in` exists behind `--experimental-loops`, lowers to recursion.
- `INVENTORY_PYTHON_COMPARISON.md`: recursion is a documented source of the 33%
  LOC tax and the verbosity/frustration signal.
- **No evidence** that a *default* loop changes outcome metrics: B4/B5/B6 showed
  parity for refactoring/upgrade/maintenance, and B7 showed AGENTS.md alone saved
  3× iterations. Loops would most plausibly affect *perception* (frustration,
  "which was easier"), not measured engineering outcomes.

**B. Evidence type:** Engineering review + inference. **No** external-user evidence.
This is a **language-design change** (determinism surface: lowering is
compile-time and deterministic, but it alters the language's public grammar).

**C. Can A100 measure it?** **Partially.** A100 records frustration and
"which was easier," which are the plausible channels. But the protocol is a
head-to-head *task* comparison — it cannot isolate "loops" as the causal variable
unless the study is amended to compare default-loops vs flagged-loops groups,
which **would change the baseline** (forbidden).

**D. A100 metric:** Frustration; "easier to build"; "would choose AILang again."
(Not iterations — that channel is already parity.)

**E. Governance (Q1–Q6):**
- Q1: supports AI-assisted dev only if loops reduce real friction. ⚠
- Q2: measured pain = LOC tax, not loop absence specifically. ⚠
- Q3: existing tooling = `--experimental-loops` already ships the capability. ✅
- Q4: expressiveness increase (clear). ✅
- Q5: determinism impact = lowering is deterministic; risk is LOW but non-zero
  (new public syntax, migration of existing code/playbook/anti-pattern docs). ⚠
- Q6: loops are the most generic language feature imaginable. ❌
- **Net:** high-attractiveness, high-governance-cost change. Must be ADR-gated,
  not shipped on recommendation.

**F. Classification:** **A100 EXPERIMENTAL HYPOTHESIS** — explicitly NOT a
precondition and NOT a pre-A100 change. It is a language-design decision whose
only legitimate trigger is external-user evidence.

**G. Trigger to ship (sufficient for ADR):** One of:
1. ≥2 A100 participants independently name loop absence as a source of
   frustration or difficulty (verbatim, in the study notes) **and** mark AILang
   "would choose again" = No, **or**
2. ≥1 participant explicitly states they would have picked AILang if loops
   existed, **or**
3. Post-A100 survey where loop-absence is raised by ≥2/3 of participants who
   completed the maintenance phase.
A single "it'd be nicer with loops" comment is **not** sufficient.

---

## 5. Make Compile-Time Safety Guarantees Visible in `ail check` / `ail doctor`

**A. Supporting evidence:**
- `INVENTORY_PYTHON_COMPARISON.md` §4.2/4.5: AILang eliminates null-pointer,
  injection, and implicit-coercion bug classes — but these are **properties**, not
  a visible UX feature.
- `ail doctor` already reports a health score and "All versions consistent";
  `ail check` already surfaces ordering/import violations.

**B. Evidence type:** Engineering review + inference. The *claim* (zero silent
runtime failures, batch compile gate) is measured; the *perception* that it helps
a stranger is not.

**C. Can A100 measure it?** **Yes, cleanly and without baseline change.** A100
records "compiler/runtime errors" and "frustration rating." If participants
see compile-time errors where they expected runtime crashes, error-count and
frustration metrics capture it. Making the guarantees *presented* more visibly
does not alter the protocol.

**D. A100 metric:** Error count; frustration; confidence (maintenance phase);
"would choose AILang again."

**E. Governance (Q1–Q6):**
- Q1: turns the core differentiator into user-visible value. ✅
- Q2: the differentiator is the measured strength — surfacing it is cheap. ✅
- Q3: `ail doctor` already exists — this is incremental presentation. ✅
- Q4: no language change. ❌ (not relevant)
- Q5: determinism neutral. ✅
- Q6: tooling UX, standard in any ecosystem. ✅
- **Net:** cheapest, most mission-aligned, zero-risk item on this list.

**F. Classification:** **A100 PRECONDITION** — low-cost DX polish that directly
strengthens the A100 first-impression target ("first successful program in under
10 minutes, zero tracebacks"). It does not change the baseline protocol.

**G. Trigger:** None required for the *presentation-only* subset (e.g., `ail check`
exit summary listing "0 runtime-error classes possible"). Any *new checks or
guarantees* must wait for A100 error-count evidence.

---

## 6. Classification Summary

| Proposal | Classification | A100 trigger to ship |
|----------|---------------|----------------------|
| 1. Batch/multi-error reporting | EXPERIMENTAL HYPOTHESIS | ≥2 participants hit iteration cost from second-error-after-first-fix |
| 2a. `string.replace` / `list.set` | REJECT / NOT JUSTIFIED (for current A100 task) | ≥2 unprompted reaches, or A100 task amended to require them |
| 2b. JSON pretty / lines | POST-A100 CANDIDATE | Same evidence gate as 2a |
| 3. Verbosity / pattern library | POST-A100 CANDIDATE | ≥2 participants independently re-implement same recursive helper |
| 4. `for-in` default | EXPERIMENTAL HYPOTHESIS (ADR-gated) | ≥2 participants cite loop absence as frustration/blocker + "would choose" = No; or ≥1 explicit "would pick AILang if loops existed"; or post-study loop-absence from ≥2/3 maintenance completers |
| 5. Safety-guarantee visibility (presentation-only) | A100 PRECONDITION | None (presentation subset); new guarantees gated on error-count evidence |

**Nothing on this list is approved for implementation during the freeze.**

---

## 7. Recommendation

**WAIT FOR A100.**

Ship no feature. The only item classified as an A100 PRECONDITION (item 5,
presentation-only subset) can be deferred into the A100 kickoff without changing
the baseline — and even it is optional, since `ail doctor`/`ail check` already
provide the raw material. Every other proposal is gated on participant evidence
the current protocol can produce without modification, so there is no reason to
spend freeze budget on unverified additions.
