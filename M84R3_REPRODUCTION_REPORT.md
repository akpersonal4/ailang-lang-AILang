# M84R.3 — Reproduction Report

**Date:** 2026-07-22
**Version:** v1.1.2

---

## P0 — Standard Library Module Resolution (MOD003)

### Reproduction Steps

1. Create a completely clean virtual environment:
   ```bash
   python -m venv release_test
   ```

2. Install the built wheel (NOT editable, NOT source):
   ```bash
   release_test\Scripts\pip.exe install dist/ailang_lang-1.1.2-py3-none-any.whl
   ```

3. Create a new project from a non-repository directory:
   ```bash
   cd C:\Temp\ail_smoke_test
   release_test\Scripts\python.exe -m compiler.cli.main new demo
   cd demo
   ```

4. Run the project:
   ```bash
   release_test\Scripts\python.exe -m compiler.cli.main run main.ail
   ```

5. Test stdlib imports:
   ```bash
   echo "import math; import string; import list; import map; import json; io.writeln(\"stdlib imports OK\")" > test_imports.ail
   release_test\Scripts\python.exe -m compiler.cli.main run test_imports.ail
   ```

### Observed Behavior (Before Fix)

- Step 4: `ail run main.ail` succeeds (default template has no imports)
- Step 5: `MOD003: Module not found: math` (and string, list, map, json)

### Observed Behavior (After Fix)

- Step 4: `ail run main.ail` → `Hello, AILang!`
- Step 5: `stdlib imports OK`

### Affected Modules

`file`, `json`, `list`, `map`, `string` (and all other stdlib modules)

---

## P1 — Version Synchronization

### Reproduction Steps

1. Check version in source:
   ```bash
   python -c "from compiler._version import __version__; print(__version__)"
   ```

2. Check version in pyproject.toml:
   ```bash
   python -c "import tomllib; print(tomllib.loads(open('pyproject.toml','rb').read())['project']['version'])"
   ```

3. Check installed package version:
   ```bash
   release_test\Scripts\python.exe -m pip show ailang-lang
   ```

4. Check CLI version:
   ```bash
   release_test\Scripts\python.exe -m compiler.cli.main version
   ```

### Observed Behavior (Before Fix)

- `pip show` reported `1.1.0` (stale PyPI metadata)
- `ail version` reported `1.1.0` (stale `_version.py`)
- `pyproject.toml` had `1.1.1` (source was bumped but wheel not rebuilt)

### Observed Behavior (After Fix)

- `compiler._version.py`: `1.1.2`
- `pyproject.toml`: `1.1.2`
- `pip show ailang-lang`: `Version: 1.1.2`
- `ail version`: `AILang v1.1.2`

All version sources are now identical.

---

## P1 — Doctor Diagnostics

### Reproduction Steps

1. Install from wheel in clean venv (as above)
2. Run doctor:
   ```bash
   release_test\Scripts\python.exe -m compiler.cli.main doctor
   ```

### Observed Behavior (Before Fix)

- `ail doctor` reported "Standard library: OK" while runtime failed with MOD003
- `ail doctor` reported "ailang package NOT INSTALLED" despite pip installing from wheel

### Observed Behavior (After Fix)

- `ail doctor` correctly reports:
  - `ailang-lang: [OK] (v1.1.2 (installed from file:///...))`
  - `stdlib: [16 modules]`
  - No false positives or false negatives

---

## Test Environment

- **OS:** Windows 11
- **Python:** 3.11.15
- **Virtual Environment:** `python -m venv release_test` (clean, no source tree access)
- **Installation Method:** `pip install dist/ailang_lang-1.1.2-py3-none-any.whl`
- **Working Directory:** `C:\Temp\ail_smoke_test` (outside source repository)
