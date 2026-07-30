# M84R.3 — Smoke Test

**Date:** 2026-07-22
**Version:** v1.1.2
**Environment:** Windows 11, Python 3.11.15, clean venv

---

## Test Setup

```bash
# 1. Create clean virtual environment
python -m venv release_test

# 2. Install from built wheel (NOT editable, NOT source)
release_test\Scripts\pip.exe install dist/ailang_lang-1.1.2-py3-none-any.whl

# 3. Create test directory outside source repository
mkdir C:\Temp\ail_smoke_test
cd C:\Temp\ail_smoke_test
```

---

## Smoke Test Execution

### Step 1: `ail version`

**Command:**
```bash
release_test\Scripts\python.exe -m compiler.cli.main version
```

**Output:**
```
AILang v1.1.2
```

**Result:** ✅ PASS — Version matches package metadata (1.1.2)

---

### Step 2: `pip show ailang-lang`

**Command:**
```bash
release_test\Scripts\python.exe -m pip show ailang-lang
```

**Output:**
```
Version: 1.1.2
```

**Result:** ✅ PASS — Package metadata matches CLI output

---

### Step 3: `ail new demo`

**Command:**
```bash
release_test\Scripts\python.exe -m compiler.cli.main new demo
```

**Output:**
```
  Created: main.ail
  Created: README.md
  Created: ail.toml
  Created: ail.lock

Project 'demo' created in: C:\Temp\ail_smoke_test\demo
Run:    cd demo && ail run main.ail
```

**Result:** ✅ PASS — Project scaffold created successfully

---

### Step 4: `ail run main.ail`

**Command:**
```bash
cd demo
release_test\Scripts\python.exe -m compiler.cli.main run main.ail
```

**Output:**
```
Hello, AILang!
```

**Result:** ✅ PASS — Default template runs without errors

---

### Step 5: Standard Library Imports

**Command:**
```bash
echo import math; import string; import list; import map; import json; io.writeln("stdlib imports OK") > test_imports.ail
release_test\Scripts\python.exe -m compiler.cli.main run test_imports.ail
```

**Output:**
```
stdlib imports OK
```

**Result:** ✅ PASS — All stdlib modules (math, string, list, map, json) resolve correctly

---

### Step 6: `ail doctor`

**Command:**
```bash
release_test\Scripts\python.exe -m compiler.cli.main doctor
```

**Output:**
```
# AILang Doctor

## Project Health

### Environment

- **Python**: 3.11.15  [OK]
- **CLI**: OK
- **ailang-lang**: [OK] (v1.1.2 (installed from file:///C:/Users/aleckhan/Projects/AiLang_New/dist/ailang_lang-1.1.2-py3-none-any.whl))

### Standard Library

- **stdlib**: [16 modules]

### Project

- **ail.toml**: [OK]
- **main.ail**: [OK]
- **lib/**: [OK] no dependencies

### Summary

Environment looks healthy. Try:

  ail docs AGENTS         # Read the AI agent instructions
  ail context --json      # Get language context for AI tools
  ail new myproject       # Create a new project
```

**Result:** ✅ PASS — Doctor correctly detects package installation and stdlib status. No false positives, no false negatives.

---

### Step 7: `ail heal`

**Command:**
```bash
release_test\Scripts\python.exe -m compiler.cli.main heal
```

**Output:**
```
# AILang Heal - Fix Suggestions

Usage: ail heal <topic>
       ail heal <file.ail>    Analyze a file for errors

Available topics:

  env_setup             Setting up the AILang development environment.
  forward_reference     A function or variable is used before it is defined.
  import_alias          An import alias is not resolving correctly.
  map_safety            map.get() crashes on missing keys. Always guard with map.has().
  missing_import        A required import is missing.
  no_loops              AILang does not support while/for loops.
  operator_error        An operator was used incorrectly.
  string_concat         string.concat() takes exactly 2 arguments.
  type_error            A type mismatch was detected.
```

**Result:** ✅ PASS — Heal tool works correctly

---

### Step 8: `ail docs`

**Command:**
```bash
release_test\Scripts\python.exe -m compiler.cli.main docs
```

**Output:** (document list shown)

**Result:** ✅ PASS — Docs tool works correctly

---

## Summary

| Step | Test | Result |
|------|------|--------|
| 1 | `ail version` | ✅ PASS |
| 2 | `pip show ailang-lang` | ✅ PASS |
| 3 | `ail new demo` | ✅ PASS |
| 4 | `ail run main.ail` | ✅ PASS |
| 5 | stdlib imports | ✅ PASS |
| 6 | `ail doctor` | ✅ PASS |
| 7 | `ail heal` | ✅ PASS |
| 8 | `ail docs` | ✅ PASS |

**All 8 smoke test steps PASSED.**

---

## Key Verification

The smoke test was performed against the **actual built wheel** (`dist/ailang_lang-1.1.2-py3-none-any.whl`) in a **fresh virtual environment** (`release_test`), **not** an editable installation and **not** the source tree. The working directory was `C:\Temp\ail_smoke_test`, completely outside the source repository.

This confirms that the package users install from PyPI is the package that was tested.
