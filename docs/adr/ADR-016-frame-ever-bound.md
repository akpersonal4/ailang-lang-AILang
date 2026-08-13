# ADR-016: `_frame_ever_bound` Name-Resolution Optimization

## Status
**DRAFT — PENDING CTO / decision-holder approval.**

This ADR is a decision record, **not** an approval. No implementation was
authorized by this document; the referenced fix exists as uncommitted working-tree
changes and remains pending a separate, explicit release decision.

## Context

### Measured bottleneck
`compiler/runtime/interpreter.py` resolves names through `Environment.resolve`,
which walks the parent-environment (frame) chain recursively. In recursive business
workloads (ledger-style row helpers calling `convert.to_string`, `string.uppercase`,
and so on), every call to a per-row helper that references module-level names walks
the full call-depth chain — raising `NameError` at the end before falling through to
the global/module lookup.

M137 profiling (2026-08-13, published wheel) showed:
- `Environment.resolve` consumes **≈74–80% of runtime** on the recursive driver and
  the full Expense Tracker workload (74% / 80% respectively; 208,607 calls @n=200
  driver, 4,784,466 calls @n=400 Expense Tracker).
- Published-wheel timing scaled **quadratically**: n=100 → 17.8 ms, 200 → 75.8,
  400 → 376.3, 800 → 1687.5 ms (ratios ≈4.0–5.0 per doubling).
- CSV parsing and `list.contains` itself scale linearly and are cheap — the
  evaluator's attribution of the O(n²) behavior to `list.contains` is incorrect;
  recursion-driven frame-chain name resolution is the root cause.

### Where the fix lives
The fix (`_frame_ever_bound` monotonic set on the `Runtime`) is present in the
working tree only — `compiler/runtime/interpreter.py` — and is **not** in any
published release (latest published is v1.1.18; the v1.1.18 wheel predates it).
M136's own "wheel-verified" claims for P1b were validated against a locally-built
wheel from the fixed tree, not the PyPI artifact.

## Evidence

### Baseline (published wheel, M137 re-verified)
| n | Elapsed (ms) | Ratio vs previous |
|---|-------------|-------------------|
| 100 | 17.8 | — |
| 200 | 75.8 | 4.26 (quadratic) |
| 400 | 376.3 | 4.96 (quadratic) |
| 800 | 1687.5 | 4.48 (quadratic) |

### Fixed scaling (working tree, `_rc_verify/RC_VERIFICATION_REPORT.md` 2026-08-12)
| n | Elapsed (ms) | Ratio vs previous |
|---|-------------|-------------------|
| 100 | 3.26 | — |
| 200 | 6.34 | 1.94 (linear) |
| 400 | 13.21 | 2.08 (linear) |
| 800 | 25.24 | 1.91 (linear) |

Wheel rebuild from the fixed tree: 2.93 / 5.12 / 10.21 / 20.58 ms (ratios
1.75 / 1.99 / 2.02 — linear). **~22× speedup at n=400** vs baseline.

## Mechanism

A monotonic set, `_frame_ever_bound: set[str]`, is maintained on the `Runtime`:

- It is **added to** (never removed from) whenever a name is bound in any frame
  via `_call_function` (parameter binding), `_define_local`, or `_assign_local`.
- In `_resolve_name`, when a name is **not** in `_frame_ever_bound`, the frame-chain
  walk is skipped entirely (it is guaranteed to raise `NameError`), and resolution
  proceeds directly to the global / builtin / module lookup.
- Names that **are** (or have been) frame-bound still walk the chain exactly as
  before, preserving existing resolution semantics.

Safe by construction: names are only ever added, never removed; a name that *was*
frame-bound but whose frame has since popped merely causes a wasted walk, never an
incorrect result.

## Safety / Semantics

- **Dynamic scoping preserved:** `_assign_local` can create bindings in the frame
  chain, so assigned names are tracked and still walk the chain — the fast path only
  applies to names that provably cannot resolve via any frame.
- **Not a language-semantic change:** no syntax, grammar, scoping rules, or runtime
  behavior contract changes. The change is purely an internal resolution fast path.
- **No value-caching correctness risk** (unlike the positive-only cache in ADR-006,
  which stores binding locations; this set stores only names).

## Verification

- **Regression tests:** `tests/test_m136_fixes.py::TestNameResolutionOptimization`
  (4 tests: correctness small/large, never-bound-name invariant, scaling ratio
  < 3.0) — PASSED.
- **Full suite:** 1242 passed / 0 failed (working tree, RC verification 2026-08-12),
  0 new failures; suite ~2.1× faster, consistent with the fix.
- **Performance:** linear scaling reproduced on the fixed tree and from a fresh
  wheel-only install (RC verification §C, §D).
- **Determinism:** 10/10 runs byte-identical output (RC verification §G).

## Governance — freeze unfreeze justification

`PRODUCT_ROADMAP.md` (Frozen Components) lists the **Runtime interpreter** as
frozen with the unfreeze condition:

> Evidence of new bottleneck

M137 supplies exactly that evidence: a confirmed O(n²) name-resolution bottleneck
attributing 74–80% of runtime to `Environment.resolve`, with the project's own
established measurement methodology (ADR-007 evidence-first). This ADR records that
the bottleneck evidence exists and is sufficient to satisfy the runtime's unfreeze
condition for the narrow purpose of shipping the already-written fix — it does **not**
open the freeze for general runtime work.

## Decision

**ACCEPTED IN PRINCIPLE / PENDING GOVERNANCE APPROVAL** (DRAFT — PENDING
CTO/decision-holder approval).

Subject to approval, the fix should ship as part of a future release whose package is
verified from the published artifact (per the Pre-Publication Governance & Evidence
task), with before/after baselines recorded.

## Alternatives considered

### Alternative 1: Do nothing (status quo)
Rejected: keeps the published artifact quadratic on recursive business workloads —
the largest single credibility gap identified by independent evaluation.

### Alternative 2: Negative-cache module names
Adding NameError sentinels to the resolve cache. Rejected previously under ADR-006
(assign can create bindings, stale negative entries); the monotonic-set approach
avoids invalidation entirely.

### Alternative 3: Architectural rewrite (bytecode VM / native backend)
Disproportionate: the fix is ~50 LOC with zero semantic change and restores linear
scaling. Architecture gates (Strategic Engineering Plan §13 Gates B–E) require
measured failure of the shipped interpreter before any rewrite — not yet shown.

## Consequences

- Shipped interpreters become linear on recursive business patterns instead of
  quadratic.
- The runtime's positive-only resolve cache (ADR-006) is unaffected.
- Requires a release whose wheel is independently verified from PyPI (not a
  locally-built wheel) before claims of the fix being "shipped" are made.
- No backward-compatibility impact; observable language behavior unchanged.
