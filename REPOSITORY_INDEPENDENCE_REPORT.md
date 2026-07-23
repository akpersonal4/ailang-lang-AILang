# REPOSITORY_INDEPENDENCE_REPORT.md

**Generated:** 2026-07-21  
**Audit:** M83K Self-Contained Developer Experience Certification

---

## Overview

This report verifies that application development does not require knowledge of the repository structure.

---

## Audit Method

Simulated fresh project creation using only:
```bash
pip install ailang-lang
mkdir myproject
cd myproject
ail run main.ail
```

---

## Repository Assumptions Tested

| Assumption | Tested | Status |
|------------|--------|--------|
| No `stdlib/` directory needed | Verified | ✅ PASS |
| No repository access for stdlib | Verified | ✅ PASS |
| No `.git/` access required | Verified | ✅ PASS |
| No compiler source inspection | Verified | ✅ PASS |

---

## Evidence

### Test: Fresh Project with Stdlib Imports

```ail
import string;
import list;
import map;

fn main() {
    let s = string.uppercase("hello");
    return 0
}
```

**Result:** ✅ Compiled and ran successfully

**Key Finding:** Stdlib resolved from installed package, not repository

---

### Test: Project Scaffolding

```
ail new myproject
```

**Result:** ✅ Created main.ail, README.md, ail.toml, ail.lock

**Key Finding:** Templates generated from CLI code, not repository files

---

### Test: Documentation Access

```
ail docs STDLIB_REFERENCE
```

**Result:** ✅ Returns embedded documentation

**Key Finding:** Documentation available without repository

---

## Repository-Dependent Code Paths

### Identified (But Not Exposed to Users)

| Component | Path | Exposure |
|-----------|------|----------|
| Package manager cache | `ail_platform/manifest.py` | Internal |
| Rename tool | `compiler/cli/main.py:cmd_rename` | Internal |
| Doctor tool | `tools/ail_doctor/__main__.py` | See issues below |

---

## `ail doctor` Repository Dependencies

**Critical Issues:**

1. **checks `import ailang`** instead of `import compiler`
2. **checks for DEVELOPMENT_STATUS.md** (repo-only)
3. **checks for PROJECT_MEMORY.md** (repo-only)
4. **walks entire repository** for orphan/broken-link detection

These are implementation issues for a tool that should work in installed-only environments.

---

## Conclusion

**Status:** ✅ PASS (with tool adjustments needed)

Stdlib resolution and basic development work without repository. The `ail doctor` tool needs modification to serve installed users correctly.