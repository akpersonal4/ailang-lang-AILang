# AILang Versioning Policy

**Applies to:** v1.0.0-RC1 and all subsequent v1.x releases

---

## 1. Semantic Versioning

AILang follows [Semantic Versioning 2.0.0](https://semver.org/):

```
MAJOR.MINOR.PATCH (e.g., 1.2.3)
```

| Component | Increment When | Example |
|:----------|----------------|:-------:|
| **MAJOR** | Breaking changes to the language, compiler API, or runtime semantics | 1.0.0 → 2.0.0 |
| **MINOR** | New features, new stdlib modules, non-breaking enhancements | 1.0.0 → 1.1.0 |
| **PATCH** | Bug fixes, documentation updates, performance improvements | 1.0.0 → 1.0.1 |

### Pre-release Identifiers

| Identifier | Meaning | Example |
|:-----------|---------|:-------:|
| `-RC1` | Release Candidate — feature-complete, awaiting validation | 1.0.0-RC1 |
| `-beta.N` | Beta — feature-complete but may have known issues | 1.1.0-beta.1 |
| `-alpha.N` | Alpha — incomplete, unstable | 2.0.0-alpha.1 |

Pre-release versions have **lower precedence** than the corresponding release version.

---

## 2. What Constitutes a Breaking Change (MAJOR)

The following changes require a MAJOR version bump:

### Language
- Removal or renaming of a keyword
- Grammar changes that invalidate previously valid syntax
- Changes to operator precedence or associativity
- Changes to evaluation order (e.g., making `&&` short-circuit)
- Removal of a language construct

### Standard Library
- Removal or renaming of a stdlib module
- Removal or renaming of a stdlib function
- Adding a required parameter to an existing function
- Changing return type or semantics of an existing function

### Compiler API
- Removal or renaming of a public compiler module, class, or function
- Changes to the IR node structure that break downstream consumers
- Changes to the diagnostic error code scheme

### Runtime
- Changes to variable scoping rules
- Changes to module resolution behavior
- Changes to type coercion rules

### Tooling
- Removal of a CLI command or flag
- Incompatible changes to JSON output format
- Breaking changes to LSP protocol messages

### What is NOT Breaking
- Adding new keywords (if they are contextual or behind a flag)
- Adding new stdlib modules or functions
- Adding new optional parameters to stdlib functions
- Adding new CLI commands or flags
- Adding new fields to JSON output
- Bug fixes that change behavior from incorrect to correct
- Performance improvements
- Documentation changes

---

## 3. What Constitutes a Minor Change (MINOR)

- New language features (behind `--experimental-*` flags or opt-in)
- New stdlib modules or functions
- New CLI commands or flags
- New LSP capabilities
- New diagnostic error codes
- New tooling features

---

## 4. What Constitutes a Patch Change (PATCH)

- Bug fixes
- Performance improvements
- Documentation updates
- Test additions or improvements
- Refactoring with no behavior change
- CI/CD configuration changes

---

## 5. Backward Compatibility Guarantees

### v1.x Compatibility Promise

Any program that compiles and runs correctly on version `1.x.y` will compile and run correctly on version `1.x.z` (where `z >= y`), with the following exceptions:

| Exception | Rationale |
|-----------|-----------|
| Bug fixes that correct undefined behavior | Programs relying on bugs are not guaranteed |
| Security patches | Security fixes may change behavior |
| Experimental features (behind flags) | May change or be removed without notice |

### Deprecation Policy

1. A feature marked as deprecated will continue to work for at least **one minor release** (e.g., deprecated in 1.1.0 → removed in 1.2.0 at earliest)
2. Deprecation warnings are emitted at compile time with a clear migration path
3. The deprecation is documented in the release notes and CHANGELOG

### Experimental Features

Features behind `--experimental-*` flags:
- **No compatibility guarantees** — may change or be removed at any time
- Not subject to the deprecation policy
- Clearly documented as experimental in the language spec and release notes

---

## 6. Release Cadence

### v1.x (Stable)

| Release Type | Cadence | Scope |
|:-------------|:--------|-------|
| **MINOR** | Quarterly (every 3–4 months) | New features, stdlib additions |
| **PATCH** | As needed (typically bi-weekly) | Bug fixes, security patches |
| **Hotfix** | Within 24–48 hours for critical issues | Emergency bug fixes |

### Release Candidate Phase

During the RC phase (v1.0.0-RC1 → v1.0.0 final):
- **No new features** — only bug fixes and documentation
- Patch releases as needed (v1.0.0-RC2, etc.) if blocking issues are found
- RC phase duration: 4–8 weeks

---

## 7. Release Process

See `RELEASE_PROCESS.md` for the detailed release checklist.

### Quick Summary

1. Run full test suite + quality gates
2. Update version in `pyproject.toml` and `PROJECT_STATE.json`
3. Update `CHANGELOG.md`
4. Update `DEVELOPMENT_STATUS.md`
5. Create release notes
6. Create git tag
7. Push tag and create GitHub Release

---

## 8. LTS Policy

AILang does not currently offer Long-Term Support releases. All v1.x releases are supported until the next minor or major release. LTS may be introduced post-v1.0 based on community demand.

### Current Support Status

| Version | Status | End of Life |
|:--------|:-------|:------------|
| v0.x (pre-1.0) | ❌ End of life | 2026-07-10 |
| v1.0.0-RC1 | ✅ Active (RC) | Until v1.0.0 final |

---

## 9. Version Compatibility Matrix

| Language Version | Min Compiler Version | Min Python Version |
|:-----------------|:--------------------:|:------------------:|
| v1.0.x | v1.0.0 | 3.11+ |
| v0.x | v0.1.0 | 3.11+ |

---

## 10. Version Manifest

The canonical version is maintained in `pyproject.toml`:

```toml
[project]
name = "ailang"
version = "1.0.0"
```

Additional version references:
- `PROJECT_STATE.json` — `version` field
- `DEVELOPMENT_STATUS.md` — version in header and Latest Version table
- `CHANGELOG.md` — version headings

All version references must be updated atomically during the release process.

---

## 11. Examples

| Change | New Version | Rationale |
|--------|:-----------:|-----------|
| Initial RC | 1.0.0-RC1 | Pre-release of v1.0.0 |
| Fix duplicate import bug | 1.0.0-RC2 | Bug fix during RC phase |
| First stable release | 1.0.0 | Stable |
| Add `string.reverse` function | 1.1.0 | New stdlib function |
| Fix string.reverse edge case | 1.1.1 | Bug fix |
| Remove deprecated `string.reverse` | 2.0.0 | Breaking change |
| Add experimental `match` expression | 1.2.0 | New feature (behind flag) |
| Critical security fix | 1.2.1 | Security patch |
