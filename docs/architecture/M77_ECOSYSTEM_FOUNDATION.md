# M77 — Ecosystem Foundation & Package Management

> **Status:** Architecture
> **Date:** 2026-07-17
> **Author:** opencode (AI-assisted)
> **Supersedes:** None
> **Depends on:** M76.3 (v1.0.11)

---

## 1. Context

AILang has 66+ applications, 16 stdlib modules, and a published package manager (~800 LOC) that handles local and git dependencies. The compiler core, DX tooling, AI integration, diagnostics, and release engineering have reached stable state through M76.3.

The next bottleneck is ecosystem growth: packages cannot be shared, discovered, or managed systematically.

### What Exists Today

| Component | Status | Location | Notes |
|-----------|--------|----------|-------|
| `ail.toml` parser/validator | Complete | `tools/ail_package_manager/manifest.py` | Also duplicated in `ail_platform/manifest.py` |
| Dependency models | Complete | `tools/ail_package_manager/models.py` | `ProjectManifest`, `DependencySpec`, `LockFile` |
| `ail new` (scaffolding) | Complete | `compiler/cli/main.py:cmd_new` | Creates ail.toml + ail.lock |
| `ail add` | Complete | `tools/ail_package_manager/commands.py` | Modifies ail.toml |
| `ail remove` | Complete | `tools/ail_package_manager/commands.py` | Modifies ail.toml |
| `ail install` | Complete | `tools/ail_package_manager/installer.py` | Local + git deps, lock replay |
| `ail update` | MVP | `tools/ail_package_manager/commands.py` | Re-runs install pipeline |
| `ail list` | Complete | `tools/ail_package_manager/commands.py` | Reads ail.toml + lib/ status |
| `ail publish` | Partial | `compiler/package/registry.py` | Local only, no auth, uses older code copy |
| `ail search` | Not implemented | — | Requires registry server |
| `ail init` | Exists but unwired | `tools/ail_package_manager/init.py` | Not in main CLI dispatch |
| Lock file | Complete | `tools/ail_package_manager/lock.py` | TOML format, SHA-256 staleness |
| Resolver | Partial | `tools/ail_package_manager/resolver.py` | Exact match or `*`, no semver ranges |
| Cache | Complete | `tools/ail_package_manager/cache.py` | SHA-256 checksums, local only |
| Registry client | Partial | `tools/ail_package_manager/registry.py` | Also duplicated in `compiler/package/registry.py` |

### Key Gaps

1. **Code duplication**: `compiler/package/registry.py` and `tools/ail_package_manager/registry.py` are near-identical copies
2. **No semver range parsing**: Only exact match or `*` (latest)
3. **No conflict resolution**: Same-package-different-version not handled
4. **No `ail search`**: Requires registry server (out of scope per §3.3)
5. **`ail init` not wired**: Exists in standalone tool but not in main CLI
6. **`ail new` vs `ail init` discrepancy**: User docs say `ail new`, design doc says `ail init`
7. **No integration tests**: install, resolver, lock, registry flows untested
8. **Subprocess delegation**: All `ail pkg` commands shell out instead of importing directly

---

## 2. Architecture Decisions

### ADR-010: Consolidate Package Manager Code

**Decision:** Merge `compiler/package/registry.py` into `tools/ail_package_manager/registry.py`. Remove the `compiler/package/` directory. Wire all package management through `tools/ail_package_manager/`.

**Rationale:** Two near-identical copies create confusion about which is authoritative. The `tools/` copy is more complete (uses typed models, has checksum verification). The `compiler/` copy is older and used only by `cmd_publish`.

**Consequences:**
- `cmd_publish` imports from `tools/ail_package_manager` instead of `compiler/package`
- `compiler/package/` directory removed
- No external dependency changes

### ADR-011: `ail new` is the Public API, `ail init` is Internal

**Decision:** `ail new` remains the user-facing command for project scaffolding. `ail init` (if kept) is an internal alias used by the package manager tool.

**Rationale:** `ail new` is documented in PACKAGES.md and has been the public API since v1.0.8. Changing it would break existing documentation and user muscle memory.

**Consequences:**
- `ail new` stays in main CLI dispatch
- `ail init` remains in `tools/ail_package_manager/__main__.py` for internal use
- No breaking change

### ADR-012: Local-First, Registry-Ready Architecture

**Decision:** M77 implements full package management for local path and git dependencies. Registry support is designed but not implemented (server does not exist). The architecture must not block future registry addition.

**Rationale:** Per PACKAGE_MANAGER_DESIGN.md §3.3, the official registry is out of scope for v1. Designing for registry-ready architecture means the API surface is stable when a registry is added later.

**Consequences:**
- `ail publish` supports local directory registry only
- `ail search` is deferred to M78+ (requires registry server)
- All resolver and installer interfaces accept a `source_type` parameter that can be extended
- Registry client code is retained but marked as `@future`

### ADR-013: Semver Range Parsing

**Decision:** Implement full semver range parsing (>=, ^, ~, exact, range) using a standalone `_parse_version_requirement()` function. No external dependency.

**Rationale:** The current resolver only handles exact match or `*`. Real package management requires ranges (`^1.0.0`, `>=1.2.0,<2.0.0`). This is a prerequisite for M77.5 (dependency resolution).

**Consequences:**
- New function in `tools/ail_package_manager/resolver.py`
- ~50-80 lines of semver parsing logic
- Follows Cargo/npm semantics for range operators
- No external dependency (stdlib only)

### ADR-014: Dependency Conflict Detection

**Decision:** Implement conflict detection during resolution. When two packages require incompatible versions of the same dependency, emit a clear diagnostic with the conflicting constraints and suggested resolution.

**Rationale:** Without conflict detection, `ail install` silently installs whatever version it encounters last, leading to non-reproducible builds.

**Consequences:**
- Resolution algorithm tracks all constraints per package name
- On conflict: collect all constraints, find intersection, report if empty
- Diagnostic format: `CONFLICT: package X requires Y>=1.0 but Z requires Y<1.0`
- Exit code: non-zero on conflict

### ADR-015: Circular Dependency Detection

**Decision:** Track the resolution path and detect cycles. On cycle, emit diagnostic with the cycle path.

**Rationale:** Circular dependencies are undefined in AILang (no loops, no lazy evaluation). They must be detected at install time, not at runtime.

**Consequences:**
- Resolution maintains a `resolution_path: list[str]` stack
- Before recursing into a dep, check if it's already in the path
- On cycle: report `CIRCULAR: A → B → C → A`
- Exit code: non-zero on cycle

---

## 3. M77 Scope Definition

### M77.1 — Package Installation

**Scope:** Fix and harden existing `ail install`. Add semver range support. Add conflict detection. Add circular dependency detection. Add offline reproducible installs.

**Files to modify:**
- `tools/ail_package_manager/resolver.py` — semver ranges, conflict detection, cycle detection
- `tools/ail_package_manager/installer.py` — `--frozen-lockfile` hardening
- `tools/ail_package_manager/manifest.py` — version requirement parsing
- `tests/test_package_install.py` — new integration tests

**Not in scope:** Registry-based installation (no server exists).

### M77.2 — Package Publishing

**Scope:** Consolidate registry code. Ensure `ail publish` works for local directory registry. Add metadata validation. Add README/license support in package metadata.

**Files to modify:**
- `tools/ail_package_manager/registry.py` — consolidate from `compiler/package/registry.py`
- `compiler/cli/main.py` — update `cmd_publish` import
- `compiler/package/` — delete directory
- `tests/test_package_publish.py` — new tests

**Not in scope:** Remote registry publishing (no server exists). Authentication.

### M77.3 — Package Search

**Scope:** Implement `ail search` for **local packages only** (search `lib/` directory and any local registry directories).

**Files to create/modify:**
- `tools/ail_package_manager/search.py` — new file, local search implementation
- `compiler/cli/main.py` — wire `ail search` into dispatch
- `tests/test_package_search.py` — new tests

**Not in scope:** Remote registry search (no server exists).

### M77.4 — Package Metadata

**Scope:** Validate and standardize `ail.toml` schema. Ensure `[package]` section is consistent across all tools. Add `ail package info <name>` to display installed package metadata.

**Files to modify:**
- `tools/ail_package_manager/manifest.py` — schema validation
- `tools/ail_package_manager/models.py` — add `PackageInfo` model
- `compiler/cli/main.py` — add `ail info` command
- `tests/test_package_metadata.py` — new tests

### M77.5 — Dependency Resolution

**Scope:** Implement full resolution algorithm with semver ranges, conflict detection, circular detection, and topological sort. This is the core of M77.

**Files to modify:**
- `tools/ail_package_manager/resolver.py` — major rewrite
- `tools/ail_package_manager/lock.py` — ensure lock format supports full resolution tree
- `tests/test_package_resolver.py` — new comprehensive tests

### M77.6 — AI Workflow Integration

**Scope:** Update `ail context --json` to include package information. Update `ail docs` to support package documentation.

**Files to modify:**
- `tools/ail_context/__main__.py` — add package metadata to context output
- `compiler/cli/main.py` — update `cmd_docs` to search `lib/` for docs
- `tests/test_package_ai_integration.py` — new tests

---

## 4. Dependency Resolution Strategy

### 4.1 Algorithm

```
resolve(manifest, lockfile):
    if lockfile.is_fresh(manifest):
        return lockfile.packages  # replay lock

    resolved = {}
    resolution_path = []

    for name, constraint in manifest.dependencies.items():
        _resolve_dep(name, constraint, resolved, resolution_path, depth=0)

    return topological_sort(resolved)

_resolve_dep(name, constraint, resolved, path, depth):
    if name in path:
        raise CircularDependency(path + [name])

    path.append(name)

    if name in resolved:
        if not constraint.satisfies(resolved[name].version):
            raise VersionConflict(name, constraint, resolved[name].version)
        return  # already resolved with compatible version

    candidates = fetch_candidates(name, constraint)
    best = select_best(candidates)

    transitive = fetch_metadata(name, best.version).dependencies
    resolved[name] = ResolvedDependency(name, best.version, ...)

    for dep_name, dep_constraint in transitive.items():
        _resolve_dep(dep_name, dep_constraint, resolved, path, depth + 1)

    path.pop()
```

### 4.2 Semver Range Operators

| Operator | Meaning | Example |
|----------|---------|---------|
| `*` | Any version | `*` |
| `>=1.0.0` | Greater than or equal | `>=1.0.0` |
| `<2.0.0` | Less than | `<2.0.0` |
| `>=1.0.0,<2.0.0` | Range | `>=1.0.0,<2.0.0` |
| `^1.0.0` | Compatible with (same major) | `^1.0.0` = `>=1.0.0,<2.0.0` |
| `^0.1.0` | Compatible with (same minor for 0.x) | `^0.1.0` = `>=0.1.0,<0.2.0` |
| `~1.2.0` | Approximately equivalent (same minor) | `~1.2.0` = `>=1.2.0,<1.3.0` |
| `1.0.0` | Exact | `1.0.0` |

### 4.3 Conflict Detection

When two packages require the same dependency with incompatible constraints:

```
Package A requires: lib_math >=1.0.0,<2.0.0
Package B requires: lib_math >=2.0.0
Conflict: lib_math has no version satisfying both constraints
```

Diagnostic output:
```
ERROR CONFLICT001: Dependency conflict for 'lib_math'
  Package 'package_a@1.0.0' requires: >=1.0.0,<2.0.0
  Package 'package_b@2.1.0' requires: >=2.0.0
  No version satisfies all constraints.
Suggestion: Update package_a to a version that supports lib_math >=2.0.0
  ail update package_a
```

### 4.4 Circular Dependency Detection

When a dependency chain forms a cycle:

```
A depends on B
B depends on C
C depends on A
```

Diagnostic output:
```
ERROR CIRCULAR001: Circular dependency detected
  A → B → C → A
  Resolution stopped at depth 3.
Suggestion: Remove one of the circular dependencies or merge the packages.
```

---

## 5. Package Manifest Specification

### 5.1 `ail.toml` Schema

```toml
[package]
name = "inventory-utils"          # Required: snake_case
version = "1.0.0"                 # Required: semver
description = "Inventory utilities"  # Optional
authors = ["Name <email>"]        # Optional
license = "Apache-2.0"            # Optional: SPDX expression
entry = "src/main.ail"            # Optional: default src/main.ail
readme = "README.md"              # Optional

[language]
version = ">=1.0.0"               # Optional: AILang version constraint

[dependencies]
json = ">=1.0.0"                  # Version constraint
auth = "^2.1.0"                   # Compatible with
utils = { path = "../utils" }     # Local path
helper = { git = "https://...", tag = "v1.0.0" }  # Git

[dev-dependencies]                # Optional: dev-only deps
test_helpers = ">=0.1.0"

# [build]                          # Future
# [test]                           # Future
# [benchmark]                      # Future
```

### 5.2 `ail.lock` Format

```toml
# Auto-generated by ail install
# Do not edit manually

input_hash = "sha256:abc123..."

[[packages]]
name = "json"
version = "1.2.0"
source = "registry"
checksum = "sha256:def456..."
dependencies = ["math"]

[[packages]]
name = "auth"
version = "2.1.3"
source = "git"
git = "https://github.com/..."
tag = "v2.1.3"
checksum = "sha256:ghi789..."
dependencies = []
```

---

## 6. CLI Command Design

### 6.1 Commands Summary

| Command | Status in M77 | Description |
|---------|---------------|-------------|
| `ail new` | Exists (no change) | Create new project with ail.toml |
| `ail install` | Enhance | Install deps from ail.toml |
| `ail add` | Enhance | Add dependency to ail.toml |
| `ail remove` | Enhance | Remove dependency from ail.toml |
| `ail update` | Enhance | Re-resolve and update lock |
| `ail list` | Enhance | Show installed packages |
| `ail publish` | Consolidate | Publish to local registry |
| `ail search` | New | Search local packages |
| `ail info` | New | Show package metadata |
| `ail init` | Internal | Alias for `ail new` (not in main CLI) |

### 6.2 `ail install` Flags

```
ail install                    # Install from ail.toml, replay lock if fresh
ail install --frozen-lockfile  # Fail if lock is stale (CI mode)
ail install --offline          # Fail if any package not cached
ail install --no-lock          # Install without generating lock file
ail install --verbose          # Show resolution details
```

### 6.3 `ail publish` Flags

```
ail publish                    # Publish to local directory registry
ail publish --dry-run          # Show what would be published
ail publish --registry <path>  # Publish to specific local registry
```

### 6.4 `ail search` Flags

```
ail search <query>             # Search local lib/ directory
ail search --registry <path>   # Search specific local registry
```

### 6.5 `ail info` Flags

```
ail info <package>             # Show info for installed package
ail info --all                 # Show all installed packages
```

---

## 7. Migration Strategy for Future Registry Support

### 7.1 Phase 1: M77 (Current)

- Local path deps: fully working
- Git deps: fully working
- Local directory registry: `ail publish` writes to `./registry/`
- Remote registry: not implemented (no server)

### 7.2 Phase 2: M78+ (Future)

When a registry server exists:

1. **`ail search`** — add remote search alongside local search
2. **`ail publish`** — add remote publish with auth token
3. **`ail install`** — add registry source type to resolver
4. **Global cache** — `~/.cache/ail/` for downloaded packages
5. **Package signing** — optional GPG signatures

### 7.3 API Surface Stability

All interfaces are designed to be registry-ready:

- `resolver.resolve()` accepts a `source_priority: list[Source]` parameter
- `installer.install()` accepts a `registry_url: str | None` parameter
- `registry.py` functions accept a `mode: Literal["local", "remote"]` parameter
- New source types are added by extending the `Source` enum, not by changing APIs

---

## 8. Architectural Constraints

| Constraint | Source | Impact |
|------------|--------|--------|
| No external dependencies | ADR-001, pyproject.toml | Semver parser must be implemented in stdlib-only Python |
| No loops in AILang | Language spec | Circular deps must be detected at install time, not runtime |
| Bottom-up function ordering | ADR-004 | Package code must follow Python conventions (no constraint on AILang packages) |
| Stdlib is separate from packages | ADR-008 | Package manager never modifies stdlib |
| AI-consumable documentation | ADR-009 | All M77 docs must be structured and referenced from AGENTS.md |
| `ail.toml` is workspace root marker | WORKSPACE_ROOT.md | Manifest discovery walk-up must be consistent |
| Existing ~800 LOC is production-ready | V1 RC review | M77 must not break existing functionality |
| Official registry is out of scope for v1 | PACKAGE_MANAGER_DESIGN.md §3.3 | No remote registry implementation |

---

## 9. Test Strategy

### 9.1 Unit Tests

| Test File | Coverage |
|-----------|----------|
| `tests/test_package_semver.py` | Semver range parsing, satisfaction checks, operator behavior |
| `tests/test_package_resolver.py` | Resolution algorithm, conflict detection, cycle detection, topological sort |
| `tests/test_package_manifest.py` | Manifest parsing, validation, schema enforcement |
| `tests/test_package_lock.py` | Lock file generation, staleness detection, replay |
| `tests/test_package_install.py` | End-to-end install flow (local + git deps) |
| `tests/test_package_publish.py` | Local publish, metadata validation, archive creation |
| `tests/test_package_search.py` | Local search, query matching |
| `tests/test_package_info.py` | Package info display |

### 9.2 Integration Tests

| Test | Description |
|------|-------------|
| `test_full_install_cycle` | Create project → add deps → install → verify lib/ |
| `test_lock_reproducibility` | Install → delete lib/ → install again → same checksums |
| `test_conflict_detection` | Two packages requiring incompatible versions → clear error |
| `test_circular_detection` | A→B→C→A → clear error with cycle path |
| `test_offline_install` | Cache exists → install --offline → success |
| `test_frozen_lockfile` | Lock exists → install --frozen-lockfile → success |
| `test_frozen_lockfile_stale` | Modify ail.toml → install --frozen-lockfile → failure |

### 9.3 Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error |
| 2 | Manifest not found |
| 3 | Manifest validation error |
| 4 | Dependency conflict |
| 5 | Circular dependency |
| 6 | Package not found |
| 7 | Checksum mismatch |
| 8 | Lock file stale (frozen mode) |
| 9 | Network error (future) |

---

## 10. Open Questions

| # | Question | Recommendation | Status |
|:-:|----------|----------------|--------|
| 1 | Should `ail install` auto-add if package not in manifest? | **No** (per design doc §13 #3) | Resolved |
| 2 | Should lock file be committed to VCS? | **Yes** (per design doc §13 #5) | Resolved |
| 3 | Should `--dev` flag exist? | **Yes** (per design doc §13 #9) | Resolved |
| 4 | Global cache location? | XDG: `~/.cache/ail/` Linux, `%LOCALAPPDATA%/ail/` Windows | Deferred to Phase 2 |
| 5 | Should `ail new` become `ail init`? | **No** — `ail new` stays public, `ail init` stays internal | Resolved (ADR-011) |
| 6 | What version of semver to follow? | SemVer 2.0.0 (semver.org) | Resolved |

---

## 11. Deliverables

1. This architecture document
2. ADR-010 through ADR-015 (consolidated in ARCHITECTURE_DECISIONS.md)
3. Updated PACKAGE_MANAGER_DESIGN.md with M77 additions
4. Implementation plan (after architecture review)

---

## 12. Implementation Order

| Phase | What | Depends On | Estimated LOC |
|-------|------|------------|---------------|
| 1 | ADR-010: Consolidate registry code | Nothing | ~50 (move + delete) |
| 2 | ADR-013: Semver range parsing | Nothing | ~80 |
| 3 | ADR-014: Conflict detection | Phase 2 | ~60 |
| 4 | ADR-015: Circular detection | Phase 2 | ~30 |
| 5 | M77.1: Harden install | Phases 2-4 | ~100 |
| 6 | M77.2: Consolidate publish | Phase 1 | ~40 |
| 7 | M77.3: Local search | Nothing | ~80 |
| 8 | M77.4: Package info command | Nothing | ~60 |
| 9 | M77.5: Resolution algorithm rewrite | Phases 2-4 | ~150 |
| 10 | M77.6: AI context integration | Phase 8 | ~40 |
| 11 | Tests | All phases | ~400 |
| 12 | Documentation | All phases | ~100 |

**Total estimated:** ~1,190 LOC (code + tests + docs)

---

*This document is the authoritative architecture reference for M77. Implementation must not proceed until architecture review is complete.*
