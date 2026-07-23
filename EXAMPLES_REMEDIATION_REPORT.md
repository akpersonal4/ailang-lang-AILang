# EXAMPLES_REMEDIATION_REPORT.md — M89C

**Milestone:** M89C — Official Examples Remediation  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## Issues Fixed

### Issue 1: member_access.ail (LEX001 → TYP001)

**Root cause:** The M88 report cited LEX001 (colon operator), but the actual file used dot syntax. The real issue was that the examples lacked `main()` and `print()` calls, making them non-functional as standalone programs.

**Fix:** Rewrote example to use `map.new()` + `map.set()` with explicit `print()` calls. Uses `map.get()` for type-safe access.

**Result:** Builds and runs. Output: `Name: Alice`, `Age: 30`

### Issue 2: member_function_calls.ail

**Root cause:** Same as above — no `main()`, no `print()`.

**Fix:** Rewrote example to demonstrate map value access with `map.get()` and print output.

**Result:** Builds and runs. Output: `City: Portland`, `State: OR`

### Issue 3: chained_member_access.ail

**Root cause:** Same as above — no `main()`, no `print()`.

**Fix:** Rewrote example to demonstrate nested map access with `map.get()`.

**Result:** Builds and runs. Output: `DB Host: localhost`, `DB Port: 5432`

### Issue 4: patterns/recursive_map.ail (SEM001)

**Root cause:** The example defined a function named `map` which collided with the stdlib `map` module. The language doesn't allow shadowing stdlib module names.

**Fix:** Renamed `map` function to `transform_list` and `map_helper` to `transform_list_helper`. Added `print()` calls and descriptive comments.

**Result:** Builds and runs. Output: `Original: 1, 2, 3, 4`, `Doubled: 2, 4, 6, 8`

## Verification Summary

| Example | Before | After | Output |
|---------|--------|-------|--------|
| member_access.ail | FAIL (no main) | PASS | Name: Alice, Age: 30 |
| member_function_calls.ail | FAIL (no main) | PASS | City: Portland, State: OR |
| chained_member_access.ail | FAIL (no main) | PASS | DB Host: localhost, DB Port: 5432 |
| patterns/recursive_map.ail | FAIL (SEM001) | PASS | Doubled: 2, 4, 6, 8 |

**Result: 4/4 previously failing examples now compile, run, and produce visible output.**
