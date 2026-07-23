# M84R.3 — Packaging Verification

**Date:** 2026-07-22
**Version:** v1.1.2

---

## Clean Environment Test

### Environment Setup

1. **Created clean virtual environment:**
   ```bash
   python -m venv release_test
   ```

2. **Installed from built wheel (NOT editable, NOT source):**
   ```bash
   release_test\Scripts\pip.exe install dist/ailang_lang-1.1.2-py3-none-any.whl
   ```

3. **Verified no source tree access:**
   - Working directory: `C:\Temp\ail_smoke_test` (outside source repository)
   - No `PYTHONPATH` set to source
   - No `AILANG_DEV_ROOT` environment variable
   - No `--dev` flag used

### Wheel Contents Verification

The built wheel `dist/ailang_lang-1.1.2-py3-none-any.whl` contains:

| Component | Count | Status |
|-----------|-------|--------|
| stdlib `.ail` files | 16 | ✅ All present |
| `compiler/` package | Full | ✅ |
| `tools/` packages | Full | ✅ |
| `ail_platform/` package | Full | ✅ |
| Entry point (`ail`) | 1 | ✅ |
| `stdlib/__init__.py` | 1 | ✅ |

### Package Metadata Verification

| Field | Value | Status |
|-------|-------|--------|
| Name | `ailang-lang` | ✅ |
| Version | `1.1.2` | ✅ |
| Python requires | `>=3.11` | ✅ |
| Entry point | `ail = compiler.cli.main:main` | ✅ |

### Installation Verification

```
pip show ailang-lang
  Name: ailang-lang
  Version: 1.1.2
  Location: ...\release_test\Lib\site-packages
  Requires: watchdog>=4.0
  Required-by:
```

### ail.exe Creation

The wheel creates the `ail` console script entry point at:
`release_test\Scripts\ail.exe`

Verified working:
```
ail version
AILang v1.1.2
```

---

## Smoke Test Results

All 8 mandatory smoke test steps passed:

| Step | Command | Result |
|------|---------|--------|
| 1 | `ail version` | ✅ `AILang v1.1.2` |
| 2 | `pip show ailang-lang` | ✅ `Version: 1.1.2` |
| 3 | `ail new demo` | ✅ Created main.ail, README.md, ail.toml, ail.lock |
| 4 | `ail run main.ail` | ✅ `Hello, AILang!` |
| 5 | stdlib imports | ✅ `stdlib imports OK` |
| 6 | `ail doctor` | ✅ Correct health report |
| 7 | `ail heal` | ✅ Shows help topics |
| 8 | `ail docs` | ✅ Shows document list |

---

## No Manual Steps Required

- ✅ No environment variables set
- ✅ No manual file copying
- ✅ No `--dev` flag needed
- ✅ No `PYTHONPATH` configuration
- ✅ No `AILANG_DEV_ROOT` configuration

---

## Wheel Build Command

```bash
python -m build --wheel
```

Output:
```
Successfully built ailang_lang-1.1.2-py3-none-any.whl
```
