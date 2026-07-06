# CURRENT_MILESTONE

## Current Milestone

v0.1.2 RC — Release Audit & Bug Fix Sprint

## Status

**Completed** — All 6 compiler bugs fixed, 522 tests passing, documentation synchronized for v0.1.2 release.

## What Was Delivered in v0.1.2

### Compiler Bug Fixes (Sprint #001)

- **BUG-001**: Empty `return;` — now produces clear diagnostic instead of AssertionError crash
- **BUG-002**: Missing initializer `let x = ;` — now produces clear diagnostic instead of AssertionError crash
- **BUG-003**: Module bare-name resolution — `_resolve_name` checks `self._modules`; module functions registered at init
- **BUG-004**: Float literal `3.14` — now emits LEX004 diagnostic at lexer level instead of cryptic parser crash
- **BUG-005**: Block scope shadowing — `_execute_block` creates a new `StackFrame` per block scope
- **BUG-006**: Deep recursion — raised recursion limit from 1000 to 10000

### Documentation & Version Sync

- Version bumped to **0.1.2** across all files
- LEX004 added to LANGUAGE_SPEC.md §2.8 and Appendix E
- CHANGELOG.md restructured with proper v0.1.2 section
- README.md badges and test counts updated (374→522)
- LANGUAGE_TOUR.md float type example fixed
- PROJECT_STATE.json, ROADMAP.md, CURRENT_MILESTONE.md, RELEASE_PROCESS.md all updated

## Quality Gates

- pytest: **522 passed**
- black: clean
- ruff: clean
- mypy: clean

## Next Milestone

v0.2.x — Evidence-based improvements (post-freeze).
