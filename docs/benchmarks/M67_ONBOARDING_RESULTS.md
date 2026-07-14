# M67 — Onboarding Results

**Date:** 2026-07-14
**Status:** PROTOCOL READY — AWAITING EXTERNAL DEVELOPER
**Author:** big-pickle (maintainer)

---

## 1. Executive Summary

This document contains the measurement framework and protocol for validating
whether an external developer can become productive with AILang without maintainer
assistance.

**Critical Finding:** The documentation has 5 critical gaps that would block an
external developer. These must be fixed before recruiting a test subject.

---

## 2. Documentation Readiness Assessment

### 2.1 Blocking Issues

| # | Issue | Severity | Fix Required |
|:-:|-------|:--------:|:------------:|
| 1 | All 8 README doc links are broken | Critical | Yes |
| 2 | STDLIB_REFERENCE missing 21+ functions | Critical | Yes |
| 3 | Examples have zero documentation | High | Yes |
| 4 | QUICKSTART has wrong Python version | High | Yes |
| 5 | No PyPI publication evidence | High | Yes |

### 2.2 Readiness Score

| Category | Score | Weight | Weighted |
|----------|:-----:|:------:|:--------:|
| Documentation completeness | 2/5 | 30% | 0.6 |
| Documentation accuracy | 2/5 | 25% | 0.5 |
| Example quality | 1/5 | 20% | 0.2 |
| Tooling (VS Code, CLI) | 3/5 | 15% | 0.45 |
| Error messages | 3/5 | 10% | 0.3 |
| **Total** | | | **2.05/5** |

**Readiness: 41% — NOT READY FOR EXTERNAL DEVELOPER**

---

## 3. What Works

| Component | Status | Evidence |
|-----------|:------:|----------|
| Compiler builds correctly | ✅ | 790+ tests pass |
| Language is deterministic | ✅ | SHA-256 IR identical across runs |
| Error messages include file:line:col | ✅ | Diagnostic system implemented |
| `ail check` detects forward references | ✅ | M63 validation complete |
| `ail fmt` formats code | ✅ | 82 formatter tests pass |
| VS Code extension works | ✅ | 103 LSP tests pass |
| `ail new` scaffolds projects | ✅ | M56 implementation complete |
| `ail test` discovers and runs tests | ✅ | Test infrastructure complete |

---

## 4. What Doesn't Work (for External Developers)

### 4.1 Documentation Navigation

**Problem:** README.md links to 8 documentation files. All 8 links are broken.

**Impact:** Developer clicks "Getting Started" → 404. Clicks "Language Tour" → 404.
Developer concludes: "This project is abandoned."

**Fix:** Either:
- Move documentation files to match README paths (e.g., `docs/GETTING_STARTED.md`)
- OR update README links to match actual paths (e.g., `docs/reference/GETTING_STARTED.md`)

### 4.2 Standard Library Reference

**Problem:** STDLIB_REFERENCE.md claims `list.copy` and `list.sort` are "Known Missing Operations." Both are fully implemented.

**Impact:** Developer reads reference → writes custom `list.copy` implementation →
discovers it already exists → loses trust in documentation.

**Fix:** Update STDLIB_REFERENCE with all 21+ missing functions.

### 4.3 Installation

**Problem:** QUICKSTART.md says `pip install ailang` and "Python 3.9+".

**Impact:**
- If not on PyPI: `pip install ailang` fails with "no matching distribution"
- If on PyPI but developer has Python 3.9: cryptic errors

**Fix:** Either publish to PyPI or update QUICKSTART with correct installation method.
Update Python version to 3.11+.

### 4.4 Examples

**Problem:** 70+ example files with zero documentation.

**Impact:** Developer opens `examples/banking/main.ail` → reads comment "requires
arrays/maps + file I/O, not yet in AILang" → closes file → concludes language
is incomplete.

**Fix:** Add README to examples/ with:
- Index of all examples
- Difficulty levels
- Which stdlib modules each uses
- How to run each example
- Remove stale comments

---

## 5. Measurement Protocol

### 5.1 Phase 1 — Installation (5 minutes)

**Script:**
```bash
# Start timer
start_time=$(date +%s)

# Install
pip install ailang  # or git clone + pip install -e .

# Verify
ail version

# End timer
end_time=$(date +%s)
elapsed=$((end_time - start_time))
echo "Installation time: ${elapsed} seconds"
```

**Metrics:**
- Time to install (seconds)
- Errors encountered
- Documentation pages visited

### 5.2 Phase 2 — First Hour (60 minutes)

**Tasks:**

| Task | Time Limit | Success Criterion | Metrics |
|------|:----------:|-------------------|---------|
| Install AILang | 5 min | `ail version` works | Time, errors |
| Create project | 5 min | `ail new` succeeds | Time, errors |
| Hello world | 5 min | `ail run` returns 0 | Time, cycles |
| Add package | 10 min | `ail add` succeeds | Time, errors |
| Write tests | 10 min | `ail test` passes | Time, cycles |
| Run tests | 5 min | Tests execute | Time, errors |
| Use for-in | 10 min | Loop compiles | Time, cycles |
| Publish package | 10 min | `ail publish` works | Time, errors |
| VS Code | 5 min | Syntax highlighting | Time, errors |
| Fix error | 5 min | Error message helps | Time, cycles |

**Metrics:**
- Time per task (seconds)
- Correction cycles per task
- Documentation pages visited
- Cognitive load (1-5 self-reported)

### 5.3 Phase 3 — 500 LOC Application (4 hours)

**Application:** Mini Task Manager (see M67_EXTERNAL_ADOPTION.md §5)

**Metrics:**
- First compile success (binary)
- Total correction cycles
- Final LOC
- Developer confidence (1-10)
- Time to completion

### 5.4 Phase 4 — Python Comparison (2 hours)

**Same developer, same AI, same task.**

**Metrics:**
- Onboarding time (minutes)
- Documentation usage (pages)
- Correction cycles
- Perceived difficulty (1-10)
- Completion rate (%)

---

## 6. Scoring Rubric

### 6.1 Per-Task Score

```
task_score = (time_limit / actual_time) * 100
```

- 100 = completed in half the time limit
- 50 = completed in the time limit
- 0 = did not complete

### 6.2 Phase Score

```
phase_score = average(task_scores) * (1 - error_penalty)
error_penalty = min(0.5, errors_encountered * 0.1)
```

### 6.3 Overall Score

```
overall_score = (
    phase1_score * 0.15 +
    phase2_score * 0.25 +
    phase3_score * 0.35 +
    phase4_score * 0.25
)
```

### 6.4 Success Thresholds

| Score | Verdict |
|:-----:|---------|
| >= 80 | Excellent — ready for external adoption |
| 60-79 | Good — needs minor documentation fixes |
| 40-59 | Fair — needs significant documentation work |
| < 40 | Poor — not ready for external adoption |

---

## 7. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|:----------:|:------:|------------|
| Developer cannot install | Medium | Critical | Pre-verify installation |
| Developer cannot find docs | High | High | Fix broken links first |
| Developer hits undocumented feature | High | Medium | Update STDLIB_REFERENCE |
| Developer gives up | Medium | Critical | Ensure smooth onboarding |
| Test takes too long | Medium | Medium | Set clear time limits |

---

## 8. Recommendations

### 8.1 Before Recruiting

| Priority | Task | Effort | Impact |
|:--------:|------|:------:|:------:|
| P0 | Fix broken README doc links | 30 min | Critical |
| P0 | Update STDLIB_REFERENCE | 2 hours | Critical |
| P0 | Fix QUICKSTART Python version | 5 min | High |
| P1 | Add examples README | 1 hour | High |
| P1 | Publish to PyPI | 1 day | High |
| P2 | Update LANGUAGE_SPEC version | 30 min | Medium |
| P2 | Complete CLI reference | 1 hour | Medium |

### 8.2 During Test

- Screen record full session
- Developer uses think-aloud protocol
- Maintainer does not intervene
- Developer cannot read source code

### 8.3 After Test

- Analyze all metrics
- Compare against Python baseline
- Identify remaining documentation gaps
- Update documentation based on findings

---

## 9. Conclusion

The M67 protocol is complete and ready for execution. However, the documentation
has 5 critical gaps that would block an external developer. These must be fixed
before recruiting a test subject.

**Current readiness: 41% — NOT READY FOR EXTERNAL DEVELOPER**

**After fixing gaps: Estimated 85%+ — READY FOR EXTERNAL DEVELOPER**

The test protocol is valid. The measurement framework is complete. The scoring
rubric is defined. The only missing piece is a real external developer.
