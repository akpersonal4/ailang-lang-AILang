# PERF_SCALING_PRE_ITERATION — Bounded Phase-0 Performance Pre-Measurement

> **Date of measurement:** 2026-08-14
> **Purpose:** Inform the **Gate F** iteration-model decision (`AILANG_STRATEGIC_ENGINEERING_PLAN_V2.md`
> §1.3, §7) BEFORE any trampoline/loop work, by measuring what is runnable at 100→10k **today**.
> **Status:** Phase-0 deliverable (V2 §14 PHASE 0). Evidence, not a release; no code changed here.
>
> Field classification symbols: **MEASURED** (measured this session) · **NOT MEASURED** (requires
> evidence) · **HISTORICAL — SOURCE:** `<doc>` (from an earlier report).

---

## 1. Environment & Method (baseline discipline)

| Field | Value |
|-------|-------|
| **Substrate** | **WORKING TREE** (source checkout) at HEAD `837e05c` (tag `v1.1.19`) **plus uncommitted Phase-0 P0-1/P0-2 edits** — this is **NOT the published PyPI wheel**. |
| **Python** | CPython 3.11.15 (AMD64) |
| **OS** | Windows 10/11 build 26200, x86_64 |
| **Method** | In-process, **compile excluded for runtime**: each program compiled once; only `Runtime.execute` timed (same convention as `M137_RELEASE_AND_PERFORMANCE_INVESTIGATION.md`). |
| **Repetitions** | min-of-3 per data point (not a statistical study). |
| **Sandbox** | Disabled policy for measurement (matches direct-`Runtime.execute` methodology). |
| **Driver** | `benchmarks/perf_scaling_pre_iteration.py` (committed alongside this doc). |
| **Exact command** | `python benchmarks/perf_scaling_pre_iteration.py` (from repo root). |

**Caveat the reader must see:** these numbers are a **bounded pre-measurement**, not the canonical
10k business-workload benchmark (that is Phase 2 and can only run after the recursion model is
resolved — see §5). They isolate *compiler throughput*, *native-stdlib throughput*, and *pure
recursion call/name-resolution cost*, and they deliberately do **not** measure the full per-record
app workload.

---

## 2. A — Compile Scaling (records of data in source)

Workload: `N` top-level `let v_i = i;` bindings + `fn main(){ return v_{N-1} }`. Measures
lexer → parser → semantic analysis → type check → IR build. **No runtime.** min-of-3 ms.

| N | ms | LOC/s |
|-----|------|--------|
| 100 | 40.1 | 2,495 |
| 200 | 47.6 | 4,204 |
| 400 | 48.4 | 8,271 |
| 800 | 73.7 | 10,860 |
| 1,000 | 92.5 | 10,812 |
| 2,000 | 148.6 | 13,457 |
| 5,000 | 432.3 | 11,566 |
| **10,000** | **702.7** | **14,231** |

**Scaling (MEASURED):** 100→10,000 records is a **100×** data increase for **~17.5×** time
(40.1→702.7 ms). Sub-linear at the top end; the ~40 ms floor at small `N` is fixed compiler /
import startup. Throughput stabilizes at **~11–14k LOC/s** (≈0.7 s to compile a 10,000-record
source). No super-linear blow-up observed at or below 10k.

**Interpretation:** **Compiler throughput is NOT a binding constraint for a 10k-record workload.**
A full 10k-record app would compile in well under a second.

---

## 3. B — Native-Stdlib Runtime Scaling (no AILang recursion)

Workload: CSV string of `N` rows; `csv.parse` → `list.len` → `csv.stringify`, all **native
stdlib** (no AILang recursion), so it runs at 10k today despite the recursion ceiling.
**Compile excluded**; min-of-3 ms.

| N | ms |
|-----|------|
| 100 | 0.1 |
| 200 | 0.2 |
| 400 | 0.2 |
| 800 | 0.5 |
| 1,000 | 0.4 |
| 2,000 | 0.9 |
| 5,000 | 2.6 |
| **10,000** | **10.8** |

**Scaling (MEASURED):** roughly **linear** (small-`N` flooring noise); 10,000 rows load + re-serialize
in **~11 ms**.

**Interpretation:** **Native stdlib is NOT the bottleneck.** I/O and collection primitives handle
10k records in single-digit-to-low-tens of milliseconds. The earlier independent-evaluation figure
of ~2.4 s for a 1000-record *full app* (HISTORICAL — SOURCE: `AILANG_STRATEGIC_PLAN_AUDIT_V1_1_19.md`)
is dominated by **per-row pure-AILang recursion / map / string work**, not by these native paths.

---

## 4. C — Pure-Recursion Depth / Name-Resolution Probe

Workload: `dec(n) = if (n<=0) 0 else dec(n-1)+1`; run at depth `d` via `main(){ return dec(d) }`.
Isolates per-call **function-call + name-resolution + arithmetic** cost in a pure-AILang loop.
**Compile excluded**; min-of-3 ms.

| depth | ms | status |
|-------|------|--------|
| 100 | 0.84 | OK |
| 200 | 1.60 | OK |
| 400 | 3.33 | OK |
| 800 | 7.19 | OK |
| 1,000 | 10.45 | OK |
| 1,500 | 15.14 | OK |
| 1,999 | — | **FAIL — recursion ceiling** |
| 2,000 | — | **FAIL — recursion ceiling** |
| 3,000 | — | **FAIL — recursion ceiling** |

**Scaling (MEASURED):** 100→1,500 is a 15× depth increase for ~18× time → **linear (O(n))**. This
empirically confirms the **P1b `_frame_ever_bound` fix (shipped in v1.1.19)** removed the O(n²)
name-resolution behavior: recursion scales linearly up to the ceiling, with a per-call cost of
**~8–10 µs** for this minimal body.

**Ceiling (MEASURED):** the **effective maximum user-recursion depth is ≈ 1,999** (the `main` frame
counts against `sandbox.max_recursion = 2000`). A pure-AILang per-record recursive workload is
therefore **limited to ~1,999 records today**, independent of its per-record cost.

**Interpretation:** the recursion *ceiling* (not per-call speed) is the **binding constraint** for the
§5B 10k canonical workload, exactly as V2 §1.3/§1.4 predicted. Linear scaling means the O(n²) problem
is solved; the remaining problem is **removing the host-stack depth cap** (a Phase 2 / Gate F concern)
and confirming per-record cost at a canonical workload mix (Phase 2).

---

## 5. Implications for Gate F (iteration model)

| Gate F option | Pre-measurement signal |
|---|---|
| A — keep recursion (status quo) | **Fails 10k §5B**: ceiling ~1,999 ⇒ canonical 10k workload cannot even run. |
| B — native loops (new surface) | Not needed for *depth*; would solve ceiling but adds language surface. |
| C — IR loop node (no per-record call) | Would remove per-record call cost AND depth if lowered iteratively; architecture-only. |
| D — bytecode VM | **No evidence for it yet**: native + compiler paths are fast; dispatch overhead at scale is **NOT MEASURED** (needs profiler, Phase 2). A VM cannot lift the recursion ceiling on its own. |
| **E — trampoline / explicit stack (V2 preferred)** | **Supported**: depth is the only blocker; explicit-stack execution removes the host-stack cap while preserving the recursion surface (ADR-001/002). |

**Bottom line:** the bounded pre-measurement is consistent with the V2 hypothesis that **no VM is
required yet**, and that the smallest change that unblocks the 10k target is an **execution-model**
change (option E / C), **not** a language-surface change and **not** a VM. The per-call cost at 10k
for a canonical workload remains **NOT MEASURED** and must be measured in Phase 2 before any
escalation trigger (V2 §1.6).

---

## 6. Performance Ledger (this session)

| Workload | N | Time | Scaling | Profile evidence | Current limit | Target | Status |
|---|---|---|---|---|---|---|---|
| Compile (data records) | 10,000 | 702.7 ms | ~linear / sub-linear | min-of-3 in-process | none observed ≤10k | compile <5s @10k (V2 §5B) | ✅ PASS |
| Native stdlib (CSV load+stringify) | 10,000 | 10.8 ms | linear | min-of-3 in-process | none observed ≤10k | — | ✅ PASS |
| Pure recursion (call+resolve) | 1,500 | 15.14 ms | **O(n) linear** | min-of-3 in-process | ceiling ≈1,999 | run 10k depth | ❌ BLOCKED (ceiling) |

---

## 7. Known Limitations of This Measurement

- **NOT MEASURED:** pure-AILang recursion at 10k (impossible — ceiling); canonical business workload
  (expense-tracker-style per-row map/string) at 10k; memory at 10k; **dispatch-overhead profile**
  (needs a profiler; V2 §7/Phase 2); Python reference for these exact workloads (compare
  `docs/benchmarks/INVENTORY_PYTHON_COMPARISON.md` instead); determinism re-check at 10k.
- **Single machine**, min-of-3, no statistical error bars; results are indicative, not a guarantee.
- Measured on the **working tree**, not the published wheel — do not compare directly to PyPI
  numbers without relabeling.
- The recursion probe's per-call cost (**~8–10 µs**) is a *floor*; a real per-row workload (map.get,
  string ops) has a larger constant, so do not extrapolate the probe to full-app time.

---

## 8. Reproducibility

```bash
# from repo root (system python 3.11.15 puts the working-tree `compiler` first),
# or force the tree with `python -m benchmarks.perf_scaling_pre_iteration`:
python benchmarks/perf_scaling_pre_iteration.py
```

Driver: `benchmarks/perf_scaling_pre_iteration.py` (regenerates all workloads into a temp dir,
prints sections A/B/C). Workload generators are pinned there for reproducibility. The driver forces
the repo root onto `sys.path` so it always measures the working-tree compiler, never the installed
AILang package.

---

## 9. Related Documents

- `docs/roadmap/AILANG_STRATEGIC_ENGINEERING_PLAN_V2.md` (§1.3 bounded pre-measurement, §7 protocol, §14 Phase 0)
- `docs/roadmap/AILANG_STRATEGIC_PLAN_AUDIT_V1_1_19.md` (independent-evaluation figures quoted as HISTORICAL)
- `M137_RELEASE_AND_PERFORMANCE_INVESTIGATION.md` (O(n²) → linear attribution; in-process method)
- `docs/adr/ADR-016-frame-ever-bound.md` (P1b)
- `docs/benchmarks/INVENTORY_PYTHON_COMPARISON.md` (Python reference for inventory workloads)

