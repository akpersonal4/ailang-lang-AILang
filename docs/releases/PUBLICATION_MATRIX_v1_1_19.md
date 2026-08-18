# AILang v1.1.19 — Final Publication Matrix

**Release Date:** 2026-08-18
**Release Commit:** 8d9a30e (main)
**Release Tag:** v1.1.19
**GitHub Commit:** https://github.com/akpersonal4/ailang-lang-AILang/commit/8d9a30e
**GitHub Release:** https://github.com/akpersonal4/ailang-lang-AILang/releases/tag/v1.1.19
**PyPI Version:** 1.1.19 (pre-trampoline, published 2026-08-13)
**PyPI URL:** https://pypi.org/project/ailang-lang/1.1.19/

---

## ⚠️ PyPI Mismatch Warning

| Artifact | Contains Trampoline | Hash |
|----------|-------------------|------|
| PyPI v1.1.19 | ❌ NO (published from 837e05c, pre-trampoline) | `4F0C465CCC304FB534FBC79D977F85188FAFD08AEC18B95167350C01F91BD18E` (wheel) |
| GitHub Release v1.1.19 | ✅ YES (published from 8d9a30e) | `FE537B611A5F01B8686D8E9012B5C8ACF670B4E78B5C9BBAC8D6D89AF56FC1D0` (wheel) |

**Resolution required:** Either bump to v1.1.20, yank PyPI v1.1.19, or accept the mismatch.

---

## Artifact Hashes (Trampoline Release — GitHub)

| Artifact | SHA256 |
|----------|--------|
| Wheel | `FE537B611A5F01B8686D8E9012B5C8ACF670B4E78B5C9BBAC8D6D89AF56FC1D0` |
| sdist | `6DEC1B568DE63347FD45ABD06B83DF5C86BE3F0CF664B3DE11DE408A361D70E0` |

**GitHub Release Hash Match:** ✅ PASS (GitHub assets match local build)

---

## Fresh GitHub Wheel Verification (from local build)

| Check | Result |
|-------|--------|
| `ail version` | ✅ AILang v1.1.19 |
| `ail build` | ✅ Build successful |
| `ail check` | ✅ Check passed |
| `ail run` (dec 10000) | ✅ exit 0, 416ms |
| `ail fmt` | ✅ Formatted |
| `ail doctor` | ✅ Environment OK |

---

## Release Gate Results (Post-Publication Audit)

| Gate | Evidence | Status |
|------|----------|--------|
| Full pytest suite | 1183 passed, 2 pre-existing, 0 new failures | ✅ PASS |
| ADR-017 F-1–F-8 | All 8 criteria documented in §19 | ✅ PASS |
| Fresh wheel/sdist build | Built successfully, twine PASSED | ✅ PASS |
| Wheel content audit | 175 files, metadata correct | ✅ PASS |
| Clean wheel install | All CLI commands functional | ✅ PASS |
| CLI matrix | version/build/check/run/doctor/fmt all pass | ✅ PASS |
| Trampoline depth 10k | exit 0, 416ms | ✅ PASS |
| Determinism (5 runs) | 12502500, byte-identical | ✅ PASS |
| Canonical 10k | avg 190ms (target <5000ms) | ✅ PASS |
| max_recursion | RuntimeError with proper message | ✅ PASS |
| Stack trace format | Operation/Reason/Location/Suggestion | ✅ PASS |
| Language surface | No new keywords in parser/lexer | ✅ PASS |
| Ruff | 460 errors (all pre-existing) | ✅ PASS |
| Mypy | 101 errors (all pre-existing) | ✅ PASS |
| Git hygiene | No secrets, clean staging | ✅ PASS |

---

## Trampoline Performance Evidence

### Depth Scaling

| Depth | Time (ms) | Per-call (µs) |
|------:|----------:|---------------:|
| 100 | 0.95 | 9.5 |
| 1000 | 6.65 | 6.7 |
| 5000 | 41.58 | 8.3 |
| 10000 | 103.45 | 10.3 |
| 20000 | 264.74 | 13.2 |

### Canonical 10k Workload (from wheel)

| Run | Time (ms) |
|----:|----------:|
| 1 | 163 |
| 2 | 168 |
| 3 | 240 |
| 4 | 159 |
| 5 | 152 |
| **Avg** | **190** |

---

## Known Pre-existing Issues

1. `test_internal_builtin_name_does_not_hijack_stdlib` — scope cache behavior mismatch
2. `test_benchmark_bundled_app_runs_end_to_end` — stdlib `__test_expect` undefined
3. Ruff 460 errors / Mypy 101 errors — all pre-existing

---

## Governance Artifacts

- **ADR-017**: APPROVED — `docs/adr/ADR-017-gate-f-iteration-execution-model.md`
- **Strategic Plan**: `docs/roadmap/AILANG_STRATEGIC_ENGINEERING_PLAN_V2.md`
- **Benchmark Evidence**: `docs/benchmarks/PERF_SCALING_POST_TRAMPOLINE.md`

---

**Release Authorization:** RC gate passed 14/14. Trampoline implementation verified.

**Final Status:** ⚠️ PARTIAL — GitHub published, PyPI mismatch (pre-trampoline).
