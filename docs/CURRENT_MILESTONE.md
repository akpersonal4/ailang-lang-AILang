# CURRENT_MILESTONE

## Current Milestone

v0.3.1 — DX-006 Package Manager Architecture Design

## Status

**Architecture design complete** — TOOLING_ARCHITECTURE.md and PACKAGE_MANAGER_DESIGN.md created.
DX-006 implementation is the next priority after design review.

## What Was Delivered in v0.3.1 (Design Phase)

### Tooling Architecture Contract
- **`docs/architecture/TOOLING_ARCHITECTURE.md`** — Architecture contract for all DX tools
- 12 sections covering: layers, tool lifecycle, CLI conventions, exit code policy, JSON report conventions, generated file conventions, `tools/common/` responsibilities, shared utilities, discovery patterns, plugin/extension points, versioning policy, testing strategy
- Appendix A: Current Tool Registry (DX-001 through DX-006)
- Appendix B: Reserved Tool Names (`ail init`, `ail add`, `ail remove`, `ail install`, `ail search`, `ail publish`, `ail update`)

### Package Manager Design Specification
- **`docs/architecture/PACKAGE_MANAGER_DESIGN.md`** — Specification-first design for DX-006
- 13 sections covering: motivation, project manifest (`ail.toml`), package repository, dependency resolution, CLI commands, repository layout, lock file, offline cache, checksum verification, versioning, DX tool integration, future considerations
- 10 open questions identified for review before implementation
- 6 CLI commands designed: `ail init`, `ail add`, `ail remove`, `ail install`, `ail update`, `ail list`

### Key Design Decisions
- **Manifest**: `ail.toml` (TOML format, Python stdlib `tomllib`)
- **Package sources**: Local paths + Git repos (v1); official registry (future)
- **Lock file**: `ail.lock` (TOML, committed to VCS, staleness detection via SHA-256 hash)
- **Dependency resolution**: Backtracking algorithm, semver ranges, highest-version preference
- **Offline cache**: Project-local `.ail/cache/` (v1); global `~/.cache/ail/` (future)
- **Integrity**: SHA-256 checksum verification at download, install, and build
- **Exit codes**: Per TOOLING_ARCHITECTURE.md conventions (0=success, 1=failure, 3=internal error)

### Design Decisions Made in v0.3.0
- DX-004 (Benchmark Runner) — complete and accepted
- DX-005 (Test Generator) — complete and accepted
- tools/common/ Shared Library — extended with hashing and discovery utilities

## Runtime Frozen
No further optimizations, runtime architecture changes, or performance work
until community feedback identifies new bottlenecks.

## Next Milestone
**DX-006 Implementation** — after design documents are reviewed and approved
