# v0.3.1 Release Validation — DX-006 AILang Package Manager

## Feature Checklist

| Feature | Status | Verified |
|---------|:------:|:--------:|
| Manifest parser — valid `ail.toml` | ✅ Complete | ✅ |
| Manifest parser — invalid `ail.toml` error | ✅ Complete | ✅ |
| Manifest parser — BOM handling | ✅ Complete | ✅ |
| Manifest discovery (walk up directories) | ✅ Complete | ✅ |
| `ail init` — creates project structure | ✅ Complete | ✅ |
| `ail init` — refuses non-empty directory | ✅ Complete | ✅ |
| `ail install` — local path dependency | ✅ Complete | ✅ |
| `ail install` — Git dependency | ✅ Complete | 🔍 (needs Git repo for integration test) |
| `ail install` — lock file replay | ✅ Complete | ✅ |
| `ail install` — staleness detection | ✅ Complete | ✅ |
| `ail install` — `--no-lock` flag | ✅ Complete | ✅ |
| `ail install` — `--frozen-lockfile` flag | ✅ Complete | ✅ |
| `ail install` — `--offline` flag | ✅ Complete | ✅ |
| `ail install` — transitive dependencies | ✅ Complete | ✅ |
| `ail install` — circular dependency detection | ✅ Complete | ✅ |
| Dependency resolver — topological sort | ✅ Complete | ✅ |
| Lock file — TOML format | ✅ Complete | ✅ |
| Lock file — `input_hash` | ✅ Complete | ✅ |
| Lock file — per-package metadata | ✅ Complete | ✅ |
| Cache — SHA-256 checksums | ✅ Complete | ✅ |
| Cache — stale package cleanup | ✅ Complete | ✅ |
| `ail add` | 📋 Stub | — |
| `ail remove` | 📋 Stub | — |
| `ail update` | 📋 Stub | — |
| `ail list` | 📋 Stub | — |

## Acceptance Tests

| # | Test | Status |
|:-:|------|:------:|
| 1 | Package name validation | ✅ Pass |
| 2 | `ail init` creates project structure | ✅ Pass |
| 3 | `ail init` refuses non-empty dir | ✅ Pass |
| 4 | Parse valid manifest | ✅ Pass |
| 5 | Parse invalid manifest | ✅ Pass |
| 6 | Dependency parsing (3 source types) | ✅ Pass |
| 7 | Install local dependency | ✅ Pass |
| 8 | Lock file content | ✅ Pass |

Run: `python tests/dx_tool_006_acceptance_test.py`

## Key Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Manifest format | TOML (`ail.toml`) | Python stdlib `tomllib`, human-readable, supports comments |
| Lock file | TOML (`ail.lock`), committed to VCS | Reproducible builds, fast install replay |
| Dependency resolution | Recursive, topological sort | Dependencies before dependents |
| Local deps | `path=` in `[dependencies]` | Simple monorepo support |
| Git deps | `git=` + shallow clone | No history needed for dependencies |
| Cache | Project-local `.ail/cache/` (v1) | Simple v1, no concurrency concerns |
| Checksum | SHA-256 | Standard integrity algorithm |
| Exit codes | 0=success, 1=failure, 3=internal error | Per TOOLING_ARCHITECTURE.md |

## Open Questions (from design doc)

| # | Question | Decision |
|:-:|----------|----------|
| 1 | `ail.lock` format? | **TOML** (consistency with `ail.toml`) |
| 2 | Global cache location? | **Deferred** (v1 uses project-local `.ail/cache/`) |
| 3 | Auto `ail add` on install? | **No** (principle of least surprise) |
| 4 | Optimistic or pessimistic resolution? | **Highest** (consistent with Cargo/npm) |
| 5 | Lock file committed to VCS? | **Yes** (reproducible builds) |
| 6 | `[build]`, `[test]`, `[benchmark]` sections now? | **Incrementally** (add when tool ships) |
| 7 | Local dep directory name? | **`lib/`** (short, conventional) |
| 8 | Shallow or full Git clone? | **Shallow** (no history needed) |
| 9 | `--dev` flag? | **Deferred** (v1.1) |
| 10 | Path deps outside project? | **Yes** (`../path/to/lib`) |

## Files

| File | Purpose |
|------|---------|
| `tools/ail_package_manager/__main__.py` | CLI entry point |
| `tools/ail_package_manager/manifest.py` | `ail.toml` parser and validator |
| `tools/ail_package_manager/init.py` | `ail init` command |
| `tools/ail_package_manager/installer.py` | Installation engine |
| `tools/ail_package_manager/resolver.py` | Dependency resolution |
| `tools/ail_package_manager/lock.py` | Lock file generation/parsing |
| `tools/ail_package_manager/cache.py` | Package cache management |
| `tools/ail_package_manager/models.py` | Data models |
| `tools/ail_package_manager/README.md` | Tool documentation |
| `tests/dx_tool_006_acceptance_test.py` | Acceptance tests |
| `docs/architecture/PACKAGE_MANAGER_DESIGN.md` | Design specification |
