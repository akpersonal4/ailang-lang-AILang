# TEMPLATE_REPAIR_REPORT.md — M89B

**Milestone:** M89B — Template Repair  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## Issues Fixed

### Issue 1: Missing Semicolon in Generated Code

**Before:**
```ailang
fn main() {
    print("Hello, AILang!");
    return 0
}
```

**After:**
```ailang
fn main() {
    print("Hello, AILang!");
    return 0;
}
```

**Root cause:** Template string in `compiler/cli/main.py` had `return 0` without semicolon. The formatter auto-corrected this, but the template should generate correct code out of the box.

**Fix:** Added semicolon to `_NEW_PROJECT_TEMPLATES["main.ail"]` in `compiler/cli/main.py:1117-1121`.

### Issue 2: Language Version Mismatch in ail.toml

**Before:**
```toml
[language]
version = "0.3"
```

**After:**
```toml
[language]
version = "1.1.2"
```

**Root cause:** Template used hardcoded `0.3` instead of the current package version.

**Fix:** Updated `_AIL_TOML_TEMPLATE` in `compiler/cli/main.py:1205-1214`.

## Verification

| Step | Command | Result |
|------|---------|--------|
| Create project | `ail new _test_m89` | PASS |
| Generated main.ail | Contains `return 0;` | PASS |
| Generated ail.toml | `version = "1.1.2"` | PASS |
| Build | `ail build _test_m89/main.ail` | PASS |
| Run | `ail run _test_m89/main.ail` | PASS (prints "Hello, AILang!") |

**Result: Generated projects compile, run, and produce correct output without requiring `ail fmt`.**
