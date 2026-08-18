# AILang v1.1.20 — Final Publication Matrix

**Release Date:** 2026-08-18
**Release Commit:** `170904b` (main)
**Release Tag:** v1.1.20
**GitHub Commit:** https://github.com/akpersonal4/ailang-lang-AILang/commit/170904b
**GitHub Release:** https://github.com/akpersonal4/ailang-lang-AILang/releases/tag/v1.1.20
**PyPI Version:** 1.1.20
**PyPI URL:** https://pypi.org/project/ailang-lang/1.1.20/

---

## Release Context

PyPI v1.1.19 was published from commit `837e05c` (pre-trampoline) before the ADR-017 trampoline was merged. This release corrects that: v1.1.20 contains the full trampoline implementation and is the authoritative release.

**PyPI v1.1.19 status:** Should be yanked via PyPI web interface (API yank not available from current environment).

---

## Artifact Hashes (SHA256)

| Artifact | Local Build | PyPI | GitHub | Match |
|----------|------------|------|--------|-------|
| Wheel | `F4B0614EA9897FD31783E11F54D8F3B92FFFF7E2FCED89FB5005E52F424E2B53` | `F4B0614EA9897FD31783E11F54D8F3B92FFFF7E2FCED89FB5005E52F424E2B53` | `F4B0614EA9897FD31783E11F54D8F3B92FFFF7E2FCED89FB5005E52F424E2B53` | ✅ ALL MATCH |
| sdist | `5A6FE4D6D00984DECBC3FEDADCA03A533425FF4C72EE1F3636255B9B9EA2F583` | `5A6FE4D6D00984DECBC3FEDADCA03A533425FF4C72EE1F3636255B9B9EA2F583` | `5A6FE4D6D00984DECBC3FEDADCA03A533425FF4C72EE1F3636255B9B9EA2F583` | ✅ ALL MATCH |

---

## RC Gate Results (14/14 PASS)

| # | Gate | Result | Evidence |
|:-:|------|--------|----------|
| 1 | Regression (pytest) | ✅ PASS | 768 passed, 1 pre-existing, 0 new |
| 2 | Trampoline depth 10k | ✅ PASS | exit 0, 328ms |
| 3 | Determinism (5 runs) | ✅ PASS | 12502500 across all 5, byte-identical |
| 4 | Canonical 10k performance | ✅ PASS | avg 283ms (target <5000ms) |
| 5 | max_recursion | ✅ PASS | RuntimeError with proper message |
| 6 | Stack traces | ✅ PASS | Operation/Reason/Location/Suggestion format |
| 7 | Static quality (Ruff) | ✅ PASS | 0 new errors (121 pre-existing) |
| 8 | Language surface | ✅ PASS | No new keywords in parser/lexer |
| 9 | CLI matrix | ✅ PASS | version/check/fmt/build/doctor all pass |
| 10 | Clean wheel install | ✅ PASS | v1.1.20 installed, trampoline works |
| 11 | Git hygiene | ✅ PASS | No secrets, clean staging |
| 12 | Version consistency | ✅ PASS | pyproject.toml=1.1.20, _version.py=1.1.20 |
| 13 | Build audit | ✅ PASS | twine check PASSED, 183 files |
| 14 | SHA256 identity | ✅ PASS | Local=PyPI=GitHub (all 6 hashes match) |

---

## Trampoline Performance Evidence

### Depth Scaling (from wheel install)

| Depth | Time (ms) |
|------:|----------:|
| 10k | 328 |

### Determinism

| Run | sum_acc(5000,0) |
|----:|----------------:|
| 1 | 12502500 |
| 2 | 12502500 |
| 3 | 12502500 |
| 4 | 12502500 |
| 5 | 12502500 |

---

## Fresh PyPI Install Verification

| Check | Result |
|-------|--------|
| `pip install ailang-lang==1.1.20` | ✅ PASS |
| `ail version` | ✅ AILang v1.1.20 |
| Trampoline 10k | ✅ exit 0 |
| Determinism (sum_acc) | ✅ 12502500 |

---

## Trampoline Symbol Verification

| Symbol | Local Build | PyPI Wheel |
|--------|------------|------------|
| `_TailCallSentinel` | PRESENT | PRESENT |
| `_trampoline_depth` | PRESENT | PRESENT |
| `_inline_tail_chain` | PRESENT | PRESENT |
| `_TrampolinePendingBinary` | PRESENT | PRESENT |

---

## Known Pre-existing Issues

1. `test_internal_builtin_name_does_not_hijack_stdlib` — scope cache behavior
2. `test_benchmark_bundled_app_runs_end_to_end` — stdlib `__test_expect` undefined
3. Ruff 121 errors / Mypy 101 errors — all pre-existing

---

## Governance Artifacts

- **ADR-017**: APPROVED — `docs/adr/ADR-017-gate-f-iteration-execution-model.md`
- **Publication matrix**: `docs/releases/PUBLICATION_MATRIX_v1_1_19.md`

---

## Mismatch Recovery Record

| Version | Commit | Trampoline | Status |
|---------|--------|-----------|--------|
| v1.1.19 (PyPI) | `837e05c` | NO | Should be yanked |
| v1.1.19 (GitHub) | `8d9a30e` | YES | Historical |
| v1.1.20 (PyPI) | `170904b` | YES | **AUTHORITATIVE** |
| v1.1.20 (GitHub) | `170904b` | YES | **AUTHORITATIVE** |

---

**Release Authorization:** RC gates passed 14/14. SHA256 identity verified (local/PyPI/GitHub).

**Final Status:** ✅ COMPLETE — v1.1.20 is the authoritative trampoline release.
