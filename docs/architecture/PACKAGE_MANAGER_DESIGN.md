# Package Manager Design (DX-006)

**Specification-first design document for the AILang package manager.**

Status: **APPROVED** — implementation in progress (DX-006).

---

## Table of Contents

1. [Motivation](#1-motivation)
2. [Project Manifest: `ail.toml`](#2-project-manifest-ailtoml)
3. [Package Repository](#3-package-repository)
4. [Dependency Resolution](#4-dependency-resolution)
5. [CLI Commands](#5-cli-commands)
6. [Repository Layout](#6-repository-layout)
7. [Lock File](#7-lock-file)
8. [Offline Cache](#8-offline-cache)
9. [Checksum Verification](#9-checksum-verification)
10. [Versioning & Compatibility](#10-versioning--compatibility)
11. [Integration with Other DX Tools](#11-integration-with-other-dx-tools)
12. [Future Considerations](#12-future-considerations)
13. [Open Questions](#13-open-questions)

---

## 1. Motivation

### 1.1 Current State

AILang has:
- 66+ applications across `apps/`, `ai_benchmarks/`, `phase11/`
- 16 stdlib modules in `stdlib/`
- No dependency management — every app manually copies shared code or reimplements utilities
- No package registry or distribution mechanism beyond Git

### 1.2 Problem

Every AILang application today is self-contained. There is no way to:
- Declare a dependency on another AILang project
- Install shared libraries from a registry
- Version dependencies
- Publish reusable AILang packages
- Resolve transitive dependencies

### 1.3 Goal

A minimal, correct package manager that enables:
1. Project initialization (`ail init`)
2. Dependency declaration (`ail add`, `ail remove`)
3. Dependency installation (`ail install`)
4. Dependency updates (`ail update`)
5. Package publishing (`ail publish`)
6. Package discovery (`ail search`)

---

## 2. Project Manifest: `ail.toml`

### 2.1 Format

TOML is chosen over JSON, YAML, or custom formats because:
- TOML is human-readable and human-editable
- TOML is natively supported by Python's `tomllib` (stdlib since 3.11)
- TOML is already used by the Python ecosystem (pyproject.toml, Cargo.toml)
- TOML supports comments (unlike JSON)

### 2.2 Schema

```toml
[project]
name = "my-package"
version = "1.0.0"
description = "A short description of the package"
authors = ["Author Name <email@example.com>"]
license = "MIT"
entry = "src/main.ail"

[language]
version = "0.3"

[dependencies]
# Format: package_name = "version_req"
# Example: string-utils = ">=1.0.0"

[build]
# Build configuration (future)

[test]
# Test configuration (future)

[benchmark]
# Benchmark configuration (future)

[tools]
# Tool-specific configuration (future)
```

### 2.3 Field Reference

#### `[project]`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | ✅ | Package name (kebab-case, alphanumeric + hyphens) |
| `version` | string | ✅ | Semantic version (semver: `MAJOR.MINOR.PATCH`) |
| `description` | string | ❌ | Short description (≤80 chars) |
| `authors` | string array | ❌ | Author list in `"Name <email>"` format |
| `license` | string | ❌ | SPDX license identifier (e.g., `MIT`, `Apache-2.0`) |
| `entry` | string | ❌ | Entry point file relative to project root (default: `main.ail`) |

#### `[language]`

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `version` | string | ✅ | AILang language version this package targets |

#### `[dependencies]`

- Keys: package names
- Values: version requirement strings (semver range syntax)
- Example: `string-utils = ">=1.0.0,<2.0.0"`
- Empty `[dependencies]` section means no dependencies

### 2.4 Manifest Discovery

The package manager discovers the project manifest by looking for `ail.toml` in:
1. The current directory (exact)
2. Parent directories (walk up until found or filesystem root)

This mirrors how `pyproject.toml` and `Cargo.toml` work.

### 2.5 Version Requirement Syntax

| Syntax | Meaning |
|--------|---------|
| `"1.2.3"` | Exact version |
| `">=1.2.3"` | At least this version |
| `">=1.2.3,<2.0.0"` | Compatible version range |
| `">=1.2.3,<2.0.0"` | Cargo-style caret (default for `ail add`) |
| `"*"` | Any version (discouraged) |

---

## 3. Package Repository

### 3.1 Source Types

The package manager supports three package source types, with a priority order:

| Priority | Source | Description | Example |
|:--------:|--------|-------------|---------|
| 1 | **Local folder** | Path to a local directory with `ail.toml` | ` path = "../shared-lib"` |
| 2 | **Git repository** | Git URL with optional tag/branch/commit | ` git = "https://github.com/user/repo" tag = "v1.0"` |
| 3 | **Official registry** | Centralized package registry (future) | `version = ">=1.0.0"` |

### 3.2 Dependency Declaration Examples

```toml
[dependencies]
# From official registry (future)
string-utils = ">=1.0.0"
json-helpers = "2.1.0"

# From local folder
local-lib = { path = "../shared-ail-lib" }

# From Git repository
my-lib = { git = "https://github.com/user/my-lib.git", tag = "v1.0.0" }

# From Git with branch
dev-lib = { git = "https://github.com/user/dev-lib.git", branch = "main" }
```

### 3.3 Official Registry (Future)

The official registry is **not implemented in v1 of DX-006**. The v1 package manager supports local folders and Git repositories only.

When implemented, the official registry will be:
- A simple HTTP API (JSON-over-HTTP, no gRPC/protobuf)
- Hosted at `registry.ailang.dev` (or similar)
- Read-only for the package manager; publishing via API key
- Immutable: once published, a version cannot be deleted

### 3.4 Registry API (Future — for reference)

```http
GET /api/v1/packages/{name}          → Package metadata
GET /api/v1/packages/{name}/versions → Version list
GET /api/v1/packages/{name}/{version} → Package archive (.tar.gz or .zip)
```

---

## 4. Dependency Resolution

### 4.1 Resolution Algorithm

The dependency resolver uses a simple backtracking algorithm:

```
1. Start with direct dependencies from [dependencies]
2. For each dependency, find the best matching version:
   a. If local path → use that version directly
   b. If Git repo → clone/fetch and use specified ref
   c. If registry (future) → query registry for versions matching constraint
3. Resolve transitive dependencies recursively
4. Check for version conflicts (same package, different versions)
5. If conflict detected → backtrack and try alternative versions
6. Produce a flat dependency tree for the lock file
```

### 4.2 Conflict Resolution

| Conflict Type | Resolution | Notes |
|---------------|-----------|-------|
| Same package, different version constraints | Choose highest version satisfying all constraints | Range intersection must be non-empty |
| Circular dependency | Error: report cycle | Prevented by dependency graph traversal |
| Missing dependency | Error: report missing package | Check all sources before failing |
| Conflicting sources (local vs registry) | Local wins | Explicit local path overrides registry |

### 4.3 Transitive Dependencies

Transitive dependencies are:
- Resolved and recorded in the lock file
- Not exposed in `ail.toml` (they are indirect)
- Updated when the direct dependency is updated

### 4.4 Version Resolution Priority

When multiple versions satisfy a constraint:

1. Prefer the **highest** matching version (optimistic)
2. Prefer the **most recently published** version (tiebreaker)
3. Prefer the **fewest transitive dependencies** (tiebreaker)

---

## 5. CLI Commands

### 5.1 Command Summary

| Command | Status | Description | Exit Codes |
|---------|--------|-------------|:----------:|
| `ail init` | 📋 Design | Initialize a new AILang project | 0, 3 |
| `ail add <pkg>` | 📋 Design | Add a dependency | 0, 1, 3 |
| `ail remove <pkg>` | 📋 Design | Remove a dependency | 0, 1, 3 |
| `ail install` | 📋 Design | Install all dependencies from `ail.toml` | 0, 1, 3 |
| `ail update [pkg]` | 📋 Design | Update dependencies to latest matching versions | 0, 1, 3 |
| `ail publish` | 📋 Future | Publish package to registry | — |
| `ail search <query>` | 📋 Future | Search package registry | — |
| `ail list` | 📋 Design | List installed dependencies | 0 |

### 5.2 `ail init`

```
ail init [directory]

Initialize a new AILang project.

If directory is provided, create it and initialize inside.
If omitted, initialize the current directory.

Interactive prompts:
  - Project name (default: directory name)
  - Version (default: 0.1.0)
  - Description (default: "")
  - Entry point (default: main.ail)
  - Language version (default: 0.3)

Creates:
  - ail.toml (project manifest)
  - <entry> (main.ail stub with hello world)
  - src/ directory (if entry is under src/)
  - ail.lock (empty lock file)

Flags:
  --name NAME          Project name (skip prompt)
  --version VERSION    Initial version (default: 0.1.0)
  --entry FILE         Entry point (default: main.ail)
  --yes, -y            Accept all defaults, no prompts
```

### 5.3 `ail add`

```
ail add <package> [options]

Add a dependency to the project.

package can be:
  - A package name (for registry lookup, future)
  - A local path:  path=../lib
  - A Git URL:     git=https://github.com/user/repo

Options:
  --tag TAG           Git tag to use
  --branch BRANCH     Git branch to use
  --rev REV           Git commit hash to use
  --dev               Add as dev dependency (future)
  --save-exact        Save exact version (no range)

Effects:
  - Adds entry to [dependencies] in ail.toml
  - Runs ail install (resolves and downloads)
  - Updates ail.lock

Exit codes:
  0  Success
  1  Package not found or resolution failed
  3  Invalid package specifier
```

### 5.4 `ail remove`

```
ail remove <package>

Remove a dependency from the project.

Effects:
  - Removes entry from [dependencies] in ail.toml
  - Removes package from local cache (if not needed by other deps)
  - Updates ail.lock
  - Does NOT update transitive dependencies (they remain if still needed)

Exit codes:
  0  Success
  1  Package not in dependencies
```

### 5.5 `ail install`

```
ail install [options]

Install all dependencies declared in ail.toml.

Resolution strategy:
  1. Read ail.toml → extract [dependencies]
  2. If ail.lock exists and is consistent with ail.toml:
     → Replay lock file (no resolution needed)
  3. If ail.lock does not exist or is stale:
     → Resolve all dependencies
     → Write ail.lock
  4. Download/copy all packages to local cache
  5. Verify checksums (if available)

Options:
  --no-lock           Skip lock file creation
  --offline           Fail if network access required
  --frozen-lockfile   Fail if lock file would change

Flags:
  --production        Skip dev dependencies (future)

Exit codes:
  0  Success
  1  Resolution failure, download failure, checksum mismatch
  3  No ail.toml found, invalid manifest
```

### 5.6 `ail update`

```
ail update [package]

Update dependencies to the latest versions that satisfy constraints.

Without arguments: update all dependencies.
With package name: update only that dependency.

Effects:
  - Re-resolves dependency tree
  - Updates ail.lock
  - Does NOT modify version constraints in ail.toml

Exit codes:
  0  Success
  1  Resolution failure
```

### 5.7 `ail list`

```
ail list [options]

List all installed dependencies and their versions.

Options:
  --tree              Show dependency tree (indented)
  --outdated          Show packages with newer versions available

Output:
  package_name  version_installed  version_constraint  source
  ──────────────────────────────────────────────────────────────
  string-utils  1.2.0             >=1.0.0             registry
  json-helpers  2.1.0             =2.1.0              local: ../lib

Exit codes:
  0  Success
```

---

## 6. Repository Layout

### 6.1 Project Layout

```
my-package/
├── ail.toml              # Project manifest
├── ail.lock              # Lock file (auto-generated, committed to VCS)
├── src/
│   └── main.ail           # Entry point (or as declared in ail.toml)
├── lib/                   # Local dependencies (written by ail install)
│   └── <package-name>/
│       ├── ail.toml
│       └── ...            # Package files
├── tests/
│   └── ...                # Test files
└── .ail/                  # Tool-managed cache/metadata (hidden)
    └── cache/             # Downloaded package archive cache
```

### 6.2 Cache Layout

```
<project>/.ail/cache/
└── packages/
    ├── <package-name>/
    │   ├── <version>/
    │   │   ├── package.ail.tar.gz    # Original archive (from registry/Git)
    │   │   ├── checksum.sha256       # Integrity hash
    │   │   └── manifest.json         # Cached metadata
    │   └── ...
    └── ...
```

### 6.3 Global Cache (Future)

```
~/.ail/cache/
└── packages/
    └── <package-name>/
        └── <version>/
            ├── package.ail.tar.gz
            └── checksum.sha256
```

A global cache avoids re-downloading packages across projects. When present, a global cache is checked before downloading.

---

## 7. Lock File

### 7.1 Purpose

The lock file (`ail.lock`) records the exact resolved dependency tree, ensuring:
- Reproducible builds across environments
- Deterministic dependency resolution
- Fast install (skip resolution, replay lock file)
- Security audit trail

### 7.2 Format

```toml
# ail.lock — Auto-generated. Do not edit manually.
version = 1

[[packages]]
name = "string-utils"
version = "1.2.0"
source = "registry"
checksum = "sha256-<hex>"
dependencies = ["json-helpers >=1.0.0"]

[[packages]]
name = "json-helpers"
version = "2.1.0"
source = "local"
path = "../shared-ail-lib"
checksum = "sha256-<hex>"
dependencies = []
```

### 7.3 Lock File Rules

| Rule | Detail |
|------|--------|
| **Auto-generated** | Written by `ail install` and `ail add`. Never edit by hand. |
| **Committed to VCS** | `ail.lock` is checked into version control. |
| **Versioned schema** | `version` field at top for future format changes. |
| **Consistency check** | `ail install` verifies `ail.toml` hasn't changed since lock was generated. |
| **Staleness detection** | If `ail.toml` [dependencies] hash doesn't match lock header, re-resolve. |

### 7.4 Staleness Detection

The lock file header stores a hash of the `[dependencies]` section:

```toml
version = 1
input_hash = "sha256-<hash of ail.toml [dependencies]>"
```

On `ail install`:
1. Compute hash of current `[dependencies]`
2. Compare with `input_hash` in lock file
3. If match → replay lock (fast path)
4. If mismatch → re-resolve (slow path)

---

## 8. Offline Cache

### 8.1 Caching Strategy

| Layer | Location | Content | Persistence |
|-------|----------|---------|-------------|
| Project cache | `.ail/cache/` | Downloaded archives for this project | Deleted with project |
| Global cache (future) | `~/.ail/cache/` | Shared across projects | Permanent |

### 8.2 Offline Mode

`ail install --offline`:
- Fails if any package is not in cache
- Does not attempt network access
- Useful for CI environments without network

### 8.3 Cache Eviction

- Packages are never automatically deleted from the global cache
- Project cache can be cleaned with `ail clean`

---

## 9. Checksum Verification

### 9.1 Algorithm

SHA-256 is used for all integrity verification.

### 9.2 Verification Points

| Point | What is Verified | Action on Mismatch |
|-------|-----------------|--------------------|
| Download | Archive checksum vs remote checksum | Retry, then fail |
| Install | Extracted files checksums vs lock file | Re-extract from archive |
| Build | All dependency files checksums (optional) | Warning, re-install recommended |

### 9.3 Checksum Storage

- In `ail.lock`: per-package checksum
- In registry metadata (future): per-version checksum
- In `.ail/cache/`: checksum file alongside archive

---

## 10. Versioning & Compatibility

### 10.1 Package Versioning

All packages use Semantic Versioning 2.0:

```
MAJOR.MINOR.PATCH
```

| Increment | Meaning |
|-----------|---------|
| MAJOR | Breaking API change |
| MINOR | Backward-compatible feature addition |
| PATCH | Bug fix, no API change |

### 10.2 Language Version Compatibility

A package's `[language] version` field targets a specific AILang language version. The package manager checks:

- Package targets `0.3` → compatible with compiler `0.3.x`
- Package targets `0.2` → incompatible with compiler `0.3.x` (warning)
- Package targets `0.4` (future) → incompatible with compiler `0.3.x` (error)

### 10.3 Dependency Hell Prevention

| Mechanism | How It Prevents Dependency Hell |
|-----------|--------------------------------|
| Lock file | Freezes exact versions |
| Semver | Clear API compatibility guarantees |
| No diamond dependency merging | Error on conflict (no complex dependency solving) |
| Minimal transitive resolution | Only resolve what is needed |

---

## 11. Integration with Other DX Tools

### 11.1 Shared Project Manifest

`ail.toml` is the canonical project manifest for **all** DX tools:

| Tool | Section | Purpose |
|------|---------|---------|
| Package Manager | `[project]`, `[dependencies]` | Project metadata and dependencies |
| Benchmark Runner | `[benchmark]` | Benchmark configuration (applies, suites) |
| Test Generator | `[test]` | Test configuration (directories, patterns) |
| Static Analyzer | `[project]` | Entry point for analysis |
| LSP (future) | `[project]`, `[language]` | Project context for editor |
| Formatter | `[tools]` | Formatter configuration |

### 11.2 Dependency Integration for Test Generator

When the test generator runs:
1. Read `ail.toml` → discover entry point
2. Resolve dependencies from `lib/` (already installed)
3. Generate tests that cover all `lib/` imports if missing

### 11.3 Dependency Integration for Benchmark Runner

When the benchmark runner runs:
1. Read `ail.toml` → discover entry point and benchmark config
2. Ensure dependencies are installed before running
3. Include dependency code in line/function counts (if relevant)

### 11.4 Configuration Sharing Example

```toml
[project]
name = "inventory"
version = "1.0.0"
entry = "main.ail"

[language]
version = "0.3"

[dependencies]
string-utils = ">=1.0.0"

[test]
dir = "tests/"
pattern = "test_*.ail"

[benchmark]
suites = ["quick", "canonical"]
repeat = 5
```

---

## 12. Future Considerations

### 12.1 Not in v1

| Feature | Reason |
|---------|--------|
| Official registry server | Requires infrastructure, hosting, moderation |
| `ail publish` | Requires registry |
| `ail search` | Requires registry |
| Global cache (`~/.ail/`) | Requires concurrency/locking design |
| Pre-built package archives | Not needed until packages exceed reasonable size |
| Package signing / GPG | Not needed until security concerns arise |
| Private registries | Not needed until teams request it |
| Workspaces / monorepos | Can be added as a superset later |

### 12.2 Package Format

A package is a directory with:
- `ail.toml` (manifest)
- `.ail` source files
- No compiled artifacts (AILang is interpreted from source)

For registry distribution: `.tar.gz` or `.zip` archive of the package directory.

### 12.3 Package Naming Convention

```
<kebab-case-name>
```

Rules:
- Lowercase only
- Alphanumeric characters and hyphens
- Starts and ends with alphanumeric
- Max 64 characters
- Examples: `string-utils`, `json-helpers`, `csv-tools`

---

## 13. Open Questions

These questions must be answered before implementation begins:

| # | Question | Options | Recommended |
|:-:|----------|---------|:-----------:|
| 1 | Should `ail.lock` be TOML or JSON? | TOML (human-readable), JSON (machine-friendly) | **TOML** (consistency with `ail.toml`) |
| 2 | Should the global cache be at `~/.ail/` or `~/.cache/ail/`? | XDG convention vs project-custom | **XDSTD** (`~/.cache/ail/` on Linux, `%LOCALAPPDATA%/ail/` on Windows) |
| 3 | Should `ail install` automatically run `ail add` if package not in manifest? | No (separate commands), Yes (convenience) | **No** (principle of least surprise) |
| 4 | Should transitive dependency constraints be resolved optimistically (highest) or pessimistically (lowest)? | Highest satisfies most users, Lowest is safest for compatibility | **Highest** (consistent with Cargo/npm) |
| 5 | Should the lock file be committed to VCS? | Yes (reproducible builds), No (avoid conflicts) | **Yes** (standard practice) |
| 6 | Should `ail.toml` support `[build]`, `[test]`, `[benchmark]` sections from the start, or add them as tools ship? | All at once (clean coordination), Incrementally (add when tool ships) | **Incrementally** (add sections when the tool that uses them is implemented) |
| 7 | Should the local dependency directory be named `lib/` or `packages/`? | `lib/` (familiar), `packages/` (explicit) | **`lib/`** (short, conventional) |
| 8 | Should `ail add git=...` clone the full repo or use shallow clone? | Full (has history), Shallow (faster, smaller) | **Shallow** (no history needed for dependencies) |
| 9 | Should there be a `--dev` flag for dev-only dependencies? | Yes (common pattern), No (keep minimal) | **Yes** (standard in npm/Cargo/Poetry) |
| 10 | Should `ail install` support path dependencies outside the project? | Yes (for monorepos), No (limit scope) | **Yes** (`../path/to/lib` references) |

---

## Appendix A: Comparison with Existing Package Managers

| Feature | AILang (DX-006) | Cargo | npm | Python (pip) |
|---------|:---------------:|:-----:|:---:|:------------:|
| Manifest format | TOML | TOML | JSON | TOML (pyproject) |
| Lock file | ail.lock | Cargo.lock | package-lock.json | — |
| Semver | ✅ Full | ✅ Caret | ✅ Tilde/caret | ⚠️ PEP 440 |
| Local deps | ✅ path= | ✅ path= | ✅ file: | ✅ -e |
| Git deps | ✅ git= | ✅ git= | ✅ git: | ✅ pip install git+ |
| Registry | Future (HTTP JSON) | crates.io | npmjs.com | PyPI |
| Workspaces | Future | ✅ | ✅ | ❌ |
| Dev deps | ✅ --dev | ✅ [dev-dependencies] | ✅ --save-dev | ❌ |
| Lock file in VCS | ✅ | ✅ | ✅ | N/A |

---

*This is a design document, not implementation. It answers "what" and "why" before "how." Implementation must follow the TOOLING_ARCHITECTURE.md conventions.*
