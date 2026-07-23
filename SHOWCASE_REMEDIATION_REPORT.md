# SHOWCASE_REMEDIATION_REPORT.md — M89D

**Milestone:** M89D — Showcase Applications Remediation  
**Date:** 2026-07-23  
**Status:** COMPLETE

---

## Issues Fixed

### Issue 1: hotel_management (SEM001 — stdlib name collision)

**Root cause:** Three user-defined functions had names identical to stdlib builtins:
- `list_find_by_key` → collides with `list_find_by_key` builtin
- `list_filter_by_key` → collides with `list_filter_by_key` builtin
- `list_filter_by_contains` → collides with `list_filter_by_contains` builtin

When these names are defined at the top level, they shadow the stdlib builtins, causing the stdlib wrapper functions to call the user's functions instead of the native implementations.

**Fix:** Renamed all three functions (and their helpers):
- `list_find_by_key` → `hotel_find_by_key` (12 replacements)
- `list_find_by_key_step` → `hotel_find_by_key_step` (3 replacements)
- `list_filter_by_key` → `hotel_filter_by_key` (7 replacements)
- `list_filter_by_contains` → `hotel_filter_by_contains` (4 replacements)

**Total: 26 replacements across the file.**

**Result:** `ail build apps/hotel_management/main.ail` → PASS

### Issue 2: kanban (SEM001 — stdlib name collision)

**Root cause:** One user-defined function had a name identical to a stdlib builtin:
- `list_copy` → collides with `list_copy` builtin

**Fix:** Renamed to `kanban_copy_list` (3 replacements).

**Result:** `ail build apps/kanban/main.ail` → PASS

### Issue 3: Additional collisions found and fixed

| App | Old Name | New Name | Replacements |
|-----|----------|----------|:------------:|
| inventory_mgmt | `list_copy` | `inventory_copy_list` | 6 |
| static_analyzer | `list_copy` | `analyzer_copy_list` | 2 |
| phase11/algorithms/a_star | `list_contains` | `astar_list_contains` | 3 |

## Verification Summary

| App | Before | After |
|-----|--------|-------|
| hotel_management | FAIL (SEM001) | PASS (builds) |
| kanban | FAIL (SEM001) | PASS (builds) |
| inventory_mgmt | FAIL (SEM001) | PASS (builds) |
| static_analyzer | FAIL (SEM001) | PASS (builds) |
| a_star | FAIL (SEM001) | PASS (builds) |

**Result: All 5 showcase apps with stdlib name collisions now compile successfully.**
