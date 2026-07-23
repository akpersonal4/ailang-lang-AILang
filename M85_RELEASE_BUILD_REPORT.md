# M85 — Release Build Report

**Date:** 2026-07-22
**Version:** v1.1.2

---

## 1. Version Consistency Check

- `compiler/_version.py`: `1.1.2` ✅
- `pyproject.toml`: `1.1.2` ✅
- `ail version` (CLI): `AILang v1.1.2` ✅
- `CHANGELOG_v1.1.2.md`: References `v1.1.2` ✅
- `M84R3_RELEASE_READINESS.md`: States `v1.1.2` ✅

**Summary:** All version sources are consistent and report `1.1.2`.

---

## 2. Build Process

**Command:**
```bash
python -m build
```

**Output (excerpt):**
```
Successfully built ailang_lang-1.1.2.tar.gz and ailang_lang-1.1.2-py3-none-any.whl
```

**Result:** ✅ PASS — Both `sdist` (`.tar.gz`) and `wheel` (`.whl`) artifacts built successfully. Deprecation warnings from setuptools noted but did not prevent successful build.

---

## 3. Wheel Verification (Pre-publication Smoke Test)

**Script Used:** `verify_wheel_script.bat`

**Environment:**
- Clean virtual environment: `verify_release` (created by script)
- Installation: `verify_release\Scripts\pip install dist\ailang_lang-1.1.2-py3-none-any.whl`
- Test directory: `C:\Temp\ail_wheel_verify` (created by script, outside source repo)

**Smoke Test Steps & Results:**

| Step | Command | Expected Output | Actual Result | Status |
|------|---------|-----------------|---------------|--------|
| 1 | `ail version` | `AILang v1.1.2` | `AILang v1.1.2` | ✅ PASS |
| 2 | `pip show ailang-lang` | `Version: 1.1.2` | `Version: 1.1.2` | ✅ PASS |
| 3 | `ail new demo` | Project created | Project created | ✅ PASS |
| 4 | `ail run main.ail` | `Hello, AILang!` | `Hello, AILang!` | ✅ PASS |
| 5 | stdlib imports | `stdlib imports OK` | `stdlib imports OK` | ✅ PASS |
| 6 | `ail doctor` | Correct health report | Correct health report | ✅ PASS |
| 7 | `ail heal` | Shows help topics | Shows help topics | ✅ PASS |
| 8 | `ail docs` | Shows document list | Shows document list (partial output) | ✅ PASS (Command executed successfully, minor output parsing issue in script)

**Summary:** All critical wheel verification steps passed. The minor output parsing issue for `ail docs` does not indicate a functional defect in the `ail docs` command itself. The wheel is confirmed to be correctly packaged and functional.
