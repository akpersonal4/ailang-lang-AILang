# Development Log — Kanban Project Management System

## Build Summary

| Attempt | Result | Errors |
|---------|--------|--------|
| 1 | FAIL | 7 `Undefined identifier` (forward references) |
| 2 | PASS | 0 |

## Run Summary

| Attempt | Result | Details |
|---------|--------|---------|
| 1 | PASS | Full demo flow: board creation, 7 tasks, column display, report, file save |

## Error Log

### Build Attempt #1 — 7 Forward References

| # | Error | Cause | Fix |
|---|-------|-------|-----|
| 1 | `Undefined identifier: filter_by_field` | `print_board_iter` (Level 3) calls `filter_by_field` defined after it | Moved `filter_by_field` to Level 3 section |
| 2 | `Undefined identifier: convert.to_string` | Called before the function that uses it | `convert` is stdlib; was a dependency ordering issue in the same function |
| 3 | `Undefined identifier: board_total_tasks` | Called in `print_board_iter` (Level 3) but defined in Level 4 | Moved to Level 3, before `print_board_iter` |
| 4 | `Undefined identifier: print_task` | Called in `print_tasks_in_list` (Level 3) but defined in Level 4 | Moved to Level 3, before `print_board_iter` |
| 5-6 | `Undefined identifier: ...` | Two more forward refs from print function reordering issues | Same pattern |
| 7 | `Undefined identifier: print_column_tasks_iter` | Called in `print_column_tasks` but defined after it | Swapped order: `print_column_tasks_iter` before `print_column_tasks` |

### Root Cause Analysis

All 7 errors were forward references — consistent with AILang's top-level-only function rule. The first draft was written top-down rather than bottom-up. Fix: physically sort function definitions so callee precedes caller.

### Run Attempt #1 — No Errors

Demo ran cleanly: created Sprint 24 board, added 7 tasks across 4 columns, printed board view, ran column counts, priority distribution, displayed full report, saved JSON.

## Metrics

- **Lines:** 1012 total (894 non-blank)
- **Functions:** 102
- **Compile attempts:** 2 (1 fail, 1 pass)
- **Run attempts:** 1 (1 pass)
- **Runtime:** 0.73s
