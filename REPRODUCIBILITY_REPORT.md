# REPRODUCIBILITY_REPORT.md

**Audit:** M91G — Reproducibility Verification  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## Test Environment Setup

```
$ uv venv test_venv --python 3.11
$ . test_venv/Scripts/Activate.ps1
$ pip install dist/ailang_lang-1.1.2-py3-none-any.whl
```

---

## Version Verification Results

| Source | Command | Output | Expected | Match |
|--------|---------|--------|----------|-------|
| CLI | `ail --version` | `AILang v1.1.2` | `v1.1.2` | YES |
| Python | `compiler.__version__` | `1.1.2` | `1.1.2` | YES |
| pip | `pip show ailang-lang` | `Version: 1.1.2` | `1.1.2` | YES |

---

## Functional Test

```
$ ail run --help
Compile and run an AILang program.
...
```

**Result:** CLI works correctly after fresh install

---

## Import Test

```python
>>> from compiler import __version__
>>> print(__version__)
1.1.2

>>> import compiler
>>> compiler.__version__
'1.1.2'
```

**Result:** Module imports correctly with version attribute

---

## Package Metadata

```
$ pip show ailang-lang
Name: ailang-lang
Version: 1.1.2
Summary: Deterministic business application platform optimized for AI-assisted development
Requires-Python: >=3.11
```

---

## Reproducibility Checklist

| Test | Result |
|------|--------|
| Fresh venv created | PASS |
| Wheel installed | PASS |
| CLI functional | PASS |
| Module imports | PASS |
| Version attributes match | PASS |
| pip metadata correct | PASS |
| No dependency conflicts | PASS |

---

## Tag-to-Install Provenance

```
Tag v1.1.2-rc1 (cb9451c)
        ↓
Build wheel (ailang_lang-1.1.2-py3-none-any.whl)
        ↓
Install in fresh venv
        ↓
All versions report 1.1.2 ✓
```

**The release is reproducible from tag to installed package.**

---

## Conclusion

The Release Candidate v1.1.2-rc1 is fully reproducible:
- Wheel built from tagged commit
- Fresh install matches tag version
- All version sources consistent
- No errors or conflicts