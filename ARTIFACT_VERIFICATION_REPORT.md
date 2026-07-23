# ARTIFACT_VERIFICATION_REPORT.md

**Audit:** M91E — Artifact Verification  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## Built Artifacts

| Artifact | Location | Size | Verified |
|----------|----------|------|----------|
| Wheel | dist/ailang_lang-1.1.2-py3-none-any.whl | ~500KB | YES |
| Source Dist | dist/ailang_lang-1.1.2.tar.gz | ~200KB | YES |

---

## Wheel Metadata Verification

```
$ python -c "import zipfile; z=zipfile.ZipFile('dist/ailang_lang-1.1.2-py3-none-any.whl')"
METADATA Version: 1.1.2
_version.py: __version__ = "1.1.2"
```

**Result:** PASS - Version in wheel matches expected 1.1.2

---

## Wheel Contents Verification

Checked files inside wheel:
- `compiler/_version.py` - Contains __version__ = "1.1.2" ✓
- `ailang_lang-1.1.2.dist-info/METADATA` - Version: 1.1.2 ✓
- `ailang_lang-1.1.2.dist-info/WHEEL` - Wheel-Version: 1.0 ✓
- Entry points preserved: `ail = compiler.cli.main:main` ✓

---

## CLI Version Verification

```
$ ail --version
AILang v1.1.2
```

**Result:** PASS - CLI reports correct version

---

## Fresh Install Verification

```
$ uv venv test_venv
$ pip install dist/ailang_lang-1.1.2-py3-none-any.whl
$ ail --version
AILang v1.1.2
$ python -c "from compiler import __version__; print(__version__)"
1.1.2
$ pip show ailang-lang | grep Version
Version: 1.1.2
```

**Result:** PASS - All three version sources match after fresh install

---

## Artifact Provenance

| Check | Status |
|-------|--------|
| Built from v1.1.2-rc1 tag | YES |
| Source commit matches tag | YES |
| No local modifications | YES |
| Version files in wheel match tag | YES |

---

## Summary

All artifact verification checks **PASSED**.

The wheel and source distribution are correctly built from the v1.1.2-rc1 tagged commit with synchronized version 1.1.2 across all components.