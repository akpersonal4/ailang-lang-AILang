# PRE-1.1.19 BASELINE — Published v1.1.18 Evidence

> **Purpose:** Record the published-artifact baseline for v1.1.18, reconcile
> historical test counts and M136 naming, and separate fresh published-artifact
> measurements from historical/source-tree evidence. Governance + measurement
> only — **no release action performed or authorized.**

---

## 1. Environment

| Item | Value |
|---|---|
| Host OS | Windows (win32) |
| Python | CPython 3.11.15 |
| pytest | 9.1.1 |
| Date | 2026-08-13 |
| Repo HEAD | `7d4e315` (branch: main, 0 ahead / 0 behind origin/main) |
| Working tree | Contains unshipped M136 P0/P1a/P1b fixes (NOT in any published artifact) |

## 2. PyPI version

Installed: **`ailang-lang==1.1.18`** (latest published on PyPI; GitHub release
`v1.1.18`, 2026-08-11).

## 3. Installation method

Fresh virtual environment in a neutral temp directory
(`%TEMP%\opencode\ailang118\venv`):

```
python -m venv <tmp>\ailang118\venv
<venv>\python -m pip install --no-cache-dir --force-reinstall ailang-lang==1.1.18
```

Result: `Successfully installed ailang-lang-1.1.18 watchdog-6.0.0`.

`ail --version` → `AILang v1.1.18`.

## 4. Import-path verification (published-artifact isolation)

- `PYTHONPATH` empty/unset for every measurement below.
- Neutral CWD for every measurement (never the repository root).
- `python -c "import compiler; print(compiler.__file__)"` →
  `<venv>\Lib\site-packages\compiler\__init__.py` — resolves **exclusively from
  site-packages**, not the source checkout.
- `ail_platform` → `<venv>\Lib\site-packages\ail_platform\__init__.py`.
- No editable install; no repo path on `sys.path` (verified via printed path).

**Published wheel contents** (relevant to measurement feasibility):

- Bundled canonical apps (5): dice_roller (73 LOC), hangman_game (116),
  inventory_mgmt (1099), kanban (1130), static_analyzer (855) — under
  `<venv>\Lib\site-packages\ail_platform\data\apps\`.
- Stdlib: 18 modules (`stdlib\*.ail`).
- **The repository's 8,515-LOC `apps/inventory/` workload is NOT in the wheel.**

---

## 5. B — Runtime performance

Methodology (identical to M137/M136 RC): recursive driver program, per-row
helper resolving module names (`convert.to_string`, `string.uppercase`),
timing `Runtime.execute` only (compile excluded), min of 3 after warmup, using
the **published wheel's** `compiler` package. Workload written fresh in the
neutral dir — not copied from the repository.

| n | Elapsed (ms) | Ratio vs previous |
|---|-------------|-------------------|
| 100 | 36.72 | — |
| 200 | 145.81 | 3.97 |
| 400 | 717.86 | 4.92 |
| 800 | 3255.37 | 4.53 |

**Scaling: quadratic** (ratios ≈4× per doubling — consistent with the M137
O(n²) finding for `Environment.resolve`). These are **published-artifact**
numbers, measured fresh in this session.

### Historical source-tree comparison (labeled, NOT published-artifact)

From `_rc_verify/RC_VERIFICATION_REPORT.md` (2026-08-12, working tree with
P1b fix):

| n | Baseline HEAD ms (source tree) | Fixed working-tree ms | Fixed wheel ms |
|---|---|---|---|
| 100 | 15.01 | 3.26 | 2.93 |
| 200 | 64.32 | 6.34 | 5.12 |
| 400 | 291.88 | 13.21 | 10.21 |
| 800 | — | 25.24 | 20.58 |

And M137's published-wheel probe (2026-08-13, wheel only): n=100 → 17.8 ms,
200 → 75.8, 400 → 376.3, 800 → 1687.5 ms. **Absolute values differ across
sessions (machine load / wheel vs source); the quadratic-to-linear contrast and
the ~22× improvement at n=400 are the stable findings.** This session's fresh
published-wheel numbers are the authoritative v1.1.18 baseline for B.

## 6. H — Test execution / testgen

Measured against the **published wheel** in a neutral project (`ail.toml` +
`src/main.ail`, created fresh):

1. `ail testgen src/main.ail` → "Generated: 1 files"; emitted
   `tests/generated/test_app_main_generated.py` (a **pytest `.py`** file) +
   report files. (Published v1.1.18 testgen emits pytest `.py`, not `.ail`.)
2. `ail test` (project root) → **`No tests found`**, exit 1. Supported
   patterns: `test_*.ail`, `*_test.ail`.
3. `ail test tests/generated/test_app_main_generated.py` → **`Error: not an
   .ail file`**.

**Result: 0 of 1 generated file (0%) is executable by `ail test` against the
published artifact.** This is the expected published-v1.1.18 state; the P1a fix
(testgen emits `.ail`) is working-tree-only, not in v1.1.18.

## 7. K — Determinism

Against the **published wheel**, neutral CWD:

- **Byte-identical output:** 10 identical runs of a recursive workload
  (`ail run`), outputs written to files. `runs=10 unique_hashes=1`.
  Run content: `determinism_total=190` / `DONE`. SHA-256 of each run file:
  `DD9187370F249C74E8E638EEB03DB6ABA16861C3CA6CEA548D5D77457282ABD5`.
- **IR determinism:** same program built 3× via the wheel's compiler API;
  serialized module-IR SHA-256 identical across runs:
  `3d695a428e55129c7b473d65730072a72c50f96ce46e06a8c2071f814259e6d7`.

**Result: deterministic — 10/10 byte-identical outputs; 3/3 identical IR
SHA-256.**

## 8. A — Build speed

Measured against the **published wheel**:

- A 990-LOC single-file workload (165 helpers + main, generated fresh in the
  neutral dir — not copied from the repository) via `ail build` (min of 3):
  **713 ms, 717 ms, 740 ms → min 713 ms.**
- **The 8,515-LOC `apps/inventory/` workload is NOT in the wheel.**

**8,515-LOC build: NOT MEASURABLE FROM THE PUBLISHED ARTIFACT** — the workload
source is not shipped in the wheel, and the isolation rule forbids copying it
from the repository. Historical (source-tree, reported in Strategic Plan §4.3):
8,515-LOC inventory full build = **0.219 s**; 5,000 LOC ≈ 1.88 s. Labeled
historical, not published-artifact.

## 9. Measurements impossible against the published artifact

| Measurement | Reason |
|---|---|
| B — 8,515-LOC inventory runtime workload | Workload source not shipped in the wheel |
| H — testgen on the 8,515-LOC workload | Same; H measured instead on a fresh neutral project (0%) |
| A — 8,515-LOC build | Workload source not shipped in the wheel |
| A — canonical 1,000-LOC benchmark (as originally defined) | No 1,000-LOC benchmark file ships in the wheel; measured a fresh 990-LOC workload as the closest published-artifact proxy |

## 10. Historical values (clearly separated)

| Measurement | Value | Source | Date | Nature |
|---|---|---|---|---|
| B runtime n=100..800 | 15.01/64.32/291.88/— ms | RC_VERIFICATION (baseline HEAD) | 2026-08-12 | Source tree |
| B runtime n=100..800 | 17.8/75.8/376.3/1687.5 ms | M137 probe (published wheel) | 2026-08-13 | Published artifact, separate session |
| B runtime n=100..800 (fixed) | 3.26/6.34/13.21/25.24 ms | RC_VERIFICATION (working tree) | 2026-08-12 | Source tree (unshipped fix) |
| B fixed wheel n=100..800 | 2.93/5.12/10.21/20.58 ms | RC_VERIFICATION (local build) | 2026-08-12 | Locally-built wheel, NOT PyPI |
| A 8,515-LOC build | 0.219 s | Strategic Plan §4.3 | 2026-08-13 | Source tree |
| A 5,000 LOC compile | ≈1.88 s | Strategic Plan §4.3 | 2026-08-13 | Source tree |

## 11. Test-count reconciliation

### Canonical command (pinned)

```
python -m pytest -p no:cacheprovider --tb=short -q
```

pytest 9.1.1 / CPython 3.11.15 / repo root, **current working tree** (contains
unshipped M136 P0/P1a/P1b). Fresh run in this session (2026-08-13):

```
6 failed, 1236 passed, 87 warnings in 477.67s (0:07:57)
```

**Canonical current count: 1236 passed / 6 failed (known pre-existing
environment-artifact failures), total collected 1242, 87 warnings.**

The 6 failures are the same documented pre-existing env-artifact failures from
M136_V1_1_18_RC_REPORT §5.2 (`test_mod003_stdlib_resolution` ×4,
`test_vscode_mcp_integration::TestMCPClient::test_manager_lifecycle`,
`test_wheel_tooling::test_benchmark_bundled_app_runs_end_to_end`). They are
environment artifacts of source-tree pytest (temp-dir stdlib import, host-side
tools), not release-content defects, and are identical across baseline and
current in the RC verification.

### Historical counts

| Count | Source document | Date / revision | Why it differs from current |
|---|---|---|---|
| **1217** | DEVELOPMENT_STATUS.md (v1.1.17, M135), PROJECT_MEMORY, CHANGELOG v1.1.17 | 2026-08-07, released v1.1.17 | Earlier release; before M136's 55 regression tests; different tree |
| **1145 passed / 6 failed** | M136_V1_1_18_RC_REPORT.md §5.1 | 2026-08-11, v1.1.18 RC (J-1..J-5 shipped tree) | Same 6 env failures; fewer total tests than current tree (pre-P0/P1a/P1b, pre-+12 M136 fixes, pre-existing stubs) |
| **1179** | EVALUATION_RERUN_V1_1_13.md (1098 compiler + 81 benchmark) | v1.1.13 era | Older release; fewer tests (benchmarks reported separately) |
| **1128** | DEVELOPMENT_STATUS.md (v1.1.16, M134) | 2026-08-07, v1.1.16 | Older release; before M135 +89 and M136 net additions |
| **1242 passed / 0 failed** | _rc_verify/RC_VERIFICATION_REPORT.md | 2026-08-12, working tree (P0/P1a/P1b) | Same tree as canonical; RC run's env resolved the 6 artifact failures (stdlib/temp-dir present) — canonical run in this session shows the 6 env failures as documented; **total collected 1242 matches** |

**Reconciliation summary:** total collected is the stable comparison basis —
**1242** in the current working tree (1236 passed + 6 known env-artifact
failures here; 1242 passed + 0 failed in the RC run where those artifacts were
resolved). Historical totals are strictly increasing (1128 → 1179 → 1217 →
1151-collected(v1.1.18 with 55 regression tests and removed stubs) → 1242) as
regression tests were added across releases. No historical evidence was
deleted or rewritten.

## 12. M136 naming reconciliation

Two distinct groups share the "M136" name:

- **M136 J-1..J-5 — SHIPPED in v1.1.18** (2026-08-11): `ail rename` cp1252 fix,
  `ail test` auto-executes `test_*`, `ail benchmark` streaming, `list.sum`
  float precision, `list.sum_by_key` precision + clean errors.
- **M136 P0/P1a/P1b — completed/verified, PENDING publication** (working tree
  only): P0 `ail run` single-execution entry + welcome→stderr; P1a `ail
  testgen` emits `.ail`; P1b `_frame_ever_bound` O(n²)→O(n). **NOT present in
  published v1.1.18.**

Updated to say exactly this in: `DEVELOPMENT_STATUS.md` (project status table,
release timeline, milestone table, release history), `PROJECT_MEMORY.md` (M136
entry header note), `CHANGELOG.md` (v1.1.18 header note). Historical records
unchanged — clarifications added alongside.

## 13. Open governance questions

1. **P1b ADR approval** — `docs/adr/ADR-016-frame-ever-bound.md` is DRAFT —
   PENDING CTO / decision-holder approval. Unfreeze justification (bottleneck
   evidence) is documented; approval is a decision, not automatic.
2. **Canonical test count target** — should the canonical number be "1242
   collected" (env-independent) or "1236 passed + 6 env failures" (this host)?
   Recommend publishing the collected total with the pass/fail breakdown.
3. **6 pre-existing env-artifact failures** — reproducible in source-tree
   pytest only; the installed wheel is unaffected (RC verification §D).
   Whether to fix (new tests with fixture-based stdlib) is an engineering
   decision, out of scope here.
4. **Testgen gap (H = 0%)** — the published v1.1.18 testgen emits pytest `.py`
   that `ail test` cannot run. The P1a fix exists in the working tree; its
   release is the separate v1.1.19 publication decision.
5. **Build baseline definition** — the plan's 1,000-LOC / 8,515-LOC build
   metrics cannot be reproduced from the published artifact (source not
   shipped). Recommend either (a) shipping the 8,515-LOC inventory app in the
   wheel, or (b) redefining A to a bundled-app metric.
6. **Release authorization** — v1.1.19 requires: P1b ADR approval → baseline
   recorded → separate explicit release decision. None granted here.

---

**NO RELEASE ACTION PERFORMED.**
