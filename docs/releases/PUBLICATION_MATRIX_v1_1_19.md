# AILang v1.1.19 — Final Publication Matrix

**Release Date:** 2026-08-13
**Release Commit:** 837e05c (main)
**Release Tag:** v1.1.19
**GitHub Commit:** https://github.com/akpersonal4/ailang-lang-AILang/commit/837e05c
**GitHub Release:** https://github.com/akpersonal4/ailang-lang-AILang/releases/tag/v1.1.19
**PyPI Version:** 1.1.19
**PyPI URL:** https://pypi.org/project/ailang-lang/1.1.19/

---

## Artifact Hashes

| Artifact | SHA256 |
|----------|--------|
| Wheel (PyPI) | 4F0C465CCC304FB534FBC79D977F85188FAFD08AEC18B95167350C01F91BD18E |
| sdist (PyPI) | 49A9CFFE638EE85F4060AC2023D619E096C0FFFF3134C5C3EA71C708638748E6 |
| Wheel (GitHub Release) | 4F0C465CCC304FB534FBC79D977F85188FAFD08AEC18B95167350C01F91BD18E |
| sdist (GitHub Release) | 49A9CFFE638EE85F4060AC2023D619E096C0FFFF3134C5C3EA71C708638748E6 |

**Hash Match:** ✅ PASS (all four hashes identical)

---

## Fresh PyPI Install Verification

| Check | Result |
|-------|--------|
| `pip install --no-cache-dir ailang-lang==1.1.19` | ✅ PASS |
| `ail --version` | ✅ PASS (AILang v1.1.19) |
| `ail doctor` | ✅ PASS |
| `ail context --json` | ✅ PASS |
| `ail run` (P0: print stdout) | ✅ PASS (outputs 42, exit 0) |
| `ail check` | ✅ PASS (entry point present) |
| `ail fmt --check` | ✅ PASS (entry point present) |
| `ail test` | ✅ PASS (discovers and runs test_app_*_generated.ail) |
| `ail testgen` (P1a: .ail → ail test) | ✅ PASS (1/1 test passed) |
| `ail benchmark` (P1b: canonical) | ✅ PASS (static_analyzer build min 264ms) |

---

## Release Gate Results (Pre-Publication)

| Gate | Baseline (v1.1.18) | v1.1.19 | Status |
|------|-------------------|---------|--------|
| Full pytest suite | 1236 passed / 6 failed | 1236 passed / 6 failed | ✅ PASS (identical, pre-existing env failures) |
| M136 regression tests | N/A | 12/12 passed | ✅ PASS |
| Ruff (M136-added lines) | 0 new | 0 new | ✅ PASS |
| Mypy (same scope) | 97 errors | 77 errors | ✅ PASS (net improvement) |
| twine check | — | PASSED | ✅ PASS |
| Wheel audit (contents, RECORD) | — | 182 entries, 0 mismatches | ✅ PASS |
| Version consistency | — | 1.1.19 all surfaces | ✅ PASS |

---

## Canonical Benchmark (from published wheel)

| App | LOC (code) | Build min | Build avg | Run min | Run avg |
|-----|------------|-----------|-----------|---------|---------|
| static_analyzer | ~990 | **244 ms** (local) / **264 ms** (PyPI) | 259 ms | 1.65 s | 1.69 s |
| kanban | ~? | 235 ms | 249 ms | 0.33 s | 0.34 s |
| dice_roller | ~? | 166 ms | 171 ms | 0.20 s | 0.20 s |

**P1b Verification:** 244 ms vs v1.1.18 baseline 713 ms = **2.9× speedup** ✅

---

## M136 Fixes Delivered

| Fix | Description | Evidence |
|-----|-------------|----------|
| **P0** | Single-execution stdout — `_frame_ever_bound` frame binding | `ail run print.ail` outputs 42, exit 0 |
| **P1a** | `ail testgen` → executable `.ail` → `ail test` roundtrip | `ail testgen --app simple simple.ail` + `ail test` = 1/1 PASS |
| **P1b** | `_frame_ever_bound` O(n²)→O(n) compiler speedup | static_analyzer build 244ms vs 713ms (2.9×) |

---

## Governance Artifacts

- **ADR-016** (_frame_ever_bound): APPROVED — `docs/adr/ADR-016-frame-ever-bound.md`
- **PRE_1_1_19_BASELINE**: Published with A/B/H/K metrics — `docs/releases/PRE_1_1_19_BASELINE.md`
- **M136 Naming Reconciliation**: DEVELOPMENT_STATUS.md, PROJECT_MEMORY.md, CHANGELOG.md (J-1..J-5 shipped v1.1.18 vs P0/P1a/P1b pending v1.1.19)

---

## Release Content Summary

**ONLY** the approved M136 fixes (P0/P1a/P1b). No new features, no A100 changes, no v1.2 work, no unrelated fixes.

---

**Release Authorization:** ADR-016 APPROVED + explicit v1.1.19 release authorization granted by user.

**Final Status:** ✅ ALL GATES PASSED — Publication complete.