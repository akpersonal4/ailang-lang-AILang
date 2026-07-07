# CURRENT_MILESTONE

## Current Milestone

v0.3.1 — DX-006 Package Manager

## Status

**In progress** — DX-004 (Benchmark Runner) and DX-005 (Test Generator) complete.
DX-006 (Package Manager) is the next priority.

## What Was Delivered in v0.3.0

### DX-004 — Benchmark Runner
- `python -m tools.ail_benchmark` — auto-discovers apps, suite modes (quick/canonical/full), configurable repetition, baseline save/compare, regression detection, CI-friendly exit codes
- Output: `generated/benchmarks/BENCHMARK_REPORT.md` + `.json`

### DX-005 — Test Generator
- `python -m tools.ail_testgen` — three-stage pipeline (Discovery → Analysis → Generation)
- Intermediate `TestCase` model — facts first, rendering second
- Pure Python generators — no template files
- Flags: `--dry-run`, `--force`, `--app`, `--report-only`
- Output: 44 generated test files in `tests/generated/`, `generated/TEST_GENERATION_REPORT.md` + `.json`

### tools/common/ Shared Library
- Extended with `hashing.py` (SHA-256 file hashing), `discover_apps()`, `list_py_files()`
- Existing tools continue to work — incremental adoption

### Quality Gates
- pytest: **772 passed** (up from 658)
- black: clean, ruff: clean, mypy: clean
- DX-005: 9 acceptance + 4 regression + 4 AI validation = 17 tests, all passing

## Runtime Frozen
No further optimizations, runtime architecture changes, or performance work
until community feedback identifies new bottlenecks.

## Next Milestone
**DX-006** — Package Manager (`ail init`, `ail install`, dependency resolution)
