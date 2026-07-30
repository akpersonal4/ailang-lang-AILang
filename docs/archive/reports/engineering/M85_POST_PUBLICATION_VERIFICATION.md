# M85 — Post-Publication Verification Report

**Date:** 2026-07-22
**Version:** v1.1.2

---

## 1. Environment Setup

- **Method:** Created a brand-new virtual environment (`post_pub_verify`) completely separate from the source tree and any previous local builds.
- **Python Version:** 3.11.15

## 2. Verification Steps & Results

### Step 1: `pip install ailang-lang==1.1.2`

**Command:**
```bash
post_pub_verify\Scripts\pip.exe install ailang-lang==1.1.2
```

**Observation:** Package successfully downloaded from PyPI and installed.
**Result:** ✅ PASS

### Step 2: `ail version`

**Command:**
```bash
post_pub_verify\Scripts\python.exe -m compiler.cli.main version
```

**Output:** `AILang v1.1.2`
**Result:** ✅ PASS

### Step 3: `ail new hello`

**Command:**
```bash
post_pub_verify\Scripts\python.exe -m compiler.cli.main new hello
```

**Observation:** Project scaffold created correctly in `C:\Temp\ail_post_pub_verify\hello`.
**Result:** ✅ PASS

### Step 4: `ail run main.ail`

**Command:**
```bash
cd hello
..\post_pub_verify\Scripts\python.exe -m compiler.cli.main run main.ail
```

**Output:** `Hello, AILang!`
**Result:** ✅ PASS

## 3. Summary

| Step | Test | Status |
|------|------|--------|
| 1 | PyPI Installation | ✅ PASS |
| 2 | Version Reporting | ✅ PASS |
| 3 | Project Creation | ✅ PASS |
| 4 | Execution | ✅ PASS |

**Conclusion:** The public release of AILang v1.1.2 on PyPI is fully functional and behaves identically to the verified release candidate. The standard library resolution fix (P0) and version synchronization (P1) are confirmed active in the public distribution.
